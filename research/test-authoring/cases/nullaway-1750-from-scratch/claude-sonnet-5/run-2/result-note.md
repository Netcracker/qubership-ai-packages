Only the test file changed, as required. Here's the message I'd leave for the PR author:

---

I added the tests this change owes. `SpringHandler`'s `CompilationTestHelper`-based harness stops at the first mismatched line rather than reporting every mismatch (verified empirically), so I didn't fold these into the existing `springValueFieldTest` act — that test already holds cases of its own, and a second independent case sharing its act could mask a failure. Instead:

- **`springValueFieldNullUsedOnlyAsComparisonOperandIsNotFlagged`** — regresion-tests the PR's own motivating example, `#{someBean != null ? someBean.value : 'default'}` (no diagnostic expected), paired with a control in the same class, `#{someBean != null ? null : 'default'}` (diagnostic still expected), which shows the fix doesn't swallow expressions that can actually produce `null`.
- **`springValueFieldNullOnLeftOfComparisonOperatorIsNotFlagged`** — same shape, but exercises the regex's other alternative, `null != someBean`, since `NULL_COMPARISON_PATTERN` has one alternative for "null after the operator" and one for "null before it" — genuinely separate branches, not redundant values.
- Extracted the inline `Value.java` annotation stub out of `springValueFieldTest` into a shared `addSpringValueAnnotationStub` helper so the two new tests don't duplicate it, leaving `springValueFieldTest`'s existing cases and expectations unchanged.

Both new tests were confirmed red on the pre-fix commit (failing with the exact false-positive symptom — `@NonNull field 'comparedToNull' not initialized` — on the line the bug affects) and green after the fix, in a throwaway worktree I removed afterward. `springValueFieldTest` was unaffected on the base commit, confirming it isn't a test this change needed to move.

What I didn't add: a case for the `==` operator (`== null` / `null ==`). It's matched by the same regex alternative and character class as `!=` (`[!=]=`), just a different literal character, not a separate code path, so I judged it a redundant equivalence-class value rather than a distinct partition. Happy to add it if you'd rather have explicit coverage of the exact four forms named in the Javadoc.
