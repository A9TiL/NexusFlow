from app.db.session import engine, Base, SessionLocal
from app.db.models import ServerNode, NetworkLog, SupportTicket
import random

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    

    if db.query(ServerNode).first():
        print("Database already seeded. Skipping initialization.")
        db.close()
        return

    print("Seeding Server Nodes...")
    regions = ["US-East", "US-West", "EU-Central", "AP-South"]
    statuses = ["Active", "Active", "Active", "Failing", "Maintenance"]
    
    for i in range(1, 16):
        node = ServerNode(
            ip_address=f"192.168.1.{100 + i}",
            region=random.choice(regions),
            status=random.choice(statuses)
        )
        db.add(node)
    
    db.commit()
    
    print("Seeding Network Logs...")
    nodes = db.query(ServerNode).all()
    for node in nodes:

        for _ in range(3):
            is_failing = node.status == "Failing"
            log = NetworkLog(
                node_id=node.node_id,
                error_code="ERR-500" if is_failing else None,
                latency=random.uniform(300.0, 900.0) if is_failing else random.uniform(10.0, 50.0)
            )
            db.add(log)
            
    db.commit()
    print("Database seeding complete!")
    db.close()

if __name__ == "__main__":
    seed_database()