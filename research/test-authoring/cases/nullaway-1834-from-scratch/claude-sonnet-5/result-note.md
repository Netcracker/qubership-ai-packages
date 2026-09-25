The diff is clean: only test additions, no production code touched, nothing committed.

---

**Message for the PR author:**

I added three tests to `WildcardTests.java` for the containment fix in `CheckIdenticalNullabilityVisitor#extendsBoundContains`, per `test-authoring`:

1. **`extendsWildcardWithConcreteBoundRejectsTypeVariableActualWithNullableBound`** — covers the two `? extends <concrete>` examples from the commit message: a bare type-variable actual whose declared bound admits null (reported) vs. one with a non-null bound (control, unchanged), plus the same nullable-bound rule reached through a wildcard-wrapped actual (`Box<? extends T>`) — a distinct branch in `extendsBoundContains` (`rhsWildcard != null`) that was equally silent before the fix.
2. **`extendsWildcardWithTypeVariableBoundComparesActualAsWritten`** — covers the parametric-requirement branch (`lhsBound instanceof TypeVar`): `Box<T>` and `Box<S extends T>` stay assignable to `Box<? extends T>` (the behavior the fix is explicitly designed to preserve), while `Box<S extends @Nullable T>` is now rejected. The three share one `Box` declaration, differing by one bound each, as the twin/control the changed line reached.
3. **`extendsWildcardWithNonNullAnnotatedTypeVariableBoundRejectsNullableBoundActual`** — same branch, but with the annotation on the *requirement* side (`Box<? extends @NonNull T>`), exercising `hasNullnessAnnotation`'s other disjunct (own annotation vs. bound-derived nullness), i.e. the fourth commit example.

All three were verified red on the parent commit (`09fdea5`) and green on the fix — I temporarily reverted just the two production files, ran the new tests, confirmed all three failed, then restored the fix. `./gradlew :nullaway:test` (full module) and `:nullaway:buildWithNullAway` both pass.

**What I did not add, and why:** the commit also carves out an exception for a `Type.CapturedType` actual ("capture conversion drops type-use annotations..."). I tried three different ways to construct a captured `? extends @NonNull V` actual that reaches that branch (a generic-method-argument capture, a return-type substitution capture, and a real JLS 5.1.10 member-access capture via a `self()`-returning method) — all three did produce a genuine `Type.CapturedType` at that call site, confirmed via a temporary debug print, but in every case the `@NonNull` annotation survived capture intact, so removing the `rhsTypeArgument instanceof Type.CapturedType` disjunct didn't flip any of them to a false positive. I couldn't identify what actually triggers the annotation loss the comment describes (possibly something specific to bytecode-read symbols, given the similar `correspondingTypeVariable`/#1732 workaround elsewhere in this file) within reasonable effort, so I left it uncovered rather than ship a test that doesn't fail when the exception is removed. Worth a follow-up if you have a concrete repro in mind.

Also, per the skill: this repository's `AGENTS.md`/`CLAUDE.md` names no test stack, so I'm proposing it here rather than editing those files myself — worth adding a line such as: *"Tests: JUnit 4 engine; Error Prone `CompilationTestHelper` for NullAway diagnostics (reports every `// BUG: Diagnostic contains:` in a source, each named only by its line, not a harness-assigned label)."*
