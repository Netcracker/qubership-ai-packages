## Final review: `e3250e60..HEAD` (7 commits, one file)

**Inputs.** No task statement was handed over and I cannot ask, so item 2 is answered from the commit messages and the class comments alone. The seven commits are: `4662bcd1` add saas e2e smoke tests for alwaysgreen; `be150d28` update versions; `7e66e244` poll for conclusion; `e3ff145e` fix linting; `863daee5` add timestamp for polling; `c15b27bf` fix linting; `4459b6fc` add job timeout. The only changed file is `.github/workflows/docker-build-helm-integration.yml`, and there are no tests or doc comments. The drift script ran and printed nothing, since YAML has no members. I used the `english-developer-style` copy from the skills directory, since the Skill tool did not list it, and read `test-authoring` for the test rules. No previous report exists, so there is no §4 table. The analogue for this change is the workflow file's own steps, not a skill.

### Item 1: comments consistent with the code and with each other

Findings are in the table. Apart from those, the `description:` header (line 1) matches the job list, and the `# Grab the first run…` comment (426) matches its code. The comment `# Wait up to 40 min (80 x 30s)` (424) is true of the loop but false of the job, which is capped at 20 minutes (see item 3).

### Item 2: claimed cases covered

- **Claimed cases.** Dispatch of `run-saas-generation-smoke` with the version payload (380–392). Wait that passes on downstream `success` and fails on any other conclusion (413–446). Timeout after 40 minutes (424, 446). Observe records the status (402). Test coverage: none. The change has no test and no run is named, so every claimed case is uncovered.
- **Commands.** The `curl` dispatch and the `gh api` calls are executed by the job, not documented for a reader, so no documented-form comparison applies.
- **Hunks no sentence claims.** (a) line 84, `"slolatte"` added to the actor gate, which lets that actor's PRs run the App token and the dispatch; it was added by `4662bcd1`, whose subject does not mention it. (b) line 5, the workflow `name:` rename. (c) line 360, the checkout step added by `be150d28` "update versions"; it exists only for the local observe action. (c) is an enabler, so its label is taste-adjacent, but it is listed as substantive under the rule "however small".

### Item 3: boundaries, partitions, negative control

**Limits.** The job's `timeout-minutes: 20` (356) is the enclosing limit and starts before the wait (checkout, token, dispatch). It fires first. The loop's 80 attempts take about 31 seconds each, so about 41 minutes uncapped. The job cap is reached at roughly attempt 38. No other workflow-level timeout or concurrency setting exists in this file.

**Faults and what each prints.** The old mechanism was not a wait: `helm-deploy` had none, so there is no old duration to compare with. On the new mechanism:
- **A. Downstream fails.** The step exits within 30 seconds of the downstream completing (444), printing `Downstream workflow failed: <conclusion>` (439). No run link is printed.
- **B. One `gh api` call never returns.** A call with no timeout is counted as never returning, so the job is cut at 20 minutes. The last printed line is the previous status. The `Timed out` line (446) never runs, and the observe step has already run (402).
- **C. The dispatch is rejected, or the run is created before `TRIGGER_TIME`.** The loop finds nothing and prints nothing for the full 20 minutes, then the job is cut. A rejected dispatch is silent because `curl` lacks `--fail` (380).

**Race and wrong-run match.** The timestamp is taken at 398, after the dispatch at 380. A run created in that gap has `created_at` earlier than `TRIGGER_TIME`, and `>` at 428 excludes it. Because `created_at` has one-second precision, a run created in the same second is also excluded. Separately, the match is "first run created after the trigger", with no use of the `source_sha` the payload sends, so another PR's dispatch in the same window can be reported as this one's.

**Negative control.** No success run is named. The skipped path for an unlisted actor is gated transitively through `needs` (`build-and-push` → frontends → `should-run`, lines 60–100). I read this but did not run it.

### Item 3a: level, placement, environment

