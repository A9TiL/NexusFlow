from sqlalchemy.orm import Session
from app.db.models import ServerNode, NetworkLog, SupportTicket

def get_server_status(db: Session, node_id: int) -> dict:
    """Fetches the current status and region of a specific server node."""
    node = db.query(ServerNode).filter(ServerNode.node_id == node_id).first()
    if not node:
        return {"error": f"Node {node_id} not found in the database."}
    
    return {
        "node_id": node.node_id, 
        "ip": node.ip_address, 
        "status": node.status, 
        "region": node.region
    }

def get_network_logs(db: Session, node_id: int, limit: int = 5) -> list:
    """Retrieves recent diagnostic logs for a server node to check for latency or errors."""
    logs = db.query(NetworkLog).filter(NetworkLog.node_id == node_id).order_by(NetworkLog.timestamp.desc()).limit(limit).all()
    if not logs:
        return [{"message": f"No network logs found for Node {node_id}."}]
    
    return [
        {"log_id": log.log_id, "error": log.error_code, "latency": log.latency, "timestamp": str(log.timestamp)} 
        for log in logs
    ]

def create_support_ticket(db: Session, node_id: int, issue: str, priority: str) -> dict:
    """Logs a new support ticket into the system for a failing or degraded node."""
    ticket = SupportTicket(
        node_id=node_id, 
        issue_description=issue, 
        priority=priority
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket) # Refreshes the object to get the newly auto-generated ticket_id
    
    return {
        "message": "Ticket created successfully", 
        "ticket_id": ticket.ticket_id, 
        "status": ticket.status
    }