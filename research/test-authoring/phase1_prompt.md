# Research title

Find proven rules for what a test establishes, at which level, and how its failure reads, for a skill that writes and
reviews tests

# Goal

Run a broad discovery pass to find candidate sources for an LLM skill that writes and reviews **tests** inside a code
repository: the unit test beside a changed class, the test against a public API, the integration test that needs a
running dependency, the regression test that names a fixed defect. The consumer is a coding agent that has just made a
change ("fix the bug", "add the method") and now has to decide which tests the change owes, which inputs they use,
what each one asserts, and how the failure reads when it fires. The same agent reviews tests other people wrote.

The target is the **content and structure of a test**, not the wording of its prose and not the comment above it. What
is missing is guidance on:

- which level a change owes a test at (unit, public API, integration, end to end), and how to decide when more than
  one applies
- which inputs a test set uses: equivalence classes, boundaries, the case that is already covered and need not be
  written again
- how to tell that a test can fail: that it goes red when the behavior it guards is broken, rather than passing
  against any implementation
- how to keep a test from going red when the implementation changes and the behavior does not
- how a failing test reads to someone holding only the runner's report: the name, the assertion, the values, the
  message, and the division of labor between them
- which assertion to use in a given framework so that the report carries the values, and what a message may add
- what makes a test non-deterministic, and what prevents it
- what review rubrics and defect taxonomies exist for tests, and which defects are detectable mechanically

This is Pass 1 only. The goal is discovery and classification, not final ranking.

# Important framing

Do not search for sources that merely match the baseline included at the end of this prompt. The baseline is a
starting point written from practice, not the target. Prefer sources that improve on it, contradict it usefully, or
take a different approach.

It is acceptable to conclude that no single authoritative source covers this domain. In that case, identify the
strongest reusable rule sources and explain how they could be combined.

The consumer of the result is an LLM agent that both writes and reviews tests, so prefer sources that state a rule
**and** its rationale over sources that give a checklist. A rule an agent cannot apply without the author present is
not useful here.

Three properties matter more than they usually do, because the consumer is an agent working inside a repository:

- **Detectability.** For each rule, can a reviewer tell that it was violated from the test file and the diff, without
  running the suite? Sources that describe how a defect is spotted are worth more than sources that describe the
  ideal.
- **Mechanical checkability.** A test is code, and some of its defects have an oracle: a mutation tool reports a test
  that cannot fail, a coverage tool reports a line no test reaches, a runner in random order reports an
  order-dependent test. Sources that say what an oracle catches and what it misses are the ones this pass is looking
  for.
- **Resistance to a writer that optimizes for green.** The agent that writes the test is also the agent that wrote
  the change, and it is rewarded when the suite passes. A rule that lets a test pass by asserting less, mocking the
  unit under test, or mirroring the implementation is a rule that will be gamed. Sources that name these failure
  shapes are worth more than sources that assume good faith.

# Readers

The rules will be organized by reader. The candidate table below is fixed for this pass unless the evidence says a
row is wrong or missing; report either.

| Reader | Situation | Holds |
| --- | --- | --- |
| T1 Red-build reader | A test just failed, often in CI, often not their own | The runner's report: class or module, test name, message, values, stack trace; frequently no IDE |
| T2 Reviewer | Deciding whether a change is adequately tested | The diff of the code and of the tests |
| T3 Refactorer | Changing the implementation with the behavior fixed | A green suite, and the expectation that it stays green |
| T4 Next author | Adding a case, a feature, or a fix beside existing tests | The test directory and the question of where the new test goes and at which level |
| T5 API learner | Reading tests as the examples the documentation lacks | The test file and no other documentation |

Report whether T5 is a reader any source serves, or whether it collapses into T4.

# Out of scope

The following is covered by companion skills and must not be restated or re-derived:

- sentence-level wording: voice, tense, hedging, dialect, the wording of an assertion message or a test name once its
  content is decided (`english-developer-style`)
- the comment or docstring above a test, what it says and in what order (`javadoc-authoring`, `godoc-authoring`,
  `pythondoc-authoring`, `rustdoc-authoring`, `jsdoc-authoring`)
