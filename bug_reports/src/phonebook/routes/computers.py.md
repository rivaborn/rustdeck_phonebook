# src/phonebook/routes/computers.py

## Findings

### Missing Database Connection Cleanup [HIGH]
- **Where:** All route functions using `next(get_db())` ~lines 12, 23, 34, 45, 56, 67, 78
- **Issue:** Database connection is acquired with `next(get_db())` but never explicitly closed, relying on generator cleanup which may not happen immediately.
- **Impact:** Potential resource leak if database connections aren't promptly returned to pool, especially under high load.
- **Fix:** Wrap database acquisition in a `try/finally` block or use context manager to ensure connection is properly closed.

### Inconsistent Error Handling for IntegrityError [MEDIUM]
- **Where:** `create_computer_route` and `update_computer_route` ~lines 62-65, 73-76
- **Issue:** `IntegrityError` is caught and handled, but `delete_computer_route` catches `IntegrityError` and re-raises as `HTTPException` without proper rollback in all code paths.
- **Impact:** Database state could become inconsistent if `delete_computer` fails after a rollback attempt.
- **Fix:** Ensure consistent error handling with proper rollback and clear exception propagation.

### Potential None Dereference in Form Handling [LOW]
- **Where:** `edit_computer_form` ~line 51
- **Issue:** `ComputerUpdate(**computer.__dict__)` assumes `computer` is not None, but `get_computer` may return None.
- **Impact:** Could cause AttributeError if `computer` is None, though this is guarded by HTTPException in calling function.
- **Fix:** Add explicit None check before unpacking `computer.__dict__`.

### Incorrect Template Response for Search [LOW]
- **Where:** `search_computers_route` ~line 81
- **Issue:** Template `partials/computer_row.html` expects `computer` but receives `computers` (plural), causing template rendering error.
- **Impact:** Search results will fail to render properly due to template context mismatch.
- **Fix:** Either change template to handle `computers` or adjust context to pass single `computer` object.

## Verdict

ISSUES FOUND
