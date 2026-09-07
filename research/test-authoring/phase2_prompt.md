# Research title

Evaluate the Pass 1 shortlist and extract applicable rules for a test authoring and review skill

# Goal

Pass 1 established that no single source covers the content and structure of a test from level selection to the
failure report, and that the skill must be synthesized across four literatures: practitioner guidance from engineering
organizations, the black-box test-design techniques, framework and oracle documentation, and the empirical research
on sensitivity, flakiness, smells, and agent-written tests.

Pass 2 does not repeat that survey. Its job is to turn the shortlist into **rules an agent can apply**, and to settle
the questions Pass 1 left open.

The output of this pass feeds directly into a skill file. So the unit of the deliverable is not a source summary; it is
a rule, stated once, with a rationale, a source, the reader it serves, the situation it applies to, and the way a
reviewer detects a violation of it.

# Target domain

The consumer is an LLM agent that both writes and reviews tests inside a code repository. The most common task it
faces is not "write a test suite" but "a branch changed the product; decide which tests the change owes, write them,
and make each one able to fail". The same agent reviews tests other people or other agents wrote.

Three facts about the consumer change what counts as a usable rule:

**The agent works without the author.** It reads the test, the diff, and the source code, and it has no one to ask. A
rule that depends on knowing the intent behind a test cannot be applied, however sound it is.

**The agent wrote the change it is now testing, and it is rewarded when the suite passes.** A rule that a writer can
satisfy by asserting less, by mocking the unit under test, by computing the expected value with the code under test,
or by mirroring the implementation is a rule that will be satisfied that way. Every rule has to say what a reviewer
checks so that satisfying the letter of it is worth something.

**Some defects have an oracle.** A mutation tool reports a test that cannot fail; a random-order runner reports an
order-dependent test; the runner's own output shows what the failure report carries. Rules therefore fall into
buckets, and the report has to say which:

1. rules the agent applies while writing or reviewing, from the test file and the diff alone;
2. rules whose violation needs the suite run, and what run (the two-run red-then-green evidence, a random-order run);
3. rules a mutation tool or a smell detector reports, with what the tool's verdict does and does not establish;
4. judgments that stay with a human, which the agent may raise as a question but not decide.

# Readers

Pass 1 confirmed T1 to T4 and recommended collapsing T5 into T4. Do so: four readers, fixed.

| Reader | Situation | Holds |
| --- | --- | --- |
| T1 Red-build reader | A test just failed, often in CI, often not their own | The runner's report: class or module, test name, message, values, stack trace; frequently no IDE |
| T2 Reviewer | Deciding whether a change is adequately tested | The diff of the code and of the tests |
| T3 Refactorer | Changing the implementation with the behavior fixed | A green suite, and the expectation that it stays green |
| T4 Next author | Adding a case, a feature, or a fix beside existing tests, or reading them as the examples the documentation lacks | The test directory, and the question of where the new test goes and at which level |

Every rule names the reader whose need it exists for, listed first.

# What Pass 1 settled, and this pass does not reopen

- Synthesis is required; there is no single base source.
- Practitioner guidance from Google (chapters 12 to 14 and the Testing on the Toilet posts) and the Go wiki is the
  strongest rule source; the empirical literature supplies evidence labels, not rules; framework documentation
  supplies the per-framework table.
- The category of agent skills for test content holds one member worth reading, `obra/superpowers`
  `writing-good-tests.md`. Do not re-search the category.
- Wording is owned by `english-developer-style` and is out of scope: the phrasing of a name or a message once its
  content is decided, tense, hedging, dialect. The comment above a test is owned by the doc-comment skill of its
  language. The commit message and the pull request description are owned by `change-description-authoring`.
- The rejects from Pass 1 stay rejected: the testing trophy beyond its role as the named counter-position, the
  `awesome-cursorrules` and marketplace test-skill files, Osherove, Beizer, ISO 29119-4 in favor of the free ISTQB
  syllabus, tool-evaluation papers, CI flake-triage process.

# Shortlisted candidates from Pass 1

Evaluate these twelve. Group members count as one candidate.

1. **Software Engineering at Google, chapters 12 and 13, with the Testing on the Toilet posts** (change-detector
   tests, test behaviors not methods, state versus interactions, only verify state-changing calls, keep tests
   focused, DAMP, don't mock types you don't own, descriptive names, prefer narrow assertions).
