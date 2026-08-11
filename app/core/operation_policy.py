from dataclasses import dataclass

from app.core.enums import OperationType


@dataclass(frozen=True)
class ToolPolicy:
    """
    Defines the security policy associated with a tool.
    """

    name: str
    operation: OperationType
    requires_approval: bool


TOOL_POLICIES = {

    "get_server_status": ToolPolicy(
        name="get_server_status",
        operation=OperationType.READ,
        requires_approval=False,
    ),

    "get_network_logs": ToolPolicy(
        name="get_network_logs",
        operation=OperationType.READ,
        requires_approval=False,
    ),

    "get_support_ticket": ToolPolicy(
        name="get_support_ticket",
        operation=OperationType.READ,
        requires_approval=False,
    ),


    "create_server": ToolPolicy(
        name="create_server",
        operation=OperationType.CREATE,
        requires_approval=True,
    ),

    "create_network_log": ToolPolicy(
        name="create_network_log",
        operation=OperationType.CREATE,
        requires_approval=True,
    ),

    "create_support_ticket": ToolPolicy(
        name="create_support_ticket",
        operation=OperationType.CREATE,
        requires_approval=True,
    ),



    "update_server_status": ToolPolicy(
        name="update_server_status",
        operation=OperationType.UPDATE,
        requires_approval=True,
    ),

    "update_network_log": ToolPolicy(
        name="update_network_log",
        operation=OperationType.UPDATE,
        requires_approval=True,
    ),

    "update_support_ticket": ToolPolicy(
        name="update_support_ticket",
        operation=OperationType.UPDATE,
        requires_approval=True,
    ),



    "delete_server": ToolPolicy(
        name="delete_server",
        operation=OperationType.DELETE,
        requires_approval=True,
    ),

    "delete_network_log": ToolPolicy(
        name="delete_network_log",
        operation=OperationType.DELETE,
        requires_approval=True,
    ),

    "delete_support_ticket": ToolPolicy(
        name="delete_support_ticket",
        operation=OperationType.DELETE,
        requires_approval=True,
    ),
}


def get_tool_policy(tool_name: str) -> ToolPolicy | None:
    """
    Return the policy associated with a tool.
    """

    return TOOL_POLICIES.get(tool_name)


def requires_approval(tool_name: str) -> bool:
    """
    Determine whether a tool requires human approval.
    """

    policy = get_tool_policy(tool_name)

    if policy is None:
        raise ValueError(
            f"No security policy registered for tool: {tool_name}"
        )

    return policy.requires_approval