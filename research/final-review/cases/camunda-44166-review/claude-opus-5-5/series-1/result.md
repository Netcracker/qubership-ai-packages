# Final review: `e3250e60..HEAD` (7 commits, one file: `.github/workflows/docker-build-helm-integration.yml`)

The change adds a `trigger-saas-e2e` job to the workflow. The job sends a `repository_dispatch` to `camunda/c8-cross-component-e2e-tests` and then polls that repository until the run finishes. The job has a substantive defect: its 20-minute timeout ends the job about halfway through a polling loop meant to last 40 minutes. It also follows a downstream run that may belong to another PR or push, and it records its CI health metric before the wait starts.

No task statement was handed over, so I took the claimed cases from the commit messages alone (§1). This change is a CI configuration with no members and no tests, so I filled the form through the §2a analogues. I ran the drift script (`comment-drift.py e3250e60… HEAD`). It exited 0 and printed nothing because it does not parse YAML, so I checked the comments by hand. I loaded `english-developer-style`. There is no doc-comment or test-authoring skill for a workflow, so I did not apply one. No previous report exists.

## Item 1: comments consistent with the code and with each other
*Analogue: every statement in the file about what the workflow or the job does.*

- **L424** `# Wait up to 40 min (80 x 30s)` is false. The job's `timeout-minutes: 20` (L356) ends the job about 19 minutes into the loop. A reader would expect a 40-minute budget.
- **L426** `# Grab the first run created after the trigger event` is false. The runs endpoint returns runs newest first, so `head -n1` takes the **newest** matching run, not the first one. With two or more matching runs, the code follows the last one.
- **L1** description and **L5** `name:`: both now say "E2E tests (SaaS + Helm)". The Helm E2E part (`e2e-enabled: true`) was already in the base. The SaaS part only triggers and waits, which the L1 description states correctly. No contradiction found.

## Item 2: claimed cases covered
*Analogue: each claim in a commit message, checked against the hunk that implements it and any run that exercises it.*

| Claim (commit) | Where | Run that exercises it |
|---|---|---|
| Add SaaS E2E smoke tests for AlwaysGreen (`4662bcd`) | L352–411 | None stated. No CI run is linked or quoted. |
| Update versions (`be150d2`) | L391–394: `SNAPSHOT` / `8-SNAPSHOT` | None stated |
| Poll for conclusion (`7e66e24`) | L413–449 | None stated |
| Add timestamp for polling (`863daee`) | L398–400, L428 | None stated |
| Fix linting ×2 | `$GITHUB_OUTPUT` quoting, `_` loop variable | Consistent with shellcheck. I could not rerun it because actionlint is not installed. |
| Add job timeout (`4459b6f`) | L356 | None stated |

Commands the change runs: `curl` POST to `/dispatches` and `gh api` polling. No script or job runs either of them outside this workflow, so the only evidence would be a run of this workflow, and none is cited.

Hunks no commit sentence claims:
- **L84**: adds `"slolatte"` to the actor allowlist of the `should-run` gate. This widens who triggers the whole pipeline (Harbor push, GKE deploy), and no commit message mentions it.
- **L359–360**: `actions/checkout@v4` arrives in the "update versions" commit. It is needed for the local `observe-build-status` action, but that commit's message does not say so.
- **L357**: `permissions: { }` arrives in the "add job timeout" commit.

All three are small, but item 2 counts any unclaimed hunk.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the faults the new mechanism meets, how long each takes to fail, what each prints, and the limits on the same work.*

**Limits.** The loop's budget is 80 × (30 s sleep + three `gh api` calls). That is at least 40 minutes and, with gh's default network timeouts, longer. The job limit is `timeout-minutes: 20` (L356), counted from job start. The checkout, the token step, and the dispatch take roughly a minute before the loop starts. So the job limit fires first at the defaults: the loop's own "Timed out waiting…" message (L448) can never print, and the job ends as a runner timeout. Any downstream smoke run longer than about 18 minutes always fails this job, whatever its own result. **Substantive.** Request: derive one limit from the other, for example set `timeout-minutes` above 80 × 30 s plus margin, or size the loop to fit inside 20 minutes, and state the downstream run's typical duration.