2. **Go wiki: TestComments and the "Useful Test Failures" entry of CodeReviewComments.**
3. **obra/superpowers `writing-good-tests.md` and its test-driven-development `SKILL.md`.**
4. **The sensitivity evidence cluster:** Inozemtseva and Holmes (ICSE 2014); Just et al. (FSE 2014); Zhang and
   Mesbah (FSE 2015); Petrović et al. (ICSE 2021, TSE 2021).
5. **Mutation-tool documentation:** Stryker mutant states, PIT, cargo-mutants, mutmut.
6. **Flakiness:** Luo et al. (FSE 2014); Parry et al. (TOSEM 2021); the random-order runners (pytest-randomly, JUnit
   `MethodOrderer.Random`) and iDFlakies.
7. **Test smells with the counter-result:** the Meszaros catalog; Bavota et al. (EMSE 2015); Spadini et al. (ICSME
   2018); Panichella et al. (EMSE 2022); tsDetect.
8. **ISTQB CTFL v4.0 section 4.2 with Reid 1997** (equivalence partitioning, boundary-value analysis, decision
   tables, state transitions), and Myers chapter 4 as background.
9. **Beck's Test Desiderata.**
10. **Khorikov: the four pillars, observable behavior versus implementation detail, managed versus unmanaged
    dependencies.**
11. **Framework documentation:** JUnit 5 assertions and parameterized display names; AssertJ, Google Truth, Hamcrest;
    pytest assertion introspection and parametrize ids; the Rust book and `assert_eq!`; Jest, Vitest, `node:test`;
    KUnit tips.
12. **Agent-behavior and LLM test-quality studies:** over-mocked tests (arXiv 2602.00409); "Rethinking agent-generated
    tests" (2602.07900); "Building to the test" (2606.28430); SWT-Bench (2406.12952); test overfitting on SWE-bench
    (2511.16858); Schäfer et al. (TSE 2023); Yuan et al. (FSE 2024); Ouedraogo et al. (TOSEM 2025); Siddiq et al.
    (2023).

Also use, as supporting sources where they bear on a rule: Kubernetes SIG Testing's writing-good-e2e-tests and
testing.md; Django, rustc-dev-guide, and pytest contribution guides on the regression-test guarantee and test
placement; PostgreSQL's test-evaluation page on spurious diffs; Goldstein et al. on property-based testing; the
assertion-message and test-name studies (Taha et al. 2023; Wu and Clause).

# Measured framework output, supplied

The framework table (question 8) does not need to be measured again. The file `framework_output.md` beside this
prompt records, per framework and version, the message each assertion raises and what the runner prints around it,
measured on 2026-09-06: JUnit Jupiter 6.1.3, AssertJ 3.27.7, Google Truth 1.4.5, Hamcrest 3.0, Go 1.27.1, pytest
8.4.2, Rust 1.98.0, Node 26.8.1. Use it as the measured basis for the per-framework rules; check it against the
official documentation for anything the measurement did not cover (parameterized display names, `assertAll`,
`expect.soft`, `t.Error` versus `t.Fatal`, `EXPECT` versus `ASSERT` in KUnit), and report any place where the
documentation and the measurement disagree.

# Specific questions from Pass 1 to investigate

Answer each explicitly, and say when the evidence does not settle it.

## Conflicts Pass 1 identified as live

1. **One assertion per test against one behavior per test.** The baseline says one assertion per method; Google,
   superpowers, and "Keep tests focused" say one behavior; `assertAll` and `expect.soft` exist to put several
   assertions on one behavior. State the rule that survives, and the test a reviewer applies to tell "several
   assertions on one behavior" from "several behaviors in one test" (Eager Test).
2. **Mocks against fakes against real dependencies.** Google prefers real, then fake, then stub, then interaction
   test; Khorikov mocks unmanaged out-of-process dependencies and never intra-system communication; superpowers says
   no mocks unless unavoidable; the over-mocking study finds agents mock more than people. State one preference order
   with the criterion for each step, and the shapes a reviewer rejects outright (a mock of the unit under test, an
   assertion on the mock, interaction verification on a query).
3. **Pyramid against honeycomb.** Both asserted. Pass 1 suggested Google's size taxonomy, defined by constraints rather
   than counts, as the reusable form. Confirm or replace it, and say what the constraints are.
4. **Test smells: Bavota and Spadini against Panichella.** Read Panichella's per-smell results. Which smells survive as
   worth flagging by an agent reading the file, with what evidence label, and which are ubiquitous and harmless?

