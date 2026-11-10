# Final review: `e3250e60..HEAD` (7 commits, one file)

**Inputs.** There is no task statement. The claimed cases come from the commit messages only. They are:
- `add saas e2e smoke tests for alwaysgreen`
- `update versions`
- `poll for conclusion`
- `add timestamp for polling`
- `add job timeout`
- two `fix linting` commits

The change is a CI workflow with no code, so I used the §2a analogues. The drift script was not run because the workflow is YAML with no members or doc comments. `actionlint` is not installed here, so it was not run. I read the diff and the surrounding workflow by hand. `conftest` was not run either.

**Skills.** I did not load `docs-page-authoring`, `apm-authoring` or `english-developer-style`. The change has few prose sentences, so the wording checks were done by eye.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another or about itself)

**Finding 1.1, substantive: the wait comment and the job timeout disagree.**
- `docker-build-helm-integration.yml:419`: the comment says `# Wait up to 40 min (80 x 30s)`.
- Line 356 sets `timeout-minutes: 20` on the job.
- GitHub kills the job at 20 minutes. The loop's "Timed out waiting" branch can never run, and the comment states a bound that does not hold.
- Request: make the loop and the job timeout agree, with the job timeout covering the whole loop. Either set the timeout above 40 minutes or shrink the loop, then fix the comment.

**Finding 1.2, substantive: the workflow description now overclaims or diverges from the code.**
- The `# description:` line says it "triggers SaaS E2E smoke tests" and "runs Helm integration and E2E tests". The new job also blocks on the downstream result, which the description does not say.
- The workflow is renamed to `Docker Build, Helm Deploy & E2E Tests (SaaS + Helm)`. `git grep` finds no other file that cites the old name.
- Request: say in the description that the job waits for the downstream result, since the job status now depends on it.

**Finding 1.3, substantive: the comment on the timestamp step is missing.**
- Lines 398–400 take `trigger_time` after the dispatch `curl`. The wait later selects runs with `created_at > TRIGGER_TIME`.
- A reader would find this arbitrary. The ordering looks like a race, and the same race is described in finding 3.2.
- Request: take the timestamp before the dispatch, and add a comment saying why.

## Item 2: claimed cases covered

| Claimed case | Evidence in the change |
| --- | --- |
| Dispatch a SaaS smoke run for the PR | The dispatch step. The commits show no run of it. |
| Poll for the downstream conclusion; fail on non-success | The loop. No run is shown for success, failure or timeout. |
| Timestamp for polling | `trigger-time` step |
| Job timeout | `timeout-minutes: 20` |
| `update versions`: `SNAPSHOT` / `8-SNAPSHOT`, added checkout | be150d28 |

**Finding 2.1, substantive: no run is shown for any path.** The commit messages state no run of the new job. The success, failure, timeout and "no run found" paths are all unexercised. The request is a run, or a stated reason.

**Finding 2.2, substantive: unclaimed hunk.**
- `"slolatte"` is added to the author allowlist (around line 83). No commit message mentions it.
- Request: claim it in a commit message, or move it to its own change.

**Commands the change tells someone to run.** The only ones are the `curl` and `gh api` calls inside the workflow itself. They have no other runner (`none`) and cannot be run locally against the target repository. This is covered by finding 2.1.

## Item 3: boundaries, partitions, negative control

**Finding 3.1, substantive: a failed dispatch is not detected.**
- `curl -X POST` has no `-f`, so a 401, 403 or 404 response still exits 0.
- The job then polls for a run that was never created and waits until the job timeout.
- Request: use `curl --fail-with-body`, so the job fails at once and prints the API message.

**Finding 3.2, substantive: the lookup race and false matches.**
- The timestamp is taken after the dispatch.
- If the downstream run is created between the dispatch and the `date` call, `created_at > TRIGGER_TIME` never matches it.
- The loop then runs until the job is killed.
- The filter is also only "any `repository_dispatch` run after T" on a fixed workflow file. Concurrent PRs or reruns can match each other's runs and report another run's result.
- Request: take the timestamp before the dispatch. Match the run on something from `client_payload`, such as `source_sha`, or on a unique id, and run the failure case.

**Finding 3.3, substantive: no status-check fault handling.**
- `set -e` is combined with `gh api`. A transient API error (a 5xx or a rate limit) aborts the whole wait on the first failed call.
- The status and conclusion are fetched with two separate calls on the same run.
- A run can finish between those calls, which gives an inconsistent pair.
- Request: fetch both fields in one call, and tolerate a failed poll with a retry.

**Finding 3.4, substantive: time to fail.**
- The longest wait is limited by the 20-minute job timeout, not by the 40-minute loop (see 1.1).
- A fault where the downstream run is never found takes the full 20 minutes, with the last output "Waiting…" and no timeout message.
- Request: a deadline that bounds the loop below the job timeout, and a run of the fault.

