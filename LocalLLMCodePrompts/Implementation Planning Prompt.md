# RustDesk Phone Book — Web Application Architecture Planning Prompt

## Role and Task

You are an expert software architect. Produce a **complete Architecture Plan** for the RustDesk Phone Book web application described below. The plan will be consumed by a downstream code-generation stage. **Do not generate code.** Output only the architecture plan with the deliverables specified at the end of this document.

---

## Project Identity

- **Package name:** `phonebook`
- **Repository root name:** `rust_phonebook`
- **Mandatory layout — Python src-layout:**

```
rust_phonebook/
├── src/
│   └── phonebook/
│       ├── __init__.py
│       ├── main.py               # FastAPI app factory + lifespan
│       ├── config.py             # pydantic-settings Settings class
│       ├── database.py           # engine, SessionLocal, init_db(), get_db()
│       ├── models.py             # SQLAlchemy ORM models + declarative Base
│       ├── schemas.py            # Pydantic request/response schemas
│       ├── crud.py               # all database operations
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── computers.py      # CRUD + search HTML/HTMX routes
│       │   └── export.py         # JSON + CSV export routes
│       ├── templates/
│       │   ├── base.html
│       │   ├── index.html
│       │   └── partials/
│       │       ├── computer_row.html
│       │       ├── computer_form.html
│       │       └── computer_detail.html
│       └── static/
│           ├── style.css
│           └── app.js            # clipboard + confirm helpers only
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

---

## Application Purpose

A lightweight internal web application that runs on an Ubuntu server and is reachable on a local network through a browser. Its purpose is to maintain a list of RustDesk-managed computers/endpoints. Users can add, edit, delete, search, view details of, and export computer records. The app is a standalone companion tool and must not modify RustDesk source code.

---

## Tech Stack (Mandatory — No Substitutions)

| Layer | Technology | Version Constraint |
|---|---|---|
| Language | Python | ≥ 3.11 |
| Web framework | FastAPI | ≥ 0.111 |
| Template engine | Jinja2 (via `Jinja2Templates`) | ≥ 3.1 |
| Partial UI updates | HTMX | 1.9.x via CDN — no npm |
| ORM | SQLAlchemy | ≥ 2.0 (ORM + Core) |
| Database | SQLite | stdlib — no server |
| Settings | pydantic-settings | ≥ 2.0 |
| ASGI server | Uvicorn | ≥ 0.29 |
| Testing | pytest + httpx (`AsyncClient`) | pytest ≥ 8, httpx ≥ 0.27 |
| Linting / formatting | ruff | ≥ 0.4 |

No Docker is required. No Node.js or npm build step. No SPA framework.

---

## Data Model

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

### Validation Rules (enforced in Pydantic schemas)

- `friendly_name`: 1–120 characters, required, strip whitespace.
- `rustdesk_id`: 1–64 characters, required, unique, strip whitespace.
- `local_ip`: optional; when present, validate IPv4 (each octet 0–255) or IPv6 with Python's `ipaddress` stdlib module — do not use a hand-rolled regex alone.
- `tags`: optional; split on comma, strip each tag, re-join; each tag ≤ 40 characters; store normalized.
- All `TEXT` fields: strip leading/trailing whitespace before persistence.

---

## Module Responsibilities

### `src/phonebook/config.py`

- Defines `Settings(BaseSettings)` with fields:
  - `HOST: str = "0.0.0.0"`
  - `PORT: int = 8000`
  - `DATABASE_URL: str = "sqlite:///./phonebook.db"`
  - `DEBUG: bool = False`
- `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")`.
- Exports `get_settings() -> Settings` decorated with `@lru_cache`.

### `src/phonebook/database.py`

