All green. Here's the message for the PR author:

---

I added the tests this change owes, without touching production code. No commit was made.

**Updated existing tests that encoded the old (buggy) behavior** — these failed as soon as I ran the suite against the new code, which confirms they were asserting the double-reporting the fix removes:
- `test_resource_validate_schema_extra_headers_and_cells`, `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`, `test_resource_validate_fields_match_extra_label[exact]`, `test_resource_validate_fields_match_missing_field[exact]` (`frictionless/resource/__spec__/test_validate_schema.py`)
- `test_package_validate_with_schema_issue_348` (`frictionless/package/__spec__/test_validate.py`)
- the `"exact: extra labels get no field"` case of `test_get_expected_fields` (`frictionless/table/__spec__/test_header.py`)

Each now asserts the single header-level error with no trailing per-row `missing-cell`/`extra-cell`/`constraint-error`, which is exactly the behavior the commit intends.

**Added new tests** for partitions the diff touches that had no coverage at all:
- `Header.get_expected_fields()` under `exact`, unit-level: header shorter than the schema (fields now truncated, not just returned unchanged), and an extra label whose text collides with an already-kept field name (the new disambiguation loop that renames it to avoid a handler collision).
- `TableResource`-level regression tests for two crashes that the `table.py` hunk prevents, now that `header.py` can drop or synthesize fields: a `unique`-constrained field dropped by a short header, and a foreign key whose target field is dropped by a short header (both would raise `KeyError` without the `table.py` guards — I verified this by reverting just those hunks against a scratch copy).
- An `analyzer.py` regression test: an extra label under `exact` mode synthesizes a field that isn't in `resource.schema.fields`; without the accompanying analyzer fix, `analyze()` raises (also verified by reverting just that hunk).

For every new/changed test I confirmed it's red against the pre-fix code (the parent commit, or — for the two companion fixes that only matter once `header.py`'s truncation exists — against this commit with just that one hunk reverted) and green against the current code.

**What I didn't do:** I left the `is_integrity`/`has_primary_key` seed change and the `for field in expected_fields` → unique-loop ordering alone where I could show no observable behavior differs from before (the existing `try/except KeyError` around primary-key lookup already made that specific bit a no-op change); no test is owed there since it can't fail. I also didn't add a redundant analyzer test for the missing-field direction (schema field absent from a short header) since old and new analyzer code already produce identical output there.
