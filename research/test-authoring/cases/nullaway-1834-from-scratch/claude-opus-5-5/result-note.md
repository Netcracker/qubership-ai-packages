I added seven tests to `WildcardTests.java`, the only file I changed. Production code is untouched and nothing is committed. All seven pass, the full `:nullaway:test` suite passes, and `:nullaway:buildWithNullAway` passes.

---

**To the author of "Report a type argument whose bound admits null where a non-null wildcard is required"**

These are small tests (compile-only, through `CompilationTestHelper`), placed beside the other wildcard containment tests in `WildcardTests`. Each test holds one reported case plus silent controls that differ from it in one respect and are silent on the base commit too.

| Test | Case it reports | Controls (silent) |
| --- | --- | --- |
| `typeVariableArgumentIsRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>` with `T extends @Nullable Object` passed to `Box<? extends Object>` | bound `T extends Object`; use written as `Box<@NonNull T>`; requirement `? extends @Nullable Object` |
| `wildcardArgumentIsRejectedByNonNullWildcardWhenItsTypeVariableBoundAdmitsNull` | `Box<? extends T>` with the same `T` | the same with `T extends Object` |
| `typeVariableArgumentIsRejectedByNonNullWildcardWhenDeclaredInUnmarkedCode` | `T` declared on a `@NullUnmarked` class | `U` declared on a `@NullMarked` method |
| `typeVariableArgumentIsRejectedByParametricWildcardOnlyWhenItAdmitsNullAndTheRequirementDoesNot` | `Box<S>` with `S extends @Nullable T` passed to `Box<? extends T>` | `S extends T`; `Box<T>` itself; the same `S` where `T` itself may be null |
| `typeVariableArgumentIsRejectedByNonNullTypeVariableWildcardOnlyWhenItAdmitsNull` | `Box<T>` passed to `Box<? extends @NonNull T>` | `Box<@NonNull T>`; `Box<T>` passed to `Box<? extends T>` |
| `overrideReturningTypeVariableArgumentIsRejectedWhereOverriddenReturnsNonNullWildcard` | the override case from the changelog | an override returning `List<@NonNull V>` |
| `nullableTypeVariableUseIsRejectedByParametricWildcard` | `Box<@Nullable T>` passed to `Box<? extends T>` | `Box<T>` |

**Evidence:**
- **Red on the base commit.** I ran the tests against the two production files from `HEAD~1`. The first six fail, each with `Did not see an error on line N matching … There were no errors.`, which is the silence the commit describes. The last one passes there, by design: it guards the report the commit says it keeps.
- **Mutants.** I tried five hand-made mutants, run against all of `WildcardTests`. Four were killed:
  - substituting `T`'s declared bound for the requirement kills the `Box<@Nullable T>` test;
  - removing the `admitsNull` clause kills four of the new tests;
  - ignoring the annotation written at the use site kills the `@NonNull T` control;
  - reading only an explicit `@Nullable` in `typeVariableUpperBound` kills the unmarked-code test and four existing tests.

  That last result is also why the `wildcardUpperBound` refactoring needs no new test.

**About the test harness:** I probed it by breaking three lines in one test. A single `doTest()` stops at the first mismatch. It names a missing marker by line number and expected text, and an unexpected warning by line number and the printed source line. That is why each test holds one case. It is also why every call line uses its own argument name (`takeNonNull(nonNullBoundBox)`): an unexpected warning then shows which line it came from.

**Proposed, not done:**
1. **The captured-actual exception (`rhsTypeArgument instanceof Type.CapturedType`) is an unresolved survivor.** With that check removed, the full `:nullaway` suite (1108 tests) still passes. None of the shapes I tried produced a captured actual at this check: a parameter, a call result, a local, a return, `var`, or `List`/`Supplier` element access. Please either add the input that motivated this check as a test, or say why it is needed. I removed the test I first wrote for it because it never reached the check.
2. **The warning prints `Box<? extends T>` for a `Box<? extends @NonNull T>` requirement.** The message then reads "`Test.Box<T>` cannot be converted to `Test.Box<? extends T>`", which looks self-contradictory. Two of the tests match only up to `Box<? extends` so that they don't pin this wording.
3. **The library-model path is untested.** That is `onOverrideMethodTypeVariableUpperBound` / `onOverrideClassTypeVariableUpperBound` feeding `typeVariableUpperBound`, reached through this check. Testing it needs a test library model in another module, so I left it out.
4. **A stack line for `AGENTS.md`** (which `CLAUDE.md` links to). I did not edit the file:
   `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers as the assertion harness — one doTest() stops at the first mismatch, naming a missing marker by line and expected text and an unexpected diagnostic by line and source line.`
