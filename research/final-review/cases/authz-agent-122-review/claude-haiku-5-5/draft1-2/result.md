# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages (`17b17fc`, `9d25da7`, `8b85515`) and the test-class comments. There is no previous report, so there is no §4 table. I read the whole diff (48 files). I loaded `test-authoring` and `english-developer-style` from the given skills folder. The Go doc-comment skill is not in that folder, so the Go comments were checked against Item 1 alone.

**Drift script.** It ran and printed nothing. It parses only Java, Kotlin, Groovy and Scala, and no changed file is one of those, so I checked the Go, Helm, Makefile and Markdown comments by hand.

**Checks I ran (nothing in the repo changed):**
- `pipstub`: `go vet` and `gofmt -l` are clean. The new tests pass.
- `helm lint` passes for both stand values files, run on a copy of the chart with `files/` staged from the sources the Dockerfile copies. `helm template` renders with the expected labels, `runAsNonRoot` and read-only settings on the right containers, and a realm checksum that changes with realm content.
- `make -n e2e-suite` expands the `run-suite` recipe as intended.
- The `chart-files` jq steps, run locally on a scratch set: the profile fill gives `Parity`, `R29LevelM2M` and the `@example.test` email, and a duplicate username makes `jq -e` exit 1.
- Go's request parsing: `OPTIONS *` gives `URL.Path == "*"`.

Not run: `docker build` of the stage (the pinned base images are not cached, and I did not pull), any cluster install, the restricted Pod Security check, and OpenShift.

## Item 1: comments consistent with the code and each other

Substantive findings: #1–#4, #12, #13, #14. Taste: #15–#17. The Go doc comments on `callRecord.RequestURI`, `defaultRoute`, the `handlePIP` step-2 comment, the test comments, and `testify/helpers.go` `LoadConfig` are consistent with the code.

## Item 2: claimed cases covered

Covered: the default-route cases, the sequence across paths, the routed-path control, the 404 controls, and the request-target recording. Not covered: #5, #7, #8, and the security-context claims in #7.

Commands the change tells someone to run: `make -n` shows the recipe as intended, and the `helm test` flags `--logs` and `--timeout` exist. `make e2e-harness`, `make parity-harness`, and the suite targets run in the CI kind jobs. `make test-stand-files` was not run.

## Item 3: boundaries, partitions, negative control

The Go tests have boundary and control cases. The Helm side has no partition or negative-control test at all. The pre-existing state is finding #11.

## Item 3a: level, placement, environment

The Go tests are in-process, beside the existing tests, and `go-build.yaml` runs them. The chart's properties have no test at the smallest level, which is finding #7. `kubectl wait --for=create` needs kubectl 1.31 or later; the local kubectl is 1.33, and the CI version is not checked.

## Item 4: names by content

Taste: #15 and #16.

## Item 5: failure report

None. The Go assertions print their operands, and the test names state the case.

## Item 6: what the writer says it verified

Substantive: #6. None of the three commit messages states a red run on the base commit or a mutation verdict. `9d25da7` describes a real defect (a route with no responses indexed at -1), so its regression case needs that evidence.

## Item 7: siblings

- Pod and container security contexts: all four Pods include the pod-level context, and every container calls the container helper (`idp.yaml:40,80`, `pip-stub.yaml:37,58`, `tenant-manager.yaml:31,48`, `suite.yaml:37,57`).
- The `README.md` sentence and the docs row in #1 and #2 are stale siblings of this change.
- The parity suite's writes under a read-only root are #10.

## Item 2a: change with no code

