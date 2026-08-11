import pytest

from app.core.enums import OperationType
from app.core.operation_policy import (
    get_tool_policy,
    requires_approval,
)


def test_read_tool_does_not_require_approval():
    policy = get_tool_policy("get_server_status")

    assert policy is not None
    assert policy.operation == OperationType.READ
    assert policy.requires_approval is False


def test_create_tool_requires_approval():
    policy = get_tool_policy("create_support_ticket")

    assert policy is not None
    assert policy.operation == OperationType.CREATE
    assert policy.requires_approval is True


def test_update_tool_requires_approval():
    policy = get_tool_policy("update_server_status")

    assert policy is not None
    assert policy.operation == OperationType.UPDATE
    assert policy.requires_approval is True


def test_delete_tool_requires_approval():
    policy = get_tool_policy("delete_server")

    assert policy is not None
    assert policy.operation == OperationType.DELETE
    assert policy.requires_approval is True


def test_unknown_tool_has_no_policy():
    assert get_tool_policy("does_not_exist") is None


def test_unknown_tool_raises_when_checking_approval():
    with pytest.raises(ValueError):
        requires_approval("does_not_exist")