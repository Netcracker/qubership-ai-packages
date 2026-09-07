# Mockito

How the shapes of `SKILL.md` §5 and §6 look with Mockito, what a verification failure prints, and which of its checks
the reviewer reads as a signal. The rules that use this file are in `SKILL.md` §5, §6, and §7.

## What a verification failure prints

| Call | Message on failure |
| --- | --- |
| `verify(sender).send("bob", "hello bob")`, never called | `Wanted but not invoked:` the call, its location, and `Actually, there were zero interactions with this mock.` |
| `verify(sender).send("bob", "hi bob")`, called with `"hello bob"` | `Argument(s) are different! Wanted:` the call, then `Actual invocations have different arguments at position [1]:` and the actual call with its location |
| `verify(sender, times(2)).send(…)`, called once | `Wanted 2 times:` and `But was 1 time:`, each with a location |
| `verifyNoMoreInteractions(sender)` with an unverified call | `No interactions wanted here:` then `But found this interaction on mock 'sender':` with the call's location |
| A stub the test never used, under `MockitoExtension` | `UnnecessaryStubbingException: Unnecessary stubbings detected.` with the stub's line, after the test body |

Every failure names the mock, the wanted call with its arguments, and the location of both the verification and the
actual call, so a message on `verify` has nothing to add.

## Which shapes the diff shows

- **A mock of the unit under test, or of the collaborator the test names**, is §5's row *The unit under test, or the
  collaborator the test names, replaced by a mock*. `spy(unit)` and `doReturn(…).when(unit)` on the class the test is
  named for are the same shape.
- **A `verify` as the only assertion**, or `verify` of a query (`verify(repo).findById(1)`), is §6's *Verify state,
  not interactions*. Assert the value the unit returned or the state it left. Verify a call only where the call is the
  contract: a state-changing call to a collaborator outside the unit, whose arguments an `ArgumentCaptor` reads so
  that the assertion is on the state that crossed the boundary and `assertEquals` prints it; or a call the behavior
  promises to avoid, where `verify(backend, times(1)).load(key)` after two reads is what establishes the cache hit.
- **`verifyNoInteractions`, `verify(…, times(n))`, and `InOrder`** are right where the contract defines the absence,
  the count, or the order: `verifyNoInteractions(sender)` after rejected input, `verify(backend, times(1))` for a
  cache hit, an `InOrder` that puts the commit before the notification. `verifyNoMoreInteractions` over every
  collaborator and an `InOrder` over an incidental sequence pin the mechanism and fail on the next refactoring.
- **`mock(SomeLibraryClass.class)`** is §6's *Do not mock types you do not own*; wrap the type and fake the wrapper.
- **`when(…).thenReturn(…)` on a method the test then asserts** is §5's row *An assertion on the mock*: the assertion
  is on the configured return value.

## Strictness

`MockitoExtension` defaults to strict stubs: a stub the test never used fails the test after its body, and a stubbed
method reached from the code under test with other arguments fails at that call. The JUnit 4 `MockitoJUnitRunner`
reports only the unused stub; `MockitoJUnitRunner.StrictStubs` adds the argument check. Keep the strict default. A
`lenient()` or `@MockitoSettings(strictness = LENIENT)` in a new test is a stub that does not belong to the behavior
under test, and the reviewer asks why it is there. A mock created with `Mockito.mock()` outside the
extension is lenient, which hides the same signal.
