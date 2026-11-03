Only the test file is changed, as requested, and nothing is committed.

---

Message for the PR author:

I rewrote the 20 tests this commit added to `WildcardTests.java`, per the `test-authoring` skill. Production code is untouched; nothing is committed.

**What I found and fixed**

The harness here is error-prone's `CompilationTestHelper`. I checked empirically (deliberately broke two markers in an existing test and read the report) that it **stops at the first mismatch** rather than reporting every mismatch in a compilation. That matters because several of the new tests put a passing ("control") scenario in its own `@Test`/source, duplicating the `Box`/`take*` boilerplate from the *failing* ("case") scenario next to it, differing in only one line (bound, annotation, or wildcard shape). That's exactly the "two cases that share a long setup" anti-pattern the skill flags: the two copies aren't guaranteed to stay comparable, and a reader has to diff two bodies to see what matters.

I merged each such case with its one-line-different controls into a single test/source (one `.doTest()` act), the same pattern already used elsewhere in this file (e.g. `wildcardCheckingForReturnsAndAssignments`). Since the harness stops at the first mismatch, I kept exactly one `// BUG:`-expecting scenario per act and added only non-reporting controls alongside it — never two reporting cases in the same source. This took the file from 20 tests down to 13, with every original input preserved (no coverage dropped), just regrouped.

I also added small inline controls to a few tests that were previously bug-only with no nearby passing counterpart (`aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement`, `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement`, `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement`, `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported`, the wildcard-actual test), so each isolates the one condition it's about.

**Verification I ran**

I checked out `GenericsUtils.java`/`CheckIdenticalNullabilityVisitor.java` from the parent commit (pre-fix) with the rewritten tests on top, and confirmed the same 7 tests go red as before the rewrite, each failing with "there were no errors" on the exact line that should report — i.e. merging didn't mask or weaken any regression signal. I then restored the fix and confirmed all tests pass, `:nullaway:test` is green, and `:nullaway:buildWithNullAway` passes.

One thing worth knowing: two of the original 20 (`aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` and `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable`, now merged as cases into two of the 13) already pass on the **pre-fix** code — they test that an explicit `@Nullable`/`@NonNull` written directly on a use is honored, which wasn't broken by this bug. They're legitimate coverage of adjacent, unchanged behavior (and the commit message calls this out explicitly), just not themselves evidence for this particular fix; I kept them as controls rather than dropping them.

**What I didn't do:** I didn't touch the untouched standalone tests (`aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable[UnderInference]`, the two captured-type-argument tests) — they're legitimate stand-alone regression guards for distinct syntactic triggers (return-position assignment, type inference, capture conversion), matching plenty of existing single-purpose tests already in this file, so merging them further seemed more likely to obscure than clarify. If you'd rather also fold those into neighboring groups, say so and I'll do it, but I think they read better on their own.
