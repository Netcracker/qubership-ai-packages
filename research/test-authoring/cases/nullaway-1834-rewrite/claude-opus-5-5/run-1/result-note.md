I rewrote the 20 tests the last commit added to `WildcardTests.java` as 10. Every input from the original 20 is still there, and only that test file changed. `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` passes. I didn't run `:nullaway:buildWithNullAway`, since only test code changed. Nothing is committed.

**Message for the PR author:**

---

I reorganised the tests this PR adds to `WildcardTests`. The production change is untouched.

**What changed**

- **Each test that expects no report now shares a compilation with an input that does report.** Before, ten tests each checked one silent call in a source of their own, so nothing showed that their silence came from the rule rather than from the setup. Each silent call is now a separate method in the same source as the reported call it differs from in one respect. Grouped this way, the 20 inputs make 10 tests:
  - **Bound that admits null, concrete requirement.** `aTypeVariableFailsAWildcardRequirementOnlyWhenItMayBeNullAndTheWildcardBoundMayNot` puts the `T extends @Nullable Object` call to `takeNonNull` next to four silent calls: a non-null bound, a `@NonNull T` use, a `? extends @Nullable Object` requirement and a `Box<?>` requirement.
  - **`@Nullable T` use.** `aNullableWrittenOnATypeVariableUseFailsOnlyANonNullWildcardRequirement` holds the two calls that write `@Nullable T` at the use.
  - **Requirement bounded by a type variable (`? extends T`).** `aWildcardBoundedByATypeVariableRejectsOnlyANullableUseOfThatVariable` holds `Box<T>` returned as `Box<? extends T>`, `Box<S extends T>`, and the `CompletableFuture` inference case, with the `Box<@Nullable T>` report as their reporting control. These guard the "compare as written" branch.
  - **Non-null type variable in the requirement.** `aTypeVariableFailsAWildcardBoundedByANonNullTypeVariableOnlyWhenItsBoundAdmitsNull` puts `S extends @Nullable T` next to `S extends T`.
- **One test holds at most one input that is new behaviour.** I ran the PR's tests against the production code from before the fix. Seven fail there; the other 13 pass. The harness stops at the first missing diagnostic and names it only by line number. Two new cases in one compilation would therefore hide each other. Each of the seven stays in its own test, so a failure names it by test name. These four were already reported cases on their own, and I left them as they were: the unannotated-code bound, `S extends T extends @Nullable Object`, the `Box<? extends T>` actual, and the override. The `? extends @NonNull T` test also stays as it was.
- **The two capture tests now share one compilation**, as `aCapturedTypeArgumentMeetsATypeVariableRequirementThatAnUncapturedOneFails`. I added one input as their reporting control: a `Map<? extends K, V>` returned as `Map<? extends K, ? extends @NonNull V>`, which is reported. That shows the two silent calls are silent because of the capture exception. This input is also new behaviour: it fails on the pre-fix code and passes with the fix.

I re-ran the rewritten tests against the pre-fix code. Each of the eight tests holding a new case fails at that case's line. No control produced an unexpected report. The two tests that hold only existing behaviour pass there, as expected.

**Proposed, not done**

- **Possible missed report.** `Map<? extends K, ? extends V>` returned as `Map<? extends K, ? extends @NonNull V>` (with `V extends @Nullable Object`) is accepted. The same happens through `CompletableFuture.supplyAsync`. The capture exception in `extendsBoundContains` skips the `admitsNull` check, so map values that may be null pass as non-null. I didn't add a test for this, because its expected outcome is a decision about the production code. If you agree it should be reported, it belongs in the capture test as a second case.
- The `? extends @NonNull T` and override tests could each take a silent control: `Box<@NonNull T>` passed to `Box<? extends @NonNull T>`, and an override returning `List<@NonNull V>`. I checked that both are silent. They aren't required, since both tests already expect a report, so I left them out.

---
