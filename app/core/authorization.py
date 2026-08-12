from app.core.enums import OperationType, UserRole


ROLE_PERMISSIONS: dict[UserRole, set[OperationType]] = {
    UserRole.READ_ONLY: {
        OperationType.READ,
    },

    UserRole.OPERATOR: {
        OperationType.READ,
        OperationType.CREATE,
        OperationType.UPDATE,
    },

    UserRole.ADMIN: {
        OperationType.READ,
        OperationType.CREATE,
        OperationType.UPDATE,
        OperationType.DELETE,
    },
}


def is_authorized(
    role: UserRole,
    operation: OperationType,
) -> bool:
    """
    Determine whether a role is authorized
    to perform an operation.
    """

    return operation in ROLE_PERMISSIONS.get(role, set())


def authorize(
    role: UserRole,
    operation: OperationType,
) -> None:
    """
    Enforce authorization for an operation.

    Raises:
        PermissionError: if the role is not authorized.
    """

    if not is_authorized(role, operation):
        raise PermissionError(
            f"Role '{role.value}' is not authorized "
            f"to perform '{operation.value}' operations."
        )