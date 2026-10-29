# Final review: `e3250e60..HEAD` (7 commits, one file: `.github/workflows/docker-build-helm-integration.yml`)

There was no separate task statement, so I took the claimed cases from the seven commit messages alone: "add saas e2e smoke tests for alwaysgreen", "update versions", "poll for conclusion", "add timestamp for polling", "add job timeout", and "fix linting" twice. None of the commits has a body.

The change is a CI workflow with no code members and no tests, so I used the "change with no code" analogues (§2a). I ran the drift script, and it printed nothing, because it does not parse YAML. I loaded `english-developer-style` and `test-authoring`.

## Item 1: comments consistent with the code and with each other
Analogue: what the workflow's comments and messages say about the code next to them.

- **L424, `# Wait up to 40 min (80 x 30s)`, is false.** The job has `timeout-minutes: 20` (L356, added in 4459b6f), so the runner kills the job after about 20 minutes. That 20 minutes also includes the checkout, the token, the dispatch, and the Observe step. Each loop pass also takes longer than 30 s, because it adds up to three `gh api` calls to the sleep.
- **L446, `"Timed out waiting for downstream workflow to complete."`, can never print.** The job timeout fires before the 80 passes finish, so a timeout shows only as a cancelled job.
- **L426, `# Grab the first run created after the trigger event`, is false.** The list endpoint returns runs newest first, so `head -n1` takes the *newest* matching run, not the first one created after the trigger. Item 3 explains why this matters.
- L1 (description) and L5 (name): both match the new job. Nothing to report.

## Item 2: claimed cases covered
Analogue: each claim, against the step that makes it true, with run evidence where one is owed.

| Claim | Where | Evidence |
|---|---|---|
| Trigger SaaS E2E smoke tests | L376–396 `repository_dispatch` | No run linked |
| Update versions (SNAPSHOT payload) | L391–394 | No run linked; whether the target accepts `SNAPSHOT` / `8-SNAPSHOT` is a fact about the other repository |
| Poll for conclusion | L413–447 | No run linked |
| Timestamp for polling | L398–400, L428 | No run linked; it also has a race (Item 3) |
| Job timeout | L356 | It contradicts the 40-minute loop (Item 3) |
| Fix linting | L400, L431–432 quoting | `shellcheck` on the extracted wait script is clean. `actionlint` and `conftest` are not installed here, so I could not run them |

Commands the change runs:
- `curl -X POST …/dispatches` (L380): this is the same form as `trigger-c8run-e2e-tests.yml:43`, which does run.
- `gh api …/actions/workflows/playwright_saas_pr_trigger_monorepo_8_9.yml/runs?event=repository_dispatch` (L427): nothing in this repository runs this form. Its result depends on whether that workflow file exists in `camunda/c8-cross-component-e2e-tests`, and on whether that workflow listens for `event_type: run-saas-generation-smoke`. If either is wrong, the loop never finds a run and the job dies at the 20-minute timeout with no message. **Request:** a link to a green run of this job, plus one where the downstream run failed.

Hunks that no commit sentence claims:
- **L84: `"slolatte"` added to the actor allowlist.** This lets the workflow run on the author's own PRs. It may be scaffolding for testing that was not meant to be merged.
- L359–360: the `Checkout repository` step arrived in "ci: update versions". The local `observe-build-status` action needs it, but the message says something else.
- L357: `permissions: { }` arrived in "ci: add job timeout".
- L5: the workflow rename. "add saas e2e smoke tests" covers this loosely.

## Item 3: boundaries, partitions, and the negative control

**Limits.** Two limits bound the same wait: the job's `timeout-minutes: 20` (L356), which encloses the loop's own 80 × 30 s budget (L425). The job limit always fires first, so the loop's 40 minutes never take effect. That is a finding. Any SaaS smoke run that takes longer than about 18 minutes to finish after dispatch shows up as a cancelled job, even if the tests pass. **Request:** derive one limit from the other. Either set the job timeout to the loop budget plus setup and slack, or compute the number of passes from a deadline that fits inside the job timeout.

**Faults of the new waiting mechanism.** None of the `gh api` calls sets a timeout, so I counted each one as possibly never returning.

1. **The dispatch is rejected** (403/404/422: wrong app scope, wrong `event_type`). `curl` has no `--fail`, so the step stays green and the log shows only the JSON error body. The loop then finds no run, and the job is cancelled after 20 minutes. A fault that could fail in seconds with the HTTP status instead takes 20 minutes and reports "cancelled". **Request:** `curl --fail-with-body` (or `-f`), plus a deadline-based message before the job timeout.
2. **No matching run, caused by the timestamp race.** `TRIGGER_TIME` is taken *after* the POST (L398 comes after L376). GitHub's `created_at` has one-second resolution, and the comparison is a strict `>`. A run created in the same second as the `date` call, or before it, is never matched, and the outcome is the 20-minute cancel described above. **Request:** take the timestamp before the dispatch, and compare with `>=`.
3. **A different PR's run gets picked.** Several allowlisted PRs can dispatch in the same window. The query keeps every run with `created_at` after this job's trigger time, and `head -n1` takes the newest, which can belong to another PR. The query can also move to a newer run on a later pass. This PR's job can then go green or red on someone else's image. Nothing ties the run to this dispatch, such as `source_sha` or the image tag in the run name. **Request:** correlate on a value from the payload, for example a `run-name` in the downstream workflow that includes `zeebeVersion` or a dispatch id. Failing that, record the run id once and stop re-querying.
4. **A transient API error.** The default shell is `bash -eo pipefail` (L54–56), so one failing `gh api` call in L427, L431, or L432 ends the job immediately. The job is then reported as failed, with no word about the downstream result. **Request:** tolerate per-pass errors (`|| true`) and keep the deadline as the only way the wait gives up.

