---
description: Look up a symbol's declared interface (signature + contract) from the pipeline
---

Search the pipeline's interface catalog for `$ARGUMENTS`:

1. First read `architecture/INTERFACES.md` — the consolidated catalog.
2. If the symbol has its own per-module file, read `architecture/interfaces/src/phonebook/<owning-module>.iface.md` for the full contract.

Report:
- Signature (parameters, types, return).
- Preconditions / postconditions / invariants if documented.
- Declared callers per the pipeline.

Then cross-check against the live code with serena's `find_symbol` and `find_referencing_symbols`. If the pipeline doc and serena disagree (file moved, signature drifted, callers added/removed), call out the divergence explicitly — the doc is older than the code.

If `$ARGUMENTS` is not found in either file, say so. Don't fabricate a signature from naming.
