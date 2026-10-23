## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Breaking changes

This change affects only key types whose comparability is `NONE`. Every built-in type on `main` reports `ALL` (see Verification), so only a user-defined type can be affected, such as an `ObjectSqlType` constructed with `NONE`.

- `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY(value, key)` and `MAX_BY(value, key)` used to pass validation on `main` when the key's type has comparability `NONE`. They now fail validation, the same way `MIN(key)` and `MAX(key)` already do. For `select arg_min(empno, home_address) from emp_address`, where the key's type is the test catalog's `ADDRESS`:
  ```text
  Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
  ```
  If a type is comparable at run time, it has to report comparability `ALL`, which `MIN` and `MAX` already require.

## Changes Proposed

These four functions require the key to be comparable, but the validator accepts a key whose comparability is `NONE`. `MIN` and `MAX` reject the same type through `ComparableOperandTypeChecker`.

This matters for #5331, which adds a `VECTOR` type with comparability `NONE` because embeddings have no meaningful order. `VECTOR` would be the first built-in type to report `NONE`. On that branch, without this change, `ARG_MIN` is the only place where a non-comparable key is not rejected. The user gets an internal error instead of a validation error:

```sql
SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions, which was added in CALCITE-5283. It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. The checker also discarded the result of the operand-count check.

With this change, `ANY_COMPARABLE` honors `throwOnFailure` like the other checkers. If the operand count is invalid or the key's comparability is not `ALL`, it throws `callBinding.newValidationSignatureError()` when `throwOnFailure` is true and returns `false` otherwise. `SqlOperator.validateOperands` is unchanged.

### User-visible changes

Not changed: a value (the first argument) whose comparability is `NONE` is still accepted.
Not changed: keys with comparability `ALL` validate as before. This covers `ARRAY`, `MAP`, `MULTISET`, `ROW` and types created by `CREATE TYPE`.

### Verification

The new test `SqlValidatorTest.testArgMinMaxNonComparableKey` uses `EMP_ADDRESS.HOME_ADDRESS` as the key and checks that each of the four functions fails with the signature error. These queries validate on `main`. The test also checks that a non-comparable value is still accepted.

For the claim that built-in types report `ALL`: `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in `core` is in `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates to it. In this repository, the only type constructed with `NONE` is the testkit's `ADDRESS` fixture.

### Scope and open question

The review raised a question that needs a maintainer's decision: should these four functions reject a `NONE` key, or stay permissive? The review comment says that all types are comparable in the Calcite runtime and in the reviewer's own implementation, and that this change would break them. Two points are relevant:

- Only types that report `NONE` are affected, and `MIN` on such a type already fails validation. The PR is waiting on which of the reviewer's types report `NONE`.
- On the Enumerable convention, these functions cannot compare every key type at run time. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key, whose comparability is `ALL`, validates and then fails with the same `Unable to implement EnumerableAggregate`, although `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`.

If the functions should stay permissive, #5331 can reject `VECTOR` keys itself instead, as it already does for `ORDER BY`, `GROUP BY` and the other clauses, and this PR will be closed.

This PR does not fix the `ARRAY` key failure on Enumerable. That is a separate issue, and no Jira issue has been filed for it yet.
