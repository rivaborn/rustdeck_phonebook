# Module: src/phonebook/config.py

## Role
Provides configuration management using Pydantic settings with environment variable support and caching.

## Contract: Settings

### `__init__(params)`
- **Requires:** No parameters required; all fields have default values
- **Establishes:** Instance with validated fields; HOST defaults to "0.0.0.0", PORT to 8000, DATABASE_URL to "sqlite:///./phonebook.db", DEBUG to False
- **Raises:** ValidationError if environment variables fail validation

### `model_config`
- **Requires:** None
- **Guarantees:** Configuration object with env_file=".env" and env_file_encoding="utf-8"
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe

## Contract: get_settings() -> Settings

### `get_settings() -> Settings`
- **Requires:** Environment file ".env" may exist but is not required; if missing, defaults are used
- **Guarantees:** Returns a Settings instance with validated configuration values
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe (due to lru_cache decorator)

## Module Invariants
Settings instance fields are validated and immutable after construction.

## Resource Lifecycle
No resources acquired; Settings class uses Pydantic's built-in validation and caching mechanism.
