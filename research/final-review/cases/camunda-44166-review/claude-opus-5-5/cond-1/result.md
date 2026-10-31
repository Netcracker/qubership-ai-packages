# Final review: `e3250e60..HEAD` (7 commits, `.github/workflows/docker-build-helm-integration.yml` only)

**Inputs.** I had no task statement, so the claimed cases come from the seven commit subject lines alone. None of the commits has a body. The change is a CI configuration, so I filled the form through the §2a analogues for a configuration, and item 3 applies as written. I loaded `english-developer-style` and `test-authoring`. No doc-comment or page-authoring skill covers a workflow file. `comment-drift.py` ran (rc 0) and printed nothing because it does not parse YAML, so I read every comment by hand. `actionlint` and `conftest` are not installed here; `yq` parses the file. There is no previous report.

## 1. Comments consistent with the code and with each other

Analogue used: every statement the file makes about itself, the API it calls, or the other repository.

- **`:424` "Wait up to 40 min (80 x 30s)"** is false. `timeout-minutes: 20` (`:356`) cancels the job at about 20 minutes, and that budget also covers checkout, the token, and the dispatch. The 80 iterations also make up to 3 `gh api` calls each, so even without the job limit the loop would run longer than 40 minutes. The fix is part of the limit finding in item 3.
- **`:426` "Grab the first run created after the trigger event"** describes the wrong run. The runs endpoint returns the newest run first (I could not check this offline), so `head -n1` picks the most recently created matching run, not the first one. Item 3 covers why that matters. Request: once the selection is fixed, describe the run by what it is ("the run this dispatch created").
- `:1` description and `:5` name: accurate. `helm-deploy` already sets `e2e-enabled: true` (`:325`), so "Helm integration and E2E tests" holds.

## 2. Claimed cases covered

Analogue used: the test of a workflow change is a run of that workflow, cited in the change.

| Claim (commit) | Where it is handled | Evidence of a run |
| --- | --- | --- |
| Add SaaS E2E smoke tests (`4662bcd1`) | `trigger-saas-e2e`, `:352–447` | none cited |
| Update versions to SNAPSHOT (`be150d28`) | payload `:391–394` | none cited |
| Poll for the conclusion (`7e66e244`): succeeds on `success`, fails otherwise | `:434–441` | none cited, for either outcome |
| Add a timestamp for polling (`863daee5`) | `:398–400`, `:427–428` | none cited |
| Fix linting (×2) | quoting at `:400`, `:431–432`, `_` loop variable at `:425` | `actionlint` not run here |
| Add a job timeout (`4459b6fc`) | `:356` | none |

- **Substantive: no run is cited for the poll.** Nothing in the change shows the poll succeeding or failing against `playwright_saas_pr_trigger_monorepo_8_9.yml`. The workflow file name, the event filter, the `run-saas-generation-smoke` event type, and the app token's read access to Actions on the target repository are all unverified from this side. Request: link one run that ends `success` and one where the downstream run fails. Each should show which run ID was matched.
- **Substantive: unclaimed hunk at `:84`.** The change adds `"slolatte"` to the actor allowlist, and no commit message mentions it. That entry turns on the whole workflow for this author's PRs: the Harbor push, the GKE deploy, and the new SaaS dispatch. Request: claim it in the message with its reason, or move it to its own change.
- `be150d28` also adds `actions/checkout` (`:359`). The local `observe-build-status` action needs a checkout first, so this is part of the claimed change. `4459b6fc` adds `permissions: { }`, a lint fix that belongs to the same claim.
- Commands the change tells someone to run: none.

## 3. Boundaries, partitions, and the negative control

**Limits on the same work (substantive).**
- The job limit is `timeout-minutes: 20` (`:356`, set in the workflow).
- The loop's own deadline is about 40 minutes plus three `gh api` calls per iteration (`:425`, fixed in the script). `gh api` calls have no timeout set, so I count them as never returning.
- The downstream workflow's own timeout is in another repository and unknown to me.

The job limit fires first, so the loop's deadline and the message at `:446` are never reached. Any downstream run that takes more than about 19 minutes, after setup, fails this check even when the tests pass. The repository's own policy also warns on more than 15 minutes (`conftest-unified-ci-rules.rego:20–27`). Request: derive one limit from the other. Make the loop's deadline a wall-clock check that ends before the job limit, last attempt included, and set the job limit from the downstream run's real duration. Cite the line in the target repository that sets that workflow's timeout.

**Runs that already exist in the target repository (substantive).** The selection at `:427–428` accepts any `repository_dispatch` run of that workflow created after `TRIGGER_TIME`, then takes the newest. Nothing ties a run to this dispatch, even though `source_sha` is sent in the payload. Two allowlisted PRs that dispatch within the same few minutes can each pick the other's run, or the later run, and report its result. Every run implied by this change starts with no other dispatch in flight. Request: correlate the run with this dispatch. For example, put a unique ID in `client_payload`, have the downstream `run-name` include it, and match on it. Alternatively, cite a run made with two dispatches in flight.

**The trigger timestamp (substantive).** `TRIGGER_TIME` is taken after `curl` returns (`:398–400`). It has one-second precision, is read from the runner's clock, and is compared with a strict `>`. A downstream run created in the same second, or a few seconds earlier because of clock skew, is never matched. The job then either picks a later unrelated run or times out. Request: take the timestamp before the dispatch with a margin, or replace the timestamp with the correlation ID above.

