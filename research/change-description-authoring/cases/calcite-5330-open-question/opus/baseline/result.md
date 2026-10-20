## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

The validator accepts `ARG_MIN(value, key)` and `ARG_MAX(value, key)` when the type of the key has comparability `NONE`. It also accepts their aliases `MIN_BY` and `MAX_BY` (Spark library) for such a key. `MIN` and `MAX` already reject that type at validation, through `ComparableOperandTypeChecker`. With this change, the four functions reject it too:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

The cause is in `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions, which was added in CALCITE-5283. It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. The checker also discards the result of the operand-count check.

Changes:

- `OperandTypes.ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and either the operand count is invalid or the key is not comparable. When `throwOnFailure` is false, it returns `false` in those cases. `SqlOperator.validateOperands` is unchanged.
- `SqlValidatorTest.testArgMinMaxNonComparableKey` checks that all four functions reject a non-comparable key. It also checks that a non-comparable value (the first argument) is still accepted.

### Which types are affected

The change affects only types whose `getComparability()` returns `NONE`. On `main`, no built-in type does:

- `RelDataTypeImpl.getComparability()` returns `ALL`.
- In core, `ObjectSqlType` is the only class that overrides it, and it returns the comparability it was constructed with. `SingleColumnAliasRelDataType` delegates.
- `ARRAY`, `MAP`, `MULTISET`, `ROW`, and the types created by `CREATE TYPE` all report `ALL`. For keys of these types, the four functions validate the same way as before.
- The only type in this repository that is constructed with `NONE` is the testkit's `ADDRESS` fixture, which the new test uses.

An application type that reports `NONE` is now rejected as the key of these functions. `MIN` and `MAX` on that type already fail at validation on `main`.

### Motivation

PR #5331 adds a `VECTOR` type with comparability `NONE`, because embeddings have no meaningful order. That would make `VECTOR` the first built-in type that reports `NONE`. On that branch, without this change, `ARG_MIN` validates and then fails with an internal error, while `MIN` and `ORDER BY` fail at validation:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

`ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` are the only functions that accept a `VECTOR` operand where an order is required. This pull request makes them reject it at validation.

### How to reproduce on `main`

In the test catalog of `SqlValidatorTest`, the column `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`. The following query passes validation, and so do the same queries with `ARG_MAX`, `MIN_BY`, and `MAX_BY`:

```sql
select arg_min(empno, home_address) from emp_address
```

### Out of scope

On `main`, `ARG_MIN(x, v)` with an `ARRAY` key `v` validates and then fails on the Enumerable convention with the same `Unable to implement EnumerableAggregate` error. `MIN(v)` and `ORDER BY v` succeed on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. `ARRAY` reports `ALL`, so this pull request leaves that behavior as it is. That bug needs its own Jira issue, which nobody has filed yet.

### Alternative

These functions could instead stay permissive for keys that report `NONE`. In that case, #5331 would reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses, and this pull request would be closed.
