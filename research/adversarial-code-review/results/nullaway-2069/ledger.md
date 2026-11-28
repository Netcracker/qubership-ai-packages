# Review ledger: Accept `? extends T` and enhanced-for reads of type `T` where `T` is expected

https://github.com/uber/NullAway/pull/2069 · revision fc9b07b300d87a64e0aad111585942be8c0bdaba

Result: REQUEST_CHANGES (1 major, 21 minor, 12 nit)
Axes run: measurements, intent-scope, correctness, compatibility, performance, architecture, simplicity, least-surprise, change-reach, tests, comments, vocabulary, naive-reader, docs-pages, change-description, branch-hygiene; skipped: security (The change touches no trust boundary, input handling, secrets, or dependencies.), reliability (The change touches no timeouts, retries, limits, logs, or metrics.); failed: none

## Findings without a class

### F1 [major] Boolean contract antecedent still compares the null-tested value with NULL by equality (correctness, change-reach)

`nullaway/src/main/java/com/uber/nullaway/handlers/contract/ContractHandler.java:391-392` (outside the diff) · Confidence: high

- Problem: The change moved NullEqualityVisitor (lines 528, 531) from `Nullness.NULL.equals(...)` to `isNull()`, but the boolean-antecedent path still checks `antecedentNullness.equals(targetNullness)` with antecedentNullness `NULL`. Inside `if (v == null)` a wildcard read `v` is now `NULL_NO_CHANGE` instead of `NULL`, so for `f(null == v, w)` with `@Contract("true, null -> false")` the satisfied first argument is no longer skipped, the clause sees two unknown arguments, is dropped as unsupported, and `w` is not refined. Master refined `w`; the head reports a dereference of `w` in the then-branch, while the same code with a plain `@Nullable Object v` is still accepted.
  - fact: Probe correctness-probes/CorrectnessProbeTests.java, method contractNullFirstInsideNullTest: on head it reports `Test.java:13: dereferenced expression 'w' is @Nullable` (the wildcard variant) and nothing at line 19 (the plain `@Nullable Object v` variant) (correctness-probes/head-results.xml); on base 13392cb8 the method passes with no diagnostic (correctness-probes/base-results.xml).
  - fact: ContractHandler.java:391-392: `Nullness targetNullness = inputs.valueOfSubNode(nullTestTarget);` / `if (antecedentNullness.equals(targetNullness)) {`; antecedentNullness is only ever `Nullness.NULL` or `Nullness.NONNULL` (lines 386-390).
  - fact: The change rewrote the sibling tests at ContractHandler.java:528 and 531 to `if (lhsNullness.isNull())` / `if (rhsNullness.isNull())`.
  - fact: AccessPathNullnessPropagation.java:543-546 sets the equal branch of `v == null` to `leftVal.greatestLowerBound(...)`, which for a NO_CHANGE `v` and NULL is NULL_NO_CHANGE; `Nullness.isNull()` is true for NULL and NULL_NO_CHANGE.
- Proposed solution: At ContractHandler.java:392 compare by meaning: treat the argument as satisfied when `antecedentNullness == NULL ? targetNullness.isNull() : targetNullness == NONNULL`, as lines 528 and 531 already do for the null comparison, and add the `f(null == v, w)` case with a wildcard-read `v` inside `if (v == null)` to the contract tests, expecting no report.

### F7 [minor] Breaking-changes note names no replacement for getReceiverFields(NULLABLE) and getAccessPathsWithValue(NULLABLE) (change-reach)

no line · Confidence: high

- Problem: The description's Breaking changes section names three caller patterns that miss a NO_CHANGE value: `== NULLABLE`, `getReceiverFields(NULLABLE)`, and `getAccessPathsWithValue(NULLABLE)`. Its remedy, "test may be null with `NullabilityUtil.nullnessToBool` or `!= NONNULL`, and is null with `isNull()`", applies only to a comparison the caller writes; both store methods take one `Nullness` value and match it with `equals`, and the predicate overload of `getReceiverFields` that the change adds is private. A handler author who calls either method has no step to follow, and the same holds for a caller of `getAccessPathsWithValue(NULL)`, which now misses NULL_NO_CHANGE.
  - fact: discussion.md:7: "a call to `getReceiverFields(NULLABLE)` or `getAccessPathsWithValue(NULLABLE)`, misses a `NO_CHANGE` value once `HandleWildcardGenerics` is on: test \"may be null\" with `NullabilityUtil.nullnessToBool` or `!= NONNULL`, and \"is null\" with `isNull()`."
  - fact: NullnessStore.java:144-151 `public Set<AccessPath> getAccessPathsWithValue(Nullness value)` keeps entries where `value.equals(entry.getValue())`; NullnessStore.java:375-376 `public Set<Element> getReceiverFields(Nullness nullness) { return getReceiverFields(nullness::equals); }`; NullnessStore.java:385 `private Set<Element> getReceiverFields(Predicate<Nullness> predicate)`.
- Proposed solution: Give the two store methods a step in the note: either say that a caller queries each of NULLABLE, NO_CHANGE (and NULL with NULL_NO_CHANGE for "is null") and unions the results, or make the predicate overload of `getReceiverFields` public, add one for access paths, and point the note at them with `NullabilityUtil::nullnessToBool` and `Nullness::isNull`.

### F19 [minor] memberType: unexplained capture(skipTypeVars(t)) for non-DeclaredType sites (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/TypeSubstitutionUtils.java:100` · Confidence: high

- Problem: The maintainer asks for a comment explaining why a non-DeclaredType site is computed as types.capture(types.skipTypeVars(t, true)). No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607N4t by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Add a one-line comment giving the reason.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503929310

### F20 [minor] No test pins the array-element location that dataflow types a held NO_CHANGE value against (tests)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1348-1350` · Confidence: medium

- Problem: locationOf types an array-element holder by the location of its array, so that an element of an inherited `T[]` field in `class Sub<S> extends Holder<@NonNull S>` does not keep a NO_CHANGE fact. Replacing that branch with the node's static type, which javac gives without the supertype's @NonNull, leaves every test green. A regression there keeps NO_CHANGE in such an element and silently accepts it at a later `S` sink.
  - fact: measure/nullaway-pitest-diff-survivors.txt: AccessPathNullnessPropagation.java 1348 `if (node instanceof ArrayAccessNode arrayAccess) {` survived 'removed conditional - replaced equality check with false', reached by 30 tests.
  - fact: AccessPathNullnessPropagation.java:1339-1342 Javadoc: "an array element typed by the location of its array"; the description: "A field, array element, parameter, lambda return, or dataflow holder is typed as a member of its receiver's type".
  - inference: With the mutant, after `array[0] = box.get();` in a `Holder<@NonNull S>` subclass (reported at the store), `sink.accept(array[0])` on a `Sink<S>` is no longer reported, because the holder keeps NO_CHANGE. The sibling survivor on 1353 (static field) is equivalent, since a static field cannot have a class type-variable type.
