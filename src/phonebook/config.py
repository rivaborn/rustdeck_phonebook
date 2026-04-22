from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./phonebook.db"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
    """
    1. Use lru_cache decorator to memoize results.
    2. Create and return a new Settings instance by parsing environment variables.
    3. If environment file is missing, use default values.
    """
    return Settings()
