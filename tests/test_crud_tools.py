import pytest
from pydantic import ValidationError

from app.tools.database_tools import (
    create_server,
    get_server_status,
    update_server_status,
    delete_server,
    create_network_log,
    get_network_logs,
    update_network_log,
    delete_network_log,
    create_support_ticket,
    get_support_ticket,
    update_support_ticket,
    delete_support_ticket,
)


# SERVER NODE CRUD TESTS

def test_create_server_tool(db_session):
    result = create_server(
        db=db_session,
        ip_address="192.168.50.10",
        region="AP-South",
        status="Active",
    )

    assert result["message"] == "Server created successfully"
    assert result["node_id"] is not None
    assert result["status"] == "Active"


def test_update_server_tool(db_session):
    created = create_server(
        db=db_session,
        ip_address="192.168.50.11",
        region="AP-South",
        status="Active",
    )

    result = update_server_status(
        db=db_session,
        node_id=created["node_id"],
        status="Failing",
    )

    assert result["message"] == "Server status updated successfully"
    assert result["status"] == "Failing"


def test_get_server_tool(db_session):
    created = create_server(
        db=db_session,
        ip_address="192.168.50.12",
        region="EU-Central",
        status="Active",
    )

    result = get_server_status(
        db=db_session,
        node_id=created["node_id"],
    )

    assert result["node_id"] == created["node_id"]
    assert result["status"] == "Active"


def test_delete_server_tool(db_session):
    created = create_server(
        db=db_session,
        ip_address="192.168.50.13",
        region="US-East",
        status="Active",
    )

    result = delete_server(
        db=db_session,
        node_id=created["node_id"],
    )

    assert result["message"] == "Server deleted successfully"

    lookup = get_server_status(
        db=db_session,
        node_id=created["node_id"],
    )

    assert "error" in lookup
    

# NETWORK LOG CRUD TESTS



def test_create_network_log_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.60.10",
        region="AP-South",
        status="Active",
    )

    result = create_network_log(
        db=db_session,
        node_id=server["node_id"],
        error_code="ERR-500",
        latency=250.5,
    )

    assert result["message"] == "Network log created successfully"
    assert result["node_id"] == server["node_id"]
    assert result["latency"] == 250.5


def test_update_network_log_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.60.11",
        region="AP-South",
        status="Active",
    )

    created = create_network_log(
        db=db_session,
        node_id=server["node_id"],
        error_code="ERR-500",
        latency=300,
    )

    result = update_network_log(
        db=db_session,
        log_id=created["log_id"],
        error_code="ERR-404",
        latency=100,
    )

    assert result["message"] == "Network log updated successfully"
    assert result["error_code"] == "ERR-404"
    assert result["latency"] == 100


def test_get_network_logs_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.60.12",
        region="EU-Central",
        status="Active",
    )

    create_network_log(
        db=db_session,
        node_id=server["node_id"],
        error_code=None,
        latency=25,
    )

    result = get_network_logs(
        db=db_session,
        node_id=server["node_id"],
    )

    assert len(result) == 1
    assert result[0]["latency"] == 25


def test_delete_network_log_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.60.13",
        region="US-East",
        status="Active",
    )

    created = create_network_log(
        db=db_session,
        node_id=server["node_id"],
        error_code="ERR-500",
        latency=400,
    )

    result = delete_network_log(
        db=db_session,
        log_id=created["log_id"],
    )

    assert result["message"] == "Network log deleted successfully"
    

# SUPPORT TICKET CRUD TESTS

def test_create_ticket_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.70.10",
        region="AP-South",
        status="Failing",
    )

    result = create_support_ticket(
        db=db_session,
        node_id=server["node_id"],
        issue="High network latency",
        priority="High",
    )

    assert result["message"] == "Ticket created successfully"
    assert result["ticket_id"] is not None
    assert result["status"] == "Open"


def test_get_ticket_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.70.11",
        region="AP-South",
        status="Failing",
    )

    created = create_support_ticket(
        db=db_session,
        node_id=server["node_id"],
        issue="Network failure",
        priority="High",
    )

    result = get_support_ticket(
        db=db_session,
        ticket_id=created["ticket_id"],
    )

    assert result["ticket_id"] == created["ticket_id"]
    assert result["issue"] == "Network failure"
    assert result["priority"] == "High"


def test_update_ticket_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.70.12",
        region="EU-Central",
        status="Failing",
    )

    created = create_support_ticket(
        db=db_session,
        node_id=server["node_id"],
        issue="Initial problem",
        priority="Medium",
    )

    result = update_support_ticket(
        db=db_session,
        ticket_id=created["ticket_id"],
        issue="Escalated network problem",
        priority="High",
        status="In Progress",
    )

    assert result["message"] == "Support ticket updated successfully"
    assert result["priority"] == "High"
    assert result["status"] == "In Progress"


def test_delete_ticket_tool(db_session):
    server = create_server(
        db=db_session,
        ip_address="192.168.70.13",
        region="US-East",
        status="Failing",
    )

    created = create_support_ticket(
        db=db_session,
        node_id=server["node_id"],
        issue="Temporary issue",
        priority="Low",
    )

    result = delete_support_ticket(
        db=db_session,
        ticket_id=created["ticket_id"],
    )

    assert result["message"] == "Support ticket deleted successfully"

    lookup = get_support_ticket(
        db=db_session,
        ticket_id=created["ticket_id"],
    )

    assert "error" in lookup
    

# VALIDATION TESTS


def test_create_server_rejects_invalid_status(db_session):
    with pytest.raises(ValidationError):
        create_server(
            db=db_session,
            ip_address="192.168.80.10",
            region="AP-South",
            status="Destroyed",
        )


def test_update_server_rejects_invalid_node_id(db_session):
    with pytest.raises(ValidationError):
        update_server_status(
            db=db_session,
            node_id=0,
            status="Active",
        )


def test_network_log_rejects_negative_latency(db_session):
    with pytest.raises(ValidationError):
        create_network_log(
            db=db_session,
            node_id=1,
            error_code="ERR-500",
            latency=-100,
        )


def test_ticket_rejects_invalid_priority(db_session):
    with pytest.raises(ValidationError):
        create_support_ticket(
            db=db_session,
            node_id=1,
            issue="Something went wrong",
            priority="Critical",
        )
        
# MISSING RECORD / ERROR HANDLING TESTS

def test_update_missing_server(db_session):
    result = update_server_status(
        db=db_session,
        node_id=99999,
        status="Failing",
    )

    assert "error" in result


def test_delete_missing_server(db_session):
    result = delete_server(
        db=db_session,
        node_id=99999,
    )

    assert "error" in result


def test_delete_missing_ticket(db_session):
    result = delete_support_ticket(
        db=db_session,
        ticket_id=99999,
    )

    assert "error" in result