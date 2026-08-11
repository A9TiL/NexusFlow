import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.db.models import ServerNode, NetworkLog, SupportTicket


@pytest.fixture
def db_session():
    """
    Creates an isolated in-memory SQLite database
    for each test.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)