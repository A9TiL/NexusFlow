from pydantic import BaseModel, Field

from app.core.enums import (
    ServerStatus,
    TicketPriority,
    TicketStatus,
)


class ServerCreateRequest(BaseModel):
    ip_address: str = Field(
        min_length=7,
        max_length=45,
    )
    region: str = Field(
        min_length=1,
        max_length=100,
    )
    status: ServerStatus = ServerStatus.ACTIVE


class ServerUpdateRequest(BaseModel):
    node_id: int = Field(gt=0)
    status: ServerStatus


class ServerDeleteRequest(BaseModel):
    node_id: int = Field(gt=0)


class NetworkLogCreateRequest(BaseModel):
    node_id: int = Field(gt=0)
    error_code: str | None = None
    latency: float = Field(ge=0)


class NetworkLogUpdateRequest(BaseModel):
    log_id: int = Field(gt=0)
    error_code: str | None = None
    latency: float | None = Field(
        default=None,
        ge=0,
    )


class NetworkLogDeleteRequest(BaseModel):
    log_id: int = Field(gt=0)


class SupportTicketCreateRequest(BaseModel):
    node_id: int = Field(gt=0)
    issue: str = Field(
        min_length=1,
        max_length=1000,
    )
    priority: TicketPriority


class SupportTicketUpdateRequest(BaseModel):
    ticket_id: int = Field(gt=0)
    issue: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


class SupportTicketDeleteRequest(BaseModel):
    ticket_id: int = Field(gt=0)