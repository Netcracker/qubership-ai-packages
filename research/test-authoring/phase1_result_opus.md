# Pass 1: sources for a skill that writes and reviews tests

## 1. Executive summary

**No single source covers the domain.** The closest is *Software Engineering at Google*, chapters 11 to 14: it is the
only source that runs from level selection (test size and test scope) through what a test asserts, through failure
messages, and states a rationale for each rule. It stops short of test-input design (equivalence classes, boundaries),
says nothing about which assertion prints which values in a given framework, and its determinism guidance is a
restriction list rather than a taxonomy of causes. Synthesis is required, and the seams are clean: Google supplies
level and robustness, ISO 29119-4 and the ISTQB technique chapters supply inputs, mutation-testing sources supply
sensitivity, framework documentation supplies the failure report, and the flaky-test literature supplies determinism.

**Strongest category: framework documentation, closely followed by empirical research.** Framework docs are precise,
maintained, and checkable, and the Go wiki's `TestComments` is the single best example of a project stating both the
rule and the failure text it produces. Empirical research is strong for the four questions it has actually studied
(coverage, mutants, flakiness, test smells) and silent on the rest. **Weakest and most polluted: agent skills and rule
files**, and after them the practitioner blog layer around the test pyramid, which is almost entirely assertion.

**There is no agent skill for test content.** `obra/superpowers-skills/skills/testing` holds three skills, and all
three are process or execution: test-driven development, condition-based waiting, testing anti-patterns. Nothing in
the surveyed material governs which level a change owes a test at, which assertion prints the operands, or how a
failure reads. Cursor's own advice moves the other way and creates the gaming problem this skill has to solve: it
tells the agent to iterate until the tests pass and not to modify the tests, which is a rule for the human, not for
the agent that wrote both sides. The category is thin, and no source in it addresses a writer that optimizes for
green.

**The reader table holds, with one correction.** T1 to T4 are each served by a distinct source set. T5 is real but
narrow: Go serves it structurally through `Example` functions, which compile, run as tests, and render in the package
documentation, and *Software Engineering at Google* claims tests act as documentation. Outside that, T5 collapses into
T4 and should be folded in unless Pass 2 finds a rule that only T5 generates. One reader is missing: **T6, the writer
of the test, who is also the author of the change under test.** Nothing in the reader table represents the party whose
incentive is a green suite, and that party is the consumer of this skill.

**Answerable from existing sources:** 3 (sensitivity), 4 (robustness), 5 (the failure report), 6 (determinism),
8 (framework specifics). **Under-served:** 1 (level), where the pyramid, the trophy, and the honeycomb are all
assertion, and the only studied artifact is Google's own size taxonomy adopted at scale; 2 (inputs), where the
techniques are standardized but the evidence for their fault-finding is old and thin, with combinatorial testing the
exception; 7 (organization), which is convention, not evidence; 9 (agent-authored tests), where the empirical work is
new and good but the skill layer is empty; 10 (review), where rubrics exist as smell catalogs but their validity is
contested by the 2022 replication.

**Pass 2 should concentrate on framework documentation and mechanical oracles**, because those convert directly into
rules an agent applies alone and a reviewer checks from the diff, with practitioner guidance (Google) second for the
level and robustness rules, and research third, as the source of the calibration that says which rule is studied.

## 2. Candidate inventory

