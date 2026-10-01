Everything checks out. Here's the message for the PR author:

---

**Tests for #1799**

The commit changed behavior in three places but shipped with no tests, and it left five existing tests asserting the *old* behavior — they were passing by accident only because nothing re-ran them. I added the regression line (found via `uv venv` + running the base commit against the new/updated tests) and updated the stale ones.

**Updated (encoded the old double-reporting behavior, now red on the base commit / green on yours):**
- `test_header.py::test_get_expected_fields` — the `"exact: extra labels get no field"` case asserted the pre-fix truncation; folded it into the existing `"{mode}: extra labels get a default any-typed field"` and `"...dropped"` parametrize groups, since `exact` now produces the same outcome as the name-matched modes for both cases (just via position, not name).
- `test_get_expected_fields_default_field_is_any_typed` — extended to cover `exact` too.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`, `test_resource_validate_fields_match_extra_label[exact]`, `test_resource_validate_fields_match_missing_field[exact]`, `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`, and `package/__spec__/test_validate.py::test_package_validate_with_schema_issue_348` — all asserted the duplicate `extra-cell`/`missing-cell`/`constraint-error` rows your fix removes. Updated expectations and added a one-line comment pointing at #1791.

**Added (new behavior with zero prior coverage):**
- `test_get_expected_fields_exact_synthetic_field_avoids_name_collision` — the `while name in used_names` suffixing loop in `get_expected_fields` had no test exercising it at all (every existing extra-label case used a non-colliding label).
- `test_resource_validate_schema_primary_key_field_missing_from_header_issue_1791` — `table.py`'s new `has_primary_key` guard. Before the fix, a primary-key field missing from the header produced a spurious `primary-key` error on *every row* (cells read as all-`None`), on top of the header's own `missing-label` — a third flavor of the same double-report bug, undetected by any existing test.
- `test_analyze_resource_schema_field_missing_from_header_issue_1791` — the analyzer change. Before the fix, a schema field beyond the header's length was still analyzed as an all-null "ghost" column, showing up in `variableTypes` and `fieldStats` with a half-built stats dict (`{"type": "numeric"}` only, no mean/median/etc.).

**Considered and not added:** the foreign-key `target_key`/`expected_field_names` skip in `table.py` (lines 307–309). I built a scenario (self-referencing FK whose target field is missing from the header) and compared base vs. fix: the report is identical either way, because the pre-existing `if set(cells) == {None}: continue` guard already suppressed any per-row FK error in that case. I couldn't find an input where this skip changes observable output — looks like an equivalent mutant (likely a performance/cleanliness change, not a behavior fix), so I left it untested rather than writing a test that can't fail.

All four touched files pass (`171 passed, 5 skipped`), and a full-suite diff against the base commit shows no new failures beyond the 11 I added/fixed (the remaining ~89 failures are pre-existing environment gaps — missing optional extras like `duckdb`, `shapely`, `xlrd`, etc. — unrelated to this change).
