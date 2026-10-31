I reviewed `58316ca..HEAD` (three commits) and found 16 substantive problems. The worst three are below; I changed no files.

1. **The chart's `helm test --logs` step likely fails when the suite passes.** In Helm 3.15.2, `--logs` reads the log of a Pod named after the test hook (`pkg/action/release_testing.go:127`). Here the hook is a Job, so no Pod has that name, and `helm test` exits with `unable to get pod logs for parity-suite`. I couldn't check Helm 4 offline.
2. **Existing kind clusters break.** On a cluster set up before this change, `make e2e-harness` and `make parity-harness` will hit objects the old `kubectl apply` made. Helm refuses to take over objects it does not own, so the install fails, and no doc gives the fix.
3. **Nothing tests the restricted Pod Security claim.** No CI run uses a namespace that enforces `restricted`. `test/scripts/test-chart-render.sh` has no check for the new chart.

There was no task statement, so the claimed cases come from the three commit messages alone. No previous report exists. The drift script printed nothing: it only reads Java, Kotlin, Groovy and Scala, so item 1 was done by hand over the Go, YAML, Makefile and Markdown. I loaded `test-authoring` (with its Go `testing` reference) and `english-developer-style`; the provided set has no `godoc-authoring`.

## Item 1: comments consistent with the code and with each other
- `Makefile:96`: "It prints the log only at the end" is false. `helm test` is called without `--logs`, so it prints no log at all, and with `--logs` it would hit problem 1. **Substantive.**
- `docs/local-integration-tests.md:104`: the `e2e-harness` row says the install includes "the suite Job; waits until they are Ready". The Job is a test hook (`suite.yaml:21`), so the install does not create it. `test/k8s/README.md:53` correctly leaves it out. **Substantive.**
- `test/integration/pipstub/main.go:37-38`: "as it did before the default route existed" describes the change rather than the code. **Taste.**
- `test/k8s/parity/idp-seed/README.md:12`: "The client `parity-m2m-tenant-b`…" comes right after the description of `parity-mt-b-realm.json`, but the client lives in `parity-realm.json`. **Taste.**
- These comments are still accurate: the `pipstub` package comment, `callRecord.RequestURI`, `defaultRoute`, `LoadConfig` in `helpers.go`, the comment in the testify Dockerfile, and the chart's `_helpers.tpl`, `values.yaml` and README text other than problem 1.

## Item 2: claimed cases covered
| Claimed case | Covered by |
| --- | --- |
| `*` route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer`. It sets `routes[defaultRoute]` directly, so nothing tests that `/pip-stub/configure` accepts `*`. |
| A stub without `*` answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …or to 404 (the old index −1 case) | **None** (item 3) |
| `requestUri` keeps the raw request target | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The default route serves its responses in sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| Keycloak, stubs, emulator, Secret, suite Job as a `helm test` hook; the four make targets | CI jobs `Kind end-to-end` and `Parity on kind`, on fresh clusters only |
| Every part is off by default | None. I checked by hand that `helm template` with the defaults renders nothing. |
| Keycloak restarts when a realm file changes | None. By hand, `checksum/realms` changed from `1fb38d…` to `2d2486…` after editing a realm. |
| `profile.jq` fills in the profile fields; a user declared twice fails the build | None. `testdata/realm/` has no user files, so CI never runs this path. In the scratchpad it produced `R29LevelM2M` and `…@example.test`, and the duplicate check exited 1. |
| Error texts `no realm files under files/realms/<realms>/` and `no file files/pip-stub/<file>` | None. Both messages match what `helm template` prints. |
| Restricted Pod Security Standard: security contexts, `/tmp` emptyDir, no `runAsUser` | **None** (problem 3) |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app` | None |
| The release publishes the three new images | `.qubership/docker.cfg`; the release workflow can't run offline |

