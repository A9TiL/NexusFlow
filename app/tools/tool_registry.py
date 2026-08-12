from app.tools.registry import ToolRegistry

from app.tools.database_tools import (
    get_server_status,
    create_server,
    update_server_status,
    delete_server,
    get_network_logs,
    create_network_log,
    update_network_log,
    delete_network_log,
    get_support_ticket,
    create_support_ticket,
    update_support_ticket,
    delete_support_ticket,
)


tool_registry = ToolRegistry()


tool_registry.register(get_server_status)
tool_registry.register(create_server)
tool_registry.register(update_server_status)
tool_registry.register(delete_server)



tool_registry.register(get_network_logs)
tool_registry.register(create_network_log)
tool_registry.register(update_network_log)
tool_registry.register(delete_network_log)




tool_registry.register(get_support_ticket)
tool_registry.register(create_support_ticket)
tool_registry.register(update_support_ticket)
tool_registry.register(delete_support_ticket)



tool_registry.validate()