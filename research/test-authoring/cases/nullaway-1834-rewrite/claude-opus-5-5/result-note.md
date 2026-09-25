I rewrote the 20 tests the commit added as 12. Only `WildcardTests.java` changed; production code is untouched and nothing is committed. All 58 tests in `WildcardTests` pass on the fix, and `:nullaway:buildWithNullAway` passes.

Here is the message I'd leave for the author:

---

**Tests for "Report a type argument whose bound admits null where a non-null wildcard is required"**

**What I changed.** Most of the 20 new tests were one case each: either a call that must be reported or a call that must stay silent. The silent tests used their own copy of the source, and nothing kept that copy the same as the reporting one. A silent test only shows the rule holds while the reporting case fires on the same code. So each reporting case now shares one source with its controls: the nearest inputs that differ in one respect and must stay silent. Each test is named for the rule the cases establish together:

| Test | Case | Controls (silent) |
| --- | --- | --- |
| `aTypeVariableFailsAWildcardRequirementOnlyWhenItMayBeNullAndTheWildcardBoundMayNot` | `<T extends @Nullable Object> Box<T>` passed to `Box<? extends Object>` | `<T>` bound; `Box<@NonNull T>`; a `? extends @Nullable Object` requirement; a `Box<?>` requirement |
| `…OnlyWhenDeclaredInNullUnmarkedCode` | `T` of a `@NullUnmarked` holder | **new:** the same holder with `@NullMarked` |
| `…OnlyWhenTheVariableItExtendsAdmitsNull` | `S extends T`, where `T extends @Nullable Object` | **new:** `<T, S extends T>` |
| `aWildcardBoundedByATypeVariable…OnlyWhenTheVariableAdmitsNull` | `Box<? extends T>`, where `T extends @Nullable Object` | **new:** `<T>` |
| `aNullableTypeVariableUse…OnlyWhenTheWildcardBoundIsNonNull` | `Box<@Nullable T>` passed to `Box<? extends Object>` | a nullable requirement |
| `aTypeVariableUse…OnlyWhenItIsWrittenNullable` | `Box<@Nullable T>` passed to `Box<? extends T>` | `Box<T>` returned as `Box<? extends T>`; `<S extends T> Box<S>` |
| `…OnlyWhenItsBoundAddsNullable` | `<S extends @Nullable T>` passed to `Box<? extends T>` | `<S extends T>` |
| `…BoundedByItsNonNullUseOnlyWhenItMayBeNull` | `Box<T>` passed to `Box<? extends @NonNull T>` | **new:** `Box<@NonNull T>` |
| `anOverrideReturnType…OnlyWhenItsTypeArgumentMayBeNull` | an override returning `List<V>` | **new:** an override returning `List<@NonNull V>` |

- **The four new controls.** Four reporting cases had no silent neighbor. Without one, nothing showed that the condition named in the test is what triggers the report, so I added one to each.
- **Unchanged.** The three inference and capture tests (`…UnderInference` and the two `aCapturedTypeArgument…` tests) expect no report and have nothing to pair with, so I left them as they were.
- **Every original input is kept.** One changed shape: the `Box<T>` returned as `Box<? extends T>` now uses the holder's class-level `T` instead of a method-level one.

**Why each reporting case has its own test.** Error Prone's `CompilationTestHelper` stops at the first mismatch, whether a missing `// BUG` marker or an unexpected diagnostic, and names it only by line number. I found this in the source, not a failing run: `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` in 2.50.0, around lines 223–291. Two reporting cases in one source would therefore hide each other, so each test holds exactly one input that expects a report.

**Red on the base commit.** I ran the rewritten file against the production code of `HEAD~1`:
- The 7 tests whose case this change moves fail, each with `Did not see an error on line N matching …` at its own marker, not a compile error.
- The 2 tests whose report already existed before the fix pass: the `@Nullable T` use against `? extends Object` and against `? extends T`.

**Proposed, not done:**
1. **A stack line for `AGENTS.md`/`CLAUDE.md`**, which currently name no test stack: *"Tests: JUnit 4 engine, JUnit 4 assertions; checker tests use Error Prone's `CompilationTestHelper`, which stops at the first mismatched `// BUG: Diagnostic contains:` marker or unexpected diagnostic and names it only by line number."* It would save the next writer from looking this up again.
2. **A label for `// BUG` markers.** The report shows only the test name and a line number, so a reader needs the file open to see which case failed. The fix would be an issue against Error Prone asking for a label the report prints. I couldn't check their tracker for an existing one, since I had no gh or browser.
3. **A missing case.** `typeVariableUpperBound` also treats a bound as nullable when a library model says so, but no test sends a type variable whose bound comes from a library model to a `? extends Object` requirement. That route is untested for this change; a test using a handler/library-model fixture would cover it.
