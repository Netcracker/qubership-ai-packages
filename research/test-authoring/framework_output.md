# Measured failure output per framework

Measured on 2026-09-06 on macOS (arm64) with the versions named in each section. `expected = 0`, `actual = -1`
throughout, from a function `ensureBytes(-1)` that returns its argument. Each line is the exception message the
assertion raised, with newlines shown as `\n`; the runner adds the test name and the location around it.

## JUnit Jupiter 6.1.3 (`org.junit.jupiter.api.Assertions`)

```text
assertTrue(expected == actual)               expected: <true> but was: <false>
assertTrue(expected == actual, msg)          ensureBytes(-2147483648) must refuse ==> expected: <true> but was: <false>
assertEquals(expected, actual)               expected: <0> but was: <-1>
assertEquals(expected, actual, msg)          ensureBytes(-2147483648) ==> expected: <0> but was: <-1>
assertEquals(expected, actual, () -> msg)    ensureBytes(-2147483648) ==> expected: <0> but was: <-1>
assertEquals("Hello world", "Hello, world")  expected: <Hello world> but was: <Hello, world>
assertNotNull(null)                          expected: not <null>
assertThrows(IAE, () -> throw ISE)           Unexpected exception type thrown, expected: <java.lang.IllegalArgumentException> but was: <java.lang.IllegalStateException>
assertThrows(IAE, () -> {})                  Expected java.lang.IllegalArgumentException to be thrown, but nothing was thrown.
fail()                                       (empty message)
fail(msg)                                    ensureBytes(-2147483648) returned instead of throwing
assertAll(two failing)                       Multiple Failures (2 failures)\n  first ==> expected: <1> but was: <2>\n  second ==> expected: <3> but was: <4>
assertArrayEquals({1,2,3}, {1,2,4})          array contents differ at index [2], expected: <3> but was: <4>
assertIterableEquals(...)                    iterable contents differ at index [2], expected: <3> but was: <4>
```

The message argument is last (a `String` or a `Supplier<String>`), and the framework appends its own `expected/was`
clause after `==>`. A message on `assertTrue` therefore still reports only `true` and `false`.

## AssertJ 3.27.7

```text
assertThat(actual).isEqualTo(expected)                  \nexpected: 0\n but was: -1
assertThat(actual).as("ensureBytes(%d)", n).isEqualTo   [ensureBytes(-2147483648)] \nexpected: 0\n but was: -1
assertThat(expected == actual).isTrue()                 \nExpecting value to be true but was false
assertThat(List.of(1,2,3)).contains(4)                  \nExpecting ListN:\n  [1, 2, 3]\nto contain:\n  [4]\nbut could not find the following element(s):\n  [4]
```

The description set by `as(...)` is prefixed in brackets and must be called before the assertion method.

## Google Truth 1.4.5

```text
assertThat(actual).isEqualTo(expected)                              expected: 0\nbut was : -1
assertWithMessage("ensureBytes(-2147483648)").that(actual)...       ensureBytes(-2147483648)\nexpected: 0\nbut was : -1
assertThat(expected == actual).isTrue()                             expected to be true
assertThat(List.of(1,2,3)).contains(4)                              expected to contain: 4\nbut was            : [1, 2, 3]
```

## Hamcrest 3.0

```text
assertThat(actual, is(expected))                          \nExpected: is <0>\n     but: was <-1>
assertThat("ensureBytes(-2147483648)", actual, is(...))   ensureBytes(-2147483648)\nExpected: is <0>\n     but: was <-1>
assertThat("ensureBytes(-2147483648)", expected == actual)  ensureBytes(-2147483648)
```

The reason argument is first in Hamcrest, last in JUnit.

## Go 1.27.1 (`testing`)

```text
--- FAIL: TestEnsureBytes (0.00s)
    --- FAIL: TestEnsureBytes/negative_count_is_refused (0.00s)
        m_test.go:7: ensureBytes(-1) = -1, want 0
    --- FAIL: TestEnsureBytes/bare_fatal (0.00s)
        m_test.go:10: mismatch
    --- FAIL: TestEnsureBytes/no_message (0.00s)
--- FAIL: TestTable (0.00s)
    --- FAIL: TestTable/case_3 (0.00s)
        m_test.go:18: ensureBytes(-1) = -1, want 0
```

The runner prints the file and line before every message; `t.Fail()` with no message prints the name and nothing else;
spaces in a subtest name become underscores.

## pytest 8.4.2

