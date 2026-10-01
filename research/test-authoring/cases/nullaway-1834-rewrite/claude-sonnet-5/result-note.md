The diff looks clean and consistent. The tests build and pass. Now I'll write the message to leave for the PR author.

---

**Message for the author:**

I rewrote the 20 tests this commit added in `WildcardTests.java` into 14, applying the `test-authoring` skill. Production code is unchanged. All tests pass, plus the full `:nullaway:test` suite and `buildWithNullAway`.

**What changed and why**

The key fact driving the restructuring: `CompilationTestHelper.doTest()` reports *every* mismatch in one act (I confirmed this by decompiling `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` — it builds the full list of unmatched-expected and unexpected-actual lines and asserts both empty via Truth, rather than stopping at the first mismatch), but it names each mismatch only *by line position*, not by content. Per the skill's §7 principle 1, that means one test (one `doTest()` call) may hold one case together with its controls, but two independent cases need two separate tests — merging unrelated cases into one source would still be *caught* on a regression, but the failure would no longer read as a named scenario.

Applying that, plus §7 principle 3 ("a silent case stands with a control that reports"):

- Many of the original tests were solitary "meets" (no `// BUG:`) assertions with no reporting counterpart in the same source, which can't distinguish "the rule holds" from "the setup never exercised the check." I paired each with the minimal control that flips the one relevant respect (bound vs. no bound, annotated vs. bare, S extends T vs. S extends `@Nullable` T, etc.) and merged them into one test with two or three small methods, consistent with the file's own pre-existing convention (`simpleWildcardNoInference` already does this).
- The `#1/#2/#3/#8` group (whether a nullable-admitting-bound type variable meets a non-null wildcard, a nullable wildcard, or an unbounded wildcard) collapsed into one decision-table test, `aTypeVariableFailsAWildcardRequirementOnlyWhenItsBoundAdmitsNullAndTheWildcardDoesNot`, since they're one rule viewed through three destination wildcards.
- Several pairs that weren't adjacent in the original diff turned out to be exact one-respect controls of each other once I worked out the specification (e.g. the original "non-null written on a use" silent test is the control for the original "bound admits null" failing test, and vice versa) — I rewired those pairings rather than keep the original, looser grouping.
- Names now state the rule and its partition (`aSubtypesOwnBoundDecidesWhetherItMeetsAWildcardBoundedByTheVariableItExtends`, `aTypeVariableIsRejectedOnlyWhenTheBoundItTransitivelyExtendsAdmitsNull`, etc.) instead of joining two inputs with "and"/restating the scenario in two near-identical test names.

**What I left alone, and why (judgment calls, not verified by a run beyond "it still passes")**

- `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariableUnderInference`, `aCapturedTypeArgumentMeetsANullnessAnnotatedTypeVariableRequirement`, and `aCapturedTypeArgumentMeetsABareTypeVariableRequirement` are silent-only with no control in the same act. Each is a narrow regression test for a specific inference/capture-conversion interaction (javac capture printing `? extends V` instead of `? extends @NonNull V`), and any control I could construct would exercise a different inference path rather than flip one respect of that exact scenario — so I left them standalone rather than invent a control that tests something else. Worth a second look if you disagree.
- `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported` is reporting-only (fine without a control under §7 principle 3, which only constrains silent cases), but it exercises a different diagnostic ("mismatched type parameter nullability") than the rest of the file's "incompatible types" diagnostic — I kept it as-is since it's presumably covering the override-check call site of the factored-out `GenericsUtils.typeVariableUpperBound`, but I didn't verify that from the production diff in depth.
- No repository-wide stack line names JUnit4/CompilationTestHelper in `CLAUDE.md`/`AGENTS.md`. Per the skill's §0, I propose adding one, e.g.: *"Tests: JUnit 4 engine, Error Prone `CompilationTestHelper` for compiler-diagnostic assertions (reports every `// BUG:` mismatch on a source per `doTest()` call, named by line position, not content)."* I didn't add it myself since the skill asks to propose, not write, into `CLAUDE.md`/`AGENTS.md` without agreement.
