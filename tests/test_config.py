import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from phonebook.config import Settings, get_settings


@pytest.fixture
def mock_env_file(tmp_path):
    """Create a temporary .env file"""
    env_file = tmp_path / ".env"
    return env_file


@pytest.fixture
def mock_pathlib(tmp_path, monkeypatch):
    """Mock pathlib.Path to control file system access"""
    def mock_path_resolve(path):
        return path
    
    def mock_path_exists(path):
        return True
    
    def mock_path_read_text(path):
        return "HOST=test_host\nPORT=8080\nDATABASE_URL=postgresql://user:pass@localhost/db\nDEBUG=true"
    
    with patch('pathlib.Path.resolve', side_effect=mock_path_resolve):
        with patch('pathlib.Path.exists', side_effect=mock_path_exists):
            with patch('pathlib.Path.read_text', side_effect=mock_path_read_text):
                yield


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("HOST", "test_host")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    monkeypatch.setenv("DEBUG", "true")


def test_get_settings_defaults_no_env():
    """Test that get_settings() returns correct defaults when no .env exists"""
    # Mock that .env file doesn't exist
    with patch('pathlib.Path.exists', return_value=False):
        settings = get_settings()
        
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.DATABASE_URL == "sqlite:///./phonebook.db"
        assert settings.DEBUG is False


def test_get_settings_parses_env_vars():
    """Test that get_settings() correctly parses HOST, PORT, DATABASE_URL, DEBUG from .env"""
    # Mock that .env file exists and contains values
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="HOST=test_host\nPORT=8080\nDATABASE_URL=postgresql://user:pass@localhost/db\nDEBUG=true"):
            settings = get_settings()
            
            assert settings.HOST == "test_host"
            assert settings.PORT == 8080
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
            assert settings.DEBUG is True


def test_get_settings_invalid_port_value():
    """Fix broken test: Use pydantic's ValidationError"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="PORT=not_a_number"):
            with pytest.raises(ValidationError):
                get_settings()


def test_get_settings_invalid_database_url():
    """Fix broken test: Use pydantic's ValidationError"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="DATABASE_URL=invalid_url"):
            with pytest.raises(ValidationError):
                get_settings()


def test_get_settings_invalid_port_range():
    """Test settings validation for PORT out of 0-65535 range"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="PORT=70000"):
            with pytest.raises(ValueError, match="Input should be less than or equal to 65535"):
                get_settings()


def test_get_settings_invalid_database_url_format():
    """Test settings validation for invalid DATABASE_URL format"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="DATABASE_URL=not_a_valid_url"):
            with pytest.raises(ValueError, match="Invalid control character at:"):
                get_settings()


def test_get_settings_empty_env_file():
    """Test settings when .env file is empty"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value=""):
            settings = get_settings()

            assert settings.HOST == "0.0.0.0"
            assert settings.PORT == 8000
            assert settings.DATABASE_URL == "sqlite:///./phonebook.db"
            assert settings.DEBUG is False


def test_get_settings_unicode_env_vars():
    """Test settings with Unicode characters in environment variables"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value=f"HOST=Hëllo\nPORT=8080\nDATABASE_URL=sqlite:///db.sqlite3\nDEBUG=true"):
            settings = get_settings()

            assert settings.HOST == "Hëllo"
            assert settings.PORT == 8080
            assert settings.DATABASE_URL == "sqlite:///db.sqlite3"
            assert settings.DEBUG is True


def test_get_settings_invalid_hostname():
    """Test settings validation for invalid HOST format"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="HOST=invalid#hostname"):
            with pytest.raises(ValueError, match="Host name invalid#hostname is not a valid hostname"):
                get_settings()


def test_get_settings_caching():
    """Test that get_settings() caches results so multiple calls return the same instance"""
    with patch('pathlib.Path.exists', return_value=False):
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2


def test_settings_class_initialization():
    """Test Settings class initialization with default values"""
    settings = Settings()
    
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.DATABASE_URL == "sqlite:///./phonebook.db"
    assert settings.DEBUG is False


def test_settings_class_initialization_with_values():
    """Test Settings class initialization with custom values"""
    settings = Settings(
        HOST="test_host",
        PORT=8080,
        DATABASE_URL="postgresql://user:pass@localhost/db",
        DEBUG=True
    )
    
    assert settings.HOST == "test_host"
    assert settings.PORT == 8080
    assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert settings.DEBUG is True
