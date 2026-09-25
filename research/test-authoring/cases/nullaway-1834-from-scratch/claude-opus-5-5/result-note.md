I added seven tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. I didn't run them, because you asked for no build. So none has been seen passing on the fix or failing on the base commit, and the diagnostic text in each marker comes from reading the error-reporting code rather than from compiler output. Production code is unchanged and nothing is committed.

---

**Message for the author of the pull request**

This fix changes what NullAway reports: code that compiled clean before can now fail, and the commit had no test showing that. I added seven tests to `WildcardTests.java`, next to the existing containment tests. They are small tests: each compiles one source file in memory with `CompilationTestHelper`.

The harness stops at the first marker that doesn't match, and it identifies a failure only by line number (Error Prone 2.50.0, `DiagnosticTestHelper.java:223-292`). So each test covers one rule. It holds one case that should be reported, plus the nearest inputs that should not be, all in one source. This matches the shape the neighbouring tests already use.

| Test | Reported case | Controls that stay silent |
| --- | --- | --- |
| `aTypeVariableIsContainedByANonNullExtendsWildcardOnlyWhenItsBoundExcludesNull` | `Box<N>` with `N extends @Nullable Object` → `Box<? extends Object>` | `Box<M>` with a non-null bound; `Box<@NonNull N>`; target `Box<? extends @Nullable Object>` |
| `aWildcardBoundedByATypeVariable…` | `Box<? extends N>` → `Box<? extends Object>` | `Box<? extends M>`; `Box<? extends @NonNull N>` |
| `aTypeVariableDeclaredInUnmarkedCode…` | a type variable from a `@NullUnmarked` class, used in marked code | the same shape, declared in marked code |
| `aTypeVariableWhoseBoundAdmitsNullIsRejectedByAWildcardOverATypeVariableThatExcludesNull` | `Box<S>` with `S extends @Nullable T` → `Box<? extends T>`, where `T` can't be null | `Box<T>` and `Box<R extends T>`; the same `Box<S>` where `T extends @Nullable Object` |
| `aNullableUseIsRejectedByAWildcardOverTheSameTypeVariable…` | `Box<@Nullable T>` → `Box<? extends T>`, where `T extends @Nullable Object` | `Box<T>` |
| `aTypeVariableWhoseBoundAdmitsNullIsRejectedByAWildcardOverItsNonNullUse` | `Box<T>` → `Box<? extends @NonNull T>` | `Box<@NonNull T>` |
| `anOverrideReturningATypeVariable…` | an override returning `Box<V>` where the overridden method returns `Box<? extends @NonNull V>` | an override returning `Box<@NonNull V>` |

Why these seven:
- **Tests 1–3:** these cover the main rule, one test per kind of actual. Test 1 uses a plain type variable, test 2 a wildcard bounded by one, and test 3 a type variable whose bound admits null only because it's declared in unannotated code (the rule now in `typeVariableUpperBound`).
- **Tests 4–5:** these guard the rule that a requirement naming a type variable is compared as written. Test 5 would fail if someone replaced the required type variable with its bound, which the commit message says would hide the `Box<@Nullable T>` report.
- **Tests 6–7:** these cover the `@NonNull T` requirement through assignment and through the override check. The changelog entry promises the override case.

No existing test's expectation changed.

**What you need to do:**
- **Run the tests on the fix and on `09fdea5`.** Put the failing output from the base commit in the PR. On the base commit tests 1, 2, 3, 4, 6 and 7 should fail at their reported case. Test 5 guards existing behaviour, so it should pass there too. If a marker's message text is wrong (for example how `@NonNull T` is printed), the fix is to the marker text, not to what the test expects to be reported.
- **Add a line to `CLAUDE.md` describing the test stack**, something like: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatched "// BUG: Diagnostic contains:" marker and names it only by line number.` I didn't edit the file.

**Proposed, not done:**
- **The captured-type exception.** The special case for a captured `? extends @NonNull V` has no test. Only a method-call result produces a captured type here, and how NullAway's own inference rewrites that type can only be settled by running the code. A silent case I haven't watched would prove nothing. The test would pass a `Box<? extends @NonNull V>` through a generic identity call into `Box<? extends @NonNull V>` (it should stay silent), next to `Box<V>` (it should be reported).
- **A bound set by a library model.** Where a library model says a type variable's bound admits null, a type-variable actual isn't tested. It needs the library-model setup in `test-library-models`.
- **Labels for markers.** The harness has no way to label a `// BUG:` marker, so a failure is identified only by its line number. That limitation could be raised as an issue with Error Prone, after checking its tracker for an existing report. I didn't file anything.
