## Final review: `58316ca..HEAD` (3 commits)

**Setup.** No task statement was handed over, so the claimed cases come from the commit messages and the test class comments. Commits: `9d25da7` (pipstub default route), `8b85515` (test stand chart), `17b17fc` (restricted Pod Security). I loaded `test-authoring` (its Go references) and `english-developer-style`. There is no `godoc-authoring` in the skills directory, so Go doc comments were checked against the form only. The drift script printed nothing, because it parses only Java, Kotlin, Groovy and Scala, and the change touches none of those. I read the comments by hand. I changed nothing and committed nothing. I worked in a scratch copy of `HEAD` for the Helm checks.

**Previous report.** None exists, so there is no table over earlier findings.

### Item 1: comments consistent with the code and with each other

Three sentences are wrong or incomplete, and I checked each against the code:
- `main.go:35` and `main.go:122-123` say the default route answers "every request whose path has no route of its own". The code (`main.go:235-241`) also sends a routed path with no responses to the default.
- `main.go:36` says "No request path is \*". That is false. `httptest.NewRequest("OPTIONS", "*", nil)` gives `URL.Path == "*"`. Nothing shadows, because the default route answers it like any unrouted path.
- `_helpers.tpl:21` says the restricted SCC "rejects a pinned one". OpenShift's restricted SCC accepts a pinned uid inside the namespace range. The sentence is only true for a uid outside that range.

Taste: `Makefile:100-104` says `helm test` "prints the log only at the end". The recipe does not pass `--logs`, so `helm test` prints no log. The streaming comes from `kubectl logs -f`.

No comment narrates the change ("now", "no longer", "used to").

### Item 2: claimed cases covered

**9d25da7**
- Default route answers an unrouted path: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, case 1. Covered.
- Routed path keeps its own answer: same test, case 2. Covered.
- Route with no responses falls to the default: same test, case 3. Covered.
- Route with no responses and no default route gives 404: **no case** (see F1).
- Unconfigured stub still answers 404: cases 4 and 5. Covered.
- `/pip-stub/configure` takes `*`: no test drives the endpoint. The tests set `routes[defaultRoute]` directly (see F1).
- Sequence across paths: `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`. Covered.
- Request target kept as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`. Covered.

I ran `go test` and `go vet` in `test/integration/pipstub`. Both pass.

**17b17fc**
- Restricted PSS fields: I rendered both stands. The e2e stand has 5 pods, each with `runAsNonRoot`, `RuntimeDefault`, `allowPrivilegeEscalation: false` and `drop: ALL`. Only Keycloak has `readOnlyRootFilesystem: false`. The parity stand has 4 pods with the same result. Every image has a numeric `USER 10001` or `1000`. The claim holds, but no test asserts it (see F5).
- Labels and `helm.sh/chart` on every object: holds in the render.

**8b85515**
- "Every part off by default": the default render is empty. Verified.
- Chart lints with the realm files present: `helm lint` passes on both value files. Verified in the scratch copy.
- The `e2e-harness` and `parity-harness` install, and `e2e-suite` and `parity-suite` run `helm test`: CI runs these targets (`integration-tests.yaml`). I did not run them, since there is no cluster.
- `make test-stand-files`: it is run in CI. I did not run it, since it needs Docker. I reproduced the Dockerfile's `jq` merge on a sample user file. It fills the fields as claimed.
- "The build fails if a user is declared twice" (`testdata/realm/README.md:6-7`): no test or run exercises it (see F13).
- The parity realm "gains a second tenant realm": no case reads it (see F12).

**Commands in the changed docs:**
- `docker create … true` and `docker cp` (`docs/local-integration-tests.md`, the chart README): no job runs them. The transfer image is `FROM scratch`, so `docker create` does not run its command. Outcome: none (inference, not run).
- `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (`docs/local-integration-tests.md`): no job runs it. Outcome: none (not run).
- `helm test authz-test-stand --timeout 15m --logs` (chart README): the Makefile runs `helm test` without `--logs`. Same form, different flags. Outcome: none.

### Item 3: boundaries, partitions, and the negative control

