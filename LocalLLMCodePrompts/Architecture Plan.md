# Architecture Plan


## Project Structure

```
rust_phonebook/
├── src/
│   └── phonebook/
│       ├── __init__.py                     # Package initializer
│       ├── main.py                         # FastAPI app factory + lifespan
│       ├── config.py                       # pydantic-settings Settings class
│       ├── database.py                     # engine, SessionLocal, init_db(), get_db()
│       ├── models.py                       # SQLAlchemy ORM models + declarative Base
│       ├── schemas.py                      # Pydantic request/response schemas
│       ├── crud.py                         # all database operations
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── computers.py                # CRUD + search HTML/HTMX routes
│       │   └── export.py                   # JSON + CSV export routes
│       ├── templates/
│       │   ├── base.html
│       │   ├── index.html
│       │   └── partials/
│       │       ├── computer_row.html
│       │       ├── computer_form.html
│       │       └── computer_detail.html
│       └── static/
│           ├── style.css
│           └── app.js                      # clipboard + confirm helpers only
├── tests/
│   ├── conftest.py
│   ├── test_crud.py
│   ├── test_routes_computers.py
│   └── test_routes_export.py
├── seed/
│   └── seed_data.py
├── pyproject.toml
├── .env.example
├── phonebook.service
└── README.md
```

## Data Model

The data model defines the structure of the application's persistent storage using SQLite and SQLAlchemy ORM. It includes a single table `computers` with specific constraints and validation rules.

### Table: `computers`

| Column | SQLite Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | surrogate key |
| `friendly_name` | TEXT | NOT NULL | display name |
| `rustdesk_id` | TEXT | NOT NULL, UNIQUE | RustDesk numeric/alpha ID |
| `hostname` | TEXT | nullable | |
| `local_ip` | TEXT | nullable | validated IPv4 or IPv6 when provided |
| `operating_system` | TEXT | nullable | e.g. "Ubuntu 22.04", "Windows 11" |
| `username` | TEXT | nullable | owner or primary user |
| `location` | TEXT | nullable | physical location |
| `notes` | TEXT | nullable | freeform |
| `tags` | TEXT | nullable | comma-separated; rendered as pill badges |
| `created_at` | TEXT | NOT NULL | ISO-8601 UTC, set on insert only |
| `updated_at` | TEXT | NOT NULL | ISO-8601 UTC, refreshed on every write |

### Validation Rules

- `friendly_name`: 1–120 characters, required, strip whitespace.
- `rustdesk_id`: 1–64 characters, required, unique, strip whitespace.
- `local_ip`: optional; when present, validate IPv4 (each octet 0–255) or IPv6 with Python's `ipaddress` stdlib module — do not use a hand-rolled regex alone.
- `tags`: optional; split on comma, strip each tag, re-join; each tag ≤ 40 characters; store normalized.
- All `TEXT` fields: strip leading/trailing whitespace before persistence.

### Dataclass Definitions

```pseudocode
dataclass Computer:
  id: int
  friendly_name: str
  rustdesk_id: str
  hostname: str | None
  local_ip: str | None
  operating_system: str | None
  username: str | None
  location: str | None
  notes: str | None
  tags: str | None
  created_at: str
  updated_at: str

dataclass ComputerCreate:
  friendly_name: str
  rustdesk_id: str
  hostname: str | None
  local_ip: str | None
  operating_system: str | None
  username: str | None
  location: str | None
  notes: str | None
  tags: str | None

dataclass ComputerUpdate:
  friendly_name: str | None
  rustdesk_id: str | None
  hostname: str | None
  local_ip: str | None
  operating_system: str | None
  username: str | None
  location: str | None
  notes: str | None
  tags: str | None

dataclass ComputerOut:
  id: int
  friendly_name: str
  rustdesk_id: str
  hostname: str | None
  local_ip: str | None
  operating_system: str | None
  username: str | None
  location: str | None
  notes: str | None
  tags: str | None
  created_at: str
  updated_at: str
```

### Lifecycle Notes

- `created_at` is set to the current UTC ISO-8601 timestamp upon record creation.
- `updated_at` is set to the current UTC ISO-8601 timestamp upon record creation and updated on every subsequent write operation.
- Both timestamps are stored as strings in ISO-8601 format with UTC timezone designation.

### Testing strategy

Test file: tests/test_crud.py

- External dependencies to mock: None.
- 8 bullet-pointed behaviors or edge cases to assert:
  1. `ComputerCreate` validation raises `ValidationError` when `friendly_name` is empty or exceeds 120 characters.
  2. `ComputerCreate` validation raises `ValidationError` when `rustdesk_id` is empty or exceeds 64 characters.
  3. `ComputerCreate` validation raises `ValidationError` when `local_ip` is provided but is not a valid IPv4 or IPv6 address.
  4. `ComputerCreate` validation normalizes `tags` by splitting on comma, stripping whitespace, and rejoining with commas.
  5. `ComputerCreate` validation raises `ValidationError` when any tag in `tags` exceeds 40 characters.
  6. `ComputerCreate` validation strips leading/trailing whitespace from all `TEXT` fields.
  7. `ComputerCreate` validation ensures `rustdesk_id` is unique; raises `IntegrityError` on duplicate.
  8. `ComputerOut` serialization includes all fields with correct types and values.
- pytest fixtures and plugins to use: `db_session` fixture from `conftest.py`.
- One line on coverage goals: "must exercise both the happy path AND the validation error branches for all fields".

## Module: src/phonebook/__init__.py

Standard Python package-marker file. Owns no classes, functions, or
module-level constants — its role is to make the containing directory
importable as a package and (optionally) shorten import paths by
re-exporting selected symbols from sibling modules.

**Imports:** no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

**Re-exports:** optional, determined at implementation time. May be empty.

### Testing strategy

Test file: none — a `__init__.py` with no logic has no behaviour to
assert beyond importability, which is covered implicitly by every
sibling module's test that imports from this package.


## Module: src/phonebook/main.py
Imports: get_settings from phonebook.config; init_db from phonebook.database; routers from phonebook.routes

```pseudocode
def create_app() -> FastAPI:
  1. Get settings using get_settings().
  2. Create FastAPI app with title "RustDesk Phone Book", version "0.1.0", and debug flag from settings.
  3. Register routers from phonebook.routes.computers and phonebook.routes.export.
  4. Mount static files at "/static" pointing to "src/phonebook/static/".
  5. Instantiate Jinja2Templates with directory "src/phonebook/templates/".
  6. Return app.

async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  1. Call init_db() to initialize database.
  2. Yield control to app.
  3. On app shutdown, no cleanup needed.

app = create_app()
app.router.lifespan_context = lifespan
```

### Testing strategy
Test file: tests/test_main.py
- External dependencies to mock: None.
- Behaviors or edge cases to assert:
  1. `create_app()` returns a FastAPI instance with correct title and version.
  2. `lifespan()` calls `init_db()` on startup.
  3. App registers both routers from `phonebook.routes.computers` and `phonebook.routes.export`.
  4. Static files are mounted at `/static`.
  5. Jinja2Templates are instantiated with correct directory.
  6. App has a lifespan context manager that calls `init_db()`.
- pytest fixtures and plugins to use: pytest-asyncio, tmp_path.
- Coverage goals: must exercise the happy path of app creation and lifespan startup.

## Module: src/phonebook/config.py
Imports: None

```pseudocode
class Settings(BaseSettings):
  HOST: str = "0.0.0.0"
  PORT: int = 8000
  DATABASE_URL: str = "sqlite:///./phonebook.db"
  DEBUG: bool = False

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

def get_settings() -> Settings:
  1. Use lru_cache decorator to memoize results.
  2. Create and return a new Settings instance by parsing environment variables.
  3. If environment file is missing, use default values.
```

### Testing strategy
Test file: tests/test_config.py
- External dependencies to mock: os, pathlib.Path
- Assert that `get_settings()` returns correct defaults when no `.env` exists
- Assert that `get_settings()` correctly parses `HOST`, `PORT`, `DATABASE_URL`, `DEBUG` from `.env`
- Assert that `get_settings()` raises `SettingsError` when `PORT` is not a valid integer
- Assert that `get_settings()` raises `SettingsError` when `DATABASE_URL` is malformed
- pytest fixtures and plugins to use: tmp_path, monkeypatch
- Must exercise both the happy path AND the environment variable override branch

## Module: src/phonebook/database.py

Imports: Settings from phonebook.config; Base from phonebook.models

