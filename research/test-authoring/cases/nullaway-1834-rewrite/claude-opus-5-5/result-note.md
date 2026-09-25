I rewrote the 21 tests that `d55c150` added to `WildcardTests.java` as 12 tests. I didn't touch production code and didn't commit. `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` and `./gradlew :nullaway:buildWithNullAway` both pass.

---

**Message for the PR author**

**What I changed in the tests**

I rewrote the 21 tests as 12. No expectation changed: every `// BUG: Diagnostic contains:` marker is still there, word for word. There are now two new inputs that expect no report, and one test is merged into another.

- **Each new report now sits in one source with the cases that must stay silent.** Before, a reported case and its silent counterpart were two tests with two copies of the class. A silent test only proves the rule while its twin fires on the same code, and nothing kept the two copies the same. Error Prone compiles all of them in one run, so they belong together:
  - A bound that admits null vs. one that doesn't, against `? extends Object`, `? extends @Nullable Object` and `?`.
  - A `@Nullable T` use vs. a `@NonNull T` use.
  - `@Nullable T` vs. bare `T`, against `? extends T`.
  - `S extends @Nullable T` vs. `S extends T`, against `? extends T`.
  - A bare `T` vs. `@NonNull T`, against `? extends @NonNull T`.
- **Four reported cases had no silent counterpart, so I added one each**, differing from the case in one respect:
  - A `@NullMarked` holder next to the `@NullUnmarked` one.
  - `<T, S extends T>` with a non-null `T`.
  - `Box<? extends T>` with a non-null `T`.
  - An override returning `List<@NonNull V>`.
- **Two inputs are new.**
  - `NullableT.nullableSub`: `S extends @Nullable T` where `T` itself admits null, which must be accepted. It turns red if `admitsNull(lhsBound) ||` is removed.
  - The `List<@NonNull V>` override control from the list above.
- **Each test still holds at most one input that expects a report.** I checked the harness source: `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` (error_prone_test_helpers 2.50.0, lines 264–268 and 288) stops at the first mismatch. It identifies the mismatch by line number only, whether a report is missing or unexpected, and there is no way to label a marker. That's why cases of different rules stay in separate tests. Examples:
  - The `@NullUnmarked` declaration and the `S extends T` chain are separate from the plain `@Nullable` bound.
  - The override is separate from the call-site checks.
- **Names now state the rule the test establishes.** For example, `aTypeVariableIsRejectedOnlyWhenItsBoundAdmitsNullAndTheWildcardBoundDoesNot` instead of the name of one input.
- **Unchanged:** `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariableUnderInference`, `aCapturedTypeArgumentMeetsANullnessAnnotatedTypeVariableRequirement` and `aCapturedTypeArgumentMeetsABareTypeVariableRequirement`. They guard against false reports in the inference and capture paths, and none of them has a case to pair with.

**Evidence**

- **Red on the base commit.** I ran the new tests against the production code of `HEAD~1`. Exactly the 7 tests whose report is new failed, each with `Did not see an error on line N matching <the expected diagnostic>`. The two tests whose report existed before the fix stayed green, as expected: `@Nullable T` against a non-null wildcard, and against `? extends T`.
- **Mutations of `extendsBoundContains`**, applied one at a time and reverted:
  - Removing `admitsNull(lhsBound) ||` fails the subtype-variable test.
  - Removing `!hasNullnessAnnotation` in `typeComparedForNullness` fails the use-site annotation test.
  - Removing the `CapturedType` exception fails only the existing `aCapturedTypeArgumentMeetsANullnessAnnotatedTypeVariableRequirement`. I had tried a direct `Box<? extends @NonNull T>` pass-through as a control, but it stayed green under that mutation, so I dropped it.

**What I propose and did not do**

- **A stack line in `AGENTS.md`/`CLAUDE.md`**, if the maintainers agree: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatched marker and names it by line number only, with no label.`
- **A follow-up against Error Prone:** an optional label on a `// BUG: Diagnostic contains:` marker that the failure message prints. Until then, a failing test here is identified by the test name plus a line number inside the embedded source. I couldn't search the Error Prone tracker for an existing issue because this session had no network access.
