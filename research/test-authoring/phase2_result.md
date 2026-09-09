# Pass 2 report: rules for a test authoring and review skill, extracted from the Pass 1 shortlist

Every rule below is labeled **studied** (a measured result whose paper was read), **asserted** (a practitioner or
standards document, stated without measurement), **documented** (a framework's own documentation), **measured** (the
output recorded in `framework_output.md` on 2026-09-06), or **derived** (inferred here from mechanics). No asserted
rule has been promoted. Where a Pass 1 figure was inexact, section 11 carries the corrected figure and says what was
corrected. Rules are numbered R1 to R44 and referred to by number throughout.

## 1. Executive summary

**Rule contributors.** Seven candidates survive as rule contributors: Google's chapters 12 and 13 with the nine
Testing on the Toilet posts (robustness, doubles, one behavior per test, DAMP, narrow assertions, the failure
message); the Go wiki (the failure line and its parts, keep going, error semantics, subtest names); superpowers'
`writing-good-tests.md` (the shapes a writer optimizing for green produces, and the gate that names the break);
ISTQB 4.2 (partitions, boundaries, decision tables, state transitions); Khorikov (the one criterion for a mock that an
agent can apply: an unmanaged out-of-process dependency); the mutation-tool documentation (what each verdict
establishes); and the framework documentation with the measured output (the per-framework table). Three drop to
supporting: Beck's desiderata (vocabulary and headings), the flakiness studies (proportions behind the determinism
checklist, which is itself a list of causes with one fix each), and the agent-behavior studies (which shapes to look
for first and how often they occur). Two drop to background: the sensitivity-evidence cluster (it labels R10 and R11
but yields no further rule) and the test-smell literature, because Panichella's per-smell results, now read, leave
only Indirect Testing and Conditional Test Logic as smells worth flagging from the file and demote Eager Test and
Assertion Roulette to "ubiquitous and harmless in JUnit 4 and later".

**Settled and open.** Questions 1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 13, and 14 are settled to the extent the evidence
allows; sections 3 to 10 state the answers. Question 5 (the level rule) is answered by derivation and labeled so;
no source states it. Question 8 is settled for the techniques and open on Reid's figures: the paper is paywalled and
was not reached, so the 0.79 and 0.33 stay unconfirmed. One sub-question of 7 stays open by the nature of the
evidence: no study measures time to diagnosis as a function of name, assertion, or message, so every failure-report
rule is asserted, with the measured output saying only what each framework prints.

