# Case: review camunda/camunda#44166, a wait loop longer than its job

A case for `final-review` on the rule about two limits on one quantity (`research/final-review/coupled-limits.md`),
not derived from `authz-agent-122-review`. The input is [camunda/camunda#44166][pr], seven commits on top of
`e3250e60`, one file: `.github/workflows/docker-build-helm-integration.yml` gets a job that dispatches a SaaS end-to-end
run to another repository and polls for its result. The diff is +100 −3.

The job has `timeout-minutes: 20`. Its last step polls `80 x 30s`, under the comment `# Wait up to 40 min`, and ends
with `Timed out waiting for downstream workflow to complete.` and `exit 1`. The runner cancels the job at 20 minutes,
so that branch never runs, and a slow downstream run shows up as a cancelled job with no message.
[camunda/camunda#63383][fix] fixed it eight months later, after the job timeout had been raised to 35 minutes and still
sat below the loop.

Both limits are in one file, and the comment states the inner one, so item *Comments consistent with the code and with
each other* can find the defect without the rule.

## Checks

1. **The loop and the job timeout.** Pass: a substantive finding that the 20-minute job timeout ends the job before the
   40-minute loop, so its timeout branch or the comment does not hold. `grep -niE 'timeout-minutes|40 min|unreachable'
   result.md`

## Skill parts

- `final-review`: `SKILL.md` §2 item *Boundaries, partitions, and the negative control*, item *Comments consistent
  with the code and with each other*, §2a
- `test-authoring`: `SKILL.md` §4, §11
- `english-developer-style`: loaded, not checked

## Files

`repo`, `base`, `head`, `prompt.md`, and `<model>/<label>/…`, as in `authz-agent-122-review`. `main-<n>` ran the skills
at `1b34f27` (before this rule), `coupled-<n>` at the working copy of the branch that adds it.

[pr]: https://github.com/camunda/camunda/pull/44166
[fix]: https://github.com/camunda/camunda/pull/63383

## Results, 2026-10-23

`coupled-<n>` ran the first draft of the rule, `final-<n>` the committed text.

| Model | Arm | Check 1 | Cost, USD |
| --- | --- | --- | --- |
| Opus | main | pass, pass | 0.52, 0.58 |
| Opus | first draft | pass, pass | 0.54, 0.78 |
| Opus | committed | pass, pass | 0.66, 0.65 |
| Haiku | main | pass, pass | 0.10, 0.08 |
| Haiku | first draft | pass, pass | 0.06, 0.16 |
| Haiku | committed | pass, pass | 0.09, 0.03 |

Every run in every arm finds it, through the comment `# Wait up to 40 min` that the job timeout contradicts. The case
does not tell the arms apart; it shows that the rule did not cost the finding the form already made.

## Results of the `series` arm, 2026-10-23

`series-<n>` ran every rule in the series that adds the questions of `research/final-review/change-reach.md` and the
question on a replaced mechanism, in the wording of 2026-10-23: before two sentences were cut from the paragraphs on
values users already pass and on parallel paths, and before the question on a replaced mechanism was shortened. Opus,
two runs, as a no-regression check against the arm named below.

| Check | `series-1` | `series-2` | `final` |
| --- | --- | --- | --- |
| 1 | pass | pass | pass, pass |

Unchanged; the check-1 finding stays first. The question on unclaimed hunks finds the `slolatte` actor added in no
commit message, and in `series-1` also two small hunks the commit subject covers loosely. Cost 0.68 and 0.82 USD against
0.66 and 0.65.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with the runner also supplying
`apm-authoring`. In this tree §2a takes the input for an added instruction from what the artifact names, labels it
before writing a row, and replaces an empty table with the line `Added instructions: <n>, no rows.` Graded by reading
`result.md`. Opus and Haiku, two runs each. The results stand for tree `8545c2eb` as well, without a new run: it differs
from `796a9b8d` by one sentence in step 2 of the §2a table of added instructions, and no run of this case writes that
table, because the change adds no instruction.

| Model | Check 1 | Cost, USD | Words |
| --- | --- | --- | --- |
| Opus | pass, pass | 0.73, 0.75 | 1692, 1745 |
| Haiku | pass, pass | 0.03, 0.12 | 1253, 1464 |

All four runs file the 20-minute `timeout-minutes` ending the job before the 40-minute loop as substantive. The findings
tables say:

- `opus-1` (`result.md:74`): "The job timeout (20 min) is shorter than the loop bound ("40 min"), so the loop's bound
  and message never take effect".
- `opus-2` (`result.md:66`): "Job timeout of 20 min is below the loop's ≥40 min; conftest warns above 15", and a second
  row (`:67`) for the comment: ""Wait up to 40 min" comment is false".
- `haiku-1` (`result.md:64`): "The loop runs about 40 min, but the job is cancelled at 20".
- `haiku-2` (`result.md:55`): "Job cap of 20 minutes fires before the 40-minute loop bound".

The finding is first in the table in both Haiku runs, third in `opus-1` and fourth in `opus-2`.

Against tree `1b1ebc3e` no grade changed: pass in all four runs for both trees. Opus cost 0.73, 0.75 against 0.75, 0.70,
and its reports shrank from 1853, 1870 to 1692, 1745 words; Opus now files the finding lower in the table, after the
findings on matching the downstream run and on the trigger timestamp, and in `opus-2` on the unchecked dispatch. Haiku
cost 0.03, 0.12 against 0.11, 0.12, and its reports shrank from 1522, 1631 to 1253, 1464 words; the finding moved from
second to first in `haiku-1`. The change adds no skill or instruction file, and no run writes a table of added
instructions or the `Added instructions:` line; `haiku-1` says the table "is for skills and instruction files, so it
does not apply here".

## Results of the `cond` arm, 2026-10-31

Opus and Sonnet, two runs each, at tree `3d6a0954`, graded by reading `result.md`. Final-review tree `1b139bb8` is the
committed one. `3d6a0954` differs from it in two sentences: the analogue of *What the writer says it verified*, which
`3d6a0954` had shortened and `1b139bb8` keeps as before, and the command rule of item *Claimed cases covered*, where
`3d6a0954` made a command with no run a finding only where reading the tool "leaves the outcome in doubt" and `1b139bb8`
makes it one unless the reading shows the promised outcome. No check of this case reads either sentence, so its `cond`
results stand for `1b139bb8`. The committed tree is `a24f8021`: it differs from `1b139bb8` only by line wrapping and by
the word restored in "an item with a finding gives the file and line" in §2, which every run since `3d6a0954` read
without "finding".

| Model | Run | Check 1 | Words | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | `cond-1` | pass | 2009 | 1.31 |
| Opus | `cond-2` | pass | 2076 | 0.72 |
| Sonnet | `cond-1` | pass | 1860 | 0.28 |
| Sonnet | `cond-2` | pass | 1986 | 0.20 |

Every run files the 20-minute job timeout that ends the 40-minute loop, and both Opus runs put it first in the index,
where `instr` had it third and fourth. Opus reports grew from 1692 and 1745 words. No index carries a request.
