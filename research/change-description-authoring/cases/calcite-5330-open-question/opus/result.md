**Breaking changes.**
On `main`, `ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` accept a key whose type has comparability `NONE`. With this change, that query fails validation. Every built-in type in core reports `ALL`, so the change only affects types that are constructed with `NONE`. `MIN` and `MAX` already reject those types.

- Starting with 1.43.0, `ARG_MIN(value, key)`, `ARG_MAX`, `MIN_BY` and `MAX_BY` fail validation when the key's comparability is `NONE`. For example, `arg_min(empno, home_address)` fails with `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`. If the key is comparable at run time, construct its type with comparability `ALL`.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

These four functions need a comparable key, but the validator accepts a key that is not comparable. The user then gets an internal error at implementation time instead of a validation error. #5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, without this fix:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

On `main`, the test catalog's `EMP_ADDRESS.HOME_ADDRESS` column shows the same gap. Its structured type `ADDRESS` has comparability `NONE`, and `select arg_min(empno, home_address) from emp_address` validates.

The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283). For a non-comparable key it returns `false` but never throws, and `SqlOperator.validateOperands` ignores the returned value. It also ignored the result of the operand-count check. The checker now throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true, like the other checkers. `SqlOperator.validateOperands` is unchanged.

The claim that no built-in type is affected comes from the code. `RelDataTypeImpl.getComparability()` returns `ALL`. Its only override in core is in `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. In this repository, only the testkit's `ADDRESS` fixture is constructed with `NONE`.

The test also checks that a non-comparable value (the first argument) is still accepted. That part passes without the change.

**Scope.** The maintainer needs to decide one question: should a type that reports `NONE` but is comparable at run time stay valid as the key of these four functions? This pull request rejects it, and `MIN` on such a type already fails today. If these functions should stay permissive, #5331 can reject only `VECTOR` keys, as it already does for `ORDER BY`, `GROUP BY` and the other clauses, and this pull request can be closed. This pull request does not depend on #5331.

A separate defect is left out of this change, and no issue has been filed for it yet. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key (comparability `ALL`) validates and then fails with the same `Unable to implement EnumerableAggregate` error, while `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`.