```text
assert ensure_bytes(-1) == 0               E   assert -1 == 0
                                           E    +  where -1 = ensure_bytes(-1)
ok = ensure_bytes(-1) == 0; assert ok      E   assert False
assert ensure_bytes(-1) == 0, "msg"        E   AssertionError: ensure_bytes(-1)
                                           E   assert -1 == 0
                                           E    +  where -1 = ensure_bytes(-1)
pytest.fail()                              E   Failed
parametrize ids=["minus one"]              test_param[minus one]      (the id is the node id suffix)
with pytest.raises(ValueError): ...        E   Failed: DID NOT RAISE ValueError
```

The short summary line carries the node id and the first line of the message: `FAILED test_m.py::test_assert_ok -
assert False`.

## Rust 1.98.0 (`cargo test`)

```text
assert_eq!(ensure_bytes(-1), 0)               assertion `left == right` failed\n  left: -1\n right: 0
assert!(ensure_bytes(-1) == 0)                assertion failed: ensure_bytes(-1) == 0
assert!(ensure_bytes(-1) == 0, "msg")         ensure_bytes(-1)          (the message replaces the expression text)
assert_eq!(ensure_bytes(-1), 0, "msg {}", n)  assertion `left == right` failed: ensure_bytes(-1)\n  left: -1\n right: 0
panic!()                                      explicit panic
#[should_panic(expected = "negative")]        panic message: "boom"\n expected substring: "negative"
```

## Node 26.8.1 (`node:test`, `node:assert/strict`)

```text
assert.strictEqual(ensureBytes(-1), 0)          Expected values to be strictly equal:\n\n-1 !== 0
assert.ok(ensureBytes(-1) === 0)                The expression evaluated to a falsy value:\n\n  assert.ok(ensureBytes(-1) === 0)
assert.ok(ensureBytes(-1) === 0, "msg")         ensureBytes(-1) must return 0        (actual: false, expected: true)
assert.strictEqual(ensureBytes(-1), 0, "msg")   ensureBytes(-1)\n\n-1 !== 0
assert.deepStrictEqual({..}, {..})              Expected values to be strictly deep-equal:\n+ actual - expected\n  (line diff)
assert.throws(fn, RangeError)                   The error is expected to be an instance of "RangeError". Received "TypeError"
assert.fail()                                   Failed
```

The runner prints `test at m.test.mjs:5:3` and the `describe` and `it` strings above each failure. A message on
`assert.ok` replaces the generated expression text rather than adding to it.

## JUnit 4.13.2 (`org.junit.Assert`, run through `junit-vintage-engine` 6.1.3)

Measured on 2026-09-07, same machine, same `ensureBytes(-1)`.

```text
assertEquals(expected, actual)               expected:<0> but was:<-1>
assertEquals(msg, expected, actual)          ensureBytes(-1) expected:<0> but was:<-1>
assertEquals("Hello world", "Hello, world")  org.junit.ComparisonFailure: expected:<Hello[] world> but was:<Hello[,] world>
assertTrue(expected == actual)               java.lang.AssertionError            (no message at all)
assertTrue(msg, expected == actual)          ensureBytes(-1) must refuse
assertNotNull(null)                          java.lang.AssertionError            (no message at all)
assertArrayEquals({1,2,3}, {1,2,4})          arrays first differed at element [2]; expected:<3> but was:<4>
assertArrayEquals(msg, ...)                  arrays: arrays first differed at element [2]; expected:<3> but was:<4>
assertThrows(IAE, () -> throw ISE)           unexpected exception type thrown; expected:<java.lang.IllegalArgumentException> but was:<java.lang.IllegalStateException>
assertThrows(IAE, () -> {})                  expected java.lang.IllegalArgumentException to be thrown, but nothing was thrown
@Test(expected = IAE.class), nothing thrown  Expected exception: java.lang.IllegalArgumentException
fail()                                       java.lang.AssertionError            (no message at all)
fail(msg)                                    ensureBytes(-1) returned instead of throwing
ErrorCollector, two checkThat failures       Multiple Failures (2 failures)\n\tjava.lang.AssertionError: first\nExpected: is <1>\n     but: was <2>\n\t... second ...
@RunWith(Parameterized), default name        refused[0], refused[1]
@Parameters(name = "{index}: ensureBytes({0}) is refused")   refused[0: ensureBytes(-1) is refused]
```

The message argument is first. `assertTrue`, `assertNotNull`, and `fail()` without a message raise an
`AssertionError` whose message is null, so the report shows the class name and nothing else.

## Mockito 5.23.0 (`mockito-junit-jupiter`, `MockitoExtension`, default strictness)

