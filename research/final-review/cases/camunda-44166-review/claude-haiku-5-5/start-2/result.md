## Final review: `e3250e60..HEAD` (7 commits, one file)

**Scope and inputs.** The change is one file, `.github/workflows/docker-build-helm-integration.yml`, which adds a `trigger-saas-e2e` job. No task statement was handed over, so the claimed cases come from the commit messages alone, as the skill allows. No previous report exists, so there is no table over earlier findings. The drift script ran and printed nothing, because a YAML workflow has no members to parse. Under §2a the analogues are used: the workflow header and step comments stand in for doc comments, the commit messages for the claimed cases, and the other workflows in `.github/workflows/` for siblings. I loaded `test-authoring` and `english-developer-style` from the skills directory and used them for the wait-failure and comment rules. `yq` parses the file. `actionlint` and `conftest` are not installed here, so the CLAUDE.md lint gates were not run.

### Item 1: comments consistent with the code and with each other
Findings:
- Line 424, `# Wait up to 40 min (80 x 30s)`: the job's `timeout-minutes: 20` (line 356) ends the job before the loop can reach 40 minutes. The comment states a wait the job cannot deliver.
- Line 427, `# Grab the first run created after the trigger event`: the list is newest-first (`per_page=5`), and `head -n1` takes the newest matching run, not the first.

### Item 2: claimed cases covered
- `7e66e244 poll for conclusion` → "Wait for downstream workflow to finish" (line 413). No test or run covers the success, failure, timeout, or no-run paths.
- `863daee5 add timestamp for polling` → `trigger-time` (line 399).
- `4459b6fc add job timeout` → `timeout-minutes: 20` (line 356). This is the change that cuts the poll short (Item 3).
- `be150d28 update versions` → `"c8Version": "8.9"` (line ~387), `WORKFLOW_FILE ..._8_9.yml` (line 422), and the `camunda-platform-8.9` input default. These agree with each other.
- `4662bcd1 add saas e2e smoke tests` → the dispatch (lines 380–392). Nothing shows that the dispatch reaches the downstream repo; no run is cited.
- `fix linting` (two commits): no lint-only change is visible in the net diff.

Finding: the claimed dispatch and polling behavior has no evidence in the commits, and the failure paths have no case at all.

### Item 3: boundaries, partitions, and the negative control
- Limits: the inner poll budget is 80 × 30 s = 40 minutes, the job budget is 20 minutes, and the job budget also covers checkout, token generation, dispatch, and the observe step. The job budget fires first at every setting. The request is to derive one from the other: set the job timeout past the poll budget plus setup time, or shorten the poll to fit.
- Partitions for the wait: downstream success, downstream failure, downstream still running at the limit, dispatch rejected, no run found. Only the first and second are coded, and neither is exercised.
- Run correlation: the poll takes any run of `playwright_saas_pr_trigger_monorepo_8_9.yml` created after `TRIGGER_TIME`. Other PRs dispatch the same event type, so a concurrent PR's run can be reported as this PR's result.
- Timing: `TRIGGER_TIME` is read after the dispatch (line 399). A downstream run created before that read is filtered out and never seen.
- Pre-existing state: not applicable; the state lives in the downstream repository.
- Negative control: none needed for CI, but no run shows the failure branch being taken.

### Item 3a: level, placement, and environment
- No test exists at any level. The only check is a workflow run, and none is cited (see Item 6).
- The job does not use the `should-run` gate directly, but `needs: build-and-push` inherits it, so the gating is correct.
- `actionlint` and `conftest` were not run, which the repository's CLAUDE.md requires for workflow changes.

### Item 4: names by content, not by position
- Line 427–428: the "first run" comment is positional and wrong about the sort order (covered under Item 1).
- No other names or ordinals. None otherwise.

### Item 5: the failure report
- Line 446: `Timed out waiting for downstream workflow to complete.` It gives no last observed state and no statement of whether any run was found. A reader cannot tell a lost dispatch from a slow run. Per `test-authoring` §7 (*a wait that fails reports what it waited for and the last state it saw*), the message should carry that.
- The `curl` at line 380 has no `--fail` and no status check, so a rejected dispatch passes silently.

### Item 6: what the writer says it verified
None stated. No commit message or description cites a run, a red run, or a downstream result. I did not run the workflow, since I have no `gh` access or network here.

### Item 7: siblings of the change
- `.github/workflows/trigger-c8run-e2e-tests.yml:43` uses the same `curl -X POST` without a status check, so the silent-dispatch defect applies there too. Its observe step is last, which is correct, so only the dispatch line is affected.
- The `should-run` allowlist (line 84) gains the author's username, which gates every PR run. No commit message mentions it.
- The `@main` token action is used across the repository, so it is not a defect in this change.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| The 40-minute poll cannot finish inside the 20-minute job timeout, so the job is killed first and the comment is false | substantive | `docker-build-helm-integration.yml:356`, `:424` | Raise the job timeout past poll budget plus setup, or shorten the poll to fit, and make the comment match |
| The observe step runs before the wait, so the health metric records the dispatch as the job outcome; CLAUDE.md requires the observe step to be last | substantive | `:402`, `:413` | Move the observe step after the wait |
| The dispatch `curl` has no `--fail` or status check, so a rejected dispatch is silent and the poll runs to the timeout | substantive | `:380` | Check the HTTP status and fail the step on a non-2xx response |
| `TRIGGER_TIME` is taken after the dispatch, so a run created first is filtered out | substantive | `:399`, `:428` | Capture the timestamp before the dispatch |
| The run is not tied to this dispatch: other PRs dispatch the same event, and `head -n1` takes the newest run, which may belong to another PR. The comment's "first" is also wrong | substantive | `:427–428` | Match a token the dispatch carries (for example `source_sha`) in the downstream run name, or name this as a follow-up and correct the comment |
| The timeout message gives no last state and does not say whether any run was found | substantive | `:446` | Report the last observed status, or "no run found after the dispatch" |
| The allowlist entry `slolatte` is a gate change that no commit message claims | substantive | `:84` | Name it in the PR description with its reason, or drop it |
| No run or evidence is cited for the dispatch, the poll, or any failure path | substantive | whole change | Cite one `workflow_dispatch` run on a PR branch with the downstream result, or name the paths left unverified |
| The same silent-dispatch `curl` exists in the sibling workflow | substantive | `trigger-c8run-e2e-tests.yml:43` | Fix in this change or name it as a follow-up in the PR description |

**Not checked:** I did not run the workflow, `actionlint`, or `conftest`, which are not installed here. I did not read the downstream workflow `playwright_saas_pr_trigger_monorepo_8_9.yml` in `c8-cross-component-e2e-tests`, so the payload fields and the run name it produces are unverified. Wording was judged only where it misleads.
