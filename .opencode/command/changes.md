---
description: Show recent debug-pipeline auto-fixes from .debug_changes.md
---

Read `.debug_changes.md` at the repo root.

If the file doesn't exist, say "no debug-fix log present — debug pipeline Step 5 either hasn't run or made no changes" and stop. Don't go hunting for an alternative.

If it exists, summarize the 10 most recent entries. For each:

1. Which file was changed.
2. What bug the report identified.
3. What change was applied.
4. Whether the change still looks sensible given the *current* state of the file (use Read to check, use serena if a symbol's location matters).

Flag any entries that look like over-corrections, defensive-code additions that violate the project's "no defensive try/except" rule, or "improvements" that touched things outside the bug's scope.
