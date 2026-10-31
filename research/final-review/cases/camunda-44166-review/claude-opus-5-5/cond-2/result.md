# Final review: `e3250e60..HEAD`, 7 commits, `.github/workflows/docker-build-helm-integration.yml`

**What I could check:**
- **No task statement.** I took the claimed cases from the commit subject lines alone. None of the seven commits has a body.
- **Form used.** The change is configuration only (one GitHub Actions workflow), so I followed §2a and used the configuration analogue under every item.
- **Drift script.** `comment-drift.py` ran and exited 0 but printed nothing, because it does not parse YAML. I read the comments by hand.
- **Lint gates.** `actionlint` and `conftest` are not installed here, so the repository's workflow gates were not run. `yq` is present but I didn't need it.
- **Read-only.** I changed no files and made no commits.

## Item 1: comments consistent with the code and with each other

*Analogue: every statement the file makes about itself or about the target repository.*

- **`:424` "Wait up to 40 min (80 x 30s)"** — **Substantive.** This is false. The job has `timeout-minutes: 20` (`:356`), so the runner kills the job after 20 minutes at most. Steps before the wait also use part of that budget: checkout, token, dispatch and the Vault-backed observe step. The loop's own message "Timed out waiting…" (`:446`) can therefore never print.
  - **Request:** derive one limit from the other (see item 3) and make the comment state the limit that actually applies.
- **`:426` "Grab the first run created after the trigger event"** — **Substantive.** This is false. The runs endpoint returns runs newest first, so `head -n1` picks the most recent run created after `TRIGGER_TIME`, not the first one. On a busy day that is another PR's dispatch (see item 3).
  - **Request:** make the selection match the comment and correlate on something this run owns (item 3). Then reword the comment to say how the run is identified.
- **`:1` description and `:5` name.** Both now say the workflow "triggers SaaS E2E smoke tests". The new job also waits for the result and fails on it. That isn't false, but the `description` is the only summary a reader gets that this job gates on another repository. **Taste.**

## Item 2: claimed cases covered

**Cases claimed by the commit subjects, and what covers each:**

| Claimed case | Source commit | Covered by |
| --- | --- | --- |
| Dispatch SaaS E2E smoke tests from AlwaysGreen | 4662bcd1 | `:376–396`. The only check is this workflow's own PR run, which is triggered by its path filter `:36`. No result of that run is stated. |
| SNAPSHOT component versions | be150d28 "update versions" | `:391–394`. Same check as above. |
| Poll for the downstream conclusion: pass on `success`, fail otherwise, fail on timeout | 7e66e244 | `:413–447`. No run is stated for any of the three outcomes. The timeout outcome cannot happen as written (item 1). |
| Correlate by timestamp | 863daee5 | `:398–400`, `:427–428`. See item 3: the correlation is not tied to this run. |
| Job timeout and `permissions: { }` | 4459b6fc | `:356–357` |
| Lint fixes | e3ff145e, c15b27bf | Quoting only. No gate was run here. |

**Commands the change runs:**
- `curl -X POST …/dispatches` (`:380`) promises that the downstream workflow starts. Nothing checks this, because there is no `--fail`: a 401, 404 or 422 response leaves curl with exit 0, and the step goes green.
- `gh api …/workflows/$WORKFLOW_FILE/runs?event=repository_dispatch&per_page=5` (`:427`) promises to return this run's downstream run. Nothing checks that either. The outcome depends on whether another dispatch of `run-saas-generation-smoke` happens in the same window, which this repository cannot see.

**Unclaimed hunks:**
- **`:84` adds `"slolatte"` to the actor allowlist.** No commit subject claims this. It turns on the whole workflow (image build, Helm deploy to GKE, SaaS dispatch) for that author's PRs. **Substantive.**
  - **Request:** a sentence in the description that claims it, or move it to its own change.
- **`:5` workflow `name` change.** This also changes the `concurrency.group` key (`${{ github.workflow }}-…`, `:46`). Runs in flight under the old name are not cancelled by new pushes during the transition. No other file references the old name (I checked with `git grep`). **Taste:** claim it in the description.

## Item 3: boundaries, partitions, and the negative control

