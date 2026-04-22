# Module: src/phonebook/__init__.py

## Role
Package initializer that re-exports core components for simplified import paths.

## Contract: Module-level functions

### `__init__`
- **Requires:** All referenced modules (`config`, `database`, `models`, `crud`, `schemas`, `main`) must be importable and properly structured
- **Establishes:** Public API symbols are available at package level for direct imports
- **Raises:** ImportError — if any referenced module cannot be imported or symbols are missing

## Module Invariants
None

## Resource Lifecycle
None

Note: This file is a package marker that only re-exports symbols. No actual resources are created or managed by this module.
