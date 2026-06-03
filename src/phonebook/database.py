"""
Database setup and session management for the RustDesk Phone Book application.

A single module-level engine and ``SessionLocal`` factory are created once at
import time (fixing the previous per-request engine churn). Tests bind their own
in-memory engine by passing it explicitly to ``init_db`` / ``SessionLocal``.
"""

from typing import Generator, Optional  # noqa: F401

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base


def _connect_args(database_url: str) -> dict:
    """SQLite needs check_same_thread disabled for the threaded uvicorn workers."""
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


# Module-level engine + session factory, created once.
_settings = get_settings()
engine = create_engine(
    _settings.DATABASE_URL,
    connect_args=_connect_args(_settings.DATABASE_URL),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(bind: Optional[object] = None) -> None:
    """
    Create all tables defined on the models' ``Base`` metadata.

    Called once on application startup (against the module engine) and from the
    test suite with an explicit in-memory engine or session.
    """
    target: object = engine
    if bind is not None:
        if isinstance(bind, Engine):
            target = bind
        elif isinstance(bind, Session):
            target = bind.get_bind()
        else:
            target = bind
    Base.metadata.create_all(bind=target)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and closes it afterwards.

    Tests inject their own session via ``app.dependency_overrides[get_db]``.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