**Limits.** The work has three limits:
- the job's `timeout-minutes: 20` (`:356`), which encloses the others;
- the loop's 80 × 30 s sleep budget (`:424–425`), which is 40 minutes plus API time;
- each `gh api` call, which has no timeout and uses the `gh` default.

The enclosing 20-minute limit fires first even at the defaults, so the inner one never takes effect. If the downstream Playwright SaaS run takes longer than about 18 minutes, this job fails every time, with the runner's generic "exceeded the maximum execution time" message instead of the script's. **Substantive.**
- **Request:** derive one limit from the other. Either set `timeout-minutes` to cover 40 minutes plus setup, or bound the loop by a wall-clock deadline below the job timeout. Then make a run that reaches the timeout and record its duration and output.

**Faults on the new waiting mechanism.**
- **Dispatch rejected.** Examples: the token lacks access, or the `event_type` is unknown. Because curl has no `--fail` (`:380`), the step passes. The loop then finds either no run, or another PR's run (next point). In the first case it ends at the 20-minute job kill with no message saying the dispatch failed. **Substantive.**
  - **Request:** `curl --fail-with-body` (or check the HTTP status), so this fault fails in seconds and prints GitHub's error body.
- **Transient API error.** The default shell is `bash` (`:54–56`), which runs with `-eo pipefail`, and the step also sets `set -e` (`:418`). One transient 5xx or rate-limit error from `gh api` inside `RUN_ID=$(… | head -n1)` therefore ends the step at once, with exit 1 and only gh's error line. A 40-minute poll that fails on one 502 hasn't been accepted anywhere in the change. **Substantive.**
  - **Request:** tolerate per-attempt failures inside the loop (`|| true` and retry), and record a run with an injected failure.

**Partitions of the correlation.** The run is selected only by workflow file, event type and `created_at > TRIGGER_TIME`.
- **Strict comparison at second resolution.** `TRIGGER_TIME` is taken after the curl returns. A downstream run created in the same second is excluded by the strict `>`.
- **Concurrent dispatches.** Two PRs whose jobs overlap, or `workflow_dispatch` runs, each pick the newest run after their own timestamp, which may belong to the other one. A red SaaS run can then fail an unrelated PR, and a green one can pass a broken PR.

The negative control (two concurrent dispatches, each resolving to its own run) is absent. **Substantive.**
- **Request:** correlate on a value this run sends. For example, put `github.run_id` in `client_payload` and have the downstream workflow put it in `run-name`, then match `.display_title`. Alternatively, set `TRIGGER_TIME` before the dispatch and match on `source_sha`.

**State already in place.**
- **Reused image tag.** For PRs the tag is `<maven-version>-pr<N>` (`:226`). It is reused on every push, and `cancel-in-progress` (`:47`) cancels this job but not the downstream SaaS run it already started. That older downstream run can then pull the image tag that the new push has just overwritten. **Taste**, because it depends on the downstream repository's pull timing, which I cannot see.
- **Hard-coded 8.9 target.** A `workflow_dispatch` with `helmRepositoryDirName` set to another minor still dispatches `c8Version: "8.9"` and `…_8_9.yml` (`:389`, `:422`). **Taste:** say in a comment that SaaS is pinned to 8.9.

## Item 3a: level, placement, and the environment

**`Observe build status` is placed before the wait step (`:402–411`), not as the job's last step.** **Substantive.**
- CLAUDE.md requires this step to be last in every job, and every other job in this file follows that.
- Placed here, it reports `job.status` before the only step that can fail on downstream results. CI health metrics record this job as green whenever the dispatch succeeded.

**Request:** move it after "Wait for downstream workflow to finish".

**Other placement checks:**
- `actions/checkout@v4` (`:360`) is needed for the local observe action. It matches its siblings in this file.
- Running the job on `ubuntu-latest` matches the siblings too.
- The gates CLAUDE.md names for workflow changes (`actionlint`, `conftest … --policy .github`) were not run here because they are not installed. The change states no run of either.

## Item 4: names by content, not by position

None. I checked the step names, the job id `trigger-saas-e2e` and the comments. The only positional wording is "first run" at `:426`, which is filed under item 1 as false rather than positional.

## Item 5: the failure report

*Analogue: what the job prints on failure.*

