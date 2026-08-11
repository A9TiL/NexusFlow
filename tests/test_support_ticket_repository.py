from app.db.repositories.server_repository import ServerRepository
from app.db.repositories.support_ticket_repository import (
    SupportTicketRepository,
)


def create_test_server(db_session):
    repo = ServerRepository(db_session)

    return repo.create(
        ip_address="192.168.30.1",
        region="AP-South",
        status="Failing",
    )


def test_create_ticket(db_session):
    server = create_test_server(db_session)

    repo = SupportTicketRepository(db_session)

    ticket = repo.create(
        node_id=server.node_id,
        issue_description="High network latency",
        priority="High",
    )

    assert ticket.ticket_id is not None
    assert ticket.node_id == server.node_id
    assert ticket.issue_description == "High network latency"
    assert ticket.priority == "High"
    assert ticket.status == "Open"


def test_get_ticket(db_session):
    server = create_test_server(db_session)

    repo = SupportTicketRepository(db_session)

    created = repo.create(
        server.node_id,
        "Network degradation",
        "Medium",
    )

    ticket = repo.get_by_id(created.ticket_id)

    assert ticket is not None
    assert ticket.ticket_id == created.ticket_id


def test_get_tickets_by_node(db_session):
    server = create_test_server(db_session)

    repo = SupportTicketRepository(db_session)

    repo.create(server.node_id, "Issue 1", "Low")
    repo.create(server.node_id, "Issue 2", "High")

    tickets = repo.get_by_node(server.node_id)

    assert len(tickets) == 2


def test_update_ticket(db_session):
    server = create_test_server(db_session)

    repo = SupportTicketRepository(db_session)

    ticket = repo.create(
        server.node_id,
        "High latency",
        "Medium",
    )

    updated = repo.update(
        ticket.ticket_id,
        priority="High",
        status="Resolved",
    )

    assert updated is not None
    assert updated.priority == "High"
    assert updated.status == "Resolved"


def test_delete_ticket(db_session):
    server = create_test_server(db_session)

    repo = SupportTicketRepository(db_session)

    ticket = repo.create(
        server.node_id,
        "Temporary issue",
        "Low",
    )

    deleted = repo.delete(ticket.ticket_id)

    assert deleted is not None
    assert repo.get_by_id(ticket.ticket_id) is None