```pseudocode
def init_db() -> None
1. Call Base.metadata.create_all(bind=engine).
2. Return None.

def get_db() -> Generator[Session, None, None]
1. Create a new SessionLocal instance.
2. Yield the session.
3. In a finally block, close the session.
4. Return None.

def create_engine(database_url: str, connect_args: dict) -> Engine
1. Call sqlalchemy.create_engine with database_url and connect_args.
2. Return the engine.

def sessionmaker(autocommit: bool, autoflush: bool, bind: Engine) -> SessionLocal
1. Call sqlalchemy.sessionmaker with autocommit, autoflush, and bind.
2. Return the sessionmaker.

def get_settings() -> Settings
1. Call phonebook.config.get_settings().
2. Return the settings object.
```

### Testing strategy

Test file: tests/test_crud.py

- External dependencies to mock: None.
- 3 behaviors or edge cases to assert:
  1. `init_db()` creates all tables in the database.
  2. `get_db()` yields a valid SQLAlchemy session and closes it properly.
  3. `get_db()` raises an exception when the database connection fails.
- pytest fixtures and plugins to use: db_session, client.
- One line on coverage goals: "must exercise both the happy path AND the database connection failure branch".

## Module: src/phonebook/models.py
Imports: Base from phonebook.models; Computer from phonebook.models

### Purpose
Defines the SQLAlchemy ORM model for the `computers` table, including all columns, constraints, and lifecycle management for `created_at` and `updated_at` timestamps.

### Public symbols
- `Base`
- `Computer`

### Dataclass definitions
```pseudocode
class Computer(Base):
  __tablename__ = "computers"
  id: int = Column(Integer, primary_key=True, index=True)
  friendly_name: str = Column(String, nullable=False)
  rustdesk_id: str = Column(String, nullable=False, unique=True)
  hostname: str = Column(String, nullable=True)
  local_ip: str = Column(String, nullable=True)
  operating_system: str = Column(String, nullable=True)
  username: str = Column(String, nullable=True)
  location: str = Column(String, nullable=True)
  notes: str = Column(String, nullable=True)
  tags: str = Column(String, nullable=True)
  created_at: str = Column(String, nullable=False, default=datetime.utcnow().isoformat())
  updated_at: str = Column(String, nullable=False, default=datetime.utcnow().isoformat(), onupdate=datetime.utcnow().isoformat())
```

### Pseudocode logic
1. Define `Computer` class inheriting from `Base`.
2. Set `__tablename__` to `"computers"`.
3. Define all columns with appropriate types, constraints, and defaults:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `friendly_name`: `TEXT NOT NULL`
   - `rustdesk_id`: `TEXT NOT NULL UNIQUE`
   - `hostname`: `TEXT NULL`
   - `local_ip`: `TEXT NULL`
   - `operating_system`: `TEXT NULL`
   - `username`: `TEXT NULL`
   - `location`: `TEXT NULL`
   - `notes`: `TEXT NULL`
   - `tags`: `TEXT NULL`
   - `created_at`: `TEXT NOT NULL DEFAULT (datetime.utcnow().isoformat())`
   - `updated_at`: `TEXT NOT NULL DEFAULT (datetime.utcnow().isoformat()) ON UPDATE (datetime.utcnow().isoformat())`
4. Ensure all `TEXT` fields are stripped of leading/trailing whitespace before persistence (handled in `schemas.py` and `crud.py`).

### Error handling approach
- No explicit error handling in model definition; errors from database operations are propagated up to the calling layer (e.g., `crud.py`).
- Validation of data integrity (e.g., unique `rustdesk_id`) is enforced by the database constraints and handled by raising `IntegrityError` in `crud.py`.

### Testing strategy
Test file: tests/test_crud.py
- External dependencies to mock: None.
- 8 bullet-pointed behaviors or edge cases to assert:
  1. `Computer` model correctly maps to the `computers` table schema.
  2. `id` column is auto-incremented and primary key.
  3. `rustdesk_id` column enforces uniqueness constraint.
  4. `created_at` and `updated_at` timestamps are set correctly on insert.
  5. `updated_at` timestamp is refreshed on every update.
  6. All `TEXT` fields are stripped of leading/trailing whitespace before persistence.
  7. `Computer` model correctly handles nullable fields.
  8. `Computer` model correctly handles default values for timestamps.
- pytest fixtures and plugins to use: `db_session` fixture from `conftest.py`.
- One line on coverage goals: "must exercise all column definitions and default values."

## Module: src/phonebook/schemas.py
Imports: Computer from phonebook.models

```pseudocode
# Pydantic schemas for computer data validation and serialization

class ComputerCreate(BaseModel):
  1. friendly_name: str
  2. rustdesk_id: str
  3. hostname: str | None = None
  4. local_ip: str | None = None
  5. operating_system: str | None = None
  6. username: str | None = None
  7. location: str | None = None
  8. notes: str | None = None
  9. tags: str | None = None
  10. Validate that friendly_name is 1-120 characters, strip whitespace
  11. Validate that rustdesk_id is 1-64 characters, strip whitespace
  12. Validate that local_ip is valid IPv4 or IPv6 when provided
  13. Validate that tags are comma-separated, each ≤ 40 characters, strip and rejoin
  14. Strip leading/trailing whitespace from all TEXT fields before persistence

class ComputerUpdate(BaseModel):
  1. friendly_name: str | None = None
  2. rustdesk_id: str | None = None
  3. hostname: str | None = None
  4. local_ip: str | None = None
  5. operating_system: str | None = None
  6. username: str | None = None
  7. location: str | None = None
  8. notes: str | None = None
  9. tags: str | None = None
  10. When a field is provided, validate it according to ComputerCreate rules
  11. Strip leading/trailing whitespace from all TEXT fields before persistence

class ComputerOut(BaseModel):
  1. id: int
  2. friendly_name: str
  3. rustdesk_id: str
  4. hostname: str | None = None
  5. local_ip: str | None = None
  6. operating_system: str | None = None
  7. username: str | None = None
  8. location: str | None = None
  9. notes: str | None = None
  10. tags: str | None = None
  11. created_at: str
  12. updated_at: str
  13. model_config = ConfigDict(from_attributes=True)
```

### Testing strategy
Test file: tests/test_crud.py

- External dependencies to mock: None
- 8 bullet-pointed behaviors or edge cases to assert:
  1. `ComputerCreate` validates that `friendly_name` must be 1-120 characters
  2. `ComputerCreate` validates that `rustdesk_id` must be 1-64 characters
  3. `ComputerCreate` rejects invalid `local_ip` format (e.g. "999.999.0.0")
  4. `ComputerCreate` normalizes `tags` by splitting, stripping, and rejoining
  5. `ComputerCreate` strips whitespace from all TEXT fields before validation
  6. `ComputerUpdate` allows partial updates with validation on provided fields
  7. `ComputerOut` serializes all fields including `id`, `created_at`, `updated_at`
  8. `ComputerOut` correctly maps database attributes to schema fields via `from_attributes=True`
- pytest fixtures and plugins to use: pytest-asyncio, pytest-httpx
- One line on coverage goals: must exercise both the happy path AND all validation error cases for `ComputerCreate` and `ComputerUpdate`

## Module: src/phonebook/crud.py
Imports: Computer from phonebook.models; ComputerCreate from phonebook.schemas; ComputerUpdate from phonebook.schemas; Session from phonebook.database

### Purpose
The CRUD module implements all database operations for the `Computer` entity. It provides functions to retrieve, create, update, and delete computer records, as well as search functionality. All operations are synchronous and operate on SQLAlchemy sessions.

### Public symbols
- `get_all_computers`
- `get_computer`
- `search_computers`
- `create_computer`
- `update_computer`
- `delete_computer`

### Functions

#### `get_all_computers(db: Session) -> list[Computer]`
1. Query all Computer objects from the database.
2. Order results by `friendly_name` in ascending order.
3. Return the list of Computer objects.

#### `get_computer(db: Session, computer_id: int) -> Computer | None`
1. Query a Computer object by its `id` field.
2. Return the Computer object if found, or None if not found.

#### `search_computers(db: Session, q: str) -> list[Computer]`
1. Validate that query string `q` is not empty.
2. Construct a SQLAlchemy query that searches across multiple fields:
   - `friendly_name` using case-insensitive LIKE with `%q%`
   - `rustdesk_id` using case-insensitive LIKE with `%q%`
   - `hostname` using case-insensitive LIKE with `%q%`
   - `local_ip` using case-insensitive LIKE with `%q%`
   - `tags` using case-insensitive LIKE with `%q%`
   - `notes` using case-insensitive LIKE with `%q%`
3. Combine all search conditions with OR logic.
4. Execute the query and return the list of matching Computer objects.

#### `create_computer(db: Session, data: ComputerCreate) -> Computer`
1. Validate that `data` conforms to ComputerCreate schema.
2. Create a new Computer object with the provided data.
3. Insert the new Computer object into the database session.
4. Commit the session to persist changes.
5. Refresh the Computer object to get the generated `id` and timestamps.
6. Return the created Computer object.

