# Module: src/phonebook/routes/export.py

## Role
Provides FastAPI route handlers for exporting computer records in JSON and CSV formats.

## Contract: Module-level functions

### `export_json(request) -> JSONResponse`
- **Requires:** `request` parameter must be a valid FastAPI Request object; database must be accessible via `get_db()` dependency
- **Guarantees:** Returns a JSONResponse containing serialized array of all computer records using ComputerOut schema
- **Raises:** HTTPException with status_code=500 -- when database operation or serialization fails
- **Silent failure:** None
- **Thread safety:** Unsafe - depends on global database session management

### `export_csv(request) -> StreamingResponse`
- **Requires:** `request` parameter must be a valid FastAPI Request object; database must be accessible via `get_db()` dependency
- **Guarantees:** Returns a StreamingResponse with CSV data and proper headers; includes CSV header row even when no data exists
- **Raises:** HTTPException with status_code=500 -- when database operation or CSV generation fails
- **Silent failure:** None
- **Thread safety:** Unsafe - depends on global database session management

## Module Invariants
None

## Resource Lifecycle
Database session acquired via `get_db()` generator and explicitly closed in `finally` block of both functions. StringIO buffer created and managed within function scope.
