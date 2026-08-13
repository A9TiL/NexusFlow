import json
import pytest
from app.core.enums import ApprovalStatus
from app.db.models import PendingAction, ServerNode
from app.services.workflow_service import resume_approved_action

def test_approved_action_executes(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.90.10",
            "region": "AP-South",
            "status": "Active",
        }),
        status=ApprovalStatus.APPROVED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    result = resume_approved_action(
        db=db_session,
        action_id=action.action_id,
    )

    assert result.status == ApprovalStatus.EXECUTED.value
    assert result.executed_at is not None

def test_pending_action_cannot_resume(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.90.11",
            "region": "AP-South",
            "status": "Active",
        }),
        status=ApprovalStatus.PENDING.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
def test_rejected_action_cannot_resume(db_session):

    action = PendingAction(
        tool_name="delete_server",
        operation="DELETE",
        requested_by="ADMIN",
        parameters=json.dumps({
            "node_id": 8,
        }),
        status=ApprovalStatus.REJECTED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
def test_executed_action_cannot_resume_again(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.90.12",
            "region": "EU-Central",
            "status": "Active",
        }),
        status=ApprovalStatus.EXECUTED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
def test_missing_action_cannot_resume(db_session):

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=99999,
        )
        
def test_invalid_role_cannot_resume(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="SUPER_ADMIN",
        parameters=json.dumps({
            "ip_address": "192.168.90.13",
            "region": "AP-South",
            "status": "Active",
        }),
        status=ApprovalStatus.APPROVED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
def test_invalid_parameters_cannot_resume(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters="this-is-not-json",
        status=ApprovalStatus.APPROVED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
def test_parameters_must_be_json_object(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps([
            "invalid",
            "parameters",
        ]),
        status=ApprovalStatus.APPROVED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    with pytest.raises(ValueError):

        resume_approved_action(
            db=db_session,
            action_id=action.action_id,
        )
        
        
def test_approved_create_server_actually_mutates_database(db_session):

    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.90.20",
            "region": "AP-South",
            "status": "Active",
        }),
        status=ApprovalStatus.APPROVED.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    result = resume_approved_action(
        db=db_session,
        action_id=action.action_id,
    )

    assert result.status == ApprovalStatus.EXECUTED.value

    server = (
        db_session.query(ServerNode)
        .filter(
            ServerNode.ip_address == "192.168.90.20"
        )
        .first()
    )

    assert server is not None
    assert server.region == "AP-South"
    assert server.status == "Active"
    
