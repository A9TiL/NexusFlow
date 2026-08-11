from sqlalchemy.orm import Session

from app.db.repositories.server_repository import ServerRepository
from app.db.repositories.network_log_repository import NetworkLogRepository
from app.db.repositories.support_ticket_repository import (
    SupportTicketRepository,
)


from app.core.schemas import (
    ServerCreateRequest,
    ServerUpdateRequest,
    ServerDeleteRequest,
    NetworkLogCreateRequest,
    NetworkLogUpdateRequest,
    NetworkLogDeleteRequest,
    SupportTicketCreateRequest,
    SupportTicketUpdateRequest,
    SupportTicketDeleteRequest,
)

def get_server_status(db: Session, node_id: int) -> dict:
    """
    Fetch the current status and region of a specific server node.
    """

    repository = ServerRepository(db)

    node = repository.get_by_id(node_id)

    if not node:
        return {
            "error": f"Node {node_id} not found in the database."
        }

    return {
        "node_id": node.node_id,
        "ip": node.ip_address,
        "status": node.status,
        "region": node.region,
    }


def create_server(
    db: Session,
    ip_address: str,
    region: str,
    status: str,
) -> dict:

    request = ServerCreateRequest(
        ip_address=ip_address,
        region=region,
        status=status,
    )

    repository = ServerRepository(db)

    node = repository.create(
        ip_address=request.ip_address,
        region=request.region,
        status=request.status.value,
    )

    return {
        "message": "Server created successfully",
        "node_id": node.node_id,
        "ip": node.ip_address,
        "region": node.region,
        "status": node.status,
    }

def update_server_status(
    db: Session,
    node_id: int,
    status: str,
) -> dict:

    request = ServerUpdateRequest(
        node_id=node_id,
        status=status,
    )

    repository = ServerRepository(db)

    node = repository.update_status(
        node_id=request.node_id,
        status=request.status.value,
    )

    if not node:
        return {
            "error": f"Node {request.node_id} not found in the database."
        }

    return {
        "message": "Server status updated successfully",
        "node_id": node.node_id,
        "status": node.status,
    }

def delete_server(
    db: Session,
    node_id: int,
) -> dict:

    request = ServerDeleteRequest(
        node_id=node_id,
    )

    repository = ServerRepository(db)

    node = repository.delete(request.node_id)

    if not node:
        return {
            "error": f"Node {request.node_id} not found in the database."
        }

    return {
        "message": "Server deleted successfully",
        "node_id": node.node_id,
    }



def get_network_logs(
    db: Session,
    node_id: int,
    limit: int = 5,
) -> list:
    """
    Retrieve recent diagnostic logs for a server node.
    """

    repository = NetworkLogRepository(db)

    logs = repository.get_by_node(
        node_id=node_id,
        limit=limit,
    )

    if not logs:
        return [
            {
                "message": (
                    f"No network logs found for Node {node_id}."
                )
            }
        ]

    return [
        {
            "log_id": log.log_id,
            "error": log.error_code,
            "latency": log.latency,
            "timestamp": str(log.timestamp),
        }
        for log in logs
    ]


def create_network_log(
    db: Session,
    node_id: int,
    error_code: str | None,
    latency: float,
) -> dict:

    request = NetworkLogCreateRequest(
        node_id=node_id,
        error_code=error_code,
        latency=latency,
    )

    repository = NetworkLogRepository(db)

    log = repository.create(
        node_id=request.node_id,
        error_code=request.error_code,
        latency=request.latency,
    )

    return {
        "message": "Network log created successfully",
        "log_id": log.log_id,
        "node_id": log.node_id,
        "error_code": log.error_code,
        "latency": log.latency,
        "timestamp": str(log.timestamp),
    }


def update_network_log(
    db: Session,
    log_id: int,
    error_code: str | None = None,
    latency: float | None = None,
) -> dict:

    request = NetworkLogUpdateRequest(
        log_id=log_id,
        error_code=error_code,
        latency=latency,
    )

    repository = NetworkLogRepository(db)

    log = repository.update(
        log_id=request.log_id,
        error_code=request.error_code,
        latency=request.latency,
    )

    if not log:
        return {
            "error": f"Network log {request.log_id} not found."
        }

    return {
        "message": "Network log updated successfully",
        "log_id": log.log_id,
        "error_code": log.error_code,
        "latency": log.latency,
    }


def delete_network_log(
    db: Session,
    log_id: int,
) -> dict:

    request = NetworkLogDeleteRequest(
        log_id=log_id,
    )

    repository = NetworkLogRepository(db)

    log = repository.delete(request.log_id)

    if not log:
        return {
            "error": f"Network log {request.log_id} not found."
        }

    return {
        "message": "Network log deleted successfully",
        "log_id": log.log_id,
    }




def create_support_ticket(
    db: Session,
    node_id: int,
    issue: str,
    priority: str,
) -> dict:

    request = SupportTicketCreateRequest(
        node_id=node_id,
        issue=issue,
        priority=priority,
    )

    repository = SupportTicketRepository(db)

    ticket = repository.create(
        node_id=request.node_id,
        issue_description=request.issue,
        priority=request.priority.value,
    )

    return {
        "message": "Ticket created successfully",
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
    }


def get_support_ticket(
    db: Session,
    ticket_id: int,
) -> dict:
    """
    Retrieve a support ticket.
    """

    repository = SupportTicketRepository(db)

    ticket = repository.get_by_id(ticket_id)

    if not ticket:
        return {
            "error": f"Ticket {ticket_id} not found."
        }

    return {
        "ticket_id": ticket.ticket_id,
        "node_id": ticket.node_id,
        "issue": ticket.issue_description,
        "priority": ticket.priority,
        "status": ticket.status,
    }


def update_support_ticket(
    db: Session,
    ticket_id: int,
    issue: str | None = None,
    priority: str | None = None,
    status: str | None = None,
) -> dict:

    request = SupportTicketUpdateRequest(
        ticket_id=ticket_id,
        issue=issue,
        priority=priority,
        status=status,
    )

    repository = SupportTicketRepository(db)

    ticket = repository.update(
        ticket_id=request.ticket_id,
        issue_description=request.issue,
        priority=(
            request.priority.value
            if request.priority is not None
            else None
        ),
        status=(
            request.status.value
            if request.status is not None
            else None
        ),
    )

    if not ticket:
        return {
            "error": f"Ticket {request.ticket_id} not found."
        }

    return {
        "message": "Support ticket updated successfully",
        "ticket_id": ticket.ticket_id,
        "issue": ticket.issue_description,
        "priority": ticket.priority,
        "status": ticket.status,
    }


def delete_support_ticket(
    db: Session,
    ticket_id: int,
) -> dict:

    request = SupportTicketDeleteRequest(
        ticket_id=ticket_id,
    )

    repository = SupportTicketRepository(db)

    ticket = repository.delete(request.ticket_id)

    if not ticket:
        return {
            "error": f"Ticket {request.ticket_id} not found."
        }

    return {
        "message": "Support ticket deleted successfully",
        "ticket_id": ticket.ticket_id,
    }