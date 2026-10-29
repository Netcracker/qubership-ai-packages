## Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages. This is the first round, so there is no previous report to check. The drift script ran and printed nothing, because it parses only Java, Kotlin, Groovy, and Scala and the change touches none of them. The Go, Helm, Makefile, YAML, and Markdown comments were read by hand. Of the supplied skills, I loaded `test-authoring` and `english-developer-style`. The Go doc-comment skill (`godoc-authoring`) was not in the supplied set, and the `test-authoring` reference files for Go (`go/testing.md`, `go/testify.md`) were not supplied either, so the Go checks used the `SKILL.md` rules only.

**Runs (no file changed, nothing committed).** `go test`, `go vet`, and `gofmt` on `test/integration/pipstub` all pass. `helm lint` passes for both stands (local Helm v4.3.0; CI pins v4.3.1). I staged the generated files in a scratch copy and rendered both stands, then audited every object: labels, `securityContext`, selectors, `automountServiceAccountToken`. I changed a realm file in the scratch copy and confirmed the `checksum/realms` annotation moves. I ran `make -n` on the suite and harness targets. I ran the `profile` jq filter on a sample user. I did not run `make test-stand-files`, because it writes into the repo's gitignored `files/` tree. I did not run any cluster step.

### Item 1: comments consistent with the code and with each other
Two findings. First, `test/integration/pipstub/main.go:32` says "behaviour is exactly as before" when `PIP_STUB_CONFIG` is unset. That is false once a default route can be configured in that state. Second, `main.go:37-38` narrates the change ("as it did before the default route existed"). No other added line narrates the change. The `idp.yaml` comments on the Keycloak restart and the realm import are accurate for the current env, but see Item 7 below for the dropped flag.

### Item 2: claimed cases covered
Pipstub claims, mapped to tests:
- Unrouted path gets the default answer: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, "an unrouted path gets the default answer".
- Routed path keeps its own answer: same test, "a routed path keeps its own answer".
- Route with no responses falls to the default: same test, "a routed path with no responses gets the default answer".
- No default route gives 404: same test, two cases.
- Sequence across paths: `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`.
- `requestUri` kept as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- **Missing:** a route with no responses and no default route gives 404. The commit claims it, and no case exercises it.

Chart claims (commits 1 and 3). The security-context, label, and selector claims hold on the render. No test or CI step asserts them, and `test/scripts/test-chart-render.sh` covers only the agent and policy-admin charts.

Commands the change tells someone to run:

| Command (where) | Promised outcome | Run in CI? |
|---|---|---|
| `make test-stand-files` (README, Makefile) | files written under `files/` | Yes, `integration-tests.yaml` chart job |
| `make e2e-harness`, `make e2e-install`, `make e2e-suite`, `make e2e-logs` | install Ready; suite exit status | Yes, `kind-e2e` |
| `make parity-harness`, `parity-install`, `parity-suite`, `parity-logs` | same | Yes, `kind-parity` |
| `make e2e-restart`, `parity-restart`, `e2e-down` | rollouts; cluster deleted | No |
| `helm test authz-test-stand --timeout 15m --logs` (chart README:64) | log printed, exit status | No. The Makefile runs `helm test` without `--logs` |
| `helm upgrade ... --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...` (docs §6) | subset run | No |
| `helm upgrade --install ... --set TAG=<version> -f my-values.yaml` (chart README:58) | install from transfer image | No. Rendered here: the ghcr image names and tag come out as documented |
| `docker create ... true; docker cp` (chart README:42-43) | charts copied out | No |

For the `none` rows, the outcome depends on a live cluster, or on a `helm test` form that differs from the one that runs. The `--reuse-values` path and the `--logs` form are not verified. The override itself renders into `RUNTIME_SUITE_RUN` and into `-test.run` as documented.

### Item 3: boundaries, partitions, and the negative control
The pipstub tests have the right controls: a routed path keeps its own answer, and an unrouted path without a default gives 404. The partition named under Item 2 is missing.

