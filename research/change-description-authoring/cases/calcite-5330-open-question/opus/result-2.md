## Breaking changes

`ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` now fail validation when the key's type (the second argument) reports a comparability other than `ALL`. On `main`, such a query validates. Every built-in type reports `ALL` (see Verification), so the change affects only a type that declares `NONE` itself. If that type can be compared at run time, make it report `ALL`. `MIN` and `MAX` already reject the type as it is.

- In `SqlValidatorTest`, the test catalog's `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`. On that column, `select arg_min(empno, home_address) from emp_address` fails like `MIN(home_address)` does:
  ```text
  Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
  ```
  `ARG_MAX`, and `MIN_BY` and `MAX_BY` from the Spark library, fail with the same message under their own names.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`MIN` and `MAX` reject a non-comparable argument at validation through `ComparableOperandTypeChecker`. `ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` accept a non-comparable key. Their operand type checker, `OperandTypes.ANY_COMPARABLE` (added in [CALCITE-5283](https://issues.apache.org/jira/browse/CALCITE-5283)), returns `false` for such a key but never throws. `SqlOperator.validateOperands` ignores the returned value. The checker also discarded the result of its operand-count check.

PR #5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, without this fix, these four functions are the only place where `NONE` is not enforced:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

When `throwOnFailure` is true, `ANY_COMPARABLE` now throws `callBinding.newValidationSignatureError()` for an invalid operand count or a key that is not comparable, as the other checkers do.

Not changed: a key whose type reports `ALL` validates as before. This includes `ARRAY`, `MAP`, `MULTISET`, `ROW` and types created by `CREATE TYPE`.
Not changed: the value (the first argument) does not need to be comparable. The `ok()` cases in `testArgMinMaxNonComparableKey` cover this, and they pass without the change.

**Verification.** No test establishes that every built-in type reports `ALL`, so here is where to check it. `RelDataTypeImpl.getComparability()` returns `ALL`. Its only override in core is `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. In this repository, only the testkit's `ADDRESS` fixture is constructed with `NONE`.

**Scope.** This needs a decision from a committer, who said the change breaks their implementation, where all types are comparable at run time. One option is to keep the check here. The other is to leave these four functions permissive, close this PR, and reject only `VECTOR` keys in PR #5331, as that branch already does for `ORDER BY`, `GROUP BY` and the other clauses.

The run-time assumption does not hold for these functions on the Enumerable convention. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key (comparability `ALL`) validates, then fails with the same `Unable to implement EnumerableAggregate`. `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. This PR does not fix that, and there is no Jira issue for it yet.