- Imports `Settings` from `phonebook.config` via `get_settings()`.
- Creates `engine` using `create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})`.
- Creates `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
- Exports `init_db() -> None` — calls `Base.metadata.create_all(bind=engine)`.
- Exports `get_db()` — FastAPI dependency that yields a `Session` and closes it in a `finally` block.
- `Base` is imported from `phonebook.models`.

### `src/phonebook/models.py`

- Declares `Base = declarative_base()`.
- Defines `Computer(Base)` with all columns from the data model table above.
- `__tablename__ = "computers"`.
- `created_at` and `updated_at` default to `datetime.utcnow().isoformat()` via `default=` and `onupdate=` respectively.

### `src/phonebook/schemas.py`

- `ComputerCreate(BaseModel)` — all writable fields; applies all validation rules above.
- `ComputerUpdate(BaseModel)` — same fields, all optional; validation still fires when a field is provided.
- `ComputerOut(BaseModel)` — all fields including `id`, `created_at`, `updated_at`; `model_config = ConfigDict(from_attributes=True)`.

### `src/phonebook/crud.py`

All functions are synchronous. Exact signatures:

- `get_all_computers(db: Session) -> list[Computer]` — `ORDER BY friendly_name ASC`.
- `get_computer(db: Session, computer_id: int) -> Computer | None`
- `search_computers(db: Session, q: str) -> list[Computer]` — case-insensitive `LIKE %q%` across `friendly_name`, `rustdesk_id`, `hostname`, `local_ip`, `tags`, `notes`; uses SQLAlchemy `or_()`.
- `create_computer(db: Session, data: ComputerCreate) -> Computer`
- `update_computer(db: Session, computer_id: int, data: ComputerUpdate) -> Computer | None`
- `delete_computer(db: Session, computer_id: int) -> bool` — returns `True` if a row was deleted, `False` if not found.

### `src/phonebook/routes/computers.py`

- Imports: `get_db` from `phonebook.database`; all six crud functions from `phonebook.crud`; `ComputerCreate`, `ComputerUpdate` from `phonebook.schemas`; `Computer` from `phonebook.models`.
- Detects HTMX requests via `HX-Request` header to decide between full-page and partial `TemplateResponse`.
- All route handler functions are `async def`.

### `src/phonebook/routes/export.py`

- Imports: `get_db` from `phonebook.database`; `get_all_computers` from `phonebook.crud`; `ComputerOut` from `phonebook.schemas`.
- `export_json` serializes via `ComputerOut` and returns `JSONResponse`.
- `export_csv` streams via Python's `csv.DictWriter` and returns `StreamingResponse` with `text/csv` content type and `Content-Disposition: attachment; filename="phonebook.csv"`.

### `src/phonebook/main.py`

- Defines the FastAPI `app` using a `lifespan` async context manager that calls `init_db()` on startup.
- Mounts `StaticFiles` at `/static` pointed at `src/phonebook/static/`.
- Instantiates `Jinja2Templates` pointed at `src/phonebook/templates/`.
- Registers both routers (from `computers.py` and `export.py`).
- `uvicorn phonebook.main:app` is the entry point.
- Host and port are read from `get_settings()`.

---

## API Endpoints

### HTML / HTMX Routes (`src/phonebook/routes/computers.py`)

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

Query parameter for search: `q` (string, required, minimum 1 character).

### Export Routes (`src/phonebook/routes/export.py`)

| Method | Path | Handler | Returns |
|---|---|---|---|
| GET | `/export/json` | `export_json` | `application/json` array |
| GET | `/export/csv` | `export_csv` | `text/csv` attachment |

---

## UI Requirements

### `base.html`

- `<head>`: charset, viewport, HTMX CDN `<script>` tag, `<link>` to `style.css`.
- `<nav>`: app title ("RustDesk Phone Book"), "Add Computer" button (HTMX `hx-get="/computers/new"` swapping into `#modal`), search input (HTMX `hx-get="/computers/search"` with `hx-trigger="input changed delay:300ms"`, targeting `#computer-table-body`), export links to `/export/json` and `/export/csv`.
- `<main id="content">`: Jinja2 `{% block content %}` placeholder.
- `<div id="modal">`: empty; HTMX swaps form and detail partials here.

### `index.html`

- Extends `base.html`.
- Renders `<table>` with columns: Friendly Name, RustDesk ID, OS, Location, Tags, Updated.
- `<tbody id="computer-table-body">` populated by `computer_row.html` partials.
- Each row's Delete button uses `hx-delete`, `hx-confirm`, `hx-target="closest tr"`, `hx-swap="outerHTML"`.
- Each row's Edit button uses `hx-get="/computers/{id}/edit"`, swapping into `#modal`.
- Clicking the Friendly Name cell triggers `hx-get="/computers/{id}"` swapping into `#modal`.

### `partials/computer_row.html`

- A single `<tr>` fragment. Rendered by `search_computers_route` (multiple) and returned as OOB swap after create/update.

### `partials/computer_form.html`

- Add/edit form for all 10 writable fields.
- Each field has a `<label>`, `<input>` or `<textarea>`, and an optional `<span class="field-error">` for per-field validation messages.
- Uses HTMX `hx-post="/computers"` (add) or `hx-put="/computers/{id}"` (edit).
- Submit button text: "Save Computer".
- Cancel button clears `#modal`.

### `partials/computer_detail.html`

