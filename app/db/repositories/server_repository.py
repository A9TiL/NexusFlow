from sqlalchemy.orm import Session

from app.db.models import (
    ServerNode,
    NetworkLog,
    SupportTicket,
)


class ServerRepository:
    """Repository responsible for ServerNode persistence operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        ip_address: str,
        region: str,
        status: str,
    ) -> ServerNode:

        server = ServerNode(
            ip_address=ip_address,
            region=region,
            status=status,
        )

        self.db.add(server)
        self.db.commit()
        self.db.refresh(server)

        return server

    def get_by_id(self, node_id: int) -> ServerNode | None:
        return (
            self.db.query(ServerNode)
            .filter(ServerNode.node_id == node_id)
            .first()
        )

    def get_all(self) -> list[ServerNode]:
        return self.db.query(ServerNode).all()


    def update_status(
        self,
        node_id: int,
        status: str,
    ) -> ServerNode | None:

        server = self.get_by_id(node_id)

        if not server:
            return None

        server.status = status

        self.db.commit()
        self.db.refresh(server)

        return server

    def delete(self, node_id: int) -> ServerNode | None:

        server = self.get_by_id(node_id)

        if not server:
            return None

        has_logs = (
            self.db.query(NetworkLog)
            .filter(NetworkLog.node_id == node_id)
            .first()
            is not None
        )

        has_tickets = (
            self.db.query(SupportTicket)
            .filter(SupportTicket.node_id == node_id)
            .first()
            is not None
        )

        if has_logs or has_tickets:
            raise ValueError(
                f"ServerNode {node_id} cannot be deleted because "
                "dependent network logs or support tickets exist."
            )

        self.db.delete(server)
        self.db.commit()

        return server