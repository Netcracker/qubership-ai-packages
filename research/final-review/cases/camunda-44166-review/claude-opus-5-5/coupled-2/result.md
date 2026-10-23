# Final review of `e3250e60..HEAD`: seven commits adding the `trigger-saas-e2e` job to `docker-build-helm-integration.yml`

No task statement was handed over. Per §1, I took the claimed cases from the seven commit subjects alone; none of the commits has a body. The change is a CI workflow, a configuration with no members and no tests, so I filled the form through the §2a analogues. The drift script ran but printed nothing, because it does not parse YAML. I loaded `english-developer-style` and `test-authoring`. `test-authoring` has no test class here to apply to. There is no previous report.

## Item 1: comments consistent with the code and with each other

*Analogue: statements the file makes about itself, checked against the code.*

- **`:424` says `# Wait up to 40 min (80 x 30s)`, which is false.** The job has `timeout-minutes: 20` at `:356`. GitHub cancels the job at 20 minutes, and that includes the time spent on checkout, the token, and the dispatch. The loop's own `Timed out waiting…` message at `:446` therefore never prints. A reader trusts the 40 and expects 40.
- **`:426` says `# Grab the first run created after the trigger event`, but the code takes the newest one.** The runs endpoint returns runs newest first, so `head -n1` picks the most recent run created after the trigger. That is the same run only when exactly one dispatch landed in the window (see item 3).
- **The header at `:1` says the workflow "triggers SaaS E2E smoke tests".** The job also waits for their result and fails on it. The job name at `:353`, `Trigger SaaS E2E tests`, has the same gap. Taste.
- **The workflow name at `:5` uses notation for words.** `Docker Build, Helm Deploy & E2E Tests (SaaS + Helm)` uses `&` and `+` where it means "and" (english-developer-style, "Notation standing in for a word"). Taste.
- **`job_name: trigger-saas-e2e` at `:408` breaks the file's naming pattern.** The other five jobs use the prefix `docker-build-helm-integration-*` (`:95`, `:125`, `:154`, `:183`, `:284`, `:315`), so this metric will not group with the rest of the workflow. Taste.

## Item 2: claimed cases covered

*Analogue: each commit subject, with the part of the file that handles it.*

| Claimed case (commit) | Where it is handled | Verdict |
|---|---|---|
| SaaS E2E smoke tests for AlwaysGreen (`4662bcd1`) | job `trigger-saas-e2e`, `:352`–`:447` | Present |
| Versions updated (`be150d28`) | payload `:391`–`:394` moved to `SNAPSHOT` / `8-SNAPSHOT`; this commit also added the checkout at `:359` without saying so | Present |
| Poll for conclusion (`7e66e244`) | `:413`–`:447` | Present, with the defects in item 3 |
| Timestamp for polling (`863daee5`) | `:398`–`:400`, filter at `:428` | **Does not do its job.** The timestamp is taken *after* the dispatch, and the filter uses a strict `>` (item 3) |
| Job timeout (`4459b6fc`) | `:356`, 20 min | Present, but it contradicts the 40-minute loop (item 3) |
| Linting fixes (`e3ff145e`, `c15b27bf`) | `:400`, `:425`, `:431`–`:432` | `actionlint` and `conftest` are not installed here. `shellcheck` on the extracted wait script is clean |

Two changes are not claimed by any commit:

- `slolatte` was added to the actor allowlist at `:84`.
- The workflow was renamed at `:5`.

Both should be named in the PR description. Nothing else in the repository refers to the old workflow name. The concurrency group at `:46` is built from `github.workflow`, so the rename silently changes the group key once.

## Item 3: boundaries, partitions, and the negative control

1. **A downstream run created in the same second as the dispatch is never found (substantive).**
   - `TRIGGER_TIME` is taken after the `curl` returns, with one-second resolution.
   - A run that GitHub creates within that second, or before the `date` step runs, has `created_at <= TRIGGER_TIME`, so the filter at `:428` drops it.
   - The loop then never finds the run, and the job is cancelled at 20 minutes with no message.
   - **Request:** capture the timestamp before the dispatch, and compare with `>=`.
