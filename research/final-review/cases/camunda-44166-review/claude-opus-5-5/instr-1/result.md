# Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml`)

The change adds a `trigger-saas-e2e` job. It is a CI configuration, not code, so I filled the form through the §2a analogues and name the analogue under each item. There was no task statement. I took the claimed cases from the commit subjects alone: "add saas e2e smoke tests for alwaysgreen", "update versions", "poll for conclusion", "add timestamp for polling", "add job timeout", and two "fix linting". The drift script ran and printed nothing, because it does not parse YAML. I loaded `english-developer-style`. No doc-comment skill or `test-authoring` rule applies to a workflow file.

The most serious problem is in the polling step: it can wait on another PR's SaaS run and report that run's result as this PR's.

## Item 1: comments consistent with the code and with each other
Analogue used: the comments and `echo` messages in the workflow, checked against what the code does.
- **`:426` "Grab the first run created after the trigger event" is false.** The list-runs API returns runs newest first, so `| head -n1` takes the *newest* run after `TRIGGER_TIME`. If another PR dispatched later, that is the other PR's run.
- **`:424` "Wait up to 40 min (80 x 30s)" is false.** `timeout-minutes: 20` (`:356`) stops the job at 20 minutes. The loop never reaches 40 minutes, and its "Timed out waiting…" message (`:448`) never prints.
- `:1` description and `:5` name: both match the jobs, since `helm-deploy` sets `e2e-enabled: true`. Nothing to report there.

## Item 2: claimed cases covered
Analogue used: each commit claim, matched to the hunk that makes it true and to any run that shows it works.
- "add saas e2e smoke tests" → dispatch step `:376-397`. No run is cited. I cannot check locally that `event_type: run-saas-generation-smoke` starts `playwright_saas_pr_trigger_monorepo_8_9.yml` in the other repository.
- "poll for conclusion" → `:411-449`. No run is cited for any outcome.
- "add timestamp for polling" → `:399-401`. It has the race described under item 3.
- "add job timeout" → `:356`. It conflicts with the 40-minute loop (item 1).
- Commands the change runs, each with its promised outcome:
  - `curl -X POST …/dispatches` should start the downstream run. Nothing runs this command on this configuration. It also has no `--fail`, so a 401, 404 or 422 response still exits 0.
  - `gh api …/runs?event=repository_dispatch&per_page=5` should find this PR's run. Nothing runs it on this configuration.
- Hunks that no commit message claims:
  - **`:84`: adds `"slolatte"` to the actor allowlist.** This widens who triggers the whole pipeline, which now includes the SaaS dispatch.
  - `:359-360`: `actions/checkout` is added in "update versions". It is needed for the local observe action, but the message does not say so.
  - `:357`: `permissions: { }` is added in "add job timeout".
  - `:5`: the workflow is renamed. This also changes the `concurrency.group` key (`:46`).

