# Case: review a one-line fix with its test and an unclaimed typo

A case for `final-review` on an input where most of its items are noise. The change is one commit, `fix off-by-one in
page_count()`, on a small Python repository made for this case: the fixed line in `src/textkit/paginate.py`, its
regression test in `tests/test_paginate.py`, and a typo fixed in the first line of `README.md` (`Paginaton`) that the
commit message does not mention. The README already carries two commands, `pip install textkit` and `pytest`, that the
change does not touch. The writer's report of a red run on the base commit is in the prompt.

The case checks four rules, each added after one bad output and named by PR #200 and the audit after it: the hunk
that no sentence claims (item *Claimed cases covered*), the command lines of a changed file (same item), the findings
table that restated each request, and the closing sentence on what the review did not check (§4 and the text above §1).
On this input a reviewer that follows them files the typo, lists the commands, and states every finding twice.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **The typo is not a finding.** Pass: no finding, of any label, on the `README.md` hunk, and no request for a sentence
   that claims it. `grep -niE 'typo|Paginaton|README.md:3' result.md`
2. **The untouched commands are not listed.** Pass: the report neither lists `pip install textkit` and `pytest` against
   a script or job nor files them. A line saying the change adds no command passes. `grep -niE 'pip install|pytest\b'
   result.md`
3. **Each request is stated once.** Pass: no summary table or list repeats the change requested of a finding that an
   item section states.
4. **No closing sentence on the style pass.** Pass: the report does not end on a sentence saying the wording, the
   style, or the suite was not reviewed. A sentence naming a check the form asks for that could not be done (the drift
   script does not parse Python) passes.
5. **Length.** Pass: at most 800 words (`wc -w result.md`). The `base` runs wrote 959 to 1191.
6. **The claimed case still has its test.** Pass: item *Claimed cases covered* names
   `test_page_count_counts_partial_last_page` for the case of the task statement.

## Skill parts

- `final-review`: the text above §1; `SKILL.md` §2 item *Claimed cases covered*; §4
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Files

| File | What it is |
| --- | --- |
| `textkit.bundle` | The repository: a git bundle of `main`, two commits. `run-review-case.sh` fetches the head from it. |
| `repo`, `base`, `head` | The bundle's path, `669de41a8a448f4c8ad18155519c5c1782c3d9b5` (the commit that adds `page_count`), and `038a3d58e17a22a78d682b96627ba9f592f84eb4` (the fix). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review tree `8545c2eb` (commit `925b910`); `draft-<n>` tree `e2b69371`, the first wording of the conditions; `cond-<n>` tree `3d6a0954`. The committed tree `1b139bb8` differs from it in the analogue of *What the writer says it verified*, which applies to a skill or an instruction file, and in the outcome sentence of the command rule, which this case's commands never reach because the change does not touch them; the `cond` results stand for it. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-page-count-review <model> <label> [<rev>]
```

## Results, 2026-10-31

Opus and Sonnet, two runs per arm, graded by reading `result.md`.

| Model | Arm | 1 typo | 2 commands | 3 once | 4 closing | 5 length | 6 test | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | `base` | fail, fail | fail, pass | fail, fail | fail, fail | fail, fail | pass, pass | 1121, 962 | 0.44, 0.48 |
| Opus | `draft` | fail, fail | pass, pass | fail, fail | pass, pass | fail, fail | pass, pass | 923, 1180 | 0.41, 0.41 |
| Opus | `cond` | pass, pass | pass, pass | pass, pass | pass, pass | pass, pass | pass, pass | 796, 774 | 0.58, 0.59 |
| Sonnet | `base` | fail, fail | fail, fail | fail, fail | fail, fail | fail, fail | pass, pass | 1191, 959 | 0.31, 0.24 |
| Sonnet | `draft` | fail, fail | pass, pass | fail, fail | partial, pass | fail, fail | pass, pass | 1253, 815 | 0.24, 0.29 |
| Sonnet | `cond` | pass, pass | pass, pass | pass, pass | pass, partial | fail, fail | pass, pass | 906, 904 | 0.31, 0.36 |

- **The typo.** Every `base` run files it, three as substantive and Sonnet `base-1` as taste. The `draft` wording scoped
  the rule to hunks that change behavior, a version, or a dependency, and all four runs still filed the typo, as taste,
  saying it fell outside the rule (Opus `draft-1`, `result.md:25`: "the rule for unclaimed hunks does not cover it. A
  taste note follows"). The committed wording adds that such a hunk needs no claim and the report does not mention it;
  no `cond` run files it, and three of four still say in one clause that it needs no claim.
- **The commands.** `base` lists `pip install textkit` and `pytest` against a CI job in three runs. Every run of both
  later arms says the change adds no command line.
- **Each request once.** `base` restates every request in the closing table, and Sonnet `base-1` also adds a table per
  item. The `draft` index named its columns in prose, and all four runs wrote a request into one of its cells (Sonnet
  `draft-1`, `result.md:73`: "Item 2: mention it in the message or split it out"). The
  committed text shows the four columns as an example row; no `cond` index carries a request.
- **The closing sentence.** `base` ends every report on the wording or the suite not being checked. Under the new
  condition the closing sentence names the drift script, which does not parse Python. Sonnet `draft-1` and `cond-2`
  add that the suite was not run.
- **Length.** The committed `none` sentence ("not an answer to each of its questions") brought Opus under 800 words;
  Sonnet fell from 959 to 1191 to about 905 and still fails check 5.

The committed tree is `a24f8021`: it differs from `1b139bb8` only by line wrapping and by the word restored in "an item
with a finding gives the file and line" in §2, which every run since `3d6a0954` read without "finding".

The committed text also says an out-of-scope hunk is not mentioned; check 1 tests only that it is no finding. Opus
`cond-1` does not mention the typo; Opus `cond-2` and both Sonnet runs mention it in one clause, "needs no claim"
(Sonnet `cond-1`, `result.md:34`). The case covers a typo in prose, `README.md`; a typo fixed in a comment of a source
file, where a reviewer could read the hunk as a change to code, has no case.
