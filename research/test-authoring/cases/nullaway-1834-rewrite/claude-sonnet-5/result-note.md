## Summary for the author

I rewrote only the 20 tests this commit added to `WildcardTests.java`, per `test-authoring`. Production code is untouched; `:nullaway:test`, `spotlessJavaCheck`, and `buildWithNullAway` all pass.

**Why reshape them at all.** `CompilationTestHelper` (confirmed from its bytecode, `assertHasDiagnosticOnAllMatchingLines`) reads a source line by line and fails immediately — via a bare Truth `.isTrue()` inside the loop — on the first line whose `// BUG:` marker (or absence of one) doesn't match, naming it by line number only, no label. That's exactly the harness the skill's own worked example ("A case and its control in one act," §7) describes. Two consequences followed:

- A test may bundle a **case with its one-respect controls** in one source (same convention already used elsewhere in this file, e.g. `wildcardCaptureParameters`), because a control failing just means the case's setup was wrong.
- It must **not** bundle two independent cases that aren't control pairs of each other, since the first failure would mask the second — so most of the 20 stayed as their own test.

**What changed, concretely:**
- Merged `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` with the three tests that each differed from it in exactly one respect (bound non-null, required wildcard nullable, explicit `@NonNull` override) into one test, `aTypeVariableMeetsAWildcardRequirementAccordingToItsEffectiveNullness`, stating the rule the four methods establish together.
- Merged the `@Nullable`-written-on-a-type-variable-use pair (fails vs. nonnull requirement / meets vs. nullable requirement) into `aNullableWrittenOnATypeVariableUseIsComparedAsWritten` — their original names already signaled they were a pair.
- Merged `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` and its one-respect PASS counterpart into `aTypeVariableMeetsAWildcardBoundedByAnotherTypeVariableOnlyWhenItTooDoesNotAdmitNull`.
- The other 11 tests (unannotated-code bound, transitively-bounded actuals, inference/capture variants, the override-widening case, etc.) don't have a clean one-respect partner among the 20 without inventing new scenarios, so I left them as individually named, focused tests — renaming none of them, since their original names already read as rule statements rather than locations.

Net: 20 tests → 15, same coverage, no new scenarios invented.

**What I propose and didn't do:**
- The repo's `AGENTS.md`/`CLAUDE.md` names no test stack (JUnit 4 engine + `CompilationTestHelper`'s own `// BUG:` convention for assertions). Per the skill, I'm proposing one line for it rather than adding it myself: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper for assertions (stops at the first line mismatch, names it by line number only, offers no per-case label).` Worth adding to `AGENTS.md`/`CLAUDE.md` if you agree.
- `aCapturedTypeArgumentMeetsABareTypeVariableRequirement` looks weak to me: `pass()` returns `loadAll()` with an *identical* declared return type, so no capture conversion or interesting comparison actually happens — I can't name a plausible production change that would fail it. I left it alone since pruning coverage wasn't asked for, but flagging it for your judgment.
- `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement`, `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement`, and `aWildcardActualBoundedByATypeVariableThatAdmitsNullFailsANonNullWildcardRequirement` are reporting-only with no silent control nearby; the skill only mandates a control for a *silent* case, so I left these as is rather than fabricate matching negative scenarios not present in the original commit.
