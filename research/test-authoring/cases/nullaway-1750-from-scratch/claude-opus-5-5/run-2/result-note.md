I added five regression tests for the `SpringHandler` fix in `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. All five fail on the pre-fix code and pass with it. The full `:nullaway:test` suite and `:nullaway:buildWithNullAway` both pass. I didn't touch production code and didn't commit.

**A suggestion for you, not for the PR:** `CLAUDE.md` could record a fact about the test harness that I had to find out by running a deliberately broken test. Error Prone's `CompilationTestHelper` stops at the first mismatch in a compilation and names it by line number, not by content. If you agree, I'll add that line.

---

**Message for the PR author**

I added five regression tests for the `@Value` SpEL fix, next to `springValueFieldTest` in `FrameworkTests`. Each test compiles one class with two fields:

- **The case:** an expression where `null` appears only in a comparison, so the field must not be reported.
- **Its control:** the same expression with `null` as one branch of the ternary, so the field is still reported as not initialized.

The control shows that the silent field is silent because of the comparison, not because of how the test is set up. Each test checks one way of writing the comparison, one per form your Javadoc lists, plus spacing:

| Test | Case | Control |
| --- | --- | --- |
| `springValueSpelNullRightOfNotEqualsIsNotAResult` | `someBean != null ? someBean.value : 'default'` | `someBean != null ? null : 'default'` |
| `springValueSpelNullRightOfEqualsIsNotAResult` | `someBean == null ? 'default' : someBean.value` | `someBean == null ? null : someBean.value` |
| `springValueSpelNullLeftOfNotEqualsIsNotAResult` | `null != someBean ? …` | `null != someBean ? null : …` |
| `springValueSpelNullLeftOfEqualsIsNotAResult` | `null == someBean ? …` | `null == someBean ? null : …` |
| `springValueSpelNullComparedWithoutSpacesIsNotAResult` | `someBean!=null ? …` | `someBean!=null ? null : …` |

- **Why one test per form:** the test harness stops at the first mismatch in a compilation and reports only its line number. If all five cases were in one compilation, the first failure would hide the others.
- **Seen failing without the fix:** I put the previous `SpringHandler.java` back temporarily and ran the tests. All five failed with `Saw unexpected error on line 5`, which is the false positive on the silent field. They pass with your fix.
- **Shared stub:** the five tests and `springValueFieldTest` now build the `@Value` annotation stub through one helper, `addSpringValueAnnotationStub`. The expectations in `springValueFieldTest` are unchanged.

**Proposed, not done:** SpEL also has word operators, `eq` and `ne`. From reading the new pattern, which only matches `==` and `!=`, `#{someBean ne null ? someBean.value : 'default'}` would still be a false positive. I didn't run it, and I added no test because the fix doesn't claim to handle these. If you want them covered, it would mean changing the pattern plus one more case-and-control test like the ones above.