- Proposed solution: In nonNullTargetRejectsWildcardResult, or next to it, read the element back after the reported store into an inherited `@NonNull S` array element and pass it to an `S` sink, with the expected `passing @Nullable parameter` report.

### F21 [minor] The breaking change for `array[i] = null` has no test (tests)

`nullaway/src/test/java/com/uber/nullaway/jspecify/JSpecifyArrayTests.java:176-205` · Confidence: high

- Problem: The Breaking changes section says that an element of a `@Nullable`-element array that dataflow knows is null, "after `array[i] == null` or `array[i] = null`", is now reported "wherever it is dereferenced or passed, returned, or stored where a non-null value is expected". nullableElementReadKeepsWhatDataflowKnows covers only a dereference after `array[0] == null`. No test reads the element after a `null` store, and no test passes, returns, or stores it, so the second half of a listed user-visible break is unpinned.
  - fact: JSpecifyArrayTests.java:189-195 `if (array[0] == null) { String element = array[0]; ... element.hashCode(); }` is the only new case; a search of the jspecify tests for `] = null;` finds no read of the element after the store.
  - fact: AccessPathNullnessPropagation.java:892 now returns `input.getRegularStore().getNullnessOfAccessPath(arrayAccessPath)` instead of mapping every non-NULLABLE fact to NONNULL.
- Proposed solution: Add to nullableElementReadKeepsWhatDataflowKnows a method that does `array[0] = null; String element = array[0]; element.hashCode();` with the expected report, and one sink other than a dereference, such as `return array[0];` from a `String` method after the null test.

### F22 [minor] HandleWildcardGenerics wiki entry omits the enhanced-for type-variable case the option now gates (docs-pages)

no line · Confidence: high

- Problem: The change widens what `-XepOpt:NullAway:HandleWildcardGenerics` controls: it now also decides how NullAway treats an enhanced-for element whose type is a type variable `T` with a nullable upper bound (`NO_CHANGE` with the option on, non-null as in 0.14.0 with it off). The option's only reference entry, the Configuration page of the NullAway wiki, still says the option covers 'wildcard generic types' and nothing else. A user who hits the vavr-style `for (T t : this)` reports, or who wants the 0.14.0 behavior back, finds no hint on that page that this option is the switch, and the JSpecify Support page links to the same entry as 'checking and inference for wildcard types'.
  - fact: uber/NullAway.wiki origin/master Configuration.md:324: "Within JSpecify mode, enables improved support for nullability checking and type inference involving wildcard generic types."
  - fact: nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4647-4657 returns `Nullness.NO_CHANGE` for a `Type.TypeVar` with a non-`NONNULL` upper bound only when `config.handleWildcardGenerics()` is true; otherwise the read is `NONNULL`.
  - fact: PR description: "The option now also covers an enhanced-for element whose type is a type variable `T`; #1786 already gated wildcard element types." and "With `HandleWildcardGenerics` off, an enhanced-for variable of type `T`, where `T` has a nullable upper bound, is non-null as in 0.14.0".
  - fact: No page in the repository documents the option: README.md and the other tracked .md files contain no `HandleWildcardGenerics` or `wildcard` mention; the wiki is the record.
  - inference: The wiki is a separate repository, so the entry cannot be updated in this PR's diff; it is owed alongside the release that ships the change.
- Proposed solution: Extend the Handle Wildcard Generics entry on the wiki Configuration page (in the release that ships this change) with one sentence: the option also governs values read through a type variable with a nullable upper bound, such as `box.get()` on a `Box<? extends T>` or an enhanced-for element of type `T`; with it on they are accepted where `T` is expected and reported at a dereference, with it off an enhanced-for element of type `T` is treated as non-null.

### F27 [nit] Rename isAtMost to isLessThanOrEqualTo (previous)

`nullaway/src/main/java/com/uber/nullaway/Nullness.java:124` · Confidence: high

- Problem: The maintainer finds `isLessThanOrEqualTo` clearer than `isAtMost` for the lattice order test. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc606xrV by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Rename or reply with the reason to keep the name.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503739935

### F28 [nit] reachesThroughNonNullableBounds recurses as deep as the bound chain (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4855` · Confidence: high

- Problem: The maintainer notes the recursion depth equals the inheritance/bound chain and offers a loop. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607Akb by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Reply, or convert to a loop.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503839671

### F29 [nit] Can the path argument be pathWithLeaf(path, array)? (question) (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4877` · Confidence: high

- Problem: In getAssignedVariableType the recursive call passes pathWithLeaf(pathWithLeaf(path, arrayAccess), array); the maintainer asks whether pathWithLeaf(path, array) suffices. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607JPA by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Simplify, or reply why the intermediate leaf is needed.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503898001

### F30 [nit] Comment duplicates what paramHasNonNullAnnotation handles (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4997` · Confidence: high

- Problem: The maintainer asks why the inline comment about class-file parameters and non-null-bounded type variables is needed, since paramHasNonNullAnnotation handles it. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607Lrf by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Remove the comment or reply with what it adds.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503914339

### F31 [nit] Only the Before twin of the non-null receiver-field getters is deprecated (least-surprise)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessAnalysis.java:223-235` · Confidence: medium

