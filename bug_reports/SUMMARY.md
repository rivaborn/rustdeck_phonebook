# Bug Hunt Summary

Generated: 2026-04-22 17:23
Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.

## Files with HIGH / MEDIUM findings

- `src/phonebook/__init__.py.md` -- HIGH:1 MED:1
- `src/phonebook/config.py.md` -- MED:2
- `src/phonebook/crud.py.md` -- HIGH:1 MED:1
- `src/phonebook/database.py.md` -- HIGH:2 MED:1
- `src/phonebook/main.py.md` -- HIGH:1 MED:1
- `src/phonebook/routes/computers.py.md` -- HIGH:1 MED:1
- `src/phonebook/routes/export.py.md` -- HIGH:2 MED:1
- `src/phonebook/schemas.py.md` -- MED:1

## Totals

| Severity | Count |
|----------|-------|
| HIGH     | 8 |
| MEDIUM   | 9 |
| LOW      | 5 |
| CLEAN    | 2 files |

Reports in: `C:\Coding\WorkFolder\rustdeck_phonebook\bug_reports`
