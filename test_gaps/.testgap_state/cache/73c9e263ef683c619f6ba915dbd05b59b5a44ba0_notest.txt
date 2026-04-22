# src/phonebook/models.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. [HIGH] `Computer`: test that all columns are properly defined with correct types, constraints, and defaults
2. [HIGH] `Computer`: verify primary key and unique constraints are enforced (rustdesk_id uniqueness)
3. [HIGH] `Computer`: validate datetime default and update behaviors for created_at and updated_at
4. [MEDIUM] `Computer`: test nullable column behaviors with None values
5. [MEDIUM] `Computer`: verify table name is correctly set to "computers"
6. [MEDIUM] `Computer`: test that all expected columns exist and have correct names
7. [LOW] `Computer`: validate column types match expected SQLAlchemy types
8. [LOW] `Computer`: test that Base class inheritance works correctly
9. [LOW] `Computer`: verify default values are properly set for datetime columns
10. [LOW] `Computer`: test that autoincrement works for id column

## Mock Strategy
- `sqlalchemy`: mock `declarative_base` and `Column` to test schema definition without database
- `datetime`: mock `datetime.utcnow` to control time in tests
- `sqlalchemy.engine`: mock database engine to test schema creation without real DB
- `sqlalchemy.orm.Session`: mock session to test model operations in isolation

The most critical mocks are for the SQLAlchemy components to avoid actual database interactions during testing. The datetime mock is essential for testing timestamp behaviors.
