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
