# Case: review the commit that answered the second review of qubership-authz-agent#122

A regression case for `final-review`, with `test-authoring` loaded. The input is one commit of
[Netcracker/qubership-authz-agent#122][pr], `f3b64e02` on top of `5dcb6be8`, and its task statement is the review it
answered: three inline comments and a general comment of six points, summarized in `prompt.md`. One of those points
said that a suite Pod that never starts now held `make e2e-suite` for 15 minutes, where the old target failed after 3.
The commit answers it with a polling loop that stops after "three minutes".

The reviewer's next round found that the three minutes were 90 attempts, not a deadline ([comment][c-loop]). While the
Job exists and has no Pod, for example when a ResourceQuota or an admission webhook refuses it, each
`kubectl logs job/<name>` waits up to kubectl's default `--pod-running-timeout` of 20 seconds, so the loop takes about
90 × 22 s, roughly 33 minutes: past the `helm test` timeout and the CI job's 30 minutes.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[c-loop]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4359760444

## What it exercises

The question on a replaced mechanism in `final-review` item *Boundaries, partitions, and the negative control*, in
particular its sentence on how long a loop takes to fail.

## Checks

1. **The loop is attempts, not a deadline.** Pass: a substantive finding that each attempt of the loop can wait up to
   kubectl's `--pod-running-timeout` (20 s by default) when the Job has no Pod, so the loop runs far past three
   minutes, with a request for a bound per attempt or an elapsed-time check. Partial: the report says the loop takes
   "at least" three minutes, or counts the call time, without naming the per-attempt timeout. Fail: neither.
   `grep -niE 'pod-running-timeout|33 min|each attempt|per attempt' result.md`

## Skill parts

- `final-review`: `SKILL.md` §2 item *Boundaries, partitions, and the negative control*
- `test-authoring`: `SKILL.md` §3
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2`, and `f3b64e025d3a7eaba9bc9d303897a83ff976d0bb`. |
| `prompt.md` | The task with the review it answered, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `control-<n>` ran with the rules on documented commands and coupled limits and the questions of `change-reach.md` in their first wording; `failure-<n>` with the first wording of the question on a replaced mechanism as well, and with the matching rule of `test-authoring` §3 from the branch `feat/test-authoring-replaced-mechanism-failure`, so their pass cannot be split between the two. `series-<n>` ran the text of every rule in the series as of 2026-10-23, whose question on a replaced mechanism names the fault on which one attempt waits longest. `cut-<n>` ran the committed text, which drops a sentence of rationale from that question and merges its two sentences on what to say about each fault, with `test-authoring` from `ebe8841` on `feat/test-authoring-replaced-mechanism-failure-pr`. `bound-<n>` ran the question as Netcracker/qubership-ai-packages#188 rewords it, which counts each attempt at its call's own timeout and a deadline with its overrun and asks for a deadline at the old time to fail, with `test-authoring` from the same pull request. |

## How to run

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-122-round3-review <model> <label> <rev>
```

## Results, 2026-10-23

| Model | Arm | Check 1 | Cost, USD |
| --- | --- | --- | --- |
| Opus | `control` | partial, pass, fail, pass | 1.17, 1.63, 1.39, 1.42 |
| Opus | `failure` | pass, pass | 1.18, 1.39 |
| Opus | `series` | pass, pass | 1.12, 1.23 |
| Opus | `cut`, 2026-10-24 | pass, pass | 1.33, 1.25 |

- **Control.** `control-2` and `control-4` find the 20-second wait per attempt and the 33 minutes without the question:
  `control-2` from the limits list the rule on coupled limits asks for, `control-4` while checking the Makefile comment
  that says the loop polls "for up to three minutes". `control-1` counts the loop as 90 × (2 s + one call) and stops at
  "at least three minutes", the check's partial; `control-3` reports the loop only for a `helm test` that fails before
  it creates the Job. Every run in both arms reports that the loop keeps polling after `helm test` has exited, which the
  reviewer reported in the same comment.
- **`failure`.** Both runs compare the old and the new mechanism on `ErrImageNeverPull`, where the loop does end after
  about 3.5 minutes, and then on a Job with no Pod, where it takes about 33.

The case discriminates weakly: two of four control runs pass. It stays as a no-regression case for the loop sentence;
the discriminating case for the question is check 7 of `authz-agent-122-review`.

`series-2` reaches the 33 minutes under the fault the committed question names, "the fault where one attempt waits
longest: the Job exists but no Pod is ever created", and cites kubectl's `GetFirstPod` for the 20-second wait.
`series-1` derives it from `kubectl logs --help` and adds that the restricted Pod Security Standard this pull request
turned on makes a refused Pod a realistic fault here.

Both `cut` runs reach the 33 minutes under the fault the question names. `cut-2` cites `--pod-running-timeout` from
kubectl's `cmd/logs/logs.go` and names the restricted Pod Security Standard the previous commit turned on as the way
admission refuses the Pod; `cut-1` takes the 20 seconds from `kubectl logs --help`. Both ask for
`--pod-running-timeout=2s` or a deadline, and both file the false "up to three minutes" in the Makefile comment.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with `apm-authoring` supplied to
the reviewer as well; the reviewed commit has no skill or instruction file, so no report used it. Graded by reading
`result.md`. Opus and Haiku, two runs each. The results stand for tree `8545c2eb` as well, without a new run: it differs
from `796a9b8d` by one sentence in step 2 of the §2a table of added instructions, and no run of this case writes that
table, because the change adds no instruction.

| Model | Check 1 | Words | Cost, USD |
| --- | --- | --- | --- |
| Opus | pass, partial | 1919, 1935 | 1.22, 1.82 |
| Haiku | partial, fail | 1711, 1177 | 0.34, 0.34 |

Opus `instr-1` reaches the 33 minutes from the 20-second wait per attempt: its fault table has a row for a Job whose
Pod is never created, "Each `kubectl logs job/X` waits out the default `--pod-running-timeout=20s` looking for a Pod,
so 90 × 22 s", and the finding asks to "Limit the whole loop to 3 min: a deadline it checks, or
`--pod-running-timeout=2s`", naming the restricted Pod Security Standard or a quota as the cause. Opus `instr-2`
counts the call time without the per-attempt timeout and files it as taste: "The 3-minute bound is 90 × (2 s + an
unbounded `kubectl` call), so a slow API server stretches it with no limit", the check's partial. Its substantive
finding on the loop is the other fault, a `helm test` that exits at once, which it ran with stub `kubectl` and `helm`
("measured 185 s").

