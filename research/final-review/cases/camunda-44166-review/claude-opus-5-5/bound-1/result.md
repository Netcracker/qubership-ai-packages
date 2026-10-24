# Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml` only)

**Inputs.** I had no task statement, so the claimed cases come only from the seven commit subjects: "add saas e2e smoke tests for alwaysgreen", "update versions", "poll for conclusion", "add timestamp for polling", "add job timeout", and two "fix linting". None of the commits has a body.

**How I filled the form.** The change is a CI workflow with no code members, so I used the configuration analogues from §2a. I ran `comment-drift.py e3250e60… HEAD` and it printed nothing, because it does not parse YAML. I loaded `english-developer-style` (§7 commit messages, §7 error and log messages) and `test-authoring` (§7 failure report, §10 what needs a run). `actionlint` and `conftest` are not installed here, so neither was run. `yaml.safe_load` parses the file, and the new job's step order is: checkout, token, dispatch, timestamp, Observe build status, wait. There is no previous report.

## Item 1: comments consistent with the code and with each other
**Analogue used:** the statements the file makes about itself and about the other repository.

- **`# Wait up to 40 min (80 x 30s)` (line 424) is false.** The job sets `timeout-minutes: 20` (line 356), and that budget also covers checkout, the token step and the dispatch. The job is killed after about 38 iterations, so the loop never reaches 40 minutes. A reader who tunes the loop will expect 40 minutes.
- **`# Grab the first run created after the trigger event` (line 426) does not match the code.** The runs endpoint returns runs newest first, so `head -n1` picks the *most recent* run after `TRIGGER_TIME`, not the first one. See Item 3 for why this matters.
- **The header `# description:` (line 1) and the new `name:` are consistent with the jobs.** "Helm integration and E2E tests" matches `test-enabled`/`e2e-enabled: true`, and "SaaS E2E smoke tests" matches the new job.

## Item 2: claimed cases covered

| Claimed case | Where it is handled |
|---|---|
| Add SaaS E2E smoke tests for AlwaysGreen | job `trigger-saas-e2e`, dispatch step (lines 376–396) |
| Update versions | `client_payload` `*Version` fields (lines 389–394) |
| Poll for conclusion | wait step (lines 413–447) |
| Timestamp for polling | `trigger-time` step (lines 398–400) and `select(.created_at > …)` |
| Job timeout | `timeout-minutes: 20` (line 356) |
| Fix linting | quoting of `$GITHUB_OUTPUT` / `"$RUN_ID"`, `for _ in` |

**Commands the change tells someone to run:** none. The `curl` and `gh api` calls run in CI themselves, and no commit, page or comment names a run of the new job.

**Reading the other way, two hunks are claimed by no sentence:**
- **`"slolatte"` added to the `should-run` actor allowlist (line 84).** This widens who triggers the whole workflow, including Harbor pushes and GKE deploys, and no commit message mentions it.
- **The workflow `name:` change (line 5).** It also changes `github.workflow`, which is the concurrency group key on line 46. Nothing else in the repo references either name (checked with `git grep`), so the effect is limited to that rename of the group.

## Item 3: boundaries, partitions, and the negative control

**Limits.**
- The wait loop's own budget is ≥ 40 min. It sits inside the job's 20 min, and the job timeout fires first.
- When it fires, the script's `Timed out waiting…` line is never printed. The run ends with GitHub's generic "exceeded the maximum execution time".
- The downstream workflow's own run time lives in another repository and is not stated anywhere. Nothing shows that the SaaS smoke run finishes inside the remaining roughly 19 minutes.
- **Request:** derive the loop bound from the job timeout, or the other way round. Also state, or link a run showing, how long the downstream workflow takes.

**Run correlation (partition: concurrent PRs).**
- Every PR's run dispatches the same `event_type` to the same downstream workflow. The poll then takes the newest `repository_dispatch` run created after its own `TRIGGER_TIME`, with no link to `source_sha`.
- With two PRs in flight, PR A's job can adopt PR B's downstream run and report B's result as A's.
- `per_page=5` also lets the PR's own run drop out of the window when more than five dispatches land after it.
- Commit 7e66e244 filtered by `head_sha`. That cannot match a dispatched run, whose `head_sha` belongs to the target repo's default branch. Commit 863daee5 then replaced the filter with time alone, which loses the correlation.
- **Request:** correlate on something the payload carries, such as a `run-name` in the downstream workflow that includes `source_sha` or `github.run_id`, matched via `display_title`.

**Timestamp race.**
- `TRIGGER_TIME` is taken in a separate step *after* `curl` returns, has one-second resolution, and is compared with strict `>`.
- A downstream run created within the same second, or before the timestamp step starts, is excluded. The job then waits until the 20-minute kill.
- **Request:** take the timestamp before the dispatch, and subtract a margin or use `>=`.

**Fault: dispatch rejected** (for example 401, 404 or 422).
- `curl` runs without `--fail`, so it exits 0 on an HTTP error and the dispatch step is green.
- The job then polls for 20 minutes and dies on the generic timeout, or adopts another PR's run as above.
- Time to fail is 20 minutes instead of seconds, and the step that holds the cause shows success.
- **Request:** `curl --fail-with-body` (or `gh api -X POST …/dispatches`), plus a run showing the rejected case.

**Fault: transient `gh api` error.**
- The workflow default is `shell: bash`, which runs `-eo pipefail`. Together with `set -e`, one failed `gh api` inside `$(…)` ends the job at once.
- That makes a single transient network error fail the PR check.
- **Request:** tolerate a failed poll, logging it and continuing the loop. Each `gh api` call has no timeout of its own, so per the form it counts as never returning; the job timeout is the only bound.

