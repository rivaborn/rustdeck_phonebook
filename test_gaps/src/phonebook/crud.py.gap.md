# src/phonebook/crud.py

## Overall
PARTIAL - Tests cover most CRUD operations but miss critical error handling and edge cases.

## Untested Public Interface
- `search_computers`: Missing test for empty search query (ValueError not raised)
- `update_computer`: Missing test for when computer_id doesn't exist (returns None)
- `delete_computer`: Missing test for when computer_id doesn't exist (returns False)
- `get_computer`: Missing test for when computer_id doesn't exist (returns None)

## Untested Error Paths
- Condition: `search_computers` raises `ValueError` when q is empty string
- Condition: `update_computer` returns `None` when computer doesn't exist
- Condition: `delete_computer` returns `False` when computer doesn't exist
- Condition: `get_computer` returns `None` when computer doesn't exist

## Fixture and Mock Quality
- `db_session`: Uses in-memory SQLite but doesn't test actual database constraints or connection failures
- `get_db`: Mocked in tests but not tested for actual database connection behavior

## Broken or Misleading Tests
- `test_computer_create_validation_friendly_name_empty`: Tests validation but doesn't verify it's raised by the CRUD function, not the Pydantic model
- `test_computer_create_validation_friendly_name_too_long`: Tests validation but doesn't verify it's raised by the CRUD function, not the Pydantic model
- `test_computer_create_validation_rustdesk_id_empty`: Tests validation but doesn't verify it's raised by the CRUD function, not the Pydantic model
- `test_computer_create_validation_rustdesk_id_too_long`: Tests validation but doesn't verify it's raised by the CRUD function, not the Pydantic model
- `test_computer_create_validation_invalid_local_ip`: Tests validation but doesn't verify it's raised by the CRUD function, not the Pydantic model

## Priority Gaps
1. [HIGH] Test `search_computers` with empty query parameter to ensure ValueError is raised
2. [HIGH] Test `update_computer` with non-existent computer_id to ensure None is returned
3. [HIGH] Test `delete_computer` with non-existent computer_id to ensure False is returned
4. [MEDIUM] Test `get_computer` with non-existent computer_id to ensure None is returned
5. [MEDIUM] Test `create_computer` with database constraint violations to ensure proper error handling
