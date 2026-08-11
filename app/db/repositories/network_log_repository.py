from sqlalchemy.orm import Session

from app.db.models import NetworkLog


class NetworkLogRepository:
    """Repository responsible for NetworkLog persistence operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        node_id: int,
        error_code: str | None,
        latency: float,
    ) -> NetworkLog:

        log = NetworkLog(
            node_id=node_id,
            error_code=error_code,
            latency=latency,
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def get_by_id(self, log_id: int) -> NetworkLog | None:
        return (
            self.db.query(NetworkLog)
            .filter(NetworkLog.log_id == log_id)
            .first()
        )

    def get_by_node(
        self,
        node_id: int,
        limit: int = 5,
    ) -> list[NetworkLog]:

        return (
            self.db.query(NetworkLog)
            .filter(NetworkLog.node_id == node_id)
            .order_by(NetworkLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_all(self) -> list[NetworkLog]:
        return self.db.query(NetworkLog).all()

    def update(
        self,
        log_id: int,
        error_code: str | None = None,
        latency: float | None = None,
    ) -> NetworkLog | None:

        log = self.get_by_id(log_id)

        if not log:
            return None

        if error_code is not None:
            log.error_code = error_code

        if latency is not None:
            log.latency = latency

        self.db.commit()
        self.db.refresh(log)

        return log

    def delete(self, log_id: int) -> NetworkLog | None:

        log = self.get_by_id(log_id)

        if not log:
            return None

        self.db.delete(log)
        self.db.commit()

        return log