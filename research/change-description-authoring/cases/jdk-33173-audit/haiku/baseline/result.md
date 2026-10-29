`JNIHandles::is_same_object` calls `ValueObjectMethods.isSubstitutable` without initializing `ValueObjectMethods` first. This change initializes the class at startup when the Valhalla preview is enabled, and adds asserts that check the initialization at every upcall in debug builds.

## The defect

A post-integration audit of JDK-8391022 confirmed that fix, which added the initialization before the upcall from `JVM_IHashCode`. The audit also flagged one more upcall without it.

`JNIHandles::is_same_object` calls `JavaCalls::call` with the method from `Universe::is_substitutable_method()`, the same way `InterpreterRuntime::is_substitutable` does. The interpreter path first calls `method_holder()->initialize(...)`, and `is_same_object` does not. `JavaCalls::call` runs the pre-resolved method without initializing its holder class.

No failure has been reported. The effect on a JNI caller that runs first has not been worked out.

## Initialization order

A reviewer asked why `ValueObjectMethods` is not initialized eagerly. Eager initialization makes each missing on-demand initialization harmless, and the class is used heavily once preview features are on.

The class cannot be initialized before `System.initPhase1()` as it stands. Its static initializer read the system property `value.bsm.debug` to set `VERBOSE`. System properties are not set up before `initPhase1()`, so the initializer threw `NullPointerException`. Initializing it right after `initPhase1()` would leave earlier Java code free to start a value object comparison before the class is ready. That risk grows as more of the JDK uses value classes.

The reviewer pointed out that lazy initialization before `initPhase1()` has the same bootstrapping problem. With eager initialization, a check fails reliably when the class is used too early, so future bootstrapping bugs surface instead of staying hidden. This change follows that suggestion, and the reviewer approved it as the change they wanted instead of "plugging yet another missing initialization point."

Once `VERBOSE` no longer reads a property, `jdk.internal.misc.Unsafe` is the only prerequisite of `ValueObjectMethods`. Before this change, `Unsafe` was initialized during `initPhase1()`, as a dependency of `LazyConstantImpl`, which `Charset` uses, which `SystemProps` uses. With this change, `Unsafe` is initialized earlier, before `initPhase1()`.

## Changes

- `threads.cpp`: `Threads::initialize_java_lang_classes` initializes `ValueObjectMethods` right after `UnsafeConstants`, before `initPhase1()`, when the Valhalla preview is enabled. Without the preview, the sequence is unchanged.
- `ValueObjectMethods.java`: `VERBOSE` is the constant `false` instead of a read of `value.bsm.debug`. The class comment says the class is initialized very early and must keep minimal dependencies. `VERBOSE` stays, because enabling debug output now means changing one line rather than adding the logging code back.
- `universe.cpp`: `Universe::is_substitutable_method()` and `Universe::value_object_hash_code_method()` assert that `ValueObjectMethods` is initialized, with the messages `value object comparison occurring too early` and `value object hashcode occurring too early`.
- `interpreterRuntime.cpp` and `jvm.cpp`: the `method_holder()->initialize(...)` calls are removed from `InterpreterRuntime::is_substitutable` and `JVM_IHashCode`.
- `c1_Runtime1.cpp`: `Runtime1::substitutability_check` called `JavaCalls::call_static` with the class, method name, and signature. That resolved the method again, and the resolution initialized the class as a side effect. The method now comes from `Universe::is_substitutable_method()`, and the code calls `JavaCalls::call`, as the other sites do.
- `sharedRuntime.cpp`: in `SharedRuntime::find_callee_info_helper` (the C2 path), the `ValueObjectMethods_klass()->initialize(...)` call is removed. The debug-only lookup of `isSubstitutable` by name and signature is replaced by an assert against `Universe::is_substitutable_method()`.
- `jniHandles.cpp` is unchanged. With the class initialized at startup, `is_same_object` needs no call of its own.

## Testing

No new test is added. The new asserts check every upcall in debug builds. I ran all Valhalla tests locally, tiers 1 to 3, and the `--enable-preview` subset of tier 7.

- [x] I confirm that I make this contribution in accordance with the [OpenJDK Interim AI Policy](https://openjdk.org/legal/ai).
