## Breaking changes

`ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` now reject a key whose type reports comparability `NONE`. In 1.42.0 such a query passes validation. No built-in type in core reports `NONE`, so this affects only types that an application constructs with it, such as an `ObjectSqlType`. `MIN` and `MAX` already reject these types.

- `ARG_MIN(value, key)`, `ARG_MAX(value, key)`, `MIN_BY(value, key)`, and `MAX_BY(value, key)` with a key of comparability `NONE` passed validation in 1.42.0. They now fail validation with `Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)`, where the arguments are an `INTEGER` value and an `ADDRESS` key. If the key type is comparable at run time, make it report comparability `ALL`. `MIN` and `MAX` already need that.

## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed

`ARG_MIN(value, key)`, `ARG_MAX(value, key)`, and their aliases `MIN_BY` and `MAX_BY` require a comparable key. However, the validator accepts a key whose type has comparability `NONE`, and `MIN` and `MAX` reject that same type. In the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`:

```sql
select min(home_address) from emp_address;            -- fails validation
select arg_min(empno, home_address) from emp_address; -- passes validation on main
```

Because validation accepts the key, the first check comes during execution. #5331 adds a `VECTOR` type whose comparability is `NONE`. On that branch, `MIN(v)` and `ORDER BY v` fail validation. `ARG_MIN(x, v)` passes validation and then fails with an `IllegalStateException`:

```text
Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
```

The four functions use the operand type checker `OperandTypes.ANY_COMPARABLE`, added in [CALCITE-5283](https://issues.apache.org/jira/browse/CALCITE-5283). It returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. The checker also discarded the result of the operand-count check. With this change, `ANY_COMPARABLE` honors `throwOnFailure` like the other operand type checkers. `SqlOperator.validateOperands` is unchanged.

Not changed: the value (the first argument) still doesn't need to be comparable.
Not changed: keys of types that report `ALL` pass validation as before. That includes `ARRAY`, `MAP`, `MULTISET`, `ROW`, and types created by `CREATE TYPE`.

The cases in `testArgMinMaxNonComparableKey` that use a non-comparable value also pass on `main`. They check that the value is still accepted.

**Scope.** This needs a maintainer's decision. The review comment says that Calcite's runtime, and the reviewer's own implementation, treat all types as comparable, and that this change would break them. The choice is between two options:

- Reject non-comparable keys in these four functions, which is this pull request.
- Keep the functions permissive and close this pull request. #5331 would then reject `VECTOR` keys itself, as it already does for `ORDER BY`, `GROUP BY`, and the other clauses.

The evidence:

- `RelDataTypeImpl.getComparability()` returns `ALL`. The only override in core is `ObjectSqlType`, which returns the comparability it was constructed with, and `SingleColumnAliasRelDataType` delegates. In this repository, the only type constructed with `NONE` is the testkit's `ADDRESS` fixture.
- Comparable keys don't always run either. On `main`, `ARG_MIN(x, v)` with an `ARRAY` key passes validation and then fails with the same "Unable to implement EnumerableAggregate" error, while `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That failure is outside this change and has no Jira issue yet.
