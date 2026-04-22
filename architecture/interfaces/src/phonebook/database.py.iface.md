# Module: src/phonebook/database.py

## Role
Provides database engine creation, session management, and initialization for the RustDesk Phone Book application using SQLAlchemy.

## Contract: Module-level functions

### `create_engine(database_url: str, connect_args: dict) -> object`
- **Requires:** `database_url` must be a valid string URL for a database connection; `connect_args` must be a dictionary of valid connection arguments
- **Guarantees:** Returns a SQLAlchemy Engine instance configured with the provided parameters
- **Raises:** `sqlalchemy.exc.ArgumentError` -- if `database_url` is invalid or `connect_args` contains invalid parameters
- **Silent failure:** None
- **Thread safety:** Safe

### `get_sessionmaker(autocommit: bool, autoflush: bool, bind: object) -> object`
- **Requires:** `autocommit` and `autoflush` must be boolean values; `bind` must be a valid SQLAlchemy Engine instance
- **Guarantees:** Returns a SQLAlchemy sessionmaker configured with the provided parameters
- **Raises:** `sqlalchemy.exc.ArgumentError` -- if `bind` is not a valid Engine instance or parameters are invalid
- **Silent failure:** None
- **Thread safety:** Safe

### `get_settings_instance() -> object`
- **Requires:** `phonebook.config.get_settings()` function must be available and return a valid settings object
- **Guarantees:** Returns the application settings instance
- **Raises:** Any exception raised by `phonebook.config.get_settings()` -- typically `AttributeError` or `ImportError` if config module is missing
- **Silent failure:** None
- **Thread safety:** Safe

### `init_db() -> None`
- **Requires:** `phonebook.config.get_settings()` must return a valid settings object with a `DATABASE_URL` attribute; `Base` from `phonebook.models` must be properly initialized
- **Guarantees:** Creates all database tables defined in the models module
- **Raises:** `sqlalchemy.exc.OperationalError` -- if database connection fails or `Base.metadata.create_all()` fails
- **Silent failure:** None
- **Thread safety:** Unsafe (modifies global database state)

### `get_db() -> Generator[Session, None, None]`
- **Requires:** `phonebook.config.get_settings()` must return a valid settings object with a `DATABASE_URL` attribute; `Base` from `phonebook.models` must be properly initialized
- **Guarantees:** Yields a SQLAlchemy database session that will be automatically closed after use
- **Raises:** `sqlalchemy.exc.OperationalError` -- if database connection fails or session creation fails
- **Silent failure:** None
- **Thread safety:** Unsafe (creates per-request sessions)

## Module Invariants
- The `Base` object from `phonebook.models` is properly initialized and contains all table definitions
- Database connection parameters are consistently retrieved from application settings
- Session lifecycle is properly managed with automatic closing

## Resource Lifecycle
- Database engine is created on-demand and reused across sessions
- Database sessions are created per-request and automatically closed
- SQLite connections use `check_same_thread=False` when appropriate
- No explicit resource cleanup required beyond automatic session closing
