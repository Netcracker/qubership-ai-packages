## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)`, and their aliases `MIN_BY` and `MAX_BY` require the key to be comparable, but the validator accepts a key whose type has comparability `NONE`. `MIN` and `MAX` already reject that type during validation. This PR makes the four functions reject it too.

To reproduce in `SqlValidatorTest`: the test catalog's `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`.

```sql
select arg_min(empno, home_address) from emp_address
```

On `main`, this validates. So do `ARG_MAX`, `MIN_BY`, and `MAX_BY` (Spark library). With this change, they fail the same way `MIN(home_address)` does:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

Cause: `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283), returns `false` for a non-comparable key but never throws. `SqlOperator.validateOperands` ignores the value it returns. It also discards the result of the operand-count check.

Changes:

- `OperandTypes.ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when the operand count is invalid, or when the key is not comparable and `throwOnFailure` is true. Otherwise it returns `false`. As in the other operand type checkers, the `throwOnFailure` flag decides whether it throws. `SqlOperator.validateOperands` is unchanged.
- `SqlValidatorTest.testArgMinMaxNonComparableKey` covers the four functions with a non-comparable key. It also checks that a non-comparable value (the first argument) is still accepted.

## Effect on types that declare `NONE`

The change affects only types whose comparability is `NONE`. Built-in types in core report `ALL`. `RelDataTypeImpl.getComparability()` returns `ALL`, and the only override in core, `ObjectSqlType`, returns the comparability it was constructed with. So `ARRAY`, `MAP`, `MULTISET`, `ROW`, and types created by `CREATE TYPE` validate as before. In this repository, the only type constructed with `NONE` is the testkit's `ADDRESS` fixture.

A committer reported that the Calcite runtime treats all types as `Comparable`, and that this change would break the committer's implementation.

For a type that declares `NONE`, `MIN` and `MAX` already reject it through `ComparableOperandTypeChecker`. This PR makes the four functions match them. At run time on the Enumerable convention, a comparable type is not enough for these functions today. `ARG_MIN(x, v)` with `v` an `ARRAY` (comparability `ALL`) validates and then fails with `Unable to implement EnumerableAggregate`, while `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That runtime failure is a separate issue from this PR. This PR decides the key's comparability at validation.

## Why this matters for PR #5331

PR #5331 adds a `VECTOR` type whose comparability is `NONE`, because embeddings have no meaningful order. That would make `VECTOR` the first built-in type to report `NONE`. On that branch, without this change:

- `SELECT MIN(v) FROM t` fails validation with `Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'`.
- `SELECT x FROM t ORDER BY v` fails validation with `Values of type 'VECTOR(2, REAL)' are not comparable`.
- `SELECT ARG_MIN(x, v) FROM t` validates, then fails with `IllegalStateException: Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])`.

Without this change, `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` are the only places where `NONE` is not enforced, so the user gets an internal error instead of a validation error. This PR changes nothing for types that report `ALL`, which includes every other built-in type.

## Open question for reviewers

No decision has been recorded yet. The question is whether `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` should reject a key whose type declares `NONE`, as this PR does, or stay permissive for such types. If they should stay permissive, the alternative is to close this PR and reject `VECTOR` keys only in PR #5331, as that PR already does for `ORDER BY`, `GROUP BY`, and the other clauses.
