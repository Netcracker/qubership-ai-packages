# Final review: `e3250e60..HEAD`

**Scope.** Seven commits, one file: `.github/workflows/docker-build-helm-integration.yml` (+100 −3). The change adds a `trigger-saas-e2e` job and an actor allowlist entry. No tests changed.

**Inputs.** No task statement was handed over, so claimed cases come from the commit messages alone. No previous report exists. The drift script ran and printed nothing, since it parses no YAML members, so I read every changed comment by hand. The `Skill` tool does not list the three skills, so I read the files by path: `english-developer-style` and `test-authoring`. There is no workflow-authoring skill in the set, so the §2a analogues apply, and the developer-style skill covers wording. `yq` parses the file. `actionlint` and `conftest` are not installed, so the repo's CI lint gates were not run.

## Item 1: comments consistent with the code and with each other

Findings: F6. The header (line 1) matches the file: the SaaS dispatch exists at lines 352–396, and the E2E claim holds because `helm-deploy` sets `e2e-enabled: true` (line 332). The comment "Wait up to 40 min (80 x 30s)" (line 424) is arithmetically right, but the job limit makes it false in effect (F1).

## Item 2: claimed cases covered

| Commit | Claimed case | Where | Test |
|---|---|---|---|
| 4662bcd1 | Dispatch the SaaS smoke run | 380–395 | none |
| 7e66e244 | Poll for the conclusion | 413–447 | none. Exit paths read: success exits 0, other conclusions exit 1, timeout exits 1, but the timeout is unreachable (F1) |
| 863daee5 | Timestamp for polling | 398–400 | none. Broken by the race in F2 |
| 4459b6fc | Job timeout | 356 | none. Conflicts with the 40-minute loop (F1) |
| be150d28 | Update versions | 386–392 | none. The SNAPSHOT values cannot be checked offline |
| c15b27bf, e3ff145e | Fix linting | not stated | not checked |

The downstream side (event type `run-saas-generation-smoke`, file `playwright_saas_pr_trigger_monorepo_8_9.yml`, its `repository_dispatch` filter) lives in `camunda/c8-cross-component-e2e-tests`. It cannot be checked offline.

## Item 3: boundaries, partitions, and the negative control

No inputs and no partitions. The job has no `if:` of its own, but it needs `build-and-push` and `format-identifier`, which need `should-run`, so the actor gate and the `skip-always-green` label still apply through skip propagation.

Limits on this work:
- Job limit: 20 minutes (line 356), set in this file.
- Loop budget: 80 × 30 s = 40 minutes (lines 424–425), set in this file.
- Downstream E2E run duration: set in the other repo, not read.
- Checkout, token, dispatch, and timestamp time come out of the 20-minute job limit before the loop starts. The job limit fires first at the defaults, so the loop's budget is never used (F1).

The wait reads the run list left by other dispatches, which is state the change does not own (F3). No negative control is run: neither the success path nor the failure path is exercised.

## Item 3a: level, placement, and environment

The behavior crosses GitHub's API, so no in-process test applies. The level that can observe it is a run: a `workflow_dispatch` of this workflow on a branch, then the downstream run it creates. Neither is named in the commits or run here. `yq` parses the file, but `actionlint` and `conftest` were not run.

## Item 4: names by content, not by position

One positional reference: the comment "Grab the first run created after the trigger event" (line 426). The code takes the newest run, not the first (F6). No other ordinals.

## Item 5: the failure report

Findings: F4 (a rejected dispatch prints nothing), F8 (the timeout message), T1. No boolean assertions.

## Item 6: what the writer says it verified

None stated. The commit messages give no red run, no workflow run, and no downstream run. The two "fix linting" commits suggest lint ran, but nothing states what or its result. The gate is not evidence.

## Item 7: siblings

- `trigger-c8run-e2e-tests.yml` (lines 39–47) has the same `curl` dispatch without a status check (F4 applies there too; name it as a follow-up). Its observe step is last, as CLAUDE.md requires. It has no wait, so F1–F3 do not apply.
- `observe-build-status` accepts `job_name`, and the call at line 408 passes it. Checked.
- The `ce-dmelnych` allowlist exists only in this file. The new `slolatte` entry is F9.
- The workflow `name:` change (line 5) has no references elsewhere in the repo.
- The App token (lines 363–374) covers both repos. Its permissions on the downstream repo are not in this repo and are not checked.

## Findings

| # | Label | File and line | Change requested |
|---|---|---|---|
| F1 | Substantive | `docker-build-helm-integration.yml:356`, `:424–425` | The job limit of 20 minutes ends the job before the 40-minute loop can time out, so the timeout branch (line 446) is unreachable. Derive the loop budget from the job limit, or raise the job limit above setup plus loop plus observe. |
| F2 | Substantive | `:380`, `:398–400`, `:428` | `TRIGGER_TIME` is taken after the dispatch. A run created in that gap fails `created_at > TRIGGER_TIME` and is never found. Take the timestamp before the dispatch step, with a margin for second precision. |
| F3 | Substantive | `:427–428` | The lookup takes the newest `repository_dispatch` run from the last five. Concurrent dispatches from other PRs can make this job report another PR's result. Correlate with `source_sha` through a value the downstream run shows, or name this limit in the description. |
| F4 | Substantive | `:380` | The `curl` has no `--fail` and no status check, so a rejected dispatch (401, 404, 422) passes the step. The wait then polls for 40 minutes and reports a timeout. Use `curl --fail-with-body`, or check for 204. The sibling has the same gap. |
| F5 | Substantive | `:402` before `:413–447` | The observe step is not the last step, which CLAUDE.md requires. It records the dispatch's status, not the E2E outcome. Move it after the wait and keep `if: always()`. |
| F6 | Substantive | `:426` | "Grab the first run" is wrong: the list is newest first, so `head -n1` takes the newest matching run. Say "the newest run created after TRIGGER_TIME", and fix with F3. |
| F7 | Substantive | `:418`, `:427–432` | `bash` runs with `-eo pipefail`, so one failed `gh api` call (in the lookup or the status and conclusion reads) ends the wait. Retry the lookup inside the loop. |
| F8 | Substantive | `:446` | The timeout message does not say what it waited for or the last state it saw. Print `TRIGGER_TIME`, the last `RUN_ID` seen or none, and the last status (the skill's wait rule, `test-authoring` §7). |
| F9 | Substantive | `:83` | No commit message claims the `slolatte` allowlist entry, and it widens who can start a build that pushes to Harbor and dispatches with the App token. Name it and its reason in the description, or drop it. |
| T1 | Taste | `:440–441`, `:446` | Print the run URL `https://github.com/$TARGET_REPO/actions/runs/$RUN_ID` in the failure messages. The writer may decline. |

No churn reported.

**Not checked:** no suite was run, since the change has no tests. `actionlint` and `conftest` are not installed here, so the CI lint gates did not run. The downstream workflow and the App's permissions in `c8-cross-component-e2e-tests` were not read. The drift script parses no YAML, so every comment was read by hand.