- **Rejected dispatch.** The curl response body is printed but not acted on.
- **Timeout.** The runner's message replaces the script's (item 3).
- **Downstream failure.** The message `Downstream workflow failed: $CONCLUSION` (`:440`) prints the run ID one line earlier but no URL. **Taste:** add `https://github.com/$TARGET_REPO/actions/runs/$RUN_ID` to save the reader a lookup.

I filed nothing further under this item.

## Item 6: what the writer says it verified

No evidence is stated. The commit messages have no bodies, and no PR run, red run or failure-injection run is named for the dispatch, the success path, the failure path or the timeout. The sequence of commits (head-SHA matching, then timestamp matching, then the job timeout) suggests the job was iterated on in CI, but the results are not stated.

## Item 7: siblings of the change

- **Same dispatch pattern elsewhere.** `.github/workflows/trigger-c8run-e2e-tests.yml:43–47` builds the same `curl -X POST …/c8-cross-component-e2e-tests/dispatches` call, also without `--fail`. It does not poll, so the silent-dispatch defect there is only a missing failure, not a 20-minute hang. **Taste:** name it as a follow-up.
- **Set of `job_name` values.** Every other job in this file reports as `docker-build-helm-integration-<job>` (`:95`, `:125`, `:154`, `:183`, `:284`, `:315`). The new job reports as `trigger-saas-e2e` (`:408`), so any metrics view that groups this workflow's jobs by that prefix will miss it. **Taste**, because I cannot see a consumer that filters on the prefix.
  - **Suggestion:** `docker-build-helm-integration-trigger-saas-e2e`.
- **Other pollers of `workflow_runs`.**
  - `zeebe-version-compatibility.yml:42` selects a completed run and does not correlate a dispatch.
  - `preview-env-smoke-test.yml` checks out the target repository and runs Playwright in-process, so it has no polling to compare.
  - `retry-workflow.yml:24` uses `gh run watch` on a known run ID.

  None of the three shares the correlation defect.
- **References to the renamed workflow.** `git grep` finds no other file naming the old workflow name or this file.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "Wait up to 40 min" is false under the 20-minute job timeout | Substantive | `docker-build-helm-integration.yml:424` | 1 |
| "Grab the first run" actually picks the newest run | Substantive | `docker-build-helm-integration.yml:426` | 1 |
| Allowlist entry `slolatte` is not claimed by any commit | Substantive | `docker-build-helm-integration.yml:84` | 2 |
| Workflow rename (which also changes the concurrency group) is not claimed | Taste | `docker-build-helm-integration.yml:5` | 2 |
| Job timeout (20 min) fires before the loop limit (40 min) | Substantive | `docker-build-helm-integration.yml:356` | 3 |
| Rejected dispatch passes silently (curl without `--fail`) | Substantive | `docker-build-helm-integration.yml:380` | 3 |
| One transient `gh api` error ends the 40-minute wait | Substantive | `docker-build-helm-integration.yml:418` | 3 |
| Run correlation is not tied to this run, and there is no concurrent-dispatch control | Substantive | `docker-build-helm-integration.yml:398` | 3 |
| Reused `-pr<N>` tag can be overwritten under a running downstream test | Taste | `docker-build-helm-integration.yml:389` | 3 |
| SaaS target is pinned to 8.9 regardless of `helmRepositoryDirName` | Taste | `docker-build-helm-integration.yml:422` | 3 |
| `Observe build status` runs before the wait and is not the last step | Substantive | `docker-build-helm-integration.yml:402` | 3a |
| Failure message has no downstream run URL | Taste | `docker-build-helm-integration.yml:440` | 5 |
| No PR run or failure-injection evidence is stated | Substantive | (commit messages) | 6 |
| c8run trigger has the same curl without `--fail` | Taste | `trigger-c8run-e2e-tests.yml:43` | 7 |
| `job_name` breaks the file's `docker-build-helm-integration-` prefix | Taste | `docker-build-helm-integration.yml:408` | 7 |

Three checks could not be done: the drift script does not parse YAML, `actionlint` and `conftest` are not installed, and the downstream workflow `playwright_saas_pr_trigger_monorepo_8_9.yml` is in another repository I couldn't read.
