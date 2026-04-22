# src/phonebook/main.py - Enhanced Analysis

## Architectural Role
Serves as the central application factory and lifecycle manager for the RustDesk Phone Book backend. Acts as the entry point for FastAPI application configuration and coordinates database initialization and routing setup.

## Cross-References
### Incoming
- `src/phonebook/__main__.py` (imports `app` global)
- `src/phonebook/database.py` (called by `lifespan` for initialization)
- `src/phonebook/config.py` (called by `create_app` for settings)

### Outgoing
- `src/phonebook/routes/computers.py` (imports `computers.router`)
- `src/phonebook/routes/export.py` (imports `export.router`)
- `src/phonebook/database.py` (called by `lifespan` for initialization)
- `src/phonebook/config.py` (called by `create_app` for settings)

## Design Patterns
- **Factory Pattern**: `create_app()` function encapsulates application creation logic
- **Dependency Injection**: Configuration and database initialization are injected through function calls
- **Lifespan Management**: Uses FastAPI's lifespan context manager for proper startup/shutdown handling
