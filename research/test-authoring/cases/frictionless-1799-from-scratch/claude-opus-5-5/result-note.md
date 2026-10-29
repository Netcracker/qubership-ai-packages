I updated six existing tests that #1799 broke and added the tests it was missing, without touching production code or committing. The full suite passes on HEAD (1908 passed, 292 skipped). I also ran the four changed test files against the parent commit (#1798): every new case fails there except four controls, and each failure shows the bug it targets, not an import or name error.

Here is the message for the author of #1799:

---

#1799 left six existing tests failing because they still expected the old double reporting. I updated them and added tests for the behavior the change fixes. All tests are in the existing `__spec__` files, in the shape of the tests around them.

**Existing tests I updated** (each expected per-row cell errors that a header mismatch under `exact` no longer produces):
- `test_header.py::test_get_expected_fields[exact: extra labels get no field]`: now expects `["a", "extra"]`, and the case id changed to match.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells`: renamed `..._extra_label_is_reported_once`. It no longer expects `extra-cell` on rows 2–3.
- `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950`: the `missing-cell` and `constraint-error` on each row are gone.
- `test_resource_validate_fields_match_extra_label[exact]` and `test_resource_validate_fields_match_missing_field[exact]`: `exact` now gives the same result as `equal`.
- `package/__spec__/test_validate.py::test_package_validate_with_schema_issue_348`: only `missing-label` remains.

**Tests I added:**
- **`Header.get_expected_fields`** (`test_header.py`):
  - Under `exact`, fields beyond the labels are dropped.
  - An extra label that collides with a name already in use gets a suffix: `a2`, or `a3` if `a2` is taken.
  - Extra fields are `any`-typed under `exact` too (I added `exact` to the existing test).
  - With no header, every mode keeps all schema fields.
- **Validation and reading** (`test_validate_schema.py`):
  - Under `exact`, a header mismatch still reports cell errors for rows that are irregular compared with the header, and stays silent on regular rows. There is one test for an extra label and one for a missing field.
  - An extra label named like a declared field keeps the declared field's typed value.
  - **With `header=False`, every `fieldsMatch` mode reads cells by position.** Before this change, the name-matched modes read every row as empty and flagged each one as `blank-row`. The commit message doesn't mention this fix.
  - `unique`, primary key and foreign key are checked only on fields present in the header, each next to a control on a present field that still reports. **Before this change, `unique` or a foreign key on a missing field raised `KeyError` under name-matched modes.** The foreign-key cases are separate rows because, on the old code, a failing key on a present field hid that crash.
- **Analyzer** (`analyzer/__spec__/test_resource.py`):
  - A field missing from the header no longer appears in `fieldStats` or in the null-row counts. Before, it was included under `exact` and raised `KeyError` under `equal`.
  - A column the schema doesn't declare no longer raises a schema error under `equal`.

**Level:** all the new tests are small (in-memory data and one process), except the updated tests that still read `data/table.csv`. No larger test is needed, because nothing in this change crosses a process boundary.

**Proposed, not done:**
- **Composite primary key with one part missing.** Under `exact`, a key like `["id", "key"]` where `key` isn't in the header is now skipped entirely; before, it still flagged duplicate `id` values. Name-matched modes already behaved this way. I didn't write a test for it because it's a design decision: please confirm it's intended, or keep checking the columns that are present.
- **Exact-mode controls.** The `exact` controls (the primary key on `id`, the foreign key on `parent`) can't pass on the old code, which added a `missing-cell` to every row. They still show that the check runs.
- **Test stack line.** The repository has no `AGENTS.md` or `CLAUDE.md`. I suggest adding one with: `Tests: pytest engine and assertions; tests live in __spec__ beside the code.` I didn't create the file.

---

Everything is uncommitted. The temporary checkout of the parent commit used for the comparison has been removed.