#### `update_computer(db: Session, computer_id: int, data: ComputerUpdate) -> Computer | None`
1. Retrieve the existing Computer object by `computer_id`.
2. If not found, return None.
3. Update the Computer object with values from `data`, skipping any None values.
4. Commit the session to persist changes.
5. Refresh the Computer object to get updated timestamps.
6. Return the updated Computer object.

#### `delete_computer(db: Session, computer_id: int) -> bool`
1. Retrieve the existing Computer object by `computer_id`.
2. If not found, return False.
3. Delete the Computer object from the database session.
4. Commit the session to persist changes.
5. Return True to indicate successful deletion.

### Testing strategy
Test file: tests/test_crud.py
- External dependencies to mock: None
- Behaviors to assert:
  1. `create_computer` successfully creates a record with all fields and sets `id` and timestamps
  2. `create_computer` raises `IntegrityError` when `rustdesk_id` is duplicated
  3. `get_all_computers` returns records sorted by `friendly_name` ascending
  4. `search_computers` finds records by `friendly_name`, `rustdesk_id`, `hostname`, `local_ip`, `tags`, and `notes`
  5. `update_computer` updates fields and refreshes `updated_at` timestamp
  6. `delete_computer` returns True when record is deleted and False when not found
- pytest fixtures and plugins: db_session fixture from conftest.py
- Coverage goals: must exercise all CRUD operations including error cases

## Module: src/phonebook/routes/__init__.py

Standard Python package-marker file. Owns no classes, functions, or
module-level constants — its role is to make the containing directory
importable as a package and (optionally) shorten import paths by
re-exporting selected symbols from sibling modules.

**Imports:** no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

**Re-exports:** optional, determined at implementation time. May be empty.

### Testing strategy

Test file: none — a `__init__.py` with no logic has no behaviour to
assert beyond importability, which is covered implicitly by every
sibling module's test that imports from this package.


## Module: src/phonebook/routes/computers.py
Imports: get_db from phonebook.database; get_all_computers, get_computer, search_computers, create_computer, update_computer, delete_computer from phonebook.crud; ComputerCreate, ComputerUpdate from phonebook.schemas; Computer from phonebook.models.

### Purpose
This module implements the HTML and HTMX routes for managing computer records in the RustDesk Phone Book application. It handles listing, creating, updating, and deleting computers via both full-page HTML responses and partial HTMX updates.

### Public symbols
- `list_computers`
- `new_computer_form`
- `computer_detail`
- `edit_computer_form`
- `create_computer_route`
- `update_computer_route`
- `delete_computer_route`
- `search_computers_route`

### Function signatures and pseudocode

```pseudocode
async def list_computers(request: Request) -> Response:
  1. Get database session via get_db().
  2. Fetch all computers from database using get_all_computers().
  3. Determine if request is HTMX via HX-Request header.
  4. Render index.html template with computers list.
  5. Return TemplateResponse with appropriate template and context.

async def new_computer_form(request: Request) -> Response:
  1. Determine if request is HTMX via HX-Request header.
  2. Render partials/computer_form.html template with empty ComputerCreate schema.
  3. Return TemplateResponse with appropriate template and context.

async def computer_detail(request: Request, computer_id: int) -> Response:
  1. Get database session via get_db().
  2. Fetch computer record by ID using get_computer().
  3. If not found, raise HTTPException with 404 status.
  4. Determine if request is HTMX via HX-Request header.
  5. Render partials/computer_detail.html template with computer data.
  6. Return TemplateResponse with appropriate template and context.

async def edit_computer_form(request: Request, computer_id: int) -> Response:
  1. Get database session via get_db().
  2. Fetch computer record by ID using get_computer().
  3. If not found, raise HTTPException with 404 status.
  4. Determine if request is HTMX via HX-Request header.
  5. Render partials/computer_form.html template with pre-filled ComputerUpdate schema.
  6. Return TemplateResponse with appropriate template and context.

async def create_computer_route(request: Request, form: ComputerCreate) -> Response:
  1. Get database session via get_db().
  2. Validate form data using ComputerCreate schema.
  3. If validation fails, re-render form with error messages.
  4. Create new computer record using create_computer().
  5. If successful, redirect to root path "/".
  6. If duplicate rustdesk_id, re-render form with error message.
  7. Return appropriate response based on HTMX request status.

async def update_computer_route(request: Request, computer_id: int, form: ComputerUpdate) -> Response:
  1. Get database session via get_db().
  2. Validate form data using ComputerUpdate schema.
  3. If validation fails, re-render form with error messages.
  4. Update computer record using update_computer().
  5. If not found, raise HTTPException with 404 status.
  6. If successful, return updated computer row partial or redirect.
  7. Return appropriate response based on HTMX request status.

async def delete_computer_route(request: Request, computer_id: int) -> Response:
  1. Get database session via get_db().
  2. Delete computer record using delete_computer().
  3. If not found, raise HTTPException with 404 status.
  4. Return 200 OK with empty body for HTMX requests.
  5. Return redirect to root path "/" for non-HTMX requests.

async def search_computers_route(request: Request, q: str) -> Response:
  1. Get database session via get_db().
  2. Validate search query string q (minimum 1 character).
  3. If invalid, raise HTTPException with 400 status.
  4. Search computers using search_computers().
  5. Render partials/computer_row.html for each matching computer.
  6. Return TemplateResponse with appropriate template and context.
```

### Error handling approach
- All database operations are wrapped in try/except blocks to catch SQLAlchemy exceptions.
- Validation errors are caught by Pydantic and result in re-rendering the form with error messages.
- HTTP 404 is raised when a computer record is not found during detail, edit, or delete operations.
- HTTP 400 is raised for invalid search queries (empty or missing q parameter).
- Duplicate rustdesk_id entries raise IntegrityError which is caught and results in form re-render with appropriate error message.

### Testing strategy
Test file: tests/test_routes_computers.py
- External dependencies to mock: HTTPX client, database session
- Behaviors to assert:
  1. `list_computers()` returns 200 with index.html template when no computers exist
  2. `create_computer_route()` with valid data creates record and redirects to root
  3. `create_computer_route()` with invalid data re-renders form with validation errors
  4. `update_computer_route()` updates record and returns updated partial or redirects
  5. `delete_computer_route()` removes record and returns 200 or redirects
  6. `search_computers_route()` returns matching computer rows when query matches
  7. `search_computers_route()` returns empty response when no matches found
  8. `computer_detail()` raises 404 when computer ID does not exist
- pytest fixtures and plugins: client (async), db_session (function scope)
- Coverage goals: must exercise both successful operations and error conditions for all routes

## Module: src/phonebook/routes/export.py
Imports: get_db from phonebook.database; get_all_computers from phonebook.crud; ComputerOut from phonebook.schemas

### Purpose
This module implements the export functionality for the RustDesk Phone Book web application. It provides two endpoints for exporting the computer database in JSON and CSV formats. The JSON export returns a complete array of all computer records, while the CSV export streams the data as a downloadable file with proper headers.

### Public symbols
- `export_json`
- `export_csv`

### Function signatures and pseudocode

```pseudocode
def export_json(request: Request) -> JSONResponse
1. Acquire database session via get_db dependency.
2. Fetch all computers using get_all_computers(db).
3. Serialize computers to JSON using ComputerOut model.
4. Return JSONResponse with serialized data.
5. Handle any database or serialization errors by returning 500 status.

def export_csv(request: Request) -> StreamingResponse
1. Acquire database session via get_db dependency.
2. Fetch all computers using get_all_computers(db).
3. Create CSV writer with headers matching ComputerOut fields.
4. Stream CSV rows using csv.DictWriter.
5. Set Content-Disposition header to attachment with filename "phonebook.csv".
6. Return StreamingResponse with CSV data and text/csv content type.
7. Handle any database or CSV generation errors by returning 500 status.
```

### Error handling approach
Both functions implement centralized error handling:
- Database connection failures are caught and result in 500 Internal Server Error responses
- Serialization errors (for JSON) are caught and result in 500 Internal Server Error responses
- CSV generation errors are caught and result in 500 Internal Server Error responses
- All errors are logged appropriately for debugging purposes

### Testing strategy
Test file: tests/test_routes_export.py

External dependencies to mock:
- Database session (via get_db dependency)
- get_all_computers function

Behaviors and edge cases to assert:
- GET /export/json with no records returns 200 with empty array []
- GET /export/json with data returns 200 with valid JSON array of ComputerOut objects
- GET /export/csv with no records returns 200 with CSV header row only
- GET /export/csv with data returns 200 with CSV containing header row and data rows
- GET /export/json returns valid JSON that matches ComputerOut schema
- GET /export/csv returns valid CSV with proper headers and data
- GET /export/csv with database error returns 500 status
- GET /export/json with database error returns 500 status

