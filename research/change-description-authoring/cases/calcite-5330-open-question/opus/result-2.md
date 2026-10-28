## Breaking changes

In 1.42.0, a query could pass a key whose type reports comparability `NONE` to `ARG_MIN`, `ARG_MAX`, `MIN_BY`, or `MAX_BY`, and it validated. With this change, the query fails validation. No built-in type in core reports `NONE` (see below), so this affects only a type system that declares it.

- `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, and the Spark library's `MIN_BY` and `MAX_BY` fail when the key has comparability `NONE`. The function name and argument types in the message vary. This is the message for the structured type `ADDRESS` from the test catalog: `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`. To use a type as the key, it has to report comparability `ALL`. `MIN` and `MAX` already reject a type that reports `NONE`.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`MIN` and `MAX` reject a type with comparability `NONE` at validation, through `ComparableOperandTypeChecker`. `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` accept the same type as their key. On `main` no built-in type reports `NONE`. `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in core is `ObjectSqlType`, which returns the comparability it was constructed with. The only type constructed with `NONE` is the testkit's `ADDRESS` fixture. #5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, without this change:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

These four functions use `OperandTypes.ANY_COMPARABLE` (added in CALCITE-5283) as their operand type checker. It returned `false` for a non-comparable key but never threw, and `SqlOperator.validateOperands` ignores the returned value. It also discarded the result of the operand-count check. Like the other checkers, `ANY_COMPARABLE` now throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and either the operand count is invalid or the key is not comparable. Otherwise it returns `false`. `SqlOperator.validateOperands` is unchanged.

Not changed: a key of any type that reports `ALL` validates as before. This includes `ARRAY`, `MAP`, `MULTISET`, `ROW`, and the types created by `CREATE TYPE`. The value, the first argument, can still be non-comparable.

Open question for the maintainer: in Jira you wrote that "in the Calcite runtime all types are really comparable", and that this change would break your implementation. For these functions on the Enumerable convention, that is not the case on `main`. With `v` an `ARRAY`, whose comparability is `ALL`, `ARG_MIN(x, v)` validates and then fails with the same `Unable to implement EnumerableAggregate`, while `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That failure is outside this change and has no issue yet. If one of your types reports `NONE` but is comparable at run time, `MIN` on it already fails validation. The decision needed is one of these:

- Merge this change, so the four functions reject a key that reports `NONE`, as `MIN` and `MAX` do.
- Keep the four functions permissive. In that case #5331 rejects `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses, and this pull request is closed.