- Off-by-default control: verified (empty render).
- Boundary and empty partitions for the default route: covered, except the routed-with-no-responses-and-no-default case (F1).
- The change replaces objects an earlier version created with `kubectl apply`. No test or run starts from that state, and no remedy is stated (see F7).
- Limit: `helm test --timeout 15m` and `suite.activeDeadlineSeconds: 900` fire at the same time, and the outer limit fires first (see F9).
- Keycloak's `OVERWRITE_EXISTING` was dropped without mention (see F8).

### Item 3a: level, placement, and the environment

The pipstub tests are in-process. They sit in `main_test.go`, beside the existing tests of `handlePIP`, and use the existing `resetState`. No helper is duplicated. The chart claims are tested only by `helm lint` in CI and by the e2e run. No render assertion covers the test stand, although `test/scripts/test-chart-render.sh` renders the other two charts (see F5).

### Item 4: names by content

None. The test names and case names carry content. The "allows five" in `idp.yaml:65` counts minutes, not an ordinal.

### Item 5: the failure report

None. The `t.Errorf` messages print both operands, and the table test prints the path, the got values and the want values.

### Item 6: what the writer says it verified

No red run and no mutation verdict is stated in any of the three commit messages. For `9d25da7`, a red run on the base commit would be informative: the no-responses route panics there (index -1), and `TestHandlePIP_RecordsTheRequestTargetAsSent` does not compile there, so its red run would name a missing field, not the symptom (see F10).

### Item 7: siblings