- Problem: The change adds the same pair of initialization getters for both program points (`getInitializedFieldsOfReceiverBefore` and `getInitializedFieldsOfReceiverAtExit`), but deprecates only `getNonnullFieldsOfReceiverBefore`; `getNonnullFieldsOfReceiverAtExit` stays undeprecated. Both old methods still return exactly what their names say (fields holding `NONNULL`), so the Before method is not wrong; it is deprecated only because its last in-tree caller moved. A handler author who reads the two pairs as twins gets a deprecation warning on one and not the other, and the warning on a method that still gives a non-null guarantee points to one that, by its own Javadoc, gives none. The PR description explains why AtExit stays (`@EnsuresNonNull` uses it) but not why Before, the same query at a different point, is retired.
  - fact: AccessPathNullnessAnalysis.java:223-232: `@deprecated for an initialization check, use {@link #getInitializedFieldsOfReceiverBefore}, which also returns a field that holds a value for which {@link Nullness#isNoChange()} holds. Such a value may be null, so that method gives no non-null guarantee.` followed by `@Deprecated public Set<Element> getNonnullFieldsOfReceiverBefore(...)`, whose body still selects `NullnessStore::getNonNullReceiverFields`.
  - fact: AccessPathNullnessAnalysis.java:166-175: `getNonnullFieldsOfReceiverAtExit` has no `@Deprecated` and also selects `NullnessStore::getNonNullReceiverFields`; its in-tree caller is EnsuresNonNullHandler.java:86.
  - fact: PR description: `getNonnullFieldsOfReceiverAtExit`, which `@EnsuresNonNull` checking uses, still returns only fields holding a non-null value; the author's 2026-11-03 comment gives "no main-code callers left" as the reason for deprecating the Before method.
- Proposed solution: Treat the two non-null getters alike: either drop `@Deprecated` from `getNonnullFieldsOfReceiverBefore` and keep the pointer to `getInitializedFieldsOfReceiverBefore` as a plain Javadoc note for initialization checks, or state in its `@deprecated` text why a non-null query before an expression is retired while the same query at exit is kept.

### F33 [nit] No test pins that a call declared non-null ignores a null fact on its access path (tests)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1274-1281` · Confidence: medium

- Problem: The rewrite of returnValueNullness keeps master's rule that a call whose return is non-null is NONNULL without consulting the store (`declaredNullness.equals(NONNULL) ? NONNULL : ...`). Replacing that test with false, so the store is consulted with a NONNULL default, survives the whole suite. A later edit that drops the shortcut would start reporting `s.get().hashCode()` inside `if (s.get() == null)` for a non-null getter, with no test failing.
  - fact: measure/nullaway-pitest-diff-survivors.txt: AccessPathNullnessPropagation.java 1279 `declaredNullness.equals(NONNULL)` survived 'removed conditional - replaced equality check with false', reached by 797 tests.
  - fact: Base: `} else if (node == null || methodReturnsNonNull.test(node) || (!Nullness.hasNullableAnnotation(...) && !genericReturnIsNullable(node))) { nullness = NONNULL; }`; head AccessPathNullnessPropagation.java:1274-1281 moves this into the declaredNullness branch.
  - inference: Under the mutant, the then-branch of `if (s.get() == null)` reads the NULL fact for the zero-argument call path, so a dereference there is reported where master and the head report nothing.
- Proposed solution: Add a case with a non-null getter dereferenced inside `if (s.get() == null)`, expecting no report, to the existing tests of access paths for zero-argument calls, or say in the pull request that this behavior is deliberately left unpinned.

## Class C1: Lambda return target typed apart from the argument and poly-expression paths

Root cause: NullAway.lambdaTypeAtTarget recomputes a lambda argument's target from javac's method type, so it skips the non-null-bound and inference rules the direct-argument and cached poly-expression paths apply, and only its reporting partitions are tested.

### F2 [minor] Lambda argument returns a NO_CHANGE value into a non-null-bounded method type variable unreported (correctness)

`nullaway/src/main/java/com/uber/nullaway/NullAway.java:1395-1416` · Confidence: high

