import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from phonebook.database import SessionLocal, create_engine, engine, get_db, init_db


def _memory_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_module_engine_and_sessionlocal_exist():
    """The module exposes a singleton engine and a session factory."""
    assert engine is not None
    session = SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_init_db_creates_tables_with_engine():
    eng = _memory_engine()
    init_db(eng)
    assert "computers" in inspect(eng).get_table_names()


def test_init_db_accepts_session_bind():
    """init_db resolves a Session to its underlying engine without raising."""
    eng = _memory_engine()
    session = SessionLocal(bind=eng)
    try:
        init_db(session)
        assert "computers" in inspect(eng).get_table_names()
    finally:
        session.close()


def test_init_db_defaults_to_module_engine():
    # Should not raise when called with no argument (uses the module engine).
    init_db()


def test_get_db_yields_then_closes():
    gen = get_db()
    db = next(gen)
    assert hasattr(db, "query")
    # Exhausting the generator runs the finally-block that closes the session.
    with pytest.raises(StopIteration):
        next(gen)