Haiku `instr-1` files F2 as substantive: "The loop bounds attempts, not time. It runs 90 times, and each `kubectl logs`
has no request timeout by default", and asks for an elapsed-time bound and `--request-timeout`. It does not name
`--pod-running-timeout` or the 33 minutes: partial. Haiku `instr-2` counts the new loop as "about 3 minutes" and
settles the longest attempt: "`logs -f` in the old code had no timeout either, so the new code is no worse. `none`."

Against the `1b1ebc3e` runs (Opus pass, pass; Haiku fail, partial), Opus `instr-2` moved from pass to partial, and
Haiku `instr-1` from fail to partial and `instr-2` from partial to fail; Opus `instr-1` kept its pass. Opus writes 1919
and 1935 words against 2095 and 2097 and costs 1.22 and 1.82 against 1.66 and 1.53. Haiku writes 1711 and 1177 words
against 1179 and 1357 and costs 0.34 and 0.34 against 0.31 and 0.20.

## The `cond` arm, 2026-10-31: not run

Final-review tree `3d6a0954` conditions the hunk and command rules of item *Claimed cases covered*, the twin-path
paragraph of item *Siblings of the change*, and the analogues of §2a, and changes the report of §4 to an index. This
case's check tests a paragraph of item *Boundaries, partitions, and the negative control* on a code change, which the
tree leaves as it was, and no check reads the report's shape, so its results stand for tree `3d6a0954` without a run.
