# src/phonebook/routes/__init__.py

## Purpose
Initializes the routes package and re-exports key routing components for easy access.

## Responsibilities
- Makes the containing directory importable as a Python package
- Re-exports router and templates from the computers module
- Provides a clean interface for importing route components

## Key Types
None

## Key Functions
None

## Globals
None

## Dependencies
- `.computers` (module): provides `router` and `templates` symbols
- `from .computers import router, templates` (import statement)
