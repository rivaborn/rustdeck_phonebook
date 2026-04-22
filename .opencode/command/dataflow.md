---
description: Trace a module's data flow per the pipeline's analysis, then cross-check against current code
model: ollama/qwen3:32b
---

Read `architecture/DATA_FLOW.md`. Locate the section(s) referencing `$ARGUMENTS` (a module name like `crud` or `routes/computers`, or a symbol like `Computer` or `create_computer`).

Summarize:
- Where data comes IN to `$ARGUMENTS` (inputs, callers).
- What `$ARGUMENTS` reads / writes / mutates.
- Where data flows OUT (return values, downstream consumers, side effects on DB).

Then use serena's `find_referencing_symbols` to verify the consumers are still there. Note any divergence between the doc and the live code — the doc is older.

If `$ARGUMENTS` doesn't appear in `DATA_FLOW.md`, say so and stop. Don't reconstruct it from intuition.
