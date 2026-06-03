import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool

from phonebook.config import get_settings  # noqa: F401 (kept for tests importing via conftest)
from phonebook.database import SessionLocal, create_engine, get_db, init_db
from phonebook.main import app


@pytest.fixture
def db_session():
    """A clean in-memory SQLite session shared across one test.

    StaticPool keeps every connection pointed at the same in-memory database so
    the tables created by ``init_db`` are visible to the session (and to routes
    that reuse this session via the dependency override below).
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    session = SessionLocal(bind=engine)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
async def client(db_session):
    """Async HTTP client wired to the app, with get_db overridden to db_session."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
