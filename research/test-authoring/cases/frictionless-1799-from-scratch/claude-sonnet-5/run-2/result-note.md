Only test files changed, nothing committed, as required. Here's the message for the PR author:

---

**Tests for #1799**

Your fix changed `get_expected_fields()`'s behavior under `fieldsMatch: "exact"` (it now truncates/extends to match header length), and that moved six existing assertions that encoded the old, buggy behavior — they all failed red on your commit's parent before I touched them, and pass on your commit:

- `test_header.py::test_get_expected_fields[exact: extra labels get no field]` — folded into the shared `extra labels get a default any-typed field` / `fields absent from labels are dropped` parametrizations, since exact now matches the other modes on both. Added `ALL_FIELDS_MATCH` for that.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`, `::test_resource_validate_less_actual_fields_with_required_constraint_issue_950`, `::test_resource_validate_fields_match_extra_label[exact]`, `::test_resource_validate_fields_match_missing_field[exact]`, and `test_validate.py::test_package_validate_with_schema_issue_348` — dropped the `extra-cell`/`missing-cell`/`constraint-error` duplicates from their expected lists, which is exactly the behavior your PR description says it fixes.

I also added coverage for two side effects of the same diff that had no test at all and were silent crash bugs before your fix (confirmed red on the parent commit by reverting the three production files locally, never committed):

- `test_resource_validate_fields_match_exact_missing_primary_key_is_reported_once`: a primary-key field truncated out of the expected fields under `exact` used to still get checked per row against all-`None` cells, raising a spurious `primary-key` error on every row.
- `test_resource_validate_fields_match_superset_tolerates_foreign_key_on_absent_field`: a foreign key whose own field is legitimately absent under `superset` used to **raise an uncaught `KeyError`** (`row["parent"]`), crashing validation outright rather than just tolerating the mismatch.
- `analyzer/test_resource.py::test_analyze_resource_detailed_skips_a_field_absent_from_the_header`: `detailed=True` analysis used to raise `KeyError` on `columns_data[field.name]` for a schema field the header doesn't carry (tolerated under `superset`).
- `test_header.py::test_get_expected_fields_exact_extended_fields_avoid_name_collisions`: covers the new suffix-disambiguation loop (`label2`) when a synthesized field name would otherwise collide with an existing field.

What I didn't do: I didn't add a `fieldsMatch` stack line to any instructions file — this repo already has none, and nothing here required establishing a new harness fact (pytest's own file already covers it). I also didn't touch the mutation/coverage tooling; if this repo runs one, it'd be worth scoping a run to these three files to check for any other survivor on the changed lines, particularly around the `used_names` suffix loop. Production code is untouched, nothing is committed, and `uv.lock` was left behind by `uv sync` in `.python/` setup — harmless but you may want to `git clean` it if you don't want it hanging around.
