No production code touched, nothing committed, full suite (1881 tests) green.

---

**Message for the author of #1799:**

Your fix changes `Header.get_expected_fields()` so that under `exact` fieldsMatch the expected fields follow the header's length rather than the full schema — which is exactly right, but it also **silently broke 6 existing tests** that still encoded the old double-reporting behavior, and it leaves a **new crash** in `Analyzer` unexercised. I fixed the stale tests and added the regression test that was actually owed:

- **Updated 6 tests whose expectation moved** (confirmed red on `5cca11c~1`, green on `5cca11c`), each now asserting only the header-level error with no repeated per-row cell error:
  - `test_header.py::test_get_expected_fields` — the `"exact: extra labels get no field"` case was asserting the *old* behavior (`["a"]`); it now expects `["a", "extra"]`, renamed to say so. I also added the mirror case for the "fewer labels than fields" side (`"exact: fields beyond the labels are dropped too"`), since that partition of the same change had no unit-level case at all, and widened `test_get_expected_fields_default_field_is_any_typed` to cover `exact` too.
  - `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells` → renamed to `..._is_reported_once`, dropped the two `extra-cell` rows it asserted.
  - `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950` → dropped the `constraint-error`/`missing-cell` rows (the field is gone from every row now, not just under-filled).
  - `test_validate_schema.py::test_resource_validate_fields_match_extra_label` and `..._missing_field` (`exact` cases) → dropped their trailing cell-error rows.
  - `package/__spec__/test_validate.py::test_package_validate_with_schema_issue_348` → dropped its two `missing-cell` rows.

- **Added two new regression tests**, both confirmed red on `5cca11c~1` and green on `5cca11c`:
  - `test_validate_schema.py::test_resource_validate_primary_key_missing_from_the_header_issue_1791` — a primary-key field absent from the header under `exact` used to additionally report a `missing-cell` *and* a spurious `primary-key` error on every row; this path wasn't touched by any of the 6 tests above (none of them declared a `primaryKey`), so it was completely unguarded.
  - `analyzer/__spec__/test_resource.py::test_analyze_resource_detailed_skips_a_field_missing_from_the_header_issue_1791` — this one isn't a double-report, it's a **`KeyError` crash**: `Analyzer.analyze_table_resource(detailed=True)` still iterates `resource.schema.fields` (the *full* schema) when building correlations/field stats, but `columns_data` is now only populated for the header's expected fields. I verified this throws `KeyError: 'bad'` when `analyzer.py`'s own part of your diff is reverted while `header.py`/`table.py` keep the fix — so your `analysis_fields` filter in `analyzer.py` is independently load-bearing and was previously untested.

What I didn't do, and propose instead of doing myself: the repository has no `AGENTS.md`/`CLAUDE.md` stack line for its test stack (pytest, plain `assert`). Per the test-authoring skill, I'm flagging this as a one-line proposal rather than creating the file: `Tests: pytest engine, pytest/plain-assert assertions.` Worth adding if you want future sessions to skip re-deriving it.
