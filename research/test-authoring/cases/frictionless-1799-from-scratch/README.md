# Case: write the tests frictionless-py#1799 owes, from its production change

A regression case for `test-authoring` on a batch validator: one call validates a whole table and returns every error it
found. The cases so far are compiler-like harnesses (NullAway, Calcite's validator fixture), where the harness decides
whether one act reports every mismatch. Here the test asserts on the result of one act itself, a validation report, so
it has no harness fact to learn: the skill asks for one comparison of the whole result reduced to the fields the
behavior defines. The input is the production change of
[frictionlessdata/frictionless-py#1799](https://github.com/frictionlessdata/frictionless-py/pull/1799), merged as
`dae5048627`, on its parent `44661adf0c`, without the changes the pull request made under `__spec__/`.

Before the fix, with `fieldsMatch: "exact"` (the default), a header shorter than the schema drew a `missing-label` error
and then a `missing-cell` error, plus a `constraint-error` for a required field, for the missing column in every row. A
header longer than the schema drew an `extra-label` error and an `extra-cell` error in every row. A primary key on a
missing column drew a `primary-key` error in every row. The fix makes the expected fields follow the header, so the
label error is reported once, while a row shorter or longer than its header still reports its cells. `analyze()` no
longer counts the missing column in its field statistics. Six existing tests encode the old reports and fail on the fix.

## What it exercises

- **A test that asserts on the result of one act** (§7, the paragraph on the two facts of a harness, and the pytest
  reference's *Grouping assertions*). The report of one `validate()` is the act's whole result: the assertion is one
  `report.flatten([...]) == [...]` over the row, the field, and the error type, without the message. The neighbors
  already write it that way.
- **A case that expects nothing stands with a control in one act** (§7 principle 3). The moved case is an absence: no
  cell error for the missing column. The validator checks each row on its own, so a short row whose present column still
  reports `missing-cell` can share the table with the missing label, as the pull request's own
  `test_resource_validate_missing_label_preserves_irregular_row_issue_1791` does. A primary key cannot: one schema has
  one key, and uniqueness is checked across rows, so the key's control is a separate act.
- **Which inputs** (§4). Four moved partitions: a missing label, an extra label, an integrity check on a missing column,
  and the analyzer. The pull request tests the first three and not the analyzer, although its message names it.
- **A deliberate behavior change updates the tests that encode the old behavior, and names them** (§3). On the fix,
  `test_resource_validate_schema_extra_headers_and_cells`,
  `test_resource_validate_less_actual_fields_with_required_constraint_issue_950`,
  `test_resource_validate_fields_match_extra_label[exact-…]`,
  `test_resource_validate_fields_match_missing_field[exact-…]`, `test_package_validate_with_schema_issue_348`, and
  `test_get_expected_fields[exact: extra labels get no field]` fail.
- **A neighbor shape that breaks §7** (§9).
  `test_resource_with_missing_required_header_with_schema_sync_is_true_issue_1611` loops over a list of cases with a
  stopping `assert`; the neighbors' parametrized tests carry no ids, so pytest names the rows `exact-expected0`; and
  several names end in an issue number.
- **The stack line** (§0). frictionless-py has no `AGENTS.md` or `CLAUDE.md`; the session proposes the line and creates
  no file.

## Behaviors on the base

Measured with `TableResource(data=…, schema=…).validate()` and `report.flatten(["rowNumber", "fieldNumber", "fieldName",
"type"])`:

| Input | On the base | On the fix |
| --- | --- | --- |
| header `a`, fields `a`, `b`, two rows | `missing-label` b, `missing-cell` b in rows 2 and 3 | `missing-label` b |
| the same with `b` required, one row | `missing-label` b, `constraint-error` and `missing-cell` b in row 2 | `missing-label` b |
| header `a`, `x`, field `a`, two rows | `extra-label` 2, `extra-cell` 2 in rows 2 and 3 | `extra-label` 2 |
| header `a`, `b`, fields `a`, `b`, `c`, row `1` | `missing-label` c, `missing-cell` b and c in row 2 | `missing-label` c, `missing-cell` b in row 2 |
| header `a`, `x`, field `a`, row `1`, `2`, `3` | `extra-label` 2, `extra-cell` 2 and 3 in row 2 | `extra-label` 2, `extra-cell` 3 in row 2 |
| header `a`, fields `a` integer, `b`, row `x` | `missing-label` b, `type-error` a, `missing-cell` b | `missing-label` b, `type-error` a |
| header `id`, fields `id`, `m`, primary key `m`, two rows | `missing-label` m, `missing-cell` m and `primary-key` in each row | `missing-label` m |
| header `id`, fields `id`, `m` with `unique`, or a foreign key on `m` | `missing-label` m, `missing-cell` m in each row | `missing-label` m |
| a header that matches, with a short or a long row | `missing-cell` or `extra-cell` in that row | the same |

`analyze(detailed=True)` on header `a` with integer fields `a`, `b` and two rows: on the base `fieldStats` has `a` and
`b` and `rowsWithNullValues` is 2; on the fix `fieldStats` has `a` alone and `rowsWithNullValues` is 0.

## Files

| File | What it is |
| --- | --- |
| `repo`, `base` | `https://github.com/frictionlessdata/frictionless-py.git` and `44661adf0c9ec593d48642ba380ce33bbad95e15`, the parent of the merge. |
| `change.patch` | The diff of `analyzer.py`, `resources/table.py`, and `table/header.py` between `44661adf0c` and `dae5048627`. |
| `change-message.txt` | The squash-merge message without its last paragraph, which says the commit adds regression tests and that the suite passes. |
| `production-paths` | The three files of `change.patch`. The tests live beside the code, under `frictionless/**/__spec__/`, so a directory would take them in too. |
| `build.sh` | Makes a Python 3.11 environment with `uv` under `.python/case`, which the repository ignores, then runs the four spec modules whose expectations the change moves, and every spec module that differs from `base`, and prints how many tests ran and which failed. |
| `prompt.md` | The task, with `<skill>` replaced by the path of the skill copy. It tells the session that `uv` is there, since the machine's default Python is older than the project needs. |
| `<model>/` | The output of `run-case.sh`: `result.diff`, `result-note.md`, `result-build.txt`, `run.txt`, `skill-tree`. |

The infrastructure was checked without a model on 2026-10-01 with uv 0.12 and CPython 3.11: the pull request's own tests
on the case commit give `174 tests ran, 0 failed` on the fix, and `174 tests ran, 13 failed` on the base: the six
existing tests above with their moved expectations and the seven tests the pull request added. The first run makes the
environment in about 10 seconds with a warm uv cache; the tests take under 2 seconds. Fetching the base takes about two
minutes, most of it the repository's recorded HTTP cassettes. Without the pull request's tests, the six existing tests
fail on the fix.

## How to run

From the repository root:

```bash
research/test-authoring/cases/run-case.sh research/test-authoring/cases/frictionless-1799-from-scratch <model> [<rev>]
```

## Checks

Read `result.diff` and `result-note.md` against all of them.

1. **Each moved partition has a case, through the public interface** (§3, §4). Through `TableResource.validate()` or
   `frictionless.validate()`: a missing label with no cell error for the missing column (a required field, whose
   `constraint-error` also goes, passes as this case); an extra label with no `extra-cell` for the extra column; an
   integrity check on a missing column whose report moved, such as a primary key with no `primary-key` error, or a
   foreign key under another `fieldsMatch` mode that raised `KeyError` on the base. Through `analyze()`: a missing
   column absent from `fieldStats` or from `rowsWithNullValues`. A missing one of the first three fails; a missing
   analyzer case is partial. Tests of `Header.get_expected_fields` alone do not count for the report.
2. **The tests that encoded the old reports are updated and named** (§3). Each of the six tests listed under *What it
   exercises* keeps its input and its whole-report assertion with the cell errors removed; none is deleted, skipped, or
   loosened to a count or a membership check. The parametrize id `exact: extra labels get no field` states the old rule
   and is renamed. The closing message names each updated test and the behavior that moved.
3. **The silent part of the case stands with a reporting control in one table** (§7 principle 3). The missing-label case
   shares one validated table with a row shorter or longer than its header that still reports its cell (`missing-cell`
   for a present column, or `extra-cell` past the header), or with a cell error in a present column. The extra-label
   case shares one table with such a row in the same way. A control in a separate test with its own table is partial;
   no control fails. The primary-key case is a separate act from its control (a duplicate key on a present column),
   which may be a parametrize row or a test of its own, an existing one included; it does not join the missing-label
   table if that table holds other cases.
4. **One comparison of the whole report, reduced to defined fields** (§7, pytest reference). The assertion is
   `report.flatten([...]) == ...` over the row number, the field number or name, and the error type, as a list: the
   report orders errors by row, and the neighbors compare lists. A comparison as a set or as a sorted list fails: either
   one passes an error out of order, and a set also passes a duplicated error. A comparison of `message` or `note` text
   fails. Only `report.valid`, an error count, or `"missing-cell" not in types` in place of the whole report fails (§5,
   *An assertion weakened until it passes*). Several asserts on one report where one comparison would do are partial.
   The `analyze()` result is check 10's.
5. **Each case fails under a name of its own** (§7 principle 1, §9). Cases of different rules (a missing column, an
   extra column, an integrity check, the analyzer) are separate tests or parametrize rows; no test validates a second
   table after asserting on the first, and no new test loops over cases with a stopping `assert`, as the neighbor
   `..._issue_1611` does. A new parametrized test gives each row an id that names its condition; `expected0` is partial.
6. **The reader sees each input whole** (§7 principle 2, §9). The data rows and the schema are literals in the test
   body, or the arguments of a helper that takes values, such as the existing `_validate_fields_match`. No helper builds
   the data or the schema from pieces the expectation depends on, and no new helper builds what `_validate_fields_match`
   builds with a few lines different.
7. **The name states the rule** (§7). No ordinal and no `and` joining the outcomes of two inputs; a name stating that a
   header mismatch is reported once, or that irregular rows still report their cells, passes. An issue number appended
   to a name that already states the rule is partial (the neighbors' convention, which §9 does not let override §7); a
   name that is only an issue number fails.
8. **The production code is unchanged.** The first part of `result.diff` is empty, no `AGENTS.md` or `CLAUDE.md` is
   created, and the closing message proposes a stack line (§0), such as `Tests: pytest`.
9. **Green on the fix, red on the base for each moved case** (§1). Read `result-build.txt`: no failure on the fix, and
   on the base a failure for every test that holds a moved case of check 1 and for the updated tests of check 2. A test
   that holds only controls passes on the base.
10. **One comparison of the `analyze()` result** (§7). A test of the analyzer case compares the part of the result the
    behavior defines, such as `fieldStats` keyed by field name and `rowsWithNullValues`, in one assertion (a dict or a
    tuple). Separate asserts on each key, where one comparison would show every mismatch, fail. A result with no
    analyzer test leaves this check to check 1's partial.