**The four buckets.** Of the 44 rules, 33 are applied from the diff alone; 4 need a run of the suite (the two-run
regression evidence, the random-order run, the uniqueness of parameterized names, the property test's reproducer); 3
are tool verdicts (mutation survived and no-coverage, coverage as a non-signal, the order-dependence classifier); 4
stay with a human (the partition set against the specification, the mock criterion, whether a flaky fix belongs in
the code under test, the level choice), and the agent raises those as questions. Several diff rules also have a tool
that confirms them, and section 9 says which.

**Gaming.** The rules that resist a writer optimizing for green are the ones with an oracle or an external
reference: R9 (red on the base commit), R10 (a surviving mutant), R26 (a random-order failure), R38 (partitions from
the specification, not from the implementation's branches), R41 (a shrunk counterexample). The rules that can be
satisfied without the test being worth anything are the shape rules, and each of them says what the reviewer checks
then: an assertion added to satisfy R2 can be a sanity check (R12); a literal added to satisfy R3 can be the pasted
output of the code under test (the reviewer derives it from the specification); a mock moved one level down to
satisfy R5 can still swallow the side effect the test depends on (R16's "list the side effects"); a name that
satisfies R29 can describe a behavior the body does not assert (R1). The skill has to carry both halves of each row.

## 2. Deep candidate evaluation

| # | Candidate and URL | Disposition | Strongest contribution | Main weakness | Evidence | Maintenance | Examples | False-positive risk | Portability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SWE at Google ch. 12, 13 and nine ToT posts ([ch12](https://abseil.io/resources/swe-book/html/ch12.html), [ch13](https://abseil.io/resources/swe-book/html/ch13.html), [ToT 2013](https://testing.googleblog.com/2013/03/testing-on-toilet-testing-state-vs.html), [2014a](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html), [2014b](https://testing.googleblog.com/2014/10/testing-on-toilet-writing-descriptive.html), [2015](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html), [2017](https://testing.googleblog.com/2017/12/testing-on-toilet-only-verify-state.html), [2018](https://testing.googleblog.com/2018/06/testing-on-toilet-keep-tests-focused.html), [2019](https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html), [2020](https://testing.googleblog.com/2020/07/testing-on-toilet-dont-mock-types-you.html), [2024](https://testing.googleblog.com/2024/04/prefer-narrow-assertions-in-unit-tests.html)) | Rule contributor | Rule, rationale, and a before/after per post: state over interactions, only verify state-changing calls, one behavior per test with the act-assert-act signal, DAMP, narrow assertions, don't mock types you don't own, change detectors | Everything asserted; no input-selection rule; no level rule; "narrow assertions" conflicts with the Go wiki's "compare full structures" (§8) | Asserted (Google practice; ch13 reports the maintenance cost of interaction tests qualitatively, no numbers) | Active (2024 post) | Yes, every post | Low | Easy |
| 2 | Go wiki [TestComments](https://go.dev/wiki/TestComments), [CodeReviewComments](https://go.dev/wiki/CodeReviewComments) | Rule contributor | The failure line as `YourFunc(%v) = %v, want %v`: function, input, got, want, diff direction; keep going with `t.Error`; test error semantics; human-readable subtest names | Go-specific operand order; "compare full structures" needs the reconciliation in §8 | Asserted (Go team review practice) | Active | Yes | Low | Easy once the order is stated per framework |
| 3 | superpowers [writing-good-tests.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/writing-good-tests.md), [SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md) | Rule contributor | Names the gameable shapes with a gate: "name the production change that would make this test fail"; the mirror assertion; the mock earns no assertion; the mutation check; the warning-signs list | No rationale beyond one sentence each; TDD framing ("no production code without a failing test") is a process rule, out of scope; no failure-report rules | Asserted (one author's practice) | Active (2025 to 2026) | Yes, TypeScript | Medium (the warning signs are heuristics) | Easy; already in rule form |
| 4 | Sensitivity cluster: [Inozemtseva & Holmes](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf), [Just et al.](https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf), [Zhang & Mesbah](https://people.ece.ubc.ca/amesbah/resources/papers/fse15.pdf), [Petrović et al. ICSE](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf), [TSE](https://arxiv.org/abs/2102.11378) | Background (labels R10, R11, R2, R30) | Coverage is not effectiveness; mutants are coupled to 73% of real faults; assertion count and assertion coverage track effectiveness; surfacing mutants in review makes developers write more and stronger tests | Yields evidence labels, not rules; Zhang's Finding 8 (assertTrue/False assertions the most effective type) cuts against a naive reading of "avoid assertTrue" | Studied (31,000 suites / 5 systems; 357 faults, 230,000 mutants; 6,700 suites, 24,000 assertions; 14.7 M mutants, 662,584 changes) | Stale papers; Petrović active | No | n/a | n/a |
| 5 | Mutation tools: [Stryker states](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/), [cargo-mutants](https://mutants.rs/using-results.html), [PIT](https://pitest.org/quickstart/basic_concepts/), [PIT incremental](https://pitest.org/quickstart/incremental_analysis/), [mutmut](https://mutmut.readthedocs.io/) | Rule contributor | Exact verdict semantics: Survived = all tests passed with the mutant active; No coverage = no test reached the line; Unviable = no information; "missed" prioritized where non-detection is surprising | mutmut's docs do not define its statuses on the pages reached; equivalence is undecidable by the tool | Documented | Active | cargo-mutants gives guidance, others only definitions | Low for the verdict; medium for "equivalent" | Easy |
| 6 | Flakiness: [Luo et al.](https://petertsehsun.github.io/soen7481/papers/flakyTests.pdf), [Parry et al.](https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf), [pytest-randomly](https://github.com/pytest-dev/pytest-randomly), [MethodOrderer.Random](https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/MethodOrderer.Random.html) | Supporting (proportions and fixes for R23 to R27) | Cause taxonomy with counts and the fix per cause (waitFor 54% of async fixes; cleaning shared state 74% of order fixes); 24% of fixes change the code under test and 94% of those fix a real bug | Counts are from Apache projects in 2014; the survey's proportions vary by study | Studied (201 commits, 51 projects; 76 papers) | Luo stale; Parry active | Luo gives code examples | Low | Easy as a checklist |
| 7 | Test smells: [Meszaros catalog](http://xunitpatterns.com/Test%20Smells.html), Bavota et al. 2015, [Spadini et al. 2018](https://research.tudelft.nl/en/publications/on-the-relation-of-test-smells-to-software-code-quality), [Panichella et al. 2022](https://digitalcollection.zhaw.ch/bitstreams/d3cb274c-05f9-4e3e-b583-5307692391e3/download), tsDetect | Background; the catalog supplies names for R19, R22, R24, R42 | Panichella's per-smell results (§ 3 notes, § 8 conflict 4): Eager Test present in 80% of developer suites and semantically incoherent in only 10% of those; Assertion Roulette moot under JUnit 4+; Indirect Testing at 20% is the one developers avoid | Detectors misclassify; Bavota's abstract is paywalled today (Pass 1 verification read it through the cookie redirect) | Studied, and in conflict (§8) | Catalog stale (2007), Panichella active | Panichella gives figures 8 to 10 | High if applied mechanically (Panichella's point) | Hard; keep names, drop the detector rules |
| 8 | [ISTQB CTFL v4.0 §4.2](https://www.gasq.org/files/content/gasq/downloads/certification/ISTQB/Foundation%20Level/ISTQB_CTFL_Syllabus-v4.0%20.pdf), Reid 1997 ([IEEE 637166](https://ieeexplore.ieee.org/document/637166/)), Myers ch. 4 | Rule contributor | Precise definitions: partitions non-overlapping and non-empty; one test per partition and why; valid and invalid; 2-value and 3-value BVA with the `x ≤ 10` versus `x = 10` example; decision-table columns; all-states, valid-transitions, all-transitions coverage | Reid unreachable; the syllabus gives no rule for choosing partitions from a signature, which stays a human judgment | Asserted standard; Reid studied (one Ada system, figures unconfirmed) | Active (2023) | Yes (BVA example) | Low | Easy |
| 9 | Beck, [Test Desiderata](https://testdesiderata.com/) | Supporting (headings) | Twelve one-line properties; *Behavioral*, *Structure-insensitive*, *Isolated*, *Deterministic*, *Specific* name what §3 groups by | No detection, no examples | Asserted | Stale (2019) | No | n/a | Easy as vocabulary |
| 10 | Khorikov, [When to mock](https://enterprisecraftsmanship.com/posts/when-to-mock/), [book](https://www.manning.com/books/unit-testing) | Rule contributor (R16) | Managed versus unmanaged out-of-process dependencies; intra-system communication is an implementation detail, inter-system communication is observable behavior | The Manning page does not list the four pillars; only the blog post was readable; asserted | Asserted | Stale (2020) | Blog post, no code | Low | Easy |
| 11 | Framework docs: [JUnit assertions](https://docs.junit.org/current/writing-tests/assertions.html), [JUnit parameterized](https://docs.junit.org/current/writing-tests/parameterized-classes-and-tests.html), [AssertJ](https://assertj.github.io/doc/), [Truth](https://truth.dev/comparison), [pytest assert](https://docs.pytest.org/en/stable/how-to/assert.html), [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html), [Rust book](https://doc.rust-lang.org/book/ch11-01-writing-tests.html), [assert_eq!](https://doc.rust-lang.org/std/macro.assert_eq.html), [Jest expect](https://jestjs.io/docs/expect), [Jest api](https://jestjs.io/docs/api), [Vitest expect](https://vitest.dev/api/expect.html), [Vitest api](https://vitest.dev/api/), [node:test](https://nodejs.org/api/test.html), [testify](https://pkg.go.dev/github.com/stretchr/testify/assert), [go-cmp](https://pkg.go.dev/github.com/google/go-cmp/cmp), [KUnit tips](https://www.kernel.org/doc/html/next/dev-tools/kunit/tips.html) | Rule contributor (§4) | Which assertion prints the operands, where the message goes, whether it adds or replaces, how a case is named | None of it is a universal rule; each is a convention the skill must present per framework | Documented, plus measured | Active | Yes | Low | Medium (a table, not prose) |
| 12 | Agent-behavior and LLM test-quality studies: [2602.00409](https://arxiv.org/abs/2602.00409), [2602.07900](https://arxiv.org/abs/2602.07900), [2606.28430](https://arxiv.org/abs/2606.28430), [2406.12952](https://arxiv.org/abs/2406.12952), [2511.16858](https://arxiv.org/abs/2511.16858), [2302.06527](https://arxiv.org/abs/2302.06527), [2305.04207](https://arxiv.org/abs/2305.04207), [2410.10628](https://arxiv.org/abs/2410.10628), [2305.00418](https://arxiv.org/abs/2305.00418) | Supporting (which shapes to look for first) | Agents add mocks in 36% of their test commits versus 26% for people; print statements outnumber assertions in agent test artifacts; with a visible oracle the score is near-perfect while the library is "dead or absent"; a fail-to-pass test doubles fix precision; 21.8% to 33.0% of patches that pass generated tests fail the hidden ones | Each is one benchmark or one year of commits; the defect shapes are named, not ranked by harm | Studied (1.2 M commits, 48,563 by agents; six models on SWE-bench Verified; 18 runs; 449 instances) | Active (2024 to 2026) | Some | n/a | Easy as a "look here first" list |

## 3. Extracted rules

Reader codes: T1 red-build reader, T2 reviewer, T3 refactorer, T4 next author. Bucket codes: **D** agent from the
diff, **S** suite run, **M** mutation or smell tool, **H** human. A second code in the bucket column names the oracle
that confirms a diff rule where one exists.

| # | Rule | Rationale | Reader | Source | Basis | Applies to | Detection | Gaming | Repair | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Before writing the body, name the production change that would make this test fail, and confirm it is a bug and not a decision. | T2 cannot tell a test that guards a behavior from one that guards a constant; the second fires on redesign and sleeps through bugs. | T2 | superpowers gate; Google ToT 2015 | Asserted | All | Whole-test judgment: the reviewer names the mutation; if only a renamed field or a changed constant would fail it, R8 | Claimable in a PR comment; confirmed by R10 | Redesign around an observable behavior | D, M |
| R2 | Every test asserts on an outcome the code under test produced; a test with no assertion, or with print statements in place of one, is not a test. | A test that cannot fail reports green to T2 for nothing; assertion count and assertion coverage track fault detection. | T2 | Zhang & Mesbah; Chen et al. 2602.07900; superpowers | Studied (6,700 suites; six models on SWE-bench Verified) | All | File: no `assert`/`expect`/`verify`; `print`/`console.log` of results; Jest/Vitest `expect.hasAssertions` missing on async callbacks | Add `assertNotNull(result)`: see R12 | Assert the value the behavior defines | D |
| R3 | Expected values are literals or hand-derived fixtures, never computed by the code under test or by a helper that reimplements it. | A mirror assertion is true whatever the code does; T2 sees a passing test that establishes nothing. | T2 | superpowers "mirror assertion"; Google ch. 12 "no logic in tests" | Asserted | All | Diff: the expected operand calls production code or a helper with the same arithmetic; loops that build both sides | Paste the observed output as the literal; the reviewer derives the value from the specification, the issue, or by hand | Replace with a literal derived without the code | D |
| R4 | Do not assert on a value the test supplied and never passed through the code under test. | Setup and assertion sharing an object guarantees equality; nothing was exercised. | T2 | superpowers warning signs | Asserted | All | Diff: assertion operand is a test-local object also used in setup with no call on the unit between them | Low | Read the value back through the public API | D |
| R5 | Do not replace the unit under test, or the collaborator whose behavior the test names, with a mock or stub. | The test then verifies the double, and the unit can be wrong or absent; agents add mocks in 36% of their test commits against 26% for people. | T2 | superpowers; Hora & Robbes 2602.00409 | Asserted rule; studied prevalence (11,035 agent test commits) | Tests with doubles | Diff: mock target equals the symbol the test name or the diff changed; `spyOn` on the unit; partial mocks | Mock one level down but still swallow the side effect: R16 | Unmock; move the double below the side effect the test depends on | D |
| R6 | The mock earns no assertion: never assert that a stub returned what it was told to or that a mock is present. | The assertion passes when the mock exists and fails when it is removed; it says nothing about the unit. | T2 | superpowers | Asserted | Tests with doubles | Diff: assertion operand is a configured return value; `*-mock` test ids; `expect(mockFn).toHaveBeenCalled()` as the only assertion | n/a | Assert the unit's output; delete the assertion | D |
| R7 | A test whose only failure mode is an exception (a bare call, `assertDoesNotThrow` alone, a `try/except: fail()`) names no outcome; assert the value or state. | T1 gets "passed" or a stack trace, never the behavior; T2 cannot name the bug it guards. | T2 | superpowers warning signs; Django coding style on `assertTrue` | Asserted | All | File: no assertion after the act; `assertDoesNotThrow` or `pytest.raises` absent and no assertion | n/a | Assert the returned value or the state | D |
| R8 | Do not write change-detector tests: a test that restates the implementation (in-order verification of collaborator calls, a constant compared with itself, a snapshot of private structure) has negative value. | It fails on every refactoring and catches no defect; T3 pays for it on every change. | T3 | Google ToT 2015; ch. 13 | Asserted | All | Diff: `verify` chain mirrors the method body; `expect(MAX_RETRIES).toBe(5)`; a refactoring PR that edits it (R20) | n/a | Test the behavior that depends on the decision ("retried 5 times, no 6th attempt") | D, M |
| R9 | A regression test is observed red on the pre-fix code and green after, and the pull request carries the evidence. | Without the red run T2 has only the author's word that the test exercises the bug; a fail-to-pass test doubles the precision of fix filtering. | T2 | Django submitting-patches; rustc-dev-guide; pytest contributing; SWT-Bench 2406.12952 | Asserted policy; studied criterion | Regression tests | Suite run on the base commit; or the PR's test-first commit, or the pasted failing output | A test that is red on base for another reason (a missing symbol); the reviewer checks that the failure message names the bug's symptom | Run on base, paste the output, or commit the test before the fix | S |
| R10 | Read a mutation verdict as the tool defines it: *survived* on a changed line is a missing or weak test; *no coverage* is a missing test; *unviable* or compile error is no information; equivalence is a human call after the first two are excluded. | The verdict is the only mechanical proof that a test can fail; shown to developers in review it makes them write more and stronger tests. | T2 | Stryker; PIT; cargo-mutants; Just et al.; Petrović et al. | Documented; studied (73% of real faults coupled; 14.7 M mutants) | Where a tool exists | Tool verdict scoped to the diff (PIT incremental, `cargo mutants --file`, mutmut re-tests changed functions) | A test that asserts the mutated expression itself; the reviewer applies R1 to the killing test | Strengthen the assertion or add the partition | M |
| R11 | A coverage figure is not evidence that a test can fail; do not accept one, or demand one, as the quality gate. | Coverage correlates low to moderately with effectiveness once suite size is controlled; a fixed target does not produce an effective suite. | T2 | Inozemtseva & Holmes | Studied (31,000 suites, 5 systems) | All | PR argument "coverage is N%" with no R9 or R10 evidence | This is the gaming | Ask for the red run or the mutation run | M |
| R12 | Do not weaken an assertion to make it pass: an existence, type, not-null, or `len > 0` check where the behavior defines a value is a sanity check, not a test. | The test stays green through wrong values; agent assertions concentrate on exact and property checks but sanity checks are the shape that survives a wrong fix. | T2 | Chen et al. 2602.07900 (assertion categories); superpowers | Studied categories; asserted rule | All | Diff: equality replaced by `isNotNull`, `toBeDefined`, `contains`, `instanceof`; a widened range or delta | This is the gaming | Assert the value | D, M |
| R13 | A snapshot or golden file is an expected value: accept it only after reading it, and let it cover the output the behavior defines, not the whole rendering. | An unread snapshot is R3 in disguise; a whole-rendering snapshot is a broad assertion that fails on every unrelated change. | T2 | Google ToT 2024 (one screenshot test); superpowers "behavior, not text"; PostgreSQL regress-evaluation | Asserted | Snapshot tests | Diff: snapshot updated in the same commit as the behavior with no note; `-u` update commits | This is the gaming | Name what changed in the snapshot and why; narrow it | D, H |
| R14 | Test through the public API of the unit; a private helper is tested through the caller that reaches it. | A test bound to a private name breaks on every rename; T3 cannot restructure. | T3 | Google ch. 12; Khorikov | Asserted | All | Diff: reflection, `@VisibleForTesting`, test-only exports, `_private` calls, `#[cfg(test)] pub` | Widen visibility to satisfy; the reviewer asks whether the API change is wanted | Test through the caller | D |
| R15 | Verify state, not interactions: assert the return value or observable state, and verify a call only when the call is the behavior, that is, a state-changing call to a collaborator outside the unit. | Verifying a query is redundant and brittle; the code can call the right method and do the wrong thing with the result. | T3 | Google ToT 2013, 2017; ch. 13 | Asserted | Tests with doubles | Diff: `verify(mock).getX()`, `toHaveBeenCalled` on a query, `verifyNoMoreInteractions`, `inOrder` | n/a | Stub the query, assert the result; verify only the command | D |
| R16 | Prefer the real dependency; use a fake when the real one is slow, non-deterministic, or unconstructible; stub what neither supplies; mock, in the sense of interaction verification, only an unmanaged out-of-process dependency. | Each step down leaks implementation into the test and stops guaranteeing the contract; a mock of a managed dependency tests a fiction. | T3 | Google ch. 13; Khorikov; superpowers; Hora & Robbes | Asserted; studied prevalence | Tests with dependencies | Diff: mock of an in-process collaborator; mock setup larger than the test body; missing side effects in the double | "Unavoidable" claimed; the reviewer asks which of the three criteria applies and which side effects the double drops | Real, then fake, then stub | D, H |
| R17 | Do not mock types you do not own; wrap them and fake or use the real implementation. | The mock encodes assumptions the library can break silently; the test keeps passing when the code is wrong. | T3 | Google ToT 2020 | Asserted | Tests with third-party dependencies | Diff: `@Mock`/`jest.mock` on a library class or module | n/a | Wrapper plus fake; test the wrapper against the real thing | D |
| R18 | Assert the fields the behavior defines; compare a whole value only where the whole value is the behavior (a pure function's result), and keep at most one full-equality test per common case. | Whole-object equality on an entity fails when an unrelated field is added; T3 fixes tests that found nothing. | T3 | Google ToT 2024; Go wiki "compare full structures" (reconciled in §8) | Asserted | All | Diff: `EXPECT_EQ(entity, expected)` in a test named after one field; `toEqual` on a large object | Narrowing to one field where the behavior defines several: R12 | Assert the relevant fields; `cmp.Diff` on a returned value | D |
| R19 | No logic in tests: no loops, conditionals, or computed strings on the path to an assertion. | A test with logic can be wrong in the same way as the code; the URL example hides a double slash behind concatenation. | T2 | Google ch. 12; Meszaros Conditional Test Logic | Asserted | All | File: `if`/`for`/`try` in the test body; expected strings built by concatenation | n/a | Unroll; write the literal | D |
| R20 | A pure refactoring changes no test; a refactoring PR that edits tests is flagged and the edited tests examined for R8. | The refactoring is the moment a change detector shows itself; T3 should not pay for it. | T3 | Google ch. 12 "unchanging tests"; Beck *Structure-insensitive* | Asserted | Refactoring PRs | Diff: tests touched in a PR described as refactoring | n/a | Fix the test's coupling, not the refactoring | D |
| R21 | Test the contract your code makes at its boundary, not the framework's mechanics; constructors, getters, and forwarding earn a test only when they validate, default, derive, or cause side effects. | A test of the router calling the handler is the framework's test; it costs maintenance and guards nothing of yours. | T2 | superpowers | Asserted | All | Diff: assertion that a framework invoked a registered callback; a getter test | n/a | Assert the first consumer-visible result | D |
| R22 | Production code carries no test-only methods; cleanup and reset live in test utilities. | A `destroy()` only tests call is test logic in production and a hook for R24 violations. | T3 | Meszaros Test Logic in Production; superpowers | Asserted | All | Diff: a production method whose only callers are tests | n/a | Move to a test utility | D |
| R23 | Wait on a condition, never on a fixed delay. | Async wait is the largest flakiness cause (74 of 161 classified fixes); 54% of those fixes replace the delay with `waitFor`. | T3 | Luo et al.; Kubernetes e2e guide | Studied (201 commits) | Async tests | File: `sleep`, `Thread.sleep`, `setTimeout` used as a wait | A longer sleep; still R23 | Poll or await the condition with a message per R37 | D |
| R24 | No shared mutable state between tests: no static or class-level fixture a test mutates, no rows or files left behind. | Order dependency is the third flakiness cause; 74% of its fixes clean shared state; static fields carry 61% of it. | T3 | Luo et al.; Parry et al.; Meszaros Interacting Tests; Google test sizes | Studied; asserted | All | File: a static mutable field written in a test; a shared fixture mutated; no teardown | n/a | Per-test fixture; teardown; R26 to confirm | D, S |
| R25 | No dependence on the wall clock, unseeded randomness, the network, the platform, the iteration order of an unordered collection, exact floating-point equality, or an assertion range that excludes valid outputs. | Each is a named flakiness cause with one fix; the last three are the ones agents and people write as correct-looking assertions. | T3 | Luo et al.; Parry et al. (Eck et al. categories); PostgreSQL regress-evaluation | Studied taxonomy | All | File: `now()`, `random()` without a seed, real hosts, `==` on floats, `set` order assumed, `elapsed < 100ms` | n/a | Inject clock and seed; fake the network; sort before comparing; approximate; widen to the specification's range | D |
| R26 | Run the suite in random order with the seed printed, and fix an order-dependent test by R24, never by pinning the order. | The random-order runner is the only cheap oracle for order dependence, which the file does not always show. | T3 | pytest-randomly; JUnit `MethodOrderer.Random`; Beck *Isolated*; Google test sizes | Documented; asserted | All | Random-order run fails; iDFlakies classifies order-dependent versus not | Pin the order (`@Order`, `-p no:randomly`) | R24 | S |
| R27 | A flaky test is neither retried nor deleted; decide whether the fix belongs in the code under test. | 24% of flaky-test fixes change the code under test and 94% of those fix a real bug; a retry hides it. | T3 | Luo et al.; Kubernetes flaky-tests policy | Studied; asserted policy | Flaky tests | CI config with rerun-until-green; `@Retry`, `@Flaky`, skip | This is the gaming | Root-cause by R23 to R25; file a bug when the code is wrong | H |
| R28 | Divide the failure report: the container carries the unit and the condition all its tests share; the test name carries scenario and expected outcome; the assertion carries got and want; the message carries the input and the function when the assertion cannot. | T1 reads the four together on one screen; a fact stated in the wrong slot is repeated or missing. | T1 | Google ch. 12; Go wiki; Google ToT 2014; `framework_output.md` | Asserted; measured (what each slot prints) | All | File: a message that restates the name; a name that is a location; a container named after a file | n/a | Move each fact to its slot | D |
| R29 | Name the test by scenario and expected outcome so the failure line reads as a sentence; not the method name alone, not a location, not an issue number. | T1 should know what broke without opening the file; a name with "and" signals two behaviors. | T1 | Google ToT 2014; ch. 12; Django coding style; Wu & Clause | Asserted; studied detector (95% true-positive rate on 34,352 tests) | All | File: `testEnsureBytes`, `testCase3`, `test_issue_1234`, a name with "and" | A name describing a behavior the body does not assert: R1 | `<unit>_<scenario>_<outcome>` or a `should` sentence | D |
| R30 | Use the assertion that prints the operands; a boolean wrapper around a comparison prints `true`/`false` or the expression text. | `assertTrue(expected == actual)` reports `expected: <true> but was: <false>`; T1 reverse-engineers the values from a stack trace. | T1 | `framework_output.md`; JUnit, Rust, pytest, node docs; Zhang Finding 8 as the caveat | Measured; documented; studied caveat | All | File: `assertTrue(a == b)`, `assert!(a == b)`, `assert.ok(x === y)`, `assertThat(a == b).isTrue()` | n/a | `assertEquals`, `assert_eq!`, `strictEqual`, `is(expected)` | D |
| R31 | The message supplies the function and the input when the assertion cannot, and nothing the assertion or the name already prints. | Go's `YourFunc(%v) = %v, want %v` is the whole report in one line; a repeated name competes with the lines around it. | T1 | Go wiki; JUnit, AssertJ, pytest, Rust docs; Takebayashi et al. | Asserted; documented; studied (messages rarely supplied, 20 systems) | All | File: message repeats the name; no message on a bare boolean assert; no message inside a loop over cases | n/a | `ensureBytes(%d)` form; drop the repetition | D |
| R32 | Keep the framework's operand order so the labels are right: got before want in Go; expected before actual in JUnit, testify, Hamcrest; the actual value first in AssertJ, Truth, Jest, Vitest, `node:assert`; either in Rust and pytest. | A swapped pair prints the bug as the expectation. | T1 | Go wiki; JUnit docs; testify docs; Rust book | Documented | All | File: `assertEquals(actual, expected)`; `Foo() = want, got` | n/a | Swap | D |
| R33 | A parameterized case carries a name that identifies it; an index alone is a location, and two cases with one name hide each other. | T1 sees `test_param[minus one]` or `[3]`; only the first says which input failed. | T1 | pytest parametrize; JUnit `name=`/`Named`; Jest and Vitest `%s`/`$var`; Go wiki subtest names | Documented; measured | Parameterized tests | File: `ids` absent on non-scalar values, `t.Run("", …)`, `%#` alone; uniqueness needs a run | n/a | Name from the scenario; `pytest.param(id=)` | D, S |
| R34 | Several assertions on one behavior report together (`assertAll`, `expect.soft`, `t.Error`, `EXPECT_*`); abort (`t.Fatal`, `require`, `ASSERT_*`) only when continuing is meaningless. | One run then shows every failed check instead of the first. | T1 | Go wiki "keep going"; KUnit tips; JUnit `assertAll`; Vitest `expect.soft` | Documented | Tests with several assertions | File: a chain of hard asserts on one result's fields; `require` on every line | n/a | Group them | D |
| R35 | One behavior per test: after asserting the output of one call on the unit, the test does not call the unit again. | A second act after an assert is a second scenario; its failure masks the first and its name cannot say both. | T1, T4 | Google ToT 2018; ch. 12; Panichella (semantic coherence, not assertion count, is the harm) | Asserted; studied refinement | All | File: act, assert, act; a name with "and" | n/a | Split, or parameterize | D |
| R36 | Compare error semantics, not message strings: type, sentinel, code; match a message only on the part the behavior defines. | A pinned message is a change detector for wording; T3 breaks it by improving a sentence. | T3 | Go wiki "test error semantics"; pytest `match=`; Rust `should_panic(expected=)`; JUnit `assertThrows` | Asserted; documented | Error tests | File: `assertEquals("…", e.getMessage())`, `err.Error() == "…"` | n/a | `errors.Is`, the exception type, `match=` on the varying part | D |
| R37 | A wait that fails reports what it waited for and the last state observed, never "timeout". | "Timed out after 60 seconds waiting for pod xxx to enter running state, still in pending state" is the report; "Timeout" is not. | T1 | Kubernetes e2e guide | Asserted | Async tests | File: `waitFor` with no message; a test-level timeout as the only failure | n/a | Condition and last state in the message | D |
| R38 | Partition the inputs from the signature and the specification; one test per partition, each invalid partition alone; a second value inside a partition is redundant unless it is a boundary. | Partitions are non-overlapping and non-empty and one value stands for all; two invalid values in one test mask each other. | T2 | ISTQB 4.2.1; Myers ch. 4 | Asserted standard | All | File: two cases differing only inside a partition; no invalid-partition case where the type admits one (null, empty, negative) | Partitions read off the implementation's branches; the reviewer partitions from the specification | Add or remove cases | H, D |
| R39 | Test each boundary and its neighbors: 2-value analysis at minimum, 3-value where a wrong operator is plausible. | `if (x ≤ 10)` written as `if (x = 10)` passes 10 and 11 and fails only on 9. | T2 | ISTQB 4.2.2; Reid 1997 | Asserted; studied (figures unconfirmed, §11) | All with ordered inputs | File: a range in the signature or specification with no case at min, max, min−1, max+1 | n/a | Add the boundary cases | D |
| R40 | Use a decision table when the outcome depends on a combination of conditions (one test per feasible column) and a state-transition test when behavior depends on history (every valid transition; invalid transitions one per test). | Combinations and histories are where a case list misses columns; one invalid transition per test avoids fault masking. | T2, T4 | ISTQB 4.2.3, 4.2.4 | Asserted standard | Changes to conditional or stateful logic | Diff: nested conditions with tests for the happy column only; a state machine changed with no transition test | n/a | Enumerate columns or transitions | H, D |
| R41 | A property-based test replaces enumeration for an invariant over a large domain; it carries a fixed seed or a `@reproduce_failure` blob in CI and pins each shrunk counterexample as an explicit `@example`. | T1 holds a shrunk example and a blob; without them the failure is not reproducible, and the database may be invalidated on upgrade. | T1, T2 | Hypothesis docs; Goldstein et al. | Documented; studied (30 interviews) | Property tests | File: no `@example`; CI with `print_blob` off; no seed in the report | n/a | Add `@example`; commit the blob | D, S |
| R42 | DAMP over DRY: the values an assertion depends on appear in the test body; helpers construct value objects and infrastructure, and a validation helper asserts one conceptual fact. | Tests have no tests; a reader must verify them by inspection, and a value hidden in `setUp` or a loop is a Mystery Guest. | T4 | Google ch. 12; ToT 2019; Meszaros Mystery Guest, General Fixture | Asserted | All | File: expected values in a helper, loop, or fixture; a fixture field only some tests use; a file the test reads without showing | n/a | Inline the values; narrow the fixture | D |
| R43 | A new test goes beside the nearest existing test of the unit it exercises, in the file or directory named for the code under test; a class splits when its fixture no longer serves every test. | T4 finds the examples where the code is; Django and rustc place tests by the affected module, not by author or ticket. | T4 | Django unit-tests; rustc-dev-guide; pytest contributing; Meszaros General Fixture | Asserted policy | New tests | Diff: a new test file where one exists for the unit; placement by ticket number; fixture with unused fields | n/a | Move it | D |
| R44 | Choose the lowest level at which the changed behavior is observable through a public API, and add a larger test only when the change alters what crosses a process boundary; state the choice in the PR (§5). | A small test that mocks the boundary the change altered establishes nothing about the boundary; a large test for an in-process change costs T3 minutes per run. | T4, T2 | Derived from Google test sizes, Khorikov, Spotify, Kubernetes | Derived | Every change | Diff: the PR names the level; a small test asserts on a mock of the changed boundary | "Covered by integration" claimed; the reviewer asks for the test name | §5 | H, D |

## 4. The framework table

Cells marked *measured* come from `framework_output.md`; *documented* cells cite the page. Disagreements between
documentation and measurement are listed after the table.

| Framework | Prints the operands | Prints only a boolean or the expression | Message argument | Adds or replaces | Operand order prescribed | Parameterized case name and where it appears | What the runner prints around a failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JUnit 5 (6.1.3) | `assertEquals`, `assertArrayEquals` ("contents differ at index [2]"), `assertIterableEquals`, `assertThrows` (expected and actual type); measured | `assertTrue` → `expected: <true> but was: <false>`, even with a message; measured | Last, `String` or `Supplier<String>`; measured, [documented](https://docs.junit.org/current/writing-tests/assertions.html) | Adds: `msg ==> expected: <0> but was: <-1>`; measured | `(expected, actual, message)`; documented | Default `[{index}] {argumentsWithNames}` (parameter names need `-parameters`); `@ParameterizedTest(name = "{index} ==> … {0} … {1}")`, `{arguments}`, `{argumentSetName}`, `Named`; `junit.jupiter.params.displayname.default`; shown as the invocation display name in the test tree; [documented](https://docs.junit.org/current/writing-tests/parameterized-classes-and-tests.html) | Class, method, `assertAll` → `Multiple Failures (2 failures)` with each `==>` line; message measured, framing not measured |
| AssertJ (3.27.7) | `isEqualTo` → `\nexpected: 0\n but was: -1`; `contains` lists the missing elements; measured | `assertThat(a == b).isTrue()` → `Expecting value to be true but was false`; measured | `.as("…", args)` before the assertion; measured | `as()` adds a bracketed prefix; `withFailMessage`/`overridingErrorMessage` replaces, and both must precede the assertion; measured and [documented](https://assertj.github.io/doc/) | `assertThat(actual).isEqualTo(expected)`; documented | JUnit's | JUnit's |
| Google Truth (1.4.5) | `isEqualTo` → `expected: 0\nbut was : -1`; `contains` → `expected to contain: 4\nbut was : [1, 2, 3]`; measured | `assertThat(a == b).isTrue()` → `expected to be true`; measured | `assertWithMessage("…").that(actual)`; measured | Adds a first line; measured; [documented](https://truth.dev/comparison) with a "value of" line and unified diffs for large values | `assertThat(actual)…(expected)`; documented | JUnit's | JUnit's |
| Hamcrest (3.0) | `assertThat(actual, is(expected))` → `Expected: is <0>\n but: was <-1>`; measured | `assertThat(reason, boolean)` prints the reason only; measured | First argument; measured | Adds a first line; measured | `(reason, actual, matcher)`; documented in the tutorial | JUnit's | JUnit's |
| pytest (8.4.2) | Bare `assert a == b` → `assert -1 == 0` plus `+ where -1 = ensure_bytes(-1)`; diffs for strings, sequences, dicts, sets; measured, [documented](https://docs.pytest.org/en/stable/how-to/assert.html) | `ok = …; assert ok` → `assert False`; measured | Second operand of `assert`; measured | Adds: `AssertionError: msg` above the introspection; measured | None; left and right | ids from values (`test_eval[6*9-42]`), `ids=`, `pytest.param(id=)`; part of the node id and the `FAILED` line, usable with `-k`; measured, [documented](https://docs.pytest.org/en/stable/how-to/parametrize.html) | Node id and the message's first line in the short summary; `E` lines; measured |
| Go `testing` (1.27.1), testify, go-cmp | Whatever `t.Errorf` formats: `ensureBytes(-1) = -1, want 0`; measured. testify `assert.Equal` prints `expected`/`actual` with a diff; [documented](https://pkg.go.dev/github.com/stretchr/testify/assert), not measured. `cmp.Diff(want, got)` returns `-` for x and `+` for y; [documented](https://pkg.go.dev/github.com/google/go-cmp/cmp) | `t.Fail()` prints the name and nothing; `t.Fatal("mismatch")` prints the literal; measured. testify `assert.True` prints only the message; documented | The message is the whole report; testify `msgAndArgs` last; documented | n/a; testify adds; documented | Got before want (`Foo(%q) = %d; want %d`); testify `(t, expected, actual)`; `cmp.Diff(want, got)` labeled `(-want +got)`; documented | Subtest name from `t.Run`, spaces become underscores (`negative_count_is_refused`), table case `case_3`; `--- FAIL: TestX/sub`; measured | `file:line:` before every message; measured |
| Rust (1.98.0) | `assert_eq!` → `assertion \`left == right\` failed\n left: -1\n right: 0`; measured | `assert!(expr)` → `assertion failed: ensure_bytes(-1) == 0`; measured | Format arguments after the operands; measured | `assert_eq!` adds (`failed: msg` then left and right); `assert!` replaces the expression text; measured; [documented](https://doc.rust-lang.org/std/macro.assert_eq.html) | None; the book says the order does not matter; [documented](https://doc.rust-lang.org/book/ch11-01-writing-tests.html) | No built-in; a loop or a macro; `should_panic(expected=)` prints the panic message and the expected substring; measured | `thread 'tests::name' panicked at file:line`; documented |
| Jest | `toBe`, `toEqual` → `Expected:` / `Received:` with a diff; [documented](https://jestjs.io/docs/expect); not measured | `toBeTruthy` prints the received value; documented | None on `expect`; custom matchers via `expect.extend`; documented | n/a | `expect(received).toBe(expected)`; documented | `test.each` with `%s %p %d %i %f %j %o %# %$` or `$var`, table template; the formatted string is the test title; [documented](https://jestjs.io/docs/api) | `describe › test` path, matcher message, code frame; documented |
| Vitest | Same matchers; documented | Same | `expect(actual, message)`; [documented](https://vitest.dev/api/expect.html) | Documented as "the error message will equal the provided string"; whether the diff is kept was not measured | `expect(actual)`; documented | `test.each` and `test.for` with the same placeholders and `$var`; [documented](https://vitest.dev/api/) | `expect.soft` collects every failure and reports all at the end; documented |
| `node:test` (26.8.1) | `assert.strictEqual` → `Expected values to be strictly equal:\n\n-1 !== 0`; `deepStrictEqual` → line diff; `assert.throws` names both types; measured | `assert.ok(x === y)` → `The expression evaluated to a falsy value:\n\n  assert.ok(ensureBytes(-1) === 0)`; measured | Last; measured | Replaces the generated header: `ok` with a message prints the message and `(actual: false, expected: true)`; `strictEqual` with a message prints the message and keeps `-1 !== 0`; measured | `(actual, expected)`; documented | `describe` and `it` strings joined as `parent > child`; [documented](https://nodejs.org/api/test.html) | `test at file:line:col`, the `describe`/`it` strings, then the message; measured |
| KUnit | `KUNIT_EXPECT_EQ` prints both expressions and their values; [documented](https://www.kernel.org/doc/html/next/dev-tools/kunit/tips.html) | `KUNIT_EXPECT_TRUE` prints the expression; documented | `_MSG` variants take a format string; documented | Adds; documented | `(test, left, right)`; documented | Not verified this pass | `EXPECT_*` marks failed and continues; `ASSERT_*` exits the test; documented; KTAP framing not verified |

**Documentation against measurement.** (1) AssertJ's documentation shows the single-line `[check Frodo's age]
expected:<100> but was:<33>`; 3.27.7 prints the multi-line `[ensureBytes(-2147483648)] \nexpected: 0\n but was: -1`.
Same semantics, different layout. (2) `node:assert`'s documentation says a message replaces the "default error
message"; the measurement shows `strictEqual` keeps the `-1 !== 0` line under the message while `ok` drops the
expression text. The skill should say "replaces the header" for `strictEqual` and "replaces" for `ok`. (3) The Rust
book presents the custom message on `assert!` as additional context; the measurement shows it replaces the
expression text, so the message must carry the values. (4) JUnit's documentation and the measurement agree that the
message is prefixed with `==>`; a message on `assertTrue` still reports only `true` and `false`, which is R30's
basis. (5) Jest, Vitest, and KUnit were not measured; their cells are documented only.

## 5. The level rule and its test

**Derived rule (not sourced).** A change owes its first test at the smallest size, in Google's sense (no network,
database, file system, external system, threads, sleeps, or system properties, and under sixty seconds), at which
the changed behavior is observable through a public API of the unit. A second, larger test is owed when the change
alters what crosses a process boundary: bytes on a socket, a schema, a message format, or a value read from the
deployment environment. The reviewer checks that the author chose rather than defaulted by three questions: does the
PR name the level; does the small test mock the boundary the change altered (a violation of R5 at the boundary);
does an existing larger test already exercise the path, in which case the PR names it instead of adding one.

The criteria come from four sources: Google's size table defines the levels by constraints rather than by what is
tested; Khorikov's "observable through the public API" fixes the unit; Spotify's honeycomb says the service with its
real database and its external collaborators stubbed at the boundary is the test that pays for itself; Kubernetes
says every package owes unit tests and every PR must pass integration and e2e, which is policy, not a rule per
change. The pyramid and the honeycomb are both asserted, and the size table sidesteps their disagreement (§8).

| Change | First level | Second level | What the reviewer checks |
| --- | --- | --- | --- |
| Bug fix in a private helper | Small, through the public method that reaches the helper, on the input that triggered the bug (R14, R9) | None, unless the helper's output crosses a boundary | The test does not call the helper by reflection or widened visibility; the red run on the base commit is in the PR |
| New public method | Small, one test per partition and boundary of its inputs (R38, R39), through the method itself | Medium only if the method's outcome depends on a real dependency a fake cannot reproduce (R16's three criteria) | The partition list against the specification; no mock of the method's own collaborators where a fake exists |
| Change in a protocol reader parsing bytes from a socket | Small, feeding recorded or hand-built byte sequences to the reader without a socket (the reader is a pure function of bytes) | Medium, against the real peer or its wire-level fake, because the contract crossed a process boundary; Spotify's integration test at the boundary and Google's "exercise service call contracts" | The small test's expected bytes are literals or captures, not produced by the writer under test (R3); the medium test exists or is named |
| Change in a configuration default | Small, asserting the value the code reads when nothing is set, through the public accessor | Medium or large, when the default is read at deployment (Helm values, environment) and the deployment path is what changed; Google names configuration as a gap unit tests leave | The test does not assert the constant equals itself (R8); it asserts the behavior that depends on the default |

## 6. The sensitivity list

| Shape | Names it | Detection from the diff | Repair | Oracle |
| --- | --- | --- | --- | --- |
| No assertion, or a print instead of one | Zhang & Mesbah (studied); Chen et al. 2602.07900 (studied); superpowers | No `assert`/`expect`/`verify` after the act; `print`/`console.log` of results | R2 | Mutation: every mutant on the covered lines survives |
| Assertion on a value the test supplied | superpowers | Operand is a test-local object also used in setup, no unit call between | R4 | Mutation survives |
| Expected value computed by the code under test or a duplicating helper | superpowers "mirror assertion"; Google "no logic" | Expected side calls production code or repeats its arithmetic; a loop builds both sides | R3 | Mutation survives; the reviewer derives the value from the specification |
| Mock of the unit under test | superpowers; Hora & Robbes (prevalence) | Mock target is the symbol the test or diff names; `spyOn` on the unit | R5 | Mutation: no coverage on the unit |
| Assertion on the mock | superpowers | Operand is a configured return; `toHaveBeenCalled` the only assertion; `*-mock` ids | R6 | Mutation survives |
| Passes only because no exception is thrown | superpowers warning signs | Bare call; `assertDoesNotThrow` alone | R7 | Mutation: value mutants survive, only crash mutants die |
| Change detector pinning the implementation | Google ToT 2015; ch. 13 | In-order `verify` chain mirroring the body; a constant compared with a literal | R8 | Mutation kills it, so mutation cannot tell; R20's refactoring diff can |
| Reads the same object it wrote to | superpowers | Round trip through a test-owned map or field, not the unit | R4 | Mutation survives |
| Assertion weakened until it passes | Chen et al. (sanity checks); superpowers | Equality replaced by not-null, type, contains; range widened | R12 | Mutation: value mutants survive |
| Snapshot accepted without reading | superpowers; Google ToT 2024 | Snapshot updated with the behavior, no note | R13 | None; human |
| Regression test not observed red | Django; rustc; pytest; SWT-Bench | No red run, test-first commit, or pasted output in the PR | R9 | The suite on the base commit |
| Coverage offered as proof | Inozemtseva & Holmes (studied) | "Coverage N%" as the only evidence | R11 | None; the figure is the non-signal |

**The two-run rule as the projects state it.** Django's checklist asks "Is there a proper regression test (the test
should fail before the fix is applied)?" and its style guide says a good fix "should also include a regression test to
validate the behavior that has been fixed." rustc: "We expect every PR that fixes a bug in rustc to come accompanied
by a regression test of some kind. This test should fail in `main` but pass after the PR." pytest: "If you can write
a demonstration test that currently fails but should pass (xfail), that is a very useful commit to make as well."
The evidence a PR can carry, in decreasing strength: the test in its own commit before the fix so the base commit
fails CI; the pasted failing output with the file and line; the reviewer's own run on the base commit. SWT-Bench
makes fail-to-pass the benchmark criterion and finds that such tests double the precision of fix filtering, which is
the studied basis for demanding it.

**What a mutation run on the changed lines establishes.** Stryker: *Survived* is "all tests passed while this
mutant was active … You're missing a test for it"; *No coverage* is "not covered by one of your tests and survived
as a result"; compile and runtime errors are *invalid*. cargo-mutants: *missed* means "no test failed with this
mutation applied", *unviable* "doesn't compile … inconclusive about test coverage and no action is needed", and the
guidance is to prioritize the missed mutants whose survival is surprising and to test "through appropriate public
interfaces" rather than write a test that targets the mutant. PIT: *no coverage* is "the same as Survived except
there were no tests that exercised the line"; equivalent mutants "behave in exactly the same way as the original" and
the tool cannot tell. Scoping: PIT's incremental analysis re-runs mutants whose class or killing test changed and
admits the inference is "unproven" for dependency changes; cargo-mutants `--file`; mutmut re-tests only functions
whose source changed; Google mutates only changed code in review. Petrović (ICSE 2021, 14,730,562 mutants over
662,584 changes) finds that as exposure to surfaced mutants rises, "developers tend to write more tests" and "tend to
write stronger tests in response to mutants", and that for past high-priority bugs a live mutant on the introducing
change would have been killed by the fixing test. So a survived mutant on a changed line is evidence the reviewer
can act on, and Just et al. (73% of real faults coupled, 17% not coupled to any mutant) bounds what a clean run
proves: about one real fault in six is invisible to it.

## 7. Worked examples

1. **R15, interaction verification on a query** (Google ToT 2017, its own example). Before: four `verify` calls on
   `mockUserService.isUserActive`, `getPermissions`, `isValidPermission`, and `addPermission`. After: one
   `verify(mockPermissionDb).addPermission(USER, READ_ACCESS)`, and the post adds that a fake database asserting the
   permission exists would be better still. The three removed lines were redundant, brittle, and gave "a false sense
   of security".
2. **R8, change detector** (Google ToT 2015, its own example). A `Processor` test that mocks both parts and does
   `verify_in_order` of `part1.process(w)` then `part2.process(w)` is "a transformation of the same information in
   the code under test"; it "breaks in response to any change to the production code, without verifying correct
   behavior". The post's absurd twin, a test that asserts each source line, makes the point; the repair is to test
   what `process` produces.
3. **R3, mirror assertion** (superpowers, its own example). `const expected = buildSearchQuery({tag:'urgent'});
   expect(buildSearchQuery({tag:'urgent'})).toBe(expected)` is always true; the after is
   `expect(...).toBe('tag:"urgent"')`.
4. **R19, logic in tests** (Google ch. 12, its own example). `assertThat(nav.getCurrentUrl()).isEqualTo(baseUrl +
   "/albums")` hides a double slash because `baseUrl` ends in one; writing the full literal
   `"http://photos.google.com//albums"` exposes it.
5. **R35, one behavior per test** (Google ToT 2018, its own example). `WithdrawFromAccount` deposits, withdraws 5,
   withdraws 1 and expects rejection, sets an overdraft limit, withdraws 1 again: three scenarios. After:
   `CanWithdrawWithinBalance`, `CannotOverdraw`, `CanOverdrawUpToOverdraftLimit`, each with `DepositAndSettle(Usd(5))`.
   The signal the post names: "after asserting the output of one call to the system under test, the test makes
   another call to the system under test."
6. **R18, broad assertion** (Google ToT 2024, its own example). `EXPECT_EQ(account, kExpected)` fails when a
   `CREATION_DATE` column is added; `EXPECT_EQ(account.balance, 2000)` is the test's behavior. The post keeps "at most
   one such test that checks for full equality of a complex object for the common case".
7. **R42, DAMP** (Google ToT 2019, its own example). A `setUp` list of users, a `_RegisterAllUsers` helper, and a
   loop of `assertTrue` become two `User` literals, two `Register` calls, and two assertions; the helper for value
   objects stays DRY.
8. **R17, mocking a library** (Google ToT 2020, its own example). `@Mock SalaryProcessor` with `paySalary()` stubbed
   to `SUCCESS` keeps passing after the library starts returning `SCHEDULED`; the after uses `FakeSalaryProcessor`
   or a `MySalaryProcessor` wrapper mocked in its place.

Sources without examples of their own: Khorikov's post (prose only), Beck (one line per property), ISTQB (one BVA
example only), the mutation-tool pages (definitions), the papers (figures, not tests; Panichella's figures 8 to 10
are screenshots of real tests and are the exception).

## 8. Conflicts and how they were decided

1. **One assertion per test against one behavior per test.** The baseline says one assertion per method; Google
   (ch. 12: "the vast majority of unit tests require only one 'when' and one 'then' block"), superpowers, and ToT
   2018 say one behavior; `assertAll`, `expect.soft`, `t.Error`, and `EXPECT_*` exist to put several assertions on
   one behavior and report them together. Surviving rule: R35 with R34. The reviewer's test for "several assertions
   on one behavior" versus "several behaviors" is ToT 2018's: after an assertion, is there another call on the unit?
   Several assertions on the fields of one result are one behavior; an act after an assert is a second. Panichella's
   "semantic coherence" (assertions relating to one scenario, however many) is the studied form of the same test, and
   it found the assertion-count criterion (Eager Test) a poor discriminator. T1 won; T4's convenience of a long test
   loses nothing it needed.
2. **Mocks, fakes, and real dependencies.** Google prefers real, then fake, then stub, then interaction testing, with
   three criteria for leaving the real thing; Khorikov mocks unmanaged out-of-process dependencies and never
   intra-system communication; superpowers says no mocks unless unavoidable; Hora & Robbes find agents mock more.
   These agree once "mock" is split into "double" and "interaction verification": R16 is the preference order with
   Google's criteria for each step and Khorikov's criterion for the last, and R5, R6, R15 are the shapes rejected
   outright. T3 won. The loser is the writer's speed, which superpowers accepts and the over-mocking study measures.
3. **Pyramid against honeycomb.** Both asserted; Spotify argues from microservices, where the unit is small and the
   interaction is the complexity. Google's size table replaces the count argument with constraints, and R44 uses it:
   levels are what a test may touch, and the change decides which level can observe it. Neither reader loses; the
   honeycomb's case (a service whose behavior is its boundary) is the second row of §5's table.
4. **Test smells.** Bavota (86% of JUnit classes smelly; comprehension 30% better without smells, per Pass 1's read of
   the abstract) and Spadini (Indirect Testing, Eager Test, Assertion Roulette most tied to change-proneness; the
   first two to defect-proneness) against Panichella (Eager Test in 80% of developer suites and coherent in all but
   4 of 39; Assertion Roulette in 30 of 49 suites but moot where JUnit 4 or later names the failing assert; Mystery
   Guest 0%; Indirect Testing 20% and "a concern that developers do seek to avoid"; the older detector misclassifies
   over 70% on generated tests). Decision: keep Indirect Testing (R21, R14), Conditional Test Logic (R19), Mystery
   Guest and General Fixture (R42, R43), Interacting Tests (R24), and Test Logic in Production (R22) as names for
   shapes the diff shows; drop Eager Test and Assertion Roulette as rules, and keep their content only as R35 (the
   act-after-assert signal) and R31 (a message where the framework prints nothing). T2 won; nothing Spadini measured
   is lost, because its two harmful smells survive under other names.
5. **Narrow assertions against compare full structures.** Google ToT 2024 says assert the relevant field; the Go wiki
   says construct the expected struct and compare in one shot with a diff. Reconciled in R18 by what the value is: a
   value the function returns is the behavior and is compared whole with `cmp.Diff`; an entity with fields the
   behavior does not define is asserted on the fields it does. T3 won on entities, T1 on returned values (a diff is
   the better report). The loser is neither; the two posts describe different objects.
6. **Got before want against expected before actual.** Not a conflict in substance; R32 states it per framework, and
   the framework table carries the order. The Go wiki's "some test frameworks encourage writing these backwards" is
   about labels, and the rule is that the labels be right.
7. **Issue numbers in test names.** rustc says to include the issue number in the file's first comment; Django says to
   reserve ticket references for obscure issues and put them at the end of a docstring sentence. Neither puts it in
   the name; R29 follows both, and the comment is the doc-comment skill's territory.
8. **`assertTrue` and effectiveness.** Zhang & Mesbah's Finding 8 ranks `assertTrue/False` assertions as the most
   effective method type at killing mutants, ahead of `assertEquals` and `assertNull`. The baseline's "avoid
   assertTrue" is a T1 rule about the report, not a sensitivity rule; R30 states it as "use the assertion that prints
   the operands", which a boolean assertion on a boolean result satisfies. T1 won; the sensitivity of the assertion is
   unchanged by the choice of method as long as the comparison is the same.

## 9. The detectability matrix

| Bucket | Rules, with the source that supplies the detection |
| --- | --- |
| Agent from the diff | R1 (superpowers gate), R2 (Zhang; Chen), R3 (superpowers), R4 (superpowers), R5 (superpowers; Hora & Robbes), R6 (superpowers), R7 (superpowers), R8 (Google ToT 2015), R12 (Chen; superpowers), R13 (Google ToT 2024), R14 (Google ch. 12), R15 (Google ToT 2017), R16 (Google ch. 13; Khorikov), R17 (Google ToT 2020), R18 (Google ToT 2024; Go wiki), R19 (Google ch. 12; Meszaros), R20 (Google ch. 12), R21 (superpowers), R22 (Meszaros; superpowers), R23 (Luo), R24 (Luo; Parry), R25 (Luo; Parry; PostgreSQL), R28 (Google; Go wiki), R29 (Google ToT 2014; Wu & Clause), R30 (framework_output; framework docs), R31 (Go wiki; framework docs), R32 (framework docs), R33 (framework docs), R34 (Go wiki; KUnit; JUnit; Vitest), R35 (Google ToT 2018), R36 (Go wiki; framework docs), R37 (Kubernetes), R39 (ISTQB), R42 (Google; Meszaros), R43 (Django; rustc) |
| Suite run | R9 (Django; rustc; pytest: the base-commit run), R26 (pytest-randomly; JUnit Random: the seeded random-order run), R33 uniqueness (the runner's node ids), R41 (Hypothesis: the reproducer), and R24 confirmed by R26 |
| Mutation or smell tool | R10 (Stryker; PIT; cargo-mutants; Petrović; Just), R11 (Inozemtseva: what coverage does not establish), R26's classifier (iDFlakies), and R1, R8, R12 confirmed by a survived mutant (Stryker; cargo-mutants) |
| Human | R16's criterion (Google ch. 13's three reasons; Khorikov's managed/unmanaged), R27 (Luo's 24% and 94%), R38 and R40 (ISTQB: partitions and columns come from the specification), R44 (§5), R13's acceptance of a snapshot, and R10's equivalence verdict (PIT) |

## 10. Baseline audit

**Part 1, the failing test as a bug report.** Survives as stated in its division into four parts: it is R28, and the
Go wiki, Google ch. 12, and ToT 2014 state the same division with the same rationale. Three restatements. "One
assertion per method keeps the name able to do this" becomes one behavior per method with several assertions
reported together (R35, R34; conflict 1). "`assertTrue(expected == actual, message)` renders neither" is confirmed
by measurement (`expected: <true> but was: <false>`), but the rule is about the operands, not the method: R30. "In a
parameterized test [the message] is which invocation ran" is superseded by the frameworks' case naming (R33): the
case id is a slot of its own, and the message is free for the input when the id cannot carry it. `fail()` with no
message is confirmed by measurement in JUnit (empty), pytest (`Failed`), Go (`t.Fail()` prints nothing), and
`node:assert` (`Failed`). Unsupported: "a message read while someone scans a stack trace competes with the lines
around it" is plausible and consistent with Takebayashi's finding that messages are rarely supplied, but no study
measures it; keep it asserted.

**Part 2, the four rules.** (1) "Avoid `assertTrue` and `assertFalse` unless the method returns a boolean" is
restated as R30 and loses its second half: a boolean assertion on a boolean result prints what there is to print, and
Zhang's Finding 8 removes any suggestion that the choice weakens the test. (2) "Give every assertion a message"
becomes R31 with the Go wiki's content (function and input) and its negative (not what the assertion or the name
prints); the measurement shows where the message goes per framework and that a message on `assertTrue` does not
rescue it. Takebayashi's study supports the observation that messages are rare but not the rule that every assertion
needs one; where the assertion prints the operands and the name carries the scenario, the message is empty by R28.
(3) "Choose the level deliberately" is restated as R44 with a criterion (observable through a public API at the
smallest size) and a second-level trigger (a process boundary); the baseline's "consider adding an integration test"
had neither, and Pass 1 was right that no source supplies one, so R44 is labeled derived. (4) The checklist survives
with definitions: boundaries become 2-value and 3-value analysis (R39); "no class is tested twice" becomes ISTQB's
one-per-partition with the exception for boundaries and the requirement that each invalid partition is tested alone
(R38); "the tests are able to fail when the main code is reverted" is the two-run rule (R9) plus the mutation verdict
(R10), which is the checklist's only mechanical form.

**Missing from the baseline entirely.** Everything a writer optimizing for green does (R1 to R8, R12, R13); the
robustness rules (R14 to R22), so a green suite after a refactoring is not addressed; determinism (R23 to R27); the
decision table and state transition techniques (R40); property tests (R41); organization and placement (R42, R43);
the tool verdicts and what they do not establish (R10, R11); and the per-framework mapping of the four parts (§4),
without which Part 1 is Java-shaped.

## 11. Evidence map

**Measured evidence (studied).** Inozemtseva & Holmes, ICSE 2014: 31,000 suites, five Java systems, statement,
decision, and modified-condition coverage against mutation score; Kendall τ between coverage and effectiveness drops
when suite size is controlled, to "essentially zero" for some systems and to 0.46 to 0.85 for others, "low to
moderate" overall; "using a fixed coverage value as a quality target is unlikely to produce an effective test suite."
Confirmed. Just et al., FSE 2014: 357 real faults, five programs, 230,000 mutants; 73% of real faults coupled to
mutants from common operators, 27% not, of which 10% need a new or stronger operator and 17% are "not coupled to any
mutants"; mutation score correlates with real-fault detection more strongly than statement coverage. Confirmed.
Zhang & Mesbah, FSE 2015: 6,700 suites, 24,000 assertions, five projects; a "very strong correlation" between
assertion count and effectiveness with suite size controlled; Kendall 0.88 to 0.91 between assertion coverage and
mutation score; Finding 8 ranks assertion method types by effectiveness as `assert(Not)Null` < `assert(Not)Equals` <
`assertTrue/False`. Confirmed, with Finding 8 added. Petrović et al., ICSE 2021: 14,730,562 mutants, 662,584
changes, 446,604 files; developers exposed to mutants write more tests (RQ1) and stronger tests (RQ2); reported
mutants are coupled with real high-priority faults (RQ3). TSE 2021: more than 24,000 developers, more than 1,000
projects. Confirmed. Luo et al., FSE 2014: 201 commits, 51 projects; 161 classified: Async Wait 74, Concurrency 32,
Test Order Dependency 19, Resource Leak 11, Network 10, Time 5, IO 4, Randomness 4, Floating Point 3, Unordered
Collections 1; 78% flaky when first written; 24% of fixes modify the code under test and 94% of those fix a bug;
waitFor in 54% of async fixes; cleaning shared state in 74% of order fixes. Confirmed. Parry et al., TOSEM 2021: 76
papers; order-dependent tests up to 16% of flaky bug reports (Vahabzadeh et al. 2015) and 9% of repairs; Eck et al.
2019 (21 Mozilla developers, 200 fixed flaky tests): concurrency 26%, async wait 22%, too restrictive range 17%, order
dependency 9%; static fields facilitate 61% of order dependencies. Confirmed with attributions. Panichella et al.,
EMSE 2022: 49 developer-written suites annotated; Eager Test in 39 (80%), of which all but 4 semantically coherent, so
eagerness predicts incoherence in about 10% of cases; Assertion Roulette in 30 of 49 (Table 6 reports 82% by a
different count), 20 of them under JUnit 4 where the runtime names the failing assert; Indirect Testing 10 (20%);
Mystery Guest 0; Sensitive Equality and Resource Optimism 10% each. **Corrected scope:** the "over 70%"
misclassification is the older detector (Grano et al.) on generated tests; tsDetect reached precision 1.00 and recall
0.80 on Assertion Roulette in developer tests but recall 0.39 on Eager Test. Hora & Robbes, MSR 2026 (2602.00409):
1.2 million commits, 2,168 repositories, 48,563 agent commits; **corrected denominator:** 36% is of the 11,035
agent test-modifying commits (3,934 add mocks) against 26% of non-agent test commits (40,966); the abstract's "36% of
commits made by coding agents" is the looser phrasing. Chen et al. (2602.07900): six models on SWE-bench Verified;
Claude Opus 4.5 writes a test artifact in about 83% of tasks at 74.4% resolution, GPT-5.2 in 0.6% at 71.8%;
value-revealing prints outnumber assertions; exact-output assertions are 41% to 43% and property checks 34% to 41%
of agent assertions for four models. Ahmed et al. (2511.16858): overfitting 21.8% (50 of 229, Claude 3.7 Sonnet) and
33.0% (GPT-4o); 25.5% after test-based refinement. Mündler et al., SWT-Bench: generated fail-to-pass tests double
SWE-Agent's fix precision. Ma et al. (2606.28430): claude-opus-4.7 and gpt-5.5, 222 hidden Playwright tests, 18
runs; visible oracle yields near-perfect scores with the library "dead or absent". Siddiq et al. (2305.00418): three
models, not four; correct tests 52.3% to 81.3% on HumanEval and 6.9% to 51.9% on SF110; Assertion Roulette in 23.8%
to 61.3% of generated tests; **the 62.4% figure is not in this paper** and belongs to DeCon (2501.02901), as Pass 1's
verification already moved it. Yuan et al. (2305.04207): 57.9% of ChatGPT tests fail to compile, 17.3% compile and
fail "mostly" on incorrect assertions, 24.8% pass. Ouedraogo et al.: 20,505 LLM suites against 779,585 human tests;
Assertion Roulette and Magic Number most common. Takebayashi et al. (2303.00169, not "Taha"): 20 Java systems;
messages rarely supplied. Wu & Clause: 95% true-positive rate on 34,352 tests. Goldstein et al.: 30 interviews.

**Unreachable or unconfirmed.** Reid 1997: the IEEE page returned no body and the CiteSeerX copy no file; the indexed
abstract says BVA was most effective and "neither EP nor random testing half as effective", which is consistent with
0.79 against 0.33 but does not confirm the figures or the 20 KLOC Ada scope; R39 rests on ISTQB, with Reid cited as
the one experiment and its numbers flagged. Bavota et al. 2015: the Springer abstract was elided today; Pass 1's
verification read "86 % of JUnit tests exhibiting at least one test smell" and "comprehension is 30 % better" through
the cookie redirect, and secondary sources repeat the 30%; carried as confirmed by that read, not by this pass.

**Stated policy (asserted by an organization).** Google chapters 12 and 13 and the nine posts; the Go wiki; Kubernetes
(unit tests for all packages; timeout messages; zero-flake, no automatic job retries); Django, rustc, pytest on the
regression test and placement; ISTQB 4.2; the size table.

**Inference from mechanics (derived).** R44; the got/want reconciliation in R32; the snapshot rule R13's first half;
the level of the four §5 cases; the "message replaces the header" reading of `node:assert`.

**Assertion (a practitioner without measurement).** superpowers (R1, R3 to R7, R21, R22); Khorikov (R16's last
step); Beck; Meszaros's names.

## 12. What the skill-writing session should be told

Do not write wording rules; `english-developer-style` owns the phrasing of a name, a message, and a sentence, and
this report supplies only what each carries. Do not re-derive doc-comment rules; the comment above a test, the issue
number in it, and the docstring belong to the language's doc-comment skill, and R29 says only that the number is not
the name. Do not promote an asserted row to studied: the rules with a studied basis are R2, R5 (prevalence only),
R9 (criterion), R10, R11, R12 (categories), R23 to R27, R29 (the detector), R30 (the caveat), R31 (the rarity), R35
(the coherence refinement), R39 (unconfirmed figures), R41 (interviews); every failure-report rule stays asserted
with measured output behind it, and the skill must not claim a diagnosis-time result that no study has produced. Do
not present a framework convention as a universal rule: the operand order, the message position, whether a message
adds or replaces, and the case-naming syntax are per-framework cells of §4, and the universal rules are R28 and R30
to R34 stated over them. Keep research provenance out of the skill body: no paper names, sample sizes, or
percentages in the text an agent applies; the skill's rules table carries the rule, the reader, the detection, the
gaming check, and the repair, and the evidence stays here.

Load-bearing rules, in the order a compression pass keeps them: R1 with R3, R5, R6, R12 (the gaming shapes and their
gate); R9 and R10 (the two oracles); R15 and R16 (the double rules); R28 to R31 and R33 (the report); R35; R38 and
R39; R44 with its four cases; R23 to R25 as one checklist. Dropped first under compression: R13, R17 (a corollary of
R16), R20 (a corollary of R8), R21, R22, R36, R37, R40, R41, R43, and the per-framework detail beyond the row for the
repository's own framework. The four buckets must survive any compression, because they are what tells the agent
which rules it can decide from the diff, which need a run it has to make, which need a tool verdict it has to read
as the tool defines it, and which it may only raise as a question.
