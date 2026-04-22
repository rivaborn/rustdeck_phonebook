# src/phonebook/database.py

## Purpose
Handles database engine creation, session management, and initialization for the RustDesk Phone Book application using SQLAlchemy.

## Responsibilities
- Create and configure SQLAlchemy database engines and sessions
- Initialize database tables on application startup
- Manage database session lifecycle with context management
- Provide dependency injection for database sessions
- Configure database connection parameters based on URL type

## Key Types
- Base (DeclarativeMeta): SQLAlchemy base class for database models

## Key Functions
### create_engine
- Purpose: Creates a SQLAlchemy engine instance with specified connection parameters
- Calls: None

### get_sessionmaker
- Purpose: Creates a SQLAlchemy sessionmaker bound to a specific engine
- Calls: None

### get_settings_instance
- Purpose: Retrieves application settings including database configuration
- Calls: get_settings()

### init_db
- Purpose: Initializes the database by creating all defined tables
- Calls: create_engine, get_settings_instance

### get_db
- Purpose: Provides a database session generator for request handling
- Calls: create_engine, get_sessionmaker, get_settings_instance

## Globals
- Base (DeclarativeMeta): SQLAlchemy base class imported from models module

## Dependencies
- sqlalchemy (create_engine, sessionmaker, declarative_base)
- phonebook.config.get_settings
- phonebook.models.Base
- contextlib.contextmanager
- typing.Generator
- sqlalchemy.orm.Session
