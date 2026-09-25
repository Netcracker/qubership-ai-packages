# Test authoring: research

An editorial pipeline that collects evidence for a repository-independent skill on **tests**: which level a change
owes a test at, which inputs the test set uses, how a writer or a reviewer establishes that a test can fail, how a
test stays green across a refactoring, and how a failing test reads to someone holding only the runner's report. This
folder is the audit trail; the skill itself is written from the synthesis and kept canonical in its package.

The pipeline reuses the method of [`docs-page-authoring`](../docs-page-authoring/) and
[`change-description-authoring`](../change-description-authoring/): readers are fixed before the first search, and the
unit of evaluation is a rule an agent can apply without the author present, stated once, with its rationale, the reader
it serves, and the way a reviewer detects a violation. One property weighs more here than in the other two: the agent
that writes the test also wrote the change, and it is rewarded when the suite passes, so every rule is also judged on
whether a writer optimizing for green can satisfy it without the test being worth anything.

| Reader | Situation |
| --- | --- |
| T1 Red-build reader | A test just failed, often in CI, often not their own; holds the runner's report and frequently no IDE |
| T2 Reviewer | Deciding whether a change is adequately tested; holds the diff of the code and of the tests |
| T3 Refactorer | Changing the implementation with the behavior fixed; expects the suite to stay green |
| T4 Next author | Adding a case, a feature, or a fix beside existing tests; asks where the new test goes and at which level |
| T5 API learner | Reading tests as the examples the documentation lacks (candidate; pass 1 says whether anyone serves it) |

Wording is out of scope and belongs to `english-developer-style`. The comment above a test belongs to the doc-comment
skill of its language (`javadoc-authoring`, `godoc-authoring`, `pythondoc-authoring`, `rustdoc-authoring`,
`jsdoc-authoring`). This research exists because those five skills each carried a section on the test itself, its
name, its assertion, and its message, which describes the test rather than its comment; that section is the seed here
and moves out of the doc-comment skills once the test skill exists.

## Method

| Step | Artifacts | What happened |
| --- | --- | --- |
| Seed | the *Baseline* section of `phase1_prompt.md` | The test-file section the five doc-comment skills carried, stripped of what concerns the comment, plus four rules the maintainer stated from practice: no boolean assertion on a non-boolean result, a message that makes the failure a bug report, a deliberate choice of level, and a checklist (boundaries, equivalence classes, the test fails when the change is reverted). |
| Phase 1: shortlist | `phase1_prompt.md`, `phase1_result.md` | Discovery pass over practitioner guidance, test-design standards, framework documentation, mechanical oracles (mutation, flakiness, smell detectors), empirical research, project contribution guides, and agent skills. Output: a candidate inventory, a shortlist, and a verdict on the reader table. |
| Phase 2: rules | `phase2_prompt.md`, `phase2_result.md` | Per shortlisted source: disposition, evidence basis, false-positive risk. Output: extracted rules with detection and repair, resolved conflicts, the split between what the agent applies and what an oracle reports, and an audit of the baseline. |
| Verification | `phase1_verification.md` | Every figure and quote in the phase-1 inventory checked against the paper or the official page, in parallel with phase 2. Fourteen corrections, mostly attributions and exact wording; the load-bearing figures confirmed. |
| Re-run on Opus | `phase1_result_opus.md`, `phase2_result_opus.md` | Both passes run again on 2026-09-07 with Opus over the same prompts, after the skill existed. Two edits followed: a §5 row for an assertion that is present but never executed, and pytest's rewriting scope in `pytest.md`. Everything else confirmed a decision the skill had made; one finding (a ranking of assertion types by mutation score) was left out because it rests on one program and does not compare the same check written two ways. |
| Synthesis | the skill itself | Written by the coding agent from the two results and the verification; no separate synthesis document. The measured framework output the skill's reference files cite is in `framework_output.md`. |

Phases 1 and 2 were run by the coding agent as deep-research subagents on 2026-09-06; the prompts are what the
subagents were given, and the result files are what came back, unedited.

## Files

