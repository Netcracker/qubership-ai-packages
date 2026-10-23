# Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml` only)

The change adds one job, `trigger-saas-e2e`. It dispatches a smoke run to `c8-cross-component-e2e-tests` and then polls that run until it finishes. My recommendation is not to merge yet. Three problems can make the job wait on the wrong run, miss its run, or never report a result:

- **Wrong run:** it matches the most recent downstream run, not the run it started, so it can pick up another PR's run.
- **Missed run:** it records its timestamp after sending the dispatch.
- **No result:** the job timeout (20 min) is shorter than the poll loop it contains (40 min).

There was no task statement, so I took the claimed cases from the commit subjects alone; none of the commits has a body. No earlier report of this form exists. The change contains no code, so I used the §2a analogue for each item. The drift script ran and produced no output, because it does not parse YAML. Neither `actionlint` nor `conftest` is installed here, so I ran neither.

## Item 1: comments consistent with the code and with each other
Analogue used: what the file says about itself (header, names, step comments) checked against what the jobs do.
- **Line 422 vs line 356.** The comment `# Wait up to 40 min (80 x 30s)` contradicts `timeout-minutes: 20`, which commit 4459b6fc added. The runner kills the job at 20 minutes, minus the time spent getting the token and sending the dispatch. So the loop's own `Timed out waiting…` message and its `exit 1` never run; the job ends as *cancelled*. A reader trusts the 40-minute figure.
- **Line 1 and the job name `Trigger SaaS E2E tests`.** Both say the job *triggers* the tests. It actually blocks on the downstream result and fails when that run fails (lines 433–439). A reader expects a dispatch that returns immediately.
- **Line 409, `job_name: trigger-saas-e2e`.** Every other job in the file reports metrics as `docker-build-helm-integration-<job>` (lines 95, 125, 315, …). This name breaks that pattern, so the metric can't be traced to this workflow.
- I found no wording that narrates the change ("now", "no longer").

## Item 2: claimed cases covered
Analogue used: each case a commit subject claims, against the step that handles it.

| Claimed case | Step that handles it |
|---|---|
| add SaaS E2E smoke tests for AlwaysGreen (4662bcd1) | `Trigger repository_dispatch for SaaS Monorepo`, lines 376–397 |
| update versions (be150d28) | payload lines 392–395, now `SNAPSHOT` / `8-SNAPSHOT` |
| poll for conclusion (7e66e244) | `Wait for downstream workflow to finish`, lines 413–449 |
| add timestamp for polling (863daee5) | `Get trigger timestamp`, line 399, used at line 428 |
| add job timeout (4459b6fc) | line 356; it conflicts with the loop (Item 1) |
| fix linting (×2) | quoting at lines 400, 431–432 and the `_` loop variable; I could not confirm it lint-clean |

Two changes are not claimed by any subject:
- `slolatte` was added to the actor allowlist (line 84).
- A checkout step was added inside "update versions" (line 359–360). It is needed so the job can run the local `observe-build-status` action.

Under the "add timestamp for polling" row, the design reason (pick out the run this job started) is not met. The timestamp is taken **after** the `curl` returns (line 399 follows 376). Matching uses a strict `>` on timestamps with one-second precision (line 428). If the downstream run is created in the same second, or before `date` runs, the job never sees it.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the states the job can meet.
- **Two PRs running at once.** The `concurrency` group is per PR (line 46), so allowlisted PRs run in parallel. The query at lines 427–428 takes `head -n1` of runs created after `TRIGGER_TIME`. The API lists newest first, so this is the *latest* such run, which can be another PR's run. The payload carries `source_sha` (line 386), but the poll never matches on it. As a result, one PR can go green or red on another PR's result. Taking the oldest match is still not safe: the job should pick out its own run, for example by a unique id put in the payload and shown in the downstream run name, or by matching `source_sha`.
- **The dispatch fails** (401, 404 or 422). `curl` is called without `--fail` (line 379), so the step passes and the poll then waits until the job timeout. The sibling `trigger-c8run-e2e-tests.yml:42` has the same `curl`, but nothing waits after it there.
- **A temporary API error.** `defaults.run.shell: bash` makes GitHub run the step with `-eo pipefail`, and the script also sets `set -e`. One failed `gh api` call among about 240 over the wait fails the job.
- I found no evidence that any of these partitions was run (see Item 6).

