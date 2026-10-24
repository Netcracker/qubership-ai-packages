# Final review: `58316ca..17b17fc` (3 commits)

There was no task statement, so the claimed cases come from the three commit messages, as the skill allows. No earlier report exists for this change. The drift script exited 0 with no output because it only parses Java, Kotlin, Groovy and Scala, and this change is Go, YAML, Helm, Makefile and Markdown. I listed the changed members by hand.

Runs I made:
- `go test ./...` in `test/integration/pipstub` passes.
- I copied the chart to the scratchpad and generated `files/` there with the Dockerfile's jq pipeline. `helm lint` (v4.3.0) passes for both values files. `helm template` with default values renders nothing.
- With both values files, every rendered object carries `app.kubernetes.io/name` and `helm.sh/chart`. Every Pod has `runAsNonRoot` and `RuntimeDefault`, and only Keycloak's root filesystem is writable.
- Editing a realm file changes `checksum/realms`.
- `profile.jq` fills in a sample user correctly and keeps the fields the user already declares.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-37` and `:122-124`.** Both the package doc and the `defaultRoute` comment say the default route answers "every request whose path has no route of its own". The code at `:229-237` also sends a path whose route has **no responses** to the default route, and the commit claims that case. A reader of either comment would expect such a route to answer 404 (or index at -1).
- **`main.go:39-40`.** "…answers an unrouted request 404, as it did before the default route existed" describes the history of the change, not the code.
- **`Makefile:191-192`.** "the loop polls for up to three minutes". That holds only while a Pod exists. With no Pod, each `kubectl logs job/…` waits `--pod-running-timeout` (20s by default, per `kubectl logs --help`), so 90 × (20s + 2s) ≈ 33 min. Details under item 3.
- **`docs/local-integration-tests.md:104`.** The `e2e-harness` row says the target installs "… and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so the install neither creates nor waits for it. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **`helm-templates/authz-test-stand/values.yaml:9-11`.** The list of images that `TAG` applies to names "pip-stub, authz-parity-suite, and tenant-manager". `TAG` also tags `local/authz-runtime-suite` through `suite.imageRepository`, which the e2e stand uses.
- **`test/k8s/parity/idp-seed/parity-realm.json`, the `ROLE_MT_READER` description.** It cites "TestTenantScopedDecisions and others". No such test exists (`git grep` finds nothing), and nothing outside the realm files uses `ROLE_MT_*`, `mt-a`, `parity-mt-b` or `parity-m2m-tenant-*`.
- **`README.md:58`.** "CI builds both via `.github/docker-dev-config.json`" is now false: that file lists five images (see item 7).
- Checked with no finding: the `callRecord.RequestURI` comment, `LoadConfig` (`helpers.go:77`), the testify Dockerfile, the `test/k8s/values.yaml` comment, the `_helpers.tpl` comments, the `idp.yaml` probe and startup comments, the transfer Dockerfile header and its profile comment (both match the jq output I ran), and the chart README.

## Item 2: claimed cases covered

| Claim (commit) | Covered by |
| --- | --- |
| A route registered as `*` is a default route that answers unrouted paths (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses and no default route answers 404 (the old index -1) | **none**. The 404 cases use an *unrouted* path. |
| A stub with no `*` answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | **none through configure**. Every test writes `routes[defaultRoute]` directly. |
| The chart's parts are off by default (8b85515) | My `helm template` with defaults renders 1 byte; nothing in CI checks it |
| Keycloak imports the realms; Pod restarts on a realm change | Kind jobs (import only); restart: my render only, no test |
| pip-stub instances, tenant-manager map, M2M Secret, suite as helm test hook, make targets | `kind-e2e` and `kind-parity` jobs |
| `make test-stand-files` runs the chart-files stage | The lint job in `integration-tests.yaml` |
| The merge adds the user files, fills in the profile fields, and fails on a duplicate user | **none**. `testdata/realm/` holds no user file, so every run merges zero users. |
| The parity realm gains `parity-mt-b` | The kind parity import only; no case uses it |
| The release publishes three more images | The release workflow (manual, not run here) |
| The stand starts under the **restricted** Pod Security Standard (17b17fc) | **none**. No namespace is labeled `pod-security.kubernetes.io/enforce` anywhere; `--create-namespace` adds no label. |
| Non-root user, read-only root filesystem except Keycloak, `/tmp` emptyDir | Kind jobs: the kubelet enforces `runAsNonRoot`, and the image users are numeric (`10001:10001`) |
| Labels on every object, selectors unchanged | My render; the selectors match 8b85515. No repo test. |
| No `runAsUser`, so OpenShift's SCC can assign one | Not testable here; it is a design reason |

**Command lines in the changed files:**
- **`make test-stand-files`, `make e2e-harness`, `make parity-harness`, `make e2e-suite`, `make parity-suite`.** The CI jobs run these exact commands.
- **`run-suite` (`kubectl wait --for=create`).** CI runs it with whatever kubectl `kind-action` installs. The docs' prerequisites table names no kubectl version, and `--for=create` needs kubectl 1.31 or later. On older kubectl the `&&` skips the poll, `logs -f` fails on the pending Pod, and the log is not streamed, although `helm test` still decides the exit code.
- **Chart README, `docker create … true` / `docker cp` / `docker rm`.** Run by: none. `docker create` does not run `true`, so the scratch image is fine. No finding.
- **Chart README, `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`.** Run by: none. No problem found from reading it.
- **Chart README, `helm test … --timeout 15m --logs`.** Run by: none. The Makefile form has no `--logs`. The same 15m limit problem applies (item 3).
- **`docs/local-integration-tests.md`, the `helm upgrade --reuse-values --set …` subset recipe.** Run by: none. `--reuse-values` keeps the earlier `-f` values and `--set BASE_URL` in Helm 3 and 4. No finding.

**Hunks no sentence in the commits claims:**
- **`test/svt/common/compose/docker-compose.yml`.** Keycloak `26.0` → `26.3.5@sha256…`, in a stack the change does not otherwise touch.
- **`.github/docker-dev-config.json`.** Three images added to the CI dev builds. The commit claims only the release from `.qubership/docker.cfg`.
- **`test/k8s/parity/idp-seed/parity-realm.json`.** 318 added lines: the `ROLE_MT_*` roles, the `parity-level-claim` mapper, five tenant M2M clients, and the `mt-a` and `mt-a-admin` users. The commit says only that the parity realm "gains a second tenant realm". This also differs from the pip-stub commit, which held back its stub instance until "the cases that use it".

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.** Own route (absent, with responses, empty) × default route (absent, with responses, empty). Five of the six combinations that matter are tested. The missing one is the old failure: **a routed path with no responses and no default route**, which must answer 404. Controls are present: "a routed path keeps its own answer" and the no-default 404 case.
- **Inherited state.** A kind namespace from the old harness (`authz-e2e` or `authz-parity`) still holds `kubectl apply`-created objects that this chart now renders under the **same names**:
  - Secret `authz-agent-client-credentials`
  - ConfigMaps `keycloak-realms` and `pip-mock-config`
  - Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `idp`, `pip-mock`
  - ServiceAccount `runtime-suite`

  `helm upgrade --install` will refuse to adopt them ("invalid ownership metadata"). Every run in the change starts from a fresh kind cluster, and no doc names the remedy: `make e2e-down`, deleting the namespace, or `--take-ownership`.
- **`E2E_HELM_ARGS` now reaches the stand.** The keys it shares with the agent and policy-admin charts are `TAG` and `IMAGE_PULL_POLICY`, and they mean the same thing in the stand (tag and pull policy of repo-built images). No finding.
- **Replaced mechanism, `e2e-suite` / `parity-suite`.** Worked out from the code; I did not run it.
  - *Missing image* (pull policy `Never`, the usual kind fault):
    - Old: `wait --for=condition=Ready pod … --timeout=3m` fails at **3 min** with a timeout naming the pod.
    - New: the loop runs ~3 min with its output discarded; `logs -f` prints the waiting reason once; then `wait $helm_pid` holds until `activeDeadlineSeconds` (900s) or `helm test --timeout 15m` fires, so about **15 min**.
  - *No Pod is ever created* (an admission rejection, which is exactly what an enforced restricted PSS does to a non-compliant Pod):
    - Old: `kubectl wait pod -l job-name=…` with nothing matching fails **immediately**.
    - New: 90 × (20s `--pod-running-timeout` + 2s) ≈ **33 min**, past the CI job's `timeout-minutes: 30`.
  - No sentence in the change accepts either trade.
- **Replaced mechanism, `e2e-harness` / `parity-harness`.** On a missing stub image:
  - Old: `rollout status deploy/pip-stub --timeout=2m` fails at 2 min and names the Deployment.
  - New: `helm --wait --timeout 10m` fails at 10 min.
  - No sentence accepts this either.
- **Limits on the suite run:**
  - `suite.args` `-test.timeout 600s`, a documented value.
  - `suite.activeDeadlineSeconds` = 900, a documented value.
  - `helm test --timeout 15m`, fixed in `Makefile:196` and in the chart README.
  - The CI job's `timeout-minutes: 30`.

  If `activeDeadlineSeconds` is raised past 900, Helm's fixed 15m fires first and the setting has no effect through `make`. At the defaults, Helm's 15m starts before the Job exists, so it fires before the 900s deadline rather than after it.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process (`httptest` into `handlePIP`), sit in `main_test.go` beside the existing tests, and share `resetState`. The `go-build.yaml` matrix runs `test/integration/pipstub`. The one gap is that the `configure` → `*` path goes untested.
- The security-context and label claims can be observed from rendered manifests, with no cluster. The repository already has `test/scripts/test-chart-render.sh` for render assertions, but nothing asserts on the test-stand chart: CI only lints it. The restricted-PSS claim is the one that needs a cluster, and no job enforces it (item 2).

## Item 4: names by content, not by position

None. The test names, subtest names and comments refer to things by content. `$(1)`/`$(2)`/`$(3)` in the `run-suite` comment are Make parameters and are named.

## Item 5: the failure report

None. Each failure message prints the request and both got and want (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, and `requestUri %q, path %q, want …`). `t.Fatalf` is used only before indexing `calls[0]`.

## Item 6: what the writer says it verified

None of the three commits shows a red run on the base commit or a mutation verdict. That includes the pip-stub index -1 failure the commit names, and the PSS claim. No kind run output is quoted either.

## Item 7: siblings of the change

- **`/pip-stub/configure` callers** (testify `check_resource_test.go`, `entitlements_test.go`, `pip_admin_test.go`, and the parity `PipController`). None registers `*`, so their behavior does not change. Nothing in `test/` decodes `/pip-stub/calls` with `DisallowUnknownFields`, so the new `requestUri` field is safe for them.
- **Image set.** `.qubership/docker.cfg`, `docker-dev-config.json`, the `docker-release.yaml` comment and README `:62-67` are updated. **`README.md:58` still says "CI builds both"**, which is now five images.
- **Removed manifests.** `git grep` finds no remaining reference to `runtime-suite-job.yaml`, `keycloak.yaml`, `pip-mock.yaml`, `tenant-manager.yaml`, `m2m-credentials` or `parity-realms` outside the handovers.
- **Restart lists.** `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` still name the chart's Deployments.
- **Keycloak version.** The chart's `26.3.5` digest matches the old manifests. The svt compose bump is the sibling, but no commit claims it.
- **Read-only root filesystem.** One file write was found: `test/parity/suite/compare.go:145-146`, the observed sidecar. It ignores errors, so it does not change the result. No finding.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Restricted-PSS claim has no run: no namespace enforces it | Substantive | `Makefile:178,251` | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` in the harness targets (all three charts then run under it), and add render assertions for securityContext and labels to `test-chart-render.sh` |
| 2 | `run-suite` fails later and prints less than the old wait: ~15 min instead of 3 on a missing image; ~33 min instead of immediate when no Pod is created; the "three minutes" comment is false | Substantive | `Makefile:189-201` | Bound each attempt (`--pod-running-timeout=2s`), stop the loop when `helm_pid` exits, and state the measured fault runs, or accept the trade in a sentence |
| 3 | `helm --wait --timeout 10m` replaces the 2m per-Deployment rollout waits; a missing stub image now fails at 10 min | Substantive | `Makefile:178,251` | Run the fault and state the duration and output, or accept it |
| 4 | `helm test --timeout 15m` is fixed, so raising `suite.activeDeadlineSeconds` has no effect, and at the defaults Helm fires before the deadline | Substantive | `Makefile:196`; chart `README.md:64`; `values.yaml:99` | Derive the Helm timeout from `activeDeadlineSeconds` plus a margin |
| 5 | A namespace with objects from the old `kubectl apply` harness makes the Helm install fail | Substantive | `docs/local-integration-tests.md`, `test/k8s/README.md` | Document the remedy (`make e2e-down` or delete the namespace) and run it on such a namespace |
| 6 | The user merge (profile fill-in, duplicate check) has no test and no input | Substantive | `build/authz-agent-transfer/Dockerfile:333-347` | A fixture user file in a check CI runs, including one that is declared twice |
| 7 | `*` is never registered through `/pip-stub/configure` in a test | Substantive | `test/integration/pipstub/main_test.go:500` | One test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then requests an unrouted path |
| 8 | Missing case: routed path with no responses and no default route → 404 (the old index -1) | Substantive | `main_test.go:503-518` | Add the row |
| 9 | The default-route comments leave out "a route with no responses" | Substantive | `main.go:34-37,122-124` | Name the case |
| 10 | The `e2e-harness` row says the suite Job is installed and waited for | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from the row, or say it is a test hook that `e2e-suite` runs |
| 11 | "CI builds both" is now five images | Substantive | `README.md:58` | Recount, or name the set |
| 12 | Unclaimed hunks: the svt compose Keycloak bump, the `docker-dev-config.json` additions, and the tenant-A/B additions to `parity-realm.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json:13-27`; `parity-realm.json` | A sentence claiming each, or move them to the change that uses them |
| 13 | The realm data cites a test that does not exist, `TestTenantScopedDecisions` | Substantive | `test/k8s/parity/idp-seed/parity-realm.json` (`ROLE_MT_READER`) | Remove the name, or land it together with the test |
| 14 | No red run or mutation verdict stated for any commit | Substantive | commit messages | State the base-commit failure of the routed-empty case, and a run under enforced PSS |
| 15 | The image list for `TAG` leaves out the runtime suite image | Substantive | `helm-templates/authz-test-stand/values.yaml:9-11` | Add `authz-runtime-suite`, or say "the suite image" |
| 16 | `--for=create` needs kubectl 1.31+, and the prerequisites table names no version | Taste | `docs/local-integration-tests.md:37` | Name the minimum kubectl version |
| 17 | A comment narrates history ("as it did before the default route existed") | Taste | `main.go:39-40` | State the current behavior only |

Not checked:
- I did not run either kind harness, the release workflow, a Docker build of the transfer image, or anything on OpenShift.
- The `kubectl logs` timing in findings 2 and 3 comes from kubectl's help text and its documented behavior, not from a run.
- The drift script does not parse Go, YAML or Makefiles.
- I did not do a pass over the prose for style alone.
