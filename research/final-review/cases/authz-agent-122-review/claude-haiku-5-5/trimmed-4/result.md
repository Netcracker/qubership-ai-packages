# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages of `8b85515`, `9d25da7`, and `17b17fc`, plus the Go test class comments. This is the first round, so there is no previous report to check against.

**Skills.** I loaded `test-authoring` and `english-developer-style` from the given skills directory. I did not open `test-authoring/references/go/*.md`. The Go doc-comment skill (`godoc-authoring`) is not in that directory, so it was not loaded. Item 5 is judged from `test-authoring` §7.

**Drift script.** It ran and printed nothing. It parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, and none of the changed files are those. Item 1 was done by reading the Go, YAML, Makefile, and Dockerfile comments.

**Checks run locally.** No cluster was used.
- `go test` in `test/integration/pipstub`: passes, including the three new tests.
- `golangci-lint run ./...` there: 0 issues.
- `docker build --target chart-files` into the scratchpad: succeeds.
- `helm lint` of the test-stand chart with both values files, and with defaults: passes.
- `helm template` with both values files: renders. In the rendered e2e manifests, all five containers have `runAsNonRoot`, `RuntimeDefault` seccomp, `allowPrivilegeEscalation: false`, and `drop: [ALL]`. `readOnlyRootFilesystem` is `true` everywhere except Keycloak. The suite Job's emptyDir is `sizeLimit: 256Mi`.
- `make -n` on `e2e-harness`, `parity-harness`, `e2e-suite`, and `parity-suite`: expansions are as intended.
- Go's `url.ParseRequestURI("*")` returns `Path == "*"`.

---

## Item 1: comments consistent with the code and with each other

`pipstub/main.go:36` says "No request path is \*". That is false. An `OPTIONS *` request has `URL.Path == "*"`, so it is answered by the default route. The conclusion that the default route never shadows a real route still holds. See the table.

`values.yaml:9-11` and `values.yaml:86-87` also have sentences a reader can take wrongly. See the table.

The other comments I checked match the code: the `handlePIP` precedence comment, the `defaultRoute` const, the `RequestURI` field, the `helpers.go` `LoadConfig` comment, the testify Dockerfile comment, the `idp.yaml` "no bootstrap admin" comment (the suites use `KcAdminUser` only for a password grant), and the `profile.jq` and Dockerfile comments.

## Item 2: claimed cases covered

| Claimed case | Test |
|---|---|
| Unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, case 1 |
| Routed path keeps its own answer | same, case 2 |
| Route with no responses falls through to the default route | same, case 3 |
| Route with no responses falls through to 404 | **none** (see finding 2) |
| Default route serves its sequence across paths, clamped to the last | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| Stub with no default route answers 404 | same test, cases 4 and 5 |
| Request target kept as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes the path `*` | **none** (see finding 5) |
| Restricted PSS: security contexts, seccomp, read-only root, `/tmp` emptyDir | **none** (see finding 4) |
| Labels, selectors, realm import, restart on realm change, off by default, Secret, Job as hook | **none** beyond `helm lint` (see finding 4) |

The tenant-manager 404 is covered by its own `main_test.go`.

## Item 3: boundaries, partitions, negative control, pre-existing state

- **Default route.** The boundary and control cases are present: routed versus unrouted, empty versus absent default route, and the sequence clamp. The gap is the zero-response route with no default. On the base commit, `counters[path]` is 0 and `Responses[-1]` panics, so this is a real regression case the message claims to fix.
- **Chart.** There is no negative control and no render test for the security contract.
- **Pre-existing state.** Not covered. See finding 1. The change replaces objects that `kubectl apply` created on an existing kind cluster, and no run starts from that state or documents a remedy.
- **Limits.** The inner limit fires first at the defaults: `-test.timeout 600s` in `suite.args` fires before `activeDeadlineSeconds: 900`. Raising the deadline still has no effect, because of the fixed `helm test --timeout 15m`. See finding 3.

## Item 3a: level, placement, environment

The new Go tests are in-process, appended to `main_test.go` beside the existing tests, and reuse `resetState`. `go-build.yaml` runs the pipstub package with coverage, so they run in CI. No skip logic is involved.

The chart is only checked by `helm lint` in `integration-tests.yaml:83-84`. `test-chart-render.sh` shows the repository's convention for chart behavior, and this chart has no equivalent. See finding 4.

## Item 4: names by content, not position

None found. The case names, the parameterized labels, and the Makefile macro parameters all name content.

## Item 5: failure report

None found. The `t.Errorf` calls print both operands. The `if status != … || body != …` conditions are the comparisons themselves, which §6 allows.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a cluster run. I say so as the skill requires. For the default-route tests, a base-commit run would fail with `undefined: defaultRoute`, a missing symbol. The behavioral red is the zero-response case, which the table does not yet contain (finding 2).