- the commit message and the pull request description of a change that adds tests (`change-description-authoring`)

Also out of scope: CI configuration and test infrastructure; comparisons of test runners, mocking libraries, or
coverage tools; performance, load, and security testing; UI and browser automation tooling; test management and
test-case tracking products; test-driven development as a workflow or a practice to advocate. Include TDD only where
a source states what the workflow guarantees about the resulting test (for example, that the test was observed to
fail before the change), because that guarantee is a property of the artifact.

Treat wording as settled. If a source's only contribution is wording, classify it as a reject and say so in one line.

# Questions the pass should answer

Use these to steer the search. Pass 1 does not have to answer them fully; it has to find the sources that can.

1. **Level.** Which taxonomies of test level exist (unit, integration, end to end; Google's small, medium, large; the
   pyramid, the trophy, the honeycomb), what each one claims about cost and confidence, and which of those claims is
   studied rather than asserted? Given a change, is there a stated rule for which level owes a test, and for when a
   second level is warranted?
2. **Inputs.** What do the black-box test-design techniques (equivalence partitioning, boundary-value analysis,
   decision tables, state transitions, pairwise) prescribe, what evidence exists on their fault-finding, and what is
   known about redundant tests, two tests that cannot fail independently? Where does property-based testing replace
   enumerated cases, and what does it cost the T1 reader?
3. **Sensitivity.** How does a writer or a reviewer establish that a test can fail? Cover mutation testing (its
   evidence, its tools per language, its cost), the coverage-versus-effectiveness literature, the regression test that
   was observed red before the fix, and the shapes of a test that cannot fail: no assertion, an assertion on a value
   the test itself supplied, a mock of the unit under test, an expected value computed by the code under test, a
   change-detector test that pins the implementation.
4. **Robustness.** What guidance exists on keeping a test green across a refactoring: testing through the public API,
   observable behavior versus implementation detail, state verification versus interaction verification, when a test
   double is warranted and which kind, "don't mock what you don't own", brittle tests? Which of it is studied?
5. **The failure report.** What is prescribed for the test's name, for one behavior per test, for the assertion that
   prints the operands, for the message and what it adds, and what evidence exists that any of it shortens the time
   from a red build to a diagnosis? Include the test-smell literature (assertion roulette, eager test, mystery guest,
   conditional test logic, sensitive equality, and their relatives), with what is measured about their harm.
6. **Determinism.** What causes a flaky test, in which proportions, and which practices prevent each cause? Prefer the
   empirical studies over the blog posts.
7. **Organization.** What guidance exists on where a test lives relative to the code it tests, on how test data is
   built so a reader sees what matters (DAMP versus DRY, builders, fixtures, the mystery guest), on the
   arrange-act-assert shape, and on the size of a test class or module?
8. **Framework specifics.** For JUnit 5 with AssertJ, Google Truth, and Hamcrest; pytest; Go's `testing` package with
   `go-cmp` and testify; Rust's built-in test harness; and Jest, Vitest, and `node:test`: which assertion prints the
   operands on failure and which prints only `false`, how a parameterized case is named in the report, where the
   message argument goes, and what the runner prints around the failure. Official documentation and the framework's
   own style guidance count; measured output counts more.
9. **Agent-authored tests.** Which skills, rule files, and system prompts govern test writing for a coding agent, and
   what does the empirical work on LLM-generated tests find about their defects: assertion-free tests, duplicates,
   tautologies, tests that mirror the implementation, tests weakened until they pass? If the category of skills is
   thin, say so; if the empirical work names a checkable defect shape, that is a finding.
10. **Review.** Which review rubrics for tests exist, in code-review guidelines, in contribution guides, in the
    technical literature? Which defects can a linter or a mutation tool report, which can an agent detect from the
    diff, and which need the suite run?

# Search scope

## 1. Practitioner books and engineering-organization guidance

