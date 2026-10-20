## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Breaking changes

This change breaks calls whose key has comparability `NONE`. In this repository only the testkit's `ADDRESS` fixture reports `NONE`. Built-in types report `ALL`, including `ARRAY`, `MAP`, `MULTISET` and `ROW`, and so do types created with `CREATE TYPE`. The next release from `main` is 1.43.0.

- `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY` and `MAX_BY` with a non-comparable key now fail validation. On `main` they validate. The error is `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`, with the called function's name in place of `ARG_MIN`. To keep such a call working, use a key of a comparable type, or make the key's type report `ALL` if it is comparable at run time.

Not changed: a non-comparable value, the first argument, is still accepted.

## Changes Proposed

`MIN` and `MAX` reject a key whose type reports comparability `NONE`. `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY` and `MAX_BY` accept it. In the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`. So this query validates on `main`, and so do `ARG_MAX`, `MIN_BY` and `MAX_BY` (Spark library):

```sql
select arg_min(empno, home_address) from emp_address
```

The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions, added in CALCITE-5283. It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. It also discards the result of the operand-count check.

The motivating case is #5331, which adds a `VECTOR` type with comparability `NONE`. On that branch, `MIN(v)` and `ORDER BY v` fail at validation, but `ARG_MIN(x, v)` validates and then fails with `IllegalStateException: Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])`. This change makes the four functions reject the key at validation, as `MIN` and `MAX` do.

`OperandTypes.ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when the operand count is invalid, or when the key is not comparable and `throwOnFailure` is true. Otherwise it returns `false`. The operand-count check is no longer discarded. `SqlOperator.validateOperands` is unchanged. The error is the same one `MIN(home_address)` gives.

### Verification

`SqlValidatorTest.testArgMinMaxNonComparableKey` is new. It covers the four functions with a `NONE` key and checks the error text. It also checks that a non-comparable value, the first argument, is still accepted. Without this change the four statements validate, so the four `fails` assertions fail.

### Scope

Open question for the maintainer: should these four functions reject a key whose type reports `NONE`, as `MIN` and `MAX` do? The maintainer reports that all types are comparable in their implementation and in the Calcite runtime, and that this change would break them. The maintainer has not said which of their types report `NONE`.

Evidence on the runtime: on `main`, `ARG_MIN(x, v)` with `v` an `ARRAY` (comparability `ALL`) validates and then fails with `Unable to implement EnumerableAggregate`, while `MIN(v)` and `ORDER BY v` work on the same data.

Alternative: keep these functions permissive for `NONE` keys, and reject only `VECTOR` keys in #5331, as that PR already does for `ORDER BY`, `GROUP BY` and the other clauses. Under that alternative this PR closes.
