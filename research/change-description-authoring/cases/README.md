# Regression cases for change-description-authoring

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed.

## Running a case

From the repository root:

```bash
research/change-description-authoring/cases/run-case.sh research/change-description-authoring/cases/<case> opus result
```

The script copies the skill and `english-developer-style` out of the checkout, runs `claude -p` in safe mode in a
temporary directory with the Read tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt` (cost, tokens,
turns), and `<model>/skill-tree`. `--baseline` runs the same prompt with `english-developer-style` alone and writes
under `<model>/baseline/`. Set `EFFORT=high` for Haiku, as the committed Haiku results ran. A fourth argument takes the
skill from a commit instead of the working copy.

Then grade the results:

```bash
python3 research/change-description-authoring/cases/check.py research/change-description-authoring/cases/<case>
```

`check.py` prints PASS, FAIL, or READ for every check of every result, including `controls/`. A PASS means the marker
was found, not that the check passed: read the result against the check's question in the case README before
recording a grade. READ marks a check the script leaves to the reader.

## Controls

A check that never fails is not a check. Every check has failed on at least one committed output: a baseline run
without the skill, a result of the current skill, or a file under `controls/`. A control is the real text the case was
built from (`as-pushed.md`, `posted.md`), a draft written under an earlier version of the skill (`run-B.md`), or a
passing result with the edits the case README names, made so that each check is seen failing once. The baselines of
`pgjdbc-4367-breaks` are the exception to "without the skill": they ran with the skill as it was before the rule that
case tests.

## The cases

| Case | Input | Rules |
| --- | --- | --- |
| [`pgjdbc-4367-breaks`](pgjdbc-4367-breaks/README.md) | pgjdbc#4367 draft | a break leads the description before a patch release |
| [`pgjdbc-4392-no-break`](pgjdbc-4392-no-break/README.md) | pgjdbc#4392 draft | negative control: no lead and no empty section without a break |
| [`pgjdbc-4466-squash-default`](pgjdbc-4466-squash-default/README.md) | pgjdbc#4466 branch | merge model: squash, default message |
| [`pgjdbc-4466-squash-title-description`](pgjdbc-4466-squash-title-description/README.md) | pgjdbc#4466 branch | merge model: squash, "title and description" |
| [`pgjdbc-4466-squash-or-rebase`](pgjdbc-4466-squash-or-rebase/README.md) | pgjdbc#4466 branch | merge model: squash or rebase per pull request |
| [`pgjdbc-4466-merge-commit-title-description`](pgjdbc-4466-merge-commit-title-description/README.md) | pgjdbc#4466 branch | merge model: merge commit, "title and description" |
| [`pgjdbc-4466-detection-failed`](pgjdbc-4466-detection-failed/README.md) | pgjdbc#4466 branch | merge model unknown; the detection command on a fork |
| [`pgjdbc-4424-docs-only`](pgjdbc-4424-docs-only/README.md) | pgjdbc#4424 diff and notes | verification without tests, headings, section citations, links |
| [`pgjdbc-4370-verbose`](pgjdbc-4370-verbose/README.md) | pgjdbc#4370 description | length, what the tests establish, coverage lost |
| [`pgjdbc-4374-commit-changelog`](pgjdbc-4374-commit-changelog/README.md) | pgjdbc#4374 description | `User-visible:` lines with their SQLState, the changelog entry |
| [`pgjdbc-4423-no-outcome`](pgjdbc-4423-no-outcome/README.md) | pgjdbc#4423 diff and notes | negative control: no outcome slot and no changelog entry |
| [`calcite-5330-open-question`](calcite-5330-open-question/README.md) | apache/calcite#5330 discussion | a question only a maintainer can settle; a break in a minor release |
| [`jdk-33173-audit`](jdk-33173-audit/README.md) | openjdk/jdk#33173 notes | a defect nobody has observed, hunks not read aloud, an answered review question |
| [`pgjdbc-4501-manual-check`](pgjdbc-4501-manual-check/README.md) | pgjdbc#4501 description and diff | a manual check kept literal; no search result, bookkeeping, or footer |
| [`pgjdbc-4388-contract-fix`](pgjdbc-4388-contract-fix/README.md) | pgjdbc#4388 description and diff | the old lines shown; a contract fix is not a break; no test narration |
| [`pgjdbc-4420-test-sites`](pgjdbc-4420-test-sites/README.md) | pgjdbc#4420 description and diff | negative control: the pairing of tests to sites stays in a test-only change |

The five `pgjdbc-4466-*` cases share their input below "Repository facts" and differ in the merge model, so a check that
passes in one and fails in another isolates the row of the model table. `pgjdbc-4466-detection-failed` also asks for
the detection commands.