**Faults (substantive).** There is no previous waiting mechanism here, so I checked the new one on its two likely faults:
- **The dispatch is rejected** (401, 404, or 422). `curl -X POST` without `--fail` exits 0, so the step passes and the error body is printed only as ordinary output. The loop then finds no run, prints nothing per iteration, and the job is killed at 20 minutes by GitHub's timeout. Request: use `curl --fail-with-body`, which `trigger-c8run-e2e-tests.yml:42` also lacks (see item 7).
- **The attempt that waits longest** is a hung `gh api` call. Nothing bounds it except the job limit. The bounding deadline requested above covers this.

**Partitions.**
- `pull_request` and `workflow_dispatch` both reach the job, and neither is shown run.
- On dispatch, `helmRepositoryDirName` can select a chart other than 8.9 while `c8Version` stays `"8.9"`. That is taste, filed under item 7.
- The negative control, a downstream failure that turns this job red, is not shown run (item 2).

## 3a. Level, placement, and the environment

The smallest level available is the static gates, `actionlint` and `conftest`. The "fix linting" commits suggest `actionlint` was run. Running `conftest` is not stated.

**Substantive: `Observe build status` is not the last step.** It sits at `:402`, before `Wait for downstream workflow to finish` (`:413`). It therefore records `job.status` before the wait, so a downstream failure or a timeout never reaches the CI health metrics. `CLAUDE.md` requires that this step be last in every job. The conftest rule checks only that the step exists (`conftest-unified-ci-rules.rego:174–179`), so the gate passes. Request: move it to the end of the job.

The new job's layout otherwise matches its siblings in this file and in `trigger-c8run-e2e-tests.yml`: the token action, `permissions: { }`, and bash as the default shell.

## 4. Names by content, not by position

none beyond `:426` "the first run", filed under item 1. I checked the step names, the `job_name`, and the echo messages.

## 5. The failure report

Analogue used: what the wait prints when it fails.

**Substantive.** When no run matches, the loop prints nothing after its first line (`:419`). The timeout message at `:446` is unreachable (item 3), and even if it ran, it would give neither the last state seen nor whether any run was found. The success and failure branches print the run ID but not its URL. `test-authoring` §7 says a wait that fails reports what it waited for and the last state it saw. Request:
- print one line per iteration when no run is found;
- print the run's `html_url` once a run is matched;
- make the timeout message give the last status and the run ID, or say that no run was found.

## 6. What the writer says it verified

No evidence is stated. None of the seven commits has a body, and no run of the workflow is linked: no green run and no run with the downstream workflow failing. I did not run anything to supply it.

## 7. Siblings of the change

- **Other dispatches to `c8-cross-component-e2e-tests`:** `trigger-c8run-e2e-tests.yml:42–47` (`git grep -n /dispatches`). It has the same `curl` without `--fail`, but it does not wait on the result, so only the silent-rejection half applies there. Request: mention it as follow-up. `preview-env-smoke-test.yml:137` checks the repository out and does not dispatch, so it does not apply.
- **Actor allowlist:** `git grep ce-dmelnych` finds only this file, so no second list needs the new member.
- **Workflow name:** `git grep` finds no other reference to the old name. The concurrency group at `:46` uses `github.workflow`, so the group key changes when the name changes, and nothing else depends on it.
- **Taste: `job_name: trigger-saas-e2e` at `:408`** breaks the `docker-build-helm-integration-…` prefix that the six sibling `job_name` values use (`:95`–`:315`).
- **Taste: `needs: format-identifier` at `:355`.** The job never reads that output.
- **Taste: three places hard-code 8.9.** `c8Version: "8.9"` (`:389`), `WORKFLOW_FILE …_8_9.yml` (`:422`), and the chart default (`:21`, `:313`) must change together at the next version bump or backport. One `env` value would keep them in step.
- **Taste: one failed call ends the job.** `set -e` plus the default `bash -eo pipefail` means a single transient `gh api` error ends the job at once (`:418`, `:427`).

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The 20-minute job limit fires before the 40-minute loop deadline, so a downstream run over about 19 minutes fails the check | Substantive | `docker-build-helm-integration.yml:356`, `:424–425` | 3 |
| Run selection is not tied to this dispatch, so concurrent PRs can read each other's results | Substantive | `:427–428` | 3 |
| Trigger timestamp is taken after the dispatch with a strict `>` at one-second precision, so the run can be missed | Substantive | `:398–400`, `:428` | 3 |
| `curl` without `--fail`: a rejected dispatch passes and the job waits silently until it is killed | Substantive | `:380` | 3 |
| `Observe build status` comes before the wait, so the downstream result is never reported to CI health | Substantive | `:402`, `:413` | 3a |
| Comment "Wait up to 40 min" is false under the 20-minute job limit | Substantive | `:424` | 1 |
| Comment "the first run" describes the newest matching run | Substantive | `:426` | 1 |
| A silent wait with no last state or run URL in its failure messages | Substantive | `:419`, `:446` | 5 |
| No run cited for the poll's success or failure | Substantive | `:413–447` | 2 |
| Unclaimed allowlist addition `slolatte` | Substantive | `:84` | 2 |
| `job_name` breaks the sibling prefix | Taste | `:408` | 7 |
| Unused `needs: format-identifier` | Taste | `:355` | 7 |
| Hard-coded 8.9 in three places | Taste | `:389`, `:422`, `:21` | 7 |
| A transient `gh api` error aborts the wait | Taste | `:418` | 7 |

I could not run `actionlint` or `conftest` (neither is installed), and the drift script does not parse YAML. I also could not confirm the runs endpoint's default order or the target workflow's file name and timeout without network access.
