import pytest

from app.core.enums import OperationType
from app.tools.registry import ToolRegistry


def sample_read_tool():
    return "read"


def sample_unknown_tool():
    return "unknown"


def test_register_tool():
    registry = ToolRegistry()

    registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    assert registry.exists("get_server_status")


def test_get_registered_tool():
    registry = ToolRegistry()

    registered = registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    result = registry.get("get_server_status")

    assert result.name == "get_server_status"
    assert result.function is sample_read_tool
    assert result.operation == OperationType.READ
    assert result.requires_approval is False


def test_register_unknown_tool_is_rejected():
    registry = ToolRegistry()

    with pytest.raises(ValueError):
        registry.register(
            sample_unknown_tool,
        )


def test_duplicate_registration_is_rejected():
    registry = ToolRegistry()

    registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    with pytest.raises(ValueError):
        registry.register(
            sample_read_tool,
            name="get_server_status",
        )


def test_list_tools():
    registry = ToolRegistry()

    registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0].name == "get_server_status"


def test_list_tools_by_operation():
    registry = ToolRegistry()

    registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    tools = registry.list_by_operation(
        OperationType.READ
    )

    assert len(tools) == 1
    assert tools[0].name == "get_server_status"


def test_get_unregistered_tool():
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.get("does_not_exist")


def test_registry_validation():
    registry = ToolRegistry()

    registry.register(
        sample_read_tool,
        name="get_server_status",
    )

    registry.validate()
    
    
def test_nexusflow_registry_contains_all_database_tools():
    from app.tools.tool_registry import tool_registry

    expected_tools = {
        "get_server_status",
        "create_server",
        "update_server_status",
        "delete_server",
        "get_network_logs",
        "create_network_log",
        "update_network_log",
        "delete_network_log",
        "get_support_ticket",
        "create_support_ticket",
        "update_support_ticket",
        "delete_support_ticket",
    }

    actual_tools = {
        tool.name
        for tool in tool_registry.list_tools()
    }

    assert actual_tools == expected_tools


def test_nexusflow_registry_classifies_reads_correctly():
    from app.tools.tool_registry import tool_registry

    read_tools = {
        tool.name
        for tool in tool_registry.list_by_operation(
            OperationType.READ
        )
    }

    assert read_tools == {
        "get_server_status",
        "get_network_logs",
        "get_support_ticket",
    }


def test_nexusflow_registry_classifies_mutations_correctly():
    from app.tools.tool_registry import tool_registry

    mutation_tools = {
        tool.name
        for tool in tool_registry.list_tools()
        if tool.operation != OperationType.READ
    }

    assert mutation_tools == {
        "create_server",
        "create_network_log",
        "create_support_ticket",
        "update_server_status",
        "update_network_log",
        "update_support_ticket",
        "delete_server",
        "delete_network_log",
        "delete_support_ticket",
    }


def test_nexusflow_registry_requires_approval_for_mutations():
    from app.tools.tool_registry import tool_registry

    for tool in tool_registry.list_tools():

        if tool.operation == OperationType.READ:
            assert tool.requires_approval is False

        else:
            assert tool.requires_approval is True
            


def test_read_only_can_access_read_tool():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.authorize(
        "get_server_status",
        UserRole.READ_ONLY,
    )

    assert tool.name == "get_server_status"


def test_operator_can_access_update_tool():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.authorize(
        "update_server_status",
        UserRole.OPERATOR,
    )

    assert tool.name == "update_server_status"


def test_operator_cannot_access_delete_tool():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    with pytest.raises(PermissionError):
        tool_registry.authorize(
            "delete_server",
            UserRole.OPERATOR,
        )


def test_admin_can_access_delete_tool():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.authorize(
        "delete_server",
        UserRole.ADMIN,
    )

    assert tool.name == "delete_server"
    

def test_read_tool_executes_immediately():
    from app.core.enums import UserRole
    from app.tools.registry import ToolRegistry

    registry = ToolRegistry()

    def read_tool():
        return {"status": "Active"}

    registry.register(
        read_tool,
        name="get_server_status",
    )

    decision = registry.execute(
        tool_name="get_server_status",
        role=UserRole.READ_ONLY,
    )

    assert decision.tool_name == "get_server_status"
    assert decision.operation == OperationType.READ
    assert decision.requires_approval is False
    assert decision.approval_required is False
    assert decision.executed is True
    assert decision.approved is True
    assert decision.result == {"status": "Active"}


def test_mutation_does_not_execute_without_approval():
    from app.core.enums import UserRole
    from app.tools.registry import ToolRegistry

    registry = ToolRegistry()

    execution_count = {"value": 0}

    def mutation_tool():
        execution_count["value"] += 1
        return {"message": "mutation executed"}

    registry.register(
        mutation_tool,
        name="create_server",
    )

    decision = registry.execute(
        tool_name="create_server",
        role=UserRole.OPERATOR,
    )

    assert decision.tool_name == "create_server"
    assert decision.operation == OperationType.CREATE
    assert decision.requires_approval is True
    assert decision.approval_required is True
    assert decision.executed is False
    assert decision.approved is False

    assert execution_count["value"] == 0


def test_delete_requires_approval_even_for_admin():
    from app.core.enums import UserRole
    from app.tools.registry import ToolRegistry

    registry = ToolRegistry()

    execution_count = {"value": 0}

    def delete_tool():
        execution_count["value"] += 1
        return {"message": "deleted"}

    registry.register(
        delete_tool,
        name="delete_server",
    )

    decision = registry.execute(
        tool_name="delete_server",
        role=UserRole.ADMIN,
    )

    assert decision.operation == OperationType.DELETE
    assert decision.requires_approval is True
    assert decision.approval_required is True
    assert decision.executed is False

    assert execution_count["value"] == 0


def test_unauthorized_tool_never_reaches_execution():
    from app.core.enums import UserRole
    from app.tools.registry import ToolRegistry

    registry = ToolRegistry()

    execution_count = {"value": 0}

    def delete_tool():
        execution_count["value"] += 1
        return {"message": "deleted"}

    registry.register(
        delete_tool,
        name="delete_server",
    )

    with pytest.raises(PermissionError):
        registry.execute(
            tool_name="delete_server",
            role=UserRole.OPERATOR,
        )

    assert execution_count["value"] == 0


def test_unknown_tool_cannot_execute():
    from app.core.enums import UserRole
    from app.tools.registry import ToolRegistry

    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.execute(
            tool_name="destroy_everything",
            role=UserRole.ADMIN,
        )
        
def test_real_read_tool_is_governed_without_approval():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.get("get_server_status")

    assert tool.operation == OperationType.READ
    assert tool.requires_approval is False


def test_real_create_tool_is_governed_with_approval():
    from app.core.enums import UserRole
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.get("create_server")

    assert tool.operation == OperationType.CREATE
    assert tool.requires_approval is True


def test_real_update_tool_is_governed_with_approval():
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.get("update_server_status")

    assert tool.operation == OperationType.UPDATE
    assert tool.requires_approval is True


def test_real_delete_tool_is_governed_with_approval():
    from app.tools.tool_registry import tool_registry

    tool = tool_registry.get("delete_server")

    assert tool.operation == OperationType.DELETE
    assert tool.requires_approval is True