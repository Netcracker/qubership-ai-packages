All 1835 tests pass, production code untouched, nothing committed.

---

**Message for the author of PR #1799:**

The fix changes what `Header.get_expected_fields()` and `TableResource.__open_row_stream` return/check, and that surfaced in five places. I verified every change below is red against the pre-fix code (`44661ad`) and green against your commit, using a throwaway worktree.

**Tests whose expectations moved** (they encoded the exact bug you fixed — a header mismatch double-reported as a per-row cell error — so they were silently green before and are the regression evidence for the fix):
- `test_resource_validate_schema_extra_headers_and_cells` and `test_resource_validate_less_actual_fields_with_required_constraint_issue_950` (`frictionless/resource/__spec__/test_validate_schema.py`) — also dropped a stray `print(...)` left in the second one.
- `test_package_validate_with_schema_issue_348` (`frictionless/package/__spec__/test_validate.py`).
- `test_resource_validate_fields_match_extra_label` / `test_resource_validate_fields_match_missing_field`, `exact` case (same file).
- `test_get_expected_fields[exact: extra labels get no field]` in `frictionless/table/__spec__/test_header.py` — turns out under the new code `exact` *does* now get a field for an extra label (an `any`-typed one, to make the handler count match); I renamed and fixed it.

**New tests for behavior this commit changes but a prior test never pinned:**
- `test_header.py`: `exact` truncating fields to the label count when the schema has more fields than labels; a missing header (`labels == []`) now short-circuits to the full field list under every `fieldsMatch` mode (previously only `exact` did — the name-matched modes went through the matching logic against an empty label list and silently produced **zero** expected fields, so a headerless resource with e.g. `fieldsMatch: superset` read every row as `{}`); and the new suffix-renaming of an extra label that collides with an already-used field name (`"a2"`).
- `resources/__spec__/table/test_schema.py`: three regressions I found by reasoning through why `table.py`'s unique/primary-key/foreign-key checks now filter by `expected_fields` instead of `self.schema.fields`. Pre-fix, a `unique`-constrained field or a foreign key's field absent from the header under a tolerant mode (e.g. `superset`) crashed with an unhandled `KeyError` reading `row[field_name]`. A primary-key field absent from the header under `header_case=False` didn't crash but silently compared every row's empty key against every other row's and reported spurious `primary-key` duplicates from row 2 on.
- `analyzer/__spec__/test_resource.py`: the same root cause breaks `analyze()` — an extra, undeclared label crashed with `FrictionlessException: field ... does not exist` (non-detailed path), and a schema field missing from the header crashed with `KeyError` in the `detailed=True` field-stats/correlation loop.

**What I did not add:** a test with more than one data row demonstrating the "cell error reported for every row" wording from your PR description — the mechanism builds cell handlers once per stream and reuses them unchanged across rows, so a single-row case already pins it; a multi-row variant would be redundant. I also didn't add a stack line for this repo's test harness (pytest/plain `assert`) to `AGENTS.md`/`CLAUDE.md` since neither file exists here and there's no user to confirm with in this session — happy to add `Tests: pytest engine, pytest assertions` to a new `AGENTS.md` if you'd like.