```text
verify(sender).send("bob", "hello bob"), never called
    Wanted but not invoked:\nsender.send("bob", "hello bob");\n-> at m.MockitoStrictTest.neverCalled(MockitoStrictTest.java:12)\nActually, there were zero interactions with this mock.
verify(sender).send("bob", "hi bob"), called with "hello bob"
    Argument(s) are different! Wanted:\nsender.send("bob", "hi bob");\n-> at ...\nActual invocations have different arguments at position [1]:\nsender.send("bob", "hello bob");\n-> at m.Notifier.notify(Notifier.java:5)
verify(sender, times(2)).send(anyString(), anyString()), called once
    sender.send(<any string>, <any string>);\nWanted 2 times:\n-> at ...\nBut was 1 time:\n-> at m.Notifier.notify(Notifier.java:5)
verifyNoMoreInteractions(sender) with one unverified call
    No interactions wanted here:\n-> at ...\nBut found this interaction on mock 'sender':\n-> at m.Notifier.notify(Notifier.java:5)\nActually, above is the only interaction with this mock.
when(sender.lookup("k")).thenReturn("v"), never called (strict stubs)
    org.mockito.exceptions.misusing.UnnecessaryStubbingException: Unnecessary stubbings detected. ... Following stubbings are unnecessary ...:\n  1. -> at m.MockitoStrictTest.unusedStub(MockitoStrictTest.java:10)
```

Each failure names the mock, the wanted call with its arguments, and the location of both the verification and the
actual call. The unnecessary-stubbing check runs after the test body and fails the test even where every assertion
passed.

## jetCheck 0.3.0

```text
PropertyChecker.forAll(Generator.integers(), n -> ensureBytes(n) >= 0)
    org.jetbrains.jetCheck.PropertyFalsified:
    Falsified on -1
    Shrunk in 28 stages, by trying 31 examples

    To re-run the minimal failing case, run
      PropertyChecker.customized().rechecking("8Kaashzk7pPUHgH/////Hw==")
        .forAll(...)
    To re-run the test with all intermediate shrinking steps, use `recheckingIteration(-2079737578537190492L, 1)` instead for last iteration, or `withSeed(-2079737578537190492L)` for all iterations
PropertyChecker.customized().withSeed(42L).forAll(...)    same shape; the seed in the message is 42L
```

## ArchUnit 1.5.0

```text
classes().that().implement(Handler.class).should().haveSimpleNameEndingWith("Handlr").check(prod)
    java.lang.AssertionError:
    Architecture Violation [Priority: MEDIUM] - Rule 'classes that implement m.Handler should have simple name ending with 'Handlr'' was violated (2 times):
    Class <m.AHandler> does not have simple name ending with 'Handlr' in (AHandler.java:0)
    Class <m.BHandler> does not have simple name ending with 'Handlr' in (BHandler.java:0)
JavaClasses stream mapped to Kind, compared with Set.of(Kind.values()) via assertEquals
    kinds with a Handler implementation ==> expected: <[A, B, C]> but was: <[A, B]>
```

The rule's own text is the message, and every violating class is listed with its source file.

## testify 1.12.1 (`assert`, `require`) on Go 1.27.1

```text
assert.Equal(t, 0, EnsureBytes(-1))                 Error:      \tNot equal: \n expected: 0\n actual  : -1
assert.Equal(t, 0, EnsureBytes(-1), "ensureBytes(%d)", -1)   the same, then   Messages:   \tensureBytes(-1)
assert.Equal(t, "Hello world", "Hello, world")      Not equal: expected: "Hello world" actual  : "Hello, world" then Diff: --- Expected +++ Actual @@ -1 +1 @@ -Hello world +Hello, world
assert.Equal(t, P{1, 2}, P{1, 3})                   Not equal: expected: m.P{A:1, B:2} actual  : m.P{A:1, B:3} then a field-level Diff
assert.True(t, EnsureBytes(-1) == 0)                Should be true
assert.True(t, ..., "ensureBytes(-1) must refuse")  Should be true \n Messages:   \tensureBytes(-1) must refuse
assert.ErrorIs(t, errors.New("other"), ErrNeg)      Target error should be in err chain:\n expected: "negative"\n in chain: "other"
assert.EqualError(t, errors.New("other"), "negative")   Error message not equal:\n expected: "negative"\n actual  : "other"
assert.NoError(t, errors.New("boom"))               Received unexpected error:\n boom
require.Equal(t, 0, EnsureBytes(-1)); t.Log(...)    the same message; the t.Log line is not reached
two assert.Equal in one test                        both failures printed, one block each
```

