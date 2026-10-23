## Summary

When preview features are enabled, the VM now initializes `ValueObjectMethods` during startup, before `System.initPhase1()`. Before this change, each upcall site initialized the class on demand. `JNIHandles::is_same_object` was one site that did not.

## Problem

`JNIHandles::is_same_object` upcalls `ValueObjectMethods.isSubstitutable` through `JavaCalls::call`. It gets the method from `Universe::is_substitutable_method()`. `JavaCalls::call` runs the pre-resolved method without initializing its holder class. `InterpreterRuntime::is_substitutable` makes the same upcall, but it calls `method_holder()->initialize(...)` first. `is_same_object` has no such call.

An automated post-integration audit of JDK-8391022 found the missing call. JDK-8391022 added the same missing initialization before the upcall from `JVM_IHashCode`. Nobody has reported `is_same_object` failing, and nobody has worked out what a JNI caller would see if it made the first upcall.

## Fix

This change initializes `ValueObjectMethods` eagerly, which makes the on-demand initialization at each upcall site unnecessary. Once preview features are on, the class is used heavily anyway. If a lazy initialization ran before `initPhase1()`, it would have the same bootstrapping problem as an eager one. The eager approach also lets a debug build check every upcall. If the class is used before it is initialized, the check fails reliably, so future bootstrapping bugs show up instead of being hidden.

Two things had to change before the class could be initialized before `initPhase1()`:

- The static initializer of `ValueObjectMethods` read the system property `value.bsm.debug` to set `VERBOSE`. The system properties are not set up before `initPhase1()`, so the initializer threw `NullPointerException`. `VERBOSE` is now the constant `false`.
- Once `VERBOSE` no longer reads a property, `jdk.internal.misc.Unsafe` is the only prerequisite `ValueObjectMethods` has. `Unsafe` is now initialized earlier than before. It used to be initialized during `initPhase1()` as a dependency of `LazyConstantImpl`. `Charset` uses `LazyConstantImpl`, and `SystemProps` uses `Charset`.

Without preview features, the initialization sequence is unchanged.

## Changes

- `threads.cpp`, `Threads::initialize_java_lang_classes`: when Valhalla (preview) is enabled, initialize `ValueObjectMethods` right after `UnsafeConstants` and before `initPhase1()`.
- `ValueObjectMethods.java`: `VERBOSE` is the constant `false`. The class comment says that the class is initialized very early and must keep minimal dependencies.
- `universe.cpp`: `Universe::is_substitutable_method()` and `Universe::value_object_hash_code_method()` assert that `ValueObjectMethods` is initialized. The messages are `value object comparison occurring too early` and `value object hashcode occurring too early`.
- `interpreterRuntime.cpp`, `InterpreterRuntime::is_substitutable`, and `jvm.cpp`, `JVM_IHashCode`: remove the `method_holder()->initialize(...)` calls.
- `c1_Runtime1.cpp`, `Runtime1::substitutability_check`: get the method from `Universe::is_substitutable_method()` and call `JavaCalls::call`, as the other sites do. The old code called `JavaCalls::call_static` with the class, method name, and signature. That resolved the method again and initialized the class as a side effect of resolution.
- `sharedRuntime.cpp`, `SharedRuntime::find_callee_info_helper` (the C2 path): remove the `ValueObjectMethods_klass()->initialize(...)` call. The debug-only lookup of `isSubstitutable` by name and signature is replaced by an assert against `Universe::is_substitutable_method()`.

`jniHandles.cpp` does not change. Because the class is now initialized at startup, `is_same_object` does not need an initialization call of its own.

## `VERBOSE`

`VERBOSE` stays, and it defaults to `false`. With the property gone, turning debug output on already means editing the source and recompiling. Even so, keeping the flag means a developer changes one line instead of adding the logging code back.

## Testing

This change adds no new test. In debug builds, the new asserts check every upcall. I ran these locally:

- all Valhalla tests
- tiers 1–3
- the `--enable-preview` subset of tier 7

- [x] I confirm that I make this contribution in accordance with the [OpenJDK Interim AI Policy](https://openjdk.org/legal/ai).
