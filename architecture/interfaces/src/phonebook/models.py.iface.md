# Module: src/phonebook/models.py

## Role
Defines SQLAlchemy ORM models for computer inventory management with timestamp tracking.

## Contract: Computer

### `__init__(params)`
- **Requires:** No parameters required for construction; all fields are initialized by SQLAlchemy
- **Establishes:** Instance represents a database row with all columns mapped to Python attributes; primary key auto-increment enabled
- **Raises:** None

### `id`
- **Requires:** None
- **Guarantees:** Integer primary key value; auto-incremented on insert
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `friendly_name`
- **Requires:** String value; cannot be None
- **Guarantees:** String value stored in database; raises SQLAlchemy IntegrityError if constraint violated
- **Raises:** sqlalchemy.exc.IntegrityError -- when value is None or constraint violated
- **Silent failure:** None
- **Thread safety:** Unsafe

### `rustdesk_id`
- **Requires:** String value; cannot be None
- **Guarantees:** String value stored in database; unique constraint enforced
- **Raises:** sqlalchemy.exc.IntegrityError -- when value is None or duplicate found
- **Silent failure:** None
- **Thread safety:** Unsafe

### `hostname`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `local_ip`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `operating_system`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `username`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `location`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `notes`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `tags`
- **Requires:** String value or None
- **Guarantees:** String value or None stored in database
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `created_at`
- **Requires:** None
- **Guarantees:** DateTime value; defaults to current UTC time on insert
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `updated_at`
- **Requires:** None
- **Guarantees:** DateTime value; defaults to current UTC time on insert, updates on record
