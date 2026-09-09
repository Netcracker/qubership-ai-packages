---
name: test-authoring
description: >-
  Load before writing, editing, or reviewing a test in any language, and at the end of a coding task
  that changed behavior ("fix the bug", "add the method"): the change owes tests, and this skill
  decides which. Also load when asked whether a change is tested enough, at which level a test
  belongs (unit, integration, end to end), why a test is flaky, whether a test could fail at all,
  how to name a test or a parameterized case, which assertion to use and what it prints, how to
  fake or mock a dependency, when a property-based or an exhaustiveness test is owed, or how to read
  a mutation or coverage report. Its references cover JUnit 4, JUnit 5 and 6, AssertJ, Truth,
  Hamcrest, Mockito, jetCheck, ArchUnit, pytest, Go testing and testify, cargo test, Jest, Vitest,
  and node:test. Wording belongs to the developer-style skill of the repository's language, and the
  comment above a test to the doc-comment skill of its programming language; load those too.
---

# Authoring a test

This skill governs **what a test establishes, at which level, with which inputs, and how its failure reads**. Wording,
tone, and the phrasing of a name or a message once its content is decided belong to the developer-style skill of the
language the repository writes in: `english-developer-style` unless the repository's instructions name another, such
as `russian-developer-style` or `french-developer-style`; load it too. The comment or docstring above a test belongs
to the doc-comment skill of its programming language (`javadoc-authoring`, `godoc-authoring`, `pythondoc-authoring`,
`rustdoc-authoring`, `jsdoc-authoring`). The commit message and the pull request description belong to
`change-description-authoring`.

## 0. Which references to open

The rules below hold in every framework. What each framework prints, which of its assertions carry the values, where
the message goes, and how a case is named are in `references/`, one file per **role** a library plays in the test,
grouped by ecosystem. **Before writing the first assertion, read the file for the project's test engine and the file
for its assertion library** (a matcher library on JUnit adds the JUnit assertions file, as the rule on report forms
below says). Open the other roles' files where the change calls for them, and no other.

| Role | Decides | Files |
| --- | --- | --- |
| Test engine | The container and the name in the report (§7), parameterized case names, random order (§8) | `java/junit5.md` (JUnit 5 and 6), `java/junit4.md`, `python/pytest.md`, `go/testing.md`, `rust/libtest.md`, `javascript/jest.md`, `javascript/vitest.md`, `javascript/node-test.md` |
| Assertion library | Which call prints the operands, the operand order, where the message goes, grouped assertions, error assertions (§7) | `java/junit5-assertions.md`, `java/junit4-assert.md`, `java/assertj.md`, `java/truth.md`, `java/hamcrest.md`, `go/testify.md`. pytest, Go `testing`, cargo test, Jest, Vitest, and `node:test` are both engine and assertions, and their engine file covers this role |
| Test doubles | How the shapes of §5 and §6 look in the library, what a verification failure prints | `java/mockito.md` |
| Property-based testing | The seed, the reproducer, the explicit example a counterexample becomes (§4) | `java/jetcheck.md` |
| Structural tests | The test on an open set of classes (§4) | `java/archunit.md` |
| Mutation | What the tool's verdicts mean (§1, §10) | `mutation-tools.md`, one table covering every ecosystem |

Which files, in this order:

