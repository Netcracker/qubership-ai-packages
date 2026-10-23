## Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml`)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages: "add saas e2e smoke tests for alwaysgreen", "update versions", "poll for conclusion", "add timestamp for polling", "fix linting" (twice), and "add job timeout". They are terse, so item 2 is thin. No previous report exists, so there is no §4 table. The drift script ran and printed nothing, because it parses code files and not YAML. I read the whole file, and for the no-code analogues I used the `english-developer-style` skill and §7 of `test-authoring`. The `observe-build-status` action's inputs were read directly.

**Checks run.** `yq` parses the file; `shellcheck` on the extracted "Wait" script is clean (copy in the scratchpad). `actionlint` and `conftest` are not installed, so the repository's required gates were not run.

### Item 1: comments consistent with the code and each other
- Line 424, `# Wait up to 40 min (80 x 30s)`: true of the loop, false of the job. The job is capped at `timeout-minutes: 20` (line 356). See F1.
- Header (line 1), "runs Helm integration and E2E tests": holds, since `helm-deploy` sets `e2e-enabled: true`.
- Line 426, "Grab the first run created after the trigger event": matches the code, which is also the source of F5.

### Item 2: claimed cases covered
- "add job timeout": the 20-minute cap contradicts the 40-minute wait it was meant to bound. F1.
- "poll for conclusion" and "add timestamp for polling": the success, failure, still-running, and timeout branches have no test or run in the change. The writer states no run of the new job.
- "update versions": the payload moved from `8.9.0-alpha3` to `SNAPSHOT` and `8-SNAPSHOT`. The downstream repo's expectation can't be checked here.
- Not named in any message: the `slolatte` allowlist entry (added in 4662bcd1), the `Checkout` step (added in be150d28), and the workflow rename. F7 and T2.

### Item 3: boundaries, partitions, negative control
- none (not applicable as a test partition). The wait loop has no test for zero runs found, a run still in progress, a failed conclusion, or the timeout. The only run that exercises this is a real CI run, which the writer does not state.
- Pre-existing state: none. The change writes no state an earlier version left behind.

### Item 3a: level, placement, environment
- No smaller level can observe this: the behavior is across the GitHub API boundary. The in-process test is not owed, but the change has no run that exercises the new job. The downstream `playwright_saas_pr_trigger_monorepo_8_9.yml` and its `run-saas-generation-smoke` trigger live in another repo and were not checked.

### Item 4: names by content
- none. No ordinals or positional names in the change.

### Item 5: failure report
- F6: the timeout message "Timed out waiting for downstream workflow to complete." does not say whether no run was ever found or the last run was still in progress. `test-authoring` §7 asks a wait to name what it waited for and its last state.
- The "failed" and "Downstream workflow failed: $CONCLUSION" messages are fine.
- The dispatch's HTTP failure is silent (F3), so a rejected dispatch also reads as a timeout.

### Item 6: what the writer says it verified
- No evidence is stated: no red run, no successful run of the new job, no `actionlint` or `conftest` output in the messages. "fix linting" is claimed twice without output. The gate could not be run here.

### Item 7: siblings
- `trigger-c8run-e2e-tests.yml:43-47` uses the same `curl` dispatch without `--fail`. The defect applies there too (F3).
- Every other job in this file ends with the `Observe build status` step. `trigger-saas-e2e` does not (F2), and the repo rule in CLAUDE.md requires the last step to be that observe step.
- The `should-run` allowlist gates every job. The new job has no `if:` of its own, but `needs` on `build-and-push` makes it skip whenever the gate skips. No problem found there.

### Findings

| # | Label | File and line | Finding | Requested change |
|---|---|---|---|---|
| F1 | substantive | `.github/workflows/docker-build-helm-integration.yml:356`, `:424` | `timeout-minutes: 20` cancels the job before the 40-minute loop can finish. The job reports a timeout while the downstream run may still pass, and the comment is false. | Set the timeout above the loop plus the other steps (for example 50), or shorten the loop to fit, and correct the comment. |
| F2 | substantive | `:402-411` | The `Observe build status` step runs before the wait, so it records the dispatch outcome, not the E2E outcome. It also breaks the CLAUDE.md rule that the last step submits the health metrics. | Move the observe step after the wait step, keeping `if: always()`. |
| F3 | substantive | `:380-396`; sibling `trigger-c8run-e2e-tests.yml:43-47` | `curl` without `--fail` treats a rejected dispatch (401, 404, 422) as success. The wait then times out with no cause. | Use `curl --fail-with-body` or check the HTTP code in both places. Fix the sibling here or name it as follow-up. |
| F4 | substantive | `:398-400` | The trigger timestamp is taken after the dispatch. A downstream run created before the timestamp is filtered out, and the loop waits for a run that already happened. | Take the timestamp before the `curl`. |
| F5 | substantive | `:427-428` | Matching only by creation time can adopt another dispatch's run when two PRs trigger together. The run also is not matched to `source_sha`. I could not check the downstream run name here. | Have the downstream run expose `source_sha` (for example in its run name) and match on it, or state the concurrency risk in the commit. |
| F6 | substantive | `:446-447` | The timeout message does not distinguish "no run appeared" from "still in progress". | Print the last `RUN_ID` and `STATUS`, or "no run created after $TRIGGER_TIME". |
| F7 | substantive | `:84` (added in 4662bcd1) | `slolatte` was added to the actor allowlist that gates every job, including the one using Vault secrets. No commit message names it. | Name it in the commit message, or confirm it is intended and document it. |
| T1 | taste | `:95`, `:408` | Every other job's `job_name` carries the `docker-build-helm-integration-` prefix; `trigger-saas-e2e` does not. Preferred: add the prefix. | Expect this may be declined. |
| T2 | taste | `:359-362`, `:1-5` | The `Checkout` step (be150d28) and the workflow rename are not named in any commit message. Preferred: name them. | Expect this may be declined. |

**Not checked:** I did not run actionlint or conftest, since neither is installed. I did not confirm the downstream repo's workflow, its `run-saas-generation-smoke` trigger, its run naming, or whether `SNAPSHOT` / `8-SNAPSHOT` are the right values. No CI run was made.
