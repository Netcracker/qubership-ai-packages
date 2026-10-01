I added and updated tests for the header-mismatch change; nothing is committed and no production code was touched. The full suite passes on HEAD (1898 passed, 292 skipped), and `ruff check` and `ruff format --check` are clean on the four changed files.

**Message for the PR author:**

---

This PR changed behavior that six existing tests encoded, and they failed on HEAD. I updated them and added tests for the parts that had none. All tests are small (in-process pytest) and sit next to the existing tests for the same code.

**Existing tests I updated** (the expectation changed because the behavior did):
- `test_package_validate_with_schema_issue_348`, `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`, and the `exact` rows of `test_resource_validate_fields_match_extra_label` and `test_resource_validate_fields_match_missing_field`. These now expect only the `missing-label` or `extra-label` error. The per-row `missing-cell` / `extra-cell` errors are gone, and so are the `constraint-error` rows in #950.
- `test_resource_validate_schema_extra_headers_and_cells` is renamed to `test_resource_validate_schema_extra_label_is_not_reported_again_per_row`, because the old name described the behavior this PR removes.
- In `test_get_expected_fields`, the row `exact: extra labels get no field` described the old behavior. `exact` now joins the generated "extra labels get a default any-typed field" and "fields absent from labels are dropped" rows. `test_get_expected_fields_default_field_is_any_typed` now also runs for `exact`.

**New tests:**
- **Header (`test_header.py`):**
  - Three `exact` rows for the suffix naming: an extra label that matches a schema field name, a repeated extra label, and a suffix that is already taken (`a3`).
  - For every mode, a "without a header, schema fields are returned as-is" row. On the base commit, the name-matched modes returned `[]` here, and validation reported a `blank-row` for every row of a headerless resource.
- **Row length under `exact`:** `test_resource_validate_fields_match_exact_checks_row_length_against_the_header`, for both an extra and a missing label. A row that matches the header stays silent, a short row reports `missing-cell`, and a long row reports `extra-cell` past the header.
- **Integrity checks on fields that are not in the data**, each next to a control where the field is present and the error still fires:
  - Primary key: a single-field key and a composite key with one part missing, under `exact`. The base commit reported `primary-key` on rows whose key cells were all None.
  - `unique` and foreign keys, under `superset`. The base commit raised `KeyError` here.
- **Analyzer:** `test_analyze_resource_detailed_ignores_fields_absent_from_the_data`, run under `exact` and `superset`. The base commit counted the absent field in `variableTypes`, `fieldStats` and `rowsWithNullValues` under `exact`, and raised `KeyError: 'absent'` under `superset`.

**Red on the base commit:** I ran these test files against the parent commit's production code. Every new or updated case failed with the bug itself (duplicate cell errors, `KeyError`, wrong counts), and every control passed.

**For you to confirm:**
- The PR fixes more than #1791 and its description says. The crashes in name-matched modes and the headerless `blank-row` errors described above are also fixed, so the PR description and CHANGELOG should mention them.
- Under `exact` with an extra label, a short row now reports `missing-cell` for the label's `any`-typed field, which it never did before. The tests treat this as intended, matching your "irregular rows still report cell errors". Please confirm it is.

**Proposed, not done:**
- The `except KeyError: assert not self.header.valid` branch in `TableResource.__open_row_stream` appears unreachable now that the primary key is only checked when all its fields are present. You might remove it; I didn't touch production code.
- The repository has no `AGENTS.md` or `CLAUDE.md`. I propose adding this line to a new `AGENTS.md`: `Tests: pytest engine and assertions; validation tests compare report.flatten([...]) as one list.` I haven't created the file; please say whether you want it added.
