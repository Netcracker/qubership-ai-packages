All green, formatted, and uncommitted as requested.

---

**Message for the PR author:**

I rewrote the 20 tests this commit added to `WildcardTests.java` per the `test-authoring` skill, without touching production code. Didn't commit, per your instructions.

**What changed and why:**

Most of the new tests were lone assertions — either a `// BUG` case with no sibling showing the same setup *passing*, or a passing case with no sibling showing it *failing* — so none of them proved the check discriminates on the condition its name claims. The file's own established idiom (`simpleWildcardNoInference`, `wildcardCaptureParameters`, etc.) is to put a case and its one-respect-different control as sibling methods inside one compiled source, and I followed that instead of introducing a new shape.

I consolidated 20 tests into 13, merging only where tests were already minimal-diff case/control pairs for the same rule (e.g. "bound admits null" vs. "bound excludes null" against the same `takeNonNull` requirement), and added the missing control where none existed (7 of the 13 tests needed one). Concretely:
- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + `aTypeVariableWithANonNullBoundMeetsANonNullWildcardRequirement` + the nullable/unbounded-requirement tests merged into one decision table over bound-nullness × requirement-kind.
- The `@Nullable`/`@NonNull`-at-use-site tests merged similarly, since they're the same rule with the annotation as the varying input.
- `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable` (silent-only) got a new failing control (`Box<@Nullable T>` into the same `Box<? extends T>`) — I verified the exact diagnostic text by compiling it, since this is the one genuinely new assertion I added.
- The unannotated-code, chained-bound, "extends-T" wildcard, and `@NonNull`-wildcard-bound tests each got a sibling showing the opposite outcome from a minimally different input.
- The override-widening test got a sibling showing the non-widening override is accepted.

I left three tests standalone with no added control: the two captured-actual tests and the inference-based `Box<? extends T>` test. Each is a distinct real-world shape (CompletableFuture/supplyAsync wrapping, a bare pass-through) that the commit message specifically calls out as the exception the fix had to avoid breaking; a contrived failing counterpart for them would test something the specification doesn't define, so I didn't add one.

Ran `:nullaway:test --tests WildcardTests`, the full `:nullaway:test`, and `:nullaway:buildWithNullAway` — all pass. Also ran `spotlessApply` since I hand-wrote the Java and one line exceeded the column limit; re-ran tests after, still green.

**What I didn't do:** I didn't verify "red on the base commit" for any of these (that's a property of the original fix's tests, which I preserved the diagnostic text of exactly); I also didn't check whether a mutation run on `CheckIdenticalNullabilityVisitor`/`GenericsUtils` would surface a gap the new controls don't cover — worth running if you have the mutation tooling wired up for this module.