- Read-only view of all fields.
- Copy-to-clipboard button beside `rustdesk_id`: `onclick="copyToClipboard('...')"`.
- Copy-to-clipboard button beside `local_ip` (when present): same pattern.
- Tags rendered as `<span class="tag">` badges.
- `created_at` and `updated_at` displayed with human-readable formatting (e.g. `2025-04-21 14:30 UTC`).
- Edit button links to edit form.

### `static/style.css`

- CSS custom properties at `:root`: `--color-bg`, `--color-surface`, `--color-accent`, `--color-text`, `--color-danger`, `--color-muted`.
- `@media (prefers-color-scheme: dark)` block overrides those variables; no class toggle required.
- Responsive table: at `< 768px`, rows collapse into labeled card layout using `data-label` attributes and `::before` pseudo-elements.
- `.tag` class: pill badge (border-radius, background `--color-accent` at low opacity, padding).
- `.field-error` class: red small text beneath invalid fields.
- Modal overlay: `#modal` is fixed-position when it contains content; clicking outside clears it via HTMX.
- No external CSS framework.

### `static/app.js`

Must contain **only** the following two functions and nothing else:

1. `function copyToClipboard(text)` — uses `navigator.clipboard.writeText(text)`; shows a brief "Copied!" tooltip.
2. `function confirmDelete(event, form)` — not needed because HTMX handles `hx-confirm`; this function may be omitted if HTMX's built-in confirm is sufficient (record this as a Design Decision).

No other JavaScript. No import statements. No module syntax.

---

## Configuration

### `.env.example`

```
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./phonebook.db
DEBUG=false
```

### `pyproject.toml` requirements

- `[build-system]`: `setuptools`, `wheel`.
- `[project]`: name `phonebook`, requires-python `>=3.11`, dependencies list matching the tech stack table.
- `[project.scripts]`: `phonebook = "phonebook.main:run"` where `run()` calls `uvicorn.run(app, host=..., port=...)`.
- `[tool.ruff]` configuration block with `line-length = 100`.
- `[tool.pytest.ini_options]`: `asyncio_mode = "auto"`, `testpaths = ["tests"]`.

---

## Testing Strategy

### `tests/conftest.py`

- Fixture `db_session` (scope `"function"`): creates an in-memory SQLite engine (`"sqlite:///:memory:"`), calls `init_db()` against it, yields a `Session`, drops all tables after each test.
- Fixture `client` (scope `"function"`, async): creates `httpx.AsyncClient` with the FastAPI `app`, overrides the `get_db` dependency to use `db_session`.

### `tests/test_crud.py`

Synchronous tests using `db_session` directly:

| Test name | Assertion |
|---|---|
| `test_create_computer_success` | All fields round-trip; `id` is set; `created_at` is a valid ISO-8601 string |
| `test_create_computer_duplicate_rustdesk_id` | Raises `IntegrityError` |
| `test_get_all_computers_sorted` | Three records returned in `friendly_name` ASC order |
| `test_search_computers_by_name` | Returns correct record |
| `test_search_computers_by_rustdesk_id` | Returns correct record |
| `test_search_computers_by_ip` | Returns correct record |
| `test_search_computers_by_tag` | Returns correct record |
| `test_search_computers_by_notes` | Returns correct record |
| `test_update_computer` | `friendly_name` updated; `updated_at` differs from `created_at` |
| `test_delete_computer` | Returns `True`; subsequent `get_computer` returns `None` |
| `test_delete_nonexistent_computer` | Returns `False` |

### `tests/test_routes_computers.py`

Async tests using `client`:

| Test name | Assertion |
|---|---|
| `test_list_computers_empty` | GET `/` → 200 |
| `test_create_computer_via_post` | POST `/computers` valid data → redirect or 200; record in DB |
| `test_create_computer_missing_friendly_name` | POST without `friendly_name` → 422 or form re-render with error |
| `test_create_computer_invalid_ip` | POST with `local_ip="999.999.0.0"` → 422 or form error |
| `test_create_computer_duplicate_rustdesk_id` | Second POST with same `rustdesk_id` → error response |
| `test_edit_computer` | PUT `/computers/{id}` → updated record in DB |
| `test_delete_computer_route` | DELETE `/computers/{id}` → 200; record gone from DB |
| `test_search_route_returns_match` | GET `/computers/search?q=<name>` → 200 with row HTML |
| `test_search_route_no_match` | GET `/computers/search?q=zzznomatch` → 200 with empty body |

### `tests/test_routes_export.py`

Async tests using `client` with at least one seeded record:

| Test name | Assertion |
|---|---|
| `test_export_json_empty` | GET `/export/json` with no records → 200, `[]` |
| `test_export_json_with_data` | Returns JSON array; each object has all `ComputerOut` fields |
| `test_export_csv_headers` | GET `/export/csv` → `text/csv`; first line equals expected header row |
| `test_export_csv_with_data` | Second line matches seeded record fields |

