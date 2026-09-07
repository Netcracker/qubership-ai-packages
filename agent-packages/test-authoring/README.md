# test-authoring

An APM package that governs **what a test establishes, at which level, with which inputs, and how its failure
reads**. It holds in every language and framework; the mechanics that differ per framework, which assertion prints
the values, where the message goes, how a case is named, live in reference files the skill points to.

The skill starts from a correction. A test exists to fail: its value is the production change it would catch, and the
agent that writes it usually wrote that change and is rewarded when the suite is green. So the test for a test is the
change that breaks it, not the run that passes it, and every rule says what a reviewer checks, because the letter of a
rule can be satisfied by a test worth nothing.

## What it covers

- The four readers of a test: the person holding a red build and nothing else, the reviewer holding the diff, the
  refactorer who expects the suite to stay green, and the next author looking for where a case goes.
- What a change owes in tests: nothing where the change cannot alter behavior, and for a dependency bump or a
  regeneration the surface the green suite covers, named; otherwise the smallest level at which the changed behavior
  is observable through the unit's interface, when a second level is owed, what a change made for speed owes, which
  existing tests a deliberate behavior change updates, and the three questions that tell a chosen level from a
  defaulted one.
- Which inputs the test set uses: one test per equivalence partition, each invalid partition alone, the boundaries and
  their neighbors, a decision table for combinations, a state-transition test for history, a property-based test for an
  invariant over a large domain, a test that enumerates an open set when the change adds a member to one.
- The shapes of a test that cannot fail, each visible in the diff: no assertion, an expected value computed by the code
  under test, an assertion on a value the test supplied, the unit replaced by a mock, an assertion on the mock, a test
  that passes because nothing threw, a change detector, an assertion weakened until it passes, a snapshot accepted
  unread, a regression test never seen red.
- The two oracles a reviewer may ask for, red on the base commit and a mutation verdict read as the tool defines it,
  and why a coverage figure is neither.
- Keeping a test green across a refactoring: the unit's interface, state over interactions, real before fake before stub,
  no mock of a type the repository does not own, the fields the behavior defines, no logic in the test.
- The failure report and its four parts, container, name, assertion, message, with what each carries and what it may
  not repeat; the assertion that prints the operands; the framework's operand order; parameterized case names;
  grouped assertions; error semantics over message strings; what a failed wait reports.
- Determinism as a checklist keyed by cause, each with its one fix, and the random-order run for the cause the file
  does not show.
- Organization: values in the test body rather than in a fixture, where a new test goes, when a class splits.
- The four buckets a review finding falls into: decidable from the diff, needs a run, needs a tool's verdict, or a
  question for a human.

## Scope

Every language. The skill body carries the rules; `references/` carries the mechanics, one file per role a library
plays in a test, grouped by ecosystem:

| Role | Files |
| --- | --- |
| Test engine | `java/junit5.md` (JUnit 5 and 6), `java/junit4.md`, `python/pytest.md`, `go/testing.md`, `rust/libtest.md`, `javascript/jest.md`, `javascript/vitest.md`, `javascript/node-test.md` |
| Assertion library | `java/junit5-assertions.md`, `java/junit4-assert.md`, `java/assertj.md`, `java/truth.md`, `java/hamcrest.md`, `go/testify.md` |
| Test doubles | `java/mockito.md` |
| Property-based testing | `java/jetcheck.md` |
| Structural tests | `java/archunit.md` |
| Mutation | `mutation-tools.md` |

A file covers one major version of its library and assumes the latest minor; JUnit 4 and JUnit 5 differ in how a test
is written and have separate files, JUnit 5 and 6 do not. The skill opens one file per role the project uses, chosen
from the line in the repository's instructions that names the stack, or from the imports of the nearest existing
test. The failure output each file quotes was measured; the versions and the raw output are in
[`research/test-authoring/framework_output.md`](../../research/test-authoring/framework_output.md).

The comment or docstring above a test is not this package's. It belongs to the doc-comment skill of the language:
[`javadoc-authoring`](../javadoc-authoring/), [`godoc-authoring`](../godoc-authoring/),
[`pythondoc-authoring`](../pythondoc-authoring/), [`rustdoc-authoring`](../rustdoc-authoring/), and
[`jsdoc-authoring`](../jsdoc-authoring/). Those five say what the comment on a test carries and point here for the
test itself.

## Contents

- `.apm/instructions/test-authoring.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/test-authoring/SKILL.md`: the rules, a review checklist, and three worked examples.
- `.apm/skills/test-authoring/references/`: one file per role and library, grouped by ecosystem.

The research behind the rules, with the sources and the evidence label of each, is in
[`research/test-authoring`](../../research/test-authoring/).

## Name the test stack in the project's instructions

Put one line in the repository's `AGENTS.md` or `CLAUDE.md` that names the test stack, role by role, with the major
version and nothing finer:

```text
Tests: JUnit 5 engine, JUnit 5 assertions; Mockito for doubles; jetCheck for property-based tests; ArchUnit for structural tests.
Tests: JUnit 5 engine, AssertJ assertions; no Hamcrest in new tests.
Tests: JUnit 4 engine with Hamcrest matchers; the module cannot move to JUnit 5 yet.
Tests: pytest; Hypothesis for property-based tests; no unittest.TestCase classes in new tests.
Tests: Go testing with testify require; fake clients from k8s.io/client-go/kubernetes/fake, with PrependReactor for injected errors.
Tests: cargo test; rstest for parameterized cases; proptest for property-based tests.
Tests: Vitest; expect.soft for several assertions on one result; msw for HTTP fakes.
Tests: node:test with node:assert/strict; no test framework dependency.
```

The skill opens its reference files from that line. Without it the agent reads the build file and the nearest test
to find the engine and the assertion library, on every task, and where the two disagree it guesses. Two more lines
save the same search again: the command that runs one test, and where a new test goes.

```text
Run one test class with `./gradlew --quiet :postgresql:test --tests '<class>'`; a PostgreSQL 16 on localhost:5432 accepts user test, password test, database test.
Unit tests sit beside the code under test; tests that need the server live under src/test/java/org/postgresql/test.
```

## Pairs with

- The developer-style skill of the language the repository writes in owns wording: the phrasing of a test name or a
  message once this package has decided what it carries. That is [`english-developer-style`](../english-developer-
  style/) unless the repository's instructions name another, such as [`russian-developer-style`](../russian-developer-
  style/) or [`french-developer-style`](../french-developer-style/). Install this package with one of them.
- The five doc-comment packages above own the comment on a test.
- [`change-description-authoring`](../change-description-authoring/) owns the commit message and the pull request
  description, including the sentence that names the level a change was tested at.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/test-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/test-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.3.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
