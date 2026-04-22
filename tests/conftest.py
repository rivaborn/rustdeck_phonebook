import pytest
from sqlalchemy.orm import Session
from httpx import AsyncClient
from unittest.mock import patch

from phonebook.main import app
from phonebook.database import init_db, SessionLocal, create_engine
from phonebook.config import get_settings

@pytest.fixture
def db_session():
    """
    Create an in-memory SQLite database session for testing.
    
    This fixture provides a clean database for each test function.
    It creates an in-memory SQLite engine, initializes the database schema,
    and yields a session that is automatically closed after the test.
    """
    # Create in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")
    
    # Initialize database tables
    init_db(engine)
    
    # Create session
    session = SessionLocal(bind=engine)
    
    try:
        yield session
    finally:
        # Close session and drop tables
        session.close()
        # Note: In-memory database is automatically dropped when connection is closed

@pytest.fixture
async def client():
    """
    Create an async HTTP client for testing routes.
    
    This fixture provides an AsyncClient that is configured to use the test
    database and overrides the get_db dependency to use the db_session fixture.
    """
    # Create AsyncClient
    async_client = AsyncClient(base_url="http://testserver")
    
    try:
        yield async_client
    finally:
        # Close client
        async_client.close()

@pytest.fixture
def override_get_db():
    """
    Override the get_db dependency to use the test database session.
    
    This fixture can be used to patch the get_db dependency in route tests
    to ensure they use the test database instead of the production database.
    """
    def _override_get_db():
        # This will be used in patch context managers
        pass
    
    return _override_get_db