2. **With concurrent dispatches, a PR can report another PR's result (substantive).**
   - The filter matches *any* `repository_dispatch` run of `playwright_saas_pr_trigger_monorepo_8_9.yml` created after `T`.
   - Two PRs that dispatch inside one window both match. So does a re-push on the same PR: `cancel-in-progress` at `:47` cancels this job but not the downstream run. So does another repository that dispatches to the same workflow.
   - `head -n1` takes the newest of them, so PR A can go green or red on PR B's run.
   - `per_page=5` also drops the job's own run once more than five newer runs exist.
   - The payload already carries `source_sha` and the image tag, but nothing matches on them. The previous `head_sha` filter, removed in `863daee5`, could never match a dispatch run, which is presumably why it was replaced.
   - **Request:** correlate on a unique value. For example, send `${{ github.run_id }}` in `client_payload`, have the downstream workflow put it in its `run-name`, and filter on `display_title`. If that is out of scope, state the limitation in the description.
3. **A failed dispatch is not detected (substantive).**
   - `curl -X POST` at `:380` has no `--fail`, so a 401, 404, or 422 exits 0.
   - The job then polls for a run that never exists and is cancelled at 20 minutes.
   - **Request:** `curl --fail-with-body`, or `gh api -X POST …/dispatches`.
4. **The time limits contradict each other (substantive, §2 limits paragraph).** The limits on the wait are:
   - the job's `timeout-minutes: 20` (`:356`);
   - the loop's 80 × 30 s = 40 min (`:425`), plus the time each iteration's API calls take;
   - the downstream workflow's own timeout, set in another repository and not documented here;
   - the gate's warning threshold of 15 minutes (`.github/conftest-unified-ci-rules.rego:20`), which applies because this workflow sets `GHA_BEST_PRACTICES_LINTER: enabled`, so 20 already warns.

   The inner limit (the loop) never fires before the outer one (the job timeout), so the cancellation hides the loop's report.

   **Request:** derive the loop count from the job timeout, minus a margin for setup, or the reverse. Also document the downstream workflow's expected duration so the pair can be checked.
5. **One transient API error fails the job (taste).** With `defaults.run.shell: bash`, the step runs under `-eo pipefail`. A single transient `gh api` error or rate limit at `:427`–`:432` ends the job as a failure.
6. **Every downstream conclusion other than `success` counts as a failure.** `skipped` and `neutral` fail the job; that is defensible. No finding.
7. **Pre-existing state: cancelled jobs leave downstream runs alive (taste, follow-up).** A job cancelled by `cancel-in-progress` leaves its downstream run going in the e2e repository, consuming SaaS environments.
8. **Negative control.** The job runs on both `pull_request` and `workflow_dispatch`. On `workflow_dispatch`, `inputs.version` flows unescaped into the JSON at `:390` and into the shell script. That is the same pattern as the existing `:221`–`:223`, and only users with write access can dispatch. Passing it through `env` would keep a quote character from breaking the payload. Taste.

## Item 3a: level, placement, and the environment

- **`Observe build status` is not the last step (substantive).**
  - It sits at `:402`, before `Wait for downstream workflow to finish` at `:413`.
  - `job.status` is evaluated before the wait, so a failed downstream run, or the wait's own failure, is reported to CI health as success.
  - The repository's CLAUDE.md requires this step to be the last one in each job. The conftest rule (`conftest-unified-ci-rules.rego:166`–`:180`) checks only that the step exists, so the gate does not catch this.
  - **Request:** move it to the end of the job.
- **Placement is otherwise consistent.** The job sits beside its siblings in the same file and uses `permissions: { }`, `timeout-minutes`, and a checkout before the local action.
- **`needs: format-identifier` at `:355` is unused** by this job and only delays it. Taste.
- **The token is broader than it needs to be.** It is scoped to `camunda,c8-cross-component-e2e-tests` at `:374`, but only the second repository is used. This was copied from `trigger-c8run-e2e-tests.yml:37`. Taste.
- **Gates:** `actionlint` and `conftest` are not installed here and were not run. `shellcheck` on the wait script reports nothing.

## Item 4: names by content, not by position

None beyond the "first run" comment, which is filed under item 1 as a false statement. Step names, variables (`TARGET_REPO`, `WORKFLOW_FILE`, `TRIGGER_TIME`), and messages all name things by their content.

## Item 5: the failure report

*Analogue: what the job tells the reader when it fails.*

