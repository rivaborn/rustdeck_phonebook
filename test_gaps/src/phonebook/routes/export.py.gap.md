# src/phonebook/routes/export.py

## Overall
PARTIAL - Tests cover basic functionality but miss critical error handling and edge cases.

## Untested Public Interface
- `export_json`: Missing tests for empty database results and serialization errors
- `export_csv`: Missing tests for empty database results and CSV generation errors

## Untested Error Paths
- Condition: Database connection failure in `export_json` - no test covers `get_db()` raising exception
- Condition: Database connection failure in `export_csv` - no test covers `get_db()` raising exception  
- Condition: `get_all_computers` raising exception - no test covers CRUD function failure
- Condition: `ComputerOut.model_validate()` raising validation error - no test covers schema validation failure
- Condition: CSV writing errors - no test covers `csv.DictWriter` exceptions

## Fixture and Mock Quality
- `mock_get_db`: Bypasses actual database session lifecycle and connection handling, could miss connection-related bugs
- `mock_computers`: Uses hardcoded test data that may not match real database schema, hiding potential serialization issues

## Broken or Misleading Tests
- `test_export_json`: Only tests single computer case, doesn't verify complete ComputerOut schema serialization
- `test_export_csv`: Doesn't verify CSV structure matches ComputerOut fields exactly, only checks for presence of hostname

## Priority Gaps
1. [HIGH] Test database connection failure scenarios in both export functions to ensure proper HTTP 500 responses
2. [HIGH] Test empty database results for both JSON and CSV exports to verify proper handling of no data
3. [MEDIUM] Test ComputerOut schema validation errors to ensure proper error propagation
4. [MEDIUM] Test CSV generation with various computer data types to ensure field mapping correctness
5. [LOW] Test CSV header row generation when no computers exist to verify CSV structure consistency
