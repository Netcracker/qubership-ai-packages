I reviewed `e3250e60..HEAD`: seven commits that all edit `.github/workflows/docker-build-helm-integration.yml`. They add a `trigger-saas-e2e` job that sends a `repository_dispatch` to `camunda/c8-cross-component-e2e-tests` and then polls that repo's workflow for its result. There was no task statement, so the claimed cases come from the seven commit messages alone. This change is a CI configuration, not code, so the form uses the §2a analogues. The drift script ran (exit 0) but printed nothing because it does not parse YAML. Skills loaded: `english-developer-style` (§7 "Error and log messages") and `test-authoring` (§7, §8, §10).

The two most important problems: the poll can follow another PR's downstream run or miss its own, and the 20-minute job timeout fires long before the loop's 40-minute wait. When it does, the job is killed silently, and the CI-health step has already run before the wait.

## Item 1: comments consistent with the code and with each other
Analogue: what the workflow file says about itself (header, comments, step and job names, echoed text).
- **`:424` "Wait up to 40 min (80 x 30s)"** is false. `timeout-minutes: 20` (`:356`) kills the job first, and that 20 minutes also covers checkout, the token and the dispatch. Each loop round also adds up to three `gh api` calls on top of the 30-second sleep, so even the arithmetic is understated.
- **`:426` "Grab the first run created after the trigger event"** is false. The API lists runs newest first, so `head -n1` takes the newest matching run, not the first one created after the trigger.
- `:1` (the header) and `:5` (the workflow name) match the jobs.
- The job name `Trigger SaaS E2E tests` (`:353`) only says "trigger", but the job also waits for the result and fails with it. This is taste.

## Item 2: claimed cases covered
Claimed cases, one per commit:
- **"add saas e2e smoke tests for alwaysgreen"**: covered by `:352-396`. The commit carries no run that shows the dispatch accepted (HTTP 204) or the downstream run finishing. It is also unclear whether the SaaS generation pulls `zeebeVersion` (`:390`, a tag pushed only to `registry.camunda.cloud/team-camunda/camunda`). Nothing in the change shows that it does.
- **"update versions"** (`:391-394`, operate/tasklist/connectors/optimize set to `SNAPSHOT`): no reason is given. The workflow triggers on `operate/**` and `tasklist/**` (`:40-41`), but the SaaS run then uses SNAPSHOT builds of Operate and Tasklist, not the PR's. A PR that only changes Operate is not tested on SaaS, and no sentence says that is accepted.
- **"poll for conclusion"** (`:413-447`) and **"add timestamp for polling"** (`:398-400`, `:427-428`): no run is cited. The cases these steps are supposed to handle are broken (see item 3).
- **"fix linting" ×2** (`:400`, `:425`, `:431-432`): `actionlint` is not installed here, so I could not re-check them. `yq` parses the file.
- **"add job timeout"** (`:356-357`): present, but it conflicts with the loop (item 3).

Commands the change tells someone to run: none. The `curl` and `gh api` lines are run by the job itself.

Changes no commit message mentions:
- `slolatte` added to the actor allowlist (`:83-84`, in 4662bcd1).
- The workflow renamed (`:5`). This changes `github.workflow`, so it also changes the concurrency group (`:46`).
- `Checkout repository` (`:359-360`), which arrived in "update versions" although it is needed by the local `observe-build-status` action, not by any version change.

## Item 3: boundaries, partitions, and the negative control
- **The poll can follow the wrong downstream run** (`:427-428`). It takes any `repository_dispatch` run of `playwright_saas_pr_trigger_monorepo_8_9.yml` created after `TRIGGER_TIME`, newest first. Many allowlisted PRs run this workflow at the same time, so the job can report another PR's result, and the chosen `RUN_ID` can change from one round to the next. Nothing in the payload ties a run to this trigger: there is no correlation id and no `display_title` match.
- **The poll can miss its own run.** The timestamp is taken in a separate step *after* the `curl` (`:398-400`), with one-second resolution and a strict `>` comparison. A downstream run created during the step gap, or in the same second, never matches. Take the timestamp before the dispatch.
- **The wait mechanism on its faults.** Before 7e66e244 the job only dispatched and returned. The new loop behaves like this:
  - **Dispatch rejected (401/403/404/422):** `curl` has no `--fail`, so the step stays green and prints the error body. The loop finds no run, and it prints nothing while `RUN_ID` is empty. At 20 minutes GitHub kills the job with a generic timeout message, and the `Timed out waiting…` line (`:446`) never prints. Before the poll was added, the same fault passed green in seconds.
  - **No matching run (the timestamp race above):** the same 20-minute silent failure.
  - **Transient `gh api` error:** `shell: bash` runs under `-eo pipefail`, so one 5xx or rate-limit error fails the step at once, with no retry.
