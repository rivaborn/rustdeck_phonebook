# rustdeck_phonebook — agent instructions

A FastAPI + HTMX web app for tracking RustDesk-managed computers. Companion tool, not a fork of RustDesk. Single-box deployment to Ubuntu over uvicorn + systemd.

## Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Web framework | FastAPI ≥ 0.111 | |
| Templates | Jinja2 | server-rendered, no SPA |
| Partial UI | HTMX 1.9.x via CDN | no npm, no bundler |
| ORM | SQLAlchemy 2.0 (sync) | not async — see "What not to do" |
| DB | SQLite (stdlib) | single file: `phonebook.db` |
| Settings | pydantic-settings 2.x | reads `.env` |
| Server | Uvicorn ≥ 0.29 | |
| Tests | pytest + httpx AsyncClient | `pytest_asyncio_mode = "auto"` |
| Lint/format | ruff (line-length 100) | |

## Layout (Python src-layout)

```
src/phonebook/
  __init__.py     config.py     database.py
  main.py         models.py     schemas.py
  crud.py         routes/{__init__.py, computers.py, export.py}
  templates/      static/
tests/            seed/         pyproject.toml
```

## Pipeline-generated references (read on demand, do not inline)

The `LocalLLM_Pipeline` toolkit produced these artifacts. They reflect the codebase as of pipeline run time — newer code may have drifted.

| When I ask about... | Read first |
|---|---|
| Overall architecture / what lives where | `architecture/architecture.md` |
| Cross-module data flow | `architecture/DATA_FLOW.md` |
| Function/method signatures + contracts | `architecture/INTERFACES.md` or `architecture/interfaces/src/phonebook/<file>.iface.md` |
| Cross-references for a symbol | `architecture/xref_index.md`, or use **serena** (preferred) |
| Module call graph | `architecture/callgraph.md`, `architecture/callgraph.mermaid` |
| Subsystem map | `architecture/subsystems.mermaid` |
| Known bugs in a file | `bug_reports/src/phonebook/<file>.py.md` (e.g. `bug_reports/src/phonebook/crud.py.md`) |
| Bug roll-up across files | `bug_reports/SUMMARY.md` |
| Missing test coverage per file | `test_gaps/src/phonebook/<file>.py.gap.md` |
| Coverage roll-up | `test_gaps/GAP_REPORT.md` |
| Auto-applied debug fixes | `.debug_changes.md` if present (debug Step 5 may not have run) |

Slash commands `/bug`, `/gaps`, `/iface`, `/dataflow`, `/changes` wrap these reads. Use them.

## Tool routing

- **Library API questions** (FastAPI, SQLAlchemy v2, Pydantic v2, HTMX): always **context7** MCP first. Local model knowledge is stale; FastAPI and Pydantic v2 changed substantially between training and now.
- **Symbol navigation, find references, where is X defined**: **serena** MCP (`find_symbol`, `find_referencing_symbols`). The pipeline already populated `architecture/.serena_context/` so cold-start is fast.
- **Browser / page rendering checks** (when I'm working on templates or static CSS): **playwright** MCP.
- **Anything deterministic** (regex testing, timestamp math, CSV/JSON shape verification): bash + `python -c`.

## Project conventions

- **Routes are async, CRUD is sync.** `routes/computers.py` and `routes/export.py` use `async def`; `crud.py` operates on `Session` (not `AsyncSession`) and is fully synchronous. Don't bridge them with `asyncio.to_thread` unless an actual blocking-call problem is demonstrated.
- **HTMX request detection**: the `HX-Request` header decides full-page vs partial responses. Don't introduce a separate JSON API for the same endpoints.
- **Timestamps**: `datetime.utcnow().isoformat()` for `created_at` / `updated_at`. Both stored as TEXT.
- **Tags**: comma-separated TEXT, normalized (strip + rejoin) on insert. Each tag ≤ 40 chars.
- **Validation**: Pydantic schemas in `schemas.py` carry the rules. Validate at the route boundary; CRUD assumes validated input.
- **Templates**: `base.html` extends; `partials/*.html` are HTMX-swap targets. Modal swaps go into `#modal`; row updates into `#computer-table-body`.
- **No external CSS framework.** Custom properties at `:root` + `@media (prefers-color-scheme: dark)` overrides.
- **`static/app.js`** holds exactly two functions: `copyToClipboard` and (optionally) `confirmDelete`. No imports, no module syntax.

## What not to do

- **Don't move CRUD to async SQLAlchemy.** This is a single-box SQLite app; the sync overhead is negligible and async SQLite has worse bug surface area. Documented design decision.
- **Don't add a JS framework or bundler.** HTMX is the entire interactivity story. No React, no Vue, no Webpack.
- **Don't replace Jinja2 with a different template engine.**
- **Don't add Docker.** Deployment is `git clone` + venv + systemd unit. The `phonebook.service` file in the repo root is the deployment artifact.
- **Don't "fix" findings the pipeline already validated as design choices.** When `architecture/architecture.md` records a decision (e.g. "no separate JSON API; HTMX content-negotiation only"), treat it as authoritative unless I explicitly say to revisit it.
- **Don't auto-trust old bug reports.** The reports are pre-fix snapshots. Always cross-check the cited line(s) against current code via serena before proposing the same fix again. The slash commands do this; if you're operating manually, do it manually.

## Testing

- Run all: `pytest`
- Single file: `pytest tests/test_crud.py -v`
- Single test: `pytest tests/test_crud.py::test_create_computer_success -v`
- Conftest fixtures: `db_session` (function-scoped, in-memory SQLite), `client` (function-scoped async httpx with `get_db` overridden to use `db_session`).

When proposing new tests, follow the conftest fixture style — don't invent a parallel fixture set.

## Repo hygiene flagged for cleanup (not blocking)

The repo root contains several files that look like accidental shell-redirect captures from earlier failed aider runs:
- `cp phonebook.db phonebook_backup.db`
- `DEBUG=false`
- `python seed_data.py`
- `sudo systemctl enable phonebook.service`
- `sudo systemctl start rustdesk-phonebook`
- `uvicorn src.phonebook.main`
- `}`

These are not real files anyone should reference. Safe to delete when convenient.
