# Final review of `e3250e60..HEAD`: seven `ci:` commits to `.github/workflows/docker-build-helm-integration.yml`

**Inputs.** There was no task statement, so the claimed cases come only from the seven commit messages, and those are one line each. The change is a workflow configuration with no code, so I used the §2a analogues. The skills loaded were `english-developer-style` and `test-authoring`. I ran the drift script (`comment-drift.py e3250e60… HEAD`) and it printed nothing, because it does not parse YAML. `yq` parses the file. `actionlint` and `conftest` are not installed here, so the CLAUDE.md lint gate was not run.

## Item 1: comments consistent with the code and with each other
Analogue used: the comments, the step names, the workflow name and description, each checked against what the code does.

- **`:424` "Wait up to 40 min (80 x 30s)" is false.** The job limit added in 4459b6fc, `timeout-minutes: 20` at `:356`, cancels the job after 20 minutes. That 20 minutes also includes checkout, token generation and the dispatch. Each loop pass also runs up to three `gh api` calls on top of the 30 s sleep, so even without the job limit the loop runs longer than 40 minutes. A reader who trusts the comment will expect a downstream run of 25 minutes to pass. Request: make the comment and the loop bound follow from the job timeout (see Item 3).
- **`:426` "Grab the first run created after the trigger event" is false in two ways.** The list endpoint returns runs newest first, so `head -n1` picks the *most recent* run after `TRIGGER_TIME`, not the first. Nothing ties that run to this dispatch either: another PR's dispatch in the same window matches the filter. The query also runs again on every pass, so `RUN_ID` can switch to a newer run partway through the wait. Request: correlate on the payload. For example, have the downstream workflow put `source_sha` or a unique id into its `run-name` and select on `.display_title`, or at least fix `RUN_ID` once it is found. Then make the comment say what is selected.
- Taste: the `:1` description says the workflow "triggers SaaS E2E smoke tests". The job also waits for those tests and fails on their result, which "runs" or "waits for" would say.
- No coined terms. "SaaS Monorepo" matches the downstream workflow file name `playwright_saas_pr_trigger_monorepo_8_9`.

## Item 2: claimed cases covered
Taken from the commit messages only.

| Claim | Where it is handled |
| --- | --- |
| "add saas e2e smoke tests for alwaysgreen" | `trigger-saas-e2e` job, `:352–447` |
| "update versions" | payload versions `:391–394` |
| "poll for conclusion" | wait step `:413–447` |
| "add timestamp for polling" | `:398–400`, `:416`, `:428` |
| "fix linting" (two commits) | variable quoting `:400`, `:431–432`, and `i` changed to `_`. Not verified: actionlint is unavailable here |
| "add job timeout" | `:356`, which contradicts `:424` (Item 1) and the loop (Item 3) |

The change adds no commands for anyone to run.

**Unclaimed hunk: `:84` adds `"slolatte"` to the `should-run` actor allowlist.** That list decides who triggers the whole workflow on a PR: the Harbor push, the GKE deploy, and now the SaaS dispatch. No commit message mentions it. Request: a sentence in the description that claims it, or move it to its own change.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the faults the new job will meet, and the limits that apply to it.

- **The limits contradict each other.** The loop's own bound (80 passes, at least 40 min) sits inside the job limit (20 min, `:356`), so the job limit always fires first. The script's message "Timed out waiting for downstream workflow to complete." can never print. The job ends `cancelled` with GitHub's generic "exceeded the maximum execution time" message. If the SaaS smoke run takes longer than about 19 minutes, every run of this job goes red. The repository does not say how long that downstream workflow takes. Request: derive one limit from the other, with a loop deadline below `timeout-minutes` that covers the last attempt plus one sleep. Also give the line or run that shows how long the downstream workflow takes.
- **A rejected dispatch is silent and takes 20 minutes to show.** At `:380`, `curl` runs without `--fail`. A 401, 403, 404 or 422 from `/dispatches` exits 0, and the step is green. The wait loop then finds no run, and it prints nothing on a pass with an empty `RUN_ID`. So the log shows one "Waiting for…" line and then a cancellation 20 minutes later, with nothing that points at the dispatch. Request: `curl --fail-with-body` (or `gh api -X POST`), and an echo on each pass with no run found. Then do a run with a bad event type or token to show the fault fails fast.
- **Race on the timestamp.** `TRIGGER_TIME` is taken in a *separate step after* the dispatch (`:398–400`), with one-second resolution, and compared with a strict `>` (`:428`). A run that GitHub creates before that step starts, or within the same second, is never matched. That hits the same 20-minute silent cancellation. Request: take the timestamp *before* the `curl`, in the same step, and compare with `>=`.
- **No partition for a different version.** `workflow_dispatch` lets a caller pick `helmRepositoryDirName` (for example `camunda-platform-8.8`). The SaaS trigger still sends `c8Version: "8.9"` and polls `…_8_9.yml`. Taste: derive both from an input, or document that SaaS covers 8.9 only.
- Taste: `set -e` together with the default `pipefail` (`defaults.run.shell: bash`) means one transient `gh api` error (a 5xx or a rate limit) fails the whole wait. A retry on those errors, or `|| true` with a count of failures, would keep a flaky API from turning AlwaysGreen red.
- Taste: `cancel-in-progress` (`:47`) cancels this job on a new push, but it leaves the downstream SaaS run running.

