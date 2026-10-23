# Final review: `58316ca..5dcb6be` (four commits)

There was no task statement, so the claimed cases come from the four commit messages and the comments above the new tests. I read the diff whole. `comment-drift.py` ran and printed nothing, because it parses only Java, Kotlin, Groovy and Scala. I checked the Go and Makefile comments by hand instead. Only the three skills I was pointed to were loaded, so there was no `godoc-authoring`. Test-authoring §0: `AGENTS.md` has no stack line. I propose one sentence for it: `Tests (test/integration/pipstub): Go testing engine and t.Errorf failure lines; no testify.`

What I ran: `go test` in pipstub (passes); the `chart-files` Docker stage into the scratchpad (builds); `helm lint` and `helm template` with both stand values files on a scratch copy of the chart (clean, 12 and 10 objects); and the realm-merge `jq` pipeline by hand, with one new user file and with a duplicate.

## Item 1: comments consistent with the code and with each other
- **`test/integration/pipstub/main.go:34-38` and `:122-123`.** Both comments say the default route answers "every request whose path has no route of its own". Since this change it also answers a path whose route has no responses. The commit message and the test comment (`main_test.go`, above `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`) both say so; the doc comment leaves that case out.
- **`main.go:37-38`.** "as it did before the default route existed" describes the change rather than the code (taste).
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "the suite Job; waits until they are Ready". `test/k8s/README.md:25-26` says the opposite: the Job is a `helm test` hook, and installing the stand does not start it. Its own row at `:57` leaves the Job out.
- **`README.md:58`.** "CI builds both via `.github/docker-dev-config.json`" is now false: that file lists five images.
- **`Makefile:49-50`, `helm-templates/authz-test-stand/README.md:69-70`.** These describe raising the suite limit as `E2E_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. They leave out `-test.timeout 600s` in `suite.args` (see item 3).
- **`parity-realm.json:30`.** A role description names `TestTenantScopedDecisions`, and no such test exists in the repository.
- The other comments match the code: `helpers.go` `LoadConfig`, the testify `Dockerfile`, `test/k8s/values.yaml`, `suite.yaml`, `idp.yaml`, `_helpers.tpl`, `profile.jq` (I ran it, and `parity-r29-level-m2m` does become `R29LevelM2M`), and `REALM-DESCRIPTION.md`, whose issuer fix to `/auth` matches the base Keycloak manifest.

## Item 2: claimed cases covered
| Claimed case | Covered by |
| --- | --- |
| Unrouted path gets the default answer | `…DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| Routed path keeps its answer (control) | `…/a_routed_path_keeps_its_own_answer` |
| No `*` configured: 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …or falls through to 404 | **none**. Only an unrouted path with an empty default is tested, not a routed empty path with no default |
| Default route keeps one sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `/pip-stub/configure` takes the path `*` | **none**. Every test writes `routes[defaultRoute]` directly |
| The call record keeps the target in `requestUri` | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field, not the JSON key consumers read from `/pip-stub/calls` |
| Merge of user files, profile fill-in, build fails on a duplicate user | **none** in the repo ("none so far", so CI runs the stage with no users). My manual run behaved as documented |
| Keycloak restarts when a realm file changes (checksum) | **none** |
| Restricted Pod Security Standard; app.kubernetes.io and helm.sh/chart labels; no `runAsUser` | **none**. The kind namespaces enforce no Pod Security level, and `test-chart-render.sh` does not render this chart |
| The stand's parts, both values files, the make targets | The CI jobs `kind-e2e` and `kind-parity`, plus `helm lint` of both values files |
| A suite can outlast 15 minutes | **none**. No run used a raised value |
| Release publishes three more images | The release workflow only; `build_context` per component matches the action's documented schema |

Command lines in the changed files:
- `make test-stand-files` is run by CI (`integration-tests.yaml`); I ran the same stage.
- `make e2e-down` as the inherited-state remedy: its outcome (the cluster is deleted) follows from the target.
- `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite` (chart README step 3): the Makefile's `run-suite` runs the same on Helm 4.3.1 in CI. **On Helm 3: none.** It depends on Helm 3 waiting on a Job hook. Its kube client waits for Job completion, so this should work, but nothing runs it.
- `docker create … true` / `docker cp` from the transfer image: **none**. It depends on a `FROM scratch` image with no `true` binary. `docker create` does not execute the command, so it should succeed, but nothing runs it.
- `helm upgrade --install … --set TAG=<version>` from the copied chart: **none**.
- `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` then `make e2e-suite` (`docs/local-integration-tests.md:139-143`): **none**.

Hunks no commit sentence claims:
- `test/svt/common/compose/docker-compose.yml:3`: the Keycloak bump from `26.0` to `26.3.5@sha256:…`.
- `.github/docker-dev-config.json`: three images added to the CI dev builds; the commit only claims the release.
- `parity-realm.json` gains 318 lines: tenant-A clients, `mt-a` and `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope`, and claim mappers. The commit claims only the new `parity-mt-b` realm, and nothing in the repository uses the additions.

## Item 3: boundaries, partitions, and the negative control
**pip-stub.**
- Missing partition: a routed path with empty responses and no default route.
- Missing precedence control: a request that matches a YAML rule while `*` is configured should get the rule's answer. `TestHandlePIP_RuleThenLegacyFallback` covers rules against path routes, not against the default route.
- Present: the routed-path control and the empty-default case.

**State left behind.** A cluster from an older `make e2e` or `make parity` is documented with the error text and the `make e2e-down` remedy. No run of the remedy on that state is recorded.

**Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand chart (`Makefile:90,155`). The keys both charts read are `TAG` and `IMAGE_PULL_POLICY`.
- The documented `--set IMAGE_PULL_POLICY=Never` means the same thing in the stand.
- `--set TAG=<x>`, passed to test another agent build, now makes the stand ask for `local/pip-stub:<x>` and `local/authz-runtime-suite:<x>`, which nothing builds. With `Never` that gives `ErrImageNeverPull`.

**Limits on the suite's run.**

| Limit | Where it is set | Value | Counted from |
| --- | --- | --- | --- |
| Go `-test.timeout` | `suite.args`: `values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56` | 600s | container start |
| Job `activeDeadlineSeconds` | values | 900 | Job start |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m | helm start, which is earlier than the Job start |

- The CI job's `timeout-minutes: 30` counts from the CI job start, so it is not a pair under the form's rule. It does cap a raised suite in CI.
- At the defaults the innermost limit, Go's, fires first, which is right.
- Raising the documented pair past 10 minutes has no effect, because `-test.timeout 600s` still ends the suite. That defeats the commit's claim that a suite can outlast 15 minutes.
- The documented rule "no shorter than" allows the helm timeout to equal the Job deadline. Helm's clock starts earlier, so it fires first and hides the Job's `DeadlineExceeded`.

## Item 3a: level, placement, and the environment
- The pip-stub tests are small and in-process, sit beside their neighbors in `main_test.go`, and reuse `resetState`.
- The chart's claims (Pod Security context, labels, the `fail` messages, the `emptyDir` `sizeLimit` fallback) can be observed with `helm template` offline. `test/scripts/test-chart-render.sh` is where the sibling charts' render assertions live, and CI runs it, but it has no case for this chart.

## Item 4: names by content, not by position
None. I searched the added lines for ordinals and positional references; the table cases are named by condition.

## Item 5: the failure report
None.
- `RecordsTheRequestTargetAsSent` joins two comparisons with `||`, but its message prints all four values.
- The table loop uses `t.Errorf` with the method, path and both operand pairs.
- The sequence test prints got and want.

## Item 6: what the writer says it verified
Neither the commits nor any report state a red run on the base commit or a mutation verdict. The base would panic on the empty-route case (`idx` -1), but that is not shown. No CI result is stated for the kind jobs, and none for the Helm 3/4 `--logs` behavior beyond the commit's prose.

## Item 7: siblings of the change
- **New Makefile variables.** `test/k8s/README.md:66-68` lists the variables you can override and leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`.
- **Count of images.** `README.md:58` "both" (item 1). `docker-release.yaml` and the top-level README release paragraph were updated.
- **`--logs`.** No other place tells you to use it.
- **`kubectl wait --for=create` (`Makefile:108`).** It needs kubectl 1.31 or later. The prerequisites table (`docs/local-integration-tests.md:37`) names no minimum. On an older kubectl the wait fails, `logs -f` runs too early, and the log is lost, although helm still sets the exit code.
- **Old manifest paths.** No references remain (`git grep` over every deleted file name, ConfigMap and Secret name).

## Findings
| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Raising the suite limit past 10 min has no effect, because `-test.timeout 600s` in `suite.args` ends the run first; equal helm and Job limits race | Substantive | `Makefile:49-52,104`; `values.yaml:95-99`; `test/k8s/test-stand-values.yaml:55-56`; chart `README.md:69-70` | Derive `-test.timeout` from `activeDeadlineSeconds`, or document all three together and require helm's limit to be strictly longer |
| `E2E_HELM_ARGS` now reaches the stand: `--set TAG=…` meant for the agent asks for stand images nothing builds | Substantive | `Makefile:46-48,90,155` | Give the stand its own args variable, or document which keys reach it |
| Docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop the Job, as `test/k8s/README.md:57` does |
| "CI builds both" is stale, and the dev-config hunk is unclaimed | Substantive | `README.md:58`; `.github/docker-dev-config.json` | Fix the count; claim the dev builds in the description |
| Unclaimed hunks: SVT Keycloak bump; the `parity-realm.json` additions, which nothing uses and which cite a missing `TestTenantScopedDecisions` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `parity-realm.json:30` and the additions | Claim each with its run, or move them to their own change |
| Missing pip-stub cases: a routed empty route with no default gives 404; a rule wins over `*`; `*` set through `/pip-stub/configure`; the `requestUri` JSON key | Substantive | `test/integration/pipstub/main_test.go:225-286` | Add these cases next to the existing table |
| Default-route doc comments leave out the empty-route fall-through | Substantive | `main.go:34-36,122-123` | Name the second case |
| No check of the restricted-Pod-Security, label, and `fail` claims | Substantive | `helm-templates/authz-test-stand/templates/*`; `test/scripts/test-chart-render.sh` | Add render assertions, or label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` |
| No repo test of the realm merge, profile fill-in, or duplicate-user failure | Substantive | `build/authz-agent-transfer/Dockerfile:30-47` | Add a fixture user file and a check, or record the run |
| Documented commands that nothing runs: Helm 3 `helm test`, `docker create`/`cp` from the transfer image, install from the copied chart, the `--reuse-values` subset run | Substantive | chart `README.md:39-67`; `docs/local-integration-tests.md:139-143` | Run them once and record it, or limit the README to the versions that run |
| Override list leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` | Substantive | `test/k8s/README.md:66-68` | List them |
| No kubectl ≥ 1.31 prerequisite for `wait --for=create` | Substantive | `Makefile:108`; `docs/local-integration-tests.md:37` | State the minimum |
| No red run or mutation verdict stated | Substantive | commit `9d25da7` | State the base-commit run |
| Comment describes the change ("before the default route existed") | Taste | `main.go:37-38` | Describe the behavior only |

Not checked: I did not run the kind suites or `helm test` (there is no cluster), Helm 3, or the release workflow, and I made no style pass over the prose.
