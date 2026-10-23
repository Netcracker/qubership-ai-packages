## Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml`)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages alone. This is the first review of this change, so there is no previous report. The change is a GitHub Actions workflow with no code and no tests. Item 2a's analogues apply, and the test-authoring and doc-comment rules were read for their failure-report and wait-report sections. I loaded `test-authoring` and `english-developer-style`. No GitHub-workflow authoring skill is in the set, so none was loaded.

**Tools.** The drift script ran and printed nothing, because it does not parse YAML. I built actionlint v1.7.12 from the local module cache into the scratchpad. It reports one warning, `runs-on: gcp-perf-core-8-default` at line 193, which also exists at the base commit (line 192), so it predates this change. `conftest` is not installed and was not run. I did not use `gh` or curl.

### Item 1: comments consistent with code and with each other
- Finding (substantive): line 426, `# Grab the first run created after the trigger event`, says the run found is this dispatch's. The filter at lines 427–428 does not check the dispatch. See finding S2.
- Finding (substantive): line 424, `# Wait up to 40 min (80 x 30s)`, is true of the loop but not of the job. The job is capped at 20 minutes on line 356. See S1.
- Header line 1 is accurate: the Helm job sets `e2e-enabled: true`, and the SaaS job is present. The renamed workflow title has no references in `.github` or `docs`.
- No narrating words (`now`, `no longer`, `used to`).

### Item 2: claimed cases covered
Claims, from the commit messages:
- (a) dispatch SaaS smoke tests for AlwaysGreen (`4662bcd1`);
- (b) wait for the downstream conclusion (`7e66e244`, `863daee5`);
- (c) match only the run this dispatch started (`863daee5`, "triggered after");
- (d) the job is bounded (`4459b6fc`).

No case has a named detection. Success, downstream failure, no run found, and timeout are each untested, and a workflow's only detection is a run. Case (c) does not hold when two dispatches overlap (S2). This is finding S8, requested as a dispatch run from the branch that shows the success path and a forced failure path, named in the PR description.

### Item 3: boundaries, partitions, and the negative control
- Finding S1 (substantive): the inner poll limit is 80 × 30 s = 40 min (line 425). The outer job limit is `timeout-minutes: 20` (line 356). At the defaults the inner limit never fires, so the job is cancelled at 20 minutes and the "Timed out" message (line 446) never prints. The request is to derive one bound from the other, or set both in one place. Other limits on the path are the GitHub default job limit of 360 minutes, which does not bind here, and the downstream run's own duration, which this job does not bound.
- Finding S3 (substantive): `TRIGGER_TIME` is captured at lines 398–400, after the dispatch at lines 376–391 returns. The match at line 428 is `created_at > TRIGGER_TIME`. A downstream run created before the capture is never matched, and the poll times out. The request is to capture the timestamp before the dispatch step.
- The `should-run` gate is not skipped. The new job has no `if:` of its own, but it needs `build-and-push`, which needs the frontend jobs that need `should-run`, so the job is skipped transitively.
- Pre-existing state: the wait hard-codes `playwright_saas_pr_trigger_monorepo_8_9.yml` (line 417), a file owned by the other repository. If that file is renamed, every wait ends in the timeout. Not verifiable offline.
- The negative control (a run that must be ignored) is absent. Covered by S2 and S3.

### Item 3a: level, placement, and environment
- Finding S4 (substantive): the `Observe build status` step (lines 402–410) runs before the `Wait for downstream workflow` step (lines 413–446). Every other job in the file ends with the observe step, and CLAUDE.md requires that. Here the health record reports `job.status` before the wait, so a failed wait is recorded as success.
- Level: a workflow has no in-process level, so the gate is actionlint, run above. Only the pre-existing warning appears. The `conftest` policy gate was not run.
- Environment claims not checkable offline: the downstream `repository_dispatch` event type `run-saas-generation-smoke`, the workflow file name, and the App token's permission to read that repo's runs.

### Item 4: names by content, not by position
None. The step names, the job name, and the comments do not refer to positions. `the first run` on line 426 is list order, not a case ordinal.

### Item 5: the failure report
- Finding S6 (substantive): line 446 prints `Timed out waiting for downstream workflow to complete.` It does not say whether a run was found, which run ID it was, or the last status seen. A reader cannot tell "never found" from "still queued". test-authoring §7 requires a wait's failure to name the last state.
- The `Downstream workflow failed: $CONCLUSION` message (line 439) is adequate.

### Item 6: what the writer says it verified
None stated. The commits show only lint fixes and iteration on the polling. No red run, no dispatch run from the branch, and no mutation or lint evidence is named. Request is the same as S8.

### Item 7: siblings of the change
- No helper was changed, so no call sites were listed.
- Finding S7 (substantive, named as follow-up): `.github/workflows/trigger-c8run-e2e-tests.yml:43–47` uses the same curl dispatch without `--fail`, so the same silent-failure defect applies there.
- Finding S5 (substantive): the dispatch at lines 380–391 uses curl without `--fail` or a status check. A rejected request (401, 403, 422) passes, and the wait then fails as a 20-minute timeout. The payload also interpolates `needs.build-and-push.outputs.image-tag` (line 390), which for a `workflow_dispatch` comes from the free-text `version` input and can break the JSON.
- Taste (T1): line 408, `job_name: trigger-saas-e2e`, lacks the `docker-build-helm-integration-` prefix that all six sibling entries carry. The analytics grouping differs. The reviewer prefers the prefix.
- Finding S2 (substantive): the wait takes the newest `repository_dispatch` run in the window (`head -n1`, line 428) without checking the payload. Another PR's dispatch to the same workflow file, in the same window, is reported as this PR's result. The dispatch already sends `source_sha` (line 388), which the wait ignores. The request is to match on a value the downstream run exposes, after checking that it exposes one.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| S1: 20-minute job cap fires before the 40-minute poll bound | substantive | `.github/workflows/docker-build-helm-integration.yml:356`, `:424–425` | Derive the loop bound from the job timeout, or set both in one place |
| S2: wait can report another dispatch's run | substantive | same file `:426–428`, `:388` | Match on a value this dispatch sends, after checking that the downstream run exposes it |
| S3: trigger timestamp captured after the dispatch | substantive | same file `:376–400` | Capture the timestamp before the dispatch step |
| S4: observe step is not the last step | substantive | same file `:402–410`, `:413` | Move the observe step to the end of the job |
| S5: dispatch curl does not detect HTTP or payload failure | substantive | same file `:380–391` | Use `--fail-with-body` or check the status code |
| S6: timeout message names no last state | substantive | same file `:446` | Print the run ID and last status seen, or that no run was found |
| S7: same unchecked dispatch in the sibling | substantive (follow-up) | `.github/workflows/trigger-c8run-e2e-tests.yml:43–47` | Name as follow-up in the PR description |
| S8: claimed cases have no run evidence | substantive | commits `4662bcd1` through `4459b6fc` | Dispatch run from the branch, covering success and a forced failure, named in the PR |
| T1: `job_name` lacks the file's prefix | taste | same file `:408` | Use `docker-build-helm-integration-trigger-saas-e2e`; reviewer's preference |

**Not checked:** `conftest` was not run, and the change was not run (no `gh`). The downstream repo's dispatch contract, its workflow file, and the App's permissions were not verified. The `SNAPSHOT` version values in `be150d28` were not checked for intent.
