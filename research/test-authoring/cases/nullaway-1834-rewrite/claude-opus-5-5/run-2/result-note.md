I rewrote the 20 tests that commit added as 9 tests in `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. Only that file changed, and nothing is committed. All 55 tests in `WildcardTests` pass with the fix, and `:nullaway:buildWithNullAway` passes. I also ran the rewritten tests against the production code from before the fix: exactly the 7 tests for newly reported cases fail, each at its expected-report line.

I found a false positive the fix introduces, which I left out of the tests and describe at the end of the message below.

---

**Message for the PR author**

**Why I changed the tests.** I ran your 20 tests against the code from before the fix. 7 of them fail there; those are the behaviour this PR adds. The other 13 already passed, so they are controls: inputs whose result shouldn't change. Several of those passing tests checked only that nothing was reported, with nothing next to them that does get reported. A test like that also passes when its setup is wrong.

I also checked how Error Prone's test helper reports failures. One compilation stops at the first mismatch (`Did not see an error on line N matching …`). So two new cases can't share one source file: the first failure would hide the second.

**What I changed.** Each of the 7 new cases is now its own test. Its controls sit in the same source file, and each control differs from the case in one way:

- **Concrete `? extends Object` requirement:**
  - A type variable whose bound admits null is reported.
  - Controls: a non-null bound, a `@Nullable` wildcard requirement, `Box<?>`, and `Box<@NonNull T>`.
- **Separate partitions, one test each:**
  - **Variable declared in `@NullUnmarked` code.** I added a `@NullMarked` holder as its control.
  - **Variable bounded by another variable whose bound is nullable.** Controls: a holder whose `T` is non-null, and passing the same value to a `Box<? extends T>` parameter.
  - **Wildcard bounded by a nullable type variable.** I added a non-null bound as its control.
- **Requirement that names a type variable:**
  - `S extends @Nullable T` into `? extends T`, with `S extends T` as the control.
  - `Box<T>` into `? extends @NonNull T`. Its controls are `? extends T` and the capture and `CompletableFuture` inference inputs. I checked these by mutation: removing the `CapturedType` exception makes this test fail on the capture line.
- **The two behaviours that already worked** (`@Nullable T` written at the use site) keep their own tests, each with its silent control.

I renamed the tests so each name states the rule, for example `aTypeVariableIsRejectedByANonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull`. Every input whose result already held before the fix is still in some test.

**The override test.** I moved it from `new Test<>() { … }` to a named `class Impl<V> implements Test<V>`, and added `List<V> get()` overriding `List<? extends V>` as its control. In the diamond form, the control is reported too. So the original test passed whether or not the `@NonNull` rule worked.

**A bug I propose fixing and did not fix.** Since this fix, an anonymous class created with a diamond reports a correct override as an error:

```java
interface Test<V extends @Nullable Object> {
  List<? extends V> get();
  static <V extends @Nullable Object> Test<V> make() {
    return new Test<>() {
      @Override public List<V> get() { … }  // reported: mismatched type parameter nullability
    };
  }
}
```

This was silent before the fix. The same override with `new Test<V>()`, or in a named class, is still silent. The type the diamond infers seems to reach `extendsBoundContains` in a form where `admitsNull`/`typeComparedForNullness` read it differently. I didn't add a failing test for it, because it needs a production change. Once that's fixed, a diamond control could join the override test. The CHANGELOG's sub-bullet about override checks should probably wait until then too.
