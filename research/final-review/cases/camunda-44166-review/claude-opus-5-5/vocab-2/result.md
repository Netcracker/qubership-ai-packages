# Final review: `e3250e60..HEAD`, `.github/workflows/docker-build-helm-integration.yml`

The new SaaS E2E job has three problems that would make it give the wrong result. It can wait on the wrong downstream run. It cannot finish the wait before the job is killed. And it reports its status to CI metrics before the wait runs. Nothing in the commits shows a run of the workflow.

**How I reviewed it.** There was no separate task statement, so the claimed cases come only from the seven commit messages, and those are all one-line subjects. The change is a CI configuration with no code, so I used the §2a analogues and applied Item 3 as written. I loaded `english-developer-style`. No doc-comment skill applies, and `apm-authoring` doesn't either, because this is not a skill or an instruction file. `comment-drift.py` ran and printed nothing (exit 0), because it doesn't parse YAML. I used the YAML comments, step names and the header `description:` as the comments.

## Item 1: comments consistent with the code and with each other

Analogue: YAML comments, step and job names, and the header description, each checked against the shell and YAML they describe.

- **The "first run" comment is wrong (`:426`).** The comment says "Grab the first run created after the trigger event". The runs endpoint lists runs newest first, so `head -n1` returns the newest matching run, not the earliest. A reader would think the code picks the run this dispatch started. The correlation problem behind this is filed under Item 3.
  - **Request:** say what the code selects ("the newest run created after `TRIGGER_TIME`"), or fix the selection as Item 3 asks.
- **"Wait up to 40 min (80 x 30s)" is false (`:424`).** The job limit kills the step at 20 minutes. This is filed under Item 3.
- **Coined term "SaaS Monorepo" (`:376`).** The step name is "Trigger repository_dispatch for SaaS Monorepo". The base has no "SaaS Monorepo" anywhere (`git grep -i` at the base finds nothing). The target is `c8-cross-component-e2e-tests` and the event is `run-saas-generation-smoke`. A reader could take it for the name of a repository.
  - **Request:** name the thing directly, for example "Dispatch SaaS smoke tests to c8-cross-component-e2e-tests".
- **"triggers" undersells what the job does (`:1`, `:353`) — taste.** The header description says the workflow "triggers SaaS E2E smoke tests", and the job is named "Trigger SaaS E2E tests". The job actually waits for the downstream run and fails when it fails. "Run" or "trigger and await" would say that.

## Item 2: claimed cases covered

Analogue: the cases the commit messages claim, each set against the YAML that handles it.

| Claimed case (commit) | Where it is handled |
| --- | --- |
| SaaS E2E smoke tests for AlwaysGreen (`4662bcd1`) | `trigger-saas-e2e` job, `:352-447`. No run is stated (Item 6). Nothing here shows the downstream workflow deploys `zeebeVersion` = this image tag. |
| Update versions (`be150d28`) | Payload `:391-394`, alpha3 → `SNAPSHOT`/`8-SNAPSHOT` |
| Poll for conclusion (`7e66e244`) | `:413-447` |
| Timestamp for polling (`863daee5`) | `:398-400`, `:428` |
| Fix linting (`e3ff145e`, `c15b27bf`) | `:425` `_`, `:400` and `:431-432` quoting |
| Job timeout (`4459b6fc`) | `:356` `timeout-minutes: 20`, `:357` `permissions: { }` |

The change adds no command for someone to run.

Reading the claims the other way:

- **The allowlist hunk is not claimed (`:84`).** `slolatte` was added to the actor allowlist in `should-run`. This changes which PRs run the whole workflow (image build, GKE deployment, SaaS dispatch), and no commit message mentions it. It reads like a testing convenience carried into the change.
  - **Request:** claim it in a commit message, or move it to a change of its own.
- The workflow `name:` rename (`:5`) describes the job being added, so it is claimed along with that job.

## Item 3: boundaries, partitions, and the negative control

- **Two limits on the same wait, and the outer one fires first (`:356` vs `:424-445`).**
  - Three limits apply:
    - The job's `timeout-minutes: 20`.
    - The loop's 80 × 30 s sleeps, which is at least 40 minutes plus three `gh api` calls per iteration.
    - The downstream workflow's own timeout, which is set in `c8-cross-component-e2e-tests` and isn't in this repository.
  - The loop is the inner limit and never fires first. Before the loop starts, the 20 minutes have already paid for checkout, the Vault token and the dispatch.
  - So "Timed out waiting…" can never print. Any downstream run that takes longer than about 18 minutes ends with GitHub cancelling the job.
  - **Request:** derive one limit from the other. Either compute the loop bound from the job timeout, or set the job timeout above the loop's worst case. Also cite the line that sets the downstream run's timeout, or a run that shows how long it takes.
- **The wait is not tied to the run this job dispatched (`:398-400`, `:427-428`).** Two partitions are not handled:
  1. **Another dispatch to the same workflow.** A concurrent PR from this workflow, or any other sender of `repository_dispatch`, can create a run after `TRIGGER_TIME`. The loop then reports that run's result. It takes the newest of the 5 most recent runs, so it prefers the other run whenever that one is newer.
  2. **A run created before the timestamp.** `TRIGGER_TIME` is taken in a separate step after `curl` returns, and the filter uses strict `>` on seconds. A run created before that step, or within the same second, is never selected. The job then waits until it is killed.

  The earlier `head_sha` match in `7e66e244` was replaced, and no field of `client_payload` is used to find the run again.
  - **Request:** take the timestamp before the dispatch, and use `>=`. Also correlate on an identifier the payload carries, for example a unique id that the downstream `run-name` echoes, or say why only one dispatch can exist at a time.