pytest fixtures and plugins to use:
- client fixture from conftest.py (async)
- db_session fixture from conftest.py (function scope)

Coverage goals:
- Must exercise both empty database and populated database scenarios for both export formats
- Must test error handling paths for database failures
- Must verify correct HTTP status codes and content types for all scenarios

## File: src/phonebook/templates/base.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RustDesk Phone Book</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <h1>RustDesk Phone Book</h1>
        <button hx-get="/computers/new" hx-target="#modal" hx-swap="innerHTML">Add Computer</button>
        <input type="text" id="search-input" placeholder="Search computers..." hx-get="/computers/search" hx-target="#computer-table-body" hx-trigger="input changed delay:300ms" hx-include="#search-input">
        <a href="/export/json">Export JSON</a>
        <a href="/export/csv">Export CSV</a>
    </nav>
    <main id="content">
        {% block content %}{% endblock %}
    </main>
    <div id="modal"></div>
</body>
</html>
```

## File: src/phonebook/templates/index.html

List of template files for the phonebook application.

- `src/phonebook/templates/base.html` — Base template with navigation and layout structure.
- `src/phonebook/templates/index.html` — Main page listing all computers in a table.
- `src/phonebook/templates/partials/computer_row.html` — Partial HTML for a single computer row.
- `src/phonebook/templates/partials/computer_form.html` — Partial HTML for adding or editing a computer.
- `src/phonebook/templates/partials/computer_detail.html` — Partial HTML for displaying computer details.

## File: src/phonebook/templates/partials/computer_row.html

This file defines a Jinja2 template fragment for rendering a single computer record as an HTML table row. It is used by the search endpoint to dynamically update the computer list table body via HTMX swaps.

The template expects a `computer` variable containing a `Computer` model instance with all fields from the data model table. It renders the row with appropriate data attributes for HTMX interactions and includes a delete button with confirmation.

No Python code or functions are defined in this file — it is purely a template fragment for use with Jinja2.

## File: src/phonebook/templates/partials/computer_form.html

This file is a Jinja2 template that renders an HTML form for adding or editing computer records. It includes all writable fields from the `Computer` model, with appropriate labels, input fields, and validation error display. The form uses HTMX attributes for submission handling and integrates with the application's frontend behavior.

The template is used by:
- `new_computer_form` route handler (GET `/computers/new`) — renders a blank form
- `edit_computer_form` route handler (GET `/computers/{computer_id}/edit`) — renders a pre-filled form

The form supports both creation and update operations:
- Creation: `hx-post="/computers"` with `method="post"`
- Update: `hx-put="/computers/{id}"` with `method="put"`

The form includes:
- Input fields for `friendly_name`, `rustdesk_id`, `hostname`, `local_ip`, `operating_system`, `username`, `location`, `notes`, and `tags`
- Validation error messages for each field
- A "Save Computer" submit button
- A cancel button that clears the modal

No cross-module dependencies or imports are needed for this template file.

## File: src/phonebook/templates/partials/computer_detail.html

This file defines the HTML partial for displaying detailed information about a single computer record. It is rendered as an HTMX swap target when users click on a computer's name or when editing a computer's details.

Imports: None

### Testing strategy
Test file: tests/test_routes_computers.py

- The partial renders all computer fields correctly including rustdesk_id, hostname, local_ip, operating_system, username, location, notes, and tags.
- Copy-to-clipboard buttons are present for rustdesk_id and local_ip fields when they have values.
- Tags are rendered as `<span class="tag">` badges with proper spacing.
- Dates are formatted in a human-readable way (e.g., "2025-04-21 14:30 UTC").
- Edit button links to the correct edit form route.
- When local_ip is null/empty, the copy button for it is not rendered.
- When rustdesk_id is null/empty, the copy button for it is not rendered.
- The partial includes proper HTMX attributes for the edit button to trigger the correct HTMX swap behavior.

```html
<div class="modal-content">
  <h2>Computer Details</h2>
  <dl class="detail-list">
    <div>
      <dt>Friendly Name</dt>
      <dd>{{ computer.friendly_name }}</dd>
    </div>
    <div>
      <dt>RustDesk ID</dt>
      <dd>
        {{ computer.rustdesk_id }}
        {% if computer.rustdesk_id %}
          <button onclick="copyToClipboard('{{ computer.rustdesk_id }}')" class="copy-btn">Copy</button>
        {% endif %}
      </dd>
    </div>
    <div>
      <dt>Hostname</dt>
      <dd>{{ computer.hostname or 'N/A' }}</dd>
    </div>
    <div>
      <dt>Local IP</dt>
      <dd>
        {{ computer.local_ip or 'N/A' }}
        {% if computer.local_ip %}
          <button onclick="copyToClipboard('{{ computer.local_ip }}')" class="copy-btn">Copy</button>
        {% endif %}
      </dd>
    </div>
    <div>
      <dt>Operating System</dt>
      <dd>{{ computer.operating_system or 'N/A' }}</dd>
    </div>
    <div>
      <dt>Username</dt>
      <dd>{{ computer.username or 'N/A' }}</dd>
    </div>
    <div>
      <dt>Location</dt>
      <dd>{{ computer.location or 'N/A' }}</dd>
    </div>
    <div>
      <dt>Notes</dt>
      <dd>{{ computer.notes or 'N/A' }}</dd>
    </div>
    <div>
      <dt>Tags</dt>
      <dd>
        {% if computer.tags %}
          {% for tag in computer.tags.split(',') %}
            <span class="tag">{{ tag.strip() }}</span>
          {% endfor %}
        {% else %}
          N/A
        {% endif %}
      </dd>
    </div>
    <div>
      <dt>Created At</dt>
      <dd>{{ computer.created_at }}</dd>
    </div>
    <div>
      <dt>Updated At</dt>
      <dd>{{ computer.updated_at }}</dd>
    </div>
  </dl>
  <button hx-get="/computers/{{ computer.id }}/edit" hx-target="#modal" class="btn btn-primary">Edit</button>
</div>
```

## File: src/phonebook/static/style.css

This file contains the CSS stylesheet for the RustDesk Phone Book web application. It defines responsive styling, dark mode support, and UI components for the application's interface.

Imports: None

### Testing strategy
Test file: tests/test_static_css.py
- External dependencies to mock: None
- Behaviors or edge cases to assert:
  - CSS custom properties are defined at :root and overridden in @media (prefers-color-scheme: dark)
  - Responsive table layout uses data-label attributes and ::before pseudo-elements for mobile view
  - .tag class renders pill badges with proper styling
  - .field-error class displays red text for validation errors
  - Modal overlay has fixed positioning when containing content
  - No external CSS framework is used
- pytest fixtures and plugins to use: pytest-asyncio, tmp_path
- Coverage goals: must exercise both light and dark mode CSS rules

## File: src/phonebook/static/app.js

This file contains only two JavaScript functions as specified in the requirements:

1. `copyToClipboard(text)` — copies the provided text to the clipboard and shows a brief "Copied!" tooltip.
2. `confirmDelete(event, form)` — this function is not needed because HTMX handles `hx-confirm` natively; it may be omitted.

No other JavaScript code is present in this file.

### Testing strategy
Test file: tests/test_app_js.py
- External dependencies to mock: navigator.clipboard
- Behavior assertions:
  - `copyToClipboard()` calls `navigator.clipboard.writeText()` with correct text
  - `copyToClipboard()` shows a tooltip briefly after copying
  - `confirmDelete()` is not defined in the file (as per spec)
- pytest fixtures and plugins: monkeypatch, pytest-asyncio
- Coverage goal: must verify that the file contains exactly the two specified functions and nothing else

## File: pyproject.toml

```toml
[build-system]
requires = ["setuptools>=64", "wheel>=0.38"]
build-backend = "setuptools.build_meta"

[project]
name = "phonebook"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111,<1.0",
    "uvicorn>=0.29,<1.0",
    "sqlalchemy>=2.0,<3.0",
    "pydantic-settings>=2.0,<3.0",
    "jinja2>=3.1,<4.0",
    "httpx>=0.27,<1.0",
    "pytest>=8.0,<9.0",
    "pytest-asyncio>=0.21,<1.0",
    "ruff>=0.4,<1.0",
]

[project.scripts]
phonebook = "phonebook.main:run"

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## File: .env.example

```
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./phonebook.db
DEBUG=false
```

## File: phonebook.service

