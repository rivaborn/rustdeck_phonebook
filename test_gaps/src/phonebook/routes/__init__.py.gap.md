# src/phonebook/routes/__init__.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. [HIGH] `router`: Test that the router is properly initialized and includes all expected routes from `computers` module
2. [HIGH] `templates`: Verify that template references are correctly imported and accessible from package level
3. [MEDIUM] `__init__.py` import behavior: Ensure re-exported symbols from `.computers` are properly available when importing from this package
4. [LOW] Package initialization: Confirm that the package can be imported without errors and maintains expected namespace structure

## Mock Strategy
- `phonebook.routes.computers`: Mock the `router` and `templates` imports to verify re-export behavior and ensure no circular import issues
- `phonebook.main.app`: If route registration depends on app object, mock app to verify router registration flow
- `httpx.AsyncClient`: Mock client behavior if tests involve route testing with HTTP calls

Rules:
- Focus on import/export behavior and package-level symbol availability
- Use exact names `router`, `templates` from the source
- Keep output under 400 tokens
