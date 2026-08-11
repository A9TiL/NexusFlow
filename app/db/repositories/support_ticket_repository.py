from sqlalchemy.orm import Session

from app.db.models import SupportTicket


class SupportTicketRepository:
    """Repository responsible for SupportTicket persistence operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        node_id: int,
        issue_description: str,
        priority: str,
    ) -> SupportTicket:

        ticket = SupportTicket(
            node_id=node_id,
            issue_description=issue_description,
            priority=priority,
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_by_id(
        self,
        ticket_id: int,
    ) -> SupportTicket | None:

        return (
            self.db.query(SupportTicket)
            .filter(SupportTicket.ticket_id == ticket_id)
            .first()
        )

    def get_by_node(
        self,
        node_id: int,
    ) -> list[SupportTicket]:

        return (
            self.db.query(SupportTicket)
            .filter(SupportTicket.node_id == node_id)
            .all()
        )

    def get_all(self) -> list[SupportTicket]:
        return self.db.query(SupportTicket).all()


    def update(
        self,
        ticket_id: int,
        issue_description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
    ) -> SupportTicket | None:

        ticket = self.get_by_id(ticket_id)

        if not ticket:
            return None

        if issue_description is not None:
            ticket.issue_description = issue_description

        if priority is not None:
            ticket.priority = priority

        if status is not None:
            ticket.status = status

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def delete(
        self,
        ticket_id: int,
    ) -> SupportTicket | None:

        ticket = self.get_by_id(ticket_id)

        if not ticket:
            return None

        self.db.delete(ticket)
        self.db.commit()

        return ticket