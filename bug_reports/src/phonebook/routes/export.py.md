# src/phonebook/routes/export.py

## Findings

### Exception Handling Swallows Database Errors [HIGH]
- **Where:** `export_json()` ~lines 22-25, `export_csv()` ~lines 43-46
- **Issue:** Broad `except Exception as e:` clauses catch all exceptions including database connection errors, then raise generic HTTP 500 errors without logging or preserving original error context.
- **Impact:** Database failures during export operations are silently masked, making debugging difficult and potentially hiding critical issues like connection timeouts or permission problems.
- **Fix:** Catch specific database exceptions (e.g., SQLAlchemy errors) and log them before raising HTTP exceptions, or re-raise the original exception with proper context.

### Resource Leak in Database Session Management [HIGH]
- **Where:** Both functions, `export_json()` and `export_csv()` ~lines 12, 33
- **Issue:** Database session is acquired via `next(get_db())` but if an exception occurs before `db.close()` in finally block, the session may not be properly closed due to the context manager not being used.
- **Impact:** Database connection leaks can occur under error conditions, potentially exhausting connection pool limits and causing application instability.
- **Fix:** Use a proper context manager (`with` statement) or ensure `db.close()` is called in all code paths including error conditions.

### Potential None Dereference in CSV Export [MEDIUM]
- **Where:** `export_csv()` ~lines 37-41
- **Issue:** The code assumes `ComputerOut.model_fields.keys()` will always return valid field names, but if the model schema changes or becomes corrupted, this could lead to unexpected behavior.
- **Impact:** In rare cases, malformed model fields could cause CSV generation to fail or produce incorrect headers.
- **Fix:** Add validation that `ComputerOut.model_fields` is not empty and contains valid keys before proceeding with CSV generation.

### Missing Error Handling for CSV Writer Operations [LOW]
- **Where:** `export_csv()` ~lines 38-41
- **Issue:** The `csv.DictWriter` operations (`writeheader()`, `writerow()`) are not wrapped in try/except blocks, so any I/O errors during CSV generation would propagate up unhandled.
- **Impact:** If there's an issue writing to the StringIO buffer, the application could crash instead of gracefully handling the error.
- **Fix:** Wrap CSV writer operations in try/except blocks to catch and handle potential I/O errors during CSV generation.

## Verdict

ISSUES FOUND
