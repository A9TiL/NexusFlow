from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus
from app.db.models import PendingAction


def create_pending_action(
    db: Session,
    tool_name: str,
    operation: str,
    requested_by: str,
    parameters: str,) -> PendingAction:
    """
    Create a new action waiting for human approval.
    """
    action = PendingAction(
        tool_name=tool_name,
        operation=operation,
        requested_by=requested_by,
        parameters=parameters,
        status=ApprovalStatus.PENDING.value,)

    db.add(action)
    db.commit()
    db.refresh(action)
    return action

def get_pending_action(
    db: Session,
    action_id: int,) -> PendingAction | None:
    """
    Retrieve a pending action by ID.
    """
    return (
        db.query(PendingAction).filter(PendingAction.action_id == action_id).first())

def approve_action(
    db: Session,
    action_id: int,
    decided_by: str,
    reason: str | None = None,
) -> PendingAction:
    """
    Approve a pending action.

    Approval changes state only.
    It does NOT execute the underlying tool.
    """
    action = get_pending_action(
        db=db,
        action_id=action_id,)

    if action is None:
        raise ValueError(
            f"Pending action {action_id} not found.")

    if action.status != ApprovalStatus.PENDING.value:
        raise ValueError(
            f"Action {action_id} cannot be approved "
            f"because its current status is "
            f"'{action.status}'.")

    action.status = ApprovalStatus.APPROVED.value
    action.decided_by = decided_by
    action.decision_reason = reason

    db.commit()
    db.refresh(action)
    return action


def reject_action(
    db: Session,
    action_id: int,
    decided_by: str,
    reason: str | None = None,
) -> PendingAction:
    """
    Reject a pending action.

    Rejection changes state only.
    It does NOT execute anything.
    """

    action = get_pending_action(db=db,action_id=action_id,)

    if action is None:
        raise ValueError(
            f"Pending action {action_id} not found."
        )

    if action.status != ApprovalStatus.PENDING.value:
        raise ValueError(
            f"Action {action_id} cannot be rejected "
            f"because its current status is "
            f"'{action.status}'.")

    action.status = ApprovalStatus.REJECTED.value
    action.decided_by = decided_by
    action.decision_reason = reason

    db.commit()
    db.refresh(action)
    return action