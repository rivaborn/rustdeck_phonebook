# Module: src/phonebook/routes/__init__.py

## Role
Package initializer that re-exports route-related components from sibling modules.

## Contract: Module-level functions

### `__init__`
- **Requires:** `src.phonebook.routes.computers` module must exist and define `router` and `templates` symbols
- **Establishes:** Package becomes importable and re-exports `router` and `templates` from `computers` module
- **Raises:** `ImportError` — if `src.phonebook.routes.computers` cannot be imported or does not contain required symbols

## Module Invariants
None

## Resource Lifecycle
None
