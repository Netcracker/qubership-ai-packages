I rewrote the 20 tests the last commit added to `WildcardTests.java` as 3 tests, one per rule. `WildcardTests` passes on the fixed code (49 tests). Production code is untouched and nothing is committed. I didn't run `./gradlew :nullaway:buildWithNullAway`, because only a test source changed.

The skill also points to a writing-style skill and a Javadoc skill, but neither is installed here, so the wording follows this file's own conventions. The repository's `CLAUDE.md` already describes how `CompilationTestHelper` reports mismatches, and nothing I found adds to it, so I'm not proposing any change there.

---

**Message for the author of the pull request**

I rewrote the tests in `WildcardTests.java` without touching the fix. The 20 single-case tests are now 3 tests, one per rule the change sets. Every input from the original tests is still there.

1. **`aTypeArgumentFailsANonNullWildcardRequirementOnlyWhenItMayBeNull`** covers a concrete requirement (`? extends Object`). Each method in the source is named for its partition:
   - **Reported:** a bound that admits null, a bound inherited from another variable, a wildcard actual `? extends T`, `@Nullable` at the use, and a variable declared in `@NullUnmarked` code.
   - **Not reported:** a non-null bound, `@NonNull` at the use, and the `? extends @Nullable Object` and `?` requirements.
2. **`aTypeArgumentFailsAWildcardBoundedByATypeVariableOnlyWhenItMayBeNullAndTheVariableMayNot`** covers a requirement that names a type variable:
   - **Reported:** `Box<T>` passed to `? extends @NonNull T`, `Box<S extends @Nullable T>` where `T` cannot be null, and `Box<@Nullable T>`.
   - **Not reported:** the same variable, `S extends T`, the inference case, and both captured-actual cases.
3. **`anOverrideMayNotReturnATypeArgumentThatMayBeNullWhereTheOverriddenOneMayNot`** covers the override path.

**Why.** Before, each silent test kept its own copy of the source, apart from the test that reports. Nothing kept the two copies alike, and the reader had to compare them line by line to find the one difference. Now each silent input sits in the same compilation as the inputs that do report, so the difference is one method signature. This follows the repository's stack line, which keeps one rule's cases in one source. The names now state the rule, not a single case.

**What I added.** Two inputs that check the report really depends on nullness:
- `nonNullAtTheUse(Box<@NonNull T>)` passed to `? extends @NonNull T`.
- A second override returning `List<@NonNull V>`.

Neither is reported, with or without the fix.

**How I checked it, with the production code reverted to the parent commit:**
- With the 7 markers for reports the fix adds removed, all 3 tests pass. So every input that is expected to stay silent, and the two `@Nullable`-at-the-use reports, already behaved that way before the fix.
- With any one of those 7 markers put back, its test fails.
- On the fixed code, all 3 tests pass.

**What I propose but didn't do.** Since `doTest()` stops at the first mismatch, a failure in a test with several cases shows only one of them. Fixing a regression may take a second run to see the next one. The repository's guidance accepts that until the test helper reports every mismatch.
