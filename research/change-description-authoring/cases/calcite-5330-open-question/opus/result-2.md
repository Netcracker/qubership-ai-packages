**Breaking changes.**
Before this change, a query validated when it passed `ARG_MIN`, `ARG_MAX`, `MIN_BY` or `MAX_BY` a key whose type reports comparability `NONE`. With this change, the query fails validation, as `MIN` and `MAX` on the same type already do:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

This affects only types that report `NONE`. Types that report `ALL` validate as before. A type whose values are comparable at run time should report `ALL`, and `MIN` and `MAX` then accept it as well.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)` and their aliases `MIN_BY` and `MAX_BY` require a comparable key. Their operand type checker, `OperandTypes.ANY_COMPARABLE` (added in CALCITE-5283), returns `false` for a non-comparable key but never throws. `SqlOperator.validateOperands` ignores that return value, and the checker also discards the result of the operand-count check. #5331 adds a `VECTOR` type whose comparability is `NONE`. Without this fix, `ARG_MIN` is the only one of these queries that gets past validation on that branch:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

On `main`, `select arg_min(empno, home_address) from emp_address` validates in `SqlValidatorTest`, where `HOME_ADDRESS` has the structured type `ADDRESS` with comparability `NONE`.

When `throwOnFailure` is true and either the operand count is invalid or the key is not comparable, `ANY_COMPARABLE` now throws `callBinding.newValidationSignatureError()`, as the other checkers do. Otherwise it returns `false`. `SqlOperator.validateOperands` is unchanged. The value (the first argument) still doesn't need to be comparable. The new test checks this case, and it passes without the change.

**Scope.** I need a maintainer to decide whether these four functions should enforce key comparability at validation. The Jira comment says that "in the Calcite runtime all types are really comparable". However, no built-in type in core reports `NONE`. `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in core is `ObjectSqlType`, which returns the comparability it was constructed with, and the only type constructed with `NONE` is the testkit's `ADDRESS` fixture. So `ARRAY`, `MAP`, `MULTISET`, `ROW` and the types created by `CREATE TYPE` are not affected. If these functions should stay permissive instead, #5331 can reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY` and the other clauses, and this PR can be closed.

This PR leaves out a related run-time failure, which has no Jira issue yet. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key (comparability `ALL`) validates and then fails with the same `Unable to implement EnumerableAggregate`, although `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`.
