# Module: src/phonebook/crud.py

## Role
Provides database CRUD operations for Computer entities with search and update capabilities.

## Contract: Module-level functions

### `get_all_computers(db: Session) -> list[Computer]`
- **Requires:** `db` must be a valid SQLAlchemy session object with active database connection
- **Guarantees:** Returns a list of all Computer objects ordered by friendly_name in ascending order; empty list if no computers exist
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

### `get_computer(db: Session, computer_id: int) -> Computer | None`
- **Requires:** `db` must be a valid SQLAlchemy session object; `computer_id` must be a non-negative integer
- **Guarantees:** Returns Computer object if found, None if not found
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

### `search_computers(db: Session, q: str) -> list[Computer]`
- **Requires:** `db` must be a valid SQLAlchemy session object; `q` must be a non-empty string
- **Guarantees:** Returns list of Computer objects matching search query across multiple fields using OR logic
- **Raises:** `ValueError` -- when `q` is empty string
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

### `create_computer(db: Session, data: ComputerCreate) -> Computer`
- **Requires:** `db` must be a valid SQLAlchemy session object; `data` must be a valid ComputerCreate schema object with all required fields populated
- **Guarantees:** Returns newly created Computer object with generated ID and timestamps set
- **Raises:** `sqlalchemy.exc.IntegrityError` -- if database constraint violation occurs (e.g., duplicate unique fields)
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

### `update_computer(db: Session, computer_id: int, data: ComputerUpdate) -> Computer | None`
- **Requires:** `db` must be a valid SQLAlchemy session object; `computer_id` must be a non-negative integer; `data` must be a valid ComputerUpdate schema object
- **Guarantees:** Returns updated Computer object if found, None if not found
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

### `delete_computer(db: Session, computer_id: int) -> bool`
- **Requires:** `db` must be a valid SQLAlchemy session object; `computer_id` must be a non-negative integer
- **Guarantees:** Returns True if computer was deleted, False if not found
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external lock if db session is shared across threads

## Module Invariants
- All database operations are performed within the provided session context
- Timestamps are always stored in ISO format with UTC timezone
- Computer objects are always refreshed after creation and updates to ensure consistency
- Search queries are case
