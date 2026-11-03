**Breaking changes.** Before this change, `ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` (Spark library) passed validation with a key (the second argument) whose type has comparability `NONE`. They now fail validation, as `MIN` and `MAX` already do for such a key. Only types that declare `NONE` are affected. `RelDataTypeImpl.getComparability()` returns `ALL`, and the only override in core is `ObjectSqlType`, which returns the comparability it was constructed with. In this repository, only the testkit's `ADDRESS` fixture is constructed with `NONE`. `ARRAY`, `MAP`, `MULTISET`, `ROW` and the types created by `CREATE TYPE` report `ALL` and validate as before. If a project's type reports `NONE` but can be compared at run time, the project has to make the type report `ALL`.

- With a key whose comparability is `NONE`, each of the four functions fails validation, for example: `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

These four functions require a comparable key, but the validator accepts a key whose comparability is `NONE`. In the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`, and this query validates:

```sql
select arg_min(empno, home_address) from emp_address
```

#5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, without this change, `ARG_MIN` is the only one of these queries that is not rejected at validation. It fails later with an internal error:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

`OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283), returned `false` for a non-comparable key but never threw, and `SqlOperator.validateOperands` ignores the returned value. The checker also discarded the result of the operand-count check. When `throwOnFailure` is true, the checker now throws `callBinding.newValidationSignatureError()` for an invalid operand count or a non-comparable key, like the other checkers. `SqlOperator.validateOperands` is unchanged. The value (the first argument) still doesn't need to be comparable.

The test cases with a non-comparable value, `arg_min(home_address, empno)` and `max_by(home_address, empno)`, pass without the change. They make sure that only the key is checked.

**Scope.** The maintainer said that in their implementation and in the Calcite runtime all types are comparable, so this change would break them. This needs a maintainer's decision. One option is to reject a `NONE` key in all four functions, as this PR does, which makes them consistent with `MIN` and `MAX`. The other is to keep the functions permissive, reject only `VECTOR` keys inside #5331 as that PR already does for `ORDER BY`, `GROUP BY` and the other clauses, and close this PR.

A separate problem on `main` is not fixed here. `ARG_MIN(x, v)` with an `ARRAY` key, whose comparability is `ALL`, passes validation and then fails with the same `Unable to implement EnumerableAggregate`, even though `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. No issue has been filed for it yet.
