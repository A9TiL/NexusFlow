from dataclasses import dataclass
from typing import Callable, Any

from app.core.enums import OperationType, UserRole
from app.core.authorization import authorize
from app.core.operation_policy import (
    ToolPolicy,
    get_tool_policy,
)


@dataclass(frozen=True)
class RegisteredTool:
    """
    Represents a tool registered with NexusFlow.

    A RegisteredTool connects the actual callable implementation
    with its security policy.
    """

    name: str
    function: Callable[..., Any]
    policy: ToolPolicy

    @property
    def operation(self) -> OperationType:
        return self.policy.operation

    @property
    def requires_approval(self) -> bool:
        return self.policy.requires_approval

@dataclass(frozen=True)
class ToolExecutionDecision:
    """
    Represents the governance decision for a tool invocation.

    A tool may be:
    - EXECUTED immediately
    - blocked because human approval is required
    """

    tool_name: str
    operation: OperationType
    approved: bool
    requires_approval: bool
    executed: bool
    result: Any = None

    @property
    def approval_required(self) -> bool:
        return self.requires_approval and not self.executed
    

class ToolRegistry:
    """
    Central registry for all tools exposed to the agent.

    The registry is responsible for:
    - registering tools
    - looking up tools
    - validating policy coverage
    - listing registered tools
    """
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        function: Callable[..., Any],
        name: str | None = None,
    ) -> RegisteredTool:
        """
        Register a callable as a NexusFlow tool.
        The tool must have a corresponding entry in TOOL_POLICIES.
        """
        tool_name = name or function.__name__

        if tool_name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool_name}"
            )
        policy = get_tool_policy(tool_name)
        if policy is None:
            raise ValueError(
                f"No security policy registered for tool: {tool_name}"
            )

        if policy.name != tool_name:
            raise ValueError(
                f"Tool policy name mismatch for: {tool_name}"
            )
        registered_tool = RegisteredTool(
            name=tool_name,
            function=function,
            policy=policy,
        )
        self._tools[tool_name] = registered_tool
        return registered_tool

    def get(self, tool_name: str) -> RegisteredTool:
        """
        Retrieve a registered tool.
        Raises:
            KeyError: if the tool is not registered.
        """
        tool = self._tools.get(tool_name)

        if tool is None:
            raise KeyError(
                f"Tool not registered: {tool_name}"
            )
        return tool

    def exists(self, tool_name: str) -> bool:
        """
        Check whether a tool is registered.
        """
        return tool_name in self._tools

    def list_tools(self) -> list[RegisteredTool]:
        """
        Return all registered tools.
        """
        return list(self._tools.values())

    def list_by_operation(
        self,
        operation: OperationType,) -> list[RegisteredTool]:
        """
        Return tools belonging to a specific operation type.
        """
        return [
            tool
            for tool in self._tools.values()
            if tool.operation == operation
        ]
        
    def authorize(self,tool_name: str,role: UserRole,) -> RegisteredTool:
        """
        Authorize a role to execute a registered tool.
        Returns the registered tool if authorization succeeds.
        Raises:
            KeyError: if the tool does not exist.
            PermissionError: if the role is not authorized.
        """
        tool = self.get(tool_name)
        authorize( role=role, operation=tool.operation,)
        return tool
    
    def execute(self,tool_name: str,role: UserRole,**kwargs: Any, ) -> ToolExecutionDecision:
        """
        Govern and execute a registered tool.
        READ operations that are authorized and do not require
        approval execute immediately.
        Authorized mutation operations that require approval
        are blocked and returned as APPROVAL_REQUIRED.
        Unauthorized operations raise PermissionError.
        Unknown tools raise KeyError.
        """

        tool = self.authorize(
            tool_name=tool_name,
            role=role,
        )

        if tool.requires_approval:
            return ToolExecutionDecision(
                tool_name=tool.name,
                operation=tool.operation,
                approved=False,
                requires_approval=True,
                executed=False,
                result=None,
            )

        result = tool.function(**kwargs)

        return ToolExecutionDecision(
            tool_name=tool.name,
            operation=tool.operation,
            approved=True,
            requires_approval=False,
            executed=True,
            result=result,
        )

    def execute_approved(
    self,
    tool_name: str,
    role: UserRole,
    **kwargs: Any,) -> ToolExecutionDecision:
        """
        Execute a mutation that has already passed the HITL approval stage.

        This method is intended for the workflow-resume path only.

        It still performs tool lookup and authorization, but it does not
        apply the normal "requires approval" block because approval has
        already been established by the HITL workflow.
        """

        tool = self.authorize(
            tool_name=tool_name,
            role=role,
        )

        if not tool.requires_approval:
            raise ValueError(
                f"Tool does not require approval: {tool_name}"
            )

        result = tool.function(**kwargs)

        return ToolExecutionDecision(
            tool_name=tool.name,
            operation=tool.operation,
            approved=True,
            requires_approval=True,
            executed=True,
            result=result,
        )
    
    def validate(self) -> None:
        """
        Validate registry consistency.

        Every registered tool must:
        - have a policy
        - have matching names
        """

        for name, tool in self._tools.items():

            if tool.policy is None:
                raise ValueError(
                    f"Tool has no policy: {name}"
                )

            if tool.policy.name != name:
                raise ValueError(
                    f"Policy mismatch for tool: {name}"
                )