## The gap Pass 1 could not close

5. **The level rule.** No source states which level a given change owes a test at. Build the rule from the criteria
   the sources supply (Khorikov's "observable through the public API", Google's named gaps of a unit test, Spotify's
   contract test, Kubernetes's package policy) and test it against four changes: a bug fix in a private helper; a new
   public method; a change in a protocol reader that parses bytes from a socket; a change in a configuration default.
   For each, say which level owes a test, whether a second level is owed, and what the reviewer checks to see that the
   author chose rather than defaulted. Label the result derived, not sourced.

## The highest-value question in the pass

6. **Sensitivity: how a writer or a reviewer establishes that a test can fail.** Produce the complete list of shapes of
   a test that cannot fail, or fails only for the wrong reason, with for each the source that names it and how a
   reviewer detects it from the diff: no assertion; an assertion on a value the test itself supplied; an expected
   value computed by the code under test or by a helper that duplicates it; a mock of the unit under test; an
   assertion on the mock; a test that passes only because an exception is not thrown; a change-detector test that
   pins the implementation; a test that reads the same object it wrote to; an assertion weakened until it passes; a
   snapshot accepted without reading. Then state the two-run rule for a regression test (observed red before the fix,
   green after) as Django, rustc, and pytest state it, and say what evidence of it a pull request can carry. Then
   state what a mutation run scoped to the changed lines establishes, using the tool documentation for what
   "survived", "no coverage", and "equivalent" mean, and Petrović for whether it changes what people write.

## Applicability questions

7. **The failure report.** From Google, the Go wiki, the framework documentation, and the measured output, state the
   division of labor between the four parts of a failure report (the container name, the test name, the assertion's
   own output, the message) as a rule per part, with the framework-specific mapping in a table: for each framework,
   which assertion prints the operands, which prints only `true` and `false` or the expression, where the message
   goes, whether the message adds to or replaces the generated text, how a parameterized case is named and where that
   name appears. Include the got-before-want order question and answer it per framework. Note that no study measures
   time to diagnosis; label the rules asserted and say which have measured output behind them.
8. **Inputs.** From ISTQB and Myers, state the rules an agent applies from the signature and the specification: how
   to partition, one test per partition and why a second is redundant, valid and invalid partitions, two-value and
   three-value boundary analysis, when a decision table is the right shape, when a state-transition test is. Read
   Reid 1997 and confirm or correct the 0.79 and 0.33 figures and their scope. Say where property-based testing
   replaces the enumeration and what it costs T1.
9. **Robustness.** From Google, Khorikov, and Beck, state the rules that keep a test green across a refactoring: test
   through the public API, observable behavior versus implementation detail with the test a reviewer applies,
   state verification over interaction verification, when an interaction is the behavior (a state-changing call to
   an external system), no logic in the test, no shared mutable fixture. For each, the shape that violates it.
10. **Determinism.** From Luo and Parry, the causes with their measured proportions and the fix for each, as a
    checklist keyed by cause, marking which causes are detectable from the file (a sleep, a wall-clock read, a
    shared static, an unseeded random, a network address, an order assumption on a hash map) and which need the
    random-order run. Include the finding that a fix sometimes belongs in the code under test.
11. **Organization and test data.** From Google and Meszaros: DAMP over DRY with the boundary for helpers, the
    Mystery Guest and General Fixture shapes, where a new test goes (the nearest existing file, the directory named
    by the code under test, per Django and rustc), the arrange-act-assert shape, and the size at which a test class
    or file splits. All asserted; say so.
12. **Agent-written tests.** From the agent-behavior and LLM test-quality studies, list the defect shapes with their
    measured frequency where one exists (over-mocking 36% versus 26%; print statements instead of assertions;
    incorrect assertions; empty tests; duplicated asserts; building to a visible test) and say which of the rules
    from questions 6 and 9 catches each one.
13. **Property-based tests and the T1 reader.** From Goldstein and the Hypothesis documentation: what a failing
    property test reports (the shrunk example, the seed or the reproduce blob) and what the test has to carry so the
    T1 reader can reproduce it.
14. **The baseline audit.** Judge the baseline's Part 1 (the failing test as a bug report) and its four rules of Part 2
    against the extracted rules: which survive as stated, which need restating (Pass 1 already flagged "one assertion
    per method" and "avoid assertTrue"), which are unsupported, and what the baseline is missing entirely.

# Required output

Produce a research report under 5000 words excluding tables. Cite sources with URLs; prefer primary sources, official
documentation, and the papers over commentary. Do not re-explain general testing principles unless they change the
skill's design.

## 1. Executive summary

Answer directly:

- Which sources survive as *rule contributors*, and which drop to supporting or background?
- Which of the fourteen questions did the evidence settle, and which stayed open?
- What is the recommended split across the four buckets: agent from the diff, suite run, mutation or smell tool,
  human?
- Which rules resist a writer optimizing for green, and which can be satisfied without the test being worth anything?

## 2. Deep candidate evaluation

One compact table row per candidate:

- name and URL
- disposition: rule contributor / supporting / background only / reject
- strongest contribution, in one line
- main weakness
- evidence: studied or asserted, and the sample or basis where studied
- maintenance status
- worked examples available: yes / no / partial
- false-positive risk when applied mechanically: low / medium / high
- portability into a compact skill: easy / medium / hard

## 3. Extracted rules

This is the core deliverable, and it should carry most of the word budget. Produce a table of 30 to 45 rules. One row
per rule:

| Column | Content |
| --- | --- |
| Rule | One sentence, imperative, applicable without the author present |
| Rationale | Why, in one sentence: the reader who is harmed when it is broken, and how |
| Reader | T1 to T4, the one the rule exists for first |
| Source | Which candidate, with a URL or citation |
| Basis | Studied (name the study and sample) or asserted (name who asserts it), or derived (from mechanics) |
| Applies to | All tests, or the situation: a regression test, a parameterized test, a test with an external dependency, a property test |
| Detection | How a reviewer knows it was broken: a pattern in the test file, a comparison with the diff, a run of the suite, a tool's verdict, or whole-suite judgment |
| Gaming | Whether a writer optimizing for green can satisfy the rule without the test being worth anything, and what the reviewer checks then |
| Repair | What the reviewer tells the author to do |
| Bucket | Agent from the diff / suite run / tool / human |

Rules must not overlap. Where two sources state the same rule, merge them and cite both. Where they state it
differently, keep the sharper formulation and note the difference in the conflicts section rather than emitting two
rows.

## 4. The framework table

The per-framework mapping from question 7, as a table with one row per framework (JUnit 5, AssertJ, Truth, Hamcrest,
pytest, Go `testing` with testify and `go-cmp`, Rust, Jest, Vitest, `node:test`, KUnit) and the columns: the
assertion that prints the operands; the assertion that prints only a boolean or the expression; where the message
argument goes; whether the message adds to or replaces the generated text; the operand order the framework's
documentation prescribes; how a parameterized case is named and where the name appears; what the runner prints around
a failure. Mark each cell measured (from `framework_output.md`) or documented (with the URL).

## 5. The level rule and its test

The derived rule from question 5, with the four test changes worked through.

## 6. The sensitivity list

The complete list from question 6, one row per shape: the shape, the source that names it, the detection from the
diff, the repair, and which oracle confirms it where one does.

## 7. Worked examples

For at most eight of the rules, the ones whose violation is hardest to recognize, give a short before and after drawn
from real code or from a source's own example, with the source named. Two or three sentences each. Say when a source
has no examples of its own.

## 8. Conflicts and how they were decided

Each contradiction between sources: both positions with their sources, the reader whose need won, why, and whether
the losing reader is harmed.

## 9. The detectability matrix

Every rule from section 3 by bucket, with the source per cell, as Pass 1 asked.

## 10. Baseline audit

The answer to question 14.

## 11. Evidence map

Which rules rest on measured evidence, which on stated policy, which on inference from mechanics, and which on
assertion. Name the studies and their samples once, here, with every figure checked against the paper: Reid's
detection probabilities, Just's 73% and 17%, Zhang and Mesbah's correlation, Luo's cause counts, Bavota's 30% and
86%, Panichella's misclassification rate, the over-mocking 36% and 26%, Siddiq's 62.4%. Where a figure in Pass 1 was
inexact, carry the corrected figure and say what was corrected.

## 12. What the skill-writing session should be told

What to do and what not to do: no wording rules, no re-derived doc-comment rules, no promotion of asserted rows to
studied, no framework convention presented as a universal rule, no research provenance in the skill body, which rules
are load-bearing and which a compression pass drops first.
