I rewrote the 20 tests the commit added as 10 tests. Every input they had is still there, and I added 9 new silent inputs, each a near variant of a reporting one. Production code is untouched and nothing is committed.

Results:
- **The full suite passes:** `./gradlew :nullaway:test` ran 1109 tests with 0 failures, and `./gradlew :nullaway:buildWithNullAway` passes.
- **On the base commit:** with the production code from `HEAD~1`, exactly 7 tests fail, each with "Did not see an error on line N" and nothing reported anywhere else. So none of the new inputs moved the old behaviour.
- **The other 3 tests** pass on the base commit. I mutated the production code once for each of them, and each mutant made its test fail.

One suggestion for you, not for the PR: `CLAUDE.md` has no line naming the test stack. I could add one saying the tests run on JUnit 4 and Error Prone's `CompilationTestHelper`, and that one compilation stops at the first missing diagnostic (naming it by line) but lists every diagnostic it produced. I didn't edit the file, so say if you want it.

I couldn't load the English style and Javadoc skills the test skill points to, because neither is installed here. Wording follows the file's existing style.

---

**Message for the PR author**

I regrouped the tests this PR adds to `WildcardTests.java` from 20 methods into 10. Every input from the original tests is still there. I ran the new tests against the production code from both this PR and its parent.

**Why fewer tests.** Each method had a single input, so a test that expected no diagnostic proved nothing alone: it would pass just as well if the source were set up wrong. Now each test pairs the input this PR starts reporting with near variants that differ in one respect and stay silent. The name states that rule. I checked how `CompilationTestHelper` reports with a throwaway test. One compilation stops at the first missing `// BUG` diagnostic and names it only by line number, but it lists every diagnostic produced. So each test holds exactly one expected-diagnostic input, plus any number of silent ones.

**The new tests, and which old tests they absorb:**
1. `aTypeVariableFailsANonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull`: the `T extends @Nullable Object` case, plus the old `<T>`, `? extends @Nullable Object` and `Box<?>` tests.
2. `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcard`: adds a `@NullMarked` holder that stays silent.
3. `aTypeVariableFailsANonNullWildcardWhenTheVariableItExtendsAdmitsNull`: adds `<T, S extends T>`, which stays silent.
4. `aWildcardBoundedByATypeVariableFailsANonNullWildcardWhenThatBoundAdmitsNull`: adds `<T> Box<? extends T>`, which stays silent.
5. `aNullnessAnnotationOnATypeVariableUseDecidesOverItsDeclaredBound`: the `@NonNull T` and both `@Nullable T` tests, plus `Box<@Nullable T>` with a nullable bound.
6. `aTypeVariableMeetsAWildcardBoundedByItselfUnlessItsUseIsNullable`: the "same type variable" test, its inference variant (now a nested `Loader` interface), and the `@Nullable T` into `? extends T` test.
7. `aTypeVariableFailsAWildcardBoundedByTheVariableItExtendsOnlyWhenItAloneAdmitsNull`: the `S extends @Nullable T` case and both `S extends T` tests, plus `S extends @Nullable T` under a nullable `T`, which stays silent.
8. `aTypeVariableThatMayBeNullFailsAWildcardBoundedByItsNonNullUse`: adds `Box<@NonNull T>`, which stays silent.
9. `aCapturedTypeArgumentIsComparedToATypeVariableRequirementAsWritten`: both captured-argument tests in one interface. It adds `passNullable()`, which returns a captured `? extends @Nullable V` and is reported both with and without this PR.
10. `anOverrideReturningATypeVariableThatMayBeNullFailsANonNullProjection`: adds an override returning `List<@NonNull V>`, which stays silent.

**Evidence.**
- With the parent commit's production code, tests 1–4, 7, 8 and 10 fail, each with "Did not see an error on line N … There were no errors". So every new silent input was already silent before this PR.
- Tests 5, 6 and 9 pass on the parent commit. Each fails under one mutant of `CheckIdenticalNullabilityVisitor`:
  - Dropping `!hasNullnessAnnotation` from `typeComparedForNullness` fails test 5.
  - Disabling the `lhsBound instanceof Type.TypeVar` branch fails tests 6, 7 and 9.
  - Dropping the `CapturedType` exemption fails test 9.
- `:nullaway:test` and `:nullaway:buildWithNullAway` pass.

**Proposed, not done.** The comment on the capture exemption says capture conversion drops type-use annotations. In test 9, though, a captured `? extends @Nullable V` keeps its `@Nullable`; the report prints `capture of ? extends @Nullable V`. Only `@NonNull` seems to be lost. You may want to narrow that comment. I didn't change the production code.