## Item 3a: level, placement, and the environment
Analogue used: where each rule lives, layout against sibling jobs, the repository's lint gate.

- **The "Observe build status" step at `:402` is not the job's last step.** CLAUDE.md says the metrics step must be the last step of each job. Here it runs before "Wait for downstream workflow to finish". `job.status` is recorded before the wait, so a downstream failure or a timeout never reaches the CI health metrics, and the job is reported green there. Request: move the step to the end of the job.
- The gate (actionlint and `conftest test --rego-version v0 -o github --policy .github`) could not be run, because neither tool is installed. The layout otherwise matches the sibling jobs: `permissions: { }`, `timeout-minutes`, Vault-sourced secrets.
- Taste: `needs: format-identifier` (`:355`) is unused, because the job reads no output of `format-identifier`.

## Item 4: names by content, not by position
None. I checked the step names, the job id and the comments. The one ordinal, "first run" at `:426`, is already filed under Item 1.

## Item 5: the failure report
Analogue used: what the job prints when it fails.

- The silent passes with no run and the cancellation on timeout are filed under Item 3.
- Taste: on a downstream failure, `:439` prints only the run id and the conclusion. Printing `.html_url` would let the reader open the failed run directly.

## Item 6: what the writer says it verified
None stated. No commit gives a run where the job went green after a real downstream success, or red after a real downstream failure. Nor does any commit show the job matching the run its own dispatch created.

## Item 7: siblings of the change
- **`job_name` breaks the file's naming pattern.** All six other jobs in the file use `docker-build-helm-integration-<suffix>` (for example `:95`, `:284`). The new job uses `trigger-saas-e2e` (`:408`), so its metrics are not grouped with this workflow's. Request: `docker-build-helm-integration-trigger-saas-e2e`.
- `.github/workflows/trigger-c8run-e2e-tests.yml:43` has the same `curl` without `--fail`, so a rejected dispatch there also ends green with nothing dispatched. Request: fix it in the same change, or name it as follow-up in the description.
- The actor allowlist exists only in this file, so no other list needed the new member.
- The old workflow name "Docker Build and Helm Integration Test" was used only in this file at the base, so nothing else depends on it.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "Wait up to 40 min" is false with `timeout-minutes: 20` | Substantive | `docker-build-helm-integration.yml:424` | 1 |
| "first run created after" picks the newest run, not tied to this dispatch | Substantive | `:426–428` | 1 |
| Actor allowlist addition `slolatte` not claimed | Substantive | `:84` | 2 |
| Job limit (20 min) fires before the loop bound (≥40 min) | Substantive | `:356`, `:425` | 3 |
| `curl` without `--fail`, so a rejected dispatch waits 20 min silently | Substantive | `:380` | 3 |
| Timestamp taken after dispatch and compared with strict `>`, so the run can be missed | Substantive | `:398–400`, `:428` | 3 |
| Observe-build-status step not last, so the wait outcome is never recorded | Substantive | `:402` | 3a |
| `job_name` breaks the `docker-build-helm-integration-*` pattern | Substantive | `:408` | 7 |
| Same unchecked `curl` dispatch in the c8run sibling | Substantive | `trigger-c8run-e2e-tests.yml:43` | 7 |
| Description says "triggers" for a job that also waits and gates | Taste | `:1` | 1 |
| SaaS version hardcoded to 8.9 while the Helm dir is an input | Taste | `:389`, `:422` | 3 |
| `set -e` fails the whole wait on one transient API error | Taste | `:418` | 3 |
| Cancelling this run leaves the downstream run running | Taste | `:47` | 3 |
| Unused `needs: format-identifier` | Taste | `:355` | 3a |
| Failure message lacks the downstream run URL | Taste | `:439` | 5 |

I could not run `actionlint` or `conftest` because neither is installed, and the drift script does not parse YAML, so it listed nothing.
