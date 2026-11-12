I added and updated tests for #1799 in four test files, with no production code changed and nothing committed. On HEAD the full suite passes (1903 passed, 292 skipped). Run against the base commit, 30 of the new and edited cases fail, each showing the bug itself rather than a setup error.

**Message for the PR author**

Thanks for #1799. I added the tests the change needs. Running the new cases against the old code showed it changes more than the PR description says, so I've listed what else moved below.

**Existing tests updated.** These five asserted the old double reporting, where each `exact` header mismatch was also reported as a cell error on every row. Each now expects only the header error:
- `test_resource_validate_schema_extra_headers_and_cells`, renamed `test_resource_validate_schema_extra_label` because there are no extra cells any more.
- The `exact` rows of `test_resource_validate_fields_match_extra_label` and `test_resource_validate_fields_match_missing_field`.
- `test_package_validate_with_schema_issue_348`.
- `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: a missing *required* field now gets one `missing-label` and no per-row `constraint-error`. That matches what `superset` and `partial` already did. Please confirm this is what you want for #950.

**Tests added in `test_header.py` (`get_expected_fields`):**
- Under `exact`, an extra label now gets an `any`-typed field, replacing the old row "extra labels get no field". Schema fields beyond the labels are dropped.
- With no labels, every mode returns the schema fields. On the old code the name-matched modes returned `[]`, so a table read with `header=False` under `equal`, `subset`, `superset` or `partial` reported every row as `blank-row`. Your change fixes that by moving the `self.missing` check; the description doesn't mention it.

**Tests added in `test_validate_schema.py`:**
- **Irregular rows:** under an `exact` mismatch, a row as long as the header reports nothing, but a longer or shorter row still gets `extra-cell` or `missing-cell`. Those errors are now counted against the header, not the schema.
- **Repeated name:** an extra label that repeats a declared field's name causes no cell errors. This covers the suffix loop; without it, the two fields collide and rows break.
- **Primary key:** a key on a field absent from the data no longer gives a `primary-key` error on every row. A key on a field that is present is still checked.
- **Unique constraints and foreign keys,** one test each over all five `fieldsMatch` modes: a field absent from the data is skipped, and one that is present in the same table still reports. On the old code every name-matched mode crashed with `KeyError: 'Row does not have a field code'`. That is a second fix the description doesn't mention.

**Test added in `analyzer/__spec__/test_resource.py`:** detailed analysis under `exact` and `partial`, with a missing label and with an extra label. Field stats cover only declared fields that are present, and rows are no longer counted as having nulls because of an absent column. On the old code, `partial` crashed with `KeyError` for a missing field and with a schema error for an extra label. Under `exact` it reported stats for the absent column and counted every row as having nulls.

**Mutation check.** I applied eight hand mutants to the new lines, and the tests catch seven. The one that survives drops the `issubset(expected_field_names)` check from `has_primary_key`. It changes nothing observable: without it, `primary_key_cells` raises `KeyError`, the existing `except KeyError` branch absorbs it, and a missing key field always makes the header invalid. So it's an equivalent mutant and no test is owed. You could simplify by removing either the check or the `except` branch.

**Proposed, not done:**
- The PR description should mention the two extra fixes: no more `KeyError` with `unique` or foreign keys on absent fields under name-matched modes, and no more `blank-row` on headerless tables.
- There's no resource-level test for reading a headerless table under a name-matched mode; only the `Header` unit rows cover it. Add one if you want the `blank-row` symptom guarded end to end.
- Under `exact`, `duplicate-label` is detected only among the first `len(fields)` labels, so duplicates in the extra labels are never reported. That predates this PR and I left it alone.
