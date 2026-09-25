Good — clean, no commit made, only the test file changed.

---

**Message for the PR author:**

The last commit (614efcf) changed `extendsBoundContains`/`typeComparedForNullness`/`admitsNull` in `CheckIdenticalNullabilityVisitor` and added `GenericsUtils.typeVariableUpperBound`, but shipped with no tests, so I added three to `WildcardTests.java` (the file already covering this exact unit — wildcard containment):

1. `extendsConcreteWildcardAcceptsBareTypeVariableActualOnlyWhenItsBoundIsNonNull` — the headline fix: a bare `Box<T>` with `T extends @Nullable Object` into a `Box<? extends Object>` parameter is now reported; a bare `Box<T>` with a non-null `T` stays accepted, as a control in the same input.
2. `extendsTypeVariableWildcardRejectsNullableBoundActualUnlessRequirementAdmitsNull` — the parametric branch (`? extends T` where `T` is itself a type variable): `Box<T>` into `Box<? extends T>` and `Box<S extends T>` into `Box<? extends T>` both stay accepted (guarding the two cases the commit message calls out by name as intentionally preserved); `Box<S extends @Nullable T>` into the same `Box<? extends T>` is newly reported.
3. `extendsAnnotatedNonNullTypeVariableWildcardRejectsNullableBoundActual` — a bare `Box<T>` (nullable-bound `T`) into an explicitly annotated `Box<? extends @NonNull T>` is now reported, while the same actual into the unannotated `Box<? extends T>` stays accepted as its control.

Each case/control pairing sits in one compilation, since I confirmed by breaking two markers on purpose that `CompilationTestHelper`'s `// BUG:` checking stops at the first mismatch and names a case only by line number — so each test holds at most one input that expects a report. I verified all three new tests fail with "no errors" on the base commit (614efcf's parent) by temporarily reverting just the two production files, running the tests, and restoring — confirming the failure is the bug's actual symptom (silence), not a typo. `./gradlew :nullaway:test` and `:nullaway:buildWithNullAway` both pass with the fix restored.

Proposals I did not act on:
- The repository has no stack line recording its test engine/assertion library in `AGENTS.md`/`CLAUDE.md`; worth adding one, e.g. `Tests: JUnit 4 engine; Error Prone's CompilationTestHelper for compiler-diagnostic assertions (stops at the first mismatched `// BUG:` marker per source, and names a case only by line number)`, so the next contributor doesn't have to rediscover that behavior.
- I did not add a test for the "captured actual" carve-out (`rhsTypeArgument instanceof Type.CapturedType`) mentioned in the diff's comments — it exists to avoid a false positive when capture conversion drops annotations, but constructing a deterministic repro that actually produces a `CapturedType` at that exact point felt too fragile to get right without deeper verification. Flagging it as a coverage gap rather than guessing.
