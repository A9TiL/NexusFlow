from app.main import app
from fastapi.testclient import TestClient
from app.db.models import PendingAction, ServerNode
from app.core.enums import ApprovalStatus
import json




def create_test_action(db_session):
    action = PendingAction(
        tool_name="delete_server",
        operation="DELETE",
        requested_by="ADMIN",
        parameters='{"node_id": 8}',
        status=ApprovalStatus.PENDING.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    return action


def test_list_pending_actions(client, db_session):

    create_test_action(db_session)

    response = client.get(
        "/api/v1/approvals/pending"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["actions"]) == 1
    
    
def test_approve_pending_action_executes_mutation(
    client,
    db_session,
):
    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.100.10",
            "region": "AP-South",
            "status": "Active",
        }),
        status=ApprovalStatus.PENDING.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "decided_by": "ADMIN",
            "reason": "Approved for deployment.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["action_status"] == ApprovalStatus.EXECUTED.value
    
def test_reject_pending_action(client, db_session):

    action = create_test_action(db_session)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/reject",
        json={
            "decided_by": "ADMIN",
            "reason": "Deletion is not required.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["message"] == "Action rejected successfully"
    assert data["action_id"] == action.action_id
    assert data["action_status"] == ApprovalStatus.REJECTED.value
    
def test_approve_nonexistent_action(client):

    response = client.post(
        "/api/v1/approvals/99999/approve",
        json={
            "decided_by": "ADMIN",
        },
    )

    assert response.status_code == 400
    
def test_reject_nonexistent_action(client):

    response = client.post(
        "/api/v1/approvals/99999/reject",
        json={
            "decided_by": "ADMIN",
        },
    )

    assert response.status_code == 400
    
def test_cannot_approve_already_approved_action(client, db_session):

    action = create_test_action(db_session)

    first_response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "decided_by": "ADMIN",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "decided_by": "ADMIN",
        },
    )

    assert second_response.status_code == 400
    
def test_approve_requires_decided_by(client, db_session):

    action = create_test_action(db_session)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "reason": "Approved.",
        },
    )

    assert response.status_code == 422
    
def test_api_approval_executes_approved_action(client, db_session):

    action = create_test_action(db_session)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "decided_by": "ADMIN",
            "reason": "Approved.",
        },
    )

    assert response.status_code == 200

    db_session.refresh(action)

    assert action.status == ApprovalStatus.EXECUTED.value
    assert action.executed_at is not None
    
def test_approve_api_actually_mutates_database(
    client,
    db_session,
):
    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.100.11",
            "region": "EU-Central",
            "status": "Active",
        }),
        status=ApprovalStatus.PENDING.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/approve",
        json={
            "decided_by": "ADMIN",
            "reason": "Approved.",
        },
    )

    assert response.status_code == 200

    server = (
        db_session.query(ServerNode)
        .filter(
            ServerNode.ip_address == "192.168.100.11"
        )
        .first()
    )

    assert server is not None
    assert server.region == "EU-Central"
    assert server.status == "Active"
    
def test_reject_api_does_not_execute_mutation(
    client,
    db_session,
):
    action = PendingAction(
        tool_name="create_server",
        operation="CREATE",
        requested_by="OPERATOR",
        parameters=json.dumps({
            "ip_address": "192.168.100.12",
            "region": "US-East",
            "status": "Active",
        }),
        status=ApprovalStatus.PENDING.value,
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    response = client.post(
        f"/api/v1/approvals/{action.action_id}/reject",
        json={
            "decided_by": "ADMIN",
            "reason": "Deployment rejected.",
        },
    )

    assert response.status_code == 200

    server = (
        db_session.query(ServerNode)
        .filter(
            ServerNode.ip_address == "192.168.100.12"
        )
        .first()
    )

    assert server is None