1. **The repository's instructions name the stack.** A line such as `Tests: JUnit 5 engine, JUnit 5 assertions;
   Mockito for doubles; jetCheck for property-based tests; ArchUnit for structural tests` selects the files, and
   nothing else is opened. Where the line is missing, propose it in the first pull request that writes a test under
   this skill, and not in the later ones; it names the major version and no more.
2. **Otherwise the imports of the nearest existing test of the same unit decide** (`org.junit.jupiter` against
   `org.junit.Test`, `org.assertj` against `org.junit.jupiter.api.Assertions`), then the build file. §9 already
   requires reading that test. In a repository with more than one test stack, the stack is the module's, not the
   repository's: the nearest test and the module's build file decide, and a stack line in the module's own
   instructions beats one at the root.
3. **The report rules of §7 come from the assertion library's file, never from the engine's.** `assertAll` is
   JUnit's grouping and `assertSoftly` AssertJ's; a project on AssertJ does not get the JUnit form because its engine
   is JUnit. A matcher library on JUnit (Hamcrest, Truth) borrows grouping and throw assertions from the JUnit
   assertions file, so such a project opens both.
4. **A reference is written for the latest minor of the major it names**, and marks no minor of its own. Where the
   project resolves an older minor and a call the reference names does not exist there, use the form that does. The
   compiler says so on the JVM, in Go, and in Rust; pytest, Jest, Vitest, and `node:test` say so at collection or on
   the first run; and the resolved version is one `grep` of the lock or build file away when a call looks new. A
   file covers one major, and where two majors differ in how a test is written they have two files (`junit4.md`,
   `junit5.md`).
5. **A role whose library has no file here** (Spock, Kotest, RSpec, PHPUnit, xUnit.net, GoogleTest, a doubles
   library other than Mockito, a property tool other than jetCheck) still follows the section that names the role.
   Take §7's report rules from the library itself: write one deliberately failing assertion in each form the change
   needs, read what it prints, and keep the form that prints the operands. Do not substitute the nearest file: a
   JUnit form inside an AssertJ test compiles and reports worse.

## 1. The correction that matters most

**A test exists to fail.** Its value is the production change it would catch, and a test that stays green under every
change of the code has established nothing, however many assertions it carries. The writer of the test is usually the
writer of the change, is rewarded when the suite is green, and can reach green by asserting less, by mocking the unit
under test, by computing the expected value with the code under test, or by restating the implementation. Every rule
below therefore says what a reviewer checks, because the letter of a rule can be satisfied by a test worth nothing.

**The test for a test is the change that breaks it, not the run that passes it.** Before writing the body, name the
production change that would make this test fail, and confirm that the change is a bug and not a decision. If the only
thing that would fail the test is a renamed field, a reordered call, or a changed constant, the test guards a decision
and will fire on the next redesign while sleeping through the next bug (§5, the change detector). If nothing you can
name would fail it, do not write it.

Two oracles turn that judgment into evidence, and a reviewer may ask for either:

- **Red on the base commit.** A regression test is observed failing on the code before the fix and passing after it,
  and the pull request carries the evidence: the test in its own commit ahead of the fix, or the pasted failing output
  with its file and line. A test the reviewer has only been told exercises the bug is a claim. Check that the failure
  on the base commit names the bug's symptom, not a missing symbol.
- **A surviving mutant on a changed line.** Where the repository runs a mutation tool, read its verdict as the tool
  defines it: *no coverage* is a missing test; a mutant that does not compile is no information; *survived* on a line
  the change touched is a candidate gap, and the writer settles it. A survivor that changes behavior the
  specification defines is a missing or weak test, and the test is strengthened or added; a survivor that changes no
  observable behavior is equivalent, and is explained in the pull request, since no test is owed to tell two
  equivalent implementations apart; a survivor the writer cannot place is reported as unresolved, not as covered.
  Scope the run to the diff.

**A coverage figure is evidence of neither.** A line can be executed by a test that asserts nothing about it, so
`coverage is 92%` in a pull request answers no question about whether a test can fail. Do not offer it, and do not
demand it as the gate; ask for the red run or the mutation verdict.

## 2. The four readers

A test is read in four situations, and the same line is essential to one reader and noise to another. Every rule
below names the reader it exists for.

| Reader | Situation | Holds |
| --- | --- | --- |
| **T1 Red-build reader** | A test just failed, often in CI, often not their own | The runner's report: the container, the test name, the message, the values, the stack trace; frequently no IDE |
| **T2 Reviewer** | Deciding whether a change is adequately tested | The diff of the code and of the tests |
| **T3 Refactorer** | Changing the implementation with the behavior fixed | A green suite, and the expectation that it stays green |
| **T4 Next author** | Adding a case, a feature, or a fix beside existing tests, or reading them as the examples the documentation lacks | The test directory, and the question of where the new test goes and at which level |

The test, applied to every test and every line in it: **name the reader and what they learn from it.** T1 learns what
broke from the report alone; T2 learns which change the test would catch; T3 learns nothing, because a good test does
not mention them; T4 learns where the next case goes.

## 3. What a change owes in tests

**A change owes no test when it cannot change behavior.** A rename, a move, a formatting pass, a comment, and a
regenerated file whose output is unchanged owe nothing; the pull request says so in one line. A dependency bump, a
regeneration whose output moved, and a build or configuration change are the other case: they can change behavior,
and an unchanged green suite is evidence only over the surface that suite already covers. Name that surface, or test
the behavior the bump was made for. A test written for a change that cannot alter behavior asserts the decision
rather than the behavior, which is §5's change detector.

**Otherwise, choose the smallest level at which the changed behavior is observable through the unit's interface, and
state the choice.** Levels are defined by what a test may touch, not by how much code it covers: a small test runs in
one process with no network, database, file system, sleep, or system property; a medium test may use the local
machine; a large test spans machines. These three names are this skill's. Where the repository says unit,
integration, and end to end, unit maps to small, integration to medium or to a small test with a real in-process
dependency, and end to end to large; choose by the definitions above, and write the repository's own name in the pull
request and in the directory the test lands in. A change owes its first test at the smallest level that can observe
it. It owes a second, larger test where that test establishes a failure mode the smaller one cannot: the wiring
between components, the behavior of a real dependency a fake cannot reproduce, persistence, or a contract that
crosses a process boundary (bytes on a socket, a schema, a message format, a value read from the deployment
environment). The process boundary is the usual case, not the definition. Where a larger test that exercises the
path already exists, name it in the pull request instead of adding one.

**A change made for speed or memory owes a test of the behavior it preserves and a measurement of the improvement.**
Assert that the result and the observable state are what they were, on the inputs the optimization special-cases and
on the one it does not. Measure the improvement where the repository measures: its benchmark job, its allocation or
operation-count check, a deterministic count the test can assert (calls to the backend, bytes copied, allocations
under a tracking allocator). Where none exists, the measurement is a before-and-after figure in the pull request with
the conditions it was taken under. A wall-clock bound in an ordinary functional test is §8's assertion range that
excludes valid outputs, and it fails on a loaded CI runner rather than on a regression.

**A deliberate behavior change updates the tests that encode the old behavior, and names them.** Find them before
writing the new test: they are the ones that fail on the change. Each is either updated, because the behavior it
asserted is the behavior that moved, or kept, because it caught a defect in the change. The pull request names every
test whose expectation moved and the behavior that moved with it. A test edited until the suite is green, with no such
sentence, is §5 arriving through the diff of the tests.

The rows below are examples, not a list to match a change against. Write the row a change needs from the rule: name
what the changed behavior is observable through, then ask what a larger test would establish that the small one
cannot.

| Change | First test | Second test | What the reviewer checks |
| --- | --- | --- | --- |
| A bug fix in a private helper | Small, through the caller that reaches the helper, on the input that triggered the bug | None, unless a larger test would establish wiring, a real dependency, or persistence the small test cannot | The test reaches the helper through its caller, not by reflection or widened visibility; the red run on the base commit is in the pull request |
| A new method on a unit's interface | Small, one test per partition and boundary of its inputs (§4), through the method itself | Medium only where the outcome depends on a real dependency a fake cannot reproduce | The partition list against the specification; no mock of a collaborator where a fake exists |
| A change to an error or failure path | Small, on the input that triggers it, asserting the type or the sentinel and the state left behind | None, unless the error crosses a boundary in a form a peer reads | The assertion is on error semantics, not on the message string (§7); the state after the failure is asserted, not only the throw |
| A change to what crosses a process boundary: bytes on a wire, a schema, a message format, a serialized value | Small, feeding recorded or hand-built bytes or records to the reader with no socket or file | Medium, against the real peer or its wire-level fake, because the contract crossed a process boundary | The expected bytes are literals or captures, not produced by the writer under test; the medium test exists or is named |
| A change in a configuration default | Small, asserting the behavior the code shows when nothing is set, through the accessor the rest of the code reads | Medium or large, where the default is read at deployment and the change altered the deployment path | The test asserts the behavior that depends on the default, not that the constant equals itself |

Three questions tell a chosen level from a defaulted one: does the pull request name the level; does the small test
mock the very boundary the change altered, which establishes nothing about that boundary; does an existing larger
test already cover the path. `Covered by the integration tests` with no test name is a claim, not an answer.

## 4. Which inputs

Inputs come from the signature and the specification, never from the branches of the implementation: a partition read
off an `if` in the code tests that the code does what the code does. **Partition the input whose handling the change
touched, not every input the signature has.** The other arguments keep the value the existing tests already use,
unless one of them can influence the changed behavior (another encoding, another mode, a prior state), and then it is
varied too: one test per partition of it that the changed behavior distinguishes, and the reviewer checks that each
such test would fail with the changed behavior wrong for that value alone. The decision table and the transition list
below are scoped the same way, to the conditions and the states the change reached.

- **One test per equivalence partition.** Partition each input into classes the specification treats alike, valid and
  invalid; the classes do not overlap and none is empty. One value stands for its whole class. A second value from
  the same class earns its place only where it is a boundary, a distinct representation (another encoding, a
  different collection shape, a Unicode form), an interaction with another input, or a known regression; otherwise
  it is a redundant test, not a stronger suite. Test each invalid class alone, because two invalid inputs in one call
  mask each other: the first one rejected hides whether the second would have been.
- **Each boundary and its neighbors.** For an ordered input, test the minimum, the maximum, and the value just outside
  each (two-value analysis); add the value just inside where a wrong operator is plausible, since `x <= 10` written as
  `x == 10` passes 10 and 11 and fails only on 9.
- **A decision table when the outcome depends on a combination of conditions.** One test per feasible column, so the
  happy column is not the only one tested.
- **A state-transition test when the behavior depends on history.** Every valid transition once; each invalid
  transition in its own test.
- **A property-based test for an invariant over a large domain**, where enumeration would list examples forever. It
  costs the T1 reader a reproducer. A failure carries what replays it: the seed or the reproduce blob the framework
  prints, or a seed the test pins where the framework prints none. Each shrunk counterexample the tool ever found
  is added as an explicit example, so that the failure can be rerun by name. Ordinary runs explore fresh inputs; a
  pinned seed is for replaying a failure, not for every run.
- **A test on an open set when the change adds a member to one**: a constant to an enum, an implementation to an
  interface, an entry to a registry, a type to a mapping. The test enumerates the set from the code (`values()`, a
  class-path scan) and asserts the property every member has to satisfy, or compares the set with the second place
  that enumerates it, so it fails on the next author who adds a member and handles it nowhere. Reading the set from
  the code is right here: the set is the input, and the property is still stated by hand, as §5's row *Expected value
  computed by the code under test* asks of the expected value. Where the compiler checks exhaustiveness (`match` on a
  Rust enum, `switch` on a sealed type, a `never` check in TypeScript), rely on it and write no test.

The partition set against the specification is a judgment no tool checks. Make it from the specification and the
existing tests, state it in the pull request, and stop when every partition of the changed input has one test, every
boundary of it has a case, every partition of a varied argument that the changed behavior distinguishes has one, and
every feasible column and transition the change reached has one, counting the tests that already exist. Ask about a
partition only where the specification leaves the expected behavior open.

## 5. A test that cannot fail

These are the shapes a writer optimizing for green produces, and each is visible in the diff. The T2 reader looks for
them first; a mutation run confirms most of them.

| Shape | How it shows in the diff | Repair |
| --- | --- | --- |
| No assertion, or a print of the result in its place | No `assert`, `expect`, or `verify` after the act; a `print` or `console.log` of the value | Assert the value the behavior defines |
| Expected value computed by the code under test, or by a helper that repeats its arithmetic | The expected operand calls production code; a loop builds both sides | A literal or a hand-derived fixture, checked against the specification, not pasted from the code's output |
| Assertion on a value the test itself supplied | The operand is a test-local object also used in setup, with no call on the unit between | Read the value back through the unit's interface |
| The unit under test, or the collaborator the test names, replaced by a mock | The mock target is the symbol the test name or the diff changed; a spy on the unit; a partial mock | Remove the double, or move it below the side effect the test depends on |
| An assertion on the mock | The operand is a configured return value; a `was called` check is the only assertion | Assert the unit's output; delete the assertion on the double. Where the call is the behavior (a notification sent, a row written), verify the recipient and the payload, as §6 allows |
| Passes only because nothing threw | A bare call; `assertDoesNotThrow` alone; `try { … } catch { fail() }` with no assertion after | Assert the returned value or the resulting state. Where completing without an exception is the contract (a second `close()` that used to throw), the test is a regression test: its name says what no longer throws, and the red run on the base commit is its evidence |
| A change detector | An in-order verification chain that mirrors the method body; a constant compared with its own literal; a snapshot of private structure | Test the behavior that depends on the decision: `retried five times and made no sixth attempt`, not `MAX_RETRIES == 5` |
| An assertion weakened until it passes | Equality replaced by not-null, a type check, `contains`, `length > 0`; a widened range or delta | Assert the value. An existence check where the behavior defines a value is a sanity check, not a test |
| A snapshot accepted unread | The snapshot file updated in the same commit as the behavior, with no note on what changed | Read it, name what changed and why, and narrow it to the output the behavior defines |
| A regression test never seen red | No failing run, no test-first commit, no pasted output in the pull request | The red run on the base commit (§1) |
| An assertion that is never executed | The assert is not on the test's straight-line path: behind a condition that is false, in a loop over an empty collection, after an early return, inside a callback nothing invokes, or after a line in the same `try` block that throws first, with a `catch` that swallows it | Move the assertion to the top level of the test, or assert the condition that was supposed to hold before it (the collection is not empty, the callback ran); delete the swallowing `catch`, or assert on the exception |

Each repair can be gamed in turn, and the reviewer checks the second step too: an assertion added to satisfy the row
*No assertion, or a print of the result in its place* can be a sanity check (*An assertion weakened until it passes*);
a literal added to satisfy *Expected value computed by the code under test* can be the pasted output of the code
under test, so the reviewer derives the value from the specification or by hand; a mock moved one level down can
still swallow the side effect the test depends on, so the reviewer lists the side effects the double drops.

## 6. Keeping the test green across a refactoring

The T3 reader changes the implementation with the behavior fixed and expects no test to go red. A test that fails on a
pure refactoring found nothing and cost them a fix; a refactoring pull request that edits tests is the moment the
change detectors of §5 show themselves, so flag every test it touches and examine it.

- **Test through the unit's interface, at the boundary the project draws.** That boundary is the stable behavioral
  interface the rest of the code uses, public or package-internal; it is not language-level visibility. A private
  helper is tested through the caller that reaches it; a focused internal test is right where the caller's setup is
  disproportionate or hides the failure, as long as the name is already an interface for a production reason:
  production code in another file or module calls it, the module exports it, or the neighboring tests of sibling
  units bind at the same level. A name only the test would reach is not one, whatever it is called. Never widen
  production visibility, and never add an export for a test. A test bound to an incidental name, by reflection, a
  test-only export, a widened visibility annotation, or a `_private` call, breaks on every rename.
- **Verify state, not interactions.** Assert the return value or the observable state. Verify a call only where the
  call is the behavior: a state-changing call to a collaborator outside the unit, such as a message sent or a row
  written. Verifying that a query was made is redundant and brittle, because the code can call the right method and do
  the wrong thing with the result. Absence, count, and order are verified where the contract defines them: rejected
  input causes no outbound call; a cache hit is established by the backend seeing one call, not by the second read
  returning the right value; the notification is sent after the commit, not before. `verifyNoMoreInteractions` over
  every collaborator and an `InOrder` over an incidental sequence pin the mechanism instead, and fail on the next
  refactoring.
- **Prefer the real dependency; then a fake; then a stub; and interaction verification only where the interaction
  is the contract**: an outbound command to an unmanaged out-of-process dependency, or a call the behavior
  promises to avoid. Leave the real thing only where it is slow, non-deterministic, or cannot be constructed
  in the test. A fake is a working implementation with a shortcut (an in-memory store); a stub returns canned values. A
  mock of an in-process collaborator tests a fiction. `Unavoidable` is a claim: the reviewer asks which of the three
  reasons applies, and which side effects the double drops.
- **Do not mock types you do not own.** A mock of a library class encodes today's assumption about the library, and
  the test keeps passing after the library changes its answer. Wrap the type and fake the wrapper, or use the real
  implementation.
- **Assert the fields the behavior defines.** Compare a whole value only where the whole value is the behavior, such as
  a pure function's result, and keep at most one whole-equality test per common case. Whole-object equality on an
  entity fails the day an unrelated field is added.
- **No logic on the path to an assertion.** No condition that decides whether a check runs, no loop or computed
  string that produces the expected value. A condition that *is* the check (`if got != want { t.Errorf(…) }`) is
  the assertion, and stays. A test with logic can be wrong in the same way as the code: an expected
  URL built by concatenation hides the double slash the literal would show. A loop that feeds a table of cases to
  `t.Run` or a parameterized runner is the runner, not logic: each row still carries its expected value as a
  literal.
- **Test the contract your code makes at its boundary, not the framework's mechanics.** That a router invoked a
  registered handler is the framework's test. A constructor, a getter, or a forwarding method earns a test only where
  it validates, defaults, derives, or causes a side effect.
- **Production code carries no test-only method.** A `reset()` that only tests call is test logic in production and a
  hook for shared state (§8). Cleanup lives in test utilities.

## 7. The failure report

A failing test is read as a bug report by someone holding only the runner's output. Four things write that report,
and each fact belongs in exactly one of them. Decide what each carries before writing the next.

| Part | Carries | Not |
| --- | --- | --- |
| **The container** (class, module path, `describe` block, parent test) | The unit under test and the condition every test in it shares | A file name; a fact true of one test |
| **The test name** (method, subtest, `it` string, parameterized case id) | The scenario and the expected outcome, so the failure line reads as a sentence: `a negative count is refused` | A location (`testEnsureBytes`), an ordinal (`case 3`), an issue number, a name with `and` |
| **The assertion** | The values: got and want, printed by an assertion built to print them, in the operand order the framework labels | A boolean wrapped around a comparison, which prints `true` and `false` or the expression text |
| **The message** | The function and the input where the assertion cannot print them: `ensureBytes(-2147483648)` | The scenario the name states; the values the assertion prints; `failed` |

The name is printed in the report; the comment above the test is read only once someone opens the file. So the
comment may repeat the rule the message states, and the message may not repeat the name.

- **Use the assertion that prints the operands.** `assertEquals(expected, actual)` prints both; `assertTrue(expected
  == actual)` prints `expected: <true> but was: <false>`, with or without a message, and leaves the reader to
  reverse-engineer the values from a stack trace. The same holds for `assert!(a == b)`, `assert.ok(a === b)`, and a
  boolean computed one line before a bare `assert ok`. A boolean assertion on a method that returns a boolean is
  right: it prints what there is to print.
- **Keep the framework's operand order**, so the labels are right: got before want in Go; expected before actual in
  JUnit and testify; the actual value first in Hamcrest (`assertThat(actual, is(expected))`), AssertJ, Truth, Jest,
  Vitest, and `node:assert`. A swapped pair prints the bug as the expectation. The references carry the order per
  framework.
- **A parameterized case carries a name that identifies it.** An index alone is a location, and two cases with one
  name hide each other. Name the case by its condition (`minus one`, `empty list`), not its ordinal; whether the names
  are unique is checked by running the suite and reading the ids.
- **Several assertions on one behavior report together.** `assertAll`, `expect.soft`, `t.Error`, and `EXPECT_*` show
  every failed check in one run; a hard abort (`t.Fatal`, `require`, `ASSERT_*`) is for the point after which
  continuing is meaningless, such as a nil result the next line dereferences.
- **Compare error semantics, not message strings.** Assert the exception type, the sentinel, or the code; match a
  message only on the part the behavior defines. A pinned message is a change detector for wording.
- **A wait that fails reports what it waited for and the last state it saw.** `Timed out after 60 s waiting for the
  pod to enter Running; last state Pending` is a report; `Timeout` is not.
- **One behavior per test.** The signal for a second behavior is an act after an assert: after asserting the output of
  one call on the unit, the test calls the unit again. Several assertions on the fields of one result are one
  behavior; a second call on an unrelated input is a second scenario, whose failure masks the first and whose name
  cannot say both. Split it, or parameterize. Where the relation between the calls is the behavior (the second call
  is a no-op, the second read is served from the cache, the retry succeeds, one transition of §4's state machine),
  the calls are one scenario and the name says which relation it establishes. The reviewer checks that the test
  fails when the claimed relation is violated: a cache test that also passes when the backend is queried twice, or
  an idempotency test that also passes when the second call changes the state, has established nothing.

## 8. Determinism

A flaky test is neither retried until green nor deleted; it is diagnosed, and the code under test is inspected
before the test is. Each cause below has one fix, and every cause but the last is visible in the file.

| Cause | In the file | Fix |
| --- | --- | --- |
| Waiting on a fixed delay | `sleep`, `Thread.sleep`, `setTimeout` used as a wait | Poll or await the condition, with the wait message of §7 |
| Shared mutable state | A static or class-level field a test writes; a fixture mutated in place; rows or files left behind | A per-test fixture; teardown; the random-order run below |
| The wall clock | `now()`, `Date()`, `time.Now()` read by the code under test | Inject the clock |
| Unseeded randomness | `random()` with no seed, in the test or the code | Inject or fix the seed, and print it on failure |
| The network or the platform | A real host name; a port; a locale, timezone, or path separator assumed | Fake the endpoint; pin the locale and timezone; build paths |
| Iteration order of an unordered collection | A `set` or hash map compared as a sequence | Sort before comparing, or compare as a set |
| Exact floating-point equality | `==` on a computed float | Compare within a tolerance the specification allows |
| An assertion range that excludes valid outputs | `elapsed < 100ms`; a bound tighter than the specification | Widen to the specification's range, or assert the ordering rather than the duration |
| Order dependence | Not always visible | Run the suite in random order with the seed printed; fix by removing the shared state, never by pinning the order |

## 9. Organization and test data

- **DAMP over DRY.** The values an assertion depends on appear in the test body, where the reader can check the test
  by inspection, since tests have no tests of their own. A value hidden in `setUp`, in a loop, or in a file the test
  reads without showing is a mystery guest. Helpers construct value objects and infrastructure; a validation helper
  asserts one conceptual fact.
- **A new test goes beside the nearest existing test of the unit it exercises**, in the file or directory named for
  the code under test, not in a file named for the ticket or the author. A test class splits when its fixture no
  longer serves every test in it; a fixture with fields only some tests use is the signal.
- **Arrange, act, assert**, in that order, once. The act is the call on the unit, or the sequence of calls whose
  relation is the behavior (§7); §7's one-behavior rule follows from it.

## 10. What you can decide from the diff, and what needs a run

The rules above fall into four buckets, and a review says which bucket each finding sits in.

| Bucket | Rules | What it takes |
| --- | --- | --- |
| **From the diff** | The shapes of §5; the robustness rules of §6; the report rules of §7; the file-visible causes of §8; placement and DAMP of §9; the boundary cases of §4 | Reading the test file and the diff |
| **A run of the suite** | Red on the base commit; the random-order run; the uniqueness of parameterized names; a property test's reproducer | A run you make and whose output you paste |
| **A tool's verdict** | The mutation verdict, read as the tool defines it; coverage as the non-signal it is | The tool's own report, scoped to the diff |
| **A judgment** | The partition set against the specification; the three reasons to leave the real dependency; whether a flaky fix belongs in the code; whether a surviving mutant is equivalent; the level choice of §3 | Made from the specification, the code, and the repository's conventions, and stated in the pull request in a sentence each. A question only where an unresolved ambiguity would change the expected behavior, the scope, or the test strategy. A surviving mutant is a candidate gap the writer settles: a missing or weak test where it changes behavior the specification defines, an equivalent mutant explained in the pull request where it does not, and an unresolved one reported as such |

## 11. Review checklist

Run this over a test you wrote or one you are reviewing.

- Which production change would make this test fail, and is it a bug rather than a decision (§1)?
- For a regression test: was it seen red on the base commit, and does the pull request show it (§1)?
- Can the change alter behavior at all? If not, does the pull request say so; if it is a dependency bump, a
  regeneration, or a build change, does the pull request name the surface the green suite covers (§3)?
- For a change made for speed or memory, is the behavior preserved asserted, is the improvement measured where the
  repository measures or reported with its conditions, and is no wall-clock bound in a functional test (§3)?
- Is the level named, and is it the smallest at which the behavior is observable through the unit's interface (§3)?
- Is every existing test whose expectation moved named, with the behavior that moved with it (§3)?
- Does a small test mock the boundary the change altered (§3)?
- Is there one test per partition, each invalid partition alone, and a case at each boundary and its neighbors (§4)?
- Where another argument can influence the changed behavior, is it varied, one test per partition the behavior
  distinguishes, and would each fail with the changed behavior wrong for that value alone (§4)?
- Does the change add a member to an open set, and does a test enumerate the set from the code (§4)?
- Do the partitions come from the specification, or from the branches of the code (§4)?
- Any expected value computed by the code under test, or pasted from its output (§5)?
- Any assertion on a value the test supplied, or on the mock where the call is not the behavior (§5)?
- Is the unit under test, or the collaborator the test names, replaced by a double (§5)?
- Any test whose only failure is an exception, where the contract defines a result, or whose assertion was weakened
  to pass (§5)?
- Any verification of a query, of call order, or of `no more interactions` that the contract does not define (§6)?
- Any private name reached by reflection, a test-only export, or widened visibility (§6)?
- Any mock of a type the repository does not own (§6)?
- Any loop or concatenation that produces the expected value, or condition that decides whether a check runs (§6)?
- Does the test name state the scenario and the outcome, or a location (§7)?
- Does the assertion print the operands, in the framework's order (§7)?
- Do the grouping, error, and message forms come from the assertion library's reference, not the engine's (§0)?
- Does the message repeat the name or the values, or say only `failed` (§7)?
- Is there an act after an assert that starts an unrelated scenario (§7)?
- Any sleep, wall-clock read, unseeded random, real host, or unordered collection compared as a sequence (§8)?
- Any expected value hidden in a fixture, a helper, or a file (§9)?
- Is the new test beside the existing tests of the same unit (§9)?
- For each finding: which of the four buckets, and what run or tool settles it (§10)?

## 12. Worked examples

### A mirror assertion

**Before**: the expected value is produced by the function under test, so the assertion holds whatever the function
does.

```java
@Test
void buildsTagQuery() {
    String expected = SearchQuery.build(Map.of("tag", "urgent"));
    assertEquals(expected, SearchQuery.build(Map.of("tag", "urgent")));
}
```

**After**: the expected value is a literal derived from the specification, the name states the scenario and the
outcome, and the assertion prints both operands when it fails.

```java
@Test
void aTagFilterRendersAsAQuotedTagClause() {
    assertEquals("tag:\"urgent\"", SearchQuery.build(Map.of("tag", "urgent")));
}
```

The production change that fails the second test is any change to how a tag renders. Nothing fails the first.

### Three behaviors in one test

**Before**: three scenarios, one name, and the second failure masked by the first.

```java
@Test
void withdraw() {
    account.deposit(usd(5));
    assertEquals(usd(5), account.withdraw(usd(5)));
    assertThrows(InsufficientFundsException.class, () -> account.withdraw(usd(1)));
    account.setOverdraftLimit(usd(1));
    assertEquals(usd(1), account.withdraw(usd(1)));
}
```

**After**: an act after an assert marked each split.

```java
@Test
void canWithdrawWithinBalance() {
    account.deposit(usd(5));
    assertEquals(usd(5), account.withdraw(usd(5)));
}

@Test
void cannotOverdrawWithoutALimit() {
    account.deposit(usd(5));
    assertThrows(InsufficientFundsException.class, () -> account.withdraw(usd(6)));
}

@Test
void canOverdrawUpToTheLimit() {
    account.deposit(usd(5));
    account.setOverdraftLimit(usd(1));
    assertEquals(usd(6), account.withdraw(usd(6)));
}
```

Each name now reads as a finding in the report, and a failure in the third leaves the first two green.

### A report that says nothing

**Before**: the container is a file, the name is a location, the assertion prints `true` and `false`, and the message
repeats the name.

```java
class EnsureBytesTest {
    @Test
    void testEnsureBytes() {
        assertTrue(stream.ensureBytes(-1) == 0, "testEnsureBytes failed");
    }
}
```

**After**: each fact in its slot. The failure line reads `PGStreamTest > aNegativeCountIsRefused` followed by
`ensureBytes(-1) ==> expected: <0> but was: <-1>`, and the reader knows the unit, the scenario, the input, and both
values without opening the file.

```java
class PGStreamTest {
    @Test
    void aNegativeCountIsRefused() {
        assertEquals(0, stream.ensureBytes(-1), "ensureBytes(-1)");
    }
}
```
