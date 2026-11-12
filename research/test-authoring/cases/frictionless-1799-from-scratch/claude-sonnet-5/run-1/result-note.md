---

**Message for the author of #1799:**

This change left five existing tests red and the new `get_expected_fields()` logic uncovered. No production code changed; I only touched test files.

**Fixed existing tests that encoded the old (now-wrong) behavior** — each updated to drop the duplicate `extra-cell`/`missing-cell`/`constraint-error` it used to assert:
- `frictionless/table/__spec__/test_header.py::test_get_expected_fields[exact: extra labels get no field]` — under `exact`, an extra label now *does* get a default any-typed field (needed so the handler count matches the header and rows don't re-report it); renamed and fixed.
- `frictionless/resource/__spec__/test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`
- `frictionless/resource/__spec__/test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950` — this one also lost its `constraint-error`: a required field absent from the header now gets no per-row handler at all under `exact`, so the "required" check never runs for it either, not just the cell-count check.
- `frictionless/resource/__spec__/test_validate_schema.py::test_resource_validate_fields_match_extra_label[exact]` and `test_resource_validate_fields_match_missing_field[exact]` — this parametrized suite is explicitly the "end-to-end counterpart of the Header unit tests" and was carrying the exact scenario your fix targets.
- `frictionless/package/__spec__/test_validate.py::test_package_validate_with_schema_issue_348`

**New tests for what the change added:**
- `test_header.py`: `exact` with fewer labels than fields (field-truncation partition had no test), the new de-duplication suffix for two extra labels that read the same text (`"x"`, `"x"` → `"x"`, `"x2"`), and extended `test_get_expected_fields_default_field_is_any_typed` to cover `exact` too.
- `test_header.py`: a missing header (no header row at all) now falls back to the schema fields under every non-`exact` `fieldsMatch` mode. On the base commit this returned `[]`, which meant **every row silently came back as `blank-row`, discarding all data** — a severe, previously-untested regression. Added `test_resource_name_matched_fields_match_without_a_header_reads_rows_by_schema_order` in `test_general.py` to pin the end-to-end fix.
- `test_general.py`: two regression tests for the PR's headline bug (`id`/`extra-label`/`extra-cell` and `id`/`missing-label`/`missing-cell`), each asserting a normal row gets no duplicate error while a genuinely irregular row still does.
- `test_general.py` / `test_validate.py` (package) / `analyzer/__spec__/test_resource.py`: narrowing `get_expected_fields()` also makes handlers *disappear* for dropped fields, which exposed three `KeyError` crash risks your diff happens to guard against but never tests: a `uniqueField` constraint on a field missing from a `superset` header (**verified this actually crashes on the base commit**), a foreign key whose target field is missing from an `exact`-mode header (verified it crashes if the new `continue` guard in `table.py` is removed), and `resource.analyze(detailed=True)` over a schema field absent from a `superset` header (**also verified crashing on base**). Added one test each.

All new/changed tests pass on HEAD; I confirmed each one is red on the base commit (or fails if the relevant guard line is removed) before finalizing it. Ran the full suite minus optional-dependency extras not installed here (`ods`, `pandas`, `wkt`, sql backends) — no other breakage.

**Proposed, not done:** worth a line in the PR description calling out the headless-header and the two KeyError fixes explicitly — they're real behavior changes bundled into this diff that reviewers would otherwise have to find by tracing `table.py`/`analyzer.py` by hand.
