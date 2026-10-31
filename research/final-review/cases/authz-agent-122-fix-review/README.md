# Case: review the commit that answered the first review of qubership-authz-agent#122

A regression case for `final-review`, with `test-authoring` loaded. The input is one commit of
[Netcracker/qubership-authz-agent#122][pr], `5dcb6be8` on top of `17b17fcf`, and its task statement is the three
review comments it answered, quoted in `prompt.md`. The commit adds `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, a
troubleshooting row for the Helm ownership failure, and a note in `test/k8s/README.md`. The reviewer's next round
reported that the overrides list missed the two variables ([comment][c-list]) and that the row's remedy named only
`make e2e` ([comment][c-par]).

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[c-list]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358898628
[c-par]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358898645

## What it exercises

The paragraphs on sets and parallel paths in `final-review` item *Siblings of the change*, on the shape a fix in
answer to a review usually has: a small diff, with the review comments as the task.

## Checks

1. **A new member missing from a list of the others.** As check 1 of `authz-agent-122-pr-at-fix-review`.
2. **A remedy that names one of two paths.** As check 2 of `authz-agent-122-pr-at-fix-review`.

## Skill parts

- `final-review`: `SKILL.md` §2 item *Siblings of the change*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `17b17fcf373d8d3716aa45bd7a66b5fa2d4aba9c`, and `5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2`. |
| `prompt.md` | The task with the three comments, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran with the rules on documented commands and coupled limits and without the questions of `change-reach.md`; `reach-<n>` with an earlier wording of them, before the question on parallel paths said how to check a row. |

## How to run

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-122-fix-review <model> <label> <rev>
```

## Results, 2026-10-23

| Model | Arm | Check 1 | Check 2 | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | `base` | pass, pass | pass, pass | 0.92, 0.75 |
| Opus | `reach` | pass, pass | pass, pass | 0.80, 0.72 |
| Haiku | `base` | partial, fail | fail, pass | 0.16, 0.18 |
| Haiku | `reach` | pass, pass | pass, pass | 0.20, 0.09 |

With the diff this small and the comments in hand, Opus finds both defects without the questions. The case does not
discriminate on Opus and stays as a no-regression case; Haiku `base-1` files the missing variables as taste. The
discriminating case for the same two defects is `authz-agent-122-pr-at-fix-review`, where the reviewer reads the whole
pull request.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with `apm-authoring` supplied to
the reviewer as well; the reviewed commit has no skill or instruction file, so no report used it. Graded by reading
`result.md`. Opus and Haiku, two runs each.

| Model | Check 1 | Check 2 | Words | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, pass | 1718, 1684 | 1.02, 0.67 |
| Haiku | pass, pass | pass, pass | 1444, 1164 | 0.15, 0.18 |

- **Opus `instr-1`.** Check 1 passes: "The list of Makefile overrides leaves out the two new variables", substantive.
  Check 2 passes: the row's "cause ("an older `make e2e`") and its action ("then `make e2e`") cover only e2e",
  substantive.
- **Opus `instr-2`.** Check 1 passes: "`E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are missing from the page's list
  of overrides", substantive. Check 2 passes: "its action says only "then `make e2e`" and its cause only "an older
  `make e2e`"", substantive.
- **Haiku `instr-1`.** Check 1 passes: the override paragraph "omits the two new ones", substantive. Check 2 passes:
  "its action names `make e2e` only, which does not rerun the parity stand", substantive.
- **Haiku `instr-2`.** Check 1 passes: "The override list omits the two new timeout variables", substantive. Check 2
  passes on the cause rather than the action: "The ownership row names only `make e2e` as the cause", with Item 7
  adding "while its symptom names `parity-harness` too", substantive.

Against the `1b1ebc3e` runs, the grades are unchanged: all eight cells pass on both trees. Opus writes 1718 and 1684
words against 1920 and 1930 and costs 1.02 and 0.67 against 0.96 and 0.76; Haiku writes 1444 and 1164 against 1379 and
1421 and costs 0.15 and 0.18 against 0.23 and 0.11. Beyond the checks, all four new runs file that `-test.timeout 600s`
in `suite.args` ends the suite at 10 minutes, so raising the two limits the comments name does not let a suite run
longer; of the `1b1ebc3e` runs, Opus `instr-2` did not. The reviewed commit adds no instruction for an agent, so there
is no table of added instructions to classify.
