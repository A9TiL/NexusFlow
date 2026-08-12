from enum import Enum


class ServerStatus(str, Enum):
    ACTIVE = "Active"
    FAILING = "Failing"
    MAINTENANCE = "Maintenance"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class OperationType(str, Enum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class UserRole(str, Enum):
    READ_ONLY = "READ_ONLY"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTED = "EXECUTED"