Every block is prefixed by `Error Trace:` with the absolute file path and line, and suffixed by `Test:` with the
test name.

## ArchUnit 1.5.0, `beAnnotatedWith` (measured 2026-09-07, after the first ArchUnit block above)

```text
classes().that().implement(Handler.class).should().beAnnotatedWith(Handles.class).check(prod)
    Architecture Violation [Priority: MEDIUM] - Rule 'classes that implement m.Handler should be annotated with @Handles' was violated (1 times):
    Class <m.BHandler> is not annotated with @Handles in (BHandler.java:0)
JavaClasses stream filtered by isAnnotatedWith(Handles.class), mapped to the annotation value, against EnumSet.allOf(Kind.class)
    kinds with a Handler implementation ==> expected: <[A, B, C]> but was: <[A]>
```

The interface in the rule text is fully qualified; the annotation is its simple name with `@`.

## Jest 30.5.0 on Node 26.8.1

```text
expect(ensureBytes(-1)).toBe(0)                 expect(received).toBe(expected) // Object.is equality\n\nExpected: 0\nReceived: -1
expect({a:1,b:2}).toEqual({a:1,b:3})            expect(received).toEqual(expected) // deep equality\n\n- Expected  - 1\n+ Received  + 1\n(line diff)
expect(ensureBytes(-1) === 0).toBe(true)        Expected: true\nReceived: false
expect(ensureBytes(-1) === 0).toBeTruthy()      expect(received).toBeTruthy()\n\nReceived: false
expect(() => { throw new TypeError('boom') }).toThrow(RangeError)   Expected constructor: RangeError\nReceived constructor: TypeError\n\nReceived message: "boom"
expect(() => {}).toThrow(RangeError)            Expected constructor: RangeError\n\nReceived function did not throw
it.each([[-1],[-2]])('ensureBytes(%d) is refused', ...)   ensureBytes › ensureBytes(-1) is refused
```

The failure header is `● describe › it`, and a code frame follows every message.

## Vitest 5.0.0 on Node 26.8.1

```text
expect(ensureBytes(-1)).toBe(0)                 AssertionError: expected -1 to be +0 // Object.is equality\n\n- Expected\n+ Received\n\n- 0\n+ -1
expect(ensureBytes(-1), 'ensureBytes(-1)').toBe(0)   AssertionError: ensureBytes(-1): expected -1 to be +0 // Object.is equality (then the same diff)
expect({a:1,b:2}).toEqual({a:1,b:3})            AssertionError: expected { a: 1, b: 2 } to deeply equal { a: 1, b: 3 } (then a line diff)
expect(ensureBytes(-1) === 0).toBe(true)        AssertionError: expected false to be true // Object.is equality\n\n- true\n+ false
expect(ensureBytes(-1) === 0).toBeTruthy()      AssertionError: expected false to be truthy\n\n- true\n+ false
expect(() => { throw new TypeError('boom') }).toThrow(RangeError)   AssertionError: expected error to be instance of RangeError\n\n- Expected:\n[Function RangeError]\n\n+ Received:\nTypeError {\n  "message": "boom",\n}
expect.soft twice, both failing                 two FAIL blocks for the one test (10 failures reported for 9 tests)
it.each([[-1],[-2]])('ensureBytes(%d) is refused', ...)   vitest.test.mjs > ensureBytes > ensureBytes(-1) is refused
```

The failure header is `FAIL file > describe > it`, and a code frame follows every message.

## Node 26.8.1, `t.plan` and the assertion module

```text
t.plan(1); await Promise.resolve(); assert.strictEqual(1, 1)            'plan expected 1 assertions but received 0'   (module assert is not counted)
t.plan(1); await Promise.resolve(); t.assert.strictEqual(1, 1)          passes
t.plan(1); Promise.resolve().then(() => t.assert.strictEqual(1, 1))     passes: the microtask ran before the test ended
```

The plan counts only assertions made through `t.assert`, and an assertion that runs in a microtask before the test
function returns still counts.

## pytest 8.4 (uv, Python 3.12), assertion rewriting in an imported helper

```text
def check(value): assert value == 0    in helper.py, called from the test     E   AssertionError            (no operands)
the same, with pytest.register_assert_rewrite("helper") in conftest.py        E   assert -1 == 0
assert ensure_bytes(-1) == 0           in the test module                     E   assert -1 == 0\nE    +  where -1 = ensure_bytes(-1)
```
