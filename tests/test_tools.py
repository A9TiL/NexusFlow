import pytest
from app.db.session import SessionLocal
from app.tools.database_tools import get_server_status, get_network_logs, create_support_ticket

# Pytest Fixture. It automatically sets up a database connection before each test runs, and safely closes it afterward.
@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_get_server_status_valid(db_session):

    result = get_server_status(db_session, 1) 
    assert "error" not in result
    assert result["node_id"] == 1
    assert "status" in result

def test_get_server_status_invalid(db_session):

    result = get_server_status(db_session, 999) 
    assert "error" in result

def test_get_network_logs(db_session):
    result = get_network_logs(db_session, 1)
    assert isinstance(result, list)
    assert len(result) > 0

def test_create_support_ticket(db_session):
    result = create_support_ticket(db_session, 1, "High latency detected during test", "High")
    assert result["message"] == "Ticket created successfully"
    assert "ticket_id" in result