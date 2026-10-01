I added the missing tests and fixed six existing ones that the commit left failing. Production code is unchanged and nothing is committed. The relevant test folders now pass (474 tests). In the full suite, 17 tests still fail, all `test_string_read_cell_wkt` cases. They fail the same way on the parent commit, so they come from this environment, not from the change.

---

**Message for the PR author**

This change left six tests failing, and it changes more than the commit message says. When the header doesn't match the schema under `exact`:

- **What it fixes:** per-row `missing-cell`, `extra-cell` and `constraint-error` errors are gone.
- **Primary keys:** per-row `primary-key` errors on a key whose column has no label are gone too.
- **Rows checked against the header:** a row with a cell under no label now gets `extra-cell`, and a row shorter than the header gets `missing-cell`.
- **Extra labels:** their cells are now read under the label's name, with a numeric suffix if the name is taken.
- **The analyzer** skips fields that have no label.
- **Not in the commit message:** with `header=False`, the name-matched modes (`equal`, `subset`, `superset`, `partial`) reported every row as `blank-row`. They now read cells by position.

All tests are small (one process, inline data or files from `data/`). Every new or changed test except the two noted below fails on the parent commit, and each failure shows the problem itself, not a crash.

**Existing tests I updated**, because the behaviour they checked has changed:
- `test_resource_validate_schema_extra_headers_and_cells`, renamed `…_extra_header_reports_no_extra_cells`: no per-row `extra-cell`.
- `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: a missing required field is now only `missing-label`; per-row `constraint-error` and `missing-cell` are gone.
- `test_resource_validate_fields_match_extra_label[exact]` and `…_missing_field[exact]`: no per-row cell error.
- `test_package_validate_with_schema_issue_348`: no per-row `missing-cell`.
- `test_get_expected_fields[exact: extra labels get no field]`: now expects a default `any`-typed field for each extra label, and is renamed to say so.

**New tests:**
- **`test_header.py::test_get_expected_fields`**, new cases for `exact`:
  - fields beyond the labels are dropped;
  - an extra label named like a field gets a numeric suffix;
  - the suffix skips names already taken;
  - with no header, every schema field is expected, in all five modes.
- **`test_validate_schema.py`:**
  - `test_resource_validate_exact_checks_row_length_against_the_header`: a header shorter and a header longer than the schema. Each table holds one matching row (no error) next to irregular rows that still report, so the silence can't come from the setup.
  - `…_primary_key_is_checked_only_when_its_label_is_present`: key on the missing field, plus a control with the key on a present field that still reports `primary-key`.
  - `…_unique_…` and `…_foreign_key_…`: in one validation, a constraint on the missing field stays silent while the same constraint on a present field still reports.
  - `…_fields_match_without_header_matches_fields_by_order`: all five modes, with a row of three cells as the control. I added an optional `dialect` argument to the existing `_validate_fields_match` helper rather than writing a second helper.
- **`analyzer/__spec__/test_resource.py`:**
  - `…_skips_a_field_whose_label_is_missing`: `fieldStats`, `rowsWithNullValues` and `notNullRows`; one truly empty row is the control.
  - `…_skips_a_column_the_schema_does_not_declare`: passes on the parent commit too. It guards the new path, because extra columns now appear in rows: going back to iterating the row's keys makes it fail.

**Mutation check, by hand, on the lines that changed:** removing the unique filter, the foreign-key filter, the suffix loop, the no-header branch, or either analyzer filter makes at least one of these tests fail. Removing the primary-key filter (`has_primary_key = bool(primary_key_fields)`) changes nothing anyone can observe. `primary_key_cells` raises `KeyError` for a field the row doesn't have, and the existing `except KeyError` branch swallows it. So no test can tell the two versions apart, and I didn't write one.

**Proposed, not done:**
- That `except KeyError` branch in `TableResource.__open_row_stream` can no longer run and could be removed in a follow-up.
- The repository has no `AGENTS.md` or `CLAUDE.md`. I suggest adding one with the line `Tests: pytest engine and assertions; report.flatten reports every error of a validation and names it by row and field number`. I'll only add it if you agree.
- The `print(...)` in the issue-950 test was already there. I left it alone.
