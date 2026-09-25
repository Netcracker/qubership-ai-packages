---
name: test-authoring
description: >-
  Load before writing, editing, or reviewing a test in any language, and at the end of a coding task
  that changed behavior ("fix the bug"): the change owes tests, and this skill decides which. Also
  load when asked whether a change is tested enough, at which level a test belongs, why a test is
  flaky, whether a test could fail at all, how to name a case, how related cases share their
  setup, whether several cases may share one check, whether a new test takes its file's shape or
  reuses its helpers, which assertion to use and what it prints, how to fake a dependency, when a
  property-based or exhaustiveness test is owed, or how to read a mutation or coverage report. Its
  references cover JUnit 4, JUnit 5 and 6, AssertJ, Truth, Hamcrest, Mockito, jetCheck, ArchUnit,
  pytest, Go testing and testify, cargo test, Jest, Vitest, and node:test. Wording belongs to the
  developer-style skill of the repository's language, and the comment above a test to the
  doc-comment skill of its programming language; load those too.
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

1. **The repository's instructions name the stack.** A line such as `Tests: JUnit 5 engine, JUnit 5 assertions; Mockito
   for doubles; jetCheck for property-based tests; ArchUnit for structural tests` selects the files, and nothing else is
   opened. Where the line is missing, propose it in one sentence: to the user where the session has one, in the review
   where the task is a review, and in the pull request description otherwise. The proposal edits no file. Write the line
   into the repository's instructions file (`AGENTS.md`, `CLAUDE.md`) only after the user agrees. A change made with no
   user to ask, a change to a repository that somebody else maintains, and a review all stop at the proposal. Where the
   instructions file is generated, as its header or the repository's build shows, the agreed line goes into the source
   the file is generated from. An edit to the output is lost at the next generation. Where the repository has no
   instructions file, ask the user whether to add the line in a new `AGENTS.md`, and create no instructions file
   unasked. A change that finds the line present adds to it only a fact about the harness that the change had to
   establish (§7), under the same condition. The line names the major version. For a harness that has no reference file
   here, the project's own or a library's, it also says whether one call of the harness reports every mismatch and how
   it names each case (§7). It carries no more.
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
| A new method on a unit's interface | Small, one case per partition and boundary of its inputs (§4), through the method itself | Medium only where the outcome depends on a real dependency a fake cannot reproduce | The partition list against the specification; no mock of a collaborator where a fake exists |
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
varied too: one case per partition of it that the changed behavior distinguishes, and the reviewer checks that each
such case would fail with the changed behavior wrong for that value alone. The decision table and the transition list
below are scoped the same way, to the conditions and the states the change reached.

This section counts cases, and §7 decides their form. A case is usually a test of its own. §7 says when cases are the
rows of one table, and when a case stands beside its controls in one check. The counts of this section hold in every
form.

- **One case per equivalence partition.** Partition each input into classes the specification treats alike, valid and
  invalid; the classes do not overlap and none is empty. One value stands for its whole class. A second value from
  the same class earns its place only where it is a boundary, a distinct representation (another encoding, a
  different collection shape, a Unicode form), an interaction with another input, or a known regression; otherwise
  it is a redundant case, not a stronger suite. Test each invalid class alone, because two invalid inputs in one call
  mask each other: the first one rejected hides whether the second would have been. Two inputs that one act evaluates
  separately, such as two lines of one linted source, are not one call; §7 says when they share a check.
- **Each boundary and its neighbors.** For an ordered input, test the minimum, the maximum, and the value just outside
  each (two-value analysis); add the value just inside where a wrong operator is plausible, since `x <= 10` written as
  `x == 10` passes 10 and 11 and fails only on 9.
- **A decision table when the outcome depends on a combination of conditions.** One case per feasible column, so the
  happy column is not the only one tested.
- **A state-transition test when the behavior depends on history.** Every valid transition once; each invalid transition
  as a case of its own.
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
existing tests, state it in the pull request, and stop when every partition of the changed input has one case, every
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
- **No logic on the path to an assertion.** No condition that decides whether an assertion runs, no loop or computed
  string that produces the expected value. A condition that *is* the comparison (`if got != want { t.Errorf(…) }`) is
  the assertion, and stays. A test with logic can be wrong in the same way as the code: an expected URL built by
  concatenation hides the double slash the literal would show. A loop that feeds a table of cases to `t.Run` or a
  parameterized runner is the runner, not logic: each row still carries its expected value as a literal.
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
| **The test name** (method, subtest, `it` string, parameterized case id) | The scenario and the expected outcome, so the failure line reads as a sentence: `a negative count is refused`. Where the test holds a case with its controls (*Independent cases in one check hide each other*), the rule they establish, and the partition of the case where the rule has a test for each: `a type variable is rejected only when its declared bound admits null` | A location (`testEnsureBytes`), an ordinal (`case 3`), an issue number, a conjunction, `and` or `but`, that joins the outcomes of two inputs or two scenarios (`rejects a negative count and accepts zero`) |
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
  every failed assertion in one run; a hard abort (`t.Fatal`, `require`, `ASSERT_*`) is for the point after which
  continuing is meaningless, such as a nil result the next line dereferences.
- **Compare error semantics, not message strings.** Assert the exception type, the sentinel, or the code; match a
  message only on the part the behavior defines. A pinned message is a change detector for wording.
- **A wait that fails reports what it waited for and the last state it saw.** `Timed out after 60 s waiting for the
  pod to enter Running; last state Pending` is a report; `Timeout` is not.
- **One behavior per test.** The signal for a second behavior is an act after an assert: after asserting the output of
  one call on the unit, the test calls the unit again. Several assertions on the fields of one result are one behavior;
  a second call on an unrelated input is a second scenario, whose failure masks the first and whose name cannot say
  both. Split it, or parameterize. Where the relation between the calls is the behavior (the second call is a no-op, the
  second read is served from the cache, the retry succeeds, one transition of §4's state machine), the calls are one
  scenario and the name says which relation it establishes. The reviewer checks that the test fails when the claimed
  relation is violated: a cache test that also passes when the backend is queried twice, or an idempotency test that
  also passes when the second call changes the state, has established nothing. A case and its controls that one act
  checks together, one compilation or one validation of a batch, are one behavior: the bullet *Independent cases in one
  check hide each other* says when they share a test. A loop in one test that calls the unit once per row of a table of
  literal cases is not one act: each call is a case. Where the assertion stops the test (`assert_eq!`, `node:assert`),
  the first failing row hides the rows after it, unless the loop hands each row to the runner as its own case (§6).
- **Cases that share a setup write it once, and each case shows what differs.** Related cases often differ in one value:
  a positive and a negative case (`a bound that admits null is rejected`, `a bound that does not is accepted`), the
  neighbors of a boundary, the columns of a decision table (the first backend refuses, the second refuses, both refuse).
  The outcome may flip between the cases or stay the same; this bullet is about the setup they share. Write that setup
  once, in one of these forms. Cases stand side by side in one input, where one call of a harness verifies several
  expectations and the bullet *Independent cases in one check hide each other* lets the cases stay together. A helper
  beside the tests takes the varying value as its argument. The cases are the arguments of one parameterized test, or
  subtests under one parent. The engine's per-test fixture (`@BeforeEach`, a pytest fixture) holds the part that no case
  varies and no expectation depends on (§8, §9). These are forms to choose from, not an order of preference: the
  sub-bullet *The form follows the assertions* and the file's neighbors (§9) choose among them. In an example-based
  case, write the input and the expected outcome as literals. Keep one name per case, in the runner's report or in the
  check's own report where the harness names cases, so that a case fails on its own. A property-based test (§4) has no
  literal input. It shows its generator and the property it asserts, and its failure carries the reproducer. A case and
  its controls in one input are the exception to one name per case: they carry one name, which states the rule they
  establish (the sub-bullet *A case and its controls are not independent*). The helper builds its result anew on every
  call, so that no case reads what another case changed (§8). Subtests under one parent do the same: each builds the
  setup it changes, and the parent shares only what no case changes.
  - **A short setup is repeated.** A setup the reader takes in without comparing the bodies is written in each case,
    as the worked example *Three behaviors in one test* repeats one deposit. The shared part moves out of the cases
    once a reader has to compare two bodies line by line to find what differs. A document or a source of several lines
    is that long even where one line differs. Copies of a setup that long state the difference nowhere: a change to the
    setup touches every copy, and a copy that drifts makes the cases test different things. This sub-bullet covers
    cases that are separate acts on the unit, where the shared setup would need a helper, a table, or a fixture.
  - **Drift costs most in a case that expects nothing** (nothing rejected, nothing reported). That case establishes the
    rule only while the case that expects the outcome fires on the same setup; otherwise the silence may come from the
    setup. One input that holds the case and its control cannot drift, and a helper that both cases call cannot either.
    Where one act can evaluate both (the sub-bullet *A case and its controls are not independent*), they share one input
    at any length, since the joined input is no longer than one copy and needs no helper.
  - **A helper leaves the reader the whole input the expectation depends on.** This sub-bullet is about a helper that
    assembles a textual input. A helper that receives a clock, a temporary directory, or a fake dependency is
    infrastructure (§9), and the sub-bullet does not apply to it. Three kinds of helper pass. The first takes a value:
    `configWithTimeout("-1")` leaves a document the reader can picture, and the same holds for one literal in a query,
    in a request body, or in a source the unit compiles. The argument fills a place where the input's grammar has a
    value: a number, a string literal, an address object that a request helper places in the body. Where the cases
    differ inside that value, the test writes the value out whole as the argument. The second sets or leaves out one key
    of a data record, at any depth of the record: `orderWithCoupon("EXPIRED")`, `orderWithout("address")`. Such a record
    is a request body, a configuration document, or a fixture row. The helper's name or its argument names the key, and
    the other argument is the key's value. No argument is a fragment of the record's text, such as `"\"coupon\":
    \"EXPIRED\""`. The third wraps one whole fragment that the test writes out, the body of a method or the payload of
    an envelope, in fixed text that no expectation depends on: `lintInMethod(body)`. Every line the expectation depends
    on is then in the test, in one piece. A helper fails where it assembles the input from two or more pieces of syntax,
    or splices a piece into text the expectation depends on. One such helper builds a query from clauses. Another builds
    a source from a type parameter list, a statement, and an expectation marker. The reader learns the effect of each
    piece only after the helper has put them together, so the reader never sees whole the input that the assertion
    depends on (§9). Cases that differ in the structure of the input stand side by side in one input where one act of
    the unit evaluates them all. The bullet *Independent cases in one check hide each other* says when they stay
    together. Otherwise each test writes out whole its input, or the fragment a wrapping helper takes. That covers a
    unit that takes one input per call, such as a parser or a statement sent to a database. It covers inputs that change
    each other's outcome in one act. It also covers cases that may not share a harness call that stops at the first
    mismatch. The copy is the price of an input the reader sees whole, and the name of each test states what differs.
  - **The form follows the assertions.** Cases that assert the same way, every case running the same assertions, are
    rows of one table, arguments of one parameterized test, or separate tests on one helper, and the file's neighbors
    choose among these (§9). Cases that need different assertions, one expecting a throw and one a returned value, are
    separate named tests or subtests on one helper, since a row field that selects the assertion is a condition that
    decides whether an assertion runs (§6). Many cases of each kind are two tables, one for each kind of assertion.
    This sub-bullet covers cases that are separate acts on the unit. A case and its controls that one act evaluates are
    asserted together on that act's result, a rejected record and an accepted one in one validated batch, as the bullet
    *Independent cases in one check hide each other* says.

  The reviewer reads the differing input off one line of each case without comparing bodies. The reviewer checks that no
  two cases have to be compared line by line to find what differs: such cases reach their setup through one input,
  helper, table, or fixture rather than through a copy. Where a helper wraps a fragment, or the inputs differ in
  structure, the reviewer finds every line the expectation depends on in the test body, in one piece. Every argument of
  a helper that assembles a textual input is a value, the name or the value of one key of a data record, or the one
  whole fragment that the helper wraps. No helper takes two pieces of syntax, and none splices a clause, a statement, or
  a marker into text the expectation depends on. A copied input passes where either of two conditions holds. The cases
  are separate acts on the unit and the setup is short enough to repeat (the sub-bullet *A short setup is repeated*). Or
  the inputs differ in structure and cannot stand side by side: the unit takes one input per call, the inputs change
  each other's outcome, or the cases may not share a harness call that stops at the first mismatch.
- **Independent cases in one check hide each other where the check stops at the first mismatch.** In this bullet, and
  wherever §4, §9, §10, and §11 cite it, a check is one call of a harness that verifies many expectations in one run:
  the markers in one compiled source, the records of one validated batch. Such a call reports either every mismatch or
  only the first. The writer of a test does not choose that property, so it is learned once per harness and not per
  test. The reference file says it for a library this skill covers; the stack line of the repository's instructions (§0)
  or the harness's documentation says it for any other harness, the project's own or a library's. Where none of them
  says, establish it once, by breaking two cases on purpose and counting what the report names, or by reading the
  harness's source. Propose the answer for the place the next writer reads, under the condition §0 sets for the stack
  line: the stack line, or the documentation of a harness the repository owns. Without that agreement, the answer goes
  in the pull request description, or in the review where the task is a review. The next change does not see either, so
  it cites the harness again. Two questions, answered apart: does the report carry every mismatch, and does it name each
  case without the file? A test that asserts on the result of one act itself, the error list of one validated batch, has
  no such property to learn, since the writer chooses the assertions. Several expectations on that result go into the
  grouped form whose report carries every failure (*Several assertions on one behavior report together*), each with a
  message that names its case where the assertion cannot. Where the assertion library has no grouped form (cargo test,
  Jest, `node:assert`, pytest without a plugin), one assertion compares the whole result with the expected one and
  prints both sides. The result is first reduced to the fields the behavior defines, such as the record and the error
  code, without the message text (§6), and compared as a set where the behavior defines no order (§8). Either test
  counts as a check that carries every mismatch. It names each case where each entry identifies its record by content;
  an entry that identifies it by index names it by position, as a line number does. A chain of assertions that stops at
  the first counts as a check that stops at the first mismatch.
  - **A case and its controls are not independent.** A check that stops at the first mismatch is no reason to split
    them. The bullet *Cases that share a setup write it once* and the file's shape (§9) decide whether a new case joins
    its control in one input. A rule here is one statement of the specification that ties one outcome to one condition:
    `a local is reported when nothing reads it`. The case is the partition of §4 the test is named for: the partition
    whose outcome the change sets or moves (a diagnostic the check now reports, a record it now rejects, a false report
    it no longer makes), or, where the test holds no partition the change moves, a partition the check reports. Each
    control is a nearest input with the opposite outcome, differing from the case in one respect. The change is the
    commit the tests are written for; a rewrite of existing tests counts against the commit that added them, and tests
    of behavior that no commit moves have no change under test. For a new check, compare with the check absent, which
    reported nothing. Two counts decide what shares a test, whatever the wording of the rule: the inputs that expect a
    report, which the diff shows, and the inputs whose outcome the change moves, which a run on the base settles (§1). A
    batch validator that newly applies `a timeout is accepted only when it is a nonnegative integer` rejects `-1` and
    `"abc"`: those are two cases, and an accepted value is the control of each.  They establish the rule between them,
    one run of the check is the act, and a failure of either says that this rule moved. A check that stops at the first
    mismatch costs them a second run and hides nothing about another rule. The test's name states the rule, and each
    control stands beside the case it controls. Unless the check carries every mismatch, one test holds at most one
    input that expects a report and at most one input whose outcome the change moves. Usually both are the case; in a
    fix that removes a false report, the case is silent and its control is the one input that expects a report. A second
    partition whose outcome the change moves, a timeout that is not a number beside a negative one, is a second case
    with controls of its own, however broadly the specification words the rule. Under a check that stops at the first
    mismatch it is a second test, since the first mismatch would hide the second. Each such test names the rule and its
    case's partition, `a timeout is accepted only when it is a number` and `a timeout is accepted only when it is not
    negative`, so that the report tells the tests of one rule apart. This form needs an act that evaluates several
    inputs at once: one compilation or one validation of a batch. The form also needs the act to evaluate each input on
    its own, so that each case has the outcome it would have alone. An atomic batch does not evaluate each record on its
    own: it rolls back the valid record along with the rejected one. A compilation does not either where one declaration
    changes what the compiler infers for the next. Where the unit takes one input per call, the case and its control are
    separate cases, since each call on the unit is an act of its own (§9). A loop or a grouped assertion over such a
    unit makes one call per case and changes nothing in that. Where the inputs affect each other they are separate cases
    too, since each outcome then depends on its neighbor. Separate cases take a form that the bullet *Cases that share a
    setup write it once* offers where they differ in a value, and each writes its input out whole where they differ in
    structure. The reviewer counts the inputs in the test that expect a report and the inputs whose outcome the change
    moves, and finds at most one of each, unless the check carries every mismatch. The reviewer checks that every other
    case narrowly misses that partition's condition, and that each expectation would stand with the other cases removed
    from the input. A case whose outcome a different condition decides moves to a test of its own, or to the form of the
    sub-bullet *Where the check carries every mismatch under a name*. A name whose conjunction, `and` or `but`, joins
    the outcomes of two inputs or two scenarios (`rejects a negative count and accepts zero`, `accepts a subtype but
    rejects a nullable use`) names two tests, and the test is split. An `and` inside the condition of one rule stays
    (`is rejected only when its bound admits null and the requirement does not`), and so does one between two
    observations of one act (`serves the second read from the cache and queries the backend once`).
  - **Where the check stops at the first mismatch, split between the cases.** Cases of different rules in one such check
    hide each other, and so do two inputs of one rule that each expect a report, or that each have an outcome the change
    moves. Each gets its own test, with its controls.
  - **Where the check names a case by a line number** inside an input the test embeds, only a reader holding the file
    can place it. This holds whether the check carries every mismatch or stops at the first. Give each case a label the
    report prints where the harness offers one. Where it offers none, the test name is all the report carries besides
    the line. A case with its controls is named by their rule. Cases of several rules are split between rules, and under
    a check that stops at the first mismatch the cases of one rule are split too (the sub-bullet *Where the check stops
    at the first mismatch, split between the cases*). For a test that still holds several cases, the missing label is a
    limitation that no offered form removes, so it earns the follow-up named in the pull request. Where the stack line
    or the harness's documentation already records that the harness offers no label, the follow-up has been proposed,
    and the pull request does not repeat it.
  - **Where the check carries every mismatch under a name,** the shared check is one runner test with named cases, and
    the check's own report gives each case the name that the bullet *Cases that share a setup write it once* asks for.
    The runner test then takes the container's part in the four-part table of this section: its name states what the
    cases share, and each case name states the scenario and the outcome. A grouped assertion over the results of one act
    is the same form, with the message of each assertion as the case's name, or, for one assertion on the whole result,
    the content of each entry. This form is for independent cases that one act evaluates. Cases that are separate calls
    on the unit stay under the bullet *One behavior per test*, and the runner's own forms name them: a parameterized
    case or a subtest.

  Where a form the harness already offers reports independent cases apart (a subtest or a parameterized case for
  separate calls on the unit, a grouped assertion over the results of one act), use it and propose nothing; only a
  limitation that no offered form removes earns a follow-up, proposed and named in the pull request: a change to the
  harness where its source is in the repository, or an issue against the library where it is not, checked against the
  library's tracker for an existing report. The task files nothing.

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

- **DAMP over DRY.** The values an assertion depends on, the input that varies between cases and the expected value,
  appear in the test body, where the reader can check the test by inspection, since tests have no tests of their own. A
  property-based test shows its generator and its property there instead (§7). A value hidden in `setUp`, in a loop, or
  in a file the test reads without showing is a mystery guest. Helpers and per-test fixtures construct value objects and
  infrastructure, and the part that related cases share (a request skeleton, a fixture record, a document with one
  varying value) is infrastructure. Where it is too long to repeat (§7's sub-bullet *A short setup is repeated*), it is
  written once, in one of the forms §7 lists: one input that holds the cases, a helper beside the tests that takes the
  varying value, a table, or the engine's fixture. Whether the shared part is infrastructure depends on what varies
  between the cases, whatever kind of text the input is. Where the cases differ in one value, the rest of the input is
  infrastructure. That holds for a configuration document, a request body, a query, and a source the unit compiles.
  Where the cases differ in the structure of the input, that structure is what the assertion depends on, and it stays
  whole in the test (§7). A key that a data record sets or leaves out is a value here (§7). A helper that hides the
  input or the expectation is the mystery guest; one that hides the incidental part is not. A constant the expectation
  depends on is not incidental: the balance of 5 that makes a withdrawal of 6 fail stays visible, as an argument or in
  the helper's name, `accountWithBalance(5)`. A validation helper asserts one conceptual fact.
- **A new test takes the shape of its neighbors.** Where the file writes one case per method, several cases in one
  source, or rows of a table, the new test does the same, since a file with two shapes is read twice. Where the
  neighbors' shape breaks this skill, the skill wins: the new test takes the shape the skill asks for, and the pull
  request names the section. Three such shapes are common, all from §7. Independent cases hide each other in one check
  that stops at the first mismatch or names its cases only by a line number; a loop over a table of literal cases in one
  test, whose assertion stops at the first failing row, is such a check. A long setup is copied into every test where §7
  offers a form without the copy. A case and its control that one act could evaluate are written as two tests with two
  copies of the input, at any length. A case with its controls in one check is not one of them (§7), and neither is a
  case and its control of separate acts whose setup is short enough to repeat (§7's sub-bullet *A short setup is
  repeated*): the new test takes that shape. A reference file may name the ecosystem's idiom for a table and say which
  new cases join it: those for which the idiom reports each case apart and asserts what §5 to §7 ask. Any other new case
  takes the smallest form that does, beside the table, and the table keeps its rows and its assertions. Go's `wantErr
  bool` table takes a new row whose input is accepted, and not a new row that expects an error. The neighbors stay as
  they are unless the task is to rewrite them, with one exception: an existing test of the same specification rule, the
  case the new control belongs to or the control of the new case, is the twin. The new case joins it, inside the twin's
  input where one act evaluates both (§7), or through a helper that both now call, and the twin's expectations do not
  change. Its name changes where the test now holds a case with its controls and has to state their rule (§7). §7's
  exceptions hold for a twin too. A short setup of separate acts is repeated. Inputs that differ in structure and cannot
  stand side by side are each written out whole. A new case beside a twin that already holds an input that expects a
  report, or one whose outcome the change moves, is a test of its own under a check that stops at the first mismatch,
  with the controls it needs written in its input (§7's sub-bullet *A case and its controls are not independent*). A
  twin that is a row of an idiom table the new case may not join stays in its table, and the two share a long setup
  through a helper that both call. A twin that reaches its input through a helper that assembles it from pieces of
  syntax is not joined: the new test writes its input out whole, and the pull request names the twin and the helper. A
  case of another specification rule that shares the setup takes the helper, or writes its input out (§7).
- **A new test uses the helpers the file already has.** Read the helpers of the file, and of the package's shared test
  utilities, before writing one. Where an existing helper builds the same setup except for one value, write the helper
  that takes that value and have the old one call it, so that the existing tests stay as they are. Two helpers whose
  bodies differ in one line are the copied setup of §7 one level up: the reader compares the bodies to learn which one a
  test needs. Reuse covers the helpers §7 lets pass. Where the file's helper assembles an input from pieces of syntax
  (§7), the new test does not call it and does not write another like it. The new test writes its input out whole and
  leaves that helper and its callers as they are, and the pull request says so.
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
| **A run of the suite, or a citation of the harness** | Red on the base commit; the random-order run; the uniqueness of parameterized names; a property test's reproducer; which inputs of a test have an outcome the change moves (§7); whether a harness call carries every mismatch and names each case, where no reference, stack line, or documentation of the harness records it: the run with two cases broken, or the harness's source cited by file and line | A run you make and whose output you paste, or the file and line you cite |
| **A tool's verdict** | The mutation verdict, read as the tool defines it; coverage as the non-signal it is | The tool's own report, scoped to the diff |
| **A judgment** | The partition set against the specification; the three reasons to leave the real dependency; whether a flaky fix belongs in the code; whether a surviving mutant is equivalent; the level choice of §3; whether the cases of one test belong to one rule, and whether the act of one check evaluates each input on its own (§7) | Made from the specification, the code, and the repository's conventions, and stated in the pull request in a sentence each. A question only where an unresolved ambiguity would change the expected behavior, the scope, or the test strategy. A surviving mutant is a candidate gap the writer settles: a missing or weak test where it changes behavior the specification defines, an equivalent mutant explained in the pull request where it does not, and an unresolved one reported as such |

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
- Is there one case per partition, as a test of its own or in a form §7 allows, each invalid partition alone, and a
  case at each boundary and its neighbors (§4)?
- Where another argument can influence the changed behavior, is it varied, one case per partition the behavior
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
- Any loop or concatenation that produces the expected value, or condition that decides whether an assertion runs (§6)?
- Does the test name state the scenario and the outcome, or a location, or the outcomes of two inputs or scenarios
  joined by `and` or `but` (§7)?
- Does the assertion print the operands, in the framework's order (§7)?
- Do the grouping, error, and message forms come from the assertion library's reference, not the engine's (§0)?
- Where the repository's instructions carry no stack line, was the line proposed in one sentence, to the user, in the
  review, or in the pull request (§0)? Was an instructions file edited only after the user agreed, in its source where
  the file is generated, and was none created unasked (§0)?
- Does the message repeat the name or the values, or say only `failed` (§7)?
- Is there an act after an assert that starts an unrelated scenario (§7)?
- Do any two cases have to be compared line by line to find what differs, where one input, a helper, a table, or a
  fixture would hold the shared part (§7)? Or is the copy a setup short enough to repeat in separate acts, or the
  written-out input of cases that differ in structure and cannot stand side by side (§7)?
- Is a case and its control that one act could evaluate written as two tests with two copies of the input (§7)?
- Does every example-based case carry its input and its outcome as literals, and does a property-based test show its
  generator and its property (§7)?
- Where a helper wraps a fragment, or the inputs differ in structure, is every line the expectation depends on in the
  test body, in one piece (§7)? Is every argument of a helper that assembles a textual input a value, the name or the
  value of one key of a data record, or the one whole fragment the helper wraps (§7)? Does any helper take two pieces of
  syntax, or splice a clause, a statement, or a marker into text the expectation depends on (§7)?
- Does a row field or a flag select which assertion a case runs, where separate tests on one helper, or one table for
  each kind of assertion, would do (§7)?
- Where one harness call covers several independent cases, does a reference, the stack line, or the harness's
  documentation say whether that call carries every mismatch and names each case, or does this change establish it, by a
  run or a cited line of the harness, and propose it where §0 allows, or put it in the pull request or the review (§7)?
- Do several expectations on the result of one act use the grouped form that reports every failure, each with a message
  that names its case, or, where the library has none, one assertion on the whole result reduced to the fields the
  behavior defines (§7)?
- Is a check that stops at the first mismatch split between the cases, counted by the inputs that expect a report and
  the inputs whose outcome the change moves on the base commit, not by the wording of the rule, with a case and its
  controls left together under a name that states their rule and, where the rule has several tests, the case's partition
  (§7)?
- Does a test of a case with its controls hold at most one input that expects a report and at most one whose outcome the
  change moves, unless the check carries every mismatch, and does every other case narrowly miss that partition's
  condition (§7)?
- Does a loop in one test run a table of literal cases whose assertion stops at the first failing row, where the runner
  could name each row (§7)?
- Where a case and its controls share one check, would each expectation stand with the other cases removed from the
  input (§7)?
- Does a check that names its cases only by an embedded line number give them labels the report prints, whether it
  carries every mismatch or stops at the first (§7)?
- Where the harness offers no label, are the cases of several rules split between rules, and under a check that stops at
  the first mismatch the cases of one rule too, and does the pull request name the missing label as the follow-up,
  unless the stack line or the harness's documentation already records it (§7)?
- Any sleep, wall-clock read, unseeded random, real host, or unordered collection compared as a sequence (§8)?
- Any expected value hidden in a fixture, a helper, or a file (§9)?
- Is the new test beside the existing tests of the same unit, and in the shape of its neighbors unless that shape breaks
  this skill? Beside a table a reference names as the ecosystem's idiom, does it join only where the table asserts for
  it what §5 to §7 ask (§9)?
- Does a case whose twin already exists join that twin rather than copy a setup that has to be compared line by line?
  Does it stand apart only where it is a second case under a check that stops at the first mismatch, the twin and the
  new case are separate acts with a setup short enough to repeat, the twin's helper assembles pieces of syntax, the twin
  is a row of an idiom table that asserts too little or too much for the new case, or the inputs differ in structure and
  cannot stand side by side (§9)?
- Does a new helper repeat the body of a helper the file already has, or copy one that assembles an input from pieces of
  syntax (§9)?
- For each finding: which of the four buckets, and what settles it there: the diff, a run or a citation of the
  harness, the tool's report, or a judgment stated in a sentence (§10)?

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

### Two cases that share a long setup

**Before**: two tests, the same document in each, one line different, and the difference stated nowhere.

```java
@Test
void aNegativeTimeoutIsRefused() {
    String config = """
        server:
          host: localhost
          port: 8080
          timeout: -1
        logging:
          level: info
        """;
    assertThrows(ConfigException.class, () -> Config.parse(config));
}

