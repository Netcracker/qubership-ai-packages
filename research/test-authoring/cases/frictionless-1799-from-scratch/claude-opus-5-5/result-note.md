I added and updated tests for #1799 and committed nothing. The full suite passes on HEAD (1902 passed, 292 skipped); with the old production code restored, 24 of the new or updated cases fail and the controls still pass. `ruff check` and `ruff format --check` are clean on the four files I touched. The new tests are small: each one makes a single in-process call to `validate()`, `read_rows()`, `analyze()` or `Header.get_expected_fields()`.

The old code did more than double-report. Under `equal`, `subset`, `superset` and `partial`, a field with `unique` or a foreign key that is missing from the header made `validate()` crash with `KeyError: 'Row does not have a field key'`. The commit message doesn't mention this crash. The tests below now cover it.

---

**Message for the PR author**

**Existing tests whose expectations moved (5).** Each one expected a header mismatch to also produce a cell error on every row, which is exactly what this PR removes. They now expect only the header error:
- `test_resource_validate_schema_extra_headers_and_cells`: no more `extra-cell` on rows 2–3.
- `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: no more per-row `missing-cell`. Also no more per-row `constraint-error` for a required field the header doesn't have.
- `test_resource_validate_fields_match_extra_label[exact]` and `test_resource_validate_fields_match_missing_field[exact]`.
- `test_package_validate_with_schema_issue_348`.

**`frictionless/table/__spec__/test_header.py`**
- In `test_get_expected_fields`, the case `exact: extra labels get no field` described the old behaviour. It is now `exact: extra labels get a default any-typed field`. I also added two cases:
  - `exact: fields beyond the labels are dropped`.
  - `exact: without a header, every field is expected`. This passes on the old code too and guards the new `self.missing` branch.
- `test_get_expected_fields_default_field_is_any_typed` now runs for `exact` as well.
- New `test_get_expected_fields_exact_names_each_extra_label_apart`, with three cases: an extra label that repeats a field name, one that repeats another extra label, and one whose first suffixed name is already a field's name. I assert the exact names because they show up as keys in the rows users read.

**`frictionless/resource/__spec__/test_validate_schema.py`** (each test pairs a case with a control that still reports something):
- `..._header_mismatch_reports_cell_errors_only_for_irregular_rows`, for a missing label and for an extra label. Regular rows report nothing, while rows shorter or longer than the header still get `missing-cell` / `extra-cell`.
- `test_resource_extra_label_repeating_a_field_name_is_read_as_its_own_cell`: `[{"a": 1, "a2": "x"}]`. The old code dropped the cell.
- `..._primary_key_is_checked_only_when_its_fields_are_in_the_header`. It covers a single key and a composite key, both with `header_case` on and off, plus a control where the key is present. The case-insensitive cases matter: with case-sensitive matching, the `KeyError` fallback hides the new `has_primary_key` guard. Without these two cases, replacing the guard with `self.schema.primary_key`, or `issubset` with `intersection`, left every test green.
- `..._fields_match_unique_is_checked_only_on_fields_in_the_header`, across all five `fieldsMatch` values. It covers the crash above, and a duplicate in the field that is present still raises `unique-error`.
- `..._foreign_key_is_checked_only_when_its_fields_are_in_the_header`, for `exact` and `partial`, each with a control where the key is present and points to nothing.

**`frictionless/analyzer/__spec__/test_resource.py`**
- New `test_analyze_resource_detailed_covers_only_fields_in_the_header`. When the header lacks a declared field, that field gets no `fieldStats` or `variableTypes` entry and no longer marks every row as null. The extra-label case is a control and passes on the old code too.

**Mutation check (done by hand, scoped to the diff).** Every guard I mutated is caught except one. Initialising `is_integrity` from `self.schema.primary_key` instead of `has_primary_key` changes nothing anyone can observe, because `is_integrity` only gates the unique and foreign-key checks. Those checks also need `memory_unique` or `foreign_groups` to be non-empty.

**Proposals I did not act on:**
- The repository has no `AGENTS.md` or `CLAUDE.md`. I'd propose adding this line to a new `AGENTS.md`: `Tests: pytest engine and assertions; no doubles or property-based libraries.` I didn't create the file. Should I?
- The composite-key case behaves differently from before. If any field of a composite key is missing, the whole primary-key check is now skipped. The old code compared the partial key with `None` filled in for the missing part. The tests pin the new behaviour, so if that wasn't intended, say so before merging.
- The fix for the `KeyError` crash under name-matched modes deserves a line in the changelog.
