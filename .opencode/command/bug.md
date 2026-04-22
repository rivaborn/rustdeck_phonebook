---
description: Load the pipeline's bug report for a phonebook source file and propose fixes
agent: review
---

Read `bug_reports/src/phonebook/$ARGUMENTS.md` and the current source at `src/phonebook/$ARGUMENTS`.

For each bug listed in the report, do the following in order:

1. Use serena's `find_symbol` to locate the cited function/method in the current code.
2. Decide if the bug is **still present**. The report is a pre-fix snapshot; some bugs may have been resolved by the debug pipeline's Step 5 or by hand.
3. If still present: propose a minimal fix citing `file:line`. No tangential cleanups.
4. If already fixed: say so and skip — don't re-fix.
5. Group by severity from the report (HIGH first, then MEDIUM, then INFO).

Do not edit files yet. Output proposals only; the user will pick which to apply.

If `bug_reports/src/phonebook/$ARGUMENTS.md` doesn't exist, say so and stop. Don't search blindly.