Not applicable. The change has code, so the form was applied to the Go, Helm, Makefile, and Markdown files as written.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | "CI builds both" is stale: `docker-dev-config.json` now lists five components. | Substantive | `README.md:59-60` | Drop the count and name the images the file lists. |
| 2 | Troubleshooting row names `rollout status deploy/keycloak`, which `e2e-harness` no longer runs. | Substantive | `docs/local-integration-tests.md:190` | Name the `helm --wait` timeout instead. |
| 3 | "M2M client-credentials Secret the chart expects the platform to provision" is wrong on the kind stand, where `clientCredentials.enabled: true` makes the chart create it. | Substantive | `Makefile:82-83`, `test/k8s/test-stand-values.yaml:37-38` | Say the chart creates it on kind. |
| 4 | "No request path is `*`" is false: Go gives `URL.Path == "*"` for `OPTIONS *`. The conclusion holds, since `*` answers like an unrouted path. "Behaviour is exactly as before" is untrue once `*` is configured through `PUT /pip-stub/configure`. | Substantive | `test/integration/pipstub/main.go:32,36` | Correct the reason. Narrow "exactly as before" to the rule engine. |
| 5 | `/pip-stub/configure` taking `*` has no test. All three tests set `routes[defaultRoute]` directly, so `handleConfigure` never sees `*`. | Substantive | `test/integration/pipstub/main_test.go:225-270` | Add a test that PUTs `[{"path":"*",...}]` to `handleConfigure`, then GETs an unrouted path. |
| 6 | No red run or mutation verdict in `9d25da7`, which fixes a panic (index -1). | Substantive | commit `9d25da7`; regression case at `main_test.go` (routed path with no responses) | State the red run on the base commit. |
| 7 | The chart's security properties (non-root, `RuntimeDefault`, drop ALL, no escalation, read-only except Keycloak, `/tmp` emptyDir, labels, selectors) have no test. `helm lint` does not check them, and the render script covers only the trusted-provider constructor. | Substantive | `helm-templates/authz-test-stand/templates/*`; `test/scripts/test-chart-render.sh` | Add render assertions for these fields in the existing render script or a sibling. |
| 8 | No namespace carries `pod-security.kubernetes.io/enforce: restricted`, and no CI job runs under it. The title claim is untested. | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); no CI job | Label the harness namespaces `restricted`, or name the run as follow-up. |
| 9 | The profile fill and the duplicate check have no test. `testdata/realm/` has no user file, so the path never runs in the repo. My local run shows the logic is right. | Substantive | `build/authz-agent-transfer/Dockerfile:40-47`; `build/authz-agent-transfer/profile.jq` | Add a fixture user file, run through the stage in CI, asserting the filled fields and a failing duplicate. |
| 10 | `writeObservedSidecar` writes under the working directory (`/app/test/parity/suite`) with errors discarded. In the chart's read-only root, the mismatch evidence is silently lost, and the `/tmp` emptyDir does not cover it. Not in any commit message. Not run (no cluster). | Substantive | `test/parity/suite/compare.go:140-146` | Write under `/tmp`, mount a writable volume there, or name it as follow-up. |
| 11 | Pre-existing state: the earlier harness created objects with `kubectl`, under the names the chart renders. Helm should refuse to install over them, so `make e2e-harness` on an old cluster should fail. Not run. Docs give `make e2e-down` for "cluster left behind", but no row covers this conflict. | Substantive | `docs/local-integration-tests.md:193`; old `test/k8s/*.yaml` | Run `make e2e-harness` on such a cluster, or document `make e2e-down` as the remedy. |
| 12 | The e2e stand is said to run Keycloak with two realm files. It imports all four (`test/k8s/authn/*-realm.json`, both tenant realms included). | Substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82`; `Dockerfile:27` | Say "the realms of `test/k8s/authn/`". |
| 13 | "The startup probe allows five" has no unit. It is five minutes (60 × 5 s), and a reader could take it as seconds. Wording inherited from the old `keycloak.yaml`. | Substantive | `helm-templates/authz-test-stand/templates/idp.yaml:65` | Write "five minutes". |
| 14 | "Rejects a pinned one": on OpenShift, `MustRunAsRange` checks a pinned UID against the namespace range. It does not reject every pinned UID. Not verified here, since there is no OpenShift. | Substantive (if the SCC behaves as I believe) | `helm-templates/authz-test-stand/templates/_helpers.tpl:21` | Say "a UID outside the namespace range". |
| 15 | "A second stub instance" and "A second instance" name an ordinal where the content name `entitlements-mock` exists. | Taste | `docs/local-integration-tests.md:18`; `test/k8s/test-stand-values.yaml:21` | Name the instance. |
| 16 | "Keycloak has its own image and pull policy below" is positional. | Taste | `helm-templates/authz-test-stand/values.yaml:10-11` | Name the key, `idp`. |
| 17 | "It prints the log only at the end" describes `helm test --logs`, which the recipe does not pass. | Taste | `Makefile` `run-suite` comment | Say that `helm test` prints nothing here, so the log is streamed with `kubectl logs -f`. |

**Observations, not findings.** `parity-mt-b` is imported, but nothing in the repo consumes it (the README and the `tenant-id` value are the only references). The old Keycloak's `JAVA_OPTS_APPEND` migration setting was dropped without mention. It has no effect on a fresh dev-mode container. The `svt` compose image bump is in no commit message.

**Not checked:** the suite and the kind and CI runs; a Helm install on a cluster; Keycloak 26 behaviour (`KC_HOSTNAME` with a path, the management-port relative path); the `chart-files` Docker stage; the restricted Pod Security run; OpenShift; the wording of the whole diff beyond the items above, since this review did not do a style pass.