- **A dispatch failure prints nothing that marks it as a failure** (item 3.3).
- **A timeout prints nothing:** the cancellation pre-empts `:446` (item 3.4).
- **`Downstream workflow failed: $CONCLUSION` at `:439` gives no link.** It prints the run ID at `:433` but not the run URL, so the reader has to search the other repository. Adding `.html_url` would help. Taste.
- **Status and conclusion take two API calls** (`:431`–`:432`) where one `--jq '.status + " " + (.conclusion // "")'` would do. Taste.

## Item 6: what the writer says it verified

None is stated. All seven commits have no body, and nothing links to a workflow run in which the job dispatched, found its downstream run, and reported a conclusion. The same holds for a run in which the downstream failed and this job turned red. Per the form, I did not run anything to supply this evidence.

## Item 7: siblings of the change

- **`git grep '/dispatches'` finds one other site,** `.github/workflows/trigger-c8run-e2e-tests.yml:43`–`:47`.
  - It has the same `curl` without `--fail`, so a failed dispatch passes there too. The defect applies; fix it in the same change or name it as a follow-up.
  - Separately, that file calls `./.github/actions/observe-build-status` with no checkout, which this change avoided by adding `:359`. That is pre-existing and out of scope, but worth a follow-up.
- **`git grep 'actions/runs\|workflow_runs'` finds no other polling logic,** so there is no existing helper this loop should have reused.
- **The `8.9` literal appears three times:** `c8Version` at `:389`, `WORKFLOW_FILE` at `:422`, and the Helm directory default at `:21` and `:329`. All three must move together on the next minor version. Taste: a single env variable would tie them together.
- **`generate-github-app-token-from-vault-secrets` has 13 call sites.** The defect class does not apply to the action itself, so I did not read them.

## Findings

| # | Finding | Label | Location | Request |
|---|---|---|---|---|
| 1 | Timestamp is taken after the dispatch, and the filter uses `>`; the job's own run can be missed | Substantive | `:398`–`:400`, `:428` | Take the timestamp before the `curl`, and compare with `>=` |
| 2 | No correlation to this dispatch; concurrent or other dispatches get picked (newest first, `per_page=5`) | Substantive | `:427`–`:428`, `:384`–`:396` | Correlate on a unique ID (`run_id` in the payload, matched against `display_title`), or document the limitation |
| 3 | Comment says the job waits 40 min; the job timeout is 20, so the loop's timeout never fires; 20 also trips the >15 gate warning | Substantive | `:356`, `:424`–`:425`, `:446` | Derive one limit from the other; document the downstream duration |
| 4 | `Observe build status` comes before the wait step, so failures are reported as success | Substantive | `:402`–`:411` | Make it the last step |
| 5 | `curl` without `--fail`; a rejected dispatch goes unnoticed until the cancellation | Substantive | `:380` (sibling `trigger-c8run-e2e-tests.yml:43`) | `--fail-with-body` or `gh api -X POST`; fix the sibling or name it as a follow-up |
| 6 | "Grab the first run" comment, but the code takes the newest | Substantive | `:426` | Make the comment match the code, after fixing finding 2 |
| 7 | No evidence of a red or green run of the new job | Substantive | commit messages | State the run links in the PR description |
| 8 | Allowlist addition and workflow rename are not claimed by any commit | Taste | `:5`, `:84` | Name them in the description |
| 9 | Transient `gh api` error fails the job under `-eo pipefail` | Taste | `:427`–`:432` | Tolerate errors inside the loop |
| 10 | Unused `needs: format-identifier`; token scoped to two repositories | Taste | `:355`, `:374` | Drop both |
| 11 | `job_name` lacks the file's `docker-build-helm-integration-` prefix | Taste | `:408` | `docker-build-helm-integration-trigger-saas-e2e` |
| 12 | Failure message gives no run URL; two API calls per poll | Taste | `:431`–`:439` | Print `html_url`; use one call |
| 13 | Image tag interpolated into the shell and JSON | Taste | `:390` | Pass it through `env` |
| 14 | `&` and `+` in the workflow name; job name omits the wait | Taste | `:5`, `:353` | Use words; for example "Trigger and await SaaS E2E tests" |
| 15 | `8.9` hard-coded in three places | Taste | `:21`/`:329`, `:389`, `:422` | One env variable |

This review did not run the workflow, `actionlint`, or `conftest` (neither is installed). It did not read the downstream repository's workflow or its timeout, and the drift script cannot parse YAML. It did not do a style pass over the prose beyond the sentences filed above.
