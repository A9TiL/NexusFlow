from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class ServerNode(Base):
    __tablename__ = "server_nodes"
    
    node_id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    region = Column(String)
    status = Column(String)  # status : "Active", "Failing", "Maintenance"

class NetworkLog(Base):
    __tablename__ = "network_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("server_nodes.node_id"))
    error_code = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    latency = Column(Float)  # Latency in milliseconds

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("server_nodes.node_id"))
    issue_description = Column(String)
    priority = Column(String)  # priority : "Low", "Medium", "High"
    status = Column(String, default="Open")  # status : "Open", "Resolved"
    
class PendingAction(Base):
    __tablename__ = "pending_actions"

    action_id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False, index=True)
    operation = Column(String, nullable=False)
    requested_by = Column(String, nullable=False)
    parameters = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    decided_by = Column(String, nullable=True)
    decision_reason = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    decided_at = Column(DateTime(timezone=True),nullable=True,)
    executed_at = Column(DateTime(timezone=True),nullable=True,)