All green. As instructed, I did not commit anything — these changes remain in the working tree for review.

---

**Message for the PR author:**

This fix changed `Header.get_expected_fields()` under `fieldsMatch: "exact"` and the two call sites that consume it (`TableResource.__open_row_stream`, `Analyzer`), but no tests were touched, so the diff was carrying two kinds of untested risk. I ran the affected suites (`frictionless/table`, `resources/table`, `resource`, `package`, `analyzer`) before and after this commit to find them, then fixed what the change owes without touching production code:

**Stale tests updated (they encoded the old, now-wrong behavior and were red on this branch):**
- `test_header.py::test_get_expected_fields["exact: extra labels get no field"]` — exact mode now *does* synthesize an any-typed field for a trailing extra label, same as the name-matched modes; renamed the case and fixed the expectation.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells` — the extra column no longer produces an `extra-cell` per row.
- `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950` — the missing field no longer produces `constraint-error`/`missing-cell` per row, only the header-level `missing-label`.
- `test_validate_schema.py::test_resource_validate_fields_match_extra_label["exact"]` and `::test_resource_validate_fields_match_missing_field["exact"]` — same duplicate-row-error removal, parametrized case.
- `package/test_validate.py::test_package_validate_with_schema_issue_348` — same as above, package-level.

I confirmed each of these fails against the pre-fix commit (`6d5cd51^`) with the new expectation and passes against this commit, so they're real regression tests for the fix, not just updated literals.

**New tests added (behavior this commit introduces with no coverage at all):**
- `test_header.py`: two new `get_expected_fields` cases for a code path that's entirely new in this commit — exact mode's collision-avoiding renaming of synthesized fields (the `used_names`/`while` suffix loop). One case has an extra label collide with a *kept* schema field name (the realistic case — `data/capital-invalid.csv` has exactly this shape, with a duplicated `name` column, and it was incidentally exercising this code via an unrelated analyzer test without ever asserting on it). The other needs two renaming attempts (`dup`, `dup2`, `dup3`) to catch a `while`→`if` or missing-increment mutant that a single collision wouldn't. Also added the "any"-typed assertion for exact mode, mirroring the existing one for the name-matched modes.
- `test_validate_schema.py::test_resource_validate_schema_extra_header_data_is_still_read` — asserts that `read_rows()` now actually surfaces the extra column's data (`{"id": 1, "name": "english"}`), which used to be silently dropped from every row under `exact`. This is a real, user-visible behavior change nothing else checks.

I also deleted a stray `print(...)` debug line in `test_resource_validate_less_actual_fields_with_required_constraint_issue_950` since I was already rewriting its assertion.

**Proposed, not done:** this repository has no `AGENTS.md`/`CLAUDE.md` naming its test stack. Based on the existing tests, it's pytest with plain `assert`. Worth adding a line such as `Tests: pytest engine, pytest assertions` to a new or existing instructions file, but I didn't create one since there's no explicit go-ahead for that.

I didn't find any owed test for the `resources/table.py` primary-key/unique/foreign-key scoping changes (restricting those checks to `expected_fields`) — I checked several scenarios (a missing composite primary key, a missing unique field, a partially-missing composite foreign key) against both commits and the observable output was identical in both, so that part of the diff is a behavior-preserving refactor riding along with the fix, not something that needs new coverage.