```
[Unit]
Description=RustDesk Phone Book web application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rust_phonebook
EnvironmentFile=/home/ubuntu/rust_phonebook/.env
ExecStart=/home/ubuntu/rust_phonebook/venv/bin/python -m phonebook.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## File: README.md

What the app does
================

A lightweight internal web application that runs on an Ubuntu server and is reachable on a local network through a browser. Its purpose is to maintain a list of RustDesk-managed computers/endpoints. Users can add, edit, delete, search, view details of, and export computer records. The app is a standalone companion tool and must not modify RustDesk source code.

Prerequisites
=============

- Python 3.11 or higher
- Git
- Ubuntu 22.04 or higher

Installation
============

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rust_phonebook
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

Running in development
======================

To run the application in development mode with auto-reload enabled:
```bash
uvicorn phonebook.main:app --reload --host 0.0.0.0 --port 8000
```

Running in production
=====================

To run the application in production using systemd:

1. Copy the systemd unit file:
   ```bash
   sudo cp phonebook.service /etc/systemd/system/phonebook.service
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl enable --now phonebook
   ```

Accessing from another LAN machine
==================================

Once the service is running, access the application from another machine on the same local network using:
```
http://<server-ip>:8000
```

Configuring host/port via .env
==============================

The application can be configured using environment variables defined in `.env`. The default values are:
```
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./phonebook.db
DEBUG=false
```

Seeding sample data
===================

To populate the database with sample data:
```bash
python seed/seed_data.py
```

Backing up the database
=======================

To backup the database file:
```bash
cp phonebook.db phonebook.db.bak
```

Running behind nginx
====================

To run the application behind nginx, configure a reverse proxy with the following minimal snippet:
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
}
```

Quick Start
===========

1. Clone the repository and navigate to the directory.
2. Create and activate a virtual environment.
3. Install the package in development mode.
4. Run the application using `uvicorn` or enable the systemd service for production use.

## Module: tests/conftest.py
Imports: get_db, init_db, SessionLocal from phonebook.database; app from phonebook.main

```pseudocode
def db_session() -> Generator[Session, None, None]:
  1. Create in-memory SQLite engine with URL "sqlite:///:memory:".
  2. Call init_db() with the engine to create tables.
  3. Create a new session using SessionLocal() bound to the engine.
  4. Yield the session to the test function.
  5. After test completion, close the session and drop all tables.

def client() -> Generator[AsyncClient, None, None]:
  1. Create AsyncClient with base_url "http://testserver".
  2. Override get_db dependency to use db_session fixture.
  3. Mount the app's routes onto the client.
  4. Yield the client to the test function.
  5. After test completion, close the client.
```

### Testing strategy
Test file: tests/conftest.py

- No external dependencies to mock.
- Assert that `db_session` creates a clean in-memory database for each test.
- Assert that `client` uses the test database and overrides `get_db` correctly.
- Assert that `db_session` properly closes sessions and drops tables after each test.
- Assert that `client` can make requests to the app's endpoints.
- pytest fixtures: `db_session`, `client`.
- Coverage goal: must test both the setup and teardown of the database session fixture.

## Module: tests/test_crud.py
Imports: get_db, init_db, SessionLocal, Computer, ComputerCreate, ComputerUpdate, get_all_computers, get_computer, search_computers, create_computer, update_computer, delete_computer from phonebook.crud; ComputerOut from phonebook.schemas

### Testing strategy
Test file: tests/test_crud.py
- External dependencies to mock: None
- Behaviors or edge cases to assert:
  - `test_create_computer_success` — All fields round-trip; `id` is set; `created_at` is a valid ISO-8601 string
  - `test_create_computer_duplicate_rustdesk_id` — Raises `IntegrityError`
  - `test_get_all_computers_sorted` — Three records returned in `friendly_name` ASC order
  - `test_search_computers_by_name` — Returns correct record
  - `test_search_computers_by_rustdesk_id` — Returns correct record
  - `test_search_computers_by_ip` — Returns correct record
  - `test_search_computers_by_tag` — Returns correct record
  - `test_search_computers_by_notes` — Returns correct record
  - `test_update_computer` — `friendly_name` updated; `updated_at` differs from `created_at`
  - `test_delete_computer` — Returns `True`; subsequent `get_computer` returns `None`
  - `test_delete_nonexistent_computer` — Returns `False`
- pytest fixtures and plugins to use: `db_session` (from conftest.py)
- Coverage goals: must exercise both the happy path AND the error cases (e.g., duplicate RustDesk ID)

## Module: tests/test_routes_computers.py

Imports: client, db_session from conftest; get_db from phonebook.database; get_all_computers, create_computer, update_computer, delete_computer from phonebook.crud; ComputerCreate, ComputerUpdate from phonebook.schemas; ComputerOut from phonebook.schemas.

### Testing strategy
Test file: tests/test_routes_computers.py
- External dependencies to mock: None (uses in-memory SQLite via db_session fixture)
- Behaviors/assertions to test:
  - GET `/` returns 200 with empty list
  - POST `/computers` with valid data creates record and redirects
  - POST `/computers` without `friendly_name` returns 422 or re-renders form
  - POST `/computers` with invalid `local_ip` returns 422 or form error
  - POST `/computers` with duplicate `rustdesk_id` raises error
  - PUT `/computers/{id}` updates record correctly
  - DELETE `/computers/{id}` removes record and returns 200
  - GET `/computers/search?q=<name>` returns 200 with matching rows
  - GET `/computers/search?q=zzznomatch` returns 200 with empty body
- pytest fixtures/plugins: client (async), db_session (function-scoped)
- Coverage goal: must test both success and error paths for all routes

1. Test that GET `/` returns 200 with empty list when no computers exist.
2. Test that POST `/computers` with valid data creates a new computer and redirects to `/`.
3. Test that POST `/computers` without `friendly_name` returns 422 or re-renders form with error.
4. Test that POST `/computers` with invalid `local_ip` returns 422 or form error.
5. Test that POST `/computers` with duplicate `rustdesk_id` raises an error.
6. Test that PUT `/computers/{id}` updates an existing computer correctly.
7. Test that DELETE `/computers/{id}` removes a computer and returns 200.
8. Test that GET `/computers/search?q=<name>` returns 200 with matching rows.
9. Test that GET `/computers/search?q=zzznomatch` returns 200 with empty body.

## Module: tests/test_routes_export.py

Imports: export_json, export_csv from phonebook.routes.export; ComputerOut from phonebook.schemas; get_db from phonebook.database; get_all_computers from phonebook.crud; AsyncClient from httpx; Session from sqlalchemy.orm; app from phonebook.main; db_session from conftest

### Testing strategy
Test file: tests/test_routes_export.py

External dependencies to mock:
- No external dependencies required for export routes.

3-8 bullet-pointed behaviors or edge cases to assert:
- `test_export_json_empty` — GET `/export/json` with no records returns 200 and empty JSON array.
- `test_export_json_with_data` — GET `/export/json` with records returns 200 and valid JSON array with all ComputerOut fields.
- `test_export_csv_headers` — GET `/export/csv` returns 200 with `text/csv` content type and first line matches expected CSV headers.
- `test_export_csv_with_data` — GET `/export/csv` returns 200 with second line matching seeded record fields.
- `test_export_json_invalid_db_state` — GET `/export/json` when DB connection fails raises appropriate error.
- `test_export_csv_invalid_db_state` — GET `/export/csv` when DB connection fails raises appropriate error.
- `test_export_json_with_special_characters` — GET `/export/json` with records containing special characters returns valid JSON.
- `test_export_csv_with_special_characters` — GET `/export/csv` with records containing special characters returns valid CSV.

pytest fixtures and plugins to use:
- `client` fixture from conftest (async)
- `db_session` fixture from conftest (function-scoped)
- `pytest-asyncio` plugin

One line on coverage goals:
- Must exercise both empty and populated database states for both JSON and CSV export routes.

## Module: seed/seed_data.py
Imports: SessionLocal, create_computer, ComputerCreate from phonebook.database, phonebook.crud, phonebook.schemas

```pseudocode
def seed_sample_data() -> None
1. Initialize database session using SessionLocal().
2. Define 5 sample ComputerCreate objects with diverse OS, tags, and locations.
3. For each sample computer:
   a. Attempt to create the computer using create_computer(db, computer_data).
   b. If IntegrityError is raised (due to duplicate rustdesk_id), silently skip this record.
4. Close the database session in a finally block.
```

### Testing strategy
Test file: tests/test_seed_data.py
- External dependencies to mock: database engine, SessionLocal, create_computer function.
- Behaviors or edge cases to assert:
  - 5 sample records are inserted when database is empty.
  - Duplicate rustdesk_id records are skipped without raising an exception.
  - Function handles database connection errors gracefully.
  - All sample records have valid field values according to schemas.
  - Function is idempotent — running twice does not cause duplicate entries.
- pytest fixtures and plugins to use: tmp_path, monkeypatch, pytest-asyncio.
- Coverage goals: must exercise both the happy path AND the duplicate entry branch.

