import pytest

from app.core.authorization import (
    authorize,
    is_authorized,
)
from app.core.enums import (
    OperationType,
    UserRole,
)


def test_read_only_can_read():
    assert is_authorized(
        UserRole.READ_ONLY,
        OperationType.READ,
    )


def test_read_only_cannot_create():
    assert not is_authorized(
        UserRole.READ_ONLY,
        OperationType.CREATE,
    )


def test_read_only_cannot_update():
    assert not is_authorized(
        UserRole.READ_ONLY,
        OperationType.UPDATE,
    )


def test_read_only_cannot_delete():
    assert not is_authorized(
        UserRole.READ_ONLY,
        OperationType.DELETE,
    )


def test_operator_can_read():
    assert is_authorized(
        UserRole.OPERATOR,
        OperationType.READ,
    )


def test_operator_can_create():
    assert is_authorized(
        UserRole.OPERATOR,
        OperationType.CREATE,
    )


def test_operator_can_update():
    assert is_authorized(
        UserRole.OPERATOR,
        OperationType.UPDATE,
    )


def test_operator_cannot_delete():
    assert not is_authorized(
        UserRole.OPERATOR,
        OperationType.DELETE,
    )


def test_admin_can_read():
    assert is_authorized(
        UserRole.ADMIN,
        OperationType.READ,
    )


def test_admin_can_create():
    assert is_authorized(
        UserRole.ADMIN,
        OperationType.CREATE,
    )


def test_admin_can_update():
    assert is_authorized(
        UserRole.ADMIN,
        OperationType.UPDATE,
    )


def test_admin_can_delete():
    assert is_authorized(
        UserRole.ADMIN,
        OperationType.DELETE,
    )


def test_unauthorized_operation_raises_permission_error():

    with pytest.raises(PermissionError):
        authorize(
            role=UserRole.OPERATOR,
            operation=OperationType.DELETE,
        )