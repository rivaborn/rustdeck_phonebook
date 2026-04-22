# src/phonebook/main.py

## Overall
PARTIAL - Tests cover basic app creation and lifespan but miss critical configuration and error handling scenarios.

## Untested Public Interface
- `create_app`: Missing tests for debug flag behavior based on settings, and proper router registration validation
- `lifespan`: No tests for proper async context manager behavior or database cleanup scenarios
- `app`: No tests for the global app instance configuration or lifespan assignment

## Untested Error Paths
- Settings loading failure: No test for `get_settings()` exceptions or fallback behavior
- Database initialization failure: No test for `init_db()` exceptions during startup
- Router registration errors: No test for what happens when routers fail to register
- Static file mounting errors: No test for invalid static path handling
- Jinja2Templates instantiation: No test for template directory access errors

## Fixture and Mock Quality
- `override_get_db`: The fixture function doesn't actually override anything - it's a placeholder that does nothing
- `db_session`: Uses in-memory SQLite but doesn't test actual database connection behavior or transaction handling
- `client`: Doesn't actually use the `override_get_db` fixture to patch dependencies

## Broken or Misleading Tests
- `test_create_app_registers_routers`: Uses generic route count check instead of validating specific router registration
- `test_create_app_instantiates_jinja_templates`: Only checks for attribute existence, not proper template directory instantiation
- `test_app_has_lifespan_context_manager`: Only validates existence, not functionality

## Priority Gaps
1. [HIGH] Test `create_app()` with invalid settings that would cause debug flag misconfiguration
2. [HIGH] Test `lifespan()` exception handling when `init_db()` fails during startup
3. [MEDIUM] Test `create_app()` router registration with malformed router objects
4. [MEDIUM] Test static file mounting with non-existent directory path
5. [LOW] Test `create_app()` with missing template directory to verify proper error handling
