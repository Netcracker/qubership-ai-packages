I added and updated tests for #1799 and didn't commit. The change came with no tests, and it also broke five existing ones. The whole suite on head now fails only where the base also fails: 47 tests and 9 collection errors, all from optional extras not installed here (wkt, html, ods, duckdb). Everything else passes, and ruff is clean.

I couldn't load the `english-developer-style` and `pythondoc-authoring` skills that the test-authoring skill points to, because they aren't installed. I wrote names and comments to match the neighboring tests.

---

**Message for the PR author**

All new tests are small: in-memory data, no network, in the same files as the existing tests for each unit. I checked them two ways:
- **Base commit:** with this PR's production code reverted, 37 of the new and updated tests fail, each on the bug itself: cell errors repeated on every row, a `KeyError` crash, or `blank-row` on every row.
- **Deliberate bugs:** I made seven small edits to the new code (mutation testing) by hand, one per new guard. Each edit makes at least one test fail.

**Existing tests whose expected results changed** (each listed the per-row cell errors that this PR stops reporting):
- `test_header.py::test_get_expected_fields[exact: extra labels get no field]`: an extra label now gets an `any` field. The case is renamed and joins the other modes' rows of the same rule.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`: now only `extra-label`. Renamed to `..._extra_label_is_reported_once`.
- `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: now only `missing-label`. The per-row `constraint-error` for the required field goes away too.
- `test_validate_schema.py::test_resource_validate_fields_match_extra_label[exact]` and `..._missing_field[exact]`: the `extra-cell` and `missing-cell` entries are gone.
- `package/test_validate.py::test_package_validate_with_schema_issue_348`: now only `missing-label`.

**Tests added**
- **`test_header.py::test_get_expected_fields`:**
  - Under `exact`, fields beyond the labels are dropped.
  - An extra label named like an existing field gets a numbered name (`a2`), and a number already taken is skipped (`a3`).
  - Without a header, every mode expects the schema fields. On the base, the four name-matching modes expected none.
  - `test_get_expected_fields_default_field_is_any_typed` now also covers `exact`.
- **`test_validate_schema.py`, "Fields match" section:**
  - `..._exact_reports_cells_against_the_header`: rows that are longer or shorter than the header still get `extra-cell` or `missing-cell`, for both an extra label and a missing label. Each case also has a row of the right length, which must report nothing.
  - `..._without_header_reads_cells_by_position`: with no header in a name-matching mode, the base marked every row `blank-row`. Now only the short row reports `missing-cell`.
  - `..._unique_is_checked_on_present_fields_only` and `..._foreign_key_is_checked_on_present_fields_only`, for all five modes. On the base, `superset` and `partial` crashed with `KeyError: Row does not have a field …` when a unique or foreign-key field was absent. In each test, a present field that breaks its constraint must still report.
  - `..._exact_checks_a_primary_key_only_when_present`: on the base, the primary key was checked when a key field was absent, and with a composite key that meant a false `primary-key` error on the part that was present.
    - The case with `header_case=False` is the only test that catches removing the `issubset` check in `has_primary_key`. Without it, that mutation went unnoticed, because with case-sensitive headers the old `except KeyError` path skips the check anyway.
    - The "key field is present" case also fails on the base. That's only because of the missing-cell errors this PR removes; its `primary-key` expectation already held.
  - The helper `_validate_fields_match` gained a `header=True` option. Its existing callers are unchanged.
- **`analyzer/test_resource.py`:**
  - A declared field missing from the data no longer gets `fieldStats` or counts in `variableTypes`, and no longer makes every row count as having null values. A real null in a present column still counts.
  - An undeclared column is left out of the stats. This passes on the base too. It fails if the row loop goes back to iterating the row's keys.

**Proposed, not done**
- **`read_rows()` changed shape, and nothing pins it.** Under `exact`:
  - An extra column now appears in each row: `{'a': 1, 'b': 2}`, where the base gave `{'a': 1}`.
  - A declared field missing from the data no longer appears, so `row["b"]` now raises where it used to return `None`.

  This is visible to users and isn't in the PR description or CHANGELOG. If it's intended, say so and I'll add a test for it.
- **Blank extra labels get odd names.** `["a", "", ""]` against schema `[a]` produces fields named `""` and `"2"`. I didn't pin this; is it intended?
- **Probably dead code.** With the `issubset` guard in place, the `except KeyError: assert not self.header.valid` in `TableResource.__open_row_stream` looks unreachable and could be removed.
- **Test stack line.** The repository has no `AGENTS.md` or `CLAUDE.md`. I'd propose one with the line `Tests: pytest engine and assertions (plain assert); pytest-mock for doubles.` I haven't created the file, because nobody has agreed to it yet.