**Values users already pass.**
- The `version` dispatch input previously reached only Helm, as a Harbor tag. It now also reaches the SaaS side as `zeebeVersion`.
- Whether the SaaS generation pulls `registry.camunda.cloud/team-camunda/camunda:<tag>`, or reads `zeebeVersion` as a released or Docker Hub version, is defined in the other repository and not shown here.
- **Request:** a run, linked in the description, of a PR-tagged image through the downstream workflow.

**Negative control.** No run is cited where the downstream workflow fails and the job turns red, or where it succeeds and the job turns green.

## Item 3a: level, placement, and the environment
**Analogue used:** file layout and the repository's own gate.

- The job is placed in the existing AlwaysGreen workflow, beside `helm-deploy`, and follows the `trigger-c8run-e2e-tests.yml` pattern. That placement fits.
- **The "Observe build status" step is not the last step** (CLAUDE.md: "The last step of each GHA workflow job must submit CI health metrics").
  - It runs before the wait step, so it always reports the job as `success` up to the dispatch.
  - A failed or timed-out downstream run is never recorded.
- `needs: format-identifier` is declared but `needs.format-identifier` is never read. It is a harmless extra dependency, but it suggests a use that doesn't exist.
- The gate (`actionlint` and `conftest`, run in `ci.yml`) could not be run offline here.

## Item 4: names by content, not by position
- **Observe-step `job_name: trigger-saas-e2e` breaks the file's naming.** The six sibling `job_name`s in this file are all prefixed `docker-build-helm-integration-`, so analytics grouped by that prefix will miss this job.
- No ordinals or positional references otherwise.

## Item 5: the failure report
**Analogue used:** what a failure tells the reader to look at.

- `Downstream workflow failed: $CONCLUSION` and `Workflow run $RUN_ID status: …` print a bare run ID from another repository, with no URL. The reader has to build the link by hand.
- **Request:** print the run's `html_url` (`english-developer-style` §7, error messages: "include identifiers a developer can grep").
- The 20-minute timeout case prints nothing of the script's own (see Item 3).

## Item 6: what the writer says it verified
None of the seven commits, and nothing else handed to me, cites a run of `trigger-saas-e2e`: neither a green run, nor a red run on a failing downstream workflow, nor the timeout path. The "fix linting" commits suggest actionlint was run, but no output is cited.

## Item 7: siblings of the change

- **`generate-github-app-token-from-vault-secrets@main`:** 10 call sites. The new use copies `trigger-c8run-e2e-tests.yml` exactly, so there is no defect to propagate.
- **The `curl` dispatch without `--fail` also exists in `trigger-c8run-e2e-tests.yml:43`.** There it only means a silently green trigger, because there is no wait. Name it as follow-up.
- **Hard-coded 8.9 is now in four places:**
  - `helmRepositoryDirName` default (line 21)
  - `camunda-helm-dir` fallback (line 329)
  - `c8Version: "8.9"` (line 389)
  - `WORKFLOW_FILE=…_8_9.yml` (line 422)

  The first two are inputs and the new two are not. At the next minor version, or on a backport to `stable/8.9`, all four have to change together. Taste: derive them from one input.
- **The actor allowlist:** the new member is listed only in `should-run`, which is the one list. No other file names the existing members.

## Findings

| # | Finding | Label | File:line | Request |
|---|---|---|---|---|
| 1 | Poll adopts any dispatched run after `TRIGGER_TIME`, so concurrent PRs read each other's results; comment says "first" but code takes the newest | Substantive | docker-build-helm-integration.yml:426–428 | Correlate on `source_sha`/`run_id` via a downstream `run-name` and `display_title`; fix the comment |
| 2 | `timeout-minutes: 20` cuts the "up to 40 min" loop; the comment is false and the script's timeout message is never printed | Substantive | :356, :424 | Derive one limit from the other; state the downstream run time |
| 3 | Observe-build-status runs before the wait step, so downstream failure or timeout is never recorded (violates the last-step rule) | Substantive | :402–411 | Move it to be the last step |
| 4 | `curl` without `--fail`: a rejected dispatch is green, then the job times out after 20 min | Substantive | :380 | `--fail-with-body` or `gh api -X POST`; show a rejected-dispatch run |
| 5 | Timestamp taken after dispatch at 1 s resolution with strict `>`, so the PR's own run can be missed | Substantive | :398–400, :428 | Take the timestamp before the dispatch, with a margin |
| 6 | A single transient `gh api` error fails the job (`set -e` + `pipefail`) | Substantive | :427–431 | Treat a failed poll as "retry next iteration" |
| 7 | `"slolatte"` added to the actor allowlist and the workflow renamed, with no commit sentence for either | Substantive | :5, :84 | A sentence that claims each, or move them to their own change |
| 8 | No run of the new job cited (green, red, or timeout); `zeebeVersion` = Harbor PR tag not shown to be consumable downstream | Substantive | — | Link runs in the PR description |
| 9 | Failure messages print a bare run ID, no URL | Taste | :434–441 | Print `html_url` |
| 10 | `job_name: trigger-saas-e2e` breaks the `docker-build-helm-integration-` prefix of the sibling jobs | Taste | :408 | `docker-build-helm-integration-trigger-saas-e2e` |
| 11 | Unused `needs: format-identifier`; 8.9 hard-coded beside input-driven 8.9 defaults | Taste | :355, :389, :422 | Drop the need; derive the version from one input |
| 12 | Same no-`--fail` dispatch in a sibling workflow | Taste | trigger-c8run-e2e-tests.yml:43 | Name it as follow-up |

**Not checked:** `actionlint` and `conftest` were not run (not installed), the drift script does not parse YAML, nothing in the downstream `c8-cross-component-e2e-tests` workflow was read, no CI run was observed, and I did no style-only pass over the prose.
