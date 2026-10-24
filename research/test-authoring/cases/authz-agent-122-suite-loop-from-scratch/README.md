# Case: write the tests qubership-authz-agent#122 owes for the loop that waits for the suite

A regression case for `test-authoring` on a change that replaces a mechanism: a Makefile recipe that waits for a
Kubernetes Job. The cases so far test compilers, a validator, and a service client, where nothing waits for a fault.
The input is one commit of [Netcracker/qubership-authz-agent#122][pr], `f3b64e02` on top of `5dcb6be8`, which the
pull request later rewrote; the run fetches both by sha.

Before the commit, `run-suite` started `helm test` in the background, waited for the Job with
`kubectl wait --for=create job/<name> --timeout=2m`, polled `kubectl logs job/<name>` up to 90 times with a 2-second
sleep, then streamed the log with `kubectl logs -f` and waited for `helm test`. A suite container that never started,
for example on `ErrImageNeverPull`, held the target until `helm test`'s 15-minute timeout. The commit drops the
`kubectl wait`, and when the 90 attempts fail it prints `The <job> container did not start within 3 minutes:` and the
Pod, and stops `helm test`. Its message promises that the targets "fail after about three minutes".

The reviewer's next round found that the three minutes were 90 attempts, not a deadline ([comment][c-loop]). While the
Job exists and has no Pod, for example when a ResourceQuota or an admission webhook refuses it, each
`kubectl logs job/<name>` waits up to kubectl's default `--pod-running-timeout` of 20 seconds, so the loop takes about
90 × 22 s, roughly 33 minutes: past the `helm test` timeout and the CI job's 30 minutes. The pull request then bounded
the loop by a deadline and passed `--pod-running-timeout=2s`.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[c-loop]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4359760444

## What it exercises

- **The two faults of a replaced mechanism** (§3, the paragraph on a change that replaces a mechanism). The fault the
  old recipe met most often is a container that does not start while its Pod exists; the fault on which one attempt
  waits longest is a Job with no Pod. Only the second shows the 33 minutes.
- **The count of a loop's time to fail** (§3). A loop bounded by 90 attempts takes 90 times the longest attempt plus
  the sleep, and the longest attempt is a default timeout that no flag in the Makefile shows.
- **A test of the give-up path that does not wait** (§3, §8). The recipe takes kubectl and helm as Make variables, so a
  test can pass fakes and a `sleep` that returns at once, and assert that the target exits non-zero after its attempts,
  prints the message and the Pod, and stops `helm test`.

The repository has no test of a Makefile target, and there is no cluster in the run, so the writer chooses the form of
the test and states the runs it could not make.

## Checks

Read `result.diff` and `result-note.md` against all of them.

1. **Both faults are named** (§3). Pass: the note or a test names a suite container that does not start while its Pod
   exists (a missing image, `ErrImageNeverPull`, a failing pull) and a Job that has no Pod (a quota, an admission
   refusal, a Pod that is never created). Partial: only the first. Fail: neither.
2. **The time to fail is counted with each call's own timeout** (§3). Pass: the note says that with no Pod each
   `kubectl logs job/<name>` can wait kubectl's default `--pod-running-timeout` of 20 seconds, so the loop runs far past
   three minutes (about 33), and that the commit's "about three minutes" is wrong for that fault. Partial: the 20 s
   wait named without the total, or the total with no source for the per-attempt wait. Fail: the note repeats three
   minutes as the bound, or says nothing about the loop's duration.
3. **The old and the new mechanism are compared on a fault** (§3). Pass: for the container that does not start, the
   note states that the old recipe waited out `helm test`'s timeout (15 minutes, `E2E_SUITE_TIMEOUT`) and the new one
   stops after about three minutes, with what each prints. Partial: both durations without the old output, the
   comparison made on the Job with no Pod alone, or only the new duration. Fail: no comparison.
4. **A remedy for the loop, proposed and not applied** (§3). Pass: the note proposes a deadline over the whole loop,
   alone or with a short `--pod-running-timeout`, and the Makefile is unchanged. Partial: a short
   `--pod-running-timeout` alone, which still leaves 90 attempts. Fail: no remedy for the loop's duration, or a remedy
   applied to the Makefile.
5. **A test of the give-up path that controls time** (§3, §8). Pass: a test runs `run-suite` (through `make e2e-suite`
   or `make parity-suite` with `E2E_KUBECTL`, `E2E_HELM`, or `PATH` pointing at fakes) with a `kubectl logs` that always
   fails, does not sleep for real (a fake `sleep` on `PATH`, or the attempts counted), and asserts the non-zero exit,
   the message, and that `helm test` was stopped. Partial: the test sleeps for real, or asserts the exit alone. Fail:
   no test of the give-up path, or a test that asserts a wall-clock duration; a bound on a clock the test controls
   passes.
6. **The production code is unchanged.** The first part of `result.diff` is empty, and no `AGENTS.md` or `CLAUDE.md`
   is edited.
7. **Green on the fix, red on the base** (§1). Read `result-build.txt`: on the base a failure for the test of check 5,
   since the old recipe prints no such message and does not stop `helm test`, and no failure on the fix. A test that
   fails on the fix passes this check only where it asserts the bound the commit promises on a Job with no Pod, and
   the note reports the failure as the commit's defect.

## Skill parts

- `SKILL.md`: §0, §1, §3, §8, §10, §11

## How to run

From the repository root:

```bash
research/test-authoring/cases/run-case.sh research/test-authoring/cases/authz-agent-122-suite-loop-from-scratch <model> [<rev>]
```

`build.sh` runs every test file the session added or changed: a Bats file with `bats`, a shell script under `test/`
whose name starts with `test` with `bash`, and a Go test file with `go test`, ten minutes each.

## Results, 2026-10-24

Opus, two runs per arm, graded against every check by reading. `rule` ran test-authoring at skill tree `2c84a74`, with
the paragraph on a replaced mechanism as committed; `control` ran it at `e7a22de`, from `main` before that paragraph.
`claude-opus-5-5/` holds `rule-2`, and `arms/` the other three runs.

| Arm | Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rule` | 1 | pass | pass | pass | pass | pass | pass | pass | 1.45 |
| `rule` | 2 | pass | pass | pass | partial | pass | pass | pass | 1.58 |
| `control` | 1 | partial | fail | partial | fail | pass | pass | pass | 1.80 |
| `control` | 2 | partial | fail | partial | fail | pass | pass | pass | 1.29 |

- **`control`.** Both runs test only the container that does not start and repeat three minutes as the bound: "At the
  defaults, the polling adds up to 180 s" (`control-1`), "the new 3-minute limit fires before helm's timeout"
  (`control-2`). Neither names `--pod-running-timeout`, and both propose only leaving the loop once `helm test` has
  exited. Both add a step to the CI workflow that the task did not ask for.
- **`rule`.** Both runs name the Job with no Pod, take the 20 seconds from `kubectl logs --help`, count about 33
  minutes against the commit's "about three minutes", leave the Makefile alone, and test the give-up path with a fake
  `sleep`. `rule-1` proposes a deadline over the loop and a short `--pod-running-timeout`, and tests the Job with no
  Pod against three minutes plus one attempt and one sleep, so that test fails on the fix, which its note reports as
  the commit's defect. `rule-2` proposes a short `--pod-running-timeout` and leaving the loop once `helm test` has
  exited, with no deadline over the loop (check 4), and adds a CI step.
- Two earlier `rule` runs, on a wording that still stated the loop arithmetic and a sentence on the test of the fault,
  graded the same on checks 1, 2, and 4.