**Commands the change documents:**
- `make test-stand-files`: CI runs it at `integration-tests.yaml:77`.
- `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite`: the two CI kind jobs run them.
- `docker build -f build/authz-agent-transfer/Dockerfile .`: the dev and release builds run it, with the same context.
- README transfer steps, `docker create … true` and `docker cp`: **none**. The image is `FROM scratch` with no `true` binary. `docker create` never runs the command, so it should work, but nothing has run it.
- `helm upgrade --install … --set TAG=<version>` from the transfer image: **none**.
- `helm test authz-test-stand --timeout 15m --logs`: **none** (problem 1). **Substantive.**
- The subset command in the docs (`helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite`): **none**. The two `--set` values render correctly under `helm template` 4.3.0, but nobody has run the `--reuse-values` merge or the suite after it. **Substantive.**

**Hunks no commit sentence claims:**
- `test/svt/common/compose/docker-compose.yml`: Keycloak bumped from 26.0 to 26.3.5 with a digest.
- `parity-realm.json`: new clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`; new users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`; new roles `ROLE_MT_*`. The commit only names the `parity-mt-b` realm, and no case uses any of these.
- `.github/docker-dev-config.json`: three new images in every dev build. The commit only names `docker.cfg`.
- `REALM-DESCRIPTION.md`: the issuer correction to the `/auth` path.

**Substantive.**

