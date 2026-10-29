## Final review: `e3250e60..HEAD` (seven commits, one file)

**Scope and inputs.** No task statement was handed over, so the claimed cases come from the seven commit messages only: `add saas e2e smoke tests for alwaysgreen`, `update versions`, `poll for conclusion`, `add timestamp for polling`, `add job timeout`, and `fix linting` (twice). There is no previous report. I loaded `test-authoring` and `english-developer-style` from the given skills directory. The change is one YAML workflow, `.github/workflows/docker-build-helm-integration.yml`, so the item analogues in §2a apply. The drift script ran but printed nothing: it parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala` (`comment-drift.py:29`), so it could not see this file. Nothing was changed or committed.

### Item 1: comments consistent with the code and with each other

Analogue: the header and inline comments of the workflow.

- Line 1 (`# description:`) holds. `helm-deploy` sets `e2e-enabled: true` (line 332), and the new job triggers the SaaS smoke run.
- Line 424, `# Wait up to 40 min (80 x 30s)`, is false in effect. The job is capped at 20 minutes (line 356), so the loop never reaches its own timeout. See finding 1.
- Line 426, `# Grab the first run created after the trigger event`, names the run by position. See finding 9.

### Item 2: claimed cases covered

Analogue: a CI workflow has no tests, so detection means a run, and the change states none.

- Dispatch on PRs from listed actors: gated by `should-run` (lines 65–86). No run is stated.
- Pass path (exit 0) and fail path (exit 1), lines 434–441: no run is stated for either.
- Timeout path, lines 446–447: unreachable (finding 1).
- Run selection by timestamp, line 428: no run is stated (finding 2 is a likely defect in it).
- `update versions`: the diff in `be150d28` changes the payload values to `SNAPSHOT`, which matches the claim. The downstream repo is not in this repository, so I could not check that it reads them.

Finding 6 covers the missing run evidence.

### Item 3: boundaries, partitions, and the negative control

The wait loop's partitions are: run not yet found, run in progress, completed success, completed failure, timeout, and dispatch rejected. None has a run or a control in the change.

**Limits on the same quantity, the wait duration:**

| Limit | Value | Where set |
| --- | --- | --- |
| Outer: job timeout | 20 min | this file, line 356 (added by `4459b6fc`) |
| Inner: poll loop | 80 × 30 s = 40 min | this file, lines 424–425 |
| Environment default | 360 min | applies only when `timeout-minutes` is unset, so not here |
| Downstream run's own limit | unknown | other repo, not read |

The inner limit does not fire before the outer one at the defaults, which the form counts as a finding (finding 1).

### Item 3a: level, placement, and the environment

- The behavior exists only across the GitHub API and another repo, so no in-process test is owed.
- Placement: the observe step (lines 402–411) runs before the wait step (line 413). The repo's CLAUDE.md rule is that the last step of each job submits CI health metrics. See finding 4.
- This PR runs the new job only if its author is in the `should-run` list. I did not check whether the author is listed.
- `actionlint` and `conftest` are not on PATH, so the repo's workflow gates were not run. `yq` parses the file, and the `needs` graph is valid.

### Item 4: names by content, not by position

Only finding 9 (taste).

### Item 5: the failure report

The wait's timeout message does not say whether any run was found or what state the last run was in (finding 5). The fail-path message at line 439 does name the conclusion, which is correct.

### Item 6: what the writer says it verified

None stated. The commit messages give no run, no red run, and no statement of what `fix linting` ran. The change needs a run of the workflow, not a mutation verdict.

### Item 7: siblings of the change

- **`should-run` actor list:** `git grep` for `ce-dmelnych` finds one site, so adding `slolatte` has no sibling copy to update.
- **Dispatch `curl`:** the sibling `trigger-c8run-e2e-tests.yml` (lines 39–47) has the same `curl -X POST` with no `--fail`. The defect applies there too. I read that one sibling and did not count other dispatch callers.
- **`observe-build-status`:** the sibling jobs pass `job_name` and place the observe step last. The new job breaks that placement (finding 4).

### Findings

Labels: substantive findings are requests, and taste findings are the reviewer's preference, expected to be declined.

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The 20-minute job timeout ends the job before the 40-minute poll loop can time out. The comment "Wait up to 40 min" (424) and the timeout message (446–447) are unreachable. | substantive | `.github/workflows/docker-build-helm-integration.yml:356, 424–425, 446–447` | Derive the loop bound from the job timeout, or raise `timeout-minutes` above the loop bound plus setup time. Correct the comment to match. |
| 2 | `TRIGGER_TIME` is captured after the dispatch step. A downstream run created in the gap fails `created_at > TRIGGER_TIME` (428), so the loop never sees it. The window is unmeasured, so a run is needed to confirm. | substantive | `:380–400, 428` | Capture the timestamp before the `curl` at line 380. |
| 3 | `curl` has no `--fail`, so a rejected dispatch passes the step. The failure appears only as a poll that finds nothing until the job is killed. | substantive | `:380–396` | Use `--fail-with-body`, or check the HTTP status and fail with the response. Same defect at `trigger-c8run-e2e-tests.yml:39–47`. |
| 4 | The observe step runs before the wait, so `job.status` cannot reflect the wait's result. The health metric records success when the downstream E2E fails. The repo rule says the last step submits the metrics. | substantive | `:402–411` | Move the observe step to the end of the job, after the wait. |
| 5 | The wait prints nothing when no run is found, and its timeout message does not say the last state seen. A reader cannot tell "no run was created" from "still running". | substantive | `:426–447` | Print whether a run was found and its last status in the timeout message (`test-authoring` §7, applied as the wait's report). |
| 6 | No run evidence is stated for dispatch, the pass path, the fail path, the timeout path, or the timestamp selection. | substantive | commit messages; `:376–447` | State the runs in the PR description: a green downstream run and a failed one. Add a timed-out run if the bound stays. |
| 7 | The sibling `trigger-c8run-e2e-tests.yml` repeats the no-`--fail` `curl`. | substantive (follow-up) | `.github/workflows/trigger-c8run-e2e-tests.yml:39–47` | Fix in this change, or name it as a follow-up in the PR description. |
| 8 | The observe job name `trigger-saas-e2e` breaks the `docker-build-helm-integration-*` prefix used by the eight sibling jobs. | taste | `:408` | Use `docker-build-helm-integration-trigger-saas-e2e`. |
| 9 | The comment "Grab the first run" names the run by position. | taste | `:426` | "the newest run created after the trigger". |
| 10 | `8.9` is hard-coded in the workflow file name (422) and `c8Version` (389), while the `helmRepositoryDirName` input exists. | taste | `:389, 422` | Derive from the input, or leave as is. |

**Not checked:** the workflow was not run, and `actionlint` and `conftest` were not on PATH. The downstream repo, the `slolatte` login, and the GitHub App token's scopes were not read. The drift script does not parse YAML.
