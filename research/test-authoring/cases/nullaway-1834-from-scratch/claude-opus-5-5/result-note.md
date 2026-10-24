I added six regression tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, just above `makeHelper()`. Production code is unchanged, nothing is committed, and `:nullaway:test` (1105 tests, 0 failures) and `:nullaway:buildWithNullAway --rerun` both pass. One branch of the fix, the captured-type exception, still has no test: I couldn't write an input that reaches it.

**Message for the author**

The fix had no tests, and the only symptom of the bug was silence: nothing was reported. I added six tests that each put a call that should now be reported next to similar calls that should stay silent. All six fail on `HEAD~1` with `Did not see an error on line N … There were no errors.` I checked that by putting the base commit's `nullaway/src/main` in place temporarily, then restoring it. All the silent calls were already silent on the base commit.

They are small tests: each compiles one source in the same process with `CompilationTestHelper`, like the rest of the file. That harness stops at the first wrong marker and names it only by line number, so each test holds one reported case and the silent calls beside it.

| Test | Reported | Silent beside it |
|---|---|---|
| `typeVariableActualIsJudgedByItsBoundAgainstNonNullExtendsWildcard` | `Box<T>` with `T extends @Nullable Object` passed as `Box<? extends Object>` | `T` with a non-null bound; the same value passed as `Box<? extends @Nullable Object>`; `Box<@NonNull T>` |
| `wildcardActualBoundedByTypeVariableIsJudgedByThatVariablesBound` | `Box<? extends T>`, nullable-bound `T`, passed as `Box<? extends Object>` | the same with a non-null bound |
| `typeVariableDeclaredInUnmarkedCodeIsNotContainedByNonNullExtendsWildcard` | `T` declared in a `@NullUnmarked` class | the same class marked |
| `typeVariableWhoseBoundAdmitsNullIsNotContainedByExtendsOfNonNullTypeVariable` | `Box<S>`, `S extends @Nullable T`, passed as `Box<? extends T>` | `S extends T`; `Box<T>`; a nullable-bound `T` |
| `typeVariableWhoseBoundAdmitsNullIsNotContainedByExtendsOfNonNullUse` | `Box<T>` passed as `Box<? extends @NonNull T>` | `Box<@NonNull T>`; a non-null-bound `T` |
| `overrideReturningTypeVariableWithNullableBoundMismatchesNonNullExtendsWildcard` | the override case from the changelog: `List<V>` overriding `List<? extends @NonNull V>` | an override returning `List<@NonNull V>` |

To check the silent calls aren't just filler, I made small temporary edits to the production code, one at a time, and restored each:
- **Dropping `admitsNull(lhsBound)`** fails the type-variable-requirement test.
- **Ignoring `@NonNull` in `hasNullnessAnnotation`** fails the first test, the `@NonNull T` test and the override test.
- **Reading only an explicit `@Nullable` in `typeVariableUpperBound`** fails only the unmarked-code test among the new ones.

**Not done, proposed:**

1. **The captured-type exception (`rhsTypeArgument instanceof Type.CapturedType`) is unresolved.** Replacing it with `false` leaves `:nullaway:test` and `buildWithNullAway` green. About 20 candidate sources didn't reach it either: argument passing, returns, `var`, field and method access through a `Holder<? extends @NonNull V>`, `id(box)`, `Collections.unmodifiable*`, `Optional.filter`. I removed the test I had written for it, because it passed with or without the clause. Please share the input that showed the false report so it can become a test, or say whether the clause can go.
2. **The message drops `@NonNull`.** A `Box<T>` passed to `Box<? extends @NonNull T>` prints `Box<T> cannot be converted to Box<? extends T>`, and the override test prints `List<? extends V>`, which a user can't act on. For those two cases the tests match only the text up to `? extends`, so they don't lock in the current wording.
3. **Partitions not covered:**
   - a bound made nullable by a library model (`onOverride…TypeVariableUpperBound`), which needs a model on the test classpath;
   - an unbounded `Foo<?>` requirement over a non-null-bound class, which also goes through `extendsBoundContains`.
4. **A testing line for `AGENTS.md`** (I didn't edit it): `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers, which stops at the first mismatch and names it by line number (with the expected text for a missing one), with no per-marker label.` I learned these facts by deliberately breaking two markers in a scratch test. A follow-up would be an Error Prone issue asking for per-marker labels or a report of every mismatch. I couldn't check their tracker without `gh` or a browser, so that needs checking before anyone files it.
