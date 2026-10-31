**Final review of `58316ca..HEAD`** (commits `8b85515`, `9d25da7`, `17b17fc`)

- **Task statement:** none was handed over, so the claimed cases come from the three commit messages and the code comments.
- **Languages:** Go, Helm templates, Makefile, Dockerfile and Markdown. I loaded `test-authoring` from the given skills directory. I did not open `english-developer-style`, because no finding below rests on wording alone. No `godoc-authoring` skill was supplied.
- **Drift script:** `comment-drift.py 58316ca… HEAD` exited 0 with empty output. `handlePIP`'s body changed, so the script's parse missed it. I read the changed Go comments by hand instead: the package comment and the comments on `defaultRoute`, `callRecord.RequestURI` and `LoadConfig`.
- **What I ran:** `helm lint` and `helm template` of `authz-test-stand` with both harness values files, against realm and stub files copied by hand into a scratch copy of the chart. Both lint cleanly and render a Job with the `/tmp` emptyDir. I also ran `profile.jq`: `parity-r29-level-m2m` gives `R29LevelM2M`, and the usernames and ids in `parity-realm.json` are unique. The `make test-stand-files` step itself was not run, because it needs Docker. There is no cluster, so the restricted Pod Security Standard and `helm test` behavior are unrun.

## Item 1: comments consistent with the code and with each other

- **Go comments:** none. The package comment's precedence sentence, "legacy routes, then the default route; else 404", matches `handlePIP`. The `defaultRoute` comment is true.
- **Stale troubleshooting row:** `docs/local-integration-tests.md:190` still says `make e2e-harness` "times out at `rollout status deploy/keycloak`". The harness is now `helm upgrade --install --wait --timeout 10m`, so no `rollout status` exists. A reader looking for that text will not find it.
  - **Request:** reword the row to the timeout helm prints.
  - The row's cause, Keycloak still being pulled, may still hold.
- **Narration:** `test/k8s/README.md` says "the chart creates for it". No other comment narrates the change.

## Item 2: claimed cases covered

| Claimed case | Test |
| --- | --- |
| Default route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| No default route means 404 as before (pip-mock and entitlements-mock unchanged) | `…/an_unrouted_path_without_a_default_route_is_404` |
| Default route in sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through "or to 404" | **no test** |
| `/pip-stub/configure` takes `*` | **no test** |
| Restricted Pod Security Standard (non-root, seccomp, caps dropped, read-only root filesystem except Keycloak, `/tmp` emptyDir, no `runAsUser`) | **none**; only `helm lint` and the kind runs, and neither namespace enforces `restricted` |
| Labels on every object, selectors keep `app: <name>` | `helm lint` only |
| Realm change restarts Keycloak (`checksum/realms`) | none |
| Chart parts off by default, `fail` messages | none |
| Transfer image carries the three charts with `files/` | none (built only on release) |
| Parity realm gains the `parity-mt-b` tenant realm | no test of its own; the claim is only exercised if a parity case uses it |

**Commands the change tells someone to run:**

| Command | Where | Script or CI that runs it |
| --- | --- | --- |
| `make test-stand-files`, `e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | Makefile, docs | CI jobs in `integration-tests.yaml` |
| `helm lint helm-templates/authz-test-stand -f …` | CI | the CI lint step |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false`, then `make e2e-suite` | `docs/local-integration-tests.md:139` | **none** |
| `docker create/cp` of the transfer image, `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`, `helm test … --timeout 15m --logs` | chart README | **none** |

- **Unrun commands:** both `none` forms depend on a release that `--reuse-values` merges into, and on a published image. The chart README's flow needs the unpublished tenant-manager image, so it works only for stands that don't enable it. Neither has been run. For the second command, `--reuse-values` merges the previous release's values, and with Helm 3 and 4 that is not guaranteed to leave `suite.args` and `$(RUNTIME_SUITE_RUN)` expansion as intended. Treat that as unverified rather than wrong.
  - **Request:** run the subset recipe once on kind and keep the result with the change.
- **Unclaimed hunk:** `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256…`. No commit sentence claims it, and it changes the SVT stack's behavior, not just the test stand's.
  - **Request:** add a sentence that claims it, with the SVT run that checks it, or move it to its own change.

## Item 3: boundaries, partitions, and the negative control

- **Missing partitions, pipstub:** the `"or to 404"` clause has no test.
  - The original defect was a route with no responses indexing `-1`.
  - The cases cover an empty route with a default route, and an empty default route with a non-empty route.
  - They do not cover an empty route with no default route.
  - **Request:** add that case, with `routed: []`, no default route and 404.
  - The `"*"` path is never sent through `handleConfigure`.
  - **Request:** one PUT of `[{"path":"*",…}]` followed by an unrouted GET.
- **Pre-existing state:** `e2e-cluster` reuses an existing kind cluster. A developer who already ran the old `make e2e-harness` has `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager` Deployments and Services, plus a `keycloak-realms` ConfigMap, applied by `kubectl` with no Helm ownership metadata.
  - The new `helm upgrade --install` into that namespace refuses with an invalid-ownership error, which I did not run.
  - `docs/local-integration-tests.md` and `test/k8s/README.md` have no remedy for it. The nearest row, "Cluster left behind", says only `make e2e-down`.
  - **Request:** run `make e2e-harness` over a namespace left by `8b85515^`, or add a troubleshooting row that names deleting the namespace, and run it.