- **The limits contradict each other.** The job allows 20 minutes (`:356`). The loop's own limit is at least 40 minutes (`:424-425`), so it can never fire first. The repo's conftest warns above 15 minutes (`.github/conftest-unified-ci-rules.rego:24`). The real ceiling is how long the downstream SaaS suite takes, which is set in a repo not available here. The request: choose one budget, derive the loop count from it, and cite a downstream run duration that fits inside it.
- **Cancellation:** when a new push cancels this job (`cancel-in-progress: true`, `:47`), the downstream run keeps going. Taste.

## Item 3a: level, placement, and the environment
Analogue: where each rule lives and the repo's own gates.
- **CI-health step in the wrong place.** `Observe build status` (`:402-411`) is not the last step, which `CLAUDE.md` requires. It runs before the wait, so a failed or timed-out wait is never reported to CI health.
- **Wider token than needed.** The token is requested for `camunda,c8-cross-component-e2e-tests` (`:374`), but the job only needs the e2e repo (`preview-env-smoke-test.yml:137` does it that way). That breaks least privilege.
- **Unused dependency.** `needs: format-identifier` (`:355`) is listed, but its output is never used. Taste.
- I could not run `actionlint` or `conftest` here, because neither is installed. From reading the rego, `conftest` would print the >15-minute warning for this job.

## Item 4: names by content, not by position
"the first run" (`:426`) is positional, and wrong besides (item 1). Nothing else.

## Item 5: the failure report
- During the wait, nothing is printed while no run is found. If the job then hits its timeout, the log does not show what it waited for or the last state it saw (`test-authoring` §7, "A wait that fails reports what it waited for and the last state it saw").
- A downstream failure (`:439`) prints the run id but no link to the run (`html_url`). Taste.

## Item 6: what the writer says it verified
None stated: no link to a workflow run, and no evidence that the dispatch was accepted or that a downstream run was matched.

## Item 7: siblings of the change
- `.github/workflows/trigger-c8run-e2e-tests.yml:43-47` has the same `curl` call without `--fail`. Since it does not wait for a result, a rejected dispatch there leaves the job green. It should be fixed here too, or named as a follow-up.
- `preview-env-smoke-test.yml` runs the tests itself and does not use this pattern.
- The hard-coded 8.9 appears in three places (`:389`, `:422`, `:21`/`:329`) and has to move together on the next minor version. Taste.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Poll matches any dispatch run after the timestamp, so it can report another PR's result | Substantive | `:427-428` | Put a unique id (`github.run_id`) in `client_payload`, have the downstream `run-name` include it, and match on that |
| Timestamp taken after the dispatch, so its own run can be missed | Substantive | `:398-400` | Take the timestamp before the `curl` step |
| A failed dispatch is not detected, so the job waits 20 min silently | Substantive | `:380` | Use `curl --fail-with-body` |
| Job timeout of 20 min is below the loop's ≥40 min; conftest warns above 15 | Substantive | `:356`, `:424-425` | Choose one budget, derive the loop from it, and cite a downstream run duration that fits it |
| "Wait up to 40 min" comment is false | Substantive | `:424` | State the real bound |
| "first run" comment is false; `head -n1` takes the newest | Substantive | `:426` | Fix the comment, or the selection, together with the correlation fix |
| CI-health step runs before the wait, so the wait's outcome is not reported | Substantive | `:402-411` | Move it to the last step |
| Nothing logged while no run is found | Substantive | `:430` | Print the round and the time waited on each empty round |
| No reason given for SNAPSHOT versions; PR changes to Operate/Tasklist are not tested on SaaS | Substantive | `:391-394` | A sentence that accepts or explains this, or pass the PR's versions |
| No run shows the SaaS stack pulls the Harbor PR image | Substantive | `:390` | Link a downstream run that used the PR tag |
| Allowlist addition, workflow rename and checkout step not mentioned in any commit message | Substantive | `:84`, `:5`, `:359` | Mention them in the description, or move them to a separate change |
| Token covers the `camunda` repo, which the job does not need | Substantive | `:374` | Use `repositories: c8-cross-component-e2e-tests` only |
| No evidence of a run | Substantive | (none) | Link a green run and a red run of the job |
| Same `curl` without `--fail` in the c8run trigger workflow | Substantive | `trigger-c8run-e2e-tests.yml:43` | Fix it in this change, or name it as a follow-up |
| One transient `gh api` error fails the job immediately | Taste | `:427-432` | Retry, or tolerate one failed round |
| Unused `needs: format-identifier` | Taste | `:355` | Remove it |
| Job name says "Trigger" but the job also waits for the result | Taste | `:353` | Rename it, e.g. "SaaS E2E tests" |
| 8.9 hard-coded in three places | Taste | `:389`, `:422`, `:329` | Use one shared value |

I did not run `actionlint` or `conftest` (neither is installed here), did not run the workflow or read the downstream repo, and did not do a style-only pass over the prose.