*Software Engineering at Google* (the testing chapters), the Google Testing Blog and its *Testing on the Toilet*
series, Meszaros's *xUnit Test Patterns* and its smell catalog, Khorikov's *Unit Testing: Principles, Practices,
Patterns*, Beck's test desiderata, Osherove, Fowler's articles on test doubles and the test pyramid and their critics.

## 2. Test-design technique standards and syllabi

ISTQB syllabi, ISO/IEC/IEEE 29119-4, Myers's *The Art of Software Testing*, Beizer. Only the technique chapters count:
what to choose as input and why.

## 3. Framework documentation and style guidance

The JUnit 5 user guide, AssertJ and Google Truth documentation including Truth's stated rationale on failure messages,
pytest's documentation on assertion introspection and parametrization, the Go `testing` package documentation and the
Go wiki's test comments, the Rust book's testing chapter and the `assert_eq!` documentation, the Jest and Vitest
documentation and Node's `node:test`.

## 4. Mechanical oracles

Mutation testing tools (PIT, Stryker, mutmut, cargo-mutants, go-mutesting) and their documentation on what a surviving
mutant means; coverage tools only where they state what coverage does not establish; randomized-order and
flakiness-detection runners; test-smell detectors (tsDetect and successors).

## 5. Empirical software-engineering research

Coverage versus fault detection; mutants as a substitute for real faults; test smells and their effect on defects and
maintenance; flaky tests, their causes and fixes; test naming and its effect on comprehension; assertion messages;
test readability; the quality of LLM-generated tests.

## 6. Project contribution guides

Projects with stated rules on what a change owes in tests, on test placement, and on test review: for example the
Linux kernel's KUnit guidance, PostgreSQL's regression-test conventions, Kubernetes, Rust, Go, Django, pytest itself,
JUnit itself.

## 7. Agent skills and rule files for tests

Claude Code skills, Cursor and Continue rules, and system prompts that govern test writing. Report honestly if the
category is thin, and report separately whether any of them address the writer-optimizes-for-green problem.

# Freshness

Prefer sources updated in 2023 or later where the subject is agent-authored tests, flakiness tooling, or framework
behavior. Older sources are acceptable, and expected, where they are established, authoritative, and still cited: the
test-design techniques and the test-smell catalog are decades old, and that is fine.

# What counts as evidence

Treat these as scoring signals, not hard filters:

- adopted by a known engineering organization or a large open-source project
- authored by a named engineer, testing researcher, or framework maintainer
- actively maintained
- ships with concrete before and after examples
- states a rationale, not only a rule
- independent evaluation, criticism, or measured results
- public issue discussions showing real-world trade-offs

Prefer sources with editorial authority over anonymous prompt snippets. Prefer a studied claim over a widely repeated
one, and say which is which.

# Exclusions

Exclude:

- wording guidance (see *Out of scope*)
- tool and framework comparisons, and migration guides between frameworks
- TDD advocacy with no claim about the resulting artifact
- test management and test-case tracking products
- courseware with no developer-testing application
- anonymous prompt lists with no evidence of use
- generic "how to write good tests" listicles with no rationale and no source

# Required output for Pass 1

Produce a discovery report under 3000 words. Do not deeply analyze every candidate yet; the purpose is to build a
strong candidate pool for Pass 2.

## 1. Executive summary

Answer briefly:

- Does any single source cover the content and structure of a test from level selection to the failure report, or is
  synthesis required?
- Which source category looks strongest, and which is weakest or most polluted?
- Is there any existing agent skill for test content, as opposed to test wording or TDD process?
- Does the reader table hold? Is T5 a reader anyone serves?
- Which of the ten questions above look answerable from existing sources, and which look under-served?
- Should Pass 2 concentrate on practitioner guidance, standards, framework documentation, research, or oracles?

## 2. Candidate inventory

Produce a table with 20 to 30 candidates. For each:

- name
- URL
- category: practitioner guidance / standard or syllabus / framework documentation / oracle tool / research / project
  contribution guide / agent skill
- author or organization
- which of the ten questions it speaks to (list the numbers)
- which readers it serves (T1 to T5)
- best use: authoring / reviewing / mechanical checking / background research
- evidence strength: strong / medium / weak, and whether its central claim is studied or asserted
- maintenance status: active / stale / unclear
- one line on why it is worth considering

