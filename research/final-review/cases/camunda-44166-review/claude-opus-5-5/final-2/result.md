# Final review: `e3250e60..HEAD` (7 commits, one file: `.github/workflows/docker-build-helm-integration.yml`)

There was no task statement, so I took the claimed cases from the seven commit messages alone. No earlier report of this form exists, so the round-over-round table is left out. The change is a CI workflow, not code, so the form is filled through the §2a analogues and each item names the one it used. I ran the drift script, `comment-drift.py e3250e60… HEAD`: it exited 0 and printed nothing, because it does not parse YAML. I loaded `test-authoring` and `english-developer-style`. No doc-comment skill applies.

## Item 1: comments consistent with the code and with each other
Analogue used: the statements the file makes about itself.

- **Line 424, `# Wait up to 40 min (80 x 30s)`, is false.** The job has `timeout-minutes: 20` (line 356). Runner timeout kills the step at about 20 minutes, minus the minutes already used by checkout, the token, and the dispatch. So the loop never reaches 40 minutes, and the line `Timed out waiting for downstream workflow to complete.` (line 446) is never printed.
- **Line 426, `# Grab the first run created after the trigger event`, says the opposite of what the code does.** The runs endpoint returns runs newest first, so `head -n1` takes the *latest* run created after `TRIGGER_TIME`, not the first one (see item 3 for why this matters).
- **Line 1, the header:** it says the workflow "runs Helm integration and E2E tests". That holds, because `helm-deploy` sets `e2e-enabled: true` (line 332). It also says it "triggers SaaS E2E smoke tests". The job also *waits for them and fails on their result*, which a reader of the header would not expect, but nothing it says is false.
- No comment narrates the change.

## Item 2: claimed cases covered
Analogue used: each commit's claim, set against the step that handles it and any evidence that it ran.

| Claimed case (commit) | Where handled | Evidence it works |
|---|---|---|
| Dispatch SaaS e2e smoke tests for AlwaysGreen (`4662bcd1`) | step "Trigger repository_dispatch…" | No run cited. The `curl` has no `--fail`, so a 401, 404, or 422 still exits 0 (item 5). |
| Pass SNAPSHOT versions (`be150d28`) | `client_payload` | Nothing shows the downstream workflow accepts `SNAPSHOT` / `8-SNAPSHOT`. Nothing shows it can pull `zeebeVersion` = `8.9.0-SNAPSHOT-pr<N>` from `registry.camunda.cloud/team-camunda/camunda`: the payload carries a tag but no registry or repository. |
| Poll for the conclusion (`7e66e244`) | step "Wait for downstream workflow to finish" | Four outcomes are claimed by the code: success, failure, run never found, and timeout. None has a cited run, and the timeout outcome cannot happen at all (item 3). |
| Use a timestamp to pick the run (`863daee5`) | step "Get trigger timestamp" + the `select(.created_at > …)` filter | Not correlated to this dispatch (item 3). |
| Fix linting (`e3ff145e`, `c15b27bf`) | quoting of `$GITHUB_OUTPUT` and `$RUN_ID` | I ran `shellcheck` on the extracted wait script: clean. `bash -n`: clean. `actionlint` and `conftest` are not installed here. |
| Add a job timeout (`4459b6fc`) | line 356 | Conflicts with the loop (item 3). |
| *Not claimed by any message* | `slolatte` added to the actor allowlist (line 84); workflow renamed (line 5) | No commit message mentions either change. |

## Item 3: boundaries, partitions, and the negative control
Analogue used: the limits on the polling work, how the run is matched, and the state the change meets.

**Limits on how long the SaaS run is awaited:**
- The job timeout is 20 minutes, set at line 356.
- The poll loop is 80 × 30 s plus API latency, so more than 40 minutes, set at lines 424–444.
- The downstream workflow `playwright_saas_pr_trigger_monorepo_8_9.yml` has its own limit. It lives in `camunda/c8-cross-component-e2e-tests`, which this repository does not contain.

The inner limit (the loop) does not fire before the outer one (the job). So the job is cancelled at 20 minutes, and the loop's own timeout report is hidden. If the SaaS run takes longer than about 18 minutes, the job fails even when the run would have passed. **Substantive.** Request:
- Derive one value from the other, for example a 45-minute job timeout, or a loop count computed from the job timeout.
- Cite the downstream workflow's `timeout-minutes` (file and line), or a run that shows how long it takes.

**The run is not matched to this dispatch:**
- **Concurrent PRs.** The workflow runs on every qualifying PR. The filter takes "any `repository_dispatch` run of that workflow created after `TRIGGER_TIME`" and then the newest of up to 5. When two PRs dispatch within the same window, each job can pick the other PR's run and report its result. **Substantive.** Request: match on content. For example, have the downstream set `run-name` from `client_payload.source_sha` or from a nonce, and select on `.display_title`.
- **Timestamp taken too late.** `TRIGGER_TIME` is recorded in a step *after* the dispatch, and the comparison is strict `>` at one-second precision. A run created before or in the same second as `date` runs is skipped, and the job polls until it is killed. **Substantive.** Request: take the timestamp before the `curl`, and compare with `>=`.

**Missing controls:**
- No run of the failure branch is cited, so nothing shows a failing SaaS run turns this job red.
- No run of the "dispatch rejected" branch is cited. That branch currently becomes a silent 20-minute hang.

