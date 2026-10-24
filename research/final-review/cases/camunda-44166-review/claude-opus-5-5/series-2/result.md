# Final review: `e3250e60..HEAD` (7 commits, one file: `.github/workflows/docker-build-helm-integration.yml`)

There was no task statement, so I took the claimed cases from the seven commit messages alone. The change is a CI workflow with no tests or Java members. I filled the form through the §2a analogues and also applied the §2 paragraphs on limits, faults and passed-through values, because the change adds a polling loop. I ran the drift script; it printed nothing (rc 0) because it does not parse YAML. I loaded `test-authoring` and `english-developer-style` from the given directory. No previous report exists.

## Item 1: comments consistent with the code and with each other
*Analogue: the YAML comments, step and job names, and the `# description:` header, checked against the code.*

- **Line 424, `# Wait up to 40 min (80 x 30s)`, is false.** Commit 4459b6fc set `timeout-minutes: 20` (line 356), so GitHub cancels the job at about 20 minutes, including the time spent on earlier steps. The loop can never reach 40 minutes. Even without the job limit it would run longer than 40 minutes, because each pass also makes up to three `gh api` calls. A reader would believe the job waits 40 minutes and that a slow downstream run ends with "Timed out…".
- **Line 426, `# Grab the first run created after the trigger event`, does not describe what line 428 does.** The list-runs endpoint returns runs newest first, so `head -n1` picks the newest run created after `TRIGGER_TIME`, not the first one. Item 3 covers what this does when other PRs trigger runs at the same time.
- The job name "Trigger SaaS E2E tests" and the header ("triggers SaaS E2E smoke tests") say the job only triggers the tests. The job also waits for them and gates on their result. This is taste.
- No comment describes the change itself with "now" or "no longer".

## Item 2: claimed cases covered
Claimed cases, taken from the commit messages:

| Claim | Covered by | Evidence of a run |
|---|---|---|
| add SaaS E2E smoke tests for AlwaysGreen (4662bcd1) | job `trigger-saas-e2e`, lines 352–447 | none stated |
| update versions (be150d28): operate/tasklist/connectors to `SNAPSHOT`, optimize to `8-SNAPSHOT` | lines 391–394 | none stated |
| poll for conclusion (7e66e244) | lines 413–447 | none stated |
| add timestamp for polling (863daee5) | lines 398–400 and 428 | none stated |
| fix linting ×2 (e3ff145e, c15b27bf) | `_` loop variable, quoted `$GITHUB_OUTPUT` and `"$RUN_ID"` | actionlint not run here (not installed) |
| add job timeout (4459b6fc) | line 356 | conftest warns on it (item 3a) |

Commands the change runs, with the outcome each promises:
- **`curl -X POST …/dispatches` (line 380): starts the downstream run.** Nothing in the repository runs this request against `camunda/c8-cross-component-e2e-tests`, and nothing confirms that the event type `run-saas-generation-smoke` is routed to `playwright_saas_pr_trigger_monorepo_8_9.yml`. Both pieces of config live in the other repository. Without `--fail`, curl exits 0 on HTTP 401, 403, 404 and 422 alike. Coverage: **none**.
- **`gh api …/workflows/$WORKFLOW_FILE/runs?event=repository_dispatch&per_page=5` (line 427): finds this PR's run.** Coverage: **none**. The workflow file name and the token's `actions:read` access on that repository depend on things that live outside this repository.

The request is a link to a run of this job on a PR, green and also red, or a sentence stating that it was run.

Hunks that no commit sentence claims:
- **`"slolatte"` added to the actor allow-list (line 84).** This is an access change: it lets a further actor's PRs run the whole pipeline, including the GKE deployment. No commit message mentions it.
- **`actions/checkout@v4` added (line 359) in the commit titled "update versions".** The checkout is needed for the local `observe-build-status` action, but nothing says so.
- **The workflow was renamed (line 5).** The rename is only loosely covered by "add saas e2e smoke tests". It also changes the `concurrency.group` key, which is built from `github.workflow`.
- **`needs: format-identifier` (line 355) is never used by the job.**

## Item 3: boundaries, partitions, and the negative control
*Analogue: configuration and script partitions, faults, limits, and passed-through values.*

