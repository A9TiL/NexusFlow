from app.db.models import PendingAction


def test_pending_action_model_can_be_created(db_session):

    action = PendingAction(
        tool_name="delete_server",
        operation="DELETE",
        requested_by="ADMIN",
        parameters='{"node_id": 8}',
        status="PENDING",
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    assert action.action_id is not None
    assert action.tool_name == "delete_server"
    assert action.operation == "DELETE"
    assert action.requested_by == "ADMIN"
    assert action.parameters == '{"node_id": 8}'
    assert action.status == "PENDING"
    
def test_pending_action_can_store_decision_information(db_session):

    action = PendingAction(
        tool_name="update_server_status",
        operation="UPDATE",
        requested_by="OPERATOR",
        parameters='{"node_id": 5, "status": "Failing"}',
        status="APPROVED",
        decided_by="ADMIN",
        decision_reason="Approved for remediation",
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    assert action.status == "APPROVED"
    assert action.decided_by == "ADMIN"
    assert action.decision_reason == "Approved for remediation"
    
def test_pending_action_defaults_to_pending(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters='{"ip_address": "192.168.50.10"}',
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    assert action.status == "PENDING"