@Test
void aZeroTimeoutIsAccepted() {
    String config = """
        server:
          host: localhost
          port: 8080
          timeout: 0
        logging:
          level: info
        """;
    assertEquals(Duration.ZERO, Config.parse(config).timeout());
}
```

**After**: the document is built once, the varying value is the helper's argument, and each case carries its name, its
input, and its expected outcome on one line. The outcomes differ in kind, one throws and one returns, so the cases are
two methods. Cases that assert the same way may instead be the arguments of one parameterized test, and the file's
neighbors choose (§9).

```java
private static String configWithTimeout(String timeout) {
    return """
        server:
          host: localhost
          port: 8080
          timeout: %s
        logging:
          level: info
        """.formatted(timeout);
}

@Test
void aNegativeTimeoutIsRefused() {
    assertThrows(ConfigException.class, () -> Config.parse(configWithTimeout("-1")));
}

@Test
void aZeroTimeoutIsAccepted() {
    assertEquals(Duration.ZERO, Config.parse(configWithTimeout("0")).timeout());
}
```

The reviewer reads `-1` against `0` without comparing documents, a change to the document touches one place, and the
report still names each case.

### A case and its control in one check

The harness lints one source and matches each `// expect:` marker against a finding on the next line. A finding on a
line with no marker fails the test too, so a line without a marker expects no finding. The harness stops at the first
marker without a finding and names it by line number. It offers no label for a marker, so the report carries the test's
name and a line. The repository's stack line records all three facts, so the pull request does not propose the label
again (§7).

