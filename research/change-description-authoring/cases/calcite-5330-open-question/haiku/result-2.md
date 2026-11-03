## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

### Breaking changes

In 1.43.0, the next release after `calcite-1.42.0`, `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY` and `MAX_BY` reject a key whose type reports comparability `NONE`. On `main`, such a query validates. After this change it fails with:

```text
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

Use a key whose type is comparable, as `MIN` and `MAX` already require. In this repository, only the testkit's `ADDRESS` fixture reports `NONE`. A downstream type that reports `NONE` is covered in Scope.

### Why

`ARG_MIN`, `ARG_MAX`, `MIN_BY` and `MAX_BY` accept a key whose type reports comparability `NONE`, while `MIN` and `MAX` reject it. The check for these four functions is `OperandTypes.ANY_COMPARABLE` (added in CALCITE-5283). It returns `false` for such a key but never throws, and `SqlOperator.validateOperands` ignores the return value.

On `main`, the only type that reports `NONE` is the testkit's `ADDRESS`. #5331 adds `VECTOR`, whose embeddings have no meaningful order. On that branch, without this change:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException: Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

The `ARG_MIN` query gets an internal error where the other two get a validation error.

### What

`ANY_COMPARABLE` now throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and either the operand count is invalid or the key is not comparable. Otherwise it returns `false`. The operand-count result was discarded before, and the checker now honors it, as the other checkers do. `SqlOperator.validateOperands` is unchanged.

Keys of types that report `ALL` validate as before. That covers `ARRAY`, `MAP`, `MULTISET`, `ROW`, and types from `CREATE TYPE`. A non-comparable first argument also still validates.

### Verification

`testArgMinMaxNonComparableKey` covers the four functions with a `NONE` key. Its two `ok()` assertions for a non-comparable value pass without this change. They pin the first argument, which this change must not move.

### Scope

Open question for a maintainer: should these functions keep accepting a key whose type reports `NONE`? The committer's concern is a downstream implementation whose types report `NONE` but are comparable at run time. After this change, such a key fails `ARG_MIN`, as it already fails `MIN`, because `MIN` and `MAX` reject `NONE` types through `ComparableOperandTypeChecker`. The decision is between two options:

- Merge this change and accept the break for such types. Which downstream types report `NONE` but are comparable at run time would settle whether that is acceptable.
- Keep these functions permissive, reject only `VECTOR` keys in #5331 (as #5331 already does for `ORDER BY`, `GROUP BY` and the other clauses), and close this pull request.

Not changed here: an `ARRAY` key (comparability `ALL`) validates, then fails in the Enumerable implementation with the same `Unable to implement EnumerableAggregate` error, while `MIN(v)` and `ORDER BY v` work on that data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That is a separate issue, not filed yet.
