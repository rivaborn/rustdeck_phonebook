# Prompt Updates

Generated: 2026-04-21 22:10:55

## Critique of the Original Prompt

### What Was Unclear

**Stack left to AI discretion.** The original prompt offered two equally-weighted stack options and asked the model to "pick the option you believe is best." This is ambiguous for a planning-stage prompt whose output feeds a code generator: if two different runs of Stage 2 choose different stacks, Stage 3 produces incompatible plans. The improved prompt mandates a single stack (FastAPI + Jinja2 + HTMX + SQLAlchemy + SQLite) with exact version floors.

**"Organize the code clearly" is not actionable.** Without a concrete directory layout, every AI run produces a different structure. The improved prompt mandates the Python src-layout (`src/phonebook/`) with every file named explicitly, which is both required by the user's constraint and necessary for Stage 3's module-pairing logic.

**"Basic tests if practical" is not a testing strategy.** The original treated testing as optional. The improved prompt defines three test files, their fixtures, and every individual test case with its assertion, so the code generator has no discretion to skip or abbreviate tests.

**Validation rules were behavioral but not computable.** "Prevent obviously invalid IP address formats" leaves the implementation undefined. The improved prompt specifies `ipaddress` stdlib validation and the exact column-level nullable rule so the Pydantic schema can be written unambiguously.

**"Nice-to-have features if easy" is an open invitation for scope drift.** Items like "dark mode via basic CSS variables" and "copy-to-clipboard" were vague suggestions. The improved prompt promotes them to concrete requirements — dark mode via CSS custom properties with a `@media (prefers-color-scheme: dark)` block, and `copyToClipboard()` as a named function in `app.js` — so they are either in or out with no ambiguity.

---

### What Was Contradictory

**"Keep dependencies minimal" vs. "Good options would be…HTMX."** HTMX is a dependency. The original never committed to it. The improved prompt treats HTMX as mandatory (CDN, no npm), which is consistent with the server-rendered philosophy and the "minimal JS" goal without contradiction.

**"Avoid Docker unless it meaningfully simplifies" alongside "Include instructions for running behind a reverse proxy."** Mentioning both without a decision forced the reader to wonder if Docker was expected. The improved prompt removes Docker entirely and specifies only the nginx snippet as a brief README section, resolving the ambiguity.

**"Date created / Date updated" as fields with no type or lifecycle rule.** The original listed them in the data model without specifying their format, who sets them, or whether they are updatable by the user. The improved prompt declares them `TEXT NOT NULL`, ISO-8601 UTC, with `default=` (insert) and `onupdate=` (every write) semantics, owned solely by the ORM.

---

### What Was Missing

**No package name.** Without a canonical package name (`phonebook`), every cross-module import path in the architecture plan becomes undefined. Added explicitly.

**No `pyproject.toml` specification.** The original said "install dependencies" but did not say how the project is packaged. The improved prompt specifies the `pyproject.toml` structure (build-system, project metadata, scripts entry point, ruff and pytest config blocks) so the project is installable with `pip install -e .`.

**No module responsibility boundaries.** The original had CRUD, routes, templates, and validation as bullet points under "then implement," with no indication of which file owns which symbol. Without this, Stage 2 routinely duplicates symbols across modules or leaves import paths inconsistent. The improved prompt has a dedicated Module Responsibilities section with exact public symbols and signatures per file.

**No HTMX interaction contract.** The original mentioned HTMX but never specified which routes return full pages vs. partials, which HTML element IDs are swap targets, or how HTMX headers are detected. The improved prompt specifies `HX-Request` header detection, names every target ID (`#computer-table-body`, `#modal`), and defines HTMX attributes per template.

**No `conftest.py` specification.** Without a fixture contract, test files generated in Stage 3 use incompatible assumptions about database setup and client injection. The improved prompt specifies `db_session` and `client` fixtures with scope and teardown behavior.

**No export endpoint specification.** The original listed "import/export to JSON or CSV" as a nice-to-have with no route, handler, or response-type detail. The improved prompt promotes this to a required feature with a dedicated router module, two named endpoints, handler names, content types, and test cases.

**"Open Questions" deliverable not present but guarded against.** The original deliverables list did not include an "Open Questions" item by name, but the absence of a "Design Decisions" requirement created an implicit opening for Stage 2 to defer unresolved items. The improved prompt adds an explicit Design Decisions deliverable with the rule that entries must be decisions with rationale — closing that loophole in advance.

---

### Changes Made and Why

| Change | Reason |
|---|---|
| Added mandatory Python src-layout with full file tree | Required by user constraint; prevents layout drift across runs |
| Pinned single tech stack with version floors | Eliminates stack-choice ambiguity for downstream generators |
| Added Module Responsibilities section with exact signatures | Enforces single source of truth; required by Hard Constraint 1 |
| Specified every API endpoint with handler function name | Required by Hard Constraint 4 (import-path canonicalization) |
| Expanded testing from "if practical" to full test plan | Ensures Stage 3 can generate complete, paired test files |
| Moved copy-to-clipboard and dark mode from nice-to-have to required | Removes discretion; these are simple enough to specify fully |
| Specified `ipaddress` stdlib for IP validation | Eliminates regex ambiguity; more correct than hand-rolled patterns |
| Added `pyproject.toml` and `seed/seed_data.py` specifications | Required for a fully installable, self-contained project |
| Added Design Decisions deliverable; prohibited Open Questions | Closes the main drift loophole in Stage 2 architecture generators |
| Renamed `confirmDelete` JS function note to "may be omitted" | `hx-confirm` covers this natively; recording it as a Design Decision prevents redundant JS |