# src/phonebook/schemas.py

## Findings

### Inconsistent validation logic between create and update models [MEDIUM]
- **Where:** `ComputerCreate.validate_friendly_name()` ~line 23, `ComputerUpdate.validate_friendly_name()` ~line 64
- **Issue:** `ComputerCreate` validates length after stripping whitespace, but `ComputerUpdate` does not strip whitespace before length validation.
- **Impact:** Update operations may accept strings with leading/trailing spaces that would be rejected during creation, causing inconsistent data handling.
- **Fix:** Apply `v.strip()` before length validation in `ComputerUpdate` validators to match `ComputerCreate` behavior.

### Missing validation for empty tag lists [LOW]
- **Where:** `ComputerCreate.validate_tags()` ~line 35, `ComputerUpdate.validate_tags()` ~line 76
- **Issue:** When all tags are filtered out (e.g., empty strings or whitespace-only), an empty string is returned instead of None.
- **Impact:** May cause unexpected behavior in downstream processing that expects None for empty tag fields.
- **Fix:** Return None when no valid tags remain after filtering instead of returning empty string.

### Potential None dereference in strip_whitespace validator [INFO]
- **Where:** `ComputerCreate.strip_whitespace()` ~line 42, `ComputerUpdate.strip_whitespace()` ~line 83
- **Issue:** The validator assumes `v` is either a string or None, but doesn't handle other types that might be passed.
- **Impact:** Could raise TypeError if non-string, non-None values are passed to the validator.
- **Fix:** Add explicit type checking or handle non-string types gracefully.

## Verdict

ISSUES FOUND
