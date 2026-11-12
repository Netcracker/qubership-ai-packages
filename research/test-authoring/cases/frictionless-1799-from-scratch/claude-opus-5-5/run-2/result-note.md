I wrote the tests the change owes, in four test files under `frictionless/`, and committed nothing. The full suite passes on head (1882 passed). The only local failures are the `test_string_read_cell_wkt` cases, which fail identically on the base commit because the optional `wkt` dependency isn't installed. Every new case fails on the base commit with the symptom it describes, and the inputs used as comparisons pass there.

One finding you should decide on: under `exact`, `read_rows()` and `row.to_dict()` now include extra columns, under made-up names like `id2` when a label repeats a field name. And `row["name"]` for a field missing from the header now raises `KeyError` where it used to return `None`. The commit message doesn't mention either, so I didn't pin them in a test.

Here is the message I would leave for the author:

---

**Tests updated** (each asserted the per-row cell errors this change removes):
- `test_resource_validate_schema_extra_headers_and_cells`, `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`, the `exact` rows of `test_resource_validate_fields_match_extra_label` and `test_resource_validate_fields_match_missing_field`, and `test_package_validate_with_schema_issue_348`. Each now expects only the `extra-label` or `missing-label` error. For issue 950, the `constraint-error` per row on the missing required field goes away too.
- `test_get_expected_fields[exact: extra labels get no field]` now expects `["a", "extra"]` and is renamed to match.

**Tests added:**
- **`test_header.py`**, as rows of `test_get_expected_fields`:
  - under `exact`, fields beyond the labels are dropped;
  - an extra label named like a field gets a suffix (`a2`), and the suffix skips names already taken (`a3`);
  - "without a header every field is kept", for all five modes.
  - `exact` also joins `test_get_expected_fields_default_field_is_any_typed`.
- **Irregular rows still report their own cells**, each case in one validation run with a comparison input:
  - `..._extra_cell_is_reported_only_beyond_the_header`
  - `..._missing_cell_is_reported_only_within_the_header`
- **Integrity checks on fields missing from the header:**
  - `..._primary_key_is_checked_only_with_its_fields_in_the_header` (parametrized: key in the header, key field missing);
  - `..._unique_is_checked_only_on_fields_in_the_header`;
  - `..._foreign_key_is_checked_only_on_fields_in_the_header`.
  - Without the new `unique` loop and foreign-key skip, these would fail.
- **`test_resource_fields_match_reads_a_table_without_header_by_position`**, for all five modes. Moving the `if self.missing` branch also fixed headerless files under the name-matched modes: on the base commit every row came back as `blank-row`. That fix is worth a line in the PR description and the changelog.
- **Analyzer:**
  - `..._leaves_out_a_field_missing_from_the_header` (`fieldStats`, `rowsWithNullValues`, `variableTypes`);
  - `..._leaves_out_a_label_the_schema_does_not_declare` under `partial`. On the base commit this crashed with `field "extra" does not exist`.

**Mutation check:** I broke each new line of production code one at a time and reran the suite. Every change was caught except one: dropping the `issubset(expected_field_names)` part of `has_primary_key` changes nothing observable. A key field missing from the header already lands in the existing `except KeyError` branch. So that check only makes the intent clearer, and no test can tell the two versions apart.

**Proposed, not done:**
- Decide whether the row contents changes above are intended. If they are, a test of `read_rows()` with an extra label and with a missing field should pin them, and the changelog should mention them.
- Decide whether nulls in an undeclared column count toward `rowsWithNullValues`. My analyzer test uses data with no nulls so it doesn't settle that.

---

The probe and mutation scripts I used are in `/private/tmp/claude-501/-private-var-folders-c1-c191w0fd7xb7947-1fnbyq080000gn-T-tmp-4FLB4gQSxI-repo/d6a75626-2e36-48ab-92c6-8077cb205520/scratchpad/`.
