# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A FastAPI + HTMX web app for tracking RustDesk-managed computers. It is a standalone companion tool, **not** a fork of RustDesk. Single-box deployment to Ubuntu via uvicorn + systemd (`phonebook.service`).

`AGENTS.md` is the authoritative, detailed guide — read it for the full stack table, conventions, and "what not to do" list. This file is the quick-reference summary.

## Commands

- Install (editable): `pip install -e .`
- Run dev server: `uvicorn src.phonebook.main:app --reload` (reads `.env`; defaults `HOST=0.0.0.0 PORT=8000`)
- Run all tests: `pytest`
- Single file / single test: `pytest tests/test_crud.py -v` · `pytest tests/test_crud.py::test_create_computer_success -v`
- Lint/format: `ruff check .` / `ruff format .` (line-length 100)
- Seed sample data: `python seed_data.py`

Note: `pyproject.toml` is the source of truth for tooling (ruff, pytest `asyncio_mode = "auto"`). The stale `.serena/memories/` notes mention black/flake8 — ignore those; the project uses **ruff**.

## Architecture

Python src-layout under `src/phonebook/`:

- `main.py` — `create_app()` builds the FastAPI app, registers the `computers` and `export` routers, mounts `/static`, and wires Jinja2 templates. `lifespan` calls `init_db()` on startup.
- `config.py` — pydantic-settings `Settings`, memoized via `get_settings()` (`@lru_cache`). Reads `.env`.
- `database.py` — SQLAlchemy 2.0 **sync** engine/`SessionLocal`, `get_db()` dependency, `init_db()`.
- `models.py` / `schemas.py` — SQLAlchemy ORM models vs. Pydantic request/response schemas. Validation rules live in `schemas.py`.
- `crud.py` — synchronous data access over `Session` (not `AsyncSession`).
- `routes/computers.py`, `routes/export.py` — `async def` route handlers.
- `templates/` (Jinja2: `base.html`, `partials/*.html`), `static/` (`app.js`, `style.css`).

Key design invariants (see `AGENTS.md` for the full list):

- **Routes are async, CRUD is sync.** Don't bridge them with `asyncio.to_thread` without a demonstrated blocking problem, and don't migrate CRUD to async SQLAlchemy.
- **HTMX content-negotiation, no separate JSON API.** The `HX-Request` header selects full-page vs. partial responses. Modal swaps target `#modal`; row updates target `#computer-table-body`.
- **No JS framework, bundler, npm, CSS framework, or Docker.** HTMX (1.9.x via CDN) is the entire interactivity story; CSS uses `:root` custom properties + `prefers-color-scheme`.
- Timestamps: `datetime.utcnow().isoformat()`, stored as TEXT. Tags: comma-separated TEXT, normalized on insert, ≤40 chars each.

## Tests

`tests/conftest.py` provides `db_session` (function-scoped in-memory SQLite) and `client` (async httpx `AsyncClient` with `get_db` overridden to use `db_session`). Follow this fixture style for new tests — don't invent a parallel set.

## Pipeline-generated reference docs

`architecture/`, `bug_reports/`, and `test_gaps/` hold auto-generated snapshots from the `LocalLLM_Pipeline` toolkit (architecture maps, interface contracts, known-bug reports, coverage gaps). They reflect the code **as of pipeline run time and may have drifted** — always cross-check cited lines against current code before acting on a bug report. Slash commands `/bug`, `/gaps`, `/iface`, `/dataflow`, `/changes` wrap these reads.

## Repo hygiene

The repo root contains several stray files that are accidental shell-redirect captures from earlier failed tool runs (e.g. `DEBUG=false`, `python seed_data.py`, `uvicorn src.phonebook.main`, `}`, `cp phonebook.db phonebook_backup.db`). These are **not** real files to reference; safe to delete.
