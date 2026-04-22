---
description: Load pipeline's test-gap report for a file and draft pytest tests to close the gaps
model: ollama/qwen3:32b
---

Read `test_gaps/src/phonebook/$ARGUMENTS.gap.md` and `src/phonebook/$ARGUMENTS`. Also read `tests/conftest.py` to learn the existing fixture style.

For each gap in the report:

1. Confirm the gap is real: use serena to verify the function/condition still exists in the current source (it may have been refactored since the report).
2. If real, draft a single focused pytest test that closes it. Use `db_session` for sync CRUD tests and `client` for async route tests — these are the existing conftest fixtures.
3. Name tests `test_<function>_<scenario>` consistent with the existing test files.
4. Group output by source function so I can apply tests in batches.

Do not write to disk. Output the test code as fenced blocks in the chat; I'll move them into the right `tests/test_*.py` file.

If `test_gaps/src/phonebook/$ARGUMENTS.gap.md` doesn't exist, say so and stop.