**Before**: the case and its control are two tests, and each carries its own copy of the class. The silent test
establishes the rule only while the reporting one fires on the same source, and nothing keeps the two sources the same.
One lint run could evaluate both, so they join whatever the length of the class (§7).

```java
@Test
void anUnusedLocalIsReported() {
    lint("""
        class Example {
          void run(int used) {
            // expect: unused-variable
            int unused = 1;
            System.out.println(used);
          }
        }
        """);
}

@Test
void aLocalThatIsReadIsNotReported() {
    lint("""
        class Example {
          void run(int used) {
            int read = 1;
            System.out.println(used);
            System.out.println(read);
          }
        }
        """);
}
```

**After**: one source holds the case beside its control, the name states the rule, and the reader sees the whole
program. A rule about fields would be a second test, since this check stops at the first mismatch.

```java
@Test
void aLocalIsReportedOnlyWhenNothingReadsIt() {
    lint("""
        class Example {
          void run(int used) {
            // expect: unused-variable
            int unused = 1;
            int read = 1;
            System.out.println(used);
            System.out.println(read);
          }
        }
        """);
}
```

A helper `lintLocal(declaration, marker)` would also remove the copy, and it would hide the program behind a template:
it assembles the source from two pieces of syntax, and the reader never sees the program whole.

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