**Fault: wrong credential or rejected dispatch (401/403/404/422).**
- `curl -X POST` (L380) has no `-f`/`--fail-with-body`, so curl exits 0 on an HTTP error and the step goes green.
- The wait loop then finds no run (or another PR's run, see below) and polls until the 20-minute job timeout.
- Failure takes about 20 minutes and prints only the API error body in the dispatch step's log, which is marked as passing.

**Substantive.** Request: `curl --fail-with-body`, or check for HTTP 204.

**Fault: run correlation (concurrent triggers).**
- L428 matches any `repository_dispatch` run of `playwright_saas_pr_trigger_monorepo_8_9.yml` created after `TRIGGER_TIME`, with no `source_sha` or other correlation.
- The allowlist has 15 actors, and every push to their PRs dispatches the same event. Two overlapping triggers mean each job may report the other's result.
- `head -n1` picks the newest run, which makes the cross-match the likely outcome.
- The original commit `7e66e24` filtered on `head_sha == github.sha`. That filter could never match, because a dispatch run's `head_sha` is the target repository's sha. Commit `863daee` replaced it with a filter that matches too much.

**Substantive.** Request: correlate on a value the dispatch carries, such as a unique id in `client_payload` echoed in the downstream run name (`run-name`), and match on that.

**Fault: timestamp race.**
- `TRIGGER_TIME` is taken **after** the dispatch (L398–400, after L380), at one-second resolution, and compared with strict `>`.
- A downstream run created before the `date` call, or in the same second, is excluded. The job then waits on some later run or times out.

**Substantive.** Request: take the timestamp before the `curl` and compare with `>=`.

**Fault: transient API error while polling.** The workflow's `defaults.run.shell: bash` runs steps with `-eo pipefail`. A single failed `gh api` call among up to 240 (a 5xx or a secondary rate limit) aborts the step and fails the PR check. It fails fast and prints gh's error, so this is not a slower failure. It is a false red that a retry would avoid. **Taste:** I'd tolerate a failed poll and retry.

**Value now passed to a new consumer.** `zeebeVersion` gets `needs.build-and-push.outputs.image-tag`, for example `8.9.0-SNAPSHOT-pr123`. That image exists only in `registry.camunda.cloud/team-camunda/camunda`. The payload names no registry or repository, so the downstream must already know to pull from Harbor's `team-camunda` path. I could not verify this from inside this repository. **Substantive (unverified):** I'd ask for a link to a downstream run that pulled this tag.

**Pre-existing state.** None relevant beyond the concurrency group: renaming `name:` changes `${{ github.workflow }}`, so runs already in flight under the old name are not cancelled by the first push after merge. This is a one-time effect and harmless.

## Item 3a: level, placement, and the environment
*Analogue: where the job lives, whether it matches its siblings, and whether the repository's own gates pass.*

**Placement against the CLAUDE.md CI rules:**
- **Metric step position (substantive).** "Observe build status" (L402) is not the last step: the wait step (L413) follows it. It records `job.status` right after the dispatch, so the metric shows success even when the downstream run fails or times out. Request: move it to the end.
- `job_name: trigger-saas-e2e` (L408) breaks the file's convention: every other job uses `docker-build-helm-integration-<job>` (L95–315), so the metric lands outside the workflow's group. **Substantive** for anyone filtering CI health by that prefix.
- **Token scope (taste).** The app token requests `repositories: camunda,c8-cross-component-e2e-tests` (L374), but the job only touches the second. Least privilege suggests dropping `camunda`.

**Repository gates:** the CLAUDE.md gates are `actionlint` and `conftest test --rego-version v0 -o github --policy .github`. Neither tool is installed here, so I did not run either one. `yq` parses the file.

## Item 4: names by content, not by position
- **L426** "the first run" names the run by position, and the position is also wrong (see item 1). Name it by content instead, such as "the run dispatched by this job" once correlation exists.
- Otherwise none: step and job names describe their content.

## Item 5: the failure report
*Analogue: what a failing run tells the reader.*
- **Timeout path:** the loop's message (L448) is unreachable (item 3), so a slow downstream run fails with GitHub's generic "exceeded the maximum execution time". It does not name the downstream run.
- **No run found:** the loop never prints that it has not found a run yet. Polls without a match print nothing.
- **Failure path:** it prints `Downstream workflow failed: <conclusion>` but not the run's `html_url`. Request: print the run URL once it is found.

**Substantive.**

## Item 6: what the writer says it verified
None stated. No commit links a workflow run that shows the dispatch accepted, the downstream run found, or a red result propagated. The history (a `head_sha` filter that could not match, then a timestamp, then a timeout) suggests trial and error with no run cited.

## Item 7: siblings of the change
- `.github/workflows/trigger-c8run-e2e-tests.yml:43` uses the same `curl -X POST …/dispatches` without `--fail`, so the dispatch defect has a sibling. This change copied the pattern; the request is to fix it there too or name it as follow-up.
- `preview-env-smoke-test.yml` reaches the same downstream repository through a different mechanism (`actions/checkout`), so the polling defects do not apply there.
- **Hard-coded version (taste).** `c8Version: "8.9"` (L389) and `WORKFLOW_FILE=…_8_9.yml` (L422) are fixed. The neighbouring `helm-deploy` job takes its 8.9 chart directory from `inputs.helmRepositoryDirName`. When `main` moves to 8.10 (`pom.xml` says `8.9.0-SNAPSHOT` now), these three places must change together. I'd derive them from one place.
- **Set membership.** The new allowlist entry needs no sibling list. No other file names the workflow's old title (`git grep` found none).

## Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| Job timeout (20 min) fires before the loop's 40-min budget; "Wait up to 40 min" is false and the timeout message is unreachable | Substantive | `docker-build-helm-integration.yml:356`, `:424`, `:448` | Derive one limit from the other and state the downstream run's typical duration |
| Downstream run not correlated: any dispatch run after `TRIGGER_TIME` matches, and `head -n1` takes the newest, so concurrent PRs swap results | Substantive | `:426–428` | Correlate on a unique id in `client_payload` |
| Timestamp taken after the dispatch with strict `>`, which can exclude the job's own run | Substantive | `:380`, `:398–400`, `:428` | Take the timestamp before the dispatch; use `>=` |
| `curl` without `--fail`: a rejected dispatch passes, then the job hangs until timeout | Substantive | `:380` | `curl --fail-with-body`; same fix or a follow-up note for `trigger-c8run-e2e-tests.yml:43` |
| "Observe build status" is not the last step, so it reports before the wait | Substantive | `:402` | Move it after the wait step |
| `job_name` breaks the file's `docker-build-helm-integration-*` convention | Substantive | `:408` | `docker-build-helm-integration-trigger-saas-e2e` |
| Comment says "first run", code takes the newest | Substantive | `:426` | Fix the comment with the correlation change |
| Failure output omits the downstream run URL; no output while no run has matched | Substantive | `:430–449` | Print `html_url` and a "no run yet" line |
| Unclaimed hunks: allowlist entry `slolatte`, checkout in "update versions", `permissions` in "add job timeout" | Substantive | `:84`, `:359–360`, `:357` | Add a sentence for each to the commit message or PR description, or move it out |
| Downstream's ability to pull a Harbor `team-camunda` tag from `zeebeVersion` is unverified | Substantive | `:390` | Link a downstream run that used such a tag |
| No run evidence for any claim | Substantive | none (commit messages) | Link a run showing success, a propagated failure, and the dispatch accepted |
| One transient `gh api` error fails the job under `pipefail` | Taste | `:427–432` | Tolerate a failed poll and retry |
| Token requests the `camunda` repository it does not use | Taste | `:374` | Drop `camunda` from `repositories` |
| Hard-coded 8.9 in the payload and the workflow file name | Taste | `:389`, `:422` | Derive from one place |

I did not check: `actionlint` and `conftest` (not installed here), the downstream repository's workflow and its accepted payload (no `gh` or network), and no workflow run was made. The prose was not reviewed for style alone.
