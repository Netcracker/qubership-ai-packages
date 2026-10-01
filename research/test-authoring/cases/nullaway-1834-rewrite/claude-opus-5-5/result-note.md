I rewrote the 20 tests the last commit added to `WildcardTests.java` as 8. Every source input from those tests is kept, and I added three new silent controls. The production code is unchanged and nothing is committed.

**Checks run:**
- On the fix, `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` passes.
- With the pre-fix `nullaway/src/main` checked out, 7 of the 8 tests fail. Each fails on its case's own marker with `Did not see an error on line N matching <pattern>`. The 8th test, `aNullableWrittenOnATypeVariableUseFailsOnlyANonNullWildcard`, passes there as expected, because both its inputs already behaved that way before the fix.
- I did not run `buildWithNullAway`, since only a test file changed.

---

**Message for the PR author**

**What changed in the tests and why.**

The 20 tests split into 7 cases that fail on the base commit (the regressions) and 13 inputs that pass there (the controls). Each control was in a separate test from its case, and the silent ones had no reporting input next to them, so a silent test would stay green even if its source were broken. Error Prone's `CompilationTestHelper` stops at the first missing `// BUG:` marker, which I checked with a throwaway test that had two cases broken. So each test now holds one case together with its controls in one source, and each control differs from its case in one respect. The test names state the rule, plus the partition where one rule has several tests:

| Test | Case (fails on base) | Controls |
| --- | --- | --- |
| `aNonNullWildcardRejectsATypeVariableOnlyWhenItsDeclaredBoundAdmitsNull` | `<T extends @Nullable Object>` → `? extends Object` | `<T>`; `Box<@NonNull T>`; `? extends @Nullable Object`; `Box<?>` |
| `…DeclaredInUnannotatedCode` | `@NullUnmarked` holder | **new:** the same holder without `@NullUnmarked` |
| `…WhoseBoundAdmitsNullThroughAnotherVariable` | `S extends T` → `? extends Object` | the same `S` → `? extends T` |
| `aNonNullWildcardRejectsAWildcardBoundedBy…` | `Box<? extends T>`, T's bound admits null | **new:** the same with `<T>` |
| `aWildcardBoundedByATypeVariableRejectsAVariableWhoseBoundAddsNullable` | `S extends @Nullable T` → `? extends T` | `S extends T` |
| `aWildcardBoundedByANonNullUseOfATypeVariable…` | `Box<T>` → `? extends @NonNull T` | `return b` as `Box<? extends T>`; `Box<@Nullable T>` → `? extends T` (reports) |
| `anOverrideReturningATypeVariable…FailsANonNullUseOfIt` | override `List<V>` | **new:** override `List<@NonNull V>`; plus the Caffeine-shaped capture and inference inputs (`asyncLoad`, `asyncLoadAll`, a pass-through of a captured `Map`) |
| `aNullableWrittenOnATypeVariableUseFailsOnlyANonNullWildcard` | none (both inputs held on base) | `Box<@Nullable T>` → `? extends Object` reports; → `? extends @Nullable Object` is silent |

I put the capture and inference inputs next to the override case because I couldn't find a reporting control that differs from them in only one respect. The natural variants (capture of `? extends V` into `? extends @NonNull V`, or a lambda inferred into `CompletableFuture<? extends @NonNull V>`) are silent too.

**Proposed, not done:**
1. **Possible false negative.** Returning a captured `Map<? extends K, ? extends V>`, with `V extends @Nullable Object`, as `Map<? extends K, ? extends @NonNull V>` is not reported, either on the base or with the fix. This follows from the capture exception in the commit message. Worth either a test that documents it as a known gap or an issue.
2. **A test-stack line for `CLAUDE.md`**, for example: *"Tests: JUnit 4 engine, JUnit 4 assertions and Truth; checker tests use Error Prone `CompilationTestHelper`. One `doTest` stops at the first missing `// BUG: Diagnostic contains:` marker and names it by line and pattern. It names an unexpected diagnostic by line only and offers no label for a marker."* I didn't edit the file; it needs your agreement first.
3. **Label follow-up.** Because the harness gives a marker no label, a control that wrongly reports is named only by its line number. A follow-up would be an Error Prone issue asking for a per-marker label. I couldn't check their tracker for an existing one, since `gh` and the browser were off-limits.

The longest new method name goes over the line limit; the pre-commit formatter will wrap it the way it wrapped the original.
