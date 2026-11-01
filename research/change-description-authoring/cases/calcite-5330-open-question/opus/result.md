## Breaking changes

In 1.42.0, `ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` passed validation even when the key (the second argument) had a type with comparability `NONE`. With this change they fail validation, the same way `MIN` and `MAX` already do for such a type:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

Only types that declare `NONE` are affected. `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in core is `ObjectSqlType`, which returns the comparability it was constructed with. On `main`, the only type constructed with `NONE` is the testkit's `ADDRESS` fixture. If a type's values are comparable at run time, it can declare `ALL`.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

To reproduce in `SqlValidatorTest`, use `EMP_ADDRESS.HOME_ADDRESS` from the test catalog. Its structured type `ADDRESS` has comparability `NONE`:

```sql
select arg_min(empno, home_address) from emp_address
```

On `main` this query passes validation, and so do `ARG_MAX`, `MIN_BY` and `MAX_BY` (Spark library). `MIN(home_address)` fails with the error above.

These four functions use the operand type checker `OperandTypes.ANY_COMPARABLE`, added in CALCITE-5283. For a non-comparable key it returned `false` and never threw. It also discarded the result of the operand-count check. `SqlOperator.validateOperands` ignores the returned value, so the call passed validation.

With this change, `ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and either the operand count is invalid or the key is not comparable. Otherwise it returns `false`, like the other checkers. `SqlOperator.validateOperands` is unchanged.

Keys whose type reports `ALL` validate as before. That covers `ARRAY`, `MAP`, `MULTISET`, `ROW` and types created by `CREATE TYPE`. A non-comparable value (the first argument) is still accepted. The test cases for that already pass without this change.

**Scope.** A committer needs to decide whether these functions should reject a `NONE` key or stay permissive. The maintainer said that in the Calcite runtime all types implement `Comparable`, and that this change would break their implementation. They have not yet answered which of their types report `NONE`. Facts relevant to the decision:

- #5331 adds a `VECTOR` type with comparability `NONE`, which would make it the first built-in type that reports `NONE`. On that branch, without this fix, `MIN(v)` and `ORDER BY v` fail validation. `ARG_MIN(x, v)` passes validation and then fails at implementation:

  ```text
  IllegalStateException: Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
  ```

- On `main`, `ARG_MIN(x, v)` with an `ARRAY` key (comparability `ALL`) also passes validation and then fails on the Enumerable convention with the same `Unable to implement EnumerableAggregate` error. `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That is a separate issue, and this change does not fix it.
- If these functions should stay permissive, #5331 can reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY` and other clauses, and this pull request will be closed.