**Partitions of inputs that reach the new consumer.** On `workflow_dispatch`, the existing inputs `version` and `helmRepositoryDirName` now reach the SaaS dispatch. But `c8Version: "8.9"` (L389) and `WORKFLOW_FILE …_8_9.yml` (L422) are hard-coded. So a dispatch run with `helmRepositoryDirName: camunda-platform-8.8` tests the Helm side on 8.8 and the SaaS side on 8.9. **Request:** derive the minor version in one place, or state in the workflow that the SaaS leg is 8.9-only.

**Cancellation partition.** `cancel-in-progress: true` (L47) cancels this job on a new push, but the downstream SaaS run keeps going. That is not a correctness defect for this repository; I note it for cost.

## Item 3a: level, placement, and the environment
Analogue: placement and the repository's own gate.

- **The `Observe build status` step (L402) is not the last step.** The Wait step comes after it, at L413. CLAUDE.md requires the Observe step to be the last step of every job. As written, CI health records the job status *before* the downstream wait, so failed and timed-out SaaS runs are never recorded. **Request:** move it to the end.
- `needs: format-identifier` (L355): the job never uses that output. This is taste.
- I could not run `actionlint` or `conftest` locally. As far as I can read it, the conftest `job_name` rule applies only to matrix jobs, so this job passes it.

## Item 4: names by content, not by position
None. Step names, the job id, and the variables (`TARGET_REPO`, `WORKFLOW_FILE`, `TRIGGER_TIME`) all name what they hold. The loop variable is `_`.

## Item 5: the failure report
Analogue: what the job prints when it fails.

- **L439, `Downstream workflow failed: $CONCLUSION`, prints no link to the run.** The person reading this repository's log has to hunt for the run in the other repository. **Request:** print `https://github.com/$TARGET_REPO/actions/runs/$RUN_ID` when the run is found and again on failure.
- The faults from Item 3 (dispatch rejected, no match, timeout) never print anything of their own; GitHub reports only that the job was cancelled at its time limit.

## Item 6: what the writer says it verified
Nothing is stated. No commit links a run of the new job: not a green run, not one where the downstream run failed, not one where the dispatch was rejected.

## Item 7: siblings of the change

- **Callers of the same mechanism:**
  - `trigger-c8run-e2e-tests.yml:43` uses the same `curl` without `--fail`. It does not wait, so it has neither the race nor the timeout, but it hides a rejected dispatch in the same way. The fix belongs in the same change or a named follow-up.
  - `preview-env-smoke-test.yml` checks out the E2E repository and runs the tests itself, so none of these defects apply to it.
- **Sibling job name in the set:** every other `job_name` in this file has the prefix `docker-build-helm-integration-`. The new one is `trigger-saas-e2e` (L408). This is taste: any CI-health query that filters on the prefix would miss it.
- **References to the renamed workflow:** `git grep` finds no reference in the repository to the old name "Docker Build and Helm Integration Test". Required-check settings outside the repository are not visible.

## Findings

| # | Finding | Label | File:line | Request |
|---|---|---|---|---|
| 1 | The 20-minute job timeout cuts off the 40-minute loop, so the loop budget, its comment, and its timeout message are all dead code | Substantive | `docker-build-helm-integration.yml:356,424,446` | Derive one limit from the other; fix the comment |
| 2 | The Observe step sits before the Wait step, so CI health never records the downstream result | Substantive | :402–411 | Move it to the last step |
| 3 | The run lookup picks the newest matching run, which can be another PR's | Substantive | :426–428 | Correlate on a payload value or `run-name`; fix the comment |
| 4 | `TRIGGER_TIME` is taken after the dispatch and compared with strict `>` at one-second resolution, so a run can be missed | Substantive | :398–400, :428 | Take it before the POST; use `>=` |
| 5 | `curl` without `--fail`: a rejected dispatch passes, and the job dies 20 minutes later with no message | Substantive | :380 | `--fail-with-body` |
| 6 | Under `pipefail`, one transient `gh api` error fails the whole wait | Substantive | :427–432 | Tolerate per-pass errors; bound only by the deadline |
| 7 | `c8Version` and the workflow file are hard-coded to 8.9, while the dispatch inputs allow another Helm minor version | Substantive | :389, :422 | Single source, or state that the SaaS leg is 8.9-only |
| 8 | Unclaimed hunks: author added to the allowlist, plus checkout and permissions slipped into unrelated commits | Substantive | :84, :359, :357 | A sentence that claims each one, or remove the allowlist entry |
| 9 | No run evidence linked for the dispatch or for the downstream workflow and event type | Substantive | :376–447 | Link a green run and a run where the downstream failed |
| 10 | The failure message has no link to the downstream run | Substantive | :433, :439 | Print the run URL |
| 11 | `trigger-c8run-e2e-tests.yml` has the same `curl` without `--fail` | Substantive | `trigger-c8run-e2e-tests.yml:43` | Fix it here or name it as follow-up |
| 12 | `job_name` breaks the file's `docker-build-helm-integration-` prefix | Taste | :408 | Rename to `docker-build-helm-integration-trigger-saas-e2e` |
| 13 | Unused `needs: format-identifier` | Taste | :355 | Drop it |

This review did not run `actionlint` or `conftest` (neither is installed here) or the workflow itself. It did not read `camunda/c8-cross-component-e2e-tests`, so nothing here confirms its workflow file name, its `event_type`, or the payload fields it accepts. It also did not do a style-only pass over the prose.
