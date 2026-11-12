I added four regression tests to `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. Each one fails on the commit before the fix and passes on it. `FrameworkTests` passes and `./gradlew :nullaway:buildWithNullAway` is clean. I didn't run the rest of `:nullaway:test`, and I didn't touch production code or commit anything.

**A suggestion for you, not for the PR:** `CLAUDE.md` could get a line saying how Error Prone's `CompilationTestHelper` reports failures, which I had to find out with a throwaway test. It stops at the first expected diagnostic it doesn't see. It names that one by line number and the expected text, and names an unexpected diagnostic by line number while listing every diagnostic it saw. Tell me if you want it added.

---

**Message for the author of #1750**

The fix to `containsNullSpELExpression` came with no tests, so I added four to `FrameworkTests`, next to `springValueFieldTest`:

- `springValueNullAfterNotEqualsIsNotAPossibleValue`: `someBean != null`
- `springValueNullAfterEqualsIsNotAPossibleValue`: `someBean == null`
- `springValueNullBeforeNotEqualsIsNotAPossibleValue`: `null != someBean`
- `springValueNullBeforeEqualsIsNotAPossibleValue`: `null == someBean`

These are the four forms that `NULL_COMPARISON_PATTERN` and the description list. Each test compiles two `@Value` fields:
- **The first field** uses `null` only as a comparison operand, so it must not be reported. On the commit before the fix, all four tests fail with `@NonNull field 'notReported' not initialized`, which is the false positive from the issue.
- **The second field** changes only one thing: the true branch of the ternary is `null`. It must still be reported, and it is reported both before and after the fix. This shows that removing the comparison doesn't hide a `null` that the expression can really return.

Error Prone's test helper stops at the first missing diagnostic and identifies it by line number. So each test holds one form plus its control rather than all four in one source, and a failure names the form in the test name.

The `@Value` stub that `springValueFieldTest` defined inline is now `addSpringValueAnnotationStub`, shared by the old test and the new ones. That test's expectations are unchanged. The new tests go through `checkOnlySecondValueFieldReported(notReported, reported)`, so each test is two SpEL strings on adjacent lines.

**Not done, for you to decide:**
- **`eq` / `ne`:** SpEL also has the word operators `eq` and `ne`. `#{someBean ne null ? someBean.value : 'default'}` is still a false positive, because the pattern only strips `==` and `!=`. I wrote no test that locks in the current behaviour there. If you extend the pattern, that case needs the same pair of tests.
- **No-space spelling:** I didn't test `someBean!=null`, even though the pattern allows for it with `\s*`. If you want a test for it, add one more pair using the same helper.
