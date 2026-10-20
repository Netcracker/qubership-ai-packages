# Task

Write the pull request description for the change below, in Markdown, ready to paste into GitHub. The facts come from
the author's notes, which were checked against the code; treat every fact in them as verified, and add none that they
do not carry.

## Repository facts

- Repository: openjdk/jdk. Target branch: `master`. The Skara bot integrates the pull request as one commit whose
  message is the JBS issue number and title followed by `Reviewed-by:` lines; neither the branch commits nor the
  description reach `git log`.
- JBS issue: JDK-8393327, "Missed ValueObjectMethods class initialization in JNIHandles::is_same_object". The pull
  request title is the issue number and title, and the bot checks it.
- The description template ends with one checkbox, which stays:
  `- [x] I confirm that I make this contribution in accordance with the [OpenJDK Interim AI Policy](https://openjdk.org/legal/ai).`

## The author's notes

### How the defect was found

An automated post-integration audit of JDK-8391022 (which fixed a missing initialization of `ValueObjectMethods` before
an upcall from `JVM_IHashCode`) confirmed that fix and flagged one more upcall without the initialization:
`JNIHandles::is_same_object`. It upcalls `ValueObjectMethods.isSubstitutable` through `JavaCalls::call` with the method
from `Universe::is_substitutable_method()`, the same way `InterpreterRuntime::is_substitutable` does, but without the
`method_holder()->initialize(...)` call that `InterpreterRuntime::is_substitutable` makes first. `JavaCalls::call` runs
the pre-resolved method without initializing its holder class. Nobody has reported `is_same_object` failing, and nobody
worked out what a JNI caller would see if it ran first.

### The issue discussion

- A reviewer asked why `ValueObjectMethods` is not initialized eagerly, which would make each missing on-demand
  initialization harmless, since the class is used heavily once preview features are on.
- The author agreed in principle, then found that `ValueObjectMethods` could not be initialized before
  `System.initPhase1()`: its static initializer read the system property `value.bsm.debug` to set `VERBOSE`, and
  before `initPhase1()` the system properties are not set up, so the initializer threw `NullPointerException`. The
  author first proposed initializing it right after `initPhase1()`, and worried that Java code running before that
  point could start to perform a value object comparison as more of the JDK uses value classes.
- The reviewer answered that a lazy initialization before `initPhase1()` is the same bootstrapping problem either way,
  and that with eager initialization a check can fail reliably when the class is used before it is initialized, which
  exposes future bootstrapping bugs instead of hiding them. The author adopted that.
- `jdk.internal.misc.Unsafe` is the only prerequisite `ValueObjectMethods` has once `VERBOSE` no longer reads a
  property. Before this change, `Unsafe` was initialized during `initPhase1()`, as a dependency of
  `LazyConstantImpl`, which `Charset` uses, which `SystemProps` uses.

### The change, file by file

- `threads.cpp`, `Threads::initialize_java_lang_classes`: when Valhalla (preview) is enabled, initialize
  `ValueObjectMethods` right after `UnsafeConstants`, before `initPhase1()`. This initializes `Unsafe` too, earlier
  than before. Without preview the sequence is unchanged.
- `ValueObjectMethods.java`: `VERBOSE` is now the constant `false` instead of reading `value.bsm.debug`; the class
  comment says the class is initialized very early and must keep minimal dependencies.
- `universe.cpp`: `Universe::is_substitutable_method()` and `Universe::value_object_hash_code_method()` now assert
  that `ValueObjectMethods` is initialized, with the messages `value object comparison occurring too early` and
  `value object hashcode occurring too early`.
- `interpreterRuntime.cpp`, `InterpreterRuntime::is_substitutable`, and `jvm.cpp`, `JVM_IHashCode`: the
  `method_holder()->initialize(...)` calls are removed.
- `c1_Runtime1.cpp`, `Runtime1::substitutability_check`: it called `JavaCalls::call_static` with the class, method
  name, and signature, which resolved the method again and initialized the class as a side effect of resolution; it
  now takes the method from `Universe::is_substitutable_method()` and calls `JavaCalls::call`, as the other sites do.
- `sharedRuntime.cpp`, `SharedRuntime::find_callee_info_helper` (the C2 path): the
  `ValueObjectMethods_klass()->initialize(...)` call is removed, and the debug-only lookup of `isSubstitutable` by name
  and signature is replaced by an assert against `Universe::is_substitutable_method()`.
- `jniHandles.cpp` is not changed: with the class initialized at startup, `is_same_object` needs no call of its own.

### The review

- A reviewer asked whether `VERBOSE` should be removed altogether, since turning it on now means editing the source
  and recompiling anyway. Another reviewer and the author answered that the flag is still useful: debug output is
  turned on by changing one line rather than adding the logging code back. `VERBOSE` stays, defaulting to `false`.
- The reviewer who proposed eager initialization approved with: that is what they wanted to see instead of plugging
  yet another missing initialization point.

### Testing

There is no new test: the new asserts check every upcall in debug builds. The author ran all Valhalla tests locally,
tiers 1 to 3, and the `--enable-preview` subset of tier 7.