## Item 3: boundaries, partitions, and the negative control
Analogue used: the states and faults the new job meets, and the limits on it.
- **Other dispatches in the downstream repository.** Every allowlisted PR fires the same `event_type`, and runs of the same downstream workflow can come from elsewhere. The job selects a run by `created_at > TRIGGER_TIME` alone, with no ID that ties the run to this PR. The success or failure of another PR's run then becomes this job's result. I wrote the request in the findings table.
- **Race on the timestamp.** `TRIGGER_TIME` is recorded in a separate step *after* the dispatch, to the second, by the runner's clock. A run created in the same second or earlier, or a few seconds early by clock skew, is filtered out by the strict `>`. The job then waits until it is killed at 20 minutes.
- **Two fault cases, timed:**
  - *The dispatch is rejected* (bad token, or the repository is not in the app's scope): `curl` exits 0 without `--fail`, and the job prints only the "Waiting for…" line. It is killed at 20 minutes. The loop prints nothing on an iteration where `RUN_ID` is empty.
  - *One transient `gh api` error*: under `set -e` and the workflow's `shell: bash` (pipefail is on), the job fails at once, without retrying.

  None of the three `gh api` calls in one iteration has a timeout.
- **Limits:**
  - The loop allows 80 × (30 s + 3 calls), which is more than 40 minutes. The job limit of 20 minutes covers this work, fires first, and leaves the loop's bound with no effect.
  - The GitHub App token is valid for 1 hour. Raising `timeout-minutes` past about 60 minutes would turn polling into 401 errors.
  - `cancel-in-progress` (`:47`) cancels this run on a new push but leaves the downstream SaaS run going. Taste.
- **Outcomes:** success, failure, cancelled, no run found, and timeout. No run is cited for any of them.

## Item 3a: level, placement, and the environment
Analogue used: where the job sits, and whether it passes the repository's own gates.
- `actionlint` and `conftest` are not installed here, so I could not run them. `yq` parses the file. The steps are, in order: checkout, token, dispatch, timestamp, **Observe build status**, wait.
- **The "Observe build status" step is not the last step (`:403`).** It records `job.status` *before* the wait, so a downstream failure or timeout never reaches CI health. This breaks the CLAUDE.md rule that the last step must submit metrics. `conftest-unified-ci-rules.rego:173-179` checks only that the step exists, so the gate does not catch this.
- `needs: format-identifier` (`:355`) is listed, but the job never reads its output. Taste.

## Item 4: names by content, not by position
- `job_name: trigger-saas-e2e` (`:410`) breaks the `docker-build-helm-integration-<job>` prefix that every other job in the file uses (`:95`, `:125`, `:284`, `:315`). The metrics for this job will not group with the rest of the workflow. Taste.
- No ordinal references found.

## Item 5: the failure report
Analogue used: what a failure tells the reader.
- **On failure, the job prints only `$CONCLUSION` (`:442`).** It gives no URL for the downstream run, so the reader has to search another repository to find out why.
- **When no run is found, every iteration is silent.**
- On timeout, the loop's own message is unreachable (see item 1).

## Item 6: what the writer says it verified
None. No commit links a run of the new job or shows any outcome: success, failure, or a run not found.

## Item 7: siblings of the change
- `trigger-c8run-e2e-tests.yml:43-47` has the same `curl -X POST …/dispatches` with no `--fail`. The same silent-success defect applies there. It is a fire-and-forget job, so name it as a follow-up.
- `preview-env-smoke-test.yml` uses the same token action and has no dispatch or poll. The defect does not apply.
- `git grep` finds no reference to the old workflow name, `Docker Build and Helm Integration Test`, anywhere else in the repository.
- Version pins that must move together when `main` moves past 8.9: `"c8Version": "8.9"` (`:388`), `WORKFLOW_FILE=…_8_9.yml` (`:422`), and `camunda-platform-8.9` (`:21`, `:329`). There is no shared variable for them. Taste.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| The poller can pick another dispatch's run (`head -n1` takes the newest run, with no correlation) | Substantive | `:427-428` | Put a unique ID such as `github.run_id` in `client_payload`, have the downstream workflow echo it in `run-name`, and filter on that. Fix the `:426` comment. |
| `TRIGGER_TIME` is taken after the dispatch with a strict `>`, so the run can be missed and the job waits 20 minutes | Substantive | `:399-401`, `:428` | Record the time before the `curl` (with a margin), or rely on the ID above. |
| The job timeout (20 min) is shorter than the loop bound ("40 min"), so the loop's bound and message never take effect | Substantive | `:356`, `:424`, `:448` | Derive one from the other: a loop deadline below the job timeout, and a correct comment. |
| The observe step runs before the wait, so the downstream result is never reported and the step is not last | Substantive | `:403-411` | Move it to after the wait step. |
| `curl` without `--fail`: a rejected dispatch is silent and costs 20 minutes | Substantive | `:380` | Add `--fail-with-body`, and run the job once with a bad token or repository to show it fails fast. |
| A single transient `gh api` error fails the job, and no call has a timeout | Substantive | `:427-431` | Retry each call (for example, `|| true` and continue), and bound each call. |
| No run is cited for any outcome | Substantive | commits | Link runs for success, failure, and no run found. |
| The allowlist entry `slolatte` is not claimed by any commit message | Substantive | `:84` | Claim it in the description, or move it to its own change. |
| The failure message has no URL for the downstream run, and empty polls are silent | Substantive | `:430`, `:442` | Print `html_url`, and print a line on each empty poll. |
| The sibling dispatch in `trigger-c8run-e2e-tests.yml` lacks `--fail` | Substantive | `trigger-c8run-e2e-tests.yml:43` | Name it as a follow-up in the description. |
| `job_name` breaks the file's metrics-name prefix | Taste | `:410` | `docker-build-helm-integration-trigger-saas-e2e` |
| `needs: format-identifier` is not used | Taste | `:355` | Drop it. |
| The checkout, `permissions`, and rename hunks are not claimed by their commit messages | Taste | `:5`, `:357`, `:359` | Mention them in the PR description. |
| The downstream run is not cancelled when this run is cancelled | Taste | `:47` | Accept it, or cancel it in an `if: cancelled()` step. |
| The 8.9 pins are spread across four places | Taste | `:21`, `:329`, `:388`, `:422` | Use one `env` value. |

This review did not run `actionlint` or `conftest` (neither is installed), did not run the workflow, did not inspect the downstream repository, and did not do a style pass over the prose.