The behavior is observable only across the boundary to another repository, so an in-process test is not owed. The job does run on this change's own PR, because `pull_request.paths` includes the workflow file, but only for listed actors. The Vault and App credentials are not exercised by any local check. The request is a run of faults A and C on the new job, with durations and output, as item 3 says.

### Item 4: names by content

None. Step names, comments and messages refer to content, not position.

### Item 5: the failure report

One taste finding: the failure line (439) does not print the run URL, so the red-build reader must find the run from the id printed earlier. No assertions exist.

### Item 6: what the writer says it verified

None stated. No red run, no run of the job, and no run link appears in the commit messages.

### Item 7: siblings

- **Allow-list.** `git grep ce-dmelnych` finds only this file (line 83). No other list needs `slolatte`.
- **Observe placement.** Every other job in this file ends with the observe step. The trigger job does not, which is the item 1 and 2 finding.
- **Dispatch.** `trigger-c8run-e2e-tests.yml:43–46` has the same `curl` without `--fail`. This is pre-existing, not part of the change, so it is named as a follow-up.
- **Prose.** The header says "Helm integration" (line 1) while the name says "Helm Deploy" (line 5). Taste.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Job cap of 20 minutes fires before the 40-minute loop bound; the `Timed out` line and the `40 min` comment are unreachable for this job | substantive | `…helm-integration.yml:356`, `:424–446` | Raise the job cap above setup plus 40 minutes plus observe, or derive the loop bound below the cap; print the run URL and last status on exit |
| 2 | Observe runs before the wait, so `job.status` is still success and the health metric records success before the downstream result; this breaks the CLAUDE.md last-step rule | substantive | `:402`, `:413` | Move observe to the last step of the job |
| 3 | `TRIGGER_TIME` is taken after the dispatch, and `>` excludes a same-second run, so the run can be missed and the wait runs to the cap | substantive | `:380`, `:398`, `:428` | Take the timestamp before the dispatch and compare with `>=`, or back off a few seconds; check `created_at` on one real run |
| 4 | The wait matches the first run created after the trigger, not this dispatch, so another PR's result can pass or fail this one; `source_sha` is sent and never checked | substantive | `:428` | Match on a value the downstream run carries from `source_sha`, or name the window as a known limit in the description |
| 5 | `curl` without `--fail` exits 0 on a rejected dispatch, so the wait polls silently for 20 minutes | substantive | `:380–392` | Use `--fail-with-body` so the step fails at once; the same pattern at `trigger-c8run-e2e-tests.yml:43` is a follow-up |
| 6 | Unclaimed hunks: the `slolatte` actor gate (84), the workflow rename (5), and the checkout step (360), none named by a commit sentence | substantive | `:5`, `:84`, `:360` | Name each in a commit message or the description, or move it to its own change |
| 7 | The token lists `camunda` in `repositories`, but the job calls only `c8-cross-component-e2e-tests`; least privilege per CLAUDE.md | taste | `:374` | Drop `camunda` unless the App action needs it; cannot be checked here |
| 8 | Step name `Generate GitHub App Token (for dispatch)` also covers the wait's `GH_TOKEN` | taste | `:361`, `:413–417` | Rename the step to cover both uses |
| 9 | Failure line names no run, so the red-build reader has no link | taste | `:439` | Print the run's `html_url` with the conclusion |

Churn: none reported.

**Not checked:** the workflow was not run and no GitHub run was consulted. `actionlint` and `conftest` are not installed here, so the CLAUDE.md lint gates were not run; `yq` parsed the file, and nothing else was checked by reading. The downstream workflow `playwright_saas_pr_trigger_monorepo_8_9.yml`, its `run-saas-generation-smoke` dispatch type, and the App token's permissions live in other repositories and were not checked. The drift script printed nothing because YAML has no members. The wording pass covered only text that reads wrongly, not a style pass over the prose.
