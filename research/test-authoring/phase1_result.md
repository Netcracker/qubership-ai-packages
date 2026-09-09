# Pass 1 discovery report: rules for what a test establishes, at which level, and how its failure reads

Every central claim below is labeled **studied** (a measured result in a paper or an industrial dataset) or
**asserted** (stated by a practitioner or a document without measurement). Sample sizes are the ones the source
reports; where a summary and the paper disagreed, the paper's text was read.

## 1. Executive summary

**No single source covers the domain.** The closest is *Software Engineering at Google*, chapters 12 to 14 (unit
testing, test doubles, larger tests): it covers robustness, the failure report, DAMP and test data, test sizes, and
when a double is warranted, with a rationale for each rule. It does not cover input selection (equivalence classes,
boundaries), it does not give a level rule for a given change, and every claim in it is asserted. Synthesis is
required: practitioner guidance for the rules, the empirical literature for which of them are studied, framework
documentation for question 8, and oracle documentation for what a tool can report.

**Strongest category: practitioner guidance from engineering organizations** (Google's book and the Testing on the
Toilet series, the Go wiki's TestComments). These state a rule and its rationale, ship before-and-after examples, and
are written for the reader who holds only a failing report. **Weakest and most polluted: agent skills and rule files.**
Most are conventions (framework, naming pattern, Given-When-Then) with no rationale and no rule about whether the test
can fail. One exception exists and is on the shortlist. The research category is strong on sensitivity and flakiness,
weak on the failure report, and contradicts practice on test smells.

**Existing agent skills for test content.** One: `obra/superpowers` `test-driven-development/writing-good-tests.md`.
It names the writer-optimizes-for-green shapes directly: an expectation computed by the code under test, an assertion
on the mock, a shared object for setup and assertion, and a pre-finish "mutation check". Everything else found
(`awesome-cursorrules` test files, `clear-solutions/unit-tests-skills`, marketplace "unit-test" skills) governs
conventions and wording. The category is thin.

**The reader table holds, with one amendment.** T1 to T4 are each served by at least one source. T5, the API learner,
is served by two sources only in passing: Google's chapter 12 says tests via public APIs "provide useful
documentation", and Beck's *Readable* desideratum. No source gives T5 a rule that T4 does not already get from
"the test reads without the implementation open". Recommend collapsing T5 into T4 unless Pass 2 finds otherwise.

**Answerable from existing sources:** questions 3 (sensitivity: strong studied base), 4 (robustness: asserted, but
consistently by several independent authorities), 6 (determinism: two studies and a survey with proportions), 8
(framework specifics: all official pages found and read). **Partly answerable:** 5 (the failure report: rules are
asserted; the harm of assertion roulette and eager test is studied, but 2022 work says the detectors and the vocabulary
are mismatched), 7 (organization: Google and Meszaros, all asserted), 9 (agent-authored tests: several 2023 to 2026
papers name checkable defect shapes), 2 (inputs: ISTQB and one 1997 experiment). **Under-served:** 1 (level: no source
states which level a given change owes a test at; the pyramid, honeycomb, and trophy are all asserted and the trophy's
author says so) and 10 (review rubrics: no rubric for tests exists as such; the pieces are scattered across
contribution guides and the smell catalog).

**Pass 2 should concentrate on practitioner guidance and the oracle documentation**, use the research to label each
rule studied or asserted, and use the framework documentation to fill the question 8 table. Standards can be taken
from the free ISTQB syllabus; ISO 29119-4 is paywalled and covers the same techniques.

## 2. Candidate inventory

Category codes: PG practitioner guidance, SS standard or syllabus, FD framework documentation, OT oracle tool, RS
research, CG contribution guide, AS agent skill. Use codes: A authoring, R reviewing, M mechanical checking, B
background.

| # | Name | URL | Cat. | Author or org | Questions | Readers | Use | Evidence | Maint. | Why it is worth considering |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SWE at Google ch. 12, Unit Testing | https://abseil.io/resources/swe-book/html/ch12.html | PG | Google (Winters, Manshreck, Wright) | 4, 5, 7 | T1 T2 T3 T4 | A R | strong, asserted | active (free online) | Rule plus rationale for unchanging tests, public APIs, state over interactions, behaviors not methods, name after behavior, no logic in tests, clear failure messages, DAMP over DRY |
| 2 | SWE at Google ch. 13, Test Doubles | https://abseil.io/resources/swe-book/html/ch13.html | PG | Google | 4 | T2 T3 | A R | strong, asserted | active | Preference order real > fake > stub > interaction; three named criteria for leaving the real thing; "@DoNotMock" from measured maintenance cost |
| 3 | SWE at Google ch. 14 plus "Test Sizes" (2010) | https://abseil.io/resources/swe-book/html/ch14.html, https://testing.googleblog.com/2010/12/test-sizes.html | PG | Google (Stewart) | 1 | T2 T4 | A R B | medium, asserted | active | Small/medium/large defined by constraints, not by what is tested; names the gaps unit tests leave (unfaithful doubles, config); no rule for when a change needs a larger test |
| 4 | Testing on the Toilet series (9 posts, 2013 to 2024) | https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html and siblings | PG | Google | 3, 4, 5, 7 | T1 T2 T3 | A R | strong, asserted | active (2024 post) | One page per rule with example: change-detector tests, test behaviors not methods, state vs interactions, only verify state-changing calls, keep tests focused, DAMP, don't mock types you don't own, descriptive names, narrow assertions (2024) |
| 5 | Kent Beck, Test Desiderata | https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3, https://testdesiderata.com/ | PG | Beck | 3, 4, 5, 6 | T1 T3 | R B | medium, asserted | stale (2019) but cited | Twelve properties with trade-offs named: Behavioral, Structure-insensitive, Deterministic, Isolated, Specific ("cause of failure should be obvious") map onto questions 3 to 6 |
| 6 | Khorikov, Unit Testing: Principles, Practices, and Patterns, and "When to mock" | https://www.manning.com/books/unit-testing, https://enterprisecraftsmanship.com/posts/when-to-mock/ | PG | Khorikov | 3, 4 | T2 T3 | A R | medium, asserted | stale (2020) | Four pillars; observable behavior vs implementation detail; managed vs unmanaged dependencies as the mock rule; intra-system communications are implementation details |
| 7 | Meszaros, xUnit Test Patterns smell catalog | http://xunitpatterns.com/Test%20Smells.html | PG | Meszaros | 5, 6, 7, 10 | T1 T2 T3 | R | strong, asserted | stale (2007) but canonical | Named, recognizable shapes: Obscure Test (Eager, Mystery Guest, General Fixture, Irrelevant Information), Conditional Test Logic, Assertion Roulette, Erratic Test, Fragile Test |
| 8 | Vocke, "The Practical Test Pyramid"; Fowler, "Mocks Aren't Stubs" | https://martinfowler.com/articles/practical-test-pyramid.html, https://martinfowler.com/articles/mocksArentStubs.html | PG | Fowler site | 1, 4 | T2 T4 | B | medium, asserted | stale (2018, 2007) | Pyramid cost/speed claims stated without data; solitary vs sociable units; state vs behavior verification, classical vs mockist |
| 9 | Spotify honeycomb; Dodds testing trophy | https://engineering.atspotify.com/2018/01/testing-of-microservices, https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications | PG | Spotify; Dodds | 1 | T2 T4 | B | weak, asserted | stale | The counter-position to the pyramid: integration tests as the bulk; Dodds writes that testing tenets are not "scientific knowledge" |
| 10 | ISTQB CTFL v4.0, section 4.2 | https://astqb.org/4-2-black-box-test-techniques/ | SS | ISTQB | 2 | T2 T4 | A R | medium, asserted | active (2023) | Free, precise definitions: one test per partition and why, valid and invalid partitions, 2-value and 3-value BVA, decision tables, state transitions, coverage per technique |
| 11 | ISO/IEC/IEEE 29119-4:2021 | https://www.iso.org/standard/79430.html | SS | ISO/IEC/IEEE | 2 | T2 | B | medium, asserted | active | Same techniques as ISTQB with formal coverage items; paywalled, so only worth citing |
| 12 | Reid, "An empirical analysis of EP, BVA and random testing" (1997) | https://ieeexplore.ieee.org/document/637166/ | RS | Reid | 2 | T2 | B | medium, studied (one program, 20 KLOC Ada) | stale | Only experiment found: BVA mean detection probability 0.79, EP 0.33, random lower; needs Pass 2 confirmation from the paper |
| 13 | Myers, The Art of Software Testing, 3rd ed., ch. 4 | https://www.wiley.com/en-us/The+Art+of+Software+Testing,+3rd+Edition-p-9781119202486 | SS | Myers, Sandler, Badgett | 2 | T2 T4 | B | medium, asserted | stale (2011) | Origin of EP, BVA, cause-effect graphing, error guessing, with worked derivations |
| 14 | Inozemtseva & Holmes, "Coverage is not strongly correlated with test suite effectiveness" (ICSE 2014) | https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf | RS | UBC | 3 | T2 | B | strong, studied (5 Java projects, 31000 suites, statement/decision/modified-condition coverage, mutation score) | stale | Low to moderate correlation once suite size is controlled; coverage type does not matter; "should not be used as a quality target" |
| 15 | Just et al., "Are mutants a valid substitute for real faults?" (FSE 2014) | https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf | RS | UW, UBC, Sheffield | 3 | T2 | B M | strong, studied (357 real faults, 5 projects, 230000 mutants) | stale, 10-year award 2024 | 73% of real faults coupled to mutants; 17% not coupled to any; correlation with real-fault detection stronger than statement coverage's |
| 16 | Zhang & Mesbah, "Assertions are strongly correlated with test suite effectiveness" (FSE 2015) | https://people.ece.ubc.ca/amesbah/resources/papers/fse15.pdf | RS | UBC | 3, 5 | T2 | B | strong, studied (6700 suites, 24000 assertions, 5 projects) | stale | Assertion count and assertion coverage predict effectiveness better than size; supports "a test without an assertion cannot fail" with data |
| 17 | Petrović et al., "Does mutation testing improve testing practices?" (ICSE 2021) and "Practical mutation testing at scale" (TSE 2021) | https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf, https://arxiv.org/abs/2102.11378 | RS OT | Google, Passau, UW | 3, 10 | T2 | M B | strong, studied (about 15 million mutants; 24000 developers, 1000 projects) | active | Surfacing surviving mutants in code review leads developers to write more and better tests; mutate only changed code; "productive" mutant filtering |
| 18 | Luo et al., "An empirical analysis of flaky tests" (FSE 2014) | https://petertsehsun.github.io/soen7481/papers/flakyTests.pdf | RS | UIUC | 6 | T2 T3 | B | strong, studied (201 fix commits, 51 projects) | stale | Async wait 74/201, concurrency 32, order dependency 19, resource leak 11, network 10, time 5, IO 4, randomness 4, floating point 3; 78% flaky when first written; 24% of fixes change the code under test, 94% of those fix a real bug |
| 19 | Parry et al., "A survey of flaky tests" (TOSEM 2021) | https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf | RS | Sheffield, Allegheny, CMU | 6 | T2 | B | strong, studied (survey of 76 papers) | active | Cause taxonomy incl. Too Restrictive Range, Test Case Timeout, Platform Dependency; order-dependent tests up to 16% of flaky bug reports; a later study's top three: concurrency 26%, async 22%, restrictive range 17% |
| 20 | van Deursen et al. 2001; Bavota et al. 2015; Spadini et al. 2018 (test smells and harm) | https://link.springer.com/article/10.1007/s10664-014-9313-0, https://research.tudelft.nl/en/publications/on-the-relation-of-test-smells-to-software-code-quality | RS | TU Delft, USI, others | 5, 10 | T2 | B | medium, studied (Bavota: comprehension 30% better without smells, 86% of JUnit classes smelly; Spadini: 221 releases of 10 systems) | stale | Indirect Testing, Eager Test, and Assertion Roulette are the smells most tied to change- and defect-proneness |
| 21 | Panichella et al., "Test smells 20 years later" (EMSE 2022) | https://research.tudelft.nl/en/publications/test-smells-20-years-later-detectability-validity-and-reliability/ | RS | TU Delft, ZHAW, Passau | 5, 10 | T2 | B M | strong, studied (hundreds of hand-annotated suites) | active | Contradicts row 20 in part: the detector misclassifies over 70% of smells; several smells ubiquitous in developer tests but uncorrelated with real flaws; vocabulary "highly mismatched" |
| 22 | tsDetect | https://dl.acm.org/doi/10.1145/3368089.3417921 | OT | Peruma et al. | 10 | T2 | M | medium, studied (19 smells, 96% precision on its own benchmark; see row 21 for the counter-result) | unclear | Only static detector with a published evaluation; its rule list is a checklist an agent can apply from the file |
| 23 | Stryker mutant states; PIT; cargo-mutants; mutmut; gremlins | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/, https://mutants.rs/using-results.html, https://pitest.org/quickstart/mutators/ | OT | tool maintainers | 3 | T2 | M | strong, asserted | active | Exact semantics of survived vs no-coverage vs unviable; "missed means no test failed with this mutation applied"; the oracle for "the test can fail" |
| 24 | pytest-randomly, JUnit MethodOrderer.Random, iDFlakies, NonDex | https://github.com/pytest-dev/pytest-randomly, https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/MethodOrderer.Random.html | OT | plugin maintainers; UIUC | 6 | T2 T3 | M | medium, asserted (tool docs) | active | Random order with a printed seed is the cheapest oracle for order dependence; iDFlakies partially classifies OD vs NOD |
| 25 | Go wiki: TestComments and CodeReviewComments "Useful Test Failures" | https://go.dev/wiki/TestComments, https://go.dev/wiki/CodeReviewComments | FD | Go team | 5, 7, 8 | T1 T2 | A R | strong, asserted | active | The most complete T1 guidance found: got before want, identify the function and the input, compare full structures, print diffs with direction, keep going with t.Error, human-readable subtest names, test error semantics not strings |
| 26 | JUnit 5 user guide: assertions and parameterized display names | https://docs.junit.org/current/writing-tests/assertions.html, https://docs.junit.org/current/writing-tests/parameterized-tests.html | FD | JUnit team | 8 | T1 | A | strong, asserted | active | expected/actual/message order, Supplier messages, assertAll reports every failure, assertThrows returns the exception; name placeholders {index} {arguments} {argumentsWithNames}, default pattern |
| 27 | Google Truth "comparison" page; AssertJ "Assertion description" and "Overriding error message"; Hamcrest tutorial | https://truth.dev/comparison, https://assertj.github.io/doc/, https://hamcrest.org/JavaHamcrest/tutorial | FD | Google; AssertJ; Hamcrest | 8 | T1 | A | strong, asserted | active | Truth: fewer assertions so failure messages can be designed, a "value of" line, unified diffs; AssertJ: as() prefixes the default message, withFailMessage replaces it, both must precede the assertion; Hamcrest: "Expected: … but: …" |
| 28 | pytest docs: assertion introspection and parametrize ids | https://docs.pytest.org/en/stable/how-to/assert.html, https://docs.pytest.org/en/stable/how-to/parametrize.html | FD | pytest team | 8 | T1 | A | strong, asserted | active | Bare assert prints subexpressions and diffs; a message is printed alongside, not instead; ids from values, ids= and pytest.param(id=); failures read test_eval[6*9-42] |
| 29 | Rust book ch. 11 and assert_eq! docs | https://doc.rust-lang.org/book/ch11-01-writing-tests.html, https://doc.rust-lang.org/std/macro.assert_eq.html | FD | Rust project | 8 | T1 | A | strong, asserted | active | assert! prints only the expression; assert_eq! prints left and right in Debug; custom message adds, does not replace; should_panic(expected=) narrows the panic |
| 30 | Jest expect and test.each; Vitest expect and test.each/test.for; node:test | https://jestjs.io/docs/expect, https://jestjs.io/docs/api, https://vitest.dev/api/expect.html, https://nodejs.org/api/test.html | FD | Meta; Vitest; Node.js | 8 | T1 | A | strong, asserted | active | Jest toBe reports a deep diff, no custom message without expect.extend; Vitest accepts a message as second argument and expect.soft; both name cases with %s/%p/$var; node:test reports "parent > subtest" and relies on node:assert |
| 31 | Kubernetes: testing.md, writing-good-e2e-tests.md, flaky-tests.md | https://github.com/kubernetes/community/blob/master/contributors/devel/sig-testing/writing-good-e2e-tests.md | CG | Kubernetes SIG Testing | 1, 5, 6, 7 | T1 T2 T4 | A R | strong, asserted | active | "All packages require unit tests"; table-driven preferred; hermetic and parallel-safe; "Timeout is not a useful error message"; zero-flake policy, no automatic retries; stress tool for deflaking |
| 32 | Django "Submitting contributions"; rustc-dev-guide "Adding new tests"; pytest "Contributing" | https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/submitting-patches/, https://rustc-dev-guide.rust-lang.org/tests/adding.html, https://docs.pytest.org/en/stable/contributing.html | CG | Django; Rust; pytest | 3, 7 | T2 T4 | R | medium, asserted | active | The regression-test guarantee stated as a rule: "fail while the bug still exists and pass once fixed"; "fail in master but pass after the PR"; where a new test goes (nearest existing file, directory named by the code under test); avoid issue numbers in names |
| 33 | PostgreSQL "Test Evaluation" | https://www.postgresql.org/docs/devel/regress-evaluation.html | CG | PostgreSQL | 6 | T1 T3 | B | medium, asserted | active | Catalog of spurious diffs in a golden-output suite: locale, timezone, float formatting, row order without ORDER BY, platform error text; each a determinism cause with its fix |
| 34 | KUnit tips | https://www.kernel.org/doc/html/next/dev-tools/kunit/tips.html | CG FD | Linux kernel | 8 | T1 | A | medium, asserted | active | EXPECT continues, ASSERT stops; _MSG variants add context; how to test static functions |
| 35 | obra/superpowers: writing-good-tests.md and test-driven-development SKILL.md | https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/writing-good-tests.md | AS | obra | 3, 4, 9 | T2 T3 | A R | medium, asserted | active (2025 to 2026) | Names the gameable shapes: expected value computed by the code under test, assertion on the mock, same object for setup and assertion, tests that fail only by crash, no change detectors; "watch it fail first" as a property of the artifact; a pre-finish mutation check |
| 36 | LLM test-quality studies: Schäfer et al. TSE 2023; Yuan et al. FSE 2024; DeCon 2025; Ouedraogo et al. TOSEM 2025; Siddiq et al. 2023; Kremer et al. 2025 (Python) | https://arxiv.org/abs/2302.06527, https://arxiv.org/abs/2305.04207, https://arxiv.org/abs/2501.02901, https://arxiv.org/abs/2410.10628, https://arxiv.org/abs/2305.00418, https://arxiv.org/abs/2506.14297 | RS | various | 9 | T2 | B | strong, studied (e.g. 20505 LLM suites vs 779585 human tests; 62.4% of HumanEval assertions incorrect across 4 LLMs) | active | Recurring defect shapes: incorrect assertions, Assertion Roulette and Magic Number most common, Empty Test and Duplicated Assert, assertion errors 64% of errors in Python suites |
| 37 | Agent-behavior studies: over-mocked tests (2602.00409); "Rethinking agent-generated tests" (2602.07900); "Building to the test" (2606.28430); SWT-Bench (2406.12952); test overfitting on SWE-bench (2511.16858) | https://arxiv.org/abs/2602.00409, https://arxiv.org/abs/2602.07900, https://arxiv.org/abs/2606.28430, https://arxiv.org/abs/2406.12952 | RS | various | 3, 9 | T2 | B | medium to strong, studied (1.2 million commits, 48563 by agents: 36% add mocks vs 26% for humans; six models on SWE-bench Verified) | active (2024 to 2026) | Agents mock more than people; agent tests carry print statements more often than assertions; with a visible oracle agents "build to the test"; a fail-to-pass test doubles fix precision |
| 38 | Goldstein et al., "Property-based testing in practice" (ICSE 2024); Hypothesis "Replaying failures" | https://dl.acm.org/doi/10.1145/3597503.3639581, https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html | RS FD | Penn, Jane Street; Hypothesis | 2 | T1 T2 | B | medium, studied (30 interviews) | active | PBT strongest for complex code and confidence beyond examples; weaknesses are writing properties and judging effectiveness; the T1 cost is the shrunk example plus a seed or a reproduce_failure blob |
| 39 | Assertion-message studies: Taha et al. 2023 (usage and readability); "Rationale and use of assertion messages" 2024 | https://arxiv.org/abs/2303.00169, https://arxiv.org/html/2408.01751v1 | RS | RIT and others | 5 | T1 | B | medium, studied (20 Java systems) | active | Developers rarely supply a message; identifier-only messages and literal-only messages differ in readability; no study found that measures time to diagnosis |
| 40 | Wu & Clause, test-name patterns (ASE 2016, JSS 2020); Daka et al. readability (FSE 2015) | https://dl.acm.org/doi/10.1145/2970276.2970342, https://dl.acm.org/doi/10.1145/2786805.2786838 | RS | Delaware; Sheffield | 5 | T1 | B | medium, studied | stale | Action-predicate-scenario pattern detects non-descriptive names at 95% precision; no study measures diagnosis time from names |

## 3. Promising shortlist for Pass 2

1. **SWE at Google, chapters 12 and 13, with the Testing on the Toilet posts (rows 1, 2, 4).** The only source that
   states rules for robustness, the failure report, DAMP, and doubles with a rationale and an example each, from an
   organization that measured the maintenance cost of the alternative. Contributes: unchanging tests across
   refactoring, test via public API, state over interactions, one behavior per test, name after behavior, no logic,
   the "expected X, got Y with context" message, narrow assertions, when a real dependency is left behind. Serves T1
   to T4. Converts into compact rules; every rule is asserted, so pair each with rows 14 to 21 for its evidence label.
2. **Go wiki TestComments and "Useful Test Failures" (row 25).** The strongest T1 source: it prescribes what a failure
   line carries (function, input, got, want, a directed diff) and why each part is there. Language-neutral once the
   `got/want` order is translated into each framework's convention. Converts directly into a checkable rule for the
   diff: a failure line with no input and no actual value is a violation visible without running the suite.
3. **obra/superpowers writing-good-tests.md (row 35).** The one agent skill that treats the writer as an adversary.
   Contributes the gameable shapes and a "name the production change that would fail this test" gate. Serves T2 and
   T3. Already in rule form; Pass 2 should check each rule against rows 14 to 17 and keep the ones with a rationale.
4. **The sensitivity evidence cluster: Inozemtseva and Holmes, Just et al., Zhang and Mesbah, Petrović et al. (rows 14
   to 17).** Together they settle question 3's evidence: coverage does not establish effectiveness, mutants do
   correlate with real faults (73% coupled, 17% not), assertion count and coverage do correlate, and surfacing
   surviving mutants in review changes what developers write. Serves T2. Converts into two rules with a studied label:
   a coverage number is not evidence a test can fail, and a surviving mutant on a changed line is.
5. **Mutation-tool documentation: Stryker states, cargo-mutants, PIT, mutmut (row 23).** Defines what the oracle
   reports and what it cannot: survived vs no coverage vs unviable, equivalent mutants, "missed means no test failed".
   Serves T2 as the mechanical check. Converts into the rule of what to do with each state.
6. **Luo et al. and Parry et al. (rows 18, 19).** Give question 6 its proportions and its fix strategies (waitFor over
   sleep, shared state cleaned or made per-test, seeds fixed, order not assumed). Serves T2 and T3. Converts into a
   checklist keyed by cause, each detectable from the test file except order dependence, which needs the random-order
   runner (row 24).
7. **Test-smell evidence with its counter-result: Bavota, Spadini, Panichella (rows 20, 21), and the Meszaros catalog
   (row 7).** The catalog supplies names an agent can apply; Bavota and Spadini supply the harm; Panichella limits
   which smells are worth flagging and warns that static detectors are unreliable. Serves T2. Converts into a short
   list (Eager Test, Assertion Roulette, Mystery Guest, Conditional Test Logic, Indirect Testing) with an evidence
   label per smell.
8. **ISTQB CTFL v4.0 section 4.2 with Reid 1997 (rows 10, 12).** Gives question 2 its definitions and its one measured
   comparison. Serves T2 and T4. Converts into the baseline's checklist item with a definition of "class" and
   "boundary" that an agent can apply from the signature and the specification; Pass 2 should read Reid's paper to
   confirm the 0.79 and 0.33 figures and their scope.
9. **Beck's Test Desiderata (row 5).** Twelve one-line properties with the trade-offs named; *Behavioral*,
   *Structure-insensitive*, *Deterministic*, *Isolated*, and *Specific* are the vocabulary the other sources use
   without naming. Serves T3 and T1. Converts into headings for the skill rather than rules.
10. **Khorikov (row 6).** Gives the mock rule a criterion an agent can apply: mock unmanaged out-of-process
    dependencies, use real managed ones, never mock intra-system communication. Serves T3. Converts into one rule with
    a decision question; asserted, but consistent with Google's preference order and with "don't mock types you don't
    own".
11. **Framework assertion and naming documentation (rows 26 to 30, 34).** Supplies the question 8 table: which
    assertion prints operands, where the message goes, whether it adds or replaces, how a parameterized case is named.
    Serves T1. Converts into a per-framework table; measured output should be captured in Pass 2 where the docs are
    silent (Go's `--- FAIL` layout, JUnit's default parameterized name).
12. **Agent-behavior studies (row 37) with the LLM test-quality studies (row 36).** Name the defect shapes an agent
    produces: over-mocking, print statements instead of assertions, incorrect assertions, empty tests, duplicated
    asserts, building to a visible test. Serves T2. Converts into review checks; each shape is detectable from the
    diff except "incorrect assertion", which needs the suite or a spec.

## 4. Obvious rejects

- **Dodds's testing trophy (row 9).** Front-end specific, asserted, and its author disclaims scientific grounding; keep
  only as the named counter-position to the pyramid.
- **`awesome-cursorrules` test rule files.** Framework conventions and naming patterns with no rationale and no rule
  about whether a test can fail; wording only.
- **`clear-solutions/unit-tests-skills` and marketplace "unit-test" skills.** Given-When-Then, `{method}_{state}_
  {outcome}` naming, AssertJ, Mockito; no rule addresses tautology or weakening; wording and conventions only.
- **The Medium "Mitigating Claude Code reward hacking" article.** Unreachable (403), anonymous, no evidence of use.
- **ISO/IEC/IEEE 29119-4 (row 11).** Paywalled; ISTQB section 4.2 states the same techniques for free.
- **Osherove, The Art of Unit Testing.** Its three properties (readable, maintainable, trustworthy) are covered with
  more precision by Khorikov, who co-authored the third edition.
- **Beizer, Software Testing Techniques.** Domain testing and the pesticide paradox are background; nothing an agent
  applies from a diff that ISTQB and Myers do not already give.
- **Daka et al. readability model (row 40, second part).** A readability model for generated tests; wording, out of
  scope.
- **Tufano et al. ASE 2016.** Developers' perception of smells, not a rule about the artifact.
- **RAIDE controlled experiment (arXiv 2207.05539).** A tool evaluation; the effect on comprehension is not quantified
  in the abstract.
- **Kubernetes flake triage process and `stress` workflow.** CI process, out of scope; the "Timeout is not a useful
  error message" rule from the same directory stays in.

## 5. Gaps and questions for Pass 2

**Detectability of each rule.** From the diff alone: no assertion; assertion on a value the test supplied; expected
value computed by the code under test or its helpers; a mock of the unit under test; `assertTrue(a == b)` where an
equality assertion exists; a message that repeats the name; conditional logic or loops in the test body; a sleep
instead of a wait; a shared mutable fixture; an interaction verification on a query method; a name that is a location.
Needs the suite run: whether a regression test was red before the fix (unless the PR shows the two runs), whether a
parameterized name is unique, what the runner actually prints. Needs a mutation tool: whether a test can fail on a
change other than the one it was written for, and whether the "change-detector" charge is true of a specific test.
Needs a random-order runner: order dependence. Pass 2 should produce this matrix with a source per cell.

**Conflicts to resolve.**

- Pyramid (row 8) against honeycomb and trophy (row 9): all asserted; Google's size taxonomy (row 3) sidesteps the
  question by defining levels by constraints rather than by counts, and may be the reusable form.
- Mocks against fakes: Google (row 2) prefers fakes; Khorikov (row 6) mocks unmanaged dependencies; Google's "only
  verify state-changing calls" (row 4) and Khorikov's "inter-system communications are observable behavior" agree on
  the case; superpowers (row 35) says "no mocks unless unavoidable". Reconcilable as one preference order.
- One assertion per test (baseline) against one behavior per test (Google row 1, superpowers row 35, "Keep tests
  focused" row 4): the sources say behavior; JUnit's `assertAll` and Vitest's `expect.soft` exist to support several
  assertions on one behavior. The baseline's "one assertion per method" needs restating.
- DAMP against DRY: Google (rows 1, 4) is the only source; Meszaros's General Fixture and Mystery Guest name the DRY
  failure shapes. No conflict found, only a missing boundary for helpers.
- Test smells: Bavota and Spadini (row 20) against Panichella (row 21) on whether the catalog predicts harm and whether
  detectors are trustworthy. Pass 2 should read Panichella's per-smell table and keep only the smells that survive.
- Go (row 25) against JUnit and testify (rows 26, 30) on operand order: `got, want` versus `expected, actual`. Not a
  conflict in substance, but the rule must be stated per framework.

**Gaming.** Three sources treat the test as an artifact its author may game: superpowers (row 35: the mutation check,
"name the change that would fail it"), Petrović (row 17: surviving mutants surfaced in review), and "Building to the
test" (row 37: agents optimize for the visible oracle). Django, rustc, and pytest (row 32) state the regression-test
guarantee but propose no check beyond the reviewer's word. Open question: whether a reviewer can require the two-run
evidence (red before, green after) in the PR, and whether a mutation run scoped to the changed lines is cheap enough to
be the default check.

**The level rule against a real change.** No source found gives a rule of the form "this change owes a test at this
level". Kubernetes (row 31) says every package owes unit tests and every PR must pass integration and e2e, which is a
policy, not a rule per change. Google (row 3) names the gaps a unit test leaves (unfaithful doubles, configuration,
emergent behavior) and Khorikov (row 6) gives "observable through the public API" as the unit-test criterion. Pass 2
should test the baseline's rule 3 against the three named cases: a bug fix in a private helper (Google and Vocke both
say test it through the public API that reaches it), a new public method (unit test through the API; integration only
where a real dependency changes the outcome), and a change in a protocol reader (Spotify's "integration test at the
contract" and Google's "exercise service call contracts" both point at a test against recorded or real protocol
bytes). Whether a second level is owed remains a judgment; the sources supply criteria, not a decision.

**Left to human judgment.** Whether an equivalence class is missing (no oracle knows the specification); whether an
assertion is too narrow for the behavior it guards (Google's "narrow assertions" and "narrow helpers" give the shape,
not the width); whether a surviving mutant is equivalent; whether a flaky fix belongs in the test or in the code under
test (Luo: 24% of the time it is the code); whether a test at a second level is worth its cost.

**Other uncertainties.** Reid 1997's figures come from summaries and need the paper. Panichella's per-smell findings
were read only from the abstract. The Just et al. 17% figure is from the paper text; the 10% "needs a stronger
operator" figure is worth quoting with it. Google's "Prefer narrow assertions" (2024) was found but not readable; its
example should be fetched. No study was found that measures time from a red build to a diagnosis as a function of test
name, assertion type, or message, so every rule for the failure report stays labeled asserted unless Pass 2 finds one.