**Finding 3.5, taste: the `c8Version` value `"8.9"` and `WORKFLOW_FILE` are hardcoded.** They go stale on the next version branch. I prefer deriving them from one setting.

**Pre-existing state and other limits.** There is no persisted state. The other limits are the concurrency group, which cancels the in-progress run (and with it the wait), and the downstream workflow's own time. The downstream run keeps running after cancellation. Taste: note this in a comment.

## Item 3a: level, placement, environment

- Nothing here is observable in-process.
- The job is placed in the same file as the other AlwaysGreen jobs, which is correct.
- The step's secrets come from Vault, which matches the repository's rules.
- `permissions: { }` and `timeout-minutes` are set. A blank line is missing before `trigger-saas-e2e:` (line 352). Churn, not reported.
- `@main` on the third-party action is used elsewhere in the repository, so it is not a finding.

## Item 4: names by content, not by position

None. Step and job names are content-based.

## Item 5: the failure report

**Finding 5.1, substantive: the observe step is not last and reports the wrong status.**
- The repository rule says the last step of each job must be `observe-build-status`.
- Here it sits before `Wait for downstream workflow to finish`.
- It therefore records `job.status` as success before the wait has run, and a failed or timed-out wait is never reported.
- Request: move it to the end of the job.

**Finding 5.2, taste: loop output.** The loop prints `status (conclusion)` every 30 seconds, which is acceptable. The failure message does not include the run URL. I would print the run's `html_url`.

## Item 6: what the writer says it verified

No commit message or description states a red or green run. The change has no mutation evidence. The commit history shows two "fix linting" commits, which suggests the lint check ran. That is a consistency check, not evidence that the logic works. This is part of finding 2.1.

## Item 7: siblings of the change

**Finding 7.1, substantive: shell injection through expression interpolation.**
- The `curl -d` body interpolates `${{ needs.build-and-push.outputs.image-tag }}` directly into the shell script.
- That value derives from the `workflow_dispatch` input `version` (see lines 218–230), so a dispatcher can inject shell syntax.
- The same applies to `github.repository` and `github.sha`, but those are not attacker-controlled.
- Request: pass the values through `env:` and build the JSON with `jq`.

**Finding 7.2, taste: `needs: [build-and-push, format-identifier]`.** The job uses nothing from `format-identifier`; a `needs: build-and-push` would do. It matches `helm-deploy`, which does use it, so I prefer trimming it.

**Sibling set.** The other jobs in the workflow all carry `job_name` and a final observe step; the new job breaks that pattern only in the ordering (finding 5.1). Other places that list the workflow's jobs or name: `git grep` finds none.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Comment says 40 min, job timeout is 20 min | Substantive | `docker-build-helm-integration.yml:419`, `:356` | 1 |
| Description does not say the job waits for the result | Substantive | `docker-build-helm-integration.yml:1` | 1 |
| Timestamp step has no comment and sits after the dispatch | Substantive | `docker-build-helm-integration.yml:398` | 1 |
| No run shown for any path; no red/green evidence | Substantive | `docker-build-helm-integration.yml:352-449` | 2, 6 |
| `slolatte` allowlist addition is unclaimed | Substantive | `docker-build-helm-integration.yml:83` | 2 |
| `curl` without `-f` hides a failed dispatch | Substantive | `docker-build-helm-integration.yml:376` | 3 |
| Timestamp after dispatch races the run; loose run matching | Substantive | `docker-build-helm-integration.yml:398`, `:425` | 3 |
| `set -e` aborts on a transient `gh api` error; two calls per poll | Substantive | `docker-build-helm-integration.yml:415-440` | 3 |
| Fault where the run is never found takes the full job timeout with no message | Substantive | `docker-build-helm-integration.yml:419` | 3 |
| Hardcoded `c8Version` and workflow file | Taste | `docker-build-helm-integration.yml:388`, `:422` | 3 |
| Observe step is not last and records status before the wait | Substantive | `docker-build-helm-integration.yml:402` | 5 |
| Failure message omits the run URL | Taste | `docker-build-helm-integration.yml:432` | 5 |
| Shell injection through interpolated `image-tag` | Substantive | `docker-build-helm-integration.yml:388` | 7 |
| Unused `format-identifier` dependency | Taste | `docker-build-helm-integration.yml:355` | 7 |

**Not done.** The checks `actionlint` and `conftest` could not be run here: `actionlint` is not installed, and I did not try `conftest`. The drift script was not run because the change is YAML. The task statement was not handed over, so item 2 was answered from the commit messages alone.
