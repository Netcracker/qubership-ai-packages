# Final review: `e3250e60..HEAD`, seven commits to `.github/workflows/docker-build-helm-integration.yml`

**Inputs.** I had no task statement. The claimed cases come from the commit messages only, and all seven are subject lines with no body. The change is CI configuration, so I filled the form with the §2a analogues and said which one under each item. I loaded `english-developer-style` and `test-authoring` from the provided directory. No authoring skill for GitHub workflows was supplied. I ran `comment-drift.py e3250e60… HEAD` and it printed nothing, because it does not parse YAML. I extracted the two new `run:` scripts with `yq` and checked them with `shellcheck`: one SC2016 note (info only) on the dispatch body, where the single quotes are deliberate. `actionlint` and `conftest` are not installed here, so the repository's own gate was not run.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement the file makes about itself, the downstream repository, and its own limits.

- **Line 424**: `# Wait up to 40 min (80 x 30s)` is false. Line 356 sets `timeout-minutes: 20`, so the runner kills the job at about 20 minutes, half the stated wait. The `timeout-minutes` came in the last commit and the comment was not updated.
- **Line 426**: `# Grab the first run created after the trigger event` describes the wrong run. The runs API lists runs newest first, so `head -n1` on line 428 picks the **newest** run created after `TRIGGER_TIME`, not the first one. A reader would expect the earliest match.
- **Line 1** (taste): the description says the workflow "triggers SaaS E2E smoke tests", and line 353 names the job `Trigger SaaS E2E tests`. The job also waits for that run and fails with it, so the run is a gate, not just a trigger.
- No comment narrates the change ("now", "no longer"), and the header's `# owner:` is present.

## Item 2: claimed cases covered
Analogue used: for each claim in the commit subjects, the section of the file that implements it and the evidence that it works. A CI change has no test file, so the evidence would be a workflow run, and no run is cited.

| Claim (commit) | Where it is implemented | Evidence |
|---|---|---|
| Add SaaS E2E smoke tests for AlwaysGreen (`4662bcd1`) | `trigger-saas-e2e` job (352–411); `slolatte` added to the `should-run` list (84) | No run cited |
| Update versions (`be150d28`) | Payload now sends `SNAPSHOT` / `8-SNAPSHOT` (391–394); `checkout` added so the local `observe-build-status` action resolves | No evidence that the downstream workflow accepts these strings. That workflow is in `c8-cross-component-e2e-tests`, outside this repo |
| Poll for conclusion (`7e66e244`) | Wait loop (413–447) | No run cited, green or red |
| Add timestamp for polling (`863daee5`) | `trigger-time` step (398–400), filter on line 428 | Wrong ordering, see item 3 |
| Fix linting ×2 (`e3ff145e`, `c15b27bf`) | `for _`, quoted `$GITHUB_OUTPUT` and `"$RUN_ID"` | shellcheck is clean apart from the one info note; actionlint not run here |
| Add job timeout (`4459b6fc`) | `timeout-minutes: 20`, `permissions: { }` (356–357) | Conflicts with the 40-minute loop, see item 3 |

## Item 3: boundaries, partitions, and the negative control
Analogue used: the partitions are the trigger modes and the downstream outcomes; the boundaries are the time limits on the same wait.

**Correlation race (substantive)**
- The timestamp is taken after the dispatch: line 398 runs after the `curl` on line 380. GitHub can create the downstream run before `date` runs, or in the same second.
- Because the filter is a strict `>` on second-resolution strings (line 428), such a run is excluded. The job then waits on a later, unrelated run, or until it times out.
- Even with the order fixed, the filter only says "any `repository_dispatch` run of this workflow file after T". Two PRs, or this workflow plus any other dispatcher of `playwright_saas_pr_trigger_monorepo_8_9.yml`, running within the window will gate one PR on the other's result. Line 428 picks the newest run, which makes this more likely.
- The earlier version matched on `head_sha`, which does not work for `repository_dispatch` because the run's `head_sha` belongs to the target repo. The replacement dropped correlation entirely.
- **Request:** record the time before dispatching. Also send a correlation id in `client_payload` (for example `github.run_id`) and match on it, such as through the downstream `run-name`. Where that is not possible, document the race.

**Negative control (substantive):** no run shows the job going red when the downstream run fails. No run shows the dispatch failing either.

**Limits on the same wait (substantive):**
1. Job `timeout-minutes: 20` (line 356).
2. Loop: 80 × 30 s sleeps plus three `gh` calls per iteration, more than 40 minutes (lines 424–425).
3. The downstream workflow's own timeout. It is set in `c8-cross-component-e2e-tests`, which this repo does not contain.
4. The environment: the GitHub App installation token lives 1 hour. That is above both 1 and 2, so it is not the binding limit.

The inner limit (2) never fires before the outer one (1). The step's own `Timed out waiting…` message is therefore unreachable, and a slow downstream run shows up as a runner-cancelled job. The request is to derive the loop count from the job timeout, or set one from the other, and to show the downstream smoke run's typical duration and timeout. If that run regularly takes about 19 minutes or more, the job is always red.

**Earlier state (taste):** `concurrency.cancel-in-progress` (line 47) cancels this waiting job on a new push but leaves the downstream run going. Repeated pushes pile up orphan SaaS runs, which makes the correlation race above more likely.

## Item 3a: level, placement, and the environment
Analogue used: where the job lives, whether it matches the siblings, and the registration gate.

- **Wrong step order (substantive):** `Observe build status` (402–411) is placed **before** `Wait for downstream workflow to finish`. CLAUDE.md requires it to be the last step of each job. As placed, it reports `job.status` before the wait has run, so the job's actual failure never reaches CI health metrics.
- `job_name: trigger-saas-e2e` (line 408) does not follow the `docker-build-helm-integration-*` prefix every other job in the file uses (taste).
- `needs: format-identifier` (line 355) is unused because the job reads no output from it (taste).
- The `curl` reaching `api.github.com` from a workflow is outside this review's no-curl rule, which applied to me, not to the workflow.
- Gate: `actionlint` and `conftest` are not installed here, so the commit messages' linting claims are unverified locally. `yq` parses the file and `shellcheck` reports only the info note.

## Item 4: names by content, not by position
Analogue used: the change's own step names, job names, and comments. The step and job names say what they do. The only ordinal is "the first run" on line 426, and that is filed under item 1 because it is false rather than merely positional. Otherwise none.

## Item 5: the failure report
Analogue used: what a red job tells the reader.

- **Dispatch failure is silent (substantive):** `curl -X POST` (line 380) has no `--fail` or `-f`. A 401, 404 or 422 from the dispatch exits 0. The job then polls for 20 minutes and is killed, and the log never shows the HTTP error.
- **No link to the failed run (taste):** `Downstream workflow failed: $CONCLUSION` (line 439) prints the run id but not its `html_url`, so the reader has to find the run in another repository.
- **API errors end the wait (taste):** `bash -eo pipefail` plus `set -e` means one transient `gh api` error ends the whole wait, and the message gives no context.

## Item 6: what the writer says it verified
Analogue used: a green run and a red run cited in the change. The commit messages carry no body and cite no workflow run: no successful run, no failing downstream run, no failed dispatch. Nothing is stated.

## Item 7: siblings of the change
Analogue used: other workflows that dispatch to `c8-cross-component-e2e-tests` or use the same token action. `git grep` finds 9 other users of `generate-github-app-token-from-vault-secrets` and 4 other files mentioning dispatches. I read the one with the same shape, `.github/workflows/trigger-c8run-e2e-tests.yml`, and checked the chatops ones for `curl`, finding none.

`trigger-c8run-e2e-tests.yml` has the same `curl` with no `--fail` (line 42), so the item 5 defect applies there. It also calls the local `./.github/actions/observe-build-status` with no `actions/checkout`. Commit `be150d28` fixed exactly that here by adding a checkout. That workflow belongs to `@camunda/qa-engineering`, so the request is to name it as a follow-up in the PR description.

Two more coupled sites (taste): `c8Version: "8.9"` (line 389), `WORKFLOW_FILE=…_8_9.yml` (line 422) and the `camunda-platform-8.9` default (lines 21, 329) must all change together at the next minor. One `env` value would keep them aligned.

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | Comment claims a 40-minute wait; the job timeout is 20 minutes, so the inner timeout and its message never fire | Substantive | `docker-build-helm-integration.yml:356,424-425` | Derive the loop count from `timeout-minutes` or the reverse, fix the comment, and show the downstream run's duration and timeout |
| 2 | Comment says "first run"; `head -n1` on a newest-first list picks the newest | Substantive | `:426-428` | Fix the selection or the comment (moot if #3 adds a correlation id) |
| 3 | Timestamp is recorded after the dispatch, and the strict `>` misses a run created in the same second | Substantive | `:376-400,428` | Take the timestamp before the dispatch |
| 4 | No correlation to this dispatch: concurrent PRs or other dispatchers can gate this PR on another run | Substantive | `:427-428` | Send a correlation id in `client_payload` and match on it, or document the race |
| 5 | `Observe build status` is not the last step, so it reports status before the wait runs | Substantive | `:402-411` | Move it after the wait step |
| 6 | Dispatch `curl` lacks `--fail`, so a failed dispatch becomes a silent 20-minute timeout | Substantive | `:380` | Add `--fail-with-body` (or `-f`) |
| 7 | No run evidence: no green run, no red downstream run, no evidence the downstream accepts `SNAPSHOT` / `8-SNAPSHOT` | Substantive | commits `4662bcd1`…`4459b6fc` | Cite a green run and a red run (downstream failure) in the PR description |
| 8 | Sibling `trigger-c8run-e2e-tests.yml` has the same no-`--fail` curl and a local action with no checkout | Substantive | `trigger-c8run-e2e-tests.yml:42,48` | Name it as a follow-up in the PR description |
| 9 | Description and job name say "trigger", but the job also waits for and gates on the result | Taste | `:1,353` | e.g. "Run SaaS E2E smoke tests" |
| 10 | `job_name: trigger-saas-e2e` breaks the `docker-build-helm-integration-*` prefix | Taste | `:408` | Rename to `docker-build-helm-integration-trigger-saas-e2e` |
| 11 | Unused `needs: format-identifier` | Taste | `:355` | Drop it |
| 12 | Failure message has no link to the downstream run, and one transient `gh api` error ends the wait | Taste | `:427-440` | Print `html_url`; tolerate a failed poll iteration |
| 13 | Version 8.9 is hard-coded in three places that must change together | Taste | `:21,329,389,422` | Use one `env` value |
| 14 | `cancel-in-progress` leaves orphan downstream runs | Taste | `:45-47` | Document it, or cancel the downstream run where possible |

Not checked: I did not run the workflow, `actionlint`, or `conftest` (the last two are not installed), and I read nothing in `c8-cross-component-e2e-tests`. I made no style-only pass over the prose.
