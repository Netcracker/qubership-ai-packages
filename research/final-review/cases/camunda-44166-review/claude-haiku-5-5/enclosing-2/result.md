## Final review: `e3250e60..HEAD` (seven commits, one file)

**Scope.** The change is seven `ci:` commits to `.github/workflows/docker-build-helm-integration.yml`. There is no task statement, so the claimed cases come from the commit messages: `add saas e2e smoke tests for alwaysgreen`, `update versions`, `poll for conclusion`, `add timestamp for polling`, `fix linting` (twice), and `add job timeout`. The net diff adds the `trigger-saas-e2e` job and the `slolatte` actor to an allowlist. No previous report exists, so there is no table of prior findings. Nothing was changed or committed.

**Tooling.** The drift script ran and printed nothing. It parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala`, so this YAML file is outside its reach. `yq` parses the file. `actionlint` and `conftest` are not installed here, so neither was run. The Rego policy was read where it was relevant.

### Item 1: comments consistent with the code and with each other
Findings:
- The comment `# Wait up to 40 min (80 x 30s)` (line 424) is false in effect. The job is capped at 20 minutes (line 356), so the 40-minute bound never runs. See F2.
- The comment `# Grab the first run created after the trigger event` (line 426) is wrong. The runs list is newest first, and `head -n1` takes the newest matching run. See F3.
- The header `# description:` (line 1) matches the body. The helm job has `e2e-enabled: true`, so "Helm integration and E2E tests" holds.

### Item 2: claimed cases covered
- *Dispatch* (commit `add saas e2e smoke tests`): no test or run evidence is stated. The `curl` has no `--fail`, so a rejected dispatch still passes the step. See F4.
- *Versions* (commit `update versions`): the commit message reads as a version bump. The net effect is that `operateVersion`, `tasklistVersion`, `connectorsVersion` and `optimizeVersion` move from pinned alphas (`8.9.0-alpha3`, `8.9.0-alpha3.1`) to floating `SNAPSHOT` values (lines 391–394). The downstream E2E now runs against moving builds. See F5.
- *Poll for conclusion* and *timestamp for polling*: no test covers the wait logic. See F6.
- *Job timeout*: `timeout-minutes: 20` (line 356) is set, but it is shorter than the wait loop it bounds. See F2.
- *Fix linting*: the lint check is a consistency gate, not evidence of behaviour.

Commands in the changed file, with outcomes:
- `curl -X POST …/dispatches` (lines 380–388). The outcome is an accepted dispatch. No documented form exists. The sibling `trigger-c8run-e2e-tests.yml` runs the same form.
- `gh api …/runs?event=repository_dispatch&per_page=5 --jq …` (lines 427–428). The outcome depends on the App token's `actions: read` scope on the target repo. That scope is set outside this file and was not checked.

### Item 3: boundaries, partitions, and the negative control
- Limits: the wait loop (80 × 30 s, roughly 40 minutes) sits inside the job's `timeout-minutes: 20`. The job limit fires first, and the loop's own "Timed out" message (line 446) is unreachable. The loop should be derived from the timeout, or the timeout raised past it. See F2.
- Partitions the wait must handle, none tested: run not yet visible, run in progress then success, run in progress then failure, no run ever, and the timeout. See F6.
- Negative control: none. The change reads no state from an earlier version, so the inherited-state question does not apply.

### Item 3a: level, placement, environment
- The wait logic is shell, so the smallest level is a local run of the step's script with a stubbed `gh`. Nothing in the change runs at that level. See F6.
- The new job sits beside its siblings in the same file, which is the right placement.

### Item 4: names by content, not position
- The comment `# Grab the first run created after the trigger event` (line 426) names the run by position, and the position is wrong. This is reported once, as F3, not twice.

### Item 5: the failure report
- No assertions are involved. The messages at lines 435–446 print the run id, status and conclusion. The "Timed out" message never prints under the 20-minute job cap (F2).

### Item 6: what the writer says it verified
- Neither a red run nor a successful run of the new job is stated in the commits or the change. The `fix linting` commits show only lint passes. The sequence `poll for conclusion`, `add timestamp for polling`, `fix linting` suggests iteration without a stated end-to-end run. See F6.

### Item 7: siblings of the change
- `observe-build-status` is the last step in every other job of this file. The new job breaks that pattern. See F1.
- `trigger-c8run-e2e-tests.yml` has the same `curl` without `--fail`. The fix belongs there too, or the description should name it as follow-up. See F4.
- The workflow name changed (line 5). Grep finds no in-repo reference to the old name. Required-check names held outside the repository cannot be checked from here.
- `slolatte` was added to the actor allowlist (line 84). No commit message names it. See F8.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. The `observe-build-status` step runs before the wait step, so it is not the job's last step. It records status before the downstream outcome exists, and it misses a timeout cancellation. | substantive | `.github/workflows/docker-build-helm-integration.yml:402–411` | Move the observe step to the end of the job, after the wait step, as the other jobs do. The repository's CI rule requires the last step to submit health metrics. |
| F2. The wait loop runs for about 40 minutes (`80 x 30s`, comment "Wait up to 40 min"), but the job is capped at 20 minutes. The cap fires first, so the timeout message never prints, and a slow downstream run reports as cancelled. | substantive | `:356`, `:424–425`, `:446` | Derive one from the other: raise `timeout-minutes` past the loop plus the trigger and observe steps (about 45), or cut the loop to fit 20 minutes. |
| F3. The run lookup picks the newest matching run, not the first created after the trigger, and it does not identify this dispatch. Concurrent PRs dispatch the same workflow, so the job can report another PR's conclusion. The timestamp is taken after the dispatch, and the strict `>` at one-second resolution can exclude the run. | substantive | `:380–400`, `:426–428` | Take the timestamp before the dispatch. Match the run by a value that identifies this dispatch, such as a field the downstream workflow prints in its run name. Correct the comment either way. |
| F4. The dispatch `curl` has no `--fail`, so a 4xx or 5xx response passes the step. The failure appears only as a timeout 20 minutes later. | substantive | `:380–388`; sibling `.github/workflows/trigger-c8run-e2e-tests.yml:46–48` | Add `--fail-with-body` (or check the status code). Fix the sibling too, or name it as follow-up. |
| F5. The commit `update versions` replaces pinned alpha versions with floating `SNAPSHOT` values. The message reads as a version bump, and the downstream now tests moving builds. | substantive | `:391–394`; commit `be150d28` | Name the change in the commit or PR description: the downstream now resolves `SNAPSHOT` builds, not `8.9.0-alpha3`. |
| F6. The wait logic has no test, and no run of the new job is stated. The branches (no run, success, failure, in progress, timeout) are unexercised. | substantive | `:413–446` | Run the step's script locally with a stubbed `gh` covering success, failure, no run, and timeout, and paste the output. Or state a green run of the job. |
| F7. The `job_name` passed to the observe action (`trigger-saas-e2e`) drops the `docker-build-helm-integration-` prefix that the other six calls in the file use. | taste | `:408` | Use the prefixed name, or accept the current one. The reviewer prefers the prefix; expect this to be declined. |
| F8. `slolatte` was added to the actor allowlist that gates the build. No commit names it, so a reader cannot tell it is intended. | taste | `:84` | Name the allowlist change in a commit message or the description. The reviewer cannot judge whether it is meant. |

### What the review did not check
The workflow was not run, `actionlint` and `conftest` were not installed, and the drift script does not parse YAML. The downstream repo's workflow and the App token's permissions were not visible, and no `gh` or browser access was used.