**Limits.**
- The job allows 20 minutes (line 356). The loop allows at least 80 × (30 s + poll time), which is at least 40 minutes (line 424).
- The limit set elsewhere (the job's 20 minutes) always fires first, so the loop's own timeout branch at line 446 can never run. One limit should be derived from the other.
- The repository's policy, `.github/conftest-unified-ci-rules.rego:24`, warns on any job above 15 minutes, and this job is set to 20.

**Fault: the dispatch is rejected**, for example a token without access to the other repository or an unknown event type.
- curl prints the error body and exits 0 (line 380).
- The loop then finds no run and goes on until the 20-minute job limit cancels it. All it prints is the "Waiting…" line, never "Timed out…".
- Worse, it can pick up another PR's run, as described next, and report that run's conclusion.
- That is about 20 minutes to fail, with the cause shown only in the earlier step's output. Adding `--fail-with-body` would fail it in about 1 second.

**Partition: two PRs at once.** This workflow runs on every PR from the allow-listed actors, so concurrent dispatches are normal.
- The filter keeps any `repository_dispatch` run created after this job's timestamp (line 428) and takes the newest one.
- Example: PR A dispatches at T and PR B at T+10 s. PR A's first poll, at about T+30 s, sees both runs and picks B's, then passes or fails on PR B's result.
- Nothing ties the run to `source_sha`. The request is to tie them together, for example with a downstream `run-name` that includes `source_sha`, matched on `display_title`.

**Boundary: the timestamp.**
- `TRIGGER_TIME` is taken after the curl returns (lines 398–400) and compared with a strict `>` at one-second granularity.
- A downstream run created before that step starts, or in the same second, is never matched.
- The request is to take the timestamp before the dispatch and compare with `>=`.

**Fault: a transient API error.**
- `set -e` together with the `pipefail` that `shell: bash` adds means one 5xx or rate-limit response from any of about 100 `gh api` calls fails the job at once (lines 418, 427, 431–432).
- No retry exists, and no sentence in the change accepts this behavior.

**Values users already pass.**
- `inputs.version` (workflow_dispatch) now reaches a new consumer as `zeebeVersion` (line 390). It sits inside a single-quoted JSON string in a `run:` script, so a value containing `'` or `"` breaks the request.
- The payload names no registry, while the image tag exists only in `registry.camunda.cloud/team-camunda/camunda`. Nothing in the change states that the SaaS generation can pull from there.
- `inputs.helmRepositoryDirName` (for example `camunda-platform-8.8`) changes the Helm leg only. `c8Version: "8.9"` and the `_8_9.yml` workflow stay fixed (lines 389 and 422), so the two legs can test different minor versions of the same image.

**Negative control.** No statement says what happens when the Helm leg fails and the SaaS leg passes. The two jobs are independent, and that is fine, but nothing records it.

## Item 3a: level, placement, and the environment
*Analogue: where the job lives and the repository's own offline gates.*

- `actionlint` and `conftest` are not installed here. I parsed the file with `yq` and read the policy by hand.
- Under the policy, the CI-health `deny` rule passes because the step exists. The `>15` timeout `warn` fires for `trigger-saas-e2e`. The print-metadata `warn` fires, as it already did for every job in this file.
- **The "Observe build status" step is not the last step (lines 402 → 413).** The repository's CLAUDE.md says the CI-health step must be the last step of every job. Here it records `job.status` before the wait step runs, so a downstream failure, a timeout or a cancellation is reported to CI health as success. The policy only checks that the step exists, which is why it did not catch this.
- Placing the job in this workflow, next to `helm-deploy` and depending on `build-and-push`, is consistent with the rest of the file.

## Item 4: names by content, not by position
- Line 426: "the first run" is an ordinal, and the wrong one (item 1). Naming it by content ("the run dispatched for this commit") would also fix the race described in item 3.
- Line 408: `job_name: trigger-saas-e2e` breaks the convention that every other job in this file follows, the `docker-build-helm-integration-*` prefix (lines 95–315). Dashboards that filter on the prefix will miss it. This is taste.

## Item 5: the failure report
- On a curl rejection, the error body appears in the dispatch step's output, while the job fails 20 minutes later in a different step. That is substantive, and it is the same request as the rejected-dispatch fault in item 3.
- `Downstream workflow failed: $CONCLUSION` (line 439) prints no link to the downstream run, so the reader has to build the URL from the run ID printed earlier. Printing `html_url` would help. This is taste.
- On a job cancellation, the "Timed out…" message never prints (item 3).

## Item 6: what the writer says it verified
Neither the commits nor any description state a run of the new job: no green run, no red run, and no rejected-dispatch run. The history shows 7e66e244 matching `head_sha == github.sha`, which could never match a run in another repository, and 863daee5 fixing that. This suggests the loop was tried, but no evidence is stated.

## Item 7: siblings of the change
- `.github/workflows/trigger-c8run-e2e-tests.yml:42` sends the same `curl -X POST …/dispatches` without `--fail`, so the same silent rejection applies there. That workflow does not wait for a result, so the effect is a green check over a dispatch that never happened. Name it as follow-up.
- Ten other workflows use the same `generate-github-app-token-from-vault-secrets@main` configuration, and the QA app paths match `trigger-c8run-e2e-tests.yml`. No defect there.
- No other workflow polls a run in another repository, so the loop has no sibling.
- The actor allow-list exists only in this file, so no other list needs the new member.
- I found no references to the old workflow name "Docker Build and Helm Integration Test" in the repository. Branch-protection settings are outside the repository and were not checked.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The 20-minute job limit fires before the loop's 40 minutes; the comment is false and line 446 can never run | Substantive | `docker-build-helm-integration.yml:356,424,446` | Derive the loop count from the job timeout (or the reverse) and fix the comment; resolve the conftest `>15` warning or state why it is accepted |
| CI-health step runs before the wait, so failures and timeouts are recorded as success | Substantive | `:402–411` | Move "Observe build status" to be the last step |
| Run lookup takes the newest dispatch run after the timestamp, which can be another PR's run | Substantive | `:426–428` | Tie the run to this dispatch, for example `source_sha` in the downstream `run-name` matched on `display_title`; fix the comment |
| Timestamp taken after the dispatch with a strict `>`, so the downstream run can be missed | Substantive | `:398–400,428` | Take the timestamp before the curl and use `>=` |
| curl without `--fail`: a rejected dispatch looks like success, then the job waits about 20 minutes and gives no reason | Substantive | `:380` | Add `--fail-with-body`; show a run of the rejection case with its duration and output |
| One transient `gh api` error under `set -e`/pipefail fails the gate | Substantive | `:418,427,431–432` | Retry or tolerate a failed poll, or state that it is accepted |
| No run of the dispatch or the poll is stated (event routing, workflow file name, token scope) | Substantive | `:380–396,422,427` | Link a green run and a red run of this job |
| `"slolatte"` added to the allow-list without any commit sentence claiming it | Substantive | `:84` | Claim it in the description or move it to a change of its own |
| `inputs.version` reaches the SaaS payload unescaped, with no registry; `c8Version`/workflow fixed at 8.9 while the Helm directory is an input | Substantive | `:389–390,422` | State that the SaaS side can pull the Harbor tag, and either derive the 8.9 values or document that the SaaS leg is 8.9-only |
| Same curl without `--fail` in `trigger-c8run-e2e-tests.yml` | Substantive (follow-up) | `trigger-c8run-e2e-tests.yml:42` | Name it as follow-up in the description |
| Unused `needs: format-identifier` | Taste | `:355` | Drop it |
| `job_name` breaks the file's `docker-build-helm-integration-*` prefix | Taste | `:408` | Use `docker-build-helm-integration-trigger-saas-e2e` |
| Job and step names say "Trigger", but the job also gates on the result | Taste | `:353,376` | For example "Run SaaS E2E smoke tests" |
| Failure message has no link to the downstream run | Taste | `:439` | Print the run's `html_url` |

**Not checked:** I did not run actionlint or conftest (neither is installed), did not run the workflow, and could not see the downstream repository's workflow, its event routing, or the GitHub app's permissions. I did not do a style-only pass over the prose.
