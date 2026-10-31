All green, no production code touched, and no commit made as instructed. Here's the message I'd leave for the author of the PR:

---

**Tests for #1799**

The PR changes which errors are reported for a header/schema mismatch under `fieldsMatch: "exact"`, but it shipped with no test changes — and it actually left five existing tests asserting the *old* (now-wrong) behavior, so the suite was red on this branch. I fixed those and added the cases the fix newly owns. Everything below was verified red on the parent commit (`44661ad`) and green on this one.

**Updated (stale, were asserting the pre-fix duplicate errors):**
- `test_header.py::test_get_expected_fields` — the `"exact: extra labels get no field"` case: `get_expected_fields()` now gives an extra label a synthetic `any` field under `exact` too, so it's no longer field-less.
- `test_validate_schema.py::test_resource_validate_schema_extra_headers_and_cells` — dropped the two now-gone per-row `extra-cell` errors.
- `test_validate_schema.py::test_resource_validate_less_actual_fields_with_required_constraint_issue_950` — dropped the now-gone per-row `constraint-error`/`missing-cell` pairs (the field is truncated away entirely, so it's never checked per row; the single `missing-label` is all that's left).
- `test_validate_schema.py::test_resource_validate_fields_match_extra_label` / `..._missing_field` (`exact` case) — same duplicate-error removal.
- `test_validate.py::test_package_validate_with_schema_issue_348` — same.

**New:**
- `test_header.py`: a case for `exact` truncating fields beyond the labels (the mirror of the existing "extra labels" case), plus two tests pinning the dedup logic when a synthetic field's name collides with a real field or with another synthetic field (`"a2"`, `"x2"`).
- `test_validate_schema.py::test_resource_validate_fields_match_exact_still_reports_an_irregular_row` — the control: with a field truncated away, a row that is itself genuinely irregular (wrong cell count for the header) still gets its own `extra-cell` error. This matters because the old code actually got this backwards: it reported a spurious error on the *regular* row and missed the real one on the irregular row.
- `test_schema.py::test_resource_schema_primary_key_label_missing_is_not_rechecked_per_row` and `..._foreign_key_target_label_missing_does_not_raise` — the primary-key and foreign-key integrity checks now skip a field that was truncated out of `expected_fields`. The foreign-key one is the sharper of the two: I verified that if `table.py`'s new `if not set(target_key).issubset(expected_field_names): continue` guard is removed while keeping the new `header.py`, this crashes with `KeyError: 'Row does not have a field cat'`. So that line isn't just cosmetic — it prevents a real crash the `header.py` truncation would otherwise introduce.
- `analyzer/test_resource.py::test_analyze_resource_excludes_a_field_missing_from_the_header` — `analyze(detailed=True)` no longer invents a bogus `fieldStats` entry (type `categorical`, values `{None}`) for a field with no data behind it.

**Not done, flagging for you:** the `unique` constraint path in `table.py` (`for field in expected_fields: if field.constraints.get("unique")`) changed the same way as primary/foreign keys, but I couldn't construct an observable difference — before the fix, a unique field dropped from the header just read as `None` every row and was silently skipped (`if cell is not None`), so there's no user-visible bug to pin there. I left it untested; let me know if you had a different scenario in mind for it.