- Readers of `routes` and `counters` in `handlePIP`: the fallback is applied on the one path that reads the legacy route. Nothing else needs it. None.
- Writes under a read-only root filesystem: the parity suite's `writeObservedSidecar` writes next to the goldens, outside `/tmp` (see F6). The pip-stub and tenant-manager images do no file writes. The suite tests use `TempDir` only where the test asks for it.
- Deleted manifests: no remaining reference in the repo, outside `docs/handovers`.
- Keycloak image pin: the chart and the parity values agree on 26.3.5. `test/svt/common/compose/docker-compose.yml` moved from 26.0 to 26.3.5 in this range, and no commit mentions it (see F11).

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Claimed case "a route with no responses gets 404 when no default route exists" has no test. The `/pip-stub/configure` path with `*` is also untested through the endpoint. | substantive | `test/integration/pipstub/main_test.go:225-251` | Add a case `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, `{"error":"no rule or route for /routed"}`}`. Drive one case through `handleConfigure` with path `*`. |
| F2 | "answers every request whose path has no route of its own" omits a route with no responses, which also falls through. | substantive | `test/integration/pipstub/main.go:35`, `:122-123` | State both cases: no route, or a route with no responses. |
| F3 | "No request path is \*" is false: `OPTIONS *` arrives with path `*`. | substantive, low impact | `test/integration/pipstub/main.go:36` | Say that a `*` request goes to the default route, as any unrouted path does. |
| F4 | "rejects a pinned one" overstates the restricted SCC. A pinned uid inside the namespace range is accepted. | substantive, low impact | `helm-templates/authz-test-stand/templates/_helpers.tpl:21` | Write "rejects a pinned uid outside the namespace range". |
| F5 | The restricted Pod Security claim has no test. I verified it by hand, but no CI check renders the test stand and asserts it. | substantive | `test/scripts/test-chart-render.sh` (no test-stand assertions) | Add render assertions for the test stand: `runAsNonRoot`, `RuntimeDefault`, `allowPrivilegeEscalation: false`, `drop: ALL`, and `readOnlyRootFilesystem` on every container but `idp`. Run them in CI. |
| F6 | On a golden mismatch, `writeObservedSidecar` writes next to the golden under `/app/test/parity/suite`, a read-only path on the stand. Both errors are discarded, so the `.observed.json` sidecar silently never appears. | substantive | `test/parity/suite/compare.go:139-146` (called from `:87`); `test/parity/suite/Dockerfile:27`; `helm-templates/authz-test-stand/templates/suite.yaml:60-64` | Write the sidecar under the `/tmp` emptyDir, or mount an emptyDir at the golden directory. Or say that the stand drops the sidecars. Do not discard the error silently. |
| F7 | The chart adopts nothing. `make e2e-harness` and `make parity-harness` now run `helm upgrade --install` over objects the old `kubectl apply` created: Deployments, Services, the ConfigMaps, the Secret `authz-agent-client-credentials`, and the `runtime-suite` ServiceAccount. Helm refuses to adopt objects without its ownership metadata, so the install fails on a cluster from the previous version. This is expected Helm behavior; I did not run it, since there is no cluster. The commit and the docs state no remedy. | substantive | `Makefile:85-99` (`e2e-harness`), `:137-141` (`parity-harness`); `docs/local-integration-tests.md` | State the remedy (`make e2e-down`, or delete the old objects) in the docs. Run the harness once from a cluster built by the previous version. |
| F8 | `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` was dropped from the e2e Keycloak (base `test/k8s/keycloak.yaml:39`). The commit does not mention it. "imported at every start" is true only on a fresh container filesystem. After a container restart the H2 database persists, and `--import-realm` skips realms that exist. | substantive, low impact | `helm-templates/authz-test-stand/templates/idp.yaml` (no equivalent env); `values.yaml:15-16`; `test/k8s/README.md:16` | Restore the flag, or name its removal in the commit and correct "at every start". |
| F9 | Limit: `helm test --timeout 15m` (`Makefile:102`) equals `suite.activeDeadlineSeconds: 900` (`values.yaml:99`). Helm's clock starts before the Job's deadline clock, so Helm gives up first. Raising the documented value has no effect beyond 15 minutes. | substantive | `Makefile:102`; `helm-templates/authz-test-stand/values.yaml:99` | Derive the Helm timeout from the Job deadline, so it is longer, or make the deadline the only limit. |
| F10 | No red run is stated. The regression in `9d25da7` (a no-responses route indexed at -1) needs a red run on the base commit that shows the panic or the 404 symptom. | substantive | commit `9d25da7`; `main_test.go:225-251` | Paste the base-commit failure for the default-route cases. |
| F11 | `docker-compose.yml` for the SVT stand moved Keycloak from 26.0 to 26.3.5 with a digest. No commit mentions it. | substantive | `test/svt/common/compose/docker-compose.yml:3` | Name the change in a commit message, or split it out. |
| F12 | The `parity-mt-b` realm and its client are imported into the parity stand. No test, value or doc under `test/parity` or `test/k8s` reads them, apart from the realm's own README. | taste | `test/k8s/parity/idp-seed/parity-mt-b-realm.json`; `test/k8s/parity/idp-seed/README.md:10-12` | Name the case that uses it, or say it waits for a later change. I expect this to be declined without discussion. |
| F13 | "fails when two files declare the same username or id" has no test. The `testdata/realm/` directory has no user file, so the merge has never run with input. The guard is `jq -e` in the Dockerfile. | substantive | `test/parity/suite/testdata/realm/README.md:6-7`; `build/authz-agent-transfer/Dockerfile:45-46` | Run the `chart-files` stage once with a duplicate fixture outside the repo, and paste the failure. |
| T1 | The `run-suite` comment says `helm test` "prints the log only at the end". Without `--logs`, `helm test` prints no log. | taste | `Makefile:100-104` | Say that `kubectl logs -f` streams the log while the Job runs. |
| T2 | `TestHandlePIP_RecordsTheRequestTargetAsSent` has no control. A plain path, where `RequestURI` equals `Path`, would show that the field is not just the decoded path. | taste | `main_test.go:276-287` | Optional: add the plain path as a control. |

No finding is labeled churn.

**Not checked:** I did not run the e2e or parity suites, `make test-stand-files` (Docker), or any `helm test`, since there is no cluster. The Helm adoption failure (F7), the restricted-SCC behavior (F4) and the Keycloak restart behavior (F8) rest on Helm, OpenShift and Keycloak documentation, not on a run. The drift script does not parse Go, YAML, Helm or shell, so comments in those files were read by hand. I did not review the realm JSON content, and no Go doc-comment skill was available to check the Go doc comments against its rules.
