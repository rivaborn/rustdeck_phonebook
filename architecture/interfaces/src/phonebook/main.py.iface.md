# Module: src/phonebook/main.py

## Role
Creates and configures a FastAPI application instance for the RustDesk Phone Book with database initialization and routing.

## Contract: Module-level functions

### `create_app() -> FastAPI`
- **Requires:** `src.phonebook.config.get_settings()` must be callable and return a settings object with a `DEBUG` attribute
- **Guarantees:** Returns a configured FastAPI app instance with title "RustDesk Phone Book", version "0.1.0", debug flag set from settings, registered routers, and static file mount
- **Raises:** `TypeError` — if `get_settings()` does not return a valid settings object with `DEBUG` attribute
- **Silent failure:** None
- **Thread safety:** Safe

### `lifespan(app: FastAPI) -> AsyncGenerator[None, None]`
- **Requires:** `src.phonebook.database.init_db()` must be callable and not raise exceptions during execution
- **Guarantees:** Yields control to the FastAPI application after database initialization, and performs no cleanup on shutdown
- **Raises:** Any exception raised by `init_db()` will propagate to the caller
- **Silent failure:** None
- **Thread safety:** Safe

## Module Invariants
The module maintains a global `app` instance that is fully configured and ready for use after import.

## Resource Lifecycle
- Database connection is initialized via `init_db()` during lifespan startup
- No explicit cleanup is performed on application shutdown
- Static file system paths are resolved at import time
- Template directory is resolved at import time