- **Fault timing, replaced mechanism:** the old suite target waited for the Pod to be Ready (`wait … --timeout=3m`), so a missing image failed after about 3 minutes.
  - The commonest fault is `ErrImageNeverPull`, which the troubleshooting table lists.
  - The new `run-suite` creates the Job and polls `logs` for 180 s with output discarded. It then runs `logs -f`, which fails once. Then `wait $helm_pid` blocks until `helm test` ends, which is the 15-minute `--timeout` or the Job's `activeDeadlineSeconds: 900`. The Pod never starts, so neither ends sooner.
  - **Result:** failure moves from about 3 minutes to about 15, and the screen is quiet for most of it.
  - **Request:** bound the wait, for example by checking Pod status in the loop and failing with the Pod's waiting reason, then run that fault and record its duration and output.
- **Limits on the same work:**

  | Limit | Where set |
  | --- | --- |
  | `-test.timeout 600s` | `values.yaml` `suite.args` (documented setting) |
  | `activeDeadlineSeconds: 900` | `values.yaml` (documented setting) |
  | `helm test --timeout 15m` | Makefile, fixed, equals the deadline |
  | `wait --for=create … --timeout=2m` | Makefile, fixed |

  - Raising `suite.activeDeadlineSeconds` above 900 has no effect, because `helm test` gives up at 900 s and reports a timeout while the Job runs on.
  - Raising `-test.timeout` above 900 s is cut by the deadline.
  - The inner `-test.timeout` fires first at the defaults.
  - **Request:** derive the helm timeout from the deadline, or add a margin and a note in `values.yaml`.
  - `kubectl wait --for=create` needs kubectl 1.31 or newer, and the docs list no version.
- **Shared values:** `TAG` and `IMAGE_PULL_POLICY` are read by this chart and by the agent and policy-admin charts, and `E2E_HELM_ARGS` reaches all three. Both mean the same thing in each chart, so `--set IMAGE_PULL_POLICY=Never` is harmless here. `none`.
- **Levels:** none further. The `pipstub` tests are in-process and share `resetState`.

## Item 3a: level, placement, and the environment

- **Pipstub tests:** they sit in the existing `main_test.go` and use its `resetState`. The new `serve` helper has no existing sibling to reuse.
- **Chart-render gap:** `test/scripts/test-chart-render.sh` renders the agent and policy-admin charts with assertions, and `helm lint` does not assert anything.
  - No assertion pins the Pod Security claims, the app labels or the `checksum/realms` annotation. The observable behavior is fully in-process: `helm template` needs no cluster.
  - **Request:** add render assertions for the chart: `runAsNonRoot`, seccomp and dropped capabilities on every workload, `readOnlyRootFilesystem` false only on Keycloak, `app` selectors, and the checksum changing when a realm file changes.
- **Restricted namespace never used:** neither harness namespace enforces `restricted`, so a regression would pass CI. The request is to label the harness namespaces `pod-security.kubernetes.io/enforce=restricted`, or accept the render assertions as the check.
- **Env:** `make test-stand-files` runs in CI before lint, so the chart's `fail` is not hit there. `none`.

## Item 4: names by content, not by position

`none`. I checked the Go case names, headings and cross-references. The new test cases are named by content.

## Item 5: the failure report

`none`. The Go assertions use `t.Errorf` with both operands, and the case ids are text. The `serve` helper returns a status and body that the tests compare and print together.

## Item 6: what the writer says it verified

None of the three commit messages states a red run or a mutation verdict for the new `pipstub` tests. The writer should state it: the tests against `9d25da7^`, with the `requestUri` and default-route tests failing for the right reason.

## Item 7: siblings of the change

- **`defaultRoute` and `callRecord`:** `git grep` finds no other reader of the record's JSON in the repository. `requestUri` is additive.
- **Stale references:** the removed manifests are not referenced anywhere. A search for `keycloak.yaml`, `runtime-suite-job`, `pip-mock.yaml`, `m2m-credentials` and similar names found no live reference. The keycloak troubleshooting row (Item 1) is the one leftover.
- **Release lists:** the Makefile `.PHONY` list, `docker-dev-config.json`, `.qubership/docker.cfg`, `docker-release.yaml` and the README all mention the three new images. The README's "both images" wording was fixed. I searched for the old count in prose and found no other.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Troubleshooting row names `rollout status deploy/keycloak`, which the harness no longer runs | Substantive | `docs/local-integration-tests.md:190` | 1 |
| Keycloak bump in the SVT compose stack is unclaimed | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Documented `--reuse-values` subset recipe never run | Substantive | `docs/local-integration-tests.md:139` | 2 |
| Empty-route-with-no-default 404 and PUT of `*` through `handleConfigure` untested | Substantive | `test/integration/pipstub/main_test.go:223` | 3 |
| No test or remedy for a namespace left by the loose manifests | Substantive | `Makefile` `e2e-harness`, docs | 3 |
| Missing image fails after ~15 min instead of ~3, mostly silent | Substantive | `Makefile` `run-suite` | 3 |
| `helm test --timeout 15m` fixed, so raising `activeDeadlineSeconds` has no effect | Substantive | `Makefile` `run-suite`, `values.yaml:99` | 3 |
| No render assertion or restricted-namespace run for the Pod Security claim, labels or checksum | Substantive | `test/scripts/test-chart-render.sh`, `values.yaml` | 3a |
| No red-run or mutation evidence stated for the `pipstub` tests | Substantive | commit `9d25da7` | 6 |

The drift script's empty output is a check I could not do. Commands that need Docker or a cluster (`make test-stand-files`, `helm test`, the troubleshooting recipes) are unrun.
