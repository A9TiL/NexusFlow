from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.schemas import ApprovalDecisionRequest
from app.db.session import get_db
from app.db.models import PendingAction
from app.services.approval_service import  approve_action,reject_action
from app.services.workflow_service import resume_approved_action



router = APIRouter(prefix="/api/v1/approvals",tags=["Approvals"])

@router.get("/pending")
def list_pending_actions(
    db: Session = Depends(get_db),
):
    """
    Return all actions currently waiting for approval.
    """
    actions = (
        db.query(PendingAction).filter(PendingAction.status == "PENDING").all() )

    return {
        "count": len(actions),
        "actions": actions,
    }


@router.post("/{action_id}/approve")
def approve_pending_action(
    action_id: int,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db)):
    """
    Approve and resume a pending action.

    The action is first transitioned from PENDING to APPROVED.
    Once approved, the workflow is resumed and the underlying
    mutation is executed through the governed tool registry.
    """

    try:
        action = approve_action(
            db=db,
            action_id=action_id,
            decided_by=request.decided_by,
            reason=request.reason,
        )

        action = resume_approved_action(
            db=db,
            action_id=action.action_id,
        )

        return {
            "status": "success",
            "message": "Action approved and executed successfully",
            "action_id": action.action_id,
            "action_status": action.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post("/{action_id}/reject")
def reject_pending_action(
    action_id: int,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    """
    Reject a pending action.

    Rejection changes state only.
    """

    try:
        action = reject_action(
            db=db,
            action_id=action_id,
            decided_by=request.decided_by,
            reason=request.reason,
        )

        return {
            "status": "success",
            "message": "Action rejected successfully",
            "action_id": action.action_id,
            "action_status": action.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )