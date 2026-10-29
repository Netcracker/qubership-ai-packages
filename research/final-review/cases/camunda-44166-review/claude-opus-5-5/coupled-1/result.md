# Final review: `e3250e60..HEAD` (7 commits, one file: `.github/workflows/docker-build-helm-integration.yml`)

There was no task statement, so I took the claimed cases from the seven commit messages alone. The change is a CI workflow, not code, so I filled the form using the §2a analogues. Skills loaded: `final-review`, `test-authoring`, `english-developer-style`. The authoring skill for this kind of artifact was not among the three I was allowed to load. I ran `comment-drift.py e3250e60… HEAD`: it exited 0 with no output, because it has no members to parse in YAML. `actionlint` and `conftest` are not installed here, so neither was run.

## Item 1: comments consistent with the code and with each other (analogue: statements the file makes about itself)

- **`# Wait up to 40 min (80 x 30s)` (line 423) is false at runtime.** The job sets `timeout-minutes: 20` (line 356). GitHub kills the job at 20 minutes, after about 35–38 iterations. A reader trusts the 40 min and plans downstream durations around it.
- **`# Grab the first run created after the trigger event` (line 426) describes the wrong selection.** The workflow-runs API returns newest first, so `select(...) | .id | head -n1` takes the *most recent* run created after `TRIGGER_TIME`, not the first one.
- The header `# description:` (line 1) and the new `name:` (line 5) are accurate: `helm-deploy` has `e2e-enabled: true`, and the new job triggers the SaaS tests. `git grep` found nothing else that refers to the old workflow name.
- No comment narrates the change.

## Item 2: claimed cases covered (analogue: the step that handles each claim, plus run evidence)

| Claim (commit) | Where it is handled | Evidence it works |
|---|---|---|
| add SaaS E2E smoke tests for AlwaysGreen | `trigger-saas-e2e` job, dispatch step lines 376–396 | none stated |
| update versions | payload `*Version: SNAPSHOT`, `optimizeVersion: 8-SNAPSHOT` | none stated |
| poll for conclusion | step "Wait for downstream workflow to finish" | none stated; a timeout and a wrong-run pick both fail it (Items 3, 3a) |
| add timestamp for polling | step `trigger-time` + `created_at > TRIGGER_TIME` filter | none stated; race in Item 3 |
| fix linting ×2 | `for _`, quoted `"$GITHUB_OUTPUT"` / `"$RUN_ID"` | lint not run here |
| add job timeout | `timeout-minutes: 20`, `permissions: { }` | conflicts with the 40-min loop (Item 3) |

There is also an unclaimed change: `"slolatte"` was added to the actor allowlist of `should-run` (line 84). No commit message mentions it. The writer should say whether this is meant to stay or was only there to test on their own PRs.

## Item 3: boundaries, partitions, and the negative control

- **The limit pair is inconsistent.** The same quantity, how long to wait for the downstream run, has two limits:
  - the job's `timeout-minutes: 20` (line 356, fixed in this file);
  - the loop bound of 80 × 30 s = 40 min (line 424, fixed in the script).

  The outer limit fires first. So the inner limit's report, `Timed out waiting for downstream workflow to complete.`, is never printed. The job is cancelled instead of failing with a reason. The 20 minutes also has to cover the token step and the dispatch. Request: derive one limit from the other, e.g. a loop bound below the job timeout with margin, or a timeout above 40 min. Then state the pair once.
- **The timestamp boundary is not handled.**
  - `trigger_time` is taken *after* the `curl` dispatch (lines 398–400), at one-second precision.
  - The comparison is the strict `created_at > TRIGGER_TIME`.

  A downstream run created in the same second as the timestamp, or before it, is excluded. Runner clock skew against GitHub's clock widens the gap. The loop then never finds its run, and either times out or picks up a later, unrelated run. Request: take the timestamp before the dispatch, minus a small margin, or use `>=`.
- **The concurrent-runs partition is not handled.**
  - The filter is only `event=repository_dispatch` + `created_at`.
  - Several allowlisted PRs, `workflow_dispatch` runs, or other repositories dispatching to `playwright_saas_pr_trigger_monorepo_8_9.yml` within the window produce runs this job cannot tell apart.
  - Because `head -n1` takes the newest, `RUN_ID` is recomputed on every iteration and can switch to another PR's run partway through.

  The PR then goes green or red on someone else's build. The payload already carries `source_sha`. Request: correlate on it, e.g. the downstream sets `run-name` from `client_payload.source_sha` and the filter matches `.display_title`, or say in the description that correlation is best-effort.
- **A failed dispatch is not detected.** `curl -X POST` has no `--fail` / `-f` (line 380). A 401, 404 or 422 from the dispatch API exits 0. The job then waits, and finds either nothing (timeout) or another PR's run (false result).
- **Pre-existing state.** `concurrency.cancel-in-progress: true` (line 47) cancels this job on a new push. The downstream run it already dispatched keeps running, and can be picked up by the next push's poller if its `created_at` falls after that push's `TRIGGER_TIME`. A dispatch issued late in the cancelled run can do this. No negative control (a run where the downstream fails) is mentioned.

