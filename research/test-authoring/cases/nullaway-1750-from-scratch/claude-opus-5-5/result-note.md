I added four regression tests to `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. All four fail on the commit before the fix and pass on it. I didn't touch production code and didn't commit. `./gradlew :nullaway:test --tests "com.uber.nullaway.FrameworkTests"` and `./gradlew :nullaway:buildWithNullAway` both pass.

**Message for the author of #1750**

The fix shipped with no test, so I added four small tests through the NullAway checker, next to `springValueFieldTest`. Each test compiles one class with two `@Value` fields:
- **The case:** a SpEL expression where `null` is only compared against, which must not be reported.
- **Its control:** the same expression except that one branch returns `null`, which must still be reported.

The two expressions differ in one place only, so a test can't pass just because the setup is wrong.

| Test | Case (not reported) | Control (still reported) |
| --- | --- | --- |
| `springValueNullAfterNotEqualsIsNotAPossibleValue` | `#{bean != null ? bean.name : 'default'}` | `#{bean != null ? null : 'default'}` |
| `springValueNullAfterEqualsIsNotAPossibleValue` | `#{bean == null ? 'default' : bean.name}` | `#{bean == null ? null : bean.name}` |
| `springValueNullBeforeComparisonOperatorIsNotAPossibleValue` | `#{null != bean ? bean.name : 'default'}` | `#{null != bean ? null : 'default'}` |
| `springValueNullComparisonWithoutWhitespaceIsNotAPossibleValue` | `#{bean!=null?bean.name:'default'}` | `#{bean!=null?null:'default'}` |

The cases cover the forms your new pattern handles: `null` after `!=` and after `==`, `null` before the operator, and no spaces around the operator.

- **Evidence the tests catch the bug:** I ran them against the code from before the fix, in a temporary worktree. All four failed with `Saw unexpected error on line 5 … @NonNull field 'checked' not initialized`, which is the false positive this PR fixes. The controls report on both versions.
- **Why four tests and not one:** I checked the test harness by breaking two expectations on purpose. `CompilationTestHelper.doTest()` stops at the first mismatch and points to it by line number, so if all cases shared one class, a failure in one would hide the others. One case per test means each failure shows up under its own name.
- **Shared setup:** I moved the `@Value` annotation stub into a helper, `addSpringValueAnnotationStub`. `springValueFieldTest` now uses it too, with its expectations unchanged.
- **Only small tests:** the behavior can be seen through one compilation, and nothing here crosses a process boundary, so a larger test would add nothing.

**Suggested, not done:**
- **The fix misses SpEL's word operators.** SpEL also writes the comparisons as `eq` and `ne`, and the new pattern only removes `==` and `!=`. So `@Value("#{bean ne null ? bean.name : 'default'}")` is still a false positive. I didn't add a test for it because it would fail. If you extend the pattern, add a test like the ones above.
- **A line for the repo's instructions.** `AGENTS.md`/`CLAUDE.md` don't say which test libraries the repo uses. I suggest adding: `Tests: JUnit 4 engine, JUnit 4 assertions; checker tests use Error Prone's CompilationTestHelper, whose doTest() stops at the first mismatch and names it by line number.` I didn't edit the file; that's for a maintainer to agree to.