- Problem: For a lambda passed as an argument, lambdaTypeAtTarget takes the return target from javac's parameter type at the call (getParameterTarget(...).type()) and drops the ValueTarget's excludesNull flag. With `static <U> void take(Sup<U> s)` (U has a non-null bound), javac substitutes U := T, so `take(() -> box.get())` on a `Box<? extends T>` with `T extends @Nullable Object` returns into a plain `T` and is accepted. The same value passed directly to `static <U> void takeValue(U u)` is still reported, because getParameterTarget excludes null for a parameter whose declared type is a type variable with a non-null bound. Master reported the lambda call (an inference failure on U); the head reports nothing, so a value that is null whenever T is instantiated with a nullable type now reaches a consumer whose U requires non-null. This is the rule the description states for parameters ("a nullable upper bound on that type variable"), not applied to the lambda path, and it is not one of the agreed follow-ups, which concern new reports, not missed ones. Severity is minor because the lambda path already accepts a plain `T` value there (`take(() -> t)` is unreported on master too); the change extends that gap to wildcard reads and makes the lambda and direct-argument paths disagree for them.
  - fact: Probe correctness-probes/CorrectnessProbeTests.java, method lambdaVsDirectNonNullBound, run on head fc9b07b3 with JDK 21: `./gradlew --quiet :nullaway:test --tests com.uber.nullaway.jspecify.CorrectnessProbeTests`. Head reports only `Test.java:16: passing @Nullable parameter 'box.get()' where @NonNull is required` (direct `takeValue(box.get())`) and line 19 (`take(() -> null)`); lines 10 `take(() -> box.get());` and 13 `take(() -> { return box.get(); });` get no diagnostic (correctness-probes/head-results.xml).
  - fact: The same probe on base 13392cb8 reports `Test.java:10` and `Test.java:13: inference failure: type variable U is constrained to be @Nullable, but its upper bound requires it to be @NonNull` (correctness-probes/base-results.xml).
  - fact: NullAway.java:1399-1408 reads only `.type()` of `genericsChecks.getParameterTarget(callee, call, formalParamType, ...)`, where formalParamType comes from `invokedMethodTypeAtCall` (javac's substituted type); GenericsChecks.java:5000-5002 computes the excludes-null flag from `declaredType instanceof Type.TypeVar && !GenericsUtils.upperBoundIsNullable(...)`, which only fires when the parameter itself is a type variable, not a type argument of the functional interface.
  - fact: The same probe's `viaLambdaParam`, `take(() -> t)` with a parameter `T t` (Test.java:22), gets no diagnostic on base 13392cb8 or on head (correctness-probes/base-results.xml, head-results.xml): the lambda path already accepted a plain `T` value into a non-null-bounded `U` before this change, so the head extends an existing gap to wildcard reads rather than opening a new one.
- Proposed solution: Make the lambda return target exclude null when the functional interface's return type comes from a method type variable of the callee whose upper bound is non-null (for example, map the lambda's return type back through the callee's declared parameter type `Sup<U>` and apply the same bound test getParameterTarget applies to a type-variable parameter), and add the `take(() -> box.get())` case with `<U>` (non-null bound) to NullnessOperatorTests as a reported case next to its direct-argument twin.

### F3 [minor] Lambda return target recomputed beside the poly-expression type GenericsChecks already keeps (architecture)

`nullaway/src/main/java/com/uber/nullaway/NullAway.java:1371-1417` · Confidence: medium

- Problem: GenericsChecks already computes the functional interface type of a lambda passed as an argument, with the nullness its target supplies, and stores it in inferredPolyExpressionTypes; getPolyExpressionType returns it. The new NullAway.lambdaTypeAtTarget computes the same type a second way: it walks to the parent call, iterates InvocationArguments over javac's method type, and builds the parameter type through getParameterTarget, which takes the receiver's member type but skips NullAway's inference of method type arguments and the handler and PolyNull models that getInvokedMethodTypeAtCall applies. checkReturnExpression now reads both for one lambda return: getPolyExpressionType for the @Nullable-return bail-out and lambdaTypeAtTarget for the NO_CHANGE decision. Where the two types differ, for example a generic method whose type variable NullAway infers as @NonNull T from another argument, the lambda path accepts a NO_CHANGE return that the direct-argument path reports (the PR description lists `two(box.get(), "x")` and `Holder.make(t, ts).set(box.get())` as reported because of that inference). The generics-specific target typing also lives in NullAway.java, a 3600-line file, rather than in GenericsChecks next to the cache it duplicates, so a later fix to one of the two lambda typings will not reach the other.
  - fact: NullAway.java:1464 `Type lambdaType = genericsChecks.getPolyExpressionType(lambdaTree);` and NullAway.java:1477 `() -> returnTargetAtReturn(methodSymbol, lambdaTree, state),` in the same checkReturnExpression; returnTargetAtReturn calls `lambdaTypeAtTarget(lambdaTree, state)` at NullAway.java:1348.
  - fact: NullAway.java:1394 `new InvocationArguments(call, invokedMethodTypeAtCall(call, callee))` uses javac's method type (NullAway.java:3224-3233), then NullAway.java:1416 `GenericsUtils.groundTargetType(targets.get(0), state, config, handler)`; the PR makes groundTargetType public for this caller (GenericsUtils.java diff).
  - fact: GenericsChecks.java:1541-1558 already stores, for each lambda argument, `GenericsUtils.groundTargetType(formalParamType, ...)` with inferred nullability into `inferredPolyExpressionTypes.put(argument, typeWithInferredNullability)`, and maybeStorePolyExpressionTypeFromTarget (GenericsChecks.java ~5012) stores the grounded target type from the formal parameter of getInvokedMethodTypeAtCall, which applies memberType of the receiver, NullAway inference, handler.onOverrideMethodType, and the PolyNull model (GenericsChecks.java:3914-3943).
  - inference: getParameterTarget (GenericsChecks.java:4955) builds the type from `TypeSubstitutionUtils.memberType(..., receiverType, methodSymbol, config)` or `methodSymbol.type` and javac's formalParamType, with no inference and no handler model, so for a static generic method the lambda target keeps the unannotated method type variable that NullAway's inference may have made @NonNull.
- Proposed solution: Move the lambda target typing into GenericsChecks and derive it from the type that getPolyExpressionType already returns for the lambda (fixing the cache where it lacks the receiver-supplied annotations), so checkReturnExpression reads one functional interface type for both the @Nullable bail-out and the NO_CHANGE decision; if the uninferred type is intended for NO_CHANGE, say why in lambdaTypeAtTarget's Javadoc and add a test with a lambda argument whose method type variable NullAway infers from another argument.

### F4 [minor] No test shows a lambda argument accepted through parentheses, a body-less constructor, or a later varargs position (tests)

`nullaway/src/main/java/com/uber/nullaway/NullAway.java:1377-1398` · Confidence: high

- Problem: The description and the Javadoc of lambdaTypeAtTarget claim that a lambda passed as an argument of a call, or of a constructor with no class body, returns into the type of the receiving parameter, that parentheses around the lambda are skipped, and that an anonymous-class constructor argument returns into a target that excludes null. issue1727LambdaReturnFalsePositive, the only test that reaches this method, checks the parenthesized, constructor, anonymous-class, and varargs forms only against parameters of type Box<@NonNull U>, where the expected report also appears when the method returns null and the lambda falls back to EXCLUDES_NULL. The accepting partition of each form is untested, so a regression that sends a parenthesized lambda, a `new Taker<T>(() -> box.get())` argument, or the second lambda of a varargs call to the fallback reintroduces the #1727 false positive with the suite green. The anonymous-class claim is untested for the same reason: its only case also reports under the receiving-parameter rule.
  - fact: measure/nullaway-pitest-diff-survivors.txt: NullAway.java 1377 `while (parentPath != null && parentPath.getLeaf() instanceof ParenthesizedTree)`: 2 mutants survived; 1386-1387 `|| (parent instanceof NewClassTree newClass && newClass.getClassBody() == null))`: survived; 1398 `int paramIndex = Math.min(argPos, callee.getParameters().size() - 1);` survived 'Replaced integer subtraction with addition'; 1414 `return targets.isEmpty()` survived. Each is reached by 1 test, NullnessOperatorTests.issue1727LambdaReturnFalsePositive.
  - fact: NullnessOperatorTests.java:1721-1725 has only reporting cases for these forms: `Test.<T>take((() -> box.get()));`, `Test.<T>takeAll(() -> box.get());`, `new Taker<T>(() -> box.get());`, and at :1736 `new Taker<T>(() -> box.get()) {};`, all against `Box<@NonNull U>`/`Box<@NonNull V>` parameters; the only accepted lambda arguments are unparenthesized method calls (:1711-1712 `Test.<T>takePlain(() -> box.get());`, `nonNullTaker.takePlain(() -> box.get());`).
  - fact: NullAway.java:1348-1350: a null result of lambdaTypeAtTarget yields `GenericsChecks.ValueTarget.EXCLUDES_NULL`, so every surviving mutant above turns an accepted lambda into a reported one, and no test has an accepted lambda in those forms.
  - inference: Mutant 1398 is killed by a varargs call with two individual lambda arguments, where argPos 1 must be clamped to the varargs parameter.
- Proposed solution: Add accepting cases with no diagnostic to issue1727LambdaReturnFalsePositive: `Test.<T>takePlain((() -> box.get()));`, a constructor `PlainTaker(Box<V> b)` called as `new PlainTaker<T>(() -> box.get());`, and a varargs `takeAllPlain(Box<U>... boxes)` called as `Test.<T>takeAllPlain(() -> box.get(), () -> box.get());`. Add `new PlainTaker<T>(() -> box.get()) {};` with its expected report, which separates the anonymous-class rule from the receiving-parameter rule, and a second lambda in `Test.<T>takeAll(...)` with its report.

## Class C2: PR description out of step with the review and the user-visible changes

Root cause: The description, which becomes the squash commit body, was not updated after the maintainer settled the follow-ups, and it files new reports outside the Breaking changes block and the title.

### F5 [minor] New error for `two(box.get(), "x")`, accepted on master, sits in Scope instead of the breaking-changes block (change-description)

no line · Confidence: high

- Problem: With `HandleWildcardGenerics` on, a wildcard read passed to a generic method whose other argument fixes the type argument, as in `two(box.get(), "x")` for `<U extends @Nullable Object> void two(U a, U b)`, is now reported, where 0.14.3 accepts it. That is a failure extended to inputs that worked before, so it is a break for those inputs, but the description mentions it only inside the Scope paragraph. The `**Breaking changes.**` block names only API extenders and code that reads `@Nullable` array elements after a null test, so an upgrading user scanning the break block, or the squash commit's `User-visible:` lines, does not learn about it, and the description gives no diagnostic text to grep.
  - fact: PR description, break lead-in: "Code that extends NullAway through its public API, and projects in JSpecify mode that read `@Nullable` array elements after a null test or a `null` store, see these changes from 0.14.3".
  - fact: PR description, Scope paragraph: "`U` is inferred non-null and the value is reported, which master accepts."
  - fact: vlsi in thread PRRT_kwDOBhZ_Pc60wuTl: "infers `U` as non-null `Object` from the second argument and then reports the first, which master accepts."
- Proposed solution: Add one `User-visible:` line to the breaking-changes block: with `HandleWildcardGenerics` on, a value read through `? extends T` passed to a generic method whose type argument another argument fixes to a non-null type, as in `two(box.get(), "x")`, is reported as `passing @Nullable parameter 'box.get()' where @NonNull is required`, where 0.14.3 accepts it; widen the lead-in sentence to cover it, and keep in Scope only the follow-up reference.

### F6 [minor] Scope paragraph still leaves to the review two questions the maintainer already decided as follow-ups (change-description, intent-scope)

no line · Confidence: high

- Problem: The Scope paragraph of the PR description says the `sink.accept(identity(value))` choice "is left to the review" and that adding a nullable inference constraint for `two(box.get(), "x")` "is left to the review as well". msridhar answered both on 2026-11-07: option (2) long term, done as a follow-up, and `U` should be inferred `@Nullable`, also as a follow-up. The description becomes the squash commit body, so `git log` will record as open two questions that were settled, and record no follow-up that a reader or backporter can find. No issue tracks either follow-up.
  - fact: PR description, Scope paragraph: "so that choice is left to the review" ... "changes the inference design and is left to the review as well."
  - fact: msridhar, thread PRRT_kwDOBhZ_Pc60wuTl, 2026-11-07T20:57:15Z: "Here in the long term I think we want 2, but we can do it as a follow up." and "I agree we should infer `U` as `@Nullable` here. ... I'm also fine with doing this as a follow up".
  - fact: input.md: "No tracked issue exists for either."
  - fact: msridhar in thread PRRT_kwDOBhZ_Pc60wuTl: "in the long term I think we want 2, but we can do it as a follow up" and "I'm also fine with doing this as a follow up".
- Proposed solution: Open an issue for each follow-up (carry `NULL_NO_CHANGE` through `identity(value)` so `sink.accept(identity(value))` is accepted; infer `U` as `@Nullable` in `two(box.get(), "x")`), and rewrite the two Scope sentences to state the agreed direction with the issue numbers instead of leaving the choice to the review.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4499496038

### F32 [nit] PR title omits the new reports for null-tested @Nullable-element array elements (intent-scope)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:892` · Confidence: medium

- Problem: The change to the read of a `@Nullable`-element array element (AccessPathNullnessPropagation.java:892) keeps a NULL fact that master turned into NONNULL, so JSpecify-mode code that dereferences such an element after `array[i] == null` or `array[i] = null` gets new reports unrelated to wildcard reads. The description lists it first under Breaking changes, but the PR title, which becomes the squash commit headline, names only `? extends T` and enhanced-for reads, so a reader bisecting a new array report from the log will not find it by the headline.
  - fact: Master, AccessPathNullnessPropagation.java:886-890 (base 13392cb8): `if (accessPathNullness == Nullness.NULLABLE) { resultNullness = Nullness.NULLABLE; } else { resultNullness = Nullness.NONNULL; }`, so a NULL fact on an array element became NONNULL before this PR.
  - fact: Head, AccessPathNullnessPropagation.java:892: `resultNullness = input.getRegularStore().getNullnessOfAccessPath(arrayAccessPath);`
  - fact: PR description, Breaking changes: "an element of a `@Nullable`-element array that dataflow knows is null, after `array[i] == null` or `array[i] = null`, is reported wherever it is dereferenced ... Dataflow treated such an element as non-null." The PR title names only `? extends T` and enhanced-for reads.
  - inference: The NO_CHANGE work needs only that a NO_CHANGE or NULL_NO_CHANGE fact survives the read; keeping master's NULL to NONNULL mapping for plain NULL would leave the wildcard fix intact.
  - fact: AccessPathNullnessPropagation.java:892 must at least keep NO_CHANGE and NULL_NO_CHANGE, which master's `else { resultNullness = Nullness.NONNULL; }` would turn into NONNULL; the description already lists the plain-NULL consequence first under Breaking changes.
- Proposed solution: Mention the array-element reports in the PR title or keep them out of this change; splitting is not required.

## Class C3: NO_CHANGE Javadoc in coined or loose terms

Root cause: The new Javadoc names pseudo-assignment targets with several coined words (holder, location, sink, moves) and restates the NO_CHANGE rule loosely in several places, so comments disagree with each other and the maintainer cannot follow them.

### F8 [minor] Five coined words for the target of a pseudo-assignment, plus "moves" for the assignment itself (vocabulary, previous)

`nullaway/src/main/java/com/uber/nullaway/Nullness.java:201-203` · Confidence: high

- Problem: The change names one concept, the variable, parameter, return, or array element that a value is assigned, passed, or returned to, with five words: "target" (`ValueTarget`, `holderTarget`), "location" (`locationOf`, "the location that receives"), "holder" (`holder` parameters, `valueHeldAs`, `valueHeldByPath`, "moves to a holder"), "sink" ("Every sink", "the sinks use"), and "destination" ("supplies the destination"). The operation itself is called "moves" ("once it moves to a holder", "node whose value moves", "dataflow moves it to"), a metaphor for assignment, argument passing, return, and an array store. The codebase at the base already has the words: "pseudo-assignment" and `nonNullTarget` in `ErrorBuilder`, and the change's own Javadoc on `Nullness.NO_CHANGE` lists "an assignment, an argument, a return, or an array store". A reader of the public `Nullness.withoutNoChange()` Javadoc cannot tell that "moves to a holder" means a pseudo-assignment, or that "holder", "location", and "sink" are the same thing as a `ValueTarget`; grepping for any one word finds a fraction of the uses. Open threads already ask for "assigned location" and "pseudo-assignment" in `acceptsNoChangeValue` (GenericsChecks.java:4811) and for new names of `valueHeldByPath` and `valueHeldAs`; the same coinages also sit in `Nullness.java`, `NullAway.java`, `holderTarget`, `locationOf`, and their Javadoc, which those threads do not reach.
  - fact: nullaway/src/main/java/com/uber/nullaway/Nullness.java:201: `Returns the nullness of this value once it moves to a holder that does not accept a {@code NO_CHANGE} value`
  - fact: nullaway/src/main/java/com/uber/nullaway/Nullness.java:73: `the value is {@link #NULLABLE}, as it is in a holder of another type that dataflow moves it to.`
  - fact: nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4811-4813: `Every sink, and dataflow wherever a value moves to another holder, must apply this test to the {@link ValueTarget} of the receiving location, so that a {@code NO_CHANGE} fact always holds relative to the static type of its holder.`
  - fact: nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1330-1341: `Returns the location that {@code holder}, without enclosing casts, names` ... `private GenericsChecks.ValueTarget holderTarget(Node holder)` ... `factories that the sinks use`
  - fact: nullaway/src/main/java/com/uber/nullaway/NullAway.java:1336 `Returns the location that receives a returned expression` replaces base line 1318 `Returns the destination type of a returned expression`; NullAway.java:3245 keeps `@param target supplies the destination`.
  - fact: Base 13392cb8 nullaway/src/main/java/com/uber/nullaway/ErrorBuilder.java:115: `@param nonNullTarget if non-null, this error involved a pseudo-assignment of a @Nullable`; `git grep -wi` finds no `sink`, `sinks`, or `holder` in nullaway/src/main at the base.
  - inference: The five nouns and the verb "moves" each denote the target or the act of a pseudo-assignment; no comment defines any of them as distinct from the others.
  - fact: Thread PRRT_kwDOBhZ_Pc606_nb by msridhar on GenericsChecks.java:4813, posted on head fc9b07b3 with no reply, suggests: 'This test should be applied to the ValueTarget of the assigned location at every pseudo-assignment, so that a NO_CHANGE fact always holds relative to the static type of the assigned location.'
- Proposed solution: Pick the codebase's words and use them throughout the change: "pseudo-assignment" for the operation (assignment, argument passing, return, array store) instead of "moves", and one noun for what `ValueTarget` models, such as "target" to match the record and `nonNullTarget`, or the reviewer's "assigned location". Apply it to the Javadoc of `Nullness.NO_CHANGE`, `Nullness.NULL_NO_CHANGE`, `Nullness.withoutNoChange()`, `ValueTarget`, `acceptsNoChangeValue`, `NullAway.returnTargetAtReturn`, the `target` parameter of `isTopLevelNullnessCompatible`, and to `holderTarget`, `locationOf`, and the `holder` parameters in AccessPathNullnessPropagation.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503833064

### F9 [minor] Config Javadoc says every read through a nullable-bounded type variable is NO_CHANGE (naive-reader)

`nullaway/src/main/java/com/uber/nullaway/Config.java:318-323` · Confidence: high

- Problem: The Javadoc of `handleWildcardGenerics()` says the option computes `NO_CHANGE` "for a value read through a type variable with a nullable upper bound". Read literally, that covers `List<T>.get()`, a parameter of type `T`, and a field of type `T`, and a reader of the public `Config` interface will expect those to become `NO_CHANGE` with the option on. The `Nullness.NO_CHANGE` Javadoc says the opposite: only a read through a wildcard or capture bounded by `T`, and an enhanced-for element of type `T`, gets `NO_CHANGE`; `List<T>.get()` stays `NONNULL`. The two comments in one change disagree on which values the option affects.
  - fact: Config.java:319-322: "These also compute {@link Nullness#NO_CHANGE} for a value read through a type variable with a nullable upper bound, such as the result of {@code Box<? extends T>.get()} or an enhanced-for element of type {@code T}"
  - fact: Nullness.java:59-66: "NullAway gives this nullness to a value read through a wildcard or capture bounded by {@code T} ... Any other value of type {@code T}, such as a parameter, a field, or the result of {@code List<T>.get()}, is {@link #NONNULL}"
- Proposed solution: Name the same cases `Nullness.NO_CHANGE` names: "These also compute `NO_CHANGE` for a value read through a wildcard or capture bounded by a type variable with a nullable upper bound, such as the result of `Box<? extends T>.get()`, and for an enhanced-for element of type `T`; any other value of type `T`, such as the result of `List<T>.get()`, stays `NONNULL`." Or link to `Nullness#NO_CHANGE` for the list instead of restating it.

### F10 [minor] Handler contract on set positions names no case where setting NONNULL changes the result (naive-reader)

`nullaway/src/main/java/com/uber/nullaway/handlers/Handler.java:235-237` · Confidence: high

- Problem: The new paragraph on the public extension point says that a position a handler sets to `NONNULL`, "even to the value it already holds", "requires a non-null argument whatever the parameter's type". A handler author cannot tell from this what differs between a position left at the base analysis's `NONNULL` and one set to `NONNULL`, since both read `NONNULL`, nor which argument is affected. The case is a `NO_CHANGE` argument, such as `box.get()` on a `Box<? extends T>`, passed to a parameter of type `T`: left alone, the parameter accepts it; set by a handler, the parameter is treated as `ValueTarget.EXCLUDES_NULL` and the call is reported. Nothing in the paragraph names `NO_CHANGE`, a `T` parameter, or the report, so a handler that copies every position through (a pattern the old contract allowed) silently starts producing reports.
  - fact: Handler.java:235-237: "A position that a handler sets, even to the value it already holds, is that handler's decision: NONNULL there requires a non-null argument whatever the parameter's type, so a handler sets only the positions it decides."
  - fact: NullAway.java:2614-2622: the target is `varArgsPassedAsArray || finalArgumentNullness.wasSet(paramIndex) ? GenericsChecks.ValueTarget.EXCLUDES_NULL : genericsChecks.getParameterTarget(...)`, so `wasSet` only matters for a value `isTopLevelNullnessCompatible` passes to the target supplier, which its Javadoc (NullAway.java:3246-3248) says happens only for a value for which `isNoChange()` holds
  - inference: A handler that calls `set(i, get(i))` for every position marks each one as set, so a `NO_CHANGE` argument to a `T` parameter it does not model is reported where it was accepted before
- Proposed solution: State the case in the paragraph, for example: "Where a handler leaves a position unset, a parameter whose type is a type variable `T` still accepts a value for which `Nullness#isNoChange()` holds, such as `box.get()` on a `Box<? extends T>`. A position the handler sets to `NONNULL`, even to the value it already holds, rejects that value too. Set only the positions the handler models."

### F11 [minor] NULL_NO_CHANGE Javadoc last sentence unclear to the maintainer (previous)

`nullaway/src/main/java/com/uber/nullaway/Nullness.java:89` · Confidence: high

- Problem: The maintainer cannot tell how the last sentence of the NULL_NO_CHANGE Javadoc ('Where it moves to a holder that acceptsNoChangeValue rejects, it becomes NULL') differs from how a NO_CHANGE value is handled at an assignment. The thread has no reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc606vuV by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Answer the thread and reword or drop the sentence so it states what differs from NO_CHANGE, if anything.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503726398

### F12 [minor] ValueTarget Javadoc wording: "receives a value" (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4758` · Confidence: high

- Problem: The maintainer suggested 'A location that can be assigned a value' in the ValueTarget Javadoc. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc6064qi by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Apply the suggestion or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503787107

### F13 [minor] Does a cast belong in the ValueTarget list? (question) (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4759` · Confidence: high

- Problem: The ValueTarget Javadoc lists 'a cast' among locations that receive a value; the maintainer asks whether casts are checked at all, since a cast differs from the other cases. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc6065AX by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
  - fact: AccessPathNullnessPropagation.java:985-990 (visitTypeCast) passes `GenericsChecks.ValueTarget.of((Type) node.getType(), /* declaration= */ null)` to `valueHeldAs`, so dataflow does apply the NO_CHANGE test to a cast's type; no sink reports at a cast.
- Proposed solution: Reply that dataflow types a cast as a ValueTarget (visitTypeCast, AccessPathNullnessPropagation.java:985-990) so the value of `(T) x` keeps NO_CHANGE only where the cast type accepts it, and say in the Javadoc that a cast is a dataflow target only, not a place where an error is reported; or drop 'a cast' from the list if that distinction is not worth stating.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503789292

### F14 [minor] "type arguments of the supertypes it is inherited through supply" is hard to follow (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4764` · Confidence: high

- Problem: The @param type wording of ValueTarget is unclear to the maintainer, who proposes 'the location's type, including any type-use annotations on its declaration or inherited from supertypes'. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc6066IH by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Reword the @param as suggested or equivalently.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503796476

### F15 [minor] acceptsNoChangeValue Javadoc: maintainer proposes a clearer statement of the rule (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4809` · Confidence: high

- Problem: The maintainer proposed a rewrite of the acceptsNoChangeValue Javadoc that states the subtyping rule and the bound-chain condition explicitly. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc606_EU by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Apply the suggestion (re-formatted) or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503829288

### F16 [minor] getAssignedVariableType Javadoc repeats the unclear supertype wording (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4861` · Confidence: high

- Problem: Same unclear phrase as on ValueTarget ('that the type arguments of the supertypes it is inherited through supply'). No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607H1a by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Reword together with the ValueTarget @param.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503888426

### F23 [nit] followUnsubstitutedTypeVarUpperBound is still documented as using the upper bound (comments)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4616-4617` · Confidence: high

- Problem: The change makes this flag do something different, but its @param line and the summary sentence still describe the old behavior. Before the change, true meant that for an unsubstituted type variable the method returned the nullness of its upper bound, so `T extends @Nullable Object` gave NULLABLE. Now true makes the method return NO_CHANGE for such a T when HandleWildcardGenerics is on, and NONNULL when it is off. The bound's own nullness is never returned. The @return line was updated and the @param line was not, so the two now contradict each other. A reader who goes by the @param line expects true to give NULLABLE for a nullable-bounded T. The maintainer's open question on the one-flag overload (why that overload can return NO_CHANGE when it passes false) comes from the same unclear definition of the flag.
  - fact: GenericsChecks.java:4609-4610 (unchanged): "Returns the nullness of a value read from {@code type}, optionally following the upper bound of an unsubstituted type variable." GenericsChecks.java:4616-4617 (unchanged): "@param followUnsubstitutedTypeVarUpperBound whether to use the upper bound when {@code type} is an unsubstituted type variable"
  - fact: Base 13392cb8 body: `if (followUnsubstitutedTypeVarUpperBound && type instanceof Type.TypeVar typeVar) { ... return getTypeNullnessForRead(upperBound, ..., true); }`, which returns the bound's nullness. Head GenericsChecks.java:4647-4658: `if (config.handleWildcardGenerics() && followUnsubstitutedTypeVarUpperBound && type instanceof Type.TypeVar typeVar && !getTypeNullnessForRead(typeVar.getUpperBound(), ...).equals(Nullness.NONNULL)) { return Nullness.NO_CHANGE; } return Nullness.NONNULL;`
  - fact: The new @return line at GenericsChecks.java:4618-4621 says NO_CHANGE with the option on and NONNULL with it off, which contradicts "use the upper bound" in the @param line above it.
  - inference: The flag still decides whether the upper bound of an unsubstituted type variable is consulted, so the @param is stale rather than wrong; the @return line two lines below states the new result.
- Proposed solution: Reword the @param line and the summary to the flag's current meaning. For example, the @param could read: whether an unsubstituted type variable whose upper bound may be null reads as NO_CHANGE (with HandleWildcardGenerics on) rather than NONNULL. Consider renaming the flag to match, and answer the open thread with the corrected definition.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4504045889

### F24 [nit] ValueTarget @param declaration wording (previous)

`nullaway/src/main/java/com/uber/nullaway/generics/GenericsChecks.java:4766` · Confidence: high

- Problem: The maintainer suggested 'the method that returns the value' instead of 'the method whose return receives the value'. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc6066de by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Apply the suggestion or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4503798680

## Class C4: Shape and names of the dataflow target-adaptation helpers

Root cause: valueHeldByPath and its sibling helper split one adaptation across two entry points with names and Javadoc the maintainer finds unclear.

### F17 [minor] valueHeldByPath Javadoc: maintainer proposes a clearer version (previous)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1294` · Confidence: high

- Problem: The maintainer proposed a rewrite of the Javadoc of the method that adapts the source's nullness to the holder's access path. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607tcl by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Apply the suggestion or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4504140526

### F18 [minor] Inline the helper into valueHeldByPath (previous)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1304` · Confidence: high

- Problem: The maintainer asks to inline the helper at line 1304 into valueHeldByPath and have visitAssignment call valueHeldByPath. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607w-n by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Inline, or reply why the second entry point is needed.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4504163955

### F25 [nit] Rename valueHeldByPath to adaptNullnessForAccessPath (previous)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1295` · Confidence: high

- Problem: Maintainer naming suggestion. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607uOq by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Rename or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4504145431

### F26 [nit] Rename the target-adapting helper to nullnessAdaptedToTarget and align its Javadoc (previous)

`nullaway/src/main/java/com/uber/nullaway/dataflow/AccessPathNullnessPropagation.java:1319` · Confidence: high

- Problem: Maintainer naming and Javadoc suggestion. No reply on the current head.
  - fact: Thread PRRT_kwDOBhZ_Pc607vIo by msridhar is unresolved, was posted on head fc9b07b3, and has no reply.
- Proposed solution: Rename and align the Javadoc, or reply.
- Continues: https://github.com/uber/NullAway/pull/2069#discussion_r4504151366

## Held until the code is settled

### F34 [nit] Description states three outcomes twice, in the What paragraphs and again in the outcome lines (change-description)

no line · Confidence: medium

- Problem: About 770 words of prose sit outside the outcome lines, and several paragraphs restate what a `User-visible:` or `Not changed:` line already carries, so the squash commit body says the same fact twice and a later edit can update one copy and not the other. The paragraph on handlers and `MethodParameterNullness` is also implementation detail the diff shows, and its only caller-visible fact is the `Not changed:` line about `onOverrideMethodInvocationParametersNullability`.
  - fact: Paragraph "A handler that requires a non-null argument ... so the handler API holds only `NONNULL` and `NULLABLE` as before." duplicates the Not changed line "`Handler.onOverrideMethodInvocationParametersNullability` receives only `NONNULL`, `NULLABLE`, or `null` for a parameter, as before." and the line about "a parameter a library model marks non-null".
  - fact: "Everywhere else the value stays nullable: a dereference, unboxing, an `Object` target, and a `@Contract` or `@EnsuresNonNull` postcondition." restates the first Not changed line (dereference, unboxing, `Object` target).
  - fact: "Inside `if (value == null)` the value is `NULL_NO_CHANGE` ... a target of type `T` still accepts it ... After the test, the two branches join back to `NO_CHANGE`." restates the User-visible line "such a value is still accepted where `T` is expected after `if (value == null)`, inside the branch and after it"; "The option now also covers an enhanced-for element whose type is a type variable `T`" restates the `HandleWildcardGenerics` off line.
- Proposed solution: Drop the handler/`MethodParameterNullness` paragraph, the "Everywhere else the value stays nullable" sentence, and the restated acceptance and option-coverage clauses, keeping only the reason each mechanism exists (for example, that `NULL_NO_CHANGE` is the meet of `NULL` and `NO_CHANGE` so a dereference stays reported) where the outcome line does not give it.

## Previous findings

- https://github.com/uber/NullAway/pull/2069#discussion_r4503726398: fix_not_accepted (continued by F11); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503739935: fix_not_accepted (continued by F27); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503787107: fix_not_accepted (continued by F12); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503789292: fix_not_accepted (continued by F13); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503796476: fix_not_accepted (continued by F14); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503798680: fix_not_accepted (continued by F24); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503829288: fix_not_accepted (continued by F15); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503833064: fix_not_accepted (continued by F8); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503839671: fix_not_accepted (continued by F28); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503888426: fix_not_accepted (continued by F16); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503898001: fix_not_accepted (continued by F29); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503914339: fix_not_accepted (continued by F30); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4503929310: fix_not_accepted (continued by F19); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504140526: fix_not_accepted (continued by F17); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504145431: fix_not_accepted (continued by F25); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504151366: fix_not_accepted (continued by F26); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504163955: fix_not_accepted (continued by F18); Posted on the reviewed head with no reply or later commit; the request stands.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504045889: resolved_by_clarification (continued by F23); The code answers the question: with followUnsubstitutedTypeVarUpperBound=false the overload still returns NO_CHANGE when the type is a wildcard or capture, because that branch recurses on the effective upper bound with true (GenericsChecks.java:4628-4636); only a bare unsubstituted type variable at the top stays NONNULL. The author has not replied; a reply should say so.
- https://github.com/uber/NullAway/pull/2069#discussion_r4507127113: resolved_by_clarification; LEAST_UPPER_BOUNDS and GREATEST_LOWER_BOUNDS are static final EnumMaps filled in the enum class initializer (Nullness.java:131-136) and never mutated afterwards; JVM class initialization publishes them safely. The author has not replied; a reply should say so.
- https://github.com/uber/NullAway/pull/2069#discussion_r4504067052: scope_deferred; The maintainer offered to defer sharing field and array type resolution between getAssignedVariableType and getTreeType to a follow-up; no tracked issue exists yet.
- https://github.com/uber/NullAway/pull/2069#discussion_r4499496038: scope_deferred (continued by F6); The maintainer agreed to handle both inference cases (identity(value) under a null test, and two(box.get(), "x") reporting where master accepted) as follow-ups; no tracked issue exists for either.
