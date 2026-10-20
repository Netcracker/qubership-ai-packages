## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

Only a key whose type reports comparability `NONE` is affected. Calcite's own types report `ALL`, including `ARRAY`, `MAP`, `MULTISET`, `ROW`, and the types created by `CREATE TYPE`, so queries on them validate as before. The next release from `main` is 1.43.0 (`gradle.properties`), which is not a major release.

### Breaking changes

- `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` reject a key whose type has comparability `NONE`. Such a query validates on `main` today and fails validation after this change. The error names the function, for example: `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`. Pass a key whose type is comparable instead.

### Why

`ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` accept a non-comparable key, while `MIN` and `MAX` reject it at validation. The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these four functions. It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores that return value. The result of the operand-count check is discarded too.

The gap matters for `VECTOR`, which #5331 gives comparability `NONE` because embeddings have no meaningful order. On that branch, without this change:

- `SELECT MIN(v) FROM t` fails validation with `Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'`.
- `SELECT x FROM t ORDER BY v` fails validation with `Values of type 'VECTOR(2, REAL)' are not comparable`.
- `SELECT ARG_MIN(x, v) FROM t` validates, then fails with `IllegalStateException: Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])`.

The third query gets an internal error where the first two get a validation error.

### What

`ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when the operand count is invalid, or when the key is not comparable and `throwOnFailure` is true. Otherwise it returns `false`, as before. `SqlOperator.validateOperands` is unchanged. The four functions now reject a non-comparable key the way `MIN` and `MAX` do, and the operand-count result is no longer discarded.

### Verification

`SqlValidatorTest.testArgMinMaxNonComparableKey` (new) covers the four functions with a non-comparable key. It uses `EMP_ADDRESS.HOME_ADDRESS` in the test catalog, which has the structured type `ADDRESS` with comparability `NONE`. It also checks that a non-comparable value is still accepted, as in `arg_min(home_address, empno)`.

### Scope

Open question for a maintainer: should a key whose type reports `NONE` be rejected at validation, as this change does, or should these functions stay permissive for such types? A committer has said that all types are comparable in the Calcite runtime, and that this change would break their implementation.

Evidence on both sides:

- In core, only the testkit's `ADDRESS` fixture reports `NONE`.
- `MIN` and `MAX` already reject a `NONE` key at validation, through `ComparableOperandTypeChecker`.
- On `main`, `ARG_MIN(x, v)` with an `ARRAY` key validates, then fails with `Unable to implement EnumerableAggregate`, although `MIN(v)` and `ORDER BY v` work on the same data. The Enumerable runtime therefore does not compare every type either. The cause is in `ArgMinMaxImplementor`, which compares non-primitive keys with `SqlFunctions.ltNullable`. That is outside this change and has no issue number yet.

The alternative is to close this change and reject only `VECTOR` keys in #5331, as #5331 already does for `ORDER BY`, `GROUP BY`, and the other clauses.
