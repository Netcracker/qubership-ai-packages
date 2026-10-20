# Task

The author of the pull request below asks you to rewrite its description so that it reflects the discussion so far.
Give the new description in Markdown, ready to paste into GitHub. The facts come from the description, the diff, and
the discussion, which were checked against the code; treat every fact in them as verified, and add none that they do
not carry. The discussion is as of 2026-10-15 09:20 UTC: the maintainer has not replied to the author's last comment.

## Repository facts

- Repository: apache/calcite. Target branch: `main`. Its `gradle.properties` says `calcite.version=1.43.0`; the latest
  release tag is `calcite-1.42.0`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/main` prints
  `merge 0 squash 0 plain 40`. A committer rebases each pull request onto `main`.
- The pull request has one commit, whose message is the title. Jira issue: CALCITE-7858. The pull request is #5330.
- The pull request template is an HTML comment of contributing tips followed by two sections, `## Jira Link` and
  `## Changes Proposed`; the description below already uses them, with the comments removed.

## The description as the author wrote it

Title: `[CALCITE-7858] ARG_MIN, ARG_MAX, MIN_BY and MAX_BY should reject a non-comparable key`

````markdown
## Jira Link

[CALCITE-7858](https://issues.apache.org/jira/browse/CALCITE-7858)

## Changes Proposed
`ARG_MIN(value, key)`, `ARG_MAX(value, key)` and their aliases `MIN_BY` and `MAX_BY` require the key to be comparable, but the validator accepts a key whose type has comparability `NONE`. `MIN` and `MAX` already reject the same type.

To reproduce in `SqlValidatorTest`: in the test catalog, `EMP_ADDRESS.HOME_ADDRESS` has the structured type `ADDRESS`, whose comparability is `NONE`.

```sql
select arg_min(empno, home_address) from emp_address
```

On `main` this validates, and so do `ARG_MAX`, `MIN_BY` and `MAX_BY` (Spark library). With this change, they fail like `MIN(home_address)` does:

```
Cannot apply 'ARG_MIN' to arguments of type 'ARG_MIN(<INTEGER>, <>)'. Supported form(s): ARG_MIN(<ANY>, <COMPARABLE_TYPE>)
```

Cause: `OperandTypes.ANY_COMPARABLE`, the operand type checker of these functions (added in CALCITE-5283), returns `false` for a non-comparable key but never throws, and `SqlOperator.validateOperands` ignores the returned value. It also discards the result of the operand-count check.

Changes:

- `OperandTypes.ANY_COMPARABLE` throws `callBinding.newValidationSignatureError()` when the operand count is invalid or the key is not comparable and `throwOnFailure` is true; otherwise it returns `false`. `SqlOperator.validateOperands` is unchanged.
- `SqlValidatorTest.testArgMinMaxNonComparableKey` covers the four functions with a non-comparable key, and checks that a non-comparable value (the first argument) is still accepted.
````

## The diff

````diff
diff --git a/core/src/main/java/org/apache/calcite/sql/type/OperandTypes.java b/core/src/main/java/org/apache/calcite/sql/type/OperandTypes.java
index e36017ad30d9..a0cd7e6a4a67 100644
--- a/core/src/main/java/org/apache/calcite/sql/type/OperandTypes.java
+++ b/core/src/main/java/org/apache/calcite/sql/type/OperandTypes.java
@@ -1244,9 +1244,15 @@ public static SqlSingleOperandTypeChecker same(int operandCount,
       new SqlOperandTypeChecker() {
         @Override public boolean checkOperandTypes(SqlCallBinding callBinding,
             boolean throwOnFailure) {
-          getOperandCountRange().isValidCount(callBinding.getOperandCount());
-          RelDataType type = callBinding.getOperandType(1);
-          return type.getComparability() == RelDataTypeComparability.ALL;
+          if (getOperandCountRange().isValidCount(callBinding.getOperandCount())
+              && callBinding.getOperandType(1).getComparability()
+                  == RelDataTypeComparability.ALL) {
+            return true;
+          }
+          if (throwOnFailure) {
+            throw callBinding.newValidationSignatureError();
+          }
+          return false;
         }
 
         @Override public SqlOperandCountRange getOperandCountRange() {
diff --git a/core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java b/core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java
index 1ab392832d8d..59f7b1e8ad6f 100644
--- a/core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java
+++ b/core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java
@@ -10291,6 +10291,35 @@ void testGroupExpressionEquivalenceParams() {
     sql("SELECT ARG_MAX('b', 5) FROM emp").ok();
   }
 
+  /** Test case for
+   * <a href="https://issues.apache.org/jira/browse/CALCITE-7858">[CALCITE-7858]
+   * ARG_MIN, ARG_MAX, MIN_BY and MAX_BY should reject a non-comparable
+   * key</a>.
+   *
+   * <p>The type of column {@code HOME_ADDRESS} is a structured type whose
+   * comparability is {@code NONE}. */
+  @Test void testArgMinMaxNonComparableKey() {
+    final String expected = "Cannot apply '%s' to arguments of type "
+        + "'%s\\(<INTEGER>, <>\\)'\\. "
+        + "Supported form\\(s\\): %s\\(<ANY>, <COMPARABLE_TYPE>\\)";
+    sql("select ^arg_min(empno, home_address)^ from emp_address")
+        .fails(String.format(Locale.ROOT, expected, "ARG_MIN", "ARG_MIN", "ARG_MIN"));
+    sql("select ^arg_max(empno, home_address)^ from emp_address")
+        .fails(String.format(Locale.ROOT, expected, "ARG_MAX", "ARG_MAX", "ARG_MAX"));
+    sql("select ^max_by(empno, home_address)^ from emp_address")
+        .withOperatorTable(operatorTableFor(SqlLibrary.SPARK))
+        .fails(String.format(Locale.ROOT, expected, "MAX_BY", "MAX_BY", "MAX_BY"));
+    sql("select ^min_by(empno, home_address)^ from emp_address")
+        .withOperatorTable(operatorTableFor(SqlLibrary.SPARK))
+        .fails(String.format(Locale.ROOT, expected, "MIN_BY", "MIN_BY", "MIN_BY"));
+
+    // The value (the first argument) need not be comparable
+    sql("select arg_min(home_address, empno) from emp_address").ok();
+    sql("select max_by(home_address, empno) from emp_address")
+        .withOperatorTable(operatorTableFor(SqlLibrary.SPARK))
+        .ok();
+  }
+
   @Test void testModeFunction() {
     sql("select MODE(sal) from emp").ok();
     sql("select MODE(sal) over (order by empno) from emp").ok();
````

## The discussion

The maintainer (a committer), 2026-10-15 07:02 UTC:

> I made a comment in Jira.
> In our implementation, and in the Calcite runtime, all types implement Comparable.
> This would be a breaking change for us.

The maintainer's comment in Jira: "I believe that in the Calcite runtime all types are really comparable."

The author, 07:09 UTC:

> Thanks for looking at this so quick. As far as I can tell, the change only affects types that explicitly declare comparability `NONE`, and Calcite's built-in types never do.
>
> `RelDataTypeImpl.getComparability()` returns `ALL`, and the only override in core is `ObjectSqlType`, which returns the comparability it was constructed with (`SingleColumnAliasRelDataType` just delegates). So `ARRAY`, `MAP`, `MULTISET`, `ROW` and the types created by `CREATE TYPE` all report `ALL`, and `ARG_MIN` / `ARG_MAX` / `MIN_BY` / `MAX_BY` on them validate exactly as before. In this repository the only type constructed with `NONE` is the testkit's `ADDRESS` fixture, which is what the new test uses.
>
> For a type that does declare `NONE`, `MIN` and `MAX` already reject it at validation, through `ComparableOperandTypeChecker`. This PR only makes the four `ARG_*` / `*_BY` functions consistent with them, and makes `ANY_COMPARABLE` honour `throwOnFailure` like the other checkers.
>
> Which of your types would be affected? If one of them reports `NONE` but is comparable at run time, I would expect `MIN` on it to fail today as well. If you would rather keep `ARG_MIN` permissive for such types, I am happy to close this.

The maintainer, 07:15 UTC: "I will review this tomorrow."

The author, 09:19 UTC:

> Thanks. Some context for you on why I filed this PR.
>
> #5331 adds a `VECTOR` type whose comparability is `NONE`, since embeddings have no meaningful order. On that branch, without this fix:
>
> ```sql
> SELECT MIN(v) FROM t;          -- validation error: Cannot apply 'MIN' to arguments of type 'MIN(<VECTOR(2, REAL)>)'
> SELECT x FROM t ORDER BY v;    -- validation error: Values of type 'VECTOR(2, REAL)' are not comparable
> SELECT ARG_MIN(x, v) FROM t;   -- validates, then fails with IllegalStateException:
>                                --   Unable to implement EnumerableAggregate(group=[{}], A=[ARG_MIN($0, $1)])
> ```
>
> So `VECTOR` would be the first built-in type that reports `NONE`, and `ARG_MIN` / `ARG_MAX` / `MIN_BY` / `MAX_BY` are the only places where that is not enforced; the user gets an internal error instead of a validation error. This PR is what makes them consistent. It changes nothing for types that report `ALL`, which includes every other built-in type.
>
> > all types are comparable at run time
>
> for these functions that is not quite true on the Enumerable convention today. On `main`, `ARG_MIN(x, v)` with `v` an `ARRAY` (comparability `ALL`) validates and then fails with the same "Unable to implement EnumerableAggregate", although `MIN(v)` and `ORDER BY v` work on the same data. `ArgMinMaxImplementor` compares non-primitive keys with `SqlFunctions.ltNullable(Comparable, Comparable)`, and an array is a `java.util.List`. That is a separate issue, which I can file, but it shows that validation is where the key's comparability has to be decided.
>
> If you still prefer to keep these functions permissive, I can instead reject only `VECTOR` keys inside #5331, as it already does for `ORDER BY`, `GROUP BY` and the other clauses, and close this PR.