## Data Pipeline

The data pipeline defines the flow of data from input sources through processing and storage to output destinations. In the context of the RustDesk Phone Book application, this pipeline encompasses how computer records are ingested via HTTP requests, validated, stored in the SQLite database, and then retrieved for display or export.

The pipeline is structured around three main phases:
1. **Input Processing**: Handling incoming HTTP requests with data validation.
2. **Storage Layer**: Persisting validated data into the SQLite database using SQLAlchemy ORM.
3. **Output Generation**: Serving data back to users via HTML templates or structured formats like JSON/CSV.

Each phase is designed to be robust, maintainable, and secure, with clear separation of concerns between data ingestion, business logic, and data presentation.

### Input Processing

Input processing begins when an HTTP request arrives at one of the defined routes. The system uses FastAPI's built-in validation to ensure that incoming data conforms to the expected schema. For example, when creating a new computer record, the `ComputerCreate` schema validates that required fields are present and that data types match expectations.

```pseudocode
def validate_input(data: dict) -> ComputerCreate:
    1. Parse incoming JSON data into a dictionary.
    2. Validate the dictionary against ComputerCreate schema.
    3. Raise HTTPException with status code 422 if validation fails.
    4. Return validated ComputerCreate object.
```

### Storage Layer

Once validated, data is persisted using SQLAlchemy ORM operations. The `crud.py` module handles all database interactions, ensuring that data integrity is maintained through proper transaction handling and constraint enforcement.

```pseudocode
def create_computer(db: Session, data: ComputerCreate) -> Computer:
    1. Create a new Computer object from validated data.
    2. Add the object to the database session.
    3. Commit the transaction to persist changes.
    4. Return the created Computer object with assigned ID.
```

### Output Generation

Data is served back to users in various formats depending on the request type. For HTML responses, Jinja2 templates are used to render dynamic content. For structured data exports, the system serializes data into JSON or CSV formats.

```pseudocode
def export_json(db: Session) -> JSONResponse:
    1. Retrieve all computers from the database.
    2. Serialize each computer using ComputerOut schema.
    3. Wrap serialized data in a JSON array.
    4. Return JSONResponse with serialized data.
```

### Testing strategy

Test file: tests/test_crud.py

- External dependencies to mock: None required for basic CRUD operations.
- 3 bullet-pointed behaviors or edge cases to assert:
  - `create_computer` raises `IntegrityError` when duplicate `rustdesk_id` is provided.
  - `get_all_computers` returns records sorted by `friendly_name` in ascending order.
  - `search_computers` performs case-insensitive search across multiple fields using `LIKE %q%`.
- pytest fixtures and plugins to use: `db_session` fixture from `conftest.py`.
- One line on coverage goals: "must exercise both the happy path AND the duplicate key constraint branch".

## UI/TUI Layout

This section defines the user interface components and their interactions for the RustDesk Phone Book web application. It includes the structure of HTML templates, the layout of UI elements, and how HTMX handles partial updates.

### Template Map

| Template File | Route(s) Rendering It | HTMX Target |
|---------------|-----------------------|-------------|
| `base.html` | All routes | Root layout |
| `index.html` | GET `/` | Full page |
| `partials/computer_row.html` | GET `/computers/search` | `#computer-table-body` |
| `partials/computer_form.html` | GET `/computers/new`, GET `/computers/{id}/edit` | `#modal` |
| `partials/computer_detail.html` | GET `/computers/{id}` | `#modal` |

### UI Components and Interactions

#### `base.html`

```pseudocode
1. Render HTML head with charset, viewport, HTMX CDN script, and CSS link.
2. Render navigation bar with:
   - App title "RustDesk Phone Book"
   - "Add Computer" button using HTMX `hx-get="/computers/new"` swapping into `#modal`
   - Search input using HTMX `hx-get="/computers/search"` with `hx-trigger="input changed delay:300ms"` targeting `#computer-table-body`
   - Export links to `/export/json` and `/export/csv`
3. Render main content area with Jinja2 `{% block content %}` placeholder.
4. Render empty modal div with id `#modal` for HTMX swaps.
```

#### `index.html`

```pseudocode
1. Extend `base.html` layout.
2. Render a table with columns: Friendly Name, RustDesk ID, OS, Location, Tags, Updated.
3. Populate `<tbody id="computer-table-body">` with `computer_row.html` partials.
4. Each row includes:
   - Delete button using `hx-delete`, `hx-confirm`, `hx-target="closest tr"`, `hx-swap="outerHTML"`
   - Edit button using `hx-get="/computers/{id}/edit"` swapping into `#modal`
   - Clicking Friendly Name cell triggers `hx-get="/computers/{id}"` swapping into `#modal`
```

#### `partials/computer_row.html`

```pseudocode
1. Render a single `<tr>` fragment.
2. Include cells for:
   - Friendly Name
   - RustDesk ID
   - Operating System
   - Location
   - Tags (as pill badges)
   - Updated timestamp
3. Each cell should be labeled with `data-label` attribute for responsive design.
```

#### `partials/computer_form.html`

```pseudocode
1. Render a form for adding or editing a computer.
2. Include fields:
   - Friendly Name (input)
   - RustDesk ID (input)
   - Hostname (input)
   - Local IP (input)
   - Operating System (input)
   - Username (input)
   - Location (input)
   - Notes (textarea)
   - Tags (input)
3. Each field has:
   - Label
   - Input element
   - Optional error span with class `field-error`
4. Use HTMX `hx-post="/computers"` for add or `hx-put="/computers/{id}"` for edit.
5. Submit button labeled "Save Computer".
6. Cancel button clears `#modal`.
```

#### `partials/computer_detail.html`

```pseudocode
1. Render a read-only view of all computer fields.
2. Include:
   - Friendly Name
   - RustDesk ID
   - Hostname
   - Local IP
   - Operating System
   - Username
   - Location
   - Notes
   - Tags (as pill badges)
   - Created and Updated timestamps in human-readable format
3. Copy-to-clipboard buttons beside `rustdesk_id` and `local_ip` (when present).
4. Edit button linking to edit form.
```

### Testing strategy

Test file: tests/test_routes_computers.py

- External dependencies to mock: None.
- 3 behaviors or edge cases to assert:
  1. `list_computers` returns a full `index.html` page with correct structure.
  2. `new_computer_form` returns `partials/computer_form.html` with correct form fields.
  3. `computer_detail` returns `partials/computer_detail.html` with all fields rendered.
- pytest fixtures and plugins to use: `client` fixture from `conftest.py`.
- One line on coverage goals: "must exercise both full-page and partial HTMX responses."

## Module: src/phonebook/config.py
Imports: None

```pseudocode
class Settings(BaseSettings):
  HOST: str = "0.0.0.0"
  PORT: int = 8000
  DATABASE_URL: str = "sqlite:///./phonebook.db"
  DEBUG: bool = False

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
  1. Load settings from .env file using pydantic-settings.
  2. Apply default values where not specified.
  3. Validate all fields according to their types and constraints.
  4. Return the validated Settings instance.