- **A failed dispatch fails late and prints nothing (`:380-396`).** `curl` has no `--fail`, so a 401, 404 or 422 from the dispatch endpoint leaves the step green. The wait loop then finds no run, prints nothing per iteration, and is cancelled at 20 minutes with no message from the script. Run with `-f` (or `--fail-with-body`), it would fail in seconds with the HTTP status.
  - **Request:** add `--fail-with-body`, and print a line in each iteration that finds no run.
- **The control (taste).** A run of `workflow_dispatch` with `helmRepositoryDirName` other than 8.9 still sends `c8Version: "8.9"` and waits on `…_8_9.yml`. Nothing claims other versions, so this is a partition worth noting rather than a request.
- **Taste.** With `pipefail` from `shell: bash`, a single transient `gh api` error inside the loop fails the job at once and abandons the downstream run. Tolerating a failed poll would be more robust.

## Item 3a: level, placement, and the environment

- **The metrics step is not last (`:402-411`).** "Observe build status" runs before "Wait for downstream workflow to finish", so it records `job.status` as success before the result that matters exists. CLAUDE.md requires that step to be the job's last.
  - **Request:** move it after the wait step.
- The job sits beside its siblings in the same workflow, and the token action matches its other uses (`trigger-c8run-e2e-tests.yml:26`, `preview-env-smoke-test.yml`).
- **Taste.** `needs: format-identifier` (`:355`) is unused by this job.

## Item 4: names by content, not by position

`none` beyond the "first run" ordinal at `:426`, which is filed under Item 1. I checked the step names, the job id, and `job_name`.

## Item 5: the failure report

The downstream failure prints `Workflow run $RUN_ID status:` plus its conclusion, which is enough to find the run. The silent paths (failed dispatch, run not found) are filed under Item 3.

- **Taste.** Printing the run's `html_url` would save a lookup.

## Item 6: what the writer says it verified

None of the seven commits states a run of this workflow or of the downstream dispatch. Commits `7e66e244`, `863daee5` and `c15b27bf` suggest iteration, but no run or outcome is cited.

## Item 7: siblings of the change

- **`job_name` breaks the file's prefix (`:408`).** The new `job_name: trigger-saas-e2e` drops the `docker-build-helm-integration-` prefix that all 6 other `job_name` entries in this file carry (`:95`, `:125`, `:154`, `:183`, `:284`, `:315`). Metrics grouped by that prefix will miss this job.
  - **Request:** `docker-build-helm-integration-trigger-saas-e2e`.
- **Same `curl` pattern elsewhere (`trigger-c8run-e2e-tests.yml:43-47`).** It dispatches to the same repository with the same `curl` and no `--fail`. That job doesn't wait, so a failed dispatch there passes silently.
  - **Request:** fix it in this change, or name it as follow-up.
- The actor allowlist appears only in this file.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The wait is not tied to the dispatched run: another PR's run, or a run created before the timestamp | Substantive | `docker-build-helm-integration.yml:398-400,427-428` | 3 |
| 20-minute job limit makes the 40-minute loop and its message unreachable | Substantive | `docker-build-helm-integration.yml:356,424` | 3 |
| `curl` without `--fail`: a failed dispatch passes and the job hangs silently until cancelled | Substantive | `docker-build-helm-integration.yml:380` | 3 |
| "Observe build status" runs before the wait, so the reported status ignores the result | Substantive | `docker-build-helm-integration.yml:402` | 3a |
| The "first run" comment contradicts newest-first selection | Substantive | `docker-build-helm-integration.yml:426` | 1 |
| Coined term "SaaS Monorepo" | Substantive | `docker-build-helm-integration.yml:376` | 1 |
| Allowlist addition `slolatte` not claimed by any commit | Substantive | `docker-build-helm-integration.yml:84` | 2 |
| `job_name` lacks the file's `docker-build-helm-integration-` prefix | Substantive | `docker-build-helm-integration.yml:408` | 7 |
| Sibling c8run dispatch has the same `curl` without `--fail` | Substantive | `trigger-c8run-e2e-tests.yml:43` | 7 |
| No run of the workflow stated as evidence | Substantive | (commit messages) | 6 |
| "triggers" undersells a job that waits and fails on the result | Taste | `docker-build-helm-integration.yml:1,353` | 1 |
| Hard-coded 8.9 is ignored when `helmRepositoryDirName` changes | Taste | `docker-build-helm-integration.yml:389,422` | 3 |
| A transient `gh api` error aborts the wait | Taste | `docker-build-helm-integration.yml:427-432` | 3 |
| Unused `needs: format-identifier` | Taste | `docker-build-helm-integration.yml:355` | 3a |
| Print the downstream run's `html_url` | Taste | `docker-build-helm-integration.yml:433` | 5 |

Some checks could not be run here. `actionlint` and `conftest` are not installed, so the repository's offline gate didn't run (`yq` did parse the file). The drift script doesn't parse YAML. The downstream workflow (`playwright_saas_pr_trigger_monorepo_8_9.yml`, its timeout and its `run-name`) is in another repository and could not be read.
