**Breaking changes.** A query that passes a key whose type reports comparability `NONE` to `ARG_MIN`, `ARG_MAX`, `MIN_BY`, or `MAX_BY` used to pass validation. That has been true since CALCITE-5283 added `OperandTypes.ANY_COMPARABLE`. These queries now fail validation. Every built-in type reports `ALL`, so only two kinds of key type are affected: a custom `RelDataType` that overrides `getComparability()` to return `NONE`, and an `ObjectSqlType` constructed with `NONE`. `MIN` and `MAX` already reject such a type. If the type is comparable at run time, make it report `ALL`.

- `ARG_MIN` with a key that reports comparability `NONE` fails with `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`. `ARG_MAX`, `MIN_BY`, and `MAX_BY` fail with the same message under their own names.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)`, and their aliases `MIN_BY` and `MAX_BY` require the key to be comparable. However, the validator accepts a key whose type has comparability `NONE`, and `MIN` and `MAX` reject that same type through `ComparableOperandTypeChecker`. In the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`. On `main`, this query validates:

```sql
select arg_min(empno, home_address) from emp_address
```

#5331 adds a `VECTOR` type whose comparability is `NONE`. It would be the first built-in type that reports `NONE`. On that branch, these four functions are the only places that don't enforce comparability, so the user gets an internal error instead of a validation error:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

`ANY_COMPARABLE` returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. `ANY_COMPARABLE` also discards the result of its operand-count check. It now handles `throwOnFailure` like the other checkers: it throws `callBinding.newValidationSignatureError()` when the operand count is invalid or the key is not comparable. `SqlOperator.validateOperands` is unchanged.

Not changed: a key type that reports `ALL` validates as before. `RelDataTypeImpl.getComparability()` returns `ALL`. Its only override in core is `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. So `ARRAY`, `MAP`, `MULTISET`, `ROW`, and types created by `CREATE TYPE` are not affected. In this repository, only the testkit's `ADDRESS` fixture is constructed with `NONE`.

Not changed: the value (the first argument) doesn't need to be comparable. The test's assertions on this pass without the change.

**Scope.** The maintainer wrote in Jira: "I believe that in the Calcite runtime all types are really comparable." They also said that this would be a breaking change for their implementation. That reply was posted before #5331 was mentioned here. A maintainer needs to choose between two options:

- Reject non-comparable keys for all four functions (this PR).
- Keep them permissive. #5331 would then reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses, and this PR would be closed.

On the Enumerable convention, comparable keys are not always handled either. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key (comparability `ALL`) validates and then fails with the same "Unable to implement EnumerableAggregate" error. `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`, which is not `Comparable`. That `ARRAY` failure is not fixed here, and no Jira issue has been filed for it yet.
