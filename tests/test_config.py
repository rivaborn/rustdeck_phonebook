import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from phonebook.config import Settings, get_settings, SettingsError


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


def test_get_settings_raises_error_invalid_port():
    """Test that get_settings() raises SettingsError when PORT is not a valid integer"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="PORT=not_a_number"):
            with pytest.raises(SettingsError, match="Invalid PORT value"):
                get_settings()


def test_get_settings_raises_error_malformed_database_url():
    """Test that get_settings() raises SettingsError when DATABASE_URL is malformed"""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="DATABASE_URL=not_a_valid_url"):
            with pytest.raises(SettingsError, match="Invalid DATABASE_URL"):
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
