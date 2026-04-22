"""
Database setup and session management for the RustDesk Phone Book application.
This module handles database engine creation, session management, and initialization.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from phonebook.config import get_settings
from urllib.parse import urlparse

# Create the SQLAlchemy engine
def create_engine(database_url: str, connect_args: dict) -> object:
    """
    Create a SQLAlchemy engine for the database.
    
    Args:
        database_url: The database URL to connect to
        connect_args: Additional arguments for the database connection
        
    Returns:
        Engine: A SQLAlchemy engine instance
    """
    return create_engine(database_url, connect_args=connect_args)

# Create the sessionmaker
def get_sessionmaker(autocommit: bool, autoflush: bool, bind: object) -> object:
    """
    Create a SQLAlchemy sessionmaker.
    
    Args:
        autocommit: Whether to autocommit transactions
        autoflush: Whether to autoflush sessions
        bind: The engine to bind the sessionmaker to
        
    Returns:
        SessionLocal: A SQLAlchemy sessionmaker instance
    """
    return sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=bind)

# Get settings
def get_settings_instance() -> object:
    """
    Get the application settings.
    
    Returns:
        Settings: The application settings instance
    """
    return get_settings()

# Initialize database
def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models module.
    It should be called once during application startup.
    """
    # Get the database URL from settings
    settings = get_settings_instance()
    
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL must be configured")
    
    # Create the engine with appropriate connection arguments
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error here if logging is implemented
        raise

# Get database session
def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for the current request.
    
    This is a dependency that yields a database session and ensures it's closed
    after the request is processed.
    
    Yields:
        Session: A SQLAlchemy database session
    """
    # Get the database URL from settings
    settings = get_settings_instance()
    
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL must be configured")
    
    # Create the engine once
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    
    # Create a sessionmaker
    SessionLocal = get_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Yield the session to the caller
        yield db
    except Exception:
        # Ensure engine cleanup on exceptions
        engine.dispose()
        raise
    finally:
        # Ensure the session is closed
        db.close()

# Import Base from models module
from phonebook.models import Base