| # | Name | URL | Category | Author / org | Questions | Readers | Best use | Evidence | Maint. | Why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SWE at Google ch.11, Testing Overview | https://abseil.io/resources/swe-book/html/ch11.html | practitioner | Winters, Manshreck, Wright (Google) | 1, 4, 6, 7 | T2, T3, T4 | authoring | strong; size taxonomy adopted at scale, 80/15/5 ratio asserted | active | Only source that defines size and scope as two axes, with mechanical restrictions per size |
| 2 | SWE at Google ch.12, Unit Testing | https://abseil.io/resources/swe-book/html/ch12.html | practitioner | Google | 3, 4, 5, 7 | T1, T2, T3, T5 | authoring, reviewing | strong; asserted, with rationale and examples | active | "Unchanging tests", public-API testing, state over interactions, complete and concise, DAMP, one behavior per test |
| 3 | SWE at Google ch.13-14, Test Doubles and Larger Testing | https://abseil.io/resources/swe-book/html/ch14.html | practitioner | Google | 1, 4 | T2, T3 | authoring | medium; asserted | active | When a double is warranted, which kind, and what a larger test buys |
| 4 | TotT: Change-Detector Tests Considered Harmful | https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html | practitioner | Google | 3, 4 | T2, T3 | reviewing | medium; asserted, with before/after | stale (2015), still cited | Names a test shape detectable from the diff alone |
| 5 | TotT: Tests Too DRY? Make Them DAMP!, and Don't Put Logic in Tests | https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html | practitioner | Snyder, Kuefler (Google) | 3, 5, 7 | T1, T2, T4 | authoring, reviewing | medium; asserted | stale, canonical | DAMP over DRY with its rationale (tests have no tests); conditional logic named as a defect |
| 6 | TotT: Don't Mock Types You Don't Own, Don't Overuse Mocks | https://testing.googleblog.com/2020/07/testing-on-toilet-dont-mock-types-you.html | practitioner | Google | 3, 4 | T2, T3 | reviewing | medium; asserted, with thresholds | stale | Gives a countable threshold: more than one or two mocks is a smell |
| 7 | xUnit Test Patterns and its smell catalog | http://xunitpatterns.com/ | practitioner | Meszaros | 3, 5, 7, 10 | T1, T2, T4 | reviewing | strong as a taxonomy; asserted | stale (2007), universally cited | 18 test smells and 68 patterns; the vocabulary every later source uses |
| 8 | Kent Beck, Test Desiderata | https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3 | practitioner | Beck | 1, 3, 4, 5, 6 | T1, T3 | authoring | medium; asserted, framed as trade-offs | stale (2019) | 12 named properties including behavioral, structure-insensitive, specific: the cleanest compact rule set |
| 9 | Khorikov, four pillars of a good unit test | https://enterprisecraftsmanship.com/files/Unit-Testing-Chapter-1-Excerpt.pdf | practitioner | Khorikov | 1, 3, 4 | T2, T3 | authoring | medium; asserted | stale (2020) | Separates protection against regressions from resistance to refactoring: two of the skill's axes, named |
| 10 | Fowler, Mocks Aren't Stubs | https://martinfowler.com/articles/mocksArentStubs.html | practitioner | Fowler | 4 | T2, T3 | background | medium; asserted | stale (2007) | The state-verification vs behavior-verification distinction, and the classical/mockist split |
| 11 | Dodds, The Testing Trophy | https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications | practitioner | Dodds | 1 | T4 | background | weak; asserted | active | The main published contradiction of the pyramid; useful as the conflict, not as a rule |
| 12 | ISO/IEC/IEEE 29119-4:2021, Test techniques | https://www.iso.org/standard/79430.html | standard | ISO/IEC/IEEE | 2 | T2, T4 | authoring | strong as a definition; effectiveness asserted | active (2021) | The normative definition of equivalence partitioning, BVA, decision tables, state transition, classification tree |
| 13 | NIST, interactions involved in software failures (Kuhn et al.) | https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/interactions-involved-in-software-failures | research | NIST | 2 | T2, T4 | authoring | strong; studied across several fault datasets | active | Most failures involve one or two parameters; pairwise is not sufficient, 4-way to 6-way approaches exhaustive |
| 14 | JUnit 5 User Guide | https://docs.junit.org/5.13.2/user-guide/index.html | framework doc | JUnit team | 5, 8 | T1 | authoring, mechanical | strong; normative | active | `assertThrows` return value, `assertAll` heading, `@ParameterizedTest(name = ...)` placeholders |
| 15 | AssertJ documentation and Google Truth FAQ | https://assertj.github.io/doc/ | framework doc | AssertJ, Google | 5, 8 | T1 | authoring | strong; normative, rationale asserted | active | `as()` is ignored unless it precedes the assertion; `overridingErrorMessage` replaces the operands; Truth's "value of" rationale |
| 16 | pytest: assertion introspection, parametrize ids, good practices | https://docs.pytest.org/en/stable/how-to/assert.html | framework doc | pytest | 5, 7, 8 | T1, T4 | authoring, mechanical | strong; normative | active | Rewriting reaches only collected test modules, so a helper module's asserts print nothing |
| 17 | Go wiki: Test Comments and Test Failures | https://go.dev/wiki/TestComments | project guide | Go team | 3, 5, 7, 8, 10 | T1, T2, T4 | authoring, reviewing | strong; normative for a large project | active | `YourFunc(%v) = %v, want %v`; got before want; avoid assertion libraries; `t.Error` over `t.Fatal`; name subtests |
| 18 | Rust `std::assert_eq!` and the book's testing chapter | https://doc.rust-lang.org/std/macro.assert_eq.html | framework doc | Rust project | 5, 8 | T1 | authoring | strong; normative | active | Prints `left`/`right` with Debug; the custom message is appended, not substituted |
| 19 | Jest `expect`, Vitest `expect`, `node:assert` | https://jestjs.io/docs/expect | framework doc | Meta, Vitest, Node | 5, 8 | T1 | authoring | strong; normative | active | Diff output, `toBe` vs `toEqual` failure text, `assert.deepStrictEqual` actual/expected diff |
| 20 | PIT basic concepts and the cargo-mutants book | https://pitest.org/quickstart/basic_concepts/ | oracle tool | Coles, Pool | 3, 10 | T2 | mechanical | strong; normative for the tools | active | Both state the readings of a surviving or missed mutant, including the equivalent-mutant case |
| 21 | Inozemtseva & Holmes ICSE 2014, with Zhang & Mesbah FSE 2015 | https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf | research | Waterloo, UBC | 3, 5 | T2 | background | strong; studied: 31,000 suites, 5 systems to 724 kLOC | stale, canonical | Coverage should not be a quality target once suite size is controlled; assertion count and coverage do correlate |
| 22 | Just et al., FSE 2014, mutants vs real faults | https://homes.cs.washington.edu/~rjust/publ/mutants_real_faults_fse_2014.pdf | research | UW, Waterloo, Sheffield | 3 | T2 | background | strong; studied: 357 real faults, 230,000 mutants, 321 kLOC | stale, canonical | 73% of real faults coupled to mutants; 17% coupled to none; mutation score beats statement coverage as a predictor |
| 23 | Luo et al. FSE 2014, with Parry et al. TOSEM 2022 survey | https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf | research | Illinois, Sheffield, CMU | 6 | T1, T3 | background, reviewing | strong; studied: 201 commits, 51 projects; survey of 76 papers | active | Async wait ~45%, concurrency ~20%, order dependency ~12%: the proportions the skill needs |
| 24 | Test-smell research: Panichella 2022, Spadini 2018, tsDetect mapping | https://link.springer.com/article/10.1007/s10664-022-10207-5 | research | ZHAW, TU Delft, others | 5, 10 | T2 | background | strong; contested conclusions on detector validity | active | Smells link to change- and defect-proneness, but detectors are over-strict and often rejected by developers |
| 25 | Delplanque et al., Rotten Green Tests, ICSE 2019 | https://inria.hal.science/hal-02002346v2 | research | Inria, PSU | 3, 10 | T2 | mechanical | strong; studied: 19,905 tests, 294 rotten found | stale | A green test whose assertions never execute; detected by static plus dynamic analysis |
| 26 | Takebayashi et al., assertion messages, 2023 | https://arxiv.org/abs/2303.00169 | research | Hawai'i, RIT | 5 | T1 | background | medium; studied: 20 Java systems | active | Only ~4.5% of assertion calls carry a message, 81% of those are bare string literals, readability is poor |
| 27 | Petrovic & Ivankovic, mutation testing at Google, 2018 and 2021 | https://arxiv.org/abs/2102.11378 | research | Google | 3, 10 | T2 | mechanical | strong; studied: 16.9M mutants, 776,740 changelists | active | Diff-based mutation with arid-node suppression; productive-mutant rate raised from 15% to ~89% |
| 28 | LLM test quality: TestPilot (TSE 2023) and ChatTester (2023) | https://arxiv.org/abs/2302.06527 | research | GitHub, NYU, Fudan | 9 | T2 | background | strong; studied: 25 npm packages, 1,684 functions | active | Median 61.4% of generated tests carried a non-trivial assertion; failures dominated by incorrect assertions |
| 29 | Konstantinou et al., actual vs expected oracles, 2024 | https://arxiv.org/abs/2410.21136 | research | Luxembourg | 3, 9 | T2 | background | strong; studied: 24 Java repositories | active | LLMs write oracles that capture the implementation rather than the intent: the gaming failure, measured |
| 30 | Project guides: Kubernetes sig-testing, KUnit style, PostgreSQL regress | https://github.com/kubernetes/community/blob/master/contributors/devel/sig-testing/testing.md | project guide | Kubernetes, Linux, PostgreSQL | 1, 5, 6, 7, 10 | T1, T2, T4 | authoring, reviewing | medium; normative, adopted at scale | active | State what a change owes, prescribe Arrange-Act-Assert and naming, and show an expected-output oracle model |
| 31 | Agent skills and rule files: obra/superpowers testing, Cursor guidance | https://github.com/obra/superpowers-skills/tree/main/skills/testing | agent skill | community, Cursor | 9 | T4 | background | weak; asserted, no evaluation published | active | The nearest existing agent material; confirms the content gap, and states the gaming problem as advice |