---

## Seed Data

`seed/seed_data.py` is a **standalone script** (not part of the `phonebook` package):

- Imports `SessionLocal` from `phonebook.database` and `create_computer` from `phonebook.crud` and `ComputerCreate` from `phonebook.schemas`.
- Inserts exactly **5 sample records** covering: Windows, macOS, Ubuntu, Raspberry Pi OS, and one unspecified OS; multiple tags; diverse locations.
- Idempotent: wraps each insert in a `try/except IntegrityError` and skips if `rustdesk_id` already exists.
- Runnable with `python seed/seed_data.py` from repo root (uses `PYTHONPATH=src` or `pip install -e .`).

---

## Deployment Deliverables

### `phonebook.service` (systemd unit)

Must include:

- `[Unit]`: `Description`, `After=network.target`.
- `[Service]`: `Type=simple`, `User=`, `WorkingDirectory=<repo root>`, `EnvironmentFile=<repo root>/.env`, `ExecStart=<venv>/bin/python -m phonebook.main`, `Restart=on-failure`, `RestartSec=5`.
- `[Install]`: `WantedBy=multi-user.target`.

### `README.md` — Mandatory Sections

1. What the app does
2. Prerequisites (Python 3.11+, git, Ubuntu 22.04+)
3. Installation (`git clone`, create venv, `pip install -e .`)
4. Running in development (`uvicorn phonebook.main:app --reload --host 0.0.0.0 --port 8000`)
5. Running in production (systemd: copy unit file, `systemctl enable --now phonebook`)
6. Accessing from another LAN machine (`http://<server-ip>:8000`)
7. Configuring host/port via `.env`
8. Seeding sample data (`python seed/seed_data.py`)
9. Backing up the database (`cp phonebook.db phonebook.db.bak`)
10. Running behind nginx (minimal `location /` proxy_pass snippet)
11. Quick Start (numbered single-page summary of steps 3–6)

---

## Deliverables (Architecture Plan Output)

The Architecture Plan must contain all of the following sections:

1. **Project structure** — annotated directory tree matching the layout above exactly.
2. **Module sections** — one `## Module: src/phonebook/<name>.py` section per Python source file, containing: purpose statement, list of public symbols, full pseudocode for every function/class, and a `Test file:` line at the end of the section.
3. **Data model** — table specification matching the schema above, plus `created_at`/`updated_at` lifecycle notes.
4. **API endpoint table** — complete route list: method, path, handler function name, template rendered or response type.
5. **Template map** — each template file, which route(s) render it, which HTMX target it swaps into.
6. **Test plan** — per-file table of test names and assertions matching the testing strategy above.
7. **Design Decisions** — a numbered list of implementation choices made with rationale. Each entry must be a decision with justification. Deferred questions are not permitted.
8. **Deployment notes** — full systemd unit file content, `.env.example` content, nginx reverse-proxy snippet.

---

## Hard Constraints for Architecture Plan Generation

The following are non-negotiable rules. The Architecture Plan is invalid
(and Stage 3 must not run) if any is violated:

1. **Single source of truth per symbol.** Each class, function,
   dataclass, and module-level constant is defined in EXACTLY ONE
   module section. Other sections may reference it by name but must
   not restate its signature, fields, or body. Sections for
   `__init__.py` files list re-exports only — they name the public
   symbols the package exposes and nothing else (no class bodies,
   no method signatures).

2. **No open questions on prompt-specified items.** If this Planning
   Prompt names a concrete requirement (endpoint, field, signature,
   behavior), the Architecture Plan must implement it. "Open Question"
   is not an acceptable deliverable for anything specified above. When
   a genuine ambiguity remains (an implementation detail this prompt
   did not address), record a Design Decision with rationale — not a
   question.

3. **Signature fidelity.** Every method signature in the Architecture
   Plan must match this Planning Prompt verbatim on: async/sync
   modifier, parameter names, parameter types, return type. Do not
   rename parameters or re-order them.

4. **Import-path canonicalization.** Before writing any pseudocode
   that imports a symbol, the plan must declare which module owns
   that symbol. Any cross-module reference uses the canonical import
   path and no synonyms (do not rename `Config` to `AppConfig` or
   `ConfigLoader` across sections).

5. **Each module section names its test file.** Every
   `## Module: src/<pkg>/**/<name>.py` section must end with an
   explicit `Test file: tests/test_<name>.py` reference so Stage 3's
   step planner can pair production modules with their tests.

---