from datetime import datetime, timezone
import json

from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus, UserRole
from app.db.models import PendingAction
from app.tools.tool_registry import tool_registry


def resume_approved_action(
    db: Session,
    action_id: int,
) -> PendingAction:
    """
    Resume and execute an already-approved mutation.

    This function is the bridge between the HITL approval state
    and the actual tool execution layer.

    Execution is allowed only when:
        PendingAction.status == APPROVED
    """

    action = (
        db.query(PendingAction)
        .filter(PendingAction.action_id == action_id)
        .first()
    )

    if action is None:
        raise ValueError(
            f"Pending action {action_id} not found."
        )

    if action.status != ApprovalStatus.APPROVED.value:
        raise ValueError(
            f"Action {action_id} cannot be resumed "
            f"because its current status is "
            f"'{action.status}'."
        )
        
    try:
        role = UserRole(action.requested_by)
    except ValueError:
        raise ValueError(
            f"Invalid user role stored for action {action_id}: "
            f"{action.requested_by}"
        )

    try:
        parameters = json.loads(action.parameters)
    except (json.JSONDecodeError, TypeError):
        raise ValueError(
            f"Invalid parameters stored for action {action_id}."
        )

    if not isinstance(parameters, dict):
        raise ValueError(
            f"Parameters for action {action_id} "
            f"must decode to an object."
        )

    decision = tool_registry.execute_approved(
        tool_name=action.tool_name,
        role=role,
        db=db,
        **parameters,
    )

    if not decision.executed:
        raise RuntimeError(
            f"Approved action {action_id} "
            f"was not executed."
        )

    action.status = ApprovalStatus.EXECUTED.value
    action.executed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(action)

    return action