## Item 3a: level, placement, and the environment
Analogue used: where the rule lives and whether the repository's gate passes.

- **The observe step is not the last step.** "Observe build status" is step 5 of 6 (yq listing), placed before "Wait for downstream workflow to finish". CLAUDE.md requires it to be the last step. It also records `job.status` before the only step that can fail on the SaaS result, so the CI health metrics report success for a job that later fails or times out. **Substantive.** Move it to the end.
- The repository's gate (`actionlint`, `conftest test --rego-version v0 -o github --policy .github`) could not be run offline here because neither tool is installed. The commits do not say it was run.
- **Metric job name breaks the file's pattern.** `job_name: trigger-saas-e2e` drops the `docker-build-helm-integration-` prefix that every other job in this file uses (lines 95, 125, 154, 183, 284, 315). **Taste.**
- `needs: format-identifier` (line 355) is never used by the job. It only delays the job slightly. **Taste.**

## Item 4: names by content, not by position
`none`. I checked step names, job names, and the echo messages. All of them name things by content.

## Item 5: the failure report
Analogue used: what the job prints when it fails.

- **Dispatch errors are silent.** `curl -X POST …` without `-f` / `--fail-with-body` turns an HTTP error from the dispatch API into a green step. The next thing a reader sees is a job cancelled at 20 minutes, with no hint that the dispatch was rejected. **Substantive.** Add `--fail-with-body`.
- **Run ID is not a link.** The failure message `Downstream workflow failed: $CONCLUSION` does not include the run URL. The run ID is printed earlier, but `html_url` would take the reader straight to the cause. **Taste.**
- **Transient API errors end the poll.** `set -e` combined with the `gh api` calls means one transient API error ends a 40-minute poll with a bare `gh` error. **Taste.**

## Item 6: what the writer says it verified
None of the seven commit messages states a run of the workflow, against either a passing or a failing downstream run. No evidence is stated that the job can turn red on a real failure, or that it finds the right run.

## Item 7: siblings of the change
- **`.github/workflows/trigger-c8run-e2e-tests.yml:42–47`** dispatches to the same repository with the same `curl -X POST` and also has no `--fail`. The same silent-failure defect applies there, although that job does not poll. Name it as follow-up.
- **Hard-coded 8.9 values:** `.github/workflows/preview-env-smoke-test.yml` is the other caller of this token and repository, and it does not hard-code an `8.9` workflow file. In this workflow, `c8Version: "8.9"` and `WORKFLOW_FILE=…_8_9.yml` sit beside `helmRepositoryDirName` (default `camunda-platform-8.9`), which `workflow_dispatch` lets a user change. Dispatching for a different chart version still runs the 8.9 SaaS tests. **Taste**, unless other versions are meant to be supported.
- **Workflow rename:** `git grep` finds no reference to the old name "Docker Build and Helm Integration Test" anywhere in the repository. The concurrency group is keyed on `github.workflow`, so the rename only changes the group key. Required-check settings and dashboards outside the repository were not checked.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The 20-min job timeout cuts off the >40-min poll loop; the "Wait up to 40 min" comment is false | Substantive | `.github/workflows/docker-build-helm-integration.yml:356`, `:424` | Derive one limit from the other; cite the downstream workflow's timeout |
| The run is not correlated to this dispatch; with concurrent PRs, a job can take another PR's run | Substantive | `:426–427` | Match on `source_sha` or a nonce via the downstream `run-name` / `display_title` |
| `TRIGGER_TIME` is taken after the dispatch, with strict `>` at one-second precision, so the run can be missed | Substantive | `:398`, `:427` | Take the timestamp before the `curl`; use `>=` |
| The "Grab the first run" comment is wrong: `head -n1` takes the newest run | Substantive | `:426` | Fix the comment (or the logic) together with the correlation fix |
| `curl` has no `--fail`, so a rejected dispatch is green and the job then hangs until the timeout | Substantive | `:378` | Add `--fail-with-body` |
| "Observe build status" is not the last step and reports status before the wait step | Substantive | `:400–408` | Move it after "Wait for downstream workflow to finish" |
| No run evidence for the dispatch, the SNAPSHOT payload, the registry and tag, or the failure and timeout branches | Substantive | — | Cite a passing run and a failing downstream run in the PR |
| Same no-`--fail` dispatch in a sibling workflow | Substantive (follow-up) | `.github/workflows/trigger-c8run-e2e-tests.yml:42` | Fix it here or name it as follow-up |
| Allowlist addition and workflow rename are mentioned in no commit message | Taste | `:5`, `:84` | Mention them in the squashed message or PR description |
| `job_name` lacks the file's `docker-build-helm-integration-` prefix | Taste | `:405` | `docker-build-helm-integration-trigger-saas-e2e` |
| `needs: format-identifier` is unused | Taste | `:355` | Drop it |
| Failure message has no run URL; `set -e` aborts the poll on one transient API error | Taste | `:437–441`, `:420` | Print `html_url`; tolerate transient `gh api` errors |
| SaaS version 8.9 is hard-coded while the chart dir is a dispatch input | Taste | `:386`, `:422` | Derive it from the input, or document that only 8.9 is supported |

Not checked: `actionlint` and `conftest` (not installed), the workflow itself (no run was possible), the downstream repository's workflow and its timeout, settings outside the repository that might reference the old workflow name, and a style-only pass over the prose.
