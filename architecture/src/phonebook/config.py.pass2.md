# src/phonebook/config.py - Enhanced Analysis

## Architectural Role
Manages application configuration loading and caching, serving as a central settings provider for the phonebook application's dependency injection system.

## Cross-References
### Incoming
- `src/phonebook/main.py` (imports `get_settings` to access configuration in app startup)
- `src/phonebook/database.py` (imports `get_settings` to access DATABASE_URL for session creation)

### Outgoing
- `pydantic_settings.BaseSettings` (configuration schema validation and parsing)
- `functools.lru_cache` (caching mechanism for settings instance)

## Design Patterns
- **Singleton Pattern**: `get_settings` function provides a single cached instance, ensuring consistent configuration access throughout the application lifecycle
- **Factory Pattern**: `get_settings` acts as a factory function that creates and returns a `Settings` instance with parsed environment variables
- **Configuration Loading Pattern**: Uses Pydantic's settings management with environment file fallback, enabling flexible deployment configurations