```

### Testing strategy
Test file: tests/test_config.py
- External dependencies to mock: `pathlib.Path` (for .env file access), `lru_cache` (to verify caching behavior).
- `get_settings()` returns a Settings instance with correct defaults when .env is missing.
- `get_settings()` correctly loads values from a populated .env file.
- `get_settings()` raises `SettingsError` when .env contains invalid values (e.g. non-integer PORT).
- `get_settings()` caches results so multiple calls return the same instance.
- Must exercise both the happy path AND the .env-missing branch.
pytest fixtures and plugins to use: `monkeypatch`, `pytest-asyncio`
- Coverage goal: 100% line coverage for `get_settings()` and Settings class initialization.

## Testing Strategy

This section outlines the testing approach and coverage strategy for the RustDesk Phone Book web application. The testing strategy follows a layered approach with unit tests for core logic, integration tests for database operations, and end-to-end tests for HTTP routes and UI interactions.

### Test file: tests/test_crud.py

**External dependencies to mock:**
- No external dependencies required for CRUD tests as they operate directly on the in-memory SQLite database.

**Behaviors and edge cases to assert:**
1. `create_computer` successfully persists all fields including `id`, `created_at`, and `updated_at` timestamps.
2. `create_computer` raises `IntegrityError` when attempting to insert a duplicate `rustdesk_id`.
3. `get_all_computers` returns records sorted by `friendly_name` in ascending order.
4. `search_computers` correctly matches records across `friendly_name`, `rustdesk_id`, `hostname`, `local_ip`, `tags`, and `notes` fields using case-insensitive pattern matching.
5. `update_computer` updates the `friendly_name` and refreshes the `updated_at` timestamp while preserving other fields.
6. `delete_computer` returns `True` when a record is deleted and `False` when attempting to delete a non-existent record.
7. `get_computer` returns `None` when querying for a non-existent computer ID.

**pytest fixtures and plugins:**
- `db_session` fixture from `conftest.py` provides an isolated in-memory database session for each test.
- `pytest-asyncio` plugin for async test execution (though not used directly in this file).

**Coverage goals:**
- Must exercise all CRUD operations including error conditions.
- Must cover both successful and failure paths for each function.
- Must validate data integrity constraints such as uniqueness of `rustdesk_id`.

### Test file: tests/test_routes_computers.py

**External dependencies to mock:**
- No external dependencies required for route tests as they use the `client` fixture which mocks the database dependency.

**Behaviors and edge cases to assert:**
1. `list_computers` returns a 200 status code and renders the index page with empty content when no records exist.
2. `create_computer_route` successfully creates a new computer record via POST and redirects to the main page on success.
3. `create_computer_route` returns a 422 status code or re-renders the form with validation errors when required fields are missing.
4. `create_computer_route` returns a 422 status code or re-renders the form with validation errors when `local_ip` is invalid.
5. `create_computer_route` returns an error response when attempting to create a computer with a duplicate `rustdesk_id`.
6. `update_computer_route` successfully updates an existing computer record and reflects changes in the database.
7. `delete_computer_route` returns a 200 status code and removes the computer record from the database.
8. `search_computers_route` returns a 200 status code and renders matching computer rows when a search query matches records.
9. `search_computers_route` returns a 200 status code with an empty body when a search query does not match any records.

**pytest fixtures and plugins:**
- `client` fixture from `conftest.py` provides an async HTTP client for making requests to the FastAPI app.
- `pytest-asyncio` plugin for async test execution.

**Coverage goals:**
- Must cover all HTTP methods (GET, POST, PUT, DELETE) for the computers routes.
- Must validate both successful and error responses for each route.
- Must ensure proper HTMX behavior in partial updates and full page renders.

### Test file: tests/test_routes_export.py

**External dependencies to mock:**
- No external dependencies required for export route tests as they use the `client` fixture which mocks the database dependency.

**Behaviors and edge cases to assert:**
1. `export_json` returns a 200 status code and an empty JSON array when no records exist.
2. `export_json` returns a 200 status code and a JSON array with all fields from `ComputerOut` when records exist.
3. `export_csv` returns a 200 status code with `text/csv` content type and proper headers.
4. `export_csv` returns a CSV file with the correct header row when records exist.
5. `export_csv` returns a CSV file where the second line matches the seeded record fields.

**pytest fixtures and plugins:**
- `client` fixture from `conftest.py` provides an async HTTP client for making requests to the FastAPI app.
- `pytest-asyncio` plugin for async test execution.

**Coverage goals:**
- Must validate both empty and populated export scenarios for both JSON and CSV formats.
- Must ensure correct MIME types and headers are set for each export route.
- Must verify that exported data matches the expected schema and content.

## Dependencies

### Project Dependencies

The project requires the following dependencies, specified with their minimum versions:

- `fastapi >= 0.111`
- `jinja2 >= 3.1`
- `sqlalchemy >= 2.0`
- `pydantic-settings >= 2.0`
- `uvicorn >= 0.29`
- `pytest >= 8`
- `httpx >= 0.27`
- `ruff >= 0.4`

These dependencies are declared in the `pyproject.toml` file under the `[project.dependencies]` section.

### Development Dependencies

The following development dependencies are required for building, testing, and linting:

- `setuptools`
- `wheel`
- `pytest-asyncio`
- `pytest-httpx`
- `ruff`

These are declared in the `[build-system]` section of `pyproject.toml`.

### Testing Strategy

Test file: tests/test_crud.py

- External dependencies to mock:
  - `sqlalchemy.engine.Engine` (via `unittest.mock.patch`)
  - `sqlalchemy.orm.Session` (via `unittest.mock.patch`)
  - `sqlalchemy.exc.IntegrityError` (via `unittest.mock.patch`)

- Behaviors or edge cases to assert:
  1. `create_computer` raises `IntegrityError` when `rustdesk_id` is duplicated.
  2. `get_all_computers` returns records sorted by `friendly_name` in ascending order.
  3. `search_computers` returns records matching search term across multiple fields.
  4. `update_computer` updates `updated_at` timestamp correctly.
  5. `delete_computer` returns `True` when a record is deleted, `False` when not found.
  6. `get_computer` returns `None` when no record matches the given ID.
  7. `create_computer` correctly strips whitespace from all string fields before saving.
  8. `search_computers` performs case-insensitive matching on all searchable fields.

- Pytest fixtures and plugins to use:
  - `db_session` fixture from `conftest.py`
  - `pytest-asyncio` plugin for async test support
  - `pytest-httpx` plugin for HTTP mocking

- Coverage goals:
  - Must exercise both the happy path AND all error conditions (e.g., duplicate key, invalid IP address).
  - Must cover all CRUD operations with full data validation.
  - Must ensure that `created_at` and `updated_at` timestamps are correctly set and updated.

## Build/Run Instructions

This section defines how to build and run the RustDesk Phone Book application.

### Build process

1.  Initialize a Python virtual environment using `python3 -m venv venv`.
2.  Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows).
3.  Install the project in development mode with editable install: `pip install -e .`.
4.  The build process is complete once the package is installed and dependencies are resolved.

### Run process

#### Development mode

1.  Ensure the virtual environment is activated.
2.  Run the application using Uvicorn with auto-reload enabled:
    ```bash
    uvicorn phonebook.main:app --reload --host 0.0.0.0 --port 8000
    ```
3.  The application will be accessible at `http://<server-ip>:8000`.

#### Production mode

1.  Ensure the virtual environment is activated.
2.  Copy the provided systemd unit file `phonebook.service` to `/etc/systemd/system/`.
3.  Reload systemd to recognize the new unit: `sudo systemctl daemon-reload`.
4.  Enable and start the service:
    ```bash
    sudo systemctl enable --now phonebook
    ```
5.  The application will be accessible at `http://<server-ip>:8000`.

### Configuration

The application reads configuration from a `.env` file located in the repository root. The `.env.example` file provides a template with default values. The following environment variables are supported:

- `HOST`: The host address to bind the server to (default: `"0.0.0.0"`).
- `PORT`: The port number to bind the server to (default: `8000`).
- `DATABASE_URL`: The URL for the SQLite database (default: `"sqlite:///./phonebook.db"`).
- `DEBUG`: Enable or disable debug mode (default: `False`).

### Seeding data

To populate the database with sample data, run the seed script:

```bash
python seed/seed_data.py
```

This script inserts five sample computer records into the database. It is idempotent and will skip records if a `rustdesk_id` already exists.

### Database backup

To back up the database, simply copy the `phonebook.db` file:

```bash
cp phonebook.db phonebook.db.bak
```

### Reverse proxy with nginx

To run the application behind an nginx reverse proxy, use the following minimal configuration snippet in your nginx server block:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Quick start

1.  Clone the repository.
2.  Create and activate a Python virtual environment.
3.  Install the project in development mode: `pip install -e .`.
4.  Run the application in development mode: `uvicorn phonebook.main:app --reload --host 0.0.0.0 --port 8000`.
5.  Access the application at `http://<server-ip>:8000`.

### Testing strategy

Test file: tests/test_main.py

- External dependencies to mock: `uvicorn.run`, `get_settings`, `init_db`.
- Behaviors or edge cases to assert:
  - `run()` calls `uvicorn.run()` with correct host and port from settings.
  - `run()` calls `init_db()` before starting the server.
  - `run()` raises an exception if `get_settings()` fails.
  - `run()` raises an exception if `init_db()` fails.
- pytest fixtures and plugins to use: `monkeypatch`, `pytest-asyncio`.
- Coverage goals: must exercise both the happy path AND the error handling branches.

## API Endpoint Table

| Method | Path | Handler | Returns |
|---|---|---|---|
| GET | `/` | `list_computers` | `index.html` full page |
| GET | `/computers/new` | `new_computer_form` | `partials/computer_form.html` |
| GET | `/computers/{computer_id}` | `computer_detail` | `partials/computer_detail.html` |
| GET | `/computers/{computer_id}/edit` | `edit_computer_form` | `partials/computer_form.html` pre-filled |
| POST | `/computers` | `create_computer_route` | Redirect to `/` on success; re-render form with field errors on 422 |
| PUT | `/computers/{computer_id}` | `update_computer_route` | HTMX swap updated row or redirect |
| DELETE | `/computers/{computer_id}` | `delete_computer_route` | 200 with empty body; HTMX removes row |
| GET | `/computers/search` | `search_computers_route` | list of `partials/computer_row.html` |
| GET | `/export/json` | `export_json` | `application/json` array |
| GET | `/export/csv` | `export_csv` | `text/csv` attachment |

