# Module: src/phonebook/schemas.py

## Role
Defines Pydantic data models for creating, updating, and retrieving computer records with validation rules.

## Contract: ComputerCreate

### `__init__(params)`
- **Requires:** All parameters must be of type `str` or `None`; `friendly_name` and `rustdesk_id` must not be empty after stripping whitespace
- **Establishes:** Instance with validated and stripped string fields; `local_ip` and `tags` are validated if provided
- **Raises:** `ValueError` — when `friendly_name` length is not 1-120 characters, `rustdesk_id` length is not 1-64 characters, `local_ip` is invalid IP address, or any tag exceeds 40 characters

### `validate_friendly_name(v: str) -> str`
- **Requires:** `v` must be a string
- **Guarantees:** Returns stripped string with length 1-120 characters
- **Raises:** `ValueError` — if `v` is not 1-120 characters after stripping
- **Silent failure:** None
- **Thread safety:** safe

### `validate_rustdesk_id(v: str) -> str`
- **Requires:** `v` must be a string
- **Guarantees:** Returns stripped string with length 1-64 characters
- **Raises:** `ValueError` — if `v` is not 1-64 characters after stripping
- **Silent failure:** None
- **Thread safety:** safe

### `validate_local_ip(v: Optional[str]) -> Optional[str]`
- **Requires:** `v` must be `None` or a valid IP address string
- **Guarantees:** Returns `None` or valid IP address string
- **Raises:** `ValueError` — if `v` is not a valid IPv4 or IPv6 address
- **Silent failure:** None
- **Thread safety:** safe

### `validate_tags(v: Optional[str]) -> Optional[str]`
- **Requires:** `v` must be `None` or a comma-separated string
- **Guarantees:** Returns `None` or comma-separated string with each tag ≤ 40 characters
- **Raises:** `ValueError` — if any tag exceeds 40 characters
- **Silent failure:** None
- **Thread safety:** safe

### `strip_whitespace(v: str) -> str`
- **Requires:** `v` must be a string or `None`
- **Guarantees:** Returns stripped string or `None`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** safe

## Contract: ComputerUpdate

### `__init__(params)`
- **Requires:** All parameters must be of type `str` or `None`; fields are validated only if provided
- **Establishes:** Instance with validated and stripped string fields; `local_ip` and `tags` are validated if provided
- **Raises:** `ValueError` — when `friendly_name` length is not 1-120 characters, `rustdesk_id` length is not 1-64 characters, `local_ip` is invalid IP address, or any tag exceeds 40 characters

### `validate_friendly
