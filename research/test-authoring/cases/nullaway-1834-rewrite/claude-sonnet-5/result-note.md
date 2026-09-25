Only the test file is touched, uncommitted, as requested.

---

## Message for the PR author

I read `CompilationTestHelper`'s and `DiagnosticTestHelper`'s sources (from the `error_prone_test_helpers` sources jar) to establish a fact the skill required before touching anything: each `// BUG:`-marked or silent line is checked by its own `assertWithMessage(...).isTrue()` call inside a loop, so **the harness stops at the first mismatching line and, beyond that, names a case only by its line number inside the embedded source** — it has no per-case label. That's the same shape the file's pre-existing tests already used (e.g. `simpleWildcardNoInference` packs a `testNegative`/`testPositive` pair into one compiled source), so this commit's new tests should follow it too instead of standing one-behavior-per-file.

What I changed, and why:

- **Merged four case+control pairs that duplicated a long setup to assert one rule apiece**, following the file's own established idiom of packing a failing case and its nearest passing control into one compiled source:
  - `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + `aTypeVariableWithANonNullBoundMeetsANonNullWildcardRequirement` + `aTypeVariableWhoseBoundAdmitsNullMeetsANullableWildcardRequirement` → one test, `aBareTypeVariableFailsANonNullWildcardRequirementOnlyWhenItsDeclaredBoundAdmitsNull`, whose three methods vary exactly one condition each (the declared bound, then the wildcard's own bound) against the same `Box`/`takeNonNull`/`takeNullable` declarations.
  - `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` + `aNullableWrittenOnATypeVariableUseMeetsANullableWildcardRequirement` + `aNonNullWrittenOnATypeVariableUseMeetsANonNullWildcardRequirement` → `anExplicitAnnotationOnATypeVariableUseIsComparedAsWrittenRegardlessOfItsDeclaredBound`.
  - `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends` + `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` → `aWildcardBoundedByATypeVariableAcceptsABareVariableBoundedByItButRejectsAnExplicitlyNullableUse` (identical `Holder`/`takeExtendsT` scaffold; only the test method's parameter differed).
  - `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + `aTypeVariableThatAdmitsNoNullMeetsAWildcardBoundedByOneThatDoesNot` → `aTypeVariableBoundedByAnotherFailsAWildcardBoundedByThatVariableOnlyWhenItsOwnBoundAdmitsNull` (a one-token diff: `<S extends @Nullable T>` vs. `<S extends T>`).

  Each merged test's name now states the rule the case and its controls establish together, per the skill's naming rule for that shape (`aLocalIsReportedOnlyWhenNothingReadsIt`-style), and each control sits beside the case it controls instead of repeating the `Box`/target-method declarations in a separate file.

- **Left the other ten new tests as their own tests**, unmerged: they either assert a genuinely different rule (unannotated-code declaration, transitively-bounded variable, capture conversion, override widening, wildcard-typed actual) or exercise a different compiler code path (direct assignment vs. lambda-based target-type inference) from their nearest neighbor, so packing them together would have hidden one behind another under a check that stops at the first mismatch.

What I propose and did not do:

- **A stack line for `AGENTS.md`**, since none exists for this test's harness: *"Tests: JUnit 4 engine; `CompilationTestHelper` (Error Prone) as the domain-specific harness for diagnostic tests — one compiled-source call stops at the first mismatching line and names a case only by that line number, not a label."* I didn't add it myself; the skill has me propose it and wait for agreement before editing a repository instructions file.
- **The missing per-case label is a real limitation** of `CompilationTestHelper` (confirmed by reading its source, not guessed): a reader of a failing `WildcardTests` run sees only a line number inside the embedded `Test.java`, never a case name. No fix belongs in this PR — it would be a request to the `error_prone_test_helpers` project, and this file already lived with the limitation before this commit — but it's worth naming as a known gap rather than silently repeating it forever.
- **I did not add any new test inputs.** A few passing-only tests (`aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable`, its inference variant, the unbounded-wildcard test, and both captured-type-argument tests) have no same-file failing sibling to prove the checker isn't just silent by construction on that setup; I left them as-is rather than inventing new failing cases outside the scope of reorganizing what this commit already added, but a reviewer could reasonably ask for one.
