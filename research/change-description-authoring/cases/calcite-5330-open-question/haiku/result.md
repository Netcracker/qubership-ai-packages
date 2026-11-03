## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

### Breaking changes

`ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY` and `MAX_BY` (Spark library) now reject a key whose type reports comparability `NONE`. On `main`, these calls validate. In this repository, only the test fixture `ADDRESS` reports `NONE`. `ARRAY`, `MAP`, `MULTISET`, `ROW` and types made by `CREATE TYPE` report `ALL` and are not affected. A call with a `NONE` key must pass a key whose type reports `ALL`. The error names the function:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

### Why

`MIN` and `MAX` already reject a key whose type reports comparability `NONE`. In `SqlValidatorTest`, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`. This query validates before the change:

```sql
select arg_min(empno, home_address) from emp_address
```

#5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, without this change, `MIN(v)` and `ORDER BY v` fail at validation, but `SELECT ARG_MIN(x, v) FROM t` validates and then fails with `IllegalStateException`, message `Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])`.

### What

The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283). It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores that result. It also discards the result of the operand-count check.

`ANY_COMPARABLE` now throws `callBinding.newValidationSignatureError()` when the operand count is invalid, or when the key is not comparable and `throwOnFailure` is true. Otherwise it returns `false`. This makes `ANY_COMPARABLE` honor `throwOnFailure` like the other checkers. `SqlOperator.validateOperands` is unchanged. A non-comparable first argument still validates, and so does a key whose type reports `ALL`.

### How to verify

The two `ok()` cases in `testArgMinMaxNonComparableKey` pass without this change, because a non-comparable first argument already validated.

### Scope

- Open decision for the maintainer: keep these functions rejecting a `NONE` key, as this change does, or keep them permissive and reject only `VECTOR` keys in #5331, as #5331 already does for `ORDER BY`, `GROUP BY` and the other clauses. The maintainer reports that all types in their implementation implement `Comparable`, so this change would break them. Which of their types report `NONE` is still open, and the decision depends on it.
- #5331 depends on this decision. Unless this change lands, or #5331 rejects `VECTOR` keys for these functions, `ARG_MIN` on a `VECTOR` key reaches the error above.
- Not in this change: on the Enumerable convention, `ARG_MIN(x, v)` with `v` an `ARRAY` (comparability `ALL`) validates on `main` and then fails with the same `IllegalStateException`, although `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. No issue is filed for it yet.
