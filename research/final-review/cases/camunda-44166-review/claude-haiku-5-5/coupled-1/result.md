# Final review: `e3250e60..HEAD` (seven commits, one workflow file)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages: "add saas e2e smoke tests for alwaysgreen", "poll for conclusion", "add timestamp for polling", "add job timeout", "update versions", and two "fix linting". No previous report exists. The change touches only `.github/workflows/docker-build-helm-integration.yml` (+100/−3), so §2a's analogues apply. The drift script ran and printed nothing (exit 0), because it parses no members from YAML. `actionlint` and `conftest` are not installed, so the workflow lint gates were not run. `yq` parsed the file. The skills I loaded were `english-developer-style` and `test-authoring`. No `authoring` skill exists for a workflow file, so §2a's doc-comment analogue was not used.

## Item 1: comments consistent with the code and with each other
Analogue: the header `description`, the step names, and the in-file comments.
- Finding S1 is a comment that is false at runtime. `# Wait up to 40 min (80 x 30s)` (line 424) does not hold, because the job is capped at 20 minutes (line 356).
- The header claim "runs Helm integration and E2E tests" is backed by `e2e-enabled: true` at line 331, which is unchanged.
- The name says "Helm Deploy" and the description says "Helm integration". This is a naming mismatch, labeled taste below.
- No comment narrates the change.

## Item 2: claimed cases covered
Analogue: the claimed cases are the commit-message claims, and the test is a run of the job that exercises each one. There are no tests in this change.
- Claimed and unevidenced: the dispatch with its payload, the wait branch for `success`, the wait branch for `failure`, and the timeout branch. None has a test or a stated run. Finding S6.
- "add job timeout" claims to bound the job, but the bound contradicts the wait loop (S1).
- "add timestamp for polling" claims the timestamp makes the poll correct, but it is captured after the dispatch (S2).

## Item 3: boundaries, partitions, and the negative control
Limits on the same quantity, which is wall-clock time for the wait:
- Job `timeout-minutes: 20` (line 356) is set in this file.
- The poll loop, `for _ in {1..80}` with `sleep 30` (lines 425 and 434 region), allows 40 minutes. It is set in the step script.
- The environment default is 360 minutes for a job without `timeout-minutes`, which does not apply here.
- At the defaults, the 20-minute outer limit fires before the 40-minute inner one. The "Timed out" message (line 446) is unreachable, and the job's failure hides the poll's report. Finding S1.

Trigger ordering is a boundary too. Finding S2 is the boundary where the downstream run is created before the timestamp.
- The negative control is missing. No run shows the success path or a failure that the same wait reports differently. Finding S6.
- No state from an earlier version is read or replaced, so that sub-item does not apply.

## Item 3a: level, placement, and the environment
- The behavior crosses the GitHub API boundary, so an in-process test is not owed. The CI job is the only place that observes it, and the reviewer cannot run it offline.
- The job runs only on `workflow_dispatch` or on a PR by an allowlisted actor, which I did not verify. Finding S6 asks for a run from a PR branch.
- No new test class or fixture is involved.

## Item 4: names by content, not by position
- None. Step and job names are by content. The comment "the first run created after the trigger event" names the run by its creation, not by an ordinal.

## Item 5: the failure report
- S5: the timeout message (line 446) does not say whether a run was ever found, or what its last status was. A red-build reader cannot tell "dispatch never picked up" from "stuck in progress". This is the wait rule in `test-authoring` §7.
- S4: the dispatch's HTTP result is not checked (see Item 7 and S4), so a rejected dispatch produces the same timeout message.
- The downstream failure message (line 439 region, `Downstream workflow failed: $CONCLUSION`) is fine.

## Item 6: what the writer says it verified
- None stated. The commit messages show lint fixes only. No red run, no run of the job, and no run of the wait branches is recorded. I did not run the job, which is the writer's evidence to state. Finding S6.

## Item 7: siblings of the change
- The helper relied on is `./.github/actions/observe-build-status`. Its `job_name` input exists (`action.yml`). It has 131 call lines across 52 files, and this change does not alter it. The new call site is line 402.
- Other jobs in the file end with the observe step. The new job does not (S3). Ordering is fixed by CLAUDE.md, so it is a finding.
- The dispatch without `--fail` has a sibling in `trigger-c8run-e2e-tests.yml` lines 43–48 with the same pattern. That defect predates this change, so it is named as a follow-up, not a finding against this change. S4 covers the new site.
- The `ce-dmelnych` allowlist string appears only in this file. The workflow's display name is not referenced elsewhere in the repository. Neither is a sibling copy.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| S1 | Job timeout (20 min) is below the poll budget (40 min); the poll's timeout message and the "40 min" comment cannot take effect at the defaults | substantive | `docker-build-helm-integration.yml:356`, `:424–425`, `:446` | Derive the loop from the timeout, or raise `timeout-minutes` above dispatch + poll + observe (at least 45) |
| S2 | Trigger timestamp is taken after the dispatch, so the downstream run can be created before it and `created_at > TRIGGER_TIME` never matches | substantive | `:380`, `:400`, `:428` | Capture the timestamp before the `curl`, and compare with `>=` because the value has second precision |
| S3 | `Observe build status` is not the job's last step, against the CLAUDE.md rule and every sibling job | substantive | `:402` (wait step at `:413`) | Move the observe step to the end of the job |
| S4 | `curl` lacks `--fail`, so a rejected dispatch exits 0 and the job polls until the timeout | substantive | `:380–392` | Add `--fail-with-body` or check the HTTP status, and fail the step on rejection |
| S5 | The timeout message does not say whether a run was found or its last status, against the wait rule in `test-authoring` §7 | substantive | `:446` | Print whether `RUN_ID` was found and the last `STATUS` seen |
| S6 | Claimed success, failure, and timeout branches, and the dispatch payload, have no run and no test, and no evidence is stated | substantive | whole job, `:349–` | Name a run of the job from a PR branch that shows the success path and one failure branch |
| T1 | `slolatte` is added to the `should-run` allowlist, which no commit message or description names | taste | `:84` | Name the change in the PR description |
| T2 | Name says "Helm Deploy"; description says "Helm integration" | taste | `:5`, `:1` | Pick one term; I prefer "Helm integration", which matches the job it runs |

Not findings: the `permissions: { }` on the new job matches the rest of the file, and the `needs` gate is transitive through `build-and-push`. The `image-tag` output and `format-identifier` exist.

**Not checked:** I did not run `actionlint`, `conftest`, or the job. The `playwright_saas_pr_trigger_monorepo_8_9.yml` target and the GitHub App's permissions on the downstream repo are not verifiable offline. I did not read the downstream repo, so whether the dispatch payload is accepted is unknown.
