import pytest
from pydantic import ValidationError

from phonebook.config import Settings, get_settings


def test_defaults_match_env():
    """Defaults (and the repo .env, which mirrors them) load cleanly."""
    settings = Settings()
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.DATABASE_URL == "sqlite:///./phonebook.db"
    assert settings.DEBUG is False


def test_explicit_values():
    settings = Settings(
        HOST="test_host",
        PORT=8080,
        DATABASE_URL="postgresql://user:pass@localhost/db",
        DEBUG=True,
    )
    assert settings.HOST == "test_host"
    assert settings.PORT == 8080
    assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert settings.DEBUG is True


def test_environment_variables_take_precedence(monkeypatch):
    monkeypatch.setenv("HOST", "env_host")
    monkeypatch.setenv("PORT", "9090")
    monkeypatch.setenv("DEBUG", "true")
    settings = Settings()
    assert settings.HOST == "env_host"
    assert settings.PORT == 9090
    assert settings.DEBUG is True


def test_port_must_be_an_integer(monkeypatch):
    monkeypatch.setenv("PORT", "not_a_number")
    with pytest.raises(ValidationError):
        Settings()


def test_unicode_host(monkeypatch):
    monkeypatch.setenv("HOST", "Hëllo")
    assert Settings().HOST == "Hëllo"


def test_get_settings_is_cached():
    assert get_settings() is get_settings()