## 3. Promising shortlist for Pass 2

Select 8 to 12 candidates. For each, in two to four sentences: why it is promising, which rules it may contribute,
which reader it serves, and whether it converts into a compact rule an agent can apply without the author present.

## 4. Obvious rejects

List 5 to 10 sources or categories that looked relevant but should be excluded, with a one-line reason each.

## 5. Gaps and questions for Pass 2

List the main uncertainties. Include at least these, and add your own:

- which rules have a detectable violation from the diff alone, which need the suite run, and which need a mutation
  tool
- which sources conflict with each other, and on what: the pyramid against the trophy, mocks against fakes, one
  assertion per test against one behavior per test, DAMP against DRY
- whether any source treats the test as an artifact its own author may game, and what check it proposes
- whether the level rule survives contact with a real change: a bug fix in a private helper, a new public method, a
  change in a protocol reader
- what is left that only a human can judge

# Baseline

Use the following only as context, and as a snapshot of what practice has already produced. Do not treat it as the
target, and do not limit the search to sources that agree with it. Where a source contradicts it, that contradiction
is a finding worth reporting.

The first part is the test-file section that five doc-comment skills carry today, stripped of what concerns the
comment itself; it is being moved out of those skills because it describes the test rather than its comment. The
second part is four rules stated from practice, not from any source, by the maintainer who asked for this research.
The weakest parts, and the ones most in need of external evidence, are the level rule and the checklist, which are
asserted with no source at all.

---

## Part 1: the failing test as a bug report (from the doc-comment skills)

A test is read in exactly one situation: it just went red. Write for that reader.

A failing test should read as a bug report, and four things write it. Decide what each one carries before you write
the next; the reader sees them together in one report.

- **The class name** (the module path in Rust, the `describe` string in Jest, the module and class in pytest, the
  test function's name over its subtests in Go) carries what every test in it shares: the unit under test and the
  condition they all sit under. A fact true of every test belongs here rather than in each of them.
- **The method name** (the subtest name, the `it` string, the parameterized case's id) states what this one test
  establishes. `aNegativeCountIsRefused` is a finding; `testEnsureBytes` is a location that makes the reader open the
  file. One assertion per method keeps the name able to do this, and keeps the report readable when several methods
  fail at once.
- **The assertion prints the values.** `assertEquals(expected, actual, message)` renders both and opens a diff in an
  IDE; `assertTrue(expected == actual, message)` renders neither and leaves a stack trace to reverse-engineer.
  `assertThrows` prints the expected type the same way. Choose the assertion that already prints what the reader
  needs, rather than describing it in the message.
- **The message adds what the other three cannot.** In a parameterized test that is which invocation ran, so
  `ensureBytes(-2147483648)` is the whole message. Under a bare `assertTrue` it is the invariant, because nothing else
  states it. Where the values are arguments already, do not restate them; where the class or method name states the
  scenario, do not restate that either. A message read while someone scans a stack trace competes with the lines
  around it.

`fail()` with no message is that defect at its limit: it reports that something is wrong and nothing else.

A name is printed in the report; a comment is read only once someone opens the file. Repeating a comment's rule in a
message is the useful duplication; repeating a name is the one that costs.

## Part 2: four rules from practice

1. **Avoid `assertTrue` and `assertFalse`** unless the method under test itself returns a boolean, because the failure
   message of a boolean assertion carries nothing a reader can reason from.
2. **Give every assertion a message that makes the failure read as a bug report** to someone watching a CI log. The
   log already carries the test name, the class name, and the stack trace, so the message does not repeat them.
3. **Choose the level of testing deliberately.** If the feature can be tested with a unit test, make sure the unit
   coverage is good enough. If the feature is reachable through a public API, make sure there are tests through that
   API. If the feature can have an integration test, consider adding one, after checking whether one already exists.
4. **A checklist for the test set:** boundary values are tested; the inputs are partitioned into equivalence classes
   and no class is tested twice; the tests are able to fail when the main code is reverted.