## Item 3a: level, placement, and the environment (analogue: placement and gates)

- **`Observe build status` is not the last step.** It sits at lines 402–411, *before* "Wait for downstream workflow to finish". It records `job.status` before the outcome of the wait is known, so the CI health metric reports success for jobs that later fail on the downstream result. The repository's instructions require it to be the last step. Request: move it to the end.
- **`job_name: trigger-saas-e2e` breaks the file's naming pattern.** Every other job in the file uses `docker-build-helm-integration-<job>`. If anything filters the metric by that prefix, this job is missed. Labelled taste below.
- **A transient API error fails the job.** The `run:` script uses `set -e`, and `shell: bash` gives `-eo pipefail`. So one transient `gh api` error (rate limit, 5xx) inside `RUN_ID=$(...)` fails the job on the first iteration rather than retrying.
- **`format-identifier` is unused.** It is in `needs:` (line 355) but none of its outputs are used. Taste.
- `permissions: { }` plus `actions/checkout` matches the sibling jobs.
- The lint gates (`actionlint`, `conftest`) could not be run offline here.

## Item 4: names by content, not by position

None. The step names (`Get trigger timestamp`, `Wait for downstream workflow to finish`) and the variables (`TARGET_REPO`, `WORKFLOW_FILE`, `TRIGGER_TIME`) name things by content. The one ordinal-like word is "first" in the comment at line 426, which is filed under Item 1 because it is wrong, not stale.

## Item 5: the failure report (analogue: what a failure tells the reader)

- **A wait cut short by the job timeout prints nothing.** Because of Item 3, the message the job is meant to print on timeout never appears, and the run shows only "cancelled".
- **The run is identified only by ID.** On success or failure the log prints `Workflow run $RUN_ID status: …` and `Downstream workflow failed: $CONCLUSION` but never the run URL (`html_url`). The reader has to build the link by hand to find the failing E2E run. Request: print `https://github.com/$TARGET_REPO/actions/runs/$RUN_ID` once the run is found. Taste.
- **A missed run looks like a slow one.** When no run is found, nothing is logged per iteration, so "never found" and "found but still running" look the same until the timeout.

## Item 6: what the writer says it verified

None stated. No commit message or description cites a run of this workflow, with either a passing or a failing downstream run, or a lint run. The commit "fix linting" implies `actionlint` reported something, but its output is not given.

## Item 7: siblings of the change

`git grep` for `c8-cross-component-e2e-tests` and `/dispatches` finds two siblings:

- **`.github/workflows/trigger-c8run-e2e-tests.yml:42–47`** dispatches with the same `curl -X POST` and no `--fail`, so it has the same silent-dispatch-failure defect. It is fire-and-forget, so there is no wrong-run selection. Request: name it as a follow-up.
- **`.github/workflows/preview-env-smoke-test.yml`** checks out the e2e repo and runs Playwright in-process. That avoids dispatch and polling altogether, which is an alternative design worth naming in the description.

The hardcoded versions agree with the file's existing ones: `c8Version: "8.9"` and `WORKFLOW_FILE=…_8_9.yml` match `camunda-platform-8.9` (lines 21, 329). All have to move together on the next minor version; that is not a defect now.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Job timeout of 20 min is shorter than the 40-min loop the comment promises; the timeout message never prints | substantive | docker-build-helm-integration.yml:356, 423–424 | Derive one limit from the other and state the pair once |
| `Observe build status` runs before the wait step, so the metric misses the downstream result | substantive | :402–411 | Move it to be the last step |
| Trigger timestamp is taken after the dispatch and compared with strict `>` at 1 s precision, so the run can be missed | substantive | :398–400, 428 | Take the timestamp before the dispatch (with margin) or use `>=` |
| Run selection uses only event + time, picks the newest, and is recomputed each loop, so it can follow another PR's run | substantive | :426–428 | Correlate on `source_sha` (e.g. downstream `run-name`), pin `RUN_ID` once found, or document it as best-effort |
| Comment "Grab the first run" describes newest-first selection | substantive | :426 | Correct the comment, or the selection |
| `curl` dispatch has no `--fail`, so a rejected dispatch passes silently | substantive | :380 | Add `--fail-with-body` (and the same follow-up for trigger-c8run-e2e-tests.yml:42) |
| One transient `gh api` error fails the job under `set -e`/pipefail | substantive | :427–431 | Tolerate per-iteration API errors and retry |
| No evidence of a run of the new job (pass or fail) or of lint output | substantive | — | State the run, or the run links, in the description |
| `"slolatte"` added to the allowlist without mention | substantive | :84 | Say whether it is intended to stay |
| `job_name` breaks the `docker-build-helm-integration-*` pattern | taste | :408 | Rename to `docker-build-helm-integration-trigger-saas-e2e` |
| `format-identifier` in `needs` but unused | taste | :355 | Drop it from `needs` |
| Failure log has no run URL | taste | :432–439 | Print `html_url` once found |

What this review did not check: the workflow was not run, `actionlint` and `conftest` were not run (not installed), the downstream workflow in c8-cross-component-e2e-tests was not read, and there was no style-only pass over the prose.
