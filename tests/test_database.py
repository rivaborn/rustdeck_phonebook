import pytest
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from phonebook.database import init_db, get_db, create_engine, get_sessionmaker, get_settings_instance
from phonebook.config import get_settings


def test_init_db_with_postgresql_url():
    """Test database initialization with PostgreSQL URL"""
    with patch("phonebook.database.create_engine") as mock_engine:
        with patch("phonebook.database.Base.metadata.create_all") as mock_create_all:
            mock_engine.return_value = Mock()
            init_db("postgresql://user:pass@localhost/dbname")
            
            mock_engine.assert_called_once_with("postgresql://user:pass@localhost/dbname", connect_args={})
            mock_create_all.assert_called_once_with(bind=mock_engine.return_value)


def test_init_db_with_invalid_url_raises():
    """Test that init_db raises exception for invalid URL"""
    with patch("phonebook.database.create_engine") as mock_engine:
        mock_engine.side_effect = SQLAlchemyError("Invalid URL")
        with pytest.raises(SQLAlchemyError):
            init_db("invalid://url")


def test_get_db_yields_and_closes_session():
    """Test session generation, yield, and cleanup in get_db"""
    with patch("phonebook.database.SessionLocal") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        with get_db() as db:
            assert db == mock_session
            mock_session.commit.assert_not_called()
        
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


def test_get_db_handles_commit_error():
    """Test error handling during commit in get_db"""
    with patch("phonebook.database.SessionLocal") as mock_session_class:
        mock_session = Mock()
        mock_session.commit.side_effect = Exception("Commit failed")
        mock_session.rollback.return_value = None
        mock_session_class.return_value = mock_session
        
        with pytest.raises(Exception, match="Commit failed"):
            with get_db():
                pass
        
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


def test_create_engine_with_connect_args():
    """Test engine creation with custom connection arguments"""
    with patch("phonebook.database.sqlalchemy.create_engine") as mock_sa_engine:
        engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
        
        mock_sa_engine.assert_called_once_with("sqlite:///test.db", connect_args={"check_same_thread": False})
        assert engine == mock_sa_engine.return_value


def test_create_engine_empty_connect_args():
    """Test default engine creation with empty connect arguments"""
    with patch("phonebook.database.sqlalchemy.create_engine") as mock_sa_engine:
        engine = create_engine("sqlite:///test.db")
        
        mock_sa_engine.assert_called_once_with("sqlite:///test.db", connect_args={})


def test_get_sessionmaker_with_settings():
    """Test sessionmaker creation with given settings"""
    with patch("phonebook.database.sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value = Mock()
        sessionmaker_instance = get_sessionmaker(autocommit=False, autoflush=True, bind=Mock())
        
        mock_sessionmaker.assert_called_once_with(autocommit=False, autoflush=True, bind=Mock())
        assert sessionmaker_instance == mock_sessionmaker.return_value


def test_get_settings_instance_returns_settings():
    """Test settings retrieval returns valid settings object"""
    settings = get_settings_instance()
    assert settings is not None
    assert hasattr(settings, 'DATABASE_URL')
    assert hasattr(settings, 'HOST')
    assert hasattr(settings, 'PORT')
    assert hasattr(settings, 'DEBUG')


def test_get_settings_instance_with_missing_config():
    """Test settings fallback behavior with missing config"""
    with patch("phonebook.config.get_settings") as mock_get_settings:
        mock_get_settings.side_effect = Exception("Config error")
        settings = get_settings_instance()
        assert settings is not None  # Should fall back to defaults