## 3. Promising shortlist for Pass 2

**1. *Software Engineering at Google*, chapters 11 and 12 (#1, #2).** The backbone. Chapter 11 gives the only level
taxonomy with mechanical restrictions rather than a shape metaphor: a small test runs in one process and one thread and
may not touch network, disk, sleep, or block, so an agent can classify a test it is looking at. Chapter 12 gives
"unchanging tests", public-API testing, state over interactions, one behavior per test, and complete-and-concise, each
with a rationale. Serves T2 and T3 primarily. Converts to compact rules directly; the 80/15/5 ratio does not, and
should be dropped rather than restated.

**2. Go wiki, `TestComments` (#17).** The best single model of what this skill is trying to be: a project's own rules,
each stated with the failure text it produces. It supplies the T1 rules in a checkable form, including the message
format `YourFunc(%v) = %v, want %v`, got before want, identify the function, compare whole structures rather than
field by field, and `t.Error` over `t.Fatal` so one run reports every failure. It also contradicts the baseline: Go
tells authors to avoid assertion libraries entirely and write the comparison and the message by hand.

**3. Just et al., FSE 2014 (#22) with Inozemtseva & Holmes, ICSE 2014 (#21).** Together these settle question 3's
calibration. Coverage is not a quality target; mutation score is a better predictor of real fault detection, and it
holds when coverage is controlled. The limits matter as much: 73% of real faults were coupled to mutants, 17% were
coupled to none. Serves T2. Converts to one rule about what a reviewer may conclude from a coverage number, and one
about what a surviving mutant means.

**4. Petrović & Ivanković, mutation testing at Google (#27).** The only source that makes mutation testing affordable
in a review loop: mutate the diff, suppress arid nodes, surface at most one mutant per line, median seven per change.
That is exactly the shape an agent reviewing its own change can adopt. Serves T2 and the missing T6. Strong evidence,
industrial scale.

**5. Konstantinou et al., 2024 (#29) with TestPilot and ChatTester (#28).** The measured version of the
gaming problem. LLM-written oracles capture the implementation rather than the intent; a median 61.4% of generated
tests carried a non-trivial assertion, so roughly two in five did not; failures concentrate in wrong assertions. This
converts into named, diff-detectable defect shapes and is the evidence that the skill's anti-gaming rules are needed
rather than fastidious.

**6. Luo et al., FSE 2014, with the Parry et al. survey (#23).** Question 6, answered with proportions: async wait ~45%,
concurrency ~20%, order dependency ~12%, roughly 77% of fixes in three causes. That lets the skill rank its
determinism rules by expected value instead of listing everything. Serves T1 and T3. Pair with the order-randomizing
runners (`go test -shuffle`, `pytest-randomly`, NonDex, iDFlakies) as the oracle for the third cause.

**7. Framework documentation set: JUnit 5, AssertJ, Truth, pytest, Rust, Jest/Vitest/`node:test` (#14-#16, #18, #19).**
Question 8 is answerable only here, and the answers are non-obvious: AssertJ's `as()` is silently ignored if it comes
after the assertion; pytest rewrites asserts only in collected test modules, so a helper's assert prints nothing;
Rust appends the custom message and still prints `left` and `right`; JUnit's `assertThrows` returns the exception.
Serves T1. Converts into a per-framework table, which is the most mechanically checkable artifact in the whole set.

**8. Meszaros's smell catalog (#7), read against the test-smell research (#24).** The catalog supplies the review
vocabulary (assertion roulette, eager test, mystery guest, conditional test logic, sensitive equality). The replication
supplies the correction: detectors are over-strict and developers do not accept many of their warnings, so the skill
should carry a small subset of smells with a stated detection rule rather than the whole catalog. Serves T2.

**9. Delplanque et al., Rotten Green Tests (#25).** A precise, mechanically detectable member of the "cannot fail"
family: a green test whose assertions never execute, found in 294 of 19,905 tests, some dormant for five years. It
gives the skill a concrete oracle for one of the shapes the brief names, and it shows what needs a run rather than a
read.

**10. ISO 29119-4 (#12) with the NIST combinatorial results (#13).** Question 2's normative half and its studied half.
29119-4 defines the techniques; NIST supplies the only strong evidence about how many inputs are enough, namely that
most failures involve one or two parameters and that pairwise alone is insufficient. Serves T2 and T4. The standard is
paywalled, which is a practical problem for citation; the ISTQB syllabus is the open substitute for the definitions.

**11. Takebayashi et al., assertion messages (#26).** Small but directly load-bearing, because it contradicts the
baseline: only about 4.5% of assertion calls in 20 Java systems carry a message, and 81% of those messages are bare
string literals with poor readability. Either the baseline's "give every assertion a message" is a deliberate
departure from practice that needs its own defense, or the rule should be narrowed to the cases where the assertion
cannot print what the reader needs.

**12. Kubernetes sig-testing and KUnit style (#30).** Two projects that state what a change owes in tests and how
a test is named and shaped, at a scale where the rules were forced to become mechanical. KUnit prescribes
Arrange-Act-Assert and naming that tooling depends on; Kubernetes states that all packages and significant files
require unit tests and prefers table-driven tests. Serves T4. Useful mainly as evidence that a level rule can be
written at all.

## 4. Obvious rejects

- **The test pyramid, trophy, honeycomb, and their blog debate (#11 and relatives).** Shape metaphors with no measured
  claim about cost or confidence. Keep only as the recorded conflict for question 1.
- **TDD advocacy generally, including the superpowers TDD skill (#31).** Process, not artifact. The one usable
  fragment is the guarantee that the test was observed red before the change, which the skill can require directly.
- **Assertion-library comparisons and migration guides.** Explicitly out of scope, and the docs of each library
  already state its own failure output.
- **`awesome-cursorrules`-style rule lists and the skills-marketplace aggregators.** Anonymous, unevaluated, and
  mostly restating "write tests". No editorial authority.
- **Test-smell detection tools as a shipping dependency.** The 2022 replication (#24) undercuts them; the underlying
  smell definitions are worth more than the tools.
- **Coverage tools' own documentation.** Useful only for the negative claim, which #21 already states better and with
  evidence.
- **Generic "10 unit testing best practices" articles.** Rule with no rationale, no source, no examples.
- **Test management and case-tracking products, and ISTQB material outside the technique chapters.** Out of scope by
  the brief.
- **The `RAIDE` refactoring-tool experiment.** Measures a tool's usability, not the harm of the smell it refactors.

## 5. Gaps and questions for Pass 2

**Detectability tiers are unresolved.** A first cut: detectable from the diff alone are no assertion, assertion on a
value the test supplied, mocking the unit under test, conditional logic in the test, `assertTrue` where a value
assertion exists, a missing message under a bare boolean assertion, and a test name that names a location rather than
a finding. Detectable only with a run are rotten green tests, order dependence, and flakiness. Detectable only with a
mutation tool is the test that passes against a broken implementation. Pass 2 should confirm each placement against a
source rather than by assertion.

**Conflicts to resolve, and each needs a stated winner.** Go tells authors to avoid assertion libraries and hand-write
the comparison and message; the baseline and the JVM sources tell them to pick the assertion that prints the operands.
Google says state over interactions; Fowler presents both as legitimate schools. DAMP against DRY is settled by Google
for tests, and unsettled elsewhere. One assertion per test against one behavior per test: the baseline says the
former, Google says the latter, and JUnit's `assertAll` and Go's `t.Error` both exist to make several assertions
report together. The pyramid against the trophy is unresolved and probably unresolvable on evidence.

**Whether any source treats the test as an artifact its own author may game.** Only the LLM-oracle papers (#29) and,
implicitly, mutation testing (#20, #22, #27) do. Neither proposes a rule an agent applies to itself before the suite
runs. This is the largest hole, and the check most likely to have to be invented: a rule that requires the author to
name, for each new test, the change to the production code that would make it red.

**Whether the level rule survives contact.** The three cases the brief names, a bug fix in a private helper, a new
public method, a change in a protocol reader, are not answered by any source found. Google's rule is about test size,
not about which level a given change owes. Kubernetes and KUnit state blanket requirements. Pass 2 should test the
candidate level rule against these three cases before adopting it.

**Open questions of my own.** Does any source give a rule for the test that already exists, so a change owes nothing?
Redundancy, two tests that cannot fail independently, is named in the brief and appears in no source found; mutation
tooling detects it only indirectly. What does a property-based test cost the T1 reader, given that Hypothesis shrinks
to a minimal example and prints it: is the shrunk example a sufficient bug report, or does the property's name have to
carry the finding? And what remains for a human: whether the behavior the test asserts is the behavior that was
wanted. Every source found checks the test against the code; none checks it against the intent, and that is the
judgment the specification problem leaves behind.
