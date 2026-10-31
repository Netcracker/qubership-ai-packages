I added tests across four test files and updated the six existing tests the change broke. Nothing is committed, and production code is unchanged.

**Verification**
- On this commit, the four touched packages (`analyzer`, `resource`, `table`, `package`) pass: 472 passed.
- On the parent commit, every new or edited test fails, and each failure shows the bug itself: duplicate cell errors, unwanted key errors, or a `KeyError`.
- The full suite also has 17 `test_string_read_cell_wkt` failures. They fail the same way on the parent commit, so they come from the local environment, not this change.

---

**Message for the PR author**

**Existing tests updated.** Each change removes the per-row errors that a header mismatch used to add:
- `test_resource_validate_schema_extra_headers_and_cells` and `test_resource_validate_fields_match_extra_label[exact]`: no more `extra-cell` per row.
- `test_resource_validate_fields_match_missing_field[exact]` and `test_package_validate_with_schema_issue_348`: no more `missing-cell` per row.
- `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: the per-row `constraint-error` for the missing required field is also gone, along with the `missing-cell`. The PR description only mentions cell errors, so please confirm dropping the `constraint-error` is intended.
- `test_get_expected_fields`: the row "exact: extra labels get no field" now expects an `any`-typed field for the extra label.

**New tests in `table/__spec__/test_header.py`** (unit tests of `get_expected_fields`):
- `exact`: fields beyond the labels are dropped.
- `exact`: repeated extra labels each get their own field (`["a", "a", "a"]` → `a, a2, a3`). A version that renamed only once would give two fields the same name, and that case catches it.
- Equal, subset, superset and partial without a header row: the schema fields are returned as-is. Before this change they got an empty list, and every row was reported as `blank-row`. That fix is not mentioned in the PR description.
- `test_get_expected_fields_default_field_is_any_typed` now also covers `exact`.

**New tests in `resource/__spec__/test_validate_schema.py`** (end to end):
- Four tests show that, under `exact`, rows are now checked against the header:
  - A row that matches the header reports nothing. Next to it, a longer or shorter row still reports its cells.
  - A short row reports `missing-cell` under an extra label.
  - A long row reports `extra-cell` under a missing label.
- Unique, primary-key and foreign-key checks on a field the header lacks now produce only the `missing-label` error. In each test, a key on a field the header does carry still reports.
  - Under `superset`, the unique and foreign-key cases used to raise `KeyError: Row does not have a field …`.

**New test in `analyzer/__spec__/test_resource.py`:** a schema field missing from the data no longer appears in `fieldStats` or counts as null in every row. A real empty cell still counts. Under `partial`, this used to raise `KeyError`.

**Proposed, not done:**
- Under `exact`, a cell that sits in the position of a schema field whose label is missing is now reported as an `extra-cell`, not read as that field. The test pins this because it follows from "expected fields follow the header length". Please confirm it is what you want.
- The `a2`/`a3` names given to repeated extra labels are a decision, not a spec. If you consider them internal, the header test could assert only that the names are distinct.