Query parameter for search: `q` (string, required, minimum 1 character).

## Template Map

This section describes all Jinja2 templates used in the application, their purpose, and how they are rendered by routes or swapped via HTMX.

### Template Files and Usage

1. **`base.html`**
   - **Purpose**: The base layout template that all other templates extend.
   - **Rendered by**: All HTML routes.
   - **HTMX Swapping**: None (base template).

2. **`index.html`**
   - **Purpose**: Main page listing all computers in a table format.
   - **Rendered by**: `list_computers` route handler.
   - **HTMX Swapping**: None (full page render).

3. **`partials/computer_row.html`**
   - **Purpose**: A single table row fragment for a computer, used in search results and initial table population.
   - **Rendered by**: `search_computers_route`.
   - **HTMX Swapping**: Swapped into `#computer-table-body` on search.

4. **`partials/computer_form.html`**
   - **Purpose**: Form for adding or editing a computer record.
   - **Rendered by**: 
     - `new_computer_form` (add mode)
     - `edit_computer_form` (edit mode, pre-filled)
   - **HTMX Swapping**: Swapped into `#modal` for both add and edit operations.

5. **`partials/computer_detail.html`**
   - **Purpose**: Read-only view of a computer's details.
   - **Rendered by**: `computer_detail` route handler.
   - **HTMX Swapping**: Swapped into `#modal` when clicking on a computer name or row.

### Template Rendering Logic

- **Full Page Renders**:
  - `index.html` is rendered by `list_computers` as the main page.
  - `base.html` is extended by `index.html` and provides the overall structure.

- **Partial Swaps**:
  - `partials/computer_row.html` is returned by `search_computers_route` and swapped into `#computer-table-body`.
  - `partials/computer_form.html` is returned by `new_computer_form` and `edit_computer_form` and swapped into `#modal`.
  - `partials/computer_detail.html` is returned by `computer_detail` and swapped into `#modal`.

### Testing strategy

Test file: tests/test_routes_computers.py

- External dependencies to mock: None required.
- 3 bullet-pointed behaviors or edge cases to assert:
  - `list_computers` returns a `TemplateResponse` rendering `index.html`.
  - `search_computers_route` returns a list of `partials/computer_row.html` fragments when search matches are found.
  - `computer_detail` returns a `TemplateResponse` rendering `partials/computer_detail.html` when a computer is requested.
- pytest fixtures and plugins to use: `client` fixture from `conftest.py`.
- One line on coverage goals: "must exercise both the happy path AND the search result swap path".

## Test Plan

| Test file | Test name | Assertion |
|---|---|---|
| tests/test_crud.py | test_create_computer_success | All fields round-trip; `id` is set; `created_at` is a valid ISO-8601 string |
| tests/test_crud.py | test_create_computer_duplicate_rustdesk_id | Raises `IntegrityError` |
| tests/test_crud.py | test_get_all_computers_sorted | Three records returned in `friendly_name` ASC order |
| tests/test_crud.py | test_search_computers_by_name | Returns correct record |
| tests/test_crud.py | test_search_computers_by_rustdesk_id | Returns correct record |
| tests/test_crud.py | test_search_computers_by_ip | Returns correct record |
| tests/test_crud.py | test_search_computers_by_tag | Returns correct record |
| tests/test_crud.py | test_search_computers_by_notes | Returns correct record |
| tests/test_crud.py | test_update_computer | `friendly_name` updated; `updated_at` differs from `created_at` |
| tests/test_crud.py | test_delete_computer | Returns `True`; subsequent `get_computer` returns `None` |
| tests/test_crud.py | test_delete_nonexistent_computer | Returns `False` |
| tests/test_routes_computers.py | test_list_computers_empty | GET `/` → 200 |
| tests/test_routes_computers.py | test_create_computer_via_post | POST `/computers` valid data → redirect or 200; record in DB |
| tests/test_routes_computers.py | test_create_computer_missing_friendly_name | POST without `friendly_name` → 422 or form re-render with error |
| tests/test_routes_computers.py | test_create_computer_invalid_ip | POST with `local_ip="999.999.0.0"` → 422 or form error |
| tests/test_routes_computers.py | test_create_computer_duplicate_rustdesk_id | Second POST with same `rustdesk_id` → error response |
| tests/test_routes_computers.py | test_edit_computer | PUT `/computers/{id}` → updated record in DB |
| tests/test_routes_computers.py | test_delete_computer_route | DELETE `/computers/{id}` → 200; record gone from DB |
| tests/test_routes_computers.py | test_search_route_returns_match | GET `/computers/search?q=<name>` → 200 with row HTML |
| tests/test_routes_computers.py | test_search_route_no_match | GET `/computers/search?q=zzznomatch` → 200 with empty body |
| tests/test_routes_export.py | test_export_json_empty | GET `/export/json` with no records → 200, `[]` |
| tests/test_routes_export.py | test_export_json_with_data | Returns JSON array; each object has all `ComputerOut` fields |
| tests/test_routes_export.py | test_export_csv_headers | GET `/export/csv` → `text/csv`; first line equals expected header row |
| tests/test_routes_export.py | test_export_csv_with_data | Second line matches seeded record fields |

## Design Decisions

1. **Use of HTMX for partial updates**: HTMX is chosen for its simplicity and ability to enable progressive enhancement without requiring a complex frontend framework. This decision aligns with the lightweight nature of the application and avoids the overhead of SPA frameworks.

2. **SQLite as the database backend**: SQLite is selected due to its serverless nature, ease of deployment, and sufficient performance for an internal tool. It eliminates the need for a separate database server and simplifies the deployment process.

3. **ISO-8601 UTC timestamps for `created_at` and `updated_at`**: Using ISO-8601 format ensures consistent, unambiguous timestamp representation across different systems and time zones, which is crucial for a tool that may be used across different environments.

4. **Separation of concerns in CRUD operations**: The CRUD logic is separated into its own module (`crud.py`) to maintain clean architecture and make testing easier. This also allows for better code organization and reusability.

5. **Use of Pydantic schemas for validation**: Pydantic schemas are used for input validation and serialization, providing automatic validation, type checking, and error messages. This approach reduces boilerplate code and ensures data integrity.

6. **Jinja2 templates for HTML rendering**: Jinja2 is chosen for its simplicity and integration with FastAPI, allowing for clean separation of logic and presentation while supporting partial updates via HTMX.

7. **No custom JavaScript for modal handling**: The decision to rely on HTMX's built-in capabilities for modal handling (via `hx-get` and `hx-swap`) avoids the need for custom JavaScript and reduces the application's complexity.

8. **Single-page application structure with HTMX partials**: The application uses a single-page structure with HTMX partials for dynamic content updates, which provides a responsive user experience without the complexity of a full SPA.

9. **Use of `lru_cache` for settings**: The `@lru_cache` decorator is used for the `get_settings()` function to avoid repeated parsing of the environment file, improving performance while maintaining configuration flexibility.

10. **Database session management via FastAPI dependency**: Using FastAPI's dependency injection system for database sessions ensures proper lifecycle management and automatic cleanup, reducing the risk of connection leaks.

## Deployment Notes

### phonebook.service (systemd unit file)

```
[Unit]
Description=RustDesk Phone Book web application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/rust_phonebook
EnvironmentFile=/path/to/rust_phonebook/.env
ExecStart=/path/to/rust_phonebook/venv/bin/python -m phonebook.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### .env.example

```
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./phonebook.db
DEBUG=false
```

### nginx reverse-proxy snippet

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Quick Start (numbered single-page summary of steps 3–6)

1. Clone the repository: `git clone <repo-url> && cd rust_phonebook`
2. Create and activate a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install the package in development mode: `pip install -e .`
4. Run the application in production mode: `systemctl enable --now phonebook`

### Design Decisions

1. Use `Type=simple` in the systemd unit because the application is a single-process web server that does not fork.
2. Set `User=www-data` in the systemd unit to run the service under a dedicated user account for security isolation.
3. Use `EnvironmentFile` directive in the systemd unit to load environment variables from `.env` for configuration management.
4. Place the `phonebook.service` file in `/etc/systemd/system/` to ensure it's recognized by the systemd manager.
5. Use `proxy_pass` in the nginx configuration to forward requests to the local FastAPI server running on port 8000.
6. The `.env.example` file is placed at the root of the repository to provide a template for users to configure their environment.
7. The `README.md` includes a quick start section to guide new users through the most common setup steps.
8. The systemd unit file uses `Restart=on-failure` to automatically restart the service if it crashes, ensuring high availability.
