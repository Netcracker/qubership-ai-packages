I added and updated tests for the header-mismatch change, without touching production code or committing. The full suite passes on HEAD (1898 passed, 292 skipped). Against the parent commit's production code, all 26 new or changed cases fail, each on the bug itself: duplicated cell or integrity errors, a `KeyError` crash, or a missing field. Below is the message for the author.

---

**Tests for #1799 (header mismatches no longer cause cell errors)**

**Existing tests updated because the behavior they asserted changed**
- `test_get_expected_fields[exact: extra labels get no field]` is now `…get a default any-typed field` and expects `["a", "extra"]`.
- Five validation tests no longer expect a `missing-cell` or `extra-cell` per row next to the `missing-label` or `extra-label`:
  - `test_package_validate_with_schema_issue_348`
  - `test_resource_validate_fields_match_extra_label[exact]`
  - `test_resource_validate_fields_match_missing_field[exact]`
  - `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`
  - `test_resource_validate_schema_extra_headers_and_cells`, renamed to `…_extra_header_without_cell_errors` because its old name stated the old outcome.
- In `issue_950`, the per-row `constraint-error` for a required field that is missing from the header also goes away. That matches what the name-matched modes already did, but it is worth a line in the changelog.

**New tests**
- **`Header.get_expected_fields`** (`test_header.py`, new rows in the existing table):
  - Under `exact`, fields beyond the labels are dropped.
  - An extra label that repeats a field name becomes `a2`, and the numbering skips names already taken (`a3`).
  - With no header, every mode returns the schema fields. Before, the name-matched modes returned `[]`, so every row of a headerless table was reported as `blank-row`.
  - `exact` is added to `test_get_expected_fields_default_field_is_any_typed`.
- **Rows whose length differs from the header** (`test_resource_validate_fields_match_exact_checks_row_length_against_the_header`): four cases backing the claim that irregular rows still report cell errors.
  - With an extra label, a row as long as the header has no error and a longer row has an `extra-cell`. A shorter row now reports a `missing-cell` named after the extra label (`name`).
  - With a missing label, a row as long as the header has no error and a shorter row has a `missing-cell`. A longer row now reports an `extra-cell` where the cell used to be read into the schema field.
  - The two "now" outcomes are new behavior; please confirm they are intended.
- **Integrity checks on a field missing from the header**, under `exact` and `equal`, for a primary key, a `unique` field and a foreign key:
  - Each test also has a field that is present and still reports (a `unique-error` or a `foreign-key` error), so the absence of other errors shows the missing field was skipped, not that the checks were off.
  - On the parent commit, `equal` crashed with `KeyError` for the `unique` field and the foreign key. With another field `unique`, it also reported a spurious `primary-key` error.
- **Analyzer** (`test_analyze_resource_detailed_leaves_out_fields_missing_from_header`, `exact` and `equal`):
  - `fieldStats`, `variableTypes` and the null-row counts now cover only the fields that are present.
  - On the parent commit, `exact` counted every row as having a null value and `equal` crashed with `KeyError: 'c'`.

**Proposed, not done**
- Under `exact`, `read_rows()` now also returns the cells of extra labels: `{'id': 1, 'name': 'x'}` where it used to return `{'id': 1}`. That is visible to users and matches the name-matched modes. I didn't add a test for it, so you can decide whether it's intended and whether it needs a changelog entry.
- Blank extra labels get field names `""` and then `"2"`. An empty field name probably deserves its own rule, such as `field3`; I left it untested.
