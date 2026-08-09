from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./nexusflow.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # strictly required for SQLite in FastAPI to allow multiple web requests to share the same connection.
)

# this will be spawning new sessions for each request to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency Injection function.
    Yields a database session to a FastAPI route and safely closes it afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()