```text
phase1_prompt.md, phase1_result.md     shortlist of sources; the baseline as seed; the reader table checked
phase1_verification.md                 the phase-1 figures and quotes against their primary sources
phase1_result_opus.md, phase2_result_opus.md   the two passes run again on Opus after the skill existed
phase2_prompt.md, phase2_result.md     extracted rules, conflicts resolved, agent-versus-oracle split, baseline audit
framework_output.md                    assertion output measured per framework and version
ab-pr4405.md                           the skill tried on a real fix: one-shot against plan-then-write, Opus and Sonnet
ab-pr4404.md                           the same, with the fix written too, against the review the pull request drew
ab-refs-by-role.md                     the references split by role against the one-file-per-language layout; the AssertJ leak
ab-go-prs.md                           three Go pull requests, with and without the skill, against their own tests and hand-made mutants
ab-javadoc-reread.md                   whether a re-read-the-comment rule in javadoc-authoring changes the output; it did not
ab-final-review.md                     a checklist review in a fresh subagent (the final-review package) against two real reviews
cases/<case>/                          a regression case: the tag it starts from, the task, and each model's result
```

The phase prompts use one H1 and H2 sections; the result files are pasted unedited and are excluded from markdownlint
by `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, as the other research directories are.

## Findings

- No single source covers the domain. Google's testing chapters and its Testing on the Toilet posts are the strongest
  rule source and cover robustness, doubles, the failure report, and test data; they give no input-selection rule and
  no rule for which level a change owes a test at, and every claim in them is asserted.
- The one agent skill that treats the test's author as an adversary is `obra/superpowers` `writing-good-tests.md`; it
  supplies the shapes a writer optimizing for green produces and the gate "name the production change that would fail
  this test". Everything else in that category is convention and wording.
- The reader table held for four readers. T5, the reader who uses tests as examples, is served by nobody beyond "the
  test reads without the implementation open" and collapsed into T4.
- Sensitivity has a studied base: coverage correlates low to moderately with fault detection once suite size is
  controlled; mutants are coupled to about three real faults in four and to none for about one in six; assertion count
  and assertion coverage track effectiveness; surfacing surviving mutants in review makes developers write more and
  stronger tests. The two-run rule for a regression test is stated as policy by Django, rustc, and pytest.
- Flakiness has measured proportions: waiting on a fixed delay is the largest cause, then concurrency, then order
  dependence; about a quarter of the fixes change the code under test, and nearly all of those fix a real bug.
- The test-smell literature contradicts itself. The 2022 re-examination leaves Indirect Testing and Conditional Test
  Logic as smells worth flagging from the file and finds Eager Test and Assertion Roulette ubiquitous and mostly
  harmless; their content survives in the skill as the act-after-assert signal and the message rule.
- No source states which level a given change owes a test at. The skill's level rule is derived from Google's
  constraint-defined test sizes, the observable-through-a-public-API criterion, and the process boundary as the
  trigger for a second level, and is labeled so.
- The baseline's "one assertion per method" became one behavior per test with several assertions reported together,
  and "avoid `assertTrue`" became "use the assertion that prints the operands": a boolean assertion on a boolean result
  is right, and one study ranks boolean assertions as the type most effective at killing mutants.
- No study measures the time from a red build to a diagnosis as a function of the test's name, assertion, or message,
  so every failure-report rule is asserted, with the measured framework output saying only what each slot prints.
- Agent-written tests have named defect shapes with measured frequency: more mocks than people add, print statements
  in place of assertions, incorrect assertions, and building to a visible oracle. Each maps to a shape the skill's
  sensitivity list detects from the diff.

- Tried on a real fix the same day (`ab-pr4405.md`): with the trigger installed, Opus and Sonnet both loaded the
  skill unprompted and wrote the unit test the original pull request lacked; a plan-first step cost 16 percent more
  and paid for itself with Opus (a decision table with named boundary cases, a negative control, a side defect found)
  and not with Sonnet, on one run per cell. A second trial (`ab-pr4404.md`) had the sessions write the fix as well:
  three of four cells wrote the warning assertion the reviewer had asked the original pull request for, and every cell
  narrowed the integration matrix to the failing corner, which the original had not.
- A third trial (`ab-refs-by-role.md`, 2026-09-07) split the references by the role a library plays and put a
  selection protocol in front of them. On a project using AssertJ, Opus under the old layout read `junit.md` and
  wrapped AssertJ assertions in JUnit's `assertAll`; under the split it wrote `assertSoftly` with no JUnit import.
  Opus opened the files the protocol names; Sonnet opened no reference file in any of its four runs. One sentence in
  the trigger paragraph, read the engine and assertion files before the first assertion, turned that into four of
  four on a rerun, with the new layout's cells opening exactly the two files §0 names.
- On three Go pull requests (`ab-go-prs.md`, 2026-09-07) the rule that moved was §6: every skill cell reached the
  change through the exported methods, while the pull requests' own tests and the no-skill Opus cell called the
  unexported helper. Error identity over message substrings moved for Sonnet and caught one mutant the pull request's
  tests miss; where the pull request's tests were already sound, the skill changed shape (named subtests, no sleep, no
  empty timeout branch) rather than what the tests catch.

## Cases

A case is a regression test for the skill: a repository pinned at a tag, the task a session is given there, the change
each model made with the skill, and checks. The procedure for running them is in
[`agent-packages/AGENTS.md`](../../agent-packages/AGENTS.md#testing-a-skill-against-its-cases). The cases come from two
compiler-like harnesses, NullAway's and Calcite's SQL validator, and a rule checked only against them can still break a
service, a database, or a UI test; `agent-packages/test-authoring/AGENTS.md` lists the kinds to read an edit against.

| Case | What it guards against |
| --- | --- |
| [`cases/nullaway-1834-rewrite/`](cases/nullaway-1834-rewrite/README.md) | The tests of uber/NullAway#1834 as submitted, each case and its control a separate copy of one source: a rewrite that keeps the copies, drops a case, puts two cases that expect a diagnostic into one check that stops at the first mismatch, or assembles the source from pieces of syntax |
| [`cases/nullaway-1834-from-scratch/`](cases/nullaway-1834-from-scratch/README.md) | The same production change with no tests: a defect left uncaught, a behavior the commit message names left without a case, and the same failures of form |
| [`cases/nullaway-1750-from-scratch/`](cases/nullaway-1750-from-scratch/README.md) | The production change of uber/NullAway#1750, a fix that removes a false positive: a silent case written without its reporting control, two moved inputs in one test, a new case pushed into a twin that holds cases of its own, or the `Value` stub copied again |
| [`cases/calcite-4410-rewrite/`](cases/calcite-4410-rewrite/README.md) | The tests of apache/calcite#4410 as the reviewer saw them, on a validator that takes one query per call: a dropped input, no negative case with its error position, the fixture chain copied into every test, or a loop over the inputs in one test |
| [`cases/nullaway-1834-rewrite-harness-ahead/`](cases/nullaway-1834-rewrite-harness-ahead/README.md) | The rewrite, where NullAway's instructions ask for tests written as if the harness reported every mismatch: a split by the harness's current behavior that the maintainers declined, or a proposal to change the harness they did not ask for |

`cases/run-nullaway-case.sh` runs the NullAway#1834 cases, and `cases/run-case.sh` any case that carries its repository,
base, change, and `build.sh`; both add the case's `instructions.md` to the repository's instructions where the case has
one, and `cases/check-nullaway-case.py` prints the counts their checks rely on.

The writer may run the build. On 2026-09-25 the four cells ran on skill 1.1.0 twice, one run each: once with the prompt
forbidding the build and once allowing it. Every writer that was allowed ran the tests. The cost barely moved, and the
time roughly doubled for Opus. The eight sessions and their Gradle builds ran at the same time, so the times are
inflated and noisy.

| Case, model | Without the build | With the build |
| --- | --- | --- |
| rewrite, Opus 5.5 | $1.22, 16 turns, 259 s | $1.17, 15 turns, 555 s |
| rewrite, Sonnet 5 | $1.79, 29 turns, 826 s | $1.99, 33 turns, 962 s |
| from scratch, Opus 5.5 | $1.49, 23 turns, 297 s | $1.55, 27 turns, 964 s |
| from scratch, Sonnet 5 | $1.93, 38 turns, 692 s | $1.93, 35 turns, 805 s |
| total | $6.43 | $6.64 |

Two earlier runs of from scratch with Opus, with the build forbidden, wrote tests that failed on the fix. Their markers
quoted `Test.Box<…>` where NullAway prints `Box<…>`. A writer that runs the tests sees that. A reader of the diff does
not, so the script runs the build after the session whatever the writer ran.

## Status

Both phases and the verification complete, all run on 2026-09-06. The skill lives in the APM package
[`test-authoring`](../../agent-packages/test-authoring/) and is kept canonical there, not duplicated here.
