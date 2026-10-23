# Final review: `e3250e60..HEAD` (seven commits, one file)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages: "add saas e2e smoke tests for alwaysgreen", "update versions", "poll for conclusion", "add timestamp for polling", "fix linting" (twice), and "add job timeout". No previous report exists, so §4's table is omitted. The change touches one file, `.github/workflows/docker-build-helm-integration.yml`, and has no tests. I treated the workflow as code, since it runs. The drift script ran and printed nothing, because the parser finds no members in YAML. `actionlint` and `conftest` are not installed, so I did not run them. `yq` parses the file. I loaded `english-developer-style` and `test-authoring`. The doc-comment skill does not apply to YAML comments, and no workflow authoring skill was supplied.

### Item 1: comments consistent with the code and with each other
- Line 424, `# Wait up to 40 min (80 x 30s)`, is false in effect. The job is capped at 20 minutes (line 356), so the loop never reaches its own timeout. See F2.
- Line 426, `# Grab the first run created after the trigger event`, refers to a run by position. See F3.
- Workflow header (lines 1 and 5): "runs Helm integration and E2E tests" holds, since `helm-deploy` sets `e2e-enabled: true`. The other comments are unchanged and still true.

### Item 2: claimed cases covered
- **Claimed cases and tests.** The repository has no test for this workflow. Each claimed case is covered only by a run that the change does not record. The dispatch, the wait for conclusion, the timestamp and the job timeout have no test, and no run ID is named. See F8.
- **Command lines the change runs, with outcome:**
  - Line 380, `curl -X POST …/dispatches`, promises a downstream run. No equivalent form runs elsewhere in the repository, so the answer is `none`. Without `--fail`, an HTTP error still exits 0. See F4.
  - Line 400, `date -u`, gives the trigger time. It is taken after the dispatch. See F1.
  - Lines 427–428, `gh api …/runs?event=repository_dispatch&per_page=5 --jq …`, promises the first run after the trigger. Answer `none`. The filter has no check on which dispatch a run came from. See F3.
  - Lines 431–432, `gh api …/runs/$RUN_ID --jq .status` and `.conclusion`. Answer `none`. These are the only readings of the outcome, and they are correct once a run is found.

### Item 3: boundaries, partitions, negative control
- **Limits on the same work.**
  - The job cap, `timeout-minutes: 20` (line 356), was set in this change. It encloses the loop, which allows 80 × 30 s = 40 min (line 424). The cap fires first. See F2.
  - The workflow `concurrency` block (lines 45–47) cancels this job on a new push to the same PR. That is expected, but it does cut the wait short.
  - The downstream run's own duration is not in this repository.
- **Partitions the wait must cover.** No stated run covers these: run not found, found and successful, found and failed, still running at the cap, and dispatch rejected. See F4 and F5.
- **Pre-existing state.** The change reads no earlier state. The workflow `name:` changed. Nothing in the repository refers to the old name, but branch protection or dashboards cannot be checked offline.

### Item 3a: level, placement, environment
- The wait loop is observable in one shell process with `gh` and `date` stubbed. No test exists at that level, so F8 applies.
- The PR's own run exercises the job. The workflow file is in `pull_request.paths`, and the author is in the actor list.
- The App token (lines 363–373) passes no `permissions:` input. Whether it may dispatch to, and read runs in, `c8-cross-component-e2e-tests` depends on the App installation. I could not check that offline.

### Item 4: names by content
- Line 426 names the run by position, "the first run". The defect is F3; the request is to name the run by its content.
- No other name, case id or message refers to a thing by position.

### Item 5: the failure report
- The loop prints nothing until a run is found. "No run matched" therefore looks the same as "still queued". The timeout message (line 448) names neither a run nor the last state nor the trigger time. See F5.

### Item 6: what the writer says it verified
- Not stated. The commits contain no red run, no run ID and no statement that `actionlint` or `conftest` ran. CLAUDE.md requires both for workflow changes. Neither is installed here, so I did not run them.

### Item 7: siblings
- `observe-build-status` is called from 48 workflow files. The six other jobs in this file place it last. The new job does not. See F6.
- The `should-run` actor list (lines 70–84) appears only in this file. The new actor is therefore not copied elsewhere, but see F7.
- The app-token action at `@main` is used in nine other workflows. Same pattern, no finding.
- Other `curl -X POST` sites: `c8run-build.yaml` lines 202 and 339. I did not read them, so I cannot say whether they have the same missing `--fail`.
- The version `8.9` appears in three places. See T2.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. The trigger timestamp is taken after the dispatch. A downstream run created before `TRIGGER_TIME` is never matched, and the job waits to its cap with no message. | substantive | `docker-build-helm-integration.yml:380`, `:398–400`, `:416` | Take the timestamp before the dispatch step. |
| F2. The job cap of 20 min (line 356) is shorter than the 40-min loop (line 424). The job is killed, and the timeout message at line 448 never runs. | substantive | `:356`, `:424`, `:448` | Derive one from the other: raise the job cap above the loop plus setup (about 45 min), or cap the loop by the job's remaining time. Name the downstream duration you want. |
| F3. `head -n1` (line 428) takes the newest run after the trigger time, with no check on which dispatch it came from. Other PRs' AlwaysGreen runs share the event and workflow file, so this job can report another PR's result. The run object does not carry `client_payload`. | substantive | `:426–428` | Match on a value the downstream run shows for this dispatch, such as a run name or head SHA set from `source_sha`. That workflow is in `c8-cross-component-e2e-tests` and cannot be read here. |
| F4. `curl` (line 380) has no `--fail`. An HTTP error still exits 0, so the step passes and the wait runs to the cap. | substantive | `:380–393` | Use `--fail-with-body`, or check the status code. |
| F5. The loop is silent until a run is found, and the timeout message (line 448) names no run, last state or trigger time. "No match" looks like "still queued". | substantive | `:425–448` | Log the trigger time and each iteration's match count. Name the last state and the trigger time in the timeout message. |
| F6. The observe step (lines 402–408) is not last. It runs before the wait and reads `job.status` while the job is still in progress. The health metric therefore records success even when the downstream run fails later. CLAUDE.md requires the step to be last. | substantive | `:402–408`, `:413–449` | Move the observe step below the wait, as the other six jobs do. |
| F7. The actor allowlist gains `slolatte` (line 84), which gates the whole build. No commit in the range mentions it. | substantive | `:84` | Name it in the PR description, or split it out. |
| F8. The wait-for-conclusion and fail-on-failure behavior, and the other claimed cases, have no test and no recorded run. | substantive | `:413–449` | State a run ID of this job with a green downstream run, one with a failed run, and one that times out. Put the wait loop under a stubbed-`gh` shell test. |
| T1. The analytics `job_name` `trigger-saas-e2e` (line 408) lacks the `docker-build-helm-integration-` prefix that the other six `job_name` values use. | taste | `:408` | Use the prefix, or keep it separate on purpose. Expect this to be declined if the separation is deliberate. |
| T2. `"c8Version": "8.9"` (line 389) and `playwright_saas_pr_trigger_monorepo_8_9.yml` (line 422) are fixed, while the helm directory is a dispatch input (line 21). | taste | `:21`, `:389`, `:422` | Derive the 8.9 values from the helm input, or state that they are fixed on purpose. |

**Not checked:** the workflow was not run, `actionlint` and `conftest` were not run because neither is installed, and the downstream workflow, the App token's permissions and the branch protection were not available offline.