Pre-existing state: CI always starts from a fresh kind cluster. A stand installed by the base harness has kubectl-applied objects with the same names (`keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, the ConfigMap `keycloak-realms`, the Secret `authz-agent-client-credentials`; in parity `idp`, `pip-mock`, `pip-mock-config`, `parity-realms`). Helm does not adopt objects without its ownership metadata, so `make e2e-harness` and `make parity-harness` will likely fail on such a namespace. Nothing in the change, the docs, or the Makefile covers that case. Nothing was run here to confirm it.

### Item 3a: level, placement, environment
The pipstub tests are in-process, sit beside the existing `TestHandlePIP_*` tests, and reuse `resetState`. `go-build.yaml` runs that module, so they execute in CI. The chart's security and label claims are observable with `helm template`, which is the level `test-chart-render.sh` already uses, but nothing asserts them there or on the cluster. The `restricted` Pod Security Standard is not enforced by any namespace label in CI.

### Item 4: names by content
One taste item: `test/k8s/test-stand-values.yaml:21` says "A second instance", which is an ordinal. The instance is already named by content ("the entitlements endpoint"). No other ordinal references in the changed files.

### Item 5: the failure report
None. The added Go assertions print both operands, and no boolean is wrapped around a comparison.

### Item 6: what the writer says it verified
Not stated. No commit message or description gives a red run on the base commit or a mutation verdict for the new pipstub tests. The base commit panics on a route with no responses (`Responses[-1]`), so a red run would be easy to state. I did not run one, per the review rules.

### Item 7: siblings of the change
- Rule-engine sequence (`matchRule`, `main.go:276`) already guards `len > 0`, so the empty-slice defect has no sibling.
- The deployment names in `E2E_LOCAL_DEPLOYMENTS` and `e2e-logs` match the rendered Deployments.
- No references to the 14 deleted manifests remain.
- `.dockerignore` and `.gitignore` both cover the generated `files/` tree.
- The Keycloak `OVERWRITE_EXISTING` flag was removed from the e2e Keycloak only; the parity Keycloak never had it.
- The e2e troubleshooting row in `docs/local-integration-tests.md:190` names a wait the Makefile no longer runs. This is a finding (below).

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Claimed case with no test: a route with no responses and no default route gives 404 | substantive | `test/integration/pipstub/main_test.go:228-241` | Add the case `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, ...}` |
| 2 | "exactly as before" is false once a default route is set with `PIP_STUB_CONFIG` unset; "as it did before the default route existed" narrates the change | substantive | `test/integration/pipstub/main.go:32`, `:37-38` | Delete the history clause; state the behavior with the default route |
| 3 | Dropped `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` from the e2e Keycloak, undisclosed. The "imports at every start" claim holds only for a fresh container | substantive | `helm-templates/authz-test-stand/templates/idp.yaml:49-58`; base `58316ca:test/k8s/keycloak.yaml:38-39` | Restore the flag, or state in the commit why it is gone |
| 4 | "the startup probe allows five" does not say five what; the value is 60 × 5 s, so five minutes | substantive | `idp.yaml:65` | Write "five minutes" |
| 5 | On a golden mismatch the observed sidecar write fails silently on the read-only root filesystem (errors discarded), so the file is lost on the stand. The diff still appears in the failure | substantive | `test/parity/suite/compare.go:87`, `:139-146`; `templates/suite.yaml:57-64` | Give the parity suite a writable location for the sidecar, or stop discarding the error and name the loss in the commit |
| 6 | Troubleshooting row names `rollout status deploy/keycloak`, which the Makefile no longer runs (it uses `helm upgrade --wait`) | substantive | `docs/local-integration-tests.md:190`; `Makefile:86` | Describe the Helm wait, or the failure a reader will actually see |
| 7 | Pre-existing state not covered: a stand from the base harness has kubectl-applied objects Helm will not adopt. No run, no remedy | substantive | `Makefile:86`, `:150` | Run `make e2e-harness` over a base-installed namespace, or document the teardown and say so |
| 8 | Claimed "restricted PSS" with no test and no CI enforcement | substantive | `helm-templates/authz-test-stand/README.md:8-11`; `test/scripts/test-chart-render.sh:25-26` | Add a render assertion for the test stand's securityContext and labels, or label the kind namespace `pod-security.kubernetes.io/enforce: restricted` in `kind-e2e` |
| 9 | Claimed profile fill (first name, last name, email) runs in no test. No user file exists, so the code path is never exercised in CI | substantive | `build/authz-agent-transfer/Dockerfile:32-47`; `test/parity/suite/testdata/realm/README.md` | Add a sample user file and an assertion on the derived fields; my sample run gave `R29LevelM2M` and the defaults as the comment states |
| 10 | Commit 9d25da7 names a parity case that needs a User Management stub. No stand config or test in this range sets route `*` | substantive | commit `9d25da7` message; `test/k8s/test-stand-values.yaml`, `test/k8s/parity/test-stand-values.yaml` | Name the consumer as a follow-up in the commit or PR, or wire it up here |
| 11 | `TAG` comment lists `tenant-manager` as an image of the release version, but the release does not publish it | substantive | `helm-templates/authz-test-stand/values.yaml:9-10` vs `:58-59` | Drop `tenant-manager` from the list |
| 12 | Documented commands with no run in CI, and one documented form that differs from the one that runs (`helm test --logs`) | substantive | `helm-templates/authz-test-stand/README.md:42-43`, `:58`, `:64`; `docs/local-integration-tests.md:139-140` | Run the form on a kind stand, or replace it with the form the Makefile runs |
| 13 | "A second instance" names an instance by ordinal | taste | `test/k8s/test-stand-values.yaml:21` | Write "The instance for the entitlements endpoint" |

### What this review did not check
The cluster behavior: pod admission under the restricted standard, Helm's adoption of old objects, Keycloak's realm import and its management-path claim, and the runtime and parity suites themselves. Also `make test-stand-files` and the transfer-image build were not run, and the Go doc-comment rules and the Go `test-authoring` references were not applied because they were not supplied. One stray copy went to `/tmp/x` during my checks; I removed it.