## Item 3a: level, placement, and the environment
Analogue used: where the rule lives, and whether the repository's gates and conventions are met.
- **`Observe build status` is not the last step** (lines 402–411 come before the wait step). CLAUDE.md requires it to be the last step. It records the job's status *before* the downstream result is known, so a failure from the wait never reaches CI health metrics.
- **`needs: [build-and-push, format-identifier]`** (line 355): the job never reads `format-identifier`. This is harmless, but it adds a dependency for nothing.
- Placement matches the sibling `trigger-c8run-e2e-tests.yml`: same token action, same Vault paths, `permissions: { }`, and a timeout is set.

## Item 4: names by content, not by position
None. The step names and the comment at line 425 (`Grab the first run created after the trigger event`) name things by what they are. Note that this comment reads as "earliest", while the code takes the newest; that mismatch is filed under Item 3.

## Item 5: the failure report
Analogue used: what the job's output tells the reader.
- Line 438 prints `Downstream workflow failed: $CONCLUSION`, but not the run's URL or `RUN_ID`. Line 431 prints `RUN_ID` earlier in the log, so this is taste.
- Line 448, `Timed out waiting for downstream workflow to complete.`, never runs because of the 20-minute timeout (Item 1). It also doesn't say whether a run was ever found; "no run matched" and "run still in progress" call for different fixes.

## Item 6: what the writer says it verified
Neither the commits nor any description show a run of the job: no successful dispatch, no matched run, no red result from a failing downstream run. Since there is no evidence that the job can fail correctly, the cases in Item 3 are unverified.

## Item 7: siblings of the change
- `git grep` for the old workflow name `Docker Build and Helm Integration Test` finds no references in the repository. Required-check settings outside the repository may still use the old name; I could not check them.
- `trigger-c8run-e2e-tests.yml:42` makes the same `curl` call without `--fail`. Only this change follows the call with a wait, so it is out of scope here. It could be named as follow-up.
- The value `"8.9"` is hard-coded twice (`c8Version` at line 387, and `WORKFLOW_FILE=playwright_saas_pr_trigger_monorepo_8_9.yml` at line 423). The file already hard-codes `camunda-platform-8.9` (line 21), so this follows existing practice. Expect the values to go stale when the file is backported or `main` moves to 8.10.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Poll picks the newest run after the trigger time, which can be another PR's | Substantive | `docker-build-helm-integration.yml:427-428` | Match this job's own run: a unique id in `client_payload` shown in the downstream `run-name`, or a `source_sha` match |
| Timestamp taken after the dispatch, compared with strict `>` at one-second precision | Substantive | `:376-400`, `:428` | Record the time before the `curl`, or match by id as above |
| `timeout-minutes: 20` is shorter than the 40-minute loop; the timeout message never runs | Substantive | `:356`, `:422` | Raise the timeout above 40 min plus setup, or shorten the loop to fit, and keep the comment in step |
| `Observe build status` comes before the wait step, so the downstream result is never recorded | Substantive | `:402-411` | Move it to be the last step (CLAUDE.md) |
| A failed dispatch passes silently and leads into a full-length wait | Substantive | `:379` | `curl --fail-with-body` (or `-f`) |
| One temporary `gh api` error fails the job under `-eo pipefail` | Substantive | `:427-432` | Tolerate errors per poll (`|| true` / retry), and fail only on a terminal state or timeout |
| Header and job name say "trigger", but the job blocks on and reports the downstream result | Substantive | `:1`, `:354` | Say "triggers and waits for" |
| `job_name` doesn't follow the file's `docker-build-helm-integration-` prefix | Substantive | `:409` | `docker-build-helm-integration-trigger-saas-e2e` |
| No run shows the dispatch, the run matching, or a red result | Substantive | n/a | State a run of each case in the PR description |
| Allowlist addition and the checkout are not named in any commit subject | Taste | `:84`, `:359` | Mention them in the squash message |
| Unused `needs: format-identifier` | Taste | `:355` | Drop it |
| Failure message has no run URL | Taste | `:438` | Print `html_url` of the run |
| Hard-coded `8.9` / `_8_9.yml` | Taste | `:387`, `:423` | Derive from an input or env, matching `helmRepositoryDirName` |

This review did not run the workflow, `actionlint`, or `conftest` (none is available here). It did not check whether the downstream repository accepts the `run-saas-generation-smoke` event, the Harbor image tag as `zeebeVersion`, or the mixed `SNAPSHOT`/`8-SNAPSHOT` values. It did not check branch-protection settings that might depend on the old workflow name, and it did not review the prose for style alone.
