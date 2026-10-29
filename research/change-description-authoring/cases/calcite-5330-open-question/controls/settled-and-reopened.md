## Breaking changes

`ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` now reject at validation a key (the second argument) whose type reports a comparability other than `ALL`. Calcite's built-in types all report `ALL`, so this is not a breaking change for them. The change breaks only code that defines its own type with comparability `NONE` and uses that type as the key.

- A key whose type has comparability `NONE` validated in 1.42.0. It now fails the same way `MIN` fails on that type. For example, `select arg_min(empno, home_address) from emp_address` fails with `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`, and `ARG_MAX`, `MIN_BY`, and `MAX_BY` fail with the same message under their own names. A type used as the key must report comparability `ALL`.

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

These four functions require a comparable key, but the validator accepts a key whose type has comparability `NONE`. `MIN` and `MAX` already reject the same type through `ComparableOperandTypeChecker`. The cause is `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions since [CALCITE-5283](https://issues.apache.org/jira/browse/CALCITE-5283). It returns `false` for such a key but never throws, and `SqlOperator.validateOperands` ignores the returned value. The checker also discarded the result of the operand-count check.

Because validation passes, the query fails later with an internal error. On #5331, which adds a `VECTOR` type with comparability `NONE`, `MIN(v)` and `ORDER BY v` fail validation, but `ARG_MIN` gets through:

```sql
SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
                               --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

With this change, `ANY_COMPARABLE` honors `throwOnFailure` like the other operand type checkers. When the operand count is invalid or the key's comparability is not `ALL`, it throws `callBinding.newValidationSignatureError()` if `throwOnFailure` is true, and returns `false` otherwise. `SqlOperator.validateOperands` is unchanged.

Not changed:
The value (the first argument) still does not need to be comparable.
A key whose type reports `ALL` validates as before. This covers `ARRAY`, `MAP`, `MULTISET`, `ROW`, and the types created by `CREATE TYPE`.

### Verification

The new `SqlValidatorTest.testArgMinMaxNonComparableKey` fails on `main`, where all four queries validate. It uses the testkit's structured type `ADDRESS` (column `EMP_ADDRESS.HOME_ADDRESS`, comparability `NONE`) as the key for each function, and checks that `ADDRESS` is still accepted as the value.

The claim that built-in types are unaffected comes from the code. `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in core is in `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. In this repository, the only type constructed with `NONE` is the `ADDRESS` fixture.

### Scope

Are all types comparable at run time? That is still open.

A committer needs to decide one thing: should these functions reject a key with comparability `NONE` in 1.43.0? The maintainer wrote that in their implementation, and in the Calcite runtime, all types implement `Comparable`, so this change would break them. Two facts bear on the decision:

- A downstream type that reports `NONE` already fails `MIN` and `MAX` at validation.
- We don't know yet which downstream types are affected. I asked on 07:09 UTC and there is no answer yet.

If the functions should stay permissive, #5331 can reject only `VECTOR` keys, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses, and this pull request would be closed. Either this pull request merges before #5331, or #5331 adds that check itself.

This change leaves out a separate failure on `main`. `ARG_MIN(x, v)` with `v` an `ARRAY` (comparability `ALL`) validates and then fails with the same `Unable to implement EnumerableAggregate` error, even though `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. No Jira issue is filed for it yet.
