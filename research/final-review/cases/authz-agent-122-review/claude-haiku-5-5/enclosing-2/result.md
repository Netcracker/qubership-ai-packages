# Final review: `58316ca..HEAD` (three commits)

**Inputs.** The change is 17b17fc (restricted Pod Security Standard), 9d25da7 (pip-stub default route) and 8b85515 (test-stand chart). No task statement was handed over, so the claimed cases come from those commit messages and the class comments in `main_test.go`. There is no previous report, so there is no re-review table. The drift script parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala`. None of this change is in those languages, so it printed nothing, and Item 1 was done by reading each changed comment against its code.

**Skills.** I read `final-review` in full and loaded `test-authoring` and `english-developer-style` from the provided directory. The Go doc-comment skill (`godoc-authoring`) is not among the three copies, so I did not load it and checked Go comments against `final-review` only.

**Runs.** The repository is unchanged (`git status` is clean). `go vet` and `go test ./...` in `test/integration/pipstub` pass, and `gofmt -l` is clean. `helm lint` passes for both values files. I rendered both on a scratch copy of the chart with `files/` staged in the scratchpad, not in the repo. `make -n` ran on the new targets. I replayed the transfer Dockerfile's jq steps on a sample user, and probed `OPTIONS *` with `httptest`.

## Item 1: comments consistent with the code and with each other

Findings F1, F2, F5, F6, F7. These hold: the precedence sentence (`main.go:29–31`), the `RequestURI` comment, the chart helper comments, and the tenant-manager comments in `values.yaml`, which I checked against the emulator (`name=id` list, `/health`, 404 for an unregistered name). The sentence in `requestargs.responses.yaml:6–7` is still true with the default route.

## Item 2: claimed cases covered

From 9d25da7:
- Default route answers an unrouted path: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, case "an unrouted path gets the default answer".
- Routed path keeps its own answer: same test.
- Route with no responses falls through to the default route: same test, "a routed path with no responses gets the default answer".
- Route with no responses falls through to 404: **none** (F3).
- No `*` configured gives 404: same test, two cases.
- Sequence shared across unrouted paths: `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`.
- Request target recorded as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- `/pip-stub/configure` takes `*`: **none** (F4).

From 17b17fc: the restricted fields have no test. I checked the rendered output for both value sets. Every pod has `runAsNonRoot` and `RuntimeDefault`. Every container has `allowPrivilegeEscalation: false` and drops `ALL`. `readOnlyRootFilesystem` is true except on Keycloak. No `runAsUser` is set. Every image has a numeric `USER`. Keycloak's own user and write paths are not verified (see the last section).

From 8b85515: the parts are off by default, the suite is a `helm test` hook, and the release list in `.qubership/docker.cfg` matches the commit. The tenant-manager and the runtime suite are not published. The merge, profile fill and duplicate failure have no test (F11). The `parity-mt-b` realm has no test (F13).

Commands a reader is told to run:

| Command | Where | Counterpart that runs it | Result |
| --- | --- | --- | --- |
| `make test-stand-files` | Makefile, READMEs | CI step "Generate the test-stand files" | covered |
| `make e2e-harness`, `e2e-install`, `e2e-suite`; `make parity-harness`, `parity-install`, `parity-suite` | Makefile, docs | CI, `integration-tests.yaml:145–151, 191–197` | covered on a fresh kind only (F8) |
| `helm upgrade --install authz-test-stand ./charts/authz-test-stand --set TAG=… -f …` | chart README:57–59 | none (no `--wait`, no `--create-namespace`) | none (F10) |
| `helm test authz-test-stand --timeout 15m --logs` | chart README:64 | Makefile:102 runs it without `--logs` | none (F5, F10) |
| `docker create` / `docker cp` / `docker rm` | chart README:41–45 | none | not run; I expect it to work, since `docker create` does not run the image's command |
| `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` | docs/local-integration-tests.md:139–140 | none (the Makefile uses no `--reuse-values`) | none (F10) |

## Item 3: boundaries, partitions, and the negative control

- Default route: the boundary cases are present (sequence clamped to the last response, empty routed responses, empty default). The controls are present (routed path keeps its answer; no default gives 404). The routed-empty, no-default case is missing (F3).
- Pre-existing state: the stand installs over objects an earlier version left in the same namespaces, and no test or run starts from that state (F8).
- Limits: at defaults, `-test.timeout 600s` fires before the Job's 900 s deadline, and the Keycloak startup probe (300 s) fires before `--wait --timeout 10m`. Raising the documented `activeDeadlineSeconds` or `-test.timeout` above 900 s has no effect, because `helm test --timeout 15m` fires first (F9).
- Transfer merge: no user file exists, so the one-user, duplicate and profile partitions have no evidence (F11).

## Item 3a: level, placement, and the environment

The Go tests run in-process with `httptest`, sit beside the existing tests and share `resetState`. CI runs them (`.github/workflows/go-build.yaml:63`). None skips.

The chart's security fields, labels, selectors, realm checksum and `fail` messages are all observable with `helm template` and no server. No CI job checks them. `test/scripts/test-chart-render.sh` never renders this chart, and CI runs only `helm lint` on it (F12).

## Item 4: names by content, not by position

One taste finding (F14). The new test and case names are content-based, and no other changed text refers to a named thing by ordinal.

## Item 5: the failure report

None. Every new Go assertion prints its operands: `t.Errorf` names the request and prints got and want, and `t.Fatalf` prints the count. No boolean wraps a comparison without a message. The chart's `fail` messages name the file and the remedy.

## Item 6: what the writer says it verified

Neither the commit messages nor the change states a red run or a mutation verdict, so none is stated. A run of the new Go tests on the base commit would not count as evidence, because it would fail on the missing `defaultRoute` and `RequestURI` symbols rather than on the symptom. The request is a red run of the F3 case that shows the index panic on base.

## Item 7: siblings of the change

- `handlePIP` is the only reader of `counters`. The other readers of `routes` (`handleConfigure`, `loadDefaultRoutes`, `resetState`) are unchanged and need no change for `*`. Applies: no.
- `callRecord` consumers: `test/parity/suite/pip_control.go:52–77` decodes its own struct, and no test compares the full record. Applies: no.
- Chart helpers: all four containers and all four pod specs use `containerSecurityContext` and `podSecurityContext`, at `idp.yaml:40, 80`, `pip-stub.yaml:37, 58`, `tenant-manager.yaml:31, 48`, `suite.yaml:37, 57`.
- Makefile: every `helm` call goes through `E2E_HELM` or `PARITY_HELM`.
- Removed manifests: no reference to a removed file remains (`git grep`).
- Unclaimed changes: the svt compose Keycloak pin moved to 26.3.5 with a digest, which matches the chart. The parity realm grew by 318 lines, which the commit describes only as "gains a second tenant realm" (F13). The e2e Keycloak lost `JAVA_OPTS_APPEND` (F7).

## Findings

| # | Label | File and line | Finding and change requested |
| --- | --- | --- | --- |
| F1 | substantive | `test/integration/pipstub/main.go:36` | "No request path is \*" is false. `OPTIONS *` reaches the handler with `URL.Path` = `*` (probed). Say that `*` can arrive as a path and is answered by the default route like any unrouted path. |
| F2 | substantive | `main.go:19–20, 34–37, 232–240, 246–250` | "served sequentially per path" and "in sequence like any other route" hide that the default route has one counter (`counters["*"]`) shared by every unrouted path, which `main_test.go:261` asserts. "no route of its own" also omits that a route with no responses falls through. State both. |
| F3 | substantive | `main_test.go:225–258` | No case for a routed path with no responses and no default route, which is the "or to 404" branch the commit claims. Base code indexes `Responses[-1]` for this shape. Add the case. It is the red case for the -1 fix. |
| F4 | substantive | `main.go:385–403`; new tests | "`/pip-stub/configure` now takes `*`" has no test. Every case writes `routes[defaultRoute]` directly. Add a test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then serves an unrouted path. |
| F5 | substantive | `Makefile:96–97` | "`helm test` … prints the log only at the end": without `--logs` (`Makefile:102`) `helm test` prints no log. The log comes from the `kubectl logs -f` that follows. Say that instead. |
| F6 | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`": the e2e stand imports all four `test/k8s/authn/*-realm.json` files, including the two tenant realms the same document tabulates. List four, or write "the realm files". |
| F7 | substantive | `REALM-DESCRIPTION.md:72`; `helm-templates/authz-test-stand/values.yaml:15–16`; `test/k8s/README.md:16` | "imports them at every start" holds only for a new Pod. The base e2e Keycloak set `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` (base `test/k8s/keycloak.yaml:38–39`). The chart drops it without mention. An in-place container restart keeps the dev-mode H2 database, so an existing realm is no longer re-imported. Restore the option through the chart, or say in the commit and docs that the removal changes this. I did not verify the option's effect on Keycloak 26. |
| F8 | substantive | `Makefile:85` (`e2e-harness`), `:149` (`parity-harness`); `docs/local-integration-tests.md:193` | Pre-existing state. Objects from the earlier kubectl-applied stand remain without Helm ownership labels: Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `idp`, `pip-mock`; ConfigMaps `keycloak-realms`, `pip-mock-config`; Secret `authz-agent-client-credentials`; ServiceAccount and Job `runtime-suite`. The first `helm upgrade --install` over them should fail Helm's ownership check. I could not run that here, and no test starts from this state. Document the remedy (`make e2e-down`, or delete these objects) and run `make e2e-harness` once over an old-state namespace. CI uses a fresh kind, so it does not show this. |
| F9 | substantive | `helm-templates/authz-test-stand/values.yaml:92–99`; `Makefile:102` | Limit. `suite.activeDeadlineSeconds` (900) is a documented setting, but `helm test --timeout 15m` is fixed in the Makefile and fires first when the setting is raised above 900. The same holds for `-test.timeout` above 900 s. Derive the helm timeout from the setting, or document both as fixed at 900 s. |
| F10 | substantive | `helm-templates/authz-test-stand/README.md:57–59, 64`; `docs/local-integration-tests.md:139–140` | Command forms no run covers. The install lacks `--wait`, and step 3 runs the suite straight after, so the suite can start before Keycloak and the agent are ready. Add `--wait --timeout 10m` as the Makefile does. Whether `helm test --logs` prints a Job hook's log is not verified here, since helm's help says "test pods". Run it on a stand, or document the `kubectl logs -f` path the Makefile uses. The `--reuse-values` subset command has no run and no Makefile counterpart. Run it once on a stand. |
| F11 | substantive | `build/authz-agent-transfer/Dockerfile:32–47`; `profile.jq`; `test/parity/suite/testdata/realm/README.md` | The claimed merge, profile fill and duplicate failure have no case. The directory holds only the README, so no test or CI step runs the jq steps with a user. I replayed them on a sample user in the scratchpad: the merge and profile fill gave the expected names and email, and the duplicate check exited 1. Add a fixture and a step that runs the steps on it, outside the real parity realm. |
| F12 | substantive | `test/scripts/test-chart-render.sh` (no reference to this chart); `.github/workflows/integration-tests.yaml:74–85` | The restricted fields, labels, selectors, realm checksum and `fail` messages are observable with `helm template`, but CI runs only `helm lint` on this chart. Add render assertions for each container's `securityContext`, the pod's `runAsNonRoot`, the checksum changing with a realm file, and the two `fail` messages. |
| F13 | substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | The role description says "the two-tenant cases (`TestTenantScopedDecisions` and others)" read these roles. No file in the repository defines that test. `parity-mt-b`, the `mt-*` users, the `ROLE_MT_*` roles and the tenant clients are read by no test. The commit says only "gains a second tenant realm", though the file grew by 318 lines. Either add the case, or say the tenant realms wait for cases in a later change and drop the test name. |
| F14 | taste | `test/k8s/test-stand-values.yaml:21` | "# A second instance for the entitlements endpoint." refers by ordinal. Name it: "# The stub for the entitlements endpoint." The key on the next line already says it. |

## What the review did not check

There is no cluster, so the helm installs, pod-security admission, Keycloak behavior (realm import, the "Account is not fully set up" claim, the effect of `JAVA_OPTS`, the Quarkus build path), Helm's ownership check and `helm test --logs` against a Job hook are all unverified. The `docker build` stages were not run, and I replayed their steps in the scratchpad instead. `golangci-lint` was not run, and the suite itself was not run. The example user `parity-r29-level-m2m` in the Dockerfile comment does not exist in the repository.
