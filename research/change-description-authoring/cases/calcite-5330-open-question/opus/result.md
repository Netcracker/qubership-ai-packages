## Breaking changes

`ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` now fail validation when the type of the key (the second argument) has comparability `NONE`. Calcite 1.42.0 accepts such a key. For the test catalog's `ADDRESS` type, the error is:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

Only types that report `NONE` are affected, and no built-in type does:

- `RelDataTypeImpl.getComparability()` returns `ALL`.
- The only override in core is `ObjectSqlType`, which returns the comparability it was constructed with. `SingleColumnAliasRelDataType` delegates to it.
- In this repository, the only type constructed with `NONE` is the testkit's `ADDRESS` fixture.

`MIN` and `MAX` already reject a type that reports `NONE`. If a type is comparable at run time, it should report `ALL`, and then all six functions accept it.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)` and their aliases `MIN_BY` and `MAX_BY` require a comparable key. Even so, the validator accepts a key whose type has comparability `NONE`, while `MIN` and `MAX` reject the same type. In `SqlValidatorTest`, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`:

```sql
select arg_min(empno, home_address) from emp_address
```

On `main` this query validates, and so do the same calls to `ARG_MAX`, `MIN_BY` and `MAX_BY` (Spark library). With this change, all four fail with the error above, as `MIN(home_address)` does.

#5331 adds a `VECTOR` type whose comparability is `NONE`, which would make it the first built-in type that reports `NONE`. On that branch, without this fix, the four functions are the only place where comparability is not checked. A user gets an internal error instead of a validation error:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

The operand type checker of these functions is `OperandTypes.ANY_COMPARABLE`, added in CALCITE-5283. It returns `false` for a non-comparable key but never throws, and it discards the result of its own operand-count check. `SqlOperator.validateOperands` ignores the returned value. The checker now throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and either the operand count is invalid or the key is not comparable, as the other checkers do. `SqlOperator.validateOperands` is unchanged.

These cases are unchanged:

- A key of type `ARRAY`, `MAP`, `MULTISET`, `ROW`, or a type created by `CREATE TYPE` reports `ALL` and validates as before.
- The value (the first argument) still does not need to be comparable. The `ok()` cases in `testArgMinMaxNonComparableKey` cover this, and they also pass without the change.

### Open question for the maintainer

A review comment says this is a breaking change for an implementation in which all types implement `Comparable`. It is not yet known which of those types report `NONE`. A type that reports `NONE` already fails `MIN` today.

The decision needed: should these four functions reject a non-comparable key, as this PR does? The alternative is to keep them permissive. In that case, #5331 would reject only `VECTOR` keys, as it already does for `ORDER BY`, `GROUP BY` and the other clauses, and this PR would be closed.

On the Enumerable convention, being comparable at run time does not hold for these functions today. On `main`, `ARG_MIN(x, v)` with `v` of type `ARRAY` (comparability `ALL`) validates and then fails with the same "Unable to implement EnumerableAggregate" `IllegalStateException`. On the same data, `MIN(v)` and `ORDER BY v` work. `ArgMinMaxImplementor` compares a non-primitive key with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. This PR does not fix that failure, and no issue has been filed for it yet.
