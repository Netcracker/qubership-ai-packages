I added the tests the change owed and updated six existing tests that the commit had left failing. The full suite passes on HEAD: 1920 passed, 292 skipped. Nothing is committed and no production code was changed.

The commit was not just missing tests: six existing tests failed on it, while the commit before it passes the whole suite. Each of those six asserted the duplicate per-row errors this PR sets out to remove, so I updated their expected results.

Running the new tests against the commit before this one also showed that the change fixes three things its description doesn't mention: two crashes and a whole table reported as blank rows. I've put those in the message below.

Here is the message for the PR author:

---

**Tests for #1799**

#1799 left six existing tests failing on its own commit. Each one asserted the duplicate per-row cell errors this PR removes, so I updated what they expect and named the change below. I then added tests for every behaviour the change moves. I ran them against the parent commit (44661ad): every new case fails there, except the controls, which pass on both commits as they should. The failures show the bug itself, not a missing name.

**Updated tests (the expected result moved because the old behaviour was the bug):**
- `test_header.py::test_get_expected_fields[exact: extra labels get no field]`: with `exact`, an extra label now gets an `any`-typed field. Renamed to `…get a default any-typed field`, expecting `["a", "extra"]`.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`: now only `extra-label`, with no `extra-cell` per row. Renamed to `…_extra_header_is_not_reported_again_per_row`, because the old name described errors that are no longer reported.
- `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: now only `missing-label`. The per-row `constraint-error` and `missing-cell` are gone.
- `test_validate_schema.py::test_resource_validate_fields_match_extra_label[exact]` and `…_missing_field[exact]`: `exact` now gives the same result as `equal`.
- `package/test_validate.py::test_package_validate_with_schema_issue_348`: now only `missing-label`.

**Added tests:**
- **Header (small tests on `Header.get_expected_fields`):**
  - `exact` drops fields beyond the labels.
  - The existing "extra field is `any`-typed" check now also covers `exact`.
  - With no header, every mode returns the schema fields.
  - With `exact`, extra labels get distinct names: the label repeats a field name, or a later label is already the suffixed name. Only distinctness is asserted, not the `a2` naming scheme.
- **Validation of rows that don't match the header (end to end):** with `exact` and a header that doesn't match the schema, only rows that don't match the header length report cell errors. Each test holds a row that matches the header length (no errors) next to a longer and a shorter row (errors), for an extra label and for a missing label.
- **Integrity checks on fields absent from the header:**
  - A primary key that is missing, or partly missing in a composite key, is not checked (`exact`, `superset`).
  - A `unique` field that is missing is not checked (all five modes). On the parent commit, the name-matched modes raised `KeyError`.
  - A foreign key whose field is missing is not checked (all five modes). On the parent commit, the name-matched modes raised `KeyError`. The same package still reports a foreign key on a field that is present, which serves as the control in the same validation run.
  - Controls: `unique` and the primary key are still checked when the field is in the header.
- **Reading without a header:** with `header=False` and any name-matched mode, rows are read by position. On the parent commit, every row came back as a `blank-row`.
- **Analyzer:** detailed analysis skips schema fields that are absent from the header, in every mode. On the parent commit, `exact` counted every row as having null values and the other modes raised `KeyError`. It also skips extra labels; on the parent commit, the name-matched modes raised a `schema-error`.

**Proposed, not done:**
- The PR description should mention the fixes above that it doesn't describe: reading by position with no header in name-matched modes, and the `KeyError` crashes for `unique`, foreign keys and the analyzer.
- Please confirm that skipping the primary-key check when a composite key is only partly present is intended. The parent commit still reported duplicates on the columns that were present. My test currently records the new behaviour.
- With `exact`, an extra label that is blank gets a field named `""`. I didn't test that because nothing says what it should be.
- The repository has no `AGENTS.md`. A one-line stack note could be added: `Tests: pytest (engine and assertions); no doubles or property-based library.`

---

Files changed:
- `frictionless/table/__spec__/test_header.py`
- `frictionless/resource/__spec__/test_validate_schema.py`
- `frictionless/package/__spec__/test_validate.py`
- `frictionless/analyzer/__spec__/test_resource.py`

To run tests against the parent commit I created a temporary git worktree, and I've removed it.