## Item 7: siblings

- `handleConfigure` has one caller path, and it works for `*` (see finding 5).
- The `callRecord` JSON change is additive.
- Both `run-suite` call sites are changed.
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` match the chart's instance names.
- `git grep` finds no remaining references to the deleted manifests outside the chart.
- The new `make test-stand-files` step in `integration-tests.yaml` is present.

---

## Findings

All findings are **Substantive** requests.

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Objects created by the old `kubectl apply` manifests have the names the chart now creates: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ServiceAccount `runtime-suite`; ConfigMaps `keycloak-realms`, `pip-mock-config`; Secret `authz-agent-client-credentials`. Parity has `idp`, `pip-mock`, `entitlements-mock` likewise. Helm 3 refuses to adopt unowned objects, so `make e2e-harness` or `parity-harness` on an existing kind cluster from the old Makefile should fail. This is from Helm's ownership rule, not a run. No remedy is documented beyond `make e2e-down`. | Substantive | `Makefile:85`, `Makefile:149`; base `test/k8s/*.yaml` | Run the harness once on a cluster that holds the old objects, and document or script the remedy, such as deleting the old objects or the namespace first. |
| 2 | No test for a routed path with no responses and no default route, which the commit says answers 404. The base commit panics on this case. | Substantive | `test/integration/pipstub/main_test.go:225-251`; code at `main.go:237` | Add a case: `/routed` with `[]pipResponse{}`, default `nil`, expecting 404 and `{"error":"no rule or route for /routed"}`. |
| 3 | The suite's timeouts do not form the ordering the values file implies. `helm test --timeout 15m` is fixed in the Makefile, so raising `suite.activeDeadlineSeconds` above 900 has no effect on `make e2e-suite` or `parity-suite`. The `-test.timeout 600s` in `suite.args` fires first, so raising the deadline above 600 does nothing unless the args change too. | Substantive | `Makefile` `run-suite` (about lines 100-108); `helm-templates/authz-test-stand/values.yaml:92-99`; `test/k8s/test-stand-values.yaml:52-58` | Derive the Makefile wait from the deadline, or pass it as a value, and say in `values.yaml` which limit fires first. |
| 4 | The security contract, labels, selectors, restart annotation, and off-by-default behavior of the chart are claimed but not checked by any test or render assertion. CI runs only `helm lint`. | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:23-40`; `.github/workflows/integration-tests.yaml:83-84`; pattern in `test/scripts/test-chart-render.sh` | Add render assertions for each container's security context, with Keycloak's `readOnlyRootFilesystem: false` as the exception, plus labels and the empty default render, in the style of `test-chart-render.sh`. |
| 5 | `/pip-stub/configure` accepting `*` is claimed but not tested. The tests write `routes[defaultRoute]` directly and never call `handleConfigure`. | Substantive | `test/integration/pipstub/main.go:385-398`; `main_test.go:225-251` | Add a test that PUTs `[{"path":"*","responses":[…]}]` to `handleConfigure` and checks that an unrouted path gets the answer. |
| 6 | "No request path is \*" is false. An `OPTIONS *` request has path `*` and is answered by the default route. | Substantive (low) | `test/integration/pipstub/main.go:36` | Reword to say the default route also answers an `OPTIONS *` request. |
| 7 | The TAG and pull-policy comment lists `pip-stub`, `authz-parity-suite`, and `tenant-manager` as images this repository builds, and omits `authz-runtime-suite`. The same TAG and pull policy reach that image through `suite.imageRepository`. | Substantive (low) | `helm-templates/authz-test-stand/values.yaml:9-11`; `test/k8s/test-stand-values.yaml:48` | Add the runtime suite to the list. |
| 8 | "`helm test` runs it once the stand and the charts under test are up" reads as a Helm guarantee. Helm does not wait; the Makefile order does. | Substantive (low) | `helm-templates/authz-test-stand/values.yaml:86-87` | Say that the run has to follow the install, and that `make` does this ordering. |

## What the review did not check

No cluster was used, so the chart was not installed, PSS admission was not exercised, and Helm's ownership conflict in finding 1 was not reproduced. The Keycloak image's non-root user was not verified. The `make e2e-images` builds and the parity and runtime suites were not run. I did not open `go/testing.md` or `go/testify.md`, and `godoc-authoring` was not available. The English-style pass covered only wording that reads wrongly. The docs pages (`docs/local-integration-tests.md`, `test/k8s/README.md`, `test/parity/README.md`, `REALM-DESCRIPTION.md`) were spot-checked, not read in full.
