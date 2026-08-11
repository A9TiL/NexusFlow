import pytest
from pydantic import ValidationError

from app.core.enums import (
    ServerStatus,
    TicketPriority,
)
from app.core.schemas import (
    ServerCreateRequest,
    ServerUpdateRequest,
    NetworkLogCreateRequest,
    SupportTicketCreateRequest,
)


def test_valid_server_create():
    request = ServerCreateRequest(
        ip_address="192.168.1.50",
        region="AP-South",
        status=ServerStatus.ACTIVE,
    )

    assert request.ip_address == "192.168.1.50"
    assert request.status == ServerStatus.ACTIVE


def test_invalid_server_status():
    with pytest.raises(ValidationError):
        ServerUpdateRequest(
            node_id=1,
            status="Destroyed",
        )


def test_invalid_node_id():
    with pytest.raises(ValidationError):
        ServerUpdateRequest(
            node_id=0,
            status=ServerStatus.ACTIVE,
        )


def test_invalid_latency():
    with pytest.raises(ValidationError):
        NetworkLogCreateRequest(
            node_id=1,
            latency=-50,
        )


def test_invalid_ticket_priority():
    with pytest.raises(ValidationError):
        SupportTicketCreateRequest(
            node_id=1,
            issue="Network failure",
            priority="Critical",
        )


def test_valid_ticket():
    ticket = SupportTicketCreateRequest(
        node_id=1,
        issue="High network latency",
        priority=TicketPriority.HIGH,
    )

    assert ticket.priority == TicketPriority.HIGH