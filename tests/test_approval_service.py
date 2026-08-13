import pytest

from app.core.enums import ApprovalStatus
from app.db.models import PendingAction
from app.services.approval_service import create_pending_action,get_pending_action,approve_action,reject_action

def test_create_pending_action(db_session):

    action = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="ADMIN",
        parameters='{"node_id": 8}',
    )

    assert action.action_id is not None
    assert action.tool_name == "delete_server"
    assert action.operation == "DELETE"
    assert action.requested_by == "ADMIN"
    assert action.parameters == '{"node_id": 8}'
    assert action.status == ApprovalStatus.PENDING.value
    
def test_get_pending_action(db_session):

    created = create_pending_action(
        db=db_session,
        tool_name="update_server_status",
        operation="UPDATE",
        requested_by="OPERATOR",
        parameters='{"node_id": 5, "status": "Failing"}',
    )

    result = get_pending_action(
        db=db_session,
        action_id=created.action_id,
    )

    assert result is not None
    assert result.action_id == created.action_id
    assert result.tool_name == "update_server_status"
    assert result.status == ApprovalStatus.PENDING.value
    
def test_approve_pending_action(db_session):

    created = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="ADMIN",
        parameters='{"node_id": 8}',
    )

    result = approve_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",
        reason="Approved for maintenance.",
    )

    assert result.status == ApprovalStatus.APPROVED.value
    assert result.decided_by == "ADMIN"
    assert result.decision_reason == "Approved for maintenance."
    
def test_reject_pending_action(db_session):

    created = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="OPERATOR",
        parameters='{"node_id": 8}',
    )

    result = reject_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",
        reason="Deletion not required.",
    )

    assert result.status == ApprovalStatus.REJECTED.value
    assert result.decided_by == "ADMIN"
    assert result.decision_reason == "Deletion not required."
    
def test_approve_missing_action(db_session):
    with pytest.raises(ValueError):
        approve_action(
            db=db_session,
            action_id=99999,
            decided_by="ADMIN",
            reason="Action not found.",
        )

def test_reject_missing_action(db_session):
    with pytest.raises(ValueError):
        reject_action(
            db=db_session,
            action_id=99999,
            decided_by="ADMIN",
            reason="Action not found.",
        )
        
def test_cannot_approve_already_approved_action(db_session):
    created = create_pending_action(
        db=db_session,
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters='{"ip_address": "192.168.50.10"}',)

    approve_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",)

    with pytest.raises(ValueError):
        approve_action(
            db=db_session,
            action_id=created.action_id,
            decided_by="ADMIN",
        )
        
def test_cannot_reject_approved_action(db_session):
    created = create_pending_action(
        db=db_session,
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters='{"ip_address": "192.168.50.10"}',)
    
    approve_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",)

    with pytest.raises(ValueError):
        reject_action(
            db=db_session,
            action_id=created.action_id,
            decided_by="ADMIN", )
        
def test_cannot_approve_rejected_action(db_session):
    created = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="OPERATOR",
        parameters='{"node_id": 8}',)

    reject_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",
        reason="Not necessary.", )

    with pytest.raises(ValueError):
        approve_action(
            db=db_session,
            action_id=created.action_id,
            decided_by="ADMIN",)
        
def test_cannot_reject_already_rejected_action(db_session):
    created = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="OPERATOR",
        parameters='{"node_id": 8}',)

    reject_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",)

    with pytest.raises(ValueError):
        reject_action(
            db=db_session,
            action_id=created.action_id,
            decided_by="ADMIN", )
        
def test_approval_only_changes_state(db_session):

    created = create_pending_action(
        db=db_session,
        tool_name="delete_server",
        operation="DELETE",
        requested_by="OPERATOR",
        parameters='{"node_id": 8}',
    )

    result = approve_action(
        db=db_session,
        action_id=created.action_id,
        decided_by="ADMIN",
    )

    assert result.status == ApprovalStatus.APPROVED.value

    assert result.status != ApprovalStatus.EXECUTED.value