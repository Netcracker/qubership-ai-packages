## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Breaking changes

- On `main`, `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` pass validation when the key's type has comparability `NONE`. With this change they fail validation, as `MIN` and `MAX` already do for the same type:

  ```text
  Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
  ```

  No built-in type reports `NONE`, so this affects only types that declare it. `RelDataTypeImpl.getComparability()` returns `ALL`. Its only override in core is `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. `ARRAY`, `MAP`, `MULTISET`, `ROW`, and types created by `CREATE TYPE` therefore validate as before. In this repository, the testkit's `ADDRESS` fixture is the only type constructed with `NONE`. If a type is comparable at run time, it should report `ALL`, because `MIN` and `MAX` on a `NONE` type fail validation on `main` already.

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)`, and their aliases `MIN_BY` and `MAX_BY` require a comparable key, but the validator accepts a key whose type has comparability `NONE`. In the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`:

```sql
select arg_min(empno, home_address) from emp_address  -- validates on main
select min(home_address) from emp_address             -- fails validation on main
```

The problem shows up with the `VECTOR` type from #5331, which reports `NONE` because embeddings have no meaningful order. On that branch, without this fix:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

Here the user gets an internal error where they should get a validation error.

The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283). It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. The checker also ignored the result of its operand-count check. With this change, when `throwOnFailure` is true, the checker throws `callBinding.newValidationSignatureError()` for an invalid operand count or a non-comparable key, as the other checkers do. `SqlOperator.validateOperands` is unchanged.

The value (the first argument) still does not need to be comparable. `arg_min(home_address, empno)` still validates.

**Scope.** This needs a decision from a maintainer: should these four functions reject a key whose type reports `NONE`, or stay permissive for such types? If they stay permissive, #5331 will reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses, and this PR will be closed. Until then, #5331 depends on this change to reject a `VECTOR` key in these functions.

On the point that all types are comparable at run time, the Enumerable convention does not support that for these functions. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key `v` (comparability `ALL`) validates and then fails with the same `Unable to implement EnumerableAggregate` error. On the same data, `MIN(v)` and `ORDER BY v` work. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That `ARRAY` failure is not fixed here, and no Jira issue has been filed for it yet.
