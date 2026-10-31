I rewrote the 20 tests that `d55c150` added to `WildcardTests.java` as two tests, one per rule the fix enforces. Each test passes on the fix and fails on the code before it. `./gradlew :nullaway:buildWithNullAway` also passes. Production code is unchanged and nothing is committed.

**Message for the PR author:**

> The 20 one-case tests this PR adds become two, one per rule. The repository's test instructions keep the cases of one rule in one source and accept that `doTest()` currently stops at the first mismatch.
>
> 1. **`aTypeVariableIsJudgedByItsDeclaredBoundWhereAWildcardRequiresANonNullBound`**: an unannotated type variable passed where `Box<? extends Object>` is required is judged by its declared bound.
>    - **Cases now reported:**
>      - `T extends @Nullable Object`
>      - `S extends T` where `T` is that same variable
>      - `Box<? extends T>`
>      - a `T` declared in `@NullUnmarked` code
>    - **Controls:**
>      - `<T>` and `Box<@NonNull T>`, which stay silent
>      - `Box<@Nullable T>`, which was already reported
>      - the same actuals passed to `Box<? extends @Nullable Object>` and `Box<?>`, which stay silent
>
> 2. **`aWildcardBoundedByATypeVariableRejectsAnActualThatAdmitsNullWhereTheVariableDoesNot`**: where the requirement is `? extends T`, the types are compared as written, and an actual that may be null is rejected where `T` may not be.
>    - **Cases now reported:**
>      - `Box<S extends @Nullable T>` with a non-null `T`
>      - `Box<T>` passed to `Box<? extends @NonNull T>`
>      - the override returning `List<V>` against `List<? extends @NonNull V>`
>    - **Controls:**
>      - `Box<T>` and `Box<S extends T>`, which still pass
>      - `Box<@Nullable T>`, which was already reported
>      - the inference case through `CompletableFuture.supplyAsync`
>      - the two captured-type cases
>
>    A captured `? extends @NonNull V` stays silent, and the reporting `Box<T>` into `Box<? extends @NonNull T>` sits in the same source as its control.
>
> Every input from the original 20 tests is kept; the declarations are only renamed so that each method's name says which case it is. I checked the split against the base commit. With the old production code, each test fails on its first new case. With the seven new markers removed, both tests pass on the old code, so every other input really is a control.
>
> **Proposed, not done:** no test covers a type variable whose bound becomes nullable through a library model. `typeVariableUpperBound` handles that path, but only the `@Nullable` and `@NullUnmarked` routes are tested. A case for it would go into the first test.