## Item 3: boundaries, partitions, and the negative control
- **Missing pip-stub cases.** No case has a routed path with empty responses and no default route. That is the input that indexed −1 on the base commit, and the claim "or to 404" depends on it. No case has a rule and a `*` route both matching, to check that the rule wins. **Substantive.**
- **State the old harness left.** The old harness created Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager` and `idp`, the ServiceAccount `runtime-suite`, the Secret `authz-agent-client-credentials`, and the ConfigMaps `keycloak-realms` and `pip-mock-config`. The new chart uses the same names, and Helm won't install over objects it does not own. Every CI run starts on a fresh cluster. **Substantive.** Either run the harness over an old stand, or document `make e2e-down` and run it on that state.
- **Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand chart too. It shares two keys with the agent chart: `TAG` and `IMAGE_PULL_POLICY` (agent `values.yaml:5,88`, stand `values.yaml:12-13`). With `--set TAG=1.2.3`, I got `local/pip-stub:1.2.3`, `local/tenant-manager:1.2.3` and `local/authz-runtime-suite:1.2.3`. Nothing builds those tags, and with the `Never` pull policy the harness waits out its 10 minutes. **Substantive.** The stand needs its own setting.
- **The new suite runner fails later.**
  - Fault: the suite Pod never starts, for example a missing image. The old runner failed after 3 minutes (`wait --for=condition=Ready --timeout=3m`). The new one waits about 2 minutes for the Job to exist, then polls for its log for at least 3 minutes, then lets `logs -f` fail. It still exits only when `helm test --timeout 15m` or the Job's 900 s deadline runs out, so about 15 minutes.
  - Longest single attempt: `kubectl logs` inside the poll has no `--request-timeout`, so one attempt is unbounded.
  - The harness is similar: a broken stub used to fail after 2 minutes (`rollout status`) and now fails after 10 (`helm --wait --timeout 10m`).
  - No sentence in the change accepts either delay. **Substantive.**
- **Limits on the same run.**
  - `-test.timeout 600s` is in `suite.args`.
  - `suite.activeDeadlineSeconds: 900` is a values setting.
  - `helm test --timeout 15m` is fixed in `Makefile:105` and in the chart README.
  - The CI job has `timeout-minutes: 30`.
  
  Raising `activeDeadlineSeconds` past 900 has no effect, because helm's 15 minutes run out first. At the defaults the two limits are equal and race. In the worst case the steps add up to 10 + 5 + 5 + 15 = 35 minutes plus the image build, so CI's 30 minutes ends the job first. **Substantive.** Derive helm's `--timeout` from `suite.activeDeadlineSeconds`.

## Item 3a: level, placement, and the environment
- The pip-stub tests are small, in-process, and sit in `main_test.go` next to the existing tests, sharing `resetState`. That is fine.
- The chart's security contexts, labels, checksum annotation and off-by-default parts can all be checked with `helm template`, no cluster needed. `test/scripts/test-chart-render.sh` runs in CI (`integration-tests.yaml:87`), but its chart list (`:439`) names only `authz-agent` and `authz-policy-admin`. **Substantive.**

## Item 4: names by content, not by position
None. The test and case names describe their condition. `$(1)`/`$(2)`/`$(3)` in the Makefile are make function parameters, which have no other names. The counts I checked ("three charts", "two tenant realms", "two stubs") are correct.

## Item 5: the failure report
None. All three tests print got and want in `Errorf`. The `||` and `DeepEqual` checks print every operand. The table cases are named by their condition.

## Item 6: what the writer says it verified
Neither commit states a run on the base commit that fails, or a mutation result. On the base commit the "routed path with no responses" case would panic, but the change doesn't show that.

## Item 7: siblings of the change
- `matchRule`'s response sequence already guards against an empty list (`main.go:275`), so it doesn't share the −1 bug.
- Places that still count the old set of images:
  - `README.md:59` says "CI builds both via `.github/docker-dev-config.json`", which now lists five images.
  - `.github/docs-for-publication-task.md:77` says "The two-entry array".
  
  **Substantive.**
- `kubectl wait --for=create` needs a recent kubectl, I think 1.31 or later. The prerequisites table in `docs/local-integration-tests.md` gives no minimum version. **Taste**, because I couldn't confirm the version offline.

## Findings
| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| `helm test --logs` reads a Pod named after the Job hook | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run it on Helm 3 and 4, or replace it with `kubectl logs job/<name>` |
| Comment says `helm test` prints the log at the end | Substantive | `Makefile:96` | Fix the sentence |
| `e2e-harness` row says the install creates the suite Job | Substantive | `docs/local-integration-tests.md:104` | Remove the Job from the row |
| Restricted Pod Security, labels and checksum are untested | Substantive | `test/scripts/test-chart-render.sh:439` | Add render assertions for the test stand, or label the kind namespaces `enforce=restricted` |
| No test of the user merge or the duplicate check | Substantive | `build/authz-agent-transfer/Dockerfile:39-46` | Add a test with fixture user files |
| Missing pip-stub cases: empty route with no default; rule against `*`; `*` through configure | Substantive | `test/integration/pipstub/main_test.go:225` | Add the cases |
| The subset command is unrun | Substantive | `docs/local-integration-tests.md:139` | Run it once |
| Unclaimed hunks | Substantive | svt `docker-compose.yml:3`, `parity-realm.json`, `docker-dev-config.json`, `REALM-DESCRIPTION.md` | Claim each with a sentence, or move it to its own change |
| Clusters with the old harness fail to install | Substantive | `Makefile:84,149` | Run over an old stand, or document `make e2e-down` |
| `E2E_HELM_ARGS` `TAG` reaches the stand's images | Substantive | `Makefile:84`, `values.yaml:12` | A setting of the stand's own |
| Suite fails after ~15 min instead of 3; harness after 10 instead of 2 | Substantive | `Makefile:101-107,84` | Run the fault, and add a deadline at the old time |
| Helm 15 min overrides `activeDeadlineSeconds`; CI's 30 min wraps the sum | Substantive | `Makefile:103`, `values.yaml:99`, `integration-tests.yaml` | Derive one limit from the other |
| README and publication doc still count two images | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77` | Update the counts |
| No red run or mutation result stated | Substantive | commit `9d25da7` | State the red run on the base commit |
| Narration "as it did before…" | Taste | `pipstub/main.go:37` | Drop the clause |
| Unclear which realm holds `parity-m2m-tenant-b` | Taste | `idp-seed/README.md:12` | Name `parity-realm.json` |
| No minimum kubectl version for `--for=create` | Taste | `docs/local-integration-tests.md:37` | State the minimum |

Not checked: no kind cluster, so the e2e and parity suites, the install over an old stand and the timing faults were not run (the durations come from the code). I didn't read Helm 4's source. Only the pip-stub Go tests, `helm lint`/`template` and the jq stage were run, and they passed. There was no pass over the prose for style alone.
