# Final review: `58316ca..HEAD` (three commits: test-stand chart, pip-stub default route, restricted PSS)

**Inputs.** There was no task statement, so the claimed cases come only from the three commit messages and the comments above the tests. The drift script (`comment-drift.py 58316ca HEAD`) printed nothing and exited 0. Its parse missed the Go members whose comments moved (`callRecord`, `defaultRoute`, `handlePIP`, the package comment), so I read those by hand.

What I ran:
- `go test ./...` in `test/integration/pipstub`: passes.
- `helm lint` and `helm template` (Helm 4.3.0) on a scratch copy of the chart, with `files/` filled in by hand: both values files and the defaults render.
- `build/authz-agent-transfer/profile.jq` with jq 1.8.2.

`AGENTS.md` has no line naming the test stack (test-authoring §0). Proposed line: `Tests: Go testing as engine and assertions; testify in test/integration/testify.`

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-36` and `:122-123`.** The package comment says the default route "answers every request whose path has no route of its own". The `defaultRoute` comment says the same. The new code also sends requests to the default route when the path's route has no responses (`!ok || len(route.Responses) == 0`, `:236`). The commit message names that case; neither comment lists it. A reader would expect a path configured with `responses: []` to get 404.
- The other changed comments still match the code: `callRecord.RequestURI`, the `// 2. Legacy path routes …` step, the Makefile `run-suite` comment ("up to three minutes" = 90 × 2 s), the `_helpers.tpl` blocks, `idp.yaml`, `suite.yaml`, `values.yaml`, `testify/Dockerfile`, `helpers.go:LoadConfig`, `docker-release.yaml`.
- No comment narrates the change. The phrase "as it did before the default route existed" (`main.go:37-38`) states a compatibility promise, not a history.

## Item 2: claimed cases covered

| Claimed case | Test or run |
| --- | --- |
| Configuring `*` through `/pip-stub/configure` registers the default route | **none.** Every test writes `routes[defaultRoute]` directly; `handleConfigure` is never called. |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| Nobody configures `*` → 404, as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses and no default route answers 404 (this was the index −1 panic on the base) | **none.** The empty-default case leaves `/routed` with responses. |
| The default route serves its responses in sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The call record keeps the request target as it arrived, in `requestUri` | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the Go field. The JSON key `requestUri` that consumers read from `/pip-stub/calls` is not asserted. |
| Every Pod runs non-root with seccomp RuntimeDefault; every container drops ALL and cannot escalate; read-only root filesystem except Keycloak; `/tmp` emptyDir on the suite | Rendering only (I checked the rendered output by hand). No assertion, and no run in a namespace that enforces `restricted` (`git grep pod-security` finds nothing). |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app: <name>` | Rendering only; no assertion. |
| Chart failure texts: `no realm files under files/realms/<realms>/`, `no file files/pip-stub/<file>`, `tenantManager.tenants is required`, `TAG is required` | **none** |
| `profile.jq` fills in the profile fields (`parity-r29-level-m2m` → `R29LevelM2M`); the build fails on a duplicate user | **none** in the repository. `testdata/realm/` holds no JSON, so the merge never runs. I ran `profile` by hand and it gives the documented output; the duplicate check was not exercised. |
| The harnesses run on the chart | CI `kind-e2e` and `kind-parity` jobs, on a fresh cluster |

Command lines the change documents, and what runs them:

| Command | What runs it |
| --- | --- |
| `make test-stand-files` | CI chart job, and as a prerequisite of the harness targets |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | CI kind jobs (Helm v4.3.1, kubectl from kind-action) |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` | Release workflow only. No workflow reads `.github/docker-dev-config.json`. |
| README transfer flow: `docker create/cp/rm`, `helm upgrade --install … --set TAG=<version>`, `helm test … --timeout 15m --logs` | **none** |
| `docs/local-integration-tests.md` subset recipe: `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …` then `make e2e-suite` | **none** |

What each `none` depends on:
- **Transfer flow.** The outcome depends on images published under exactly the tag that `--set TAG=<version>` supplies, and on the parity values with the four keys deleted. Nothing checks either. `--logs` does exist in Helm 4.3.0.
- **Subset recipe.** The outcome depends on `--reuse-values` keeping `suite.args` and on the `$(RUNTIME_SUITE_RUN)` expansion. I see no flaw, but nothing runs it.
- **kubectl version.** `run-suite` calls `kubectl wait --for=create`, which needs kubectl 1.31 or later. The prerequisites table names no minimum. With an older kubectl the `&&` skips the poll loop, `logs -f` fails while the container is still being created, and the log is not streamed; the exit code from `helm test` survives.

Hunks that no commit sentence claims:
- `test/svt/common/compose/docker-compose.yml`: Keycloak 26.0 → 26.3.5, pinned by digest.
- `test/k8s/parity/idp-seed/parity-realm.json`: the commit claims only the new realm `parity-mt-b`. This file also gains the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, the users `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`, the roles `ROLE_MT_READER`/`ROLE_MT_ADMIN`, and five protocol mappers.
- `.github/docker-dev-config.json`: three images added to the dev build list. The commit claims only `.qubership/docker.cfg`.

## Item 3: boundaries, partitions, and the negative control

- **Pre-existing state.** `e2e-cluster` reuses an existing cluster. A namespace left by the base version holds kubectl-applied objects with exactly the names the chart renders: Deployments and Services `keycloak`/`idp`, `pip-stub`/`pip-mock`, `entitlements-mock`, `tenant-manager`, ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`. `helm upgrade --install authz-test-stand` refuses objects that carry no Helm ownership metadata. Every run starts from a fresh kind cluster, and no doc names a remedy. This is a finding.
- **Limits on the suite's run time.**

  | Limit | Where it is set | Value |
  | --- | --- | --- |
  | `-test.timeout` | `suite.args` | 600 s |
  | `activeDeadlineSeconds` | `suite.activeDeadlineSeconds`, a documented value | 900 s |
  | `helm test --timeout` | fixed in the Makefile `run-suite` and in the chart README | 15 m = 900 s |

  The inner limit (600 s) fires first at the defaults, which is correct. But the Job deadline equals the `helm test` timeout. At the defaults the two race, and Helm's "timed out" can hide the Job's `DeadlineExceeded`. Raising `suite.activeDeadlineSeconds` past 900 has no effect, because the Helm timeout is fixed. This is a finding.

  The other pairs are fine:
  - The Keycloak startup probe (5 min) sits inside the harness `--wait --timeout 10m`.
  - The log poll (3 min) sits inside `helm test`.
- **Precedence control missing.** No test shows that a configured rule still beats the default route. `TestHandlePIP_RuleThenLegacyFallback` covers rules against legacy routes only.
- **Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand chart. Its only documented value, `--set IMAGE_PULL_POLICY=Never`, means the same thing there, and Keycloak has its own pull policy. The chart has no schema, so keys meant only for the agent chart are ignored. No finding.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process tests in `main_test.go`, beside the existing `TestHandlePIP_*` tests and sharing `resetState`. Good.
- The chart's behaviour can be observed in-process with `helm template`: the security contexts, the labels, and the `fail`/`required` messages. The repository already has `test/scripts/test-chart-render.sh` for the sibling charts, and it gains no case for this chart. CI only lints the test stand.
- The restricted-PSS behaviour exists only across the cluster boundary, so it is owed a run in a namespace labelled `pod-security.kubernetes.io/enforce=restricted`, and no CI job provides one.

## Item 4: names by content, not by position

None. Subtest names state the condition and the outcome. The counts in the Dockerfile comment ("the two tenant realms", "the three charts") are correct.

## Item 5: the failure report

None. Every assertion prints got and want, and the message names the request (`GET %s = %d %s, want …`, `statuses of /a, /b, /a = …`, `requestUri %q, path %q, want …`).

## Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict are stated. This matters for the empty-responses case, which panicked on the base.

## Item 7: siblings of the change

- **`README.md:59`** says "CI builds both via `.github/docker-dev-config.json`". That file now lists five images, so the count is stale.
- No live file still references the deleted manifests (`git grep` outside `docs/handovers`, `docs/plans`, `docs/decisions`).
- `E2E_HELM_ARGS` is documented consistently in the Makefile and in `test/k8s/README.md`.
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` match the rendered names.
- The readers of `/pip-stub/calls` are unaffected, since `requestUri` is an added field.
- "both charts" in `test-chart-render.sh` refers to the platform charts, which is still correct.

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | A cluster left by the base version blocks `helm upgrade --install authz-test-stand`, because the object names are identical and carry no Helm ownership | Substantive | `Makefile:86`, `:150` | A run starting from a base-version namespace, or a documented remedy (`make e2e-down` / delete the namespace, or `--take-ownership`) run on that state |
| 2 | `suite.activeDeadlineSeconds` (900) equals the fixed `helm test --timeout 15m`: raising the setting has no effect, and at the defaults Helm's timeout can hide the Job deadline | Substantive | `values.yaml:786`, `Makefile:83`, chart `README.md:259` | Derive the Helm timeout from the value (or the reverse), or document the pair |
| 3 | The restricted-PSS claim is exercised nowhere | Substantive | `templates/_helpers.tpl:291-308` | Label the harness namespace `enforce=restricted` in CI, or add render assertions per Pod/container |
| 4 | Configuring `*` through `/pip-stub/configure` is untested | Substantive | `main_test.go:225` | A test that POSTs `[{"path":"*",…}]` to `handleConfigure`, then serves an unrouted path |
| 5 | A route with no responses and no default route (the base panic) is untested | Substantive | `main_test.go:240-244` | Add that case |
| 6 | The package comment and the `defaultRoute` comment omit that a route with no responses also falls through | Substantive | `main.go:34-36`, `:122-123` | Add that case to both sentences |
| 7 | No control shows a rule still beats the default route | Substantive | `main_test.go` | A rule-matching request with `*` configured gets the rule's answer |
| 8 | The `requestUri` JSON key is not asserted | Substantive | `main_test.go:278-284` | Read the record back through `handleCalls` |
| 9 | The chart's `fail`/`required` texts, `profile.jq`, and the duplicate-user check have no test | Substantive | `templates/*.yaml`, `build/authz-agent-transfer/*` | Cases in `test-chart-render.sh`, and a fixture under `testdata/realm/` (or a CI step) that runs the merge and the duplicate check |
| 10 | The README transfer flow and the subset recipe run nowhere; `kubectl wait --for=create` needs kubectl ≥ 1.31, which is undocumented | Substantive | chart `README.md:234-260`, `docs/local-integration-tests.md:82-91`, `Makefile:84` | Run each once and state it, or name the kubectl minimum |
| 11 | Unclaimed hunks: svt Keycloak bump, the parity-realm additions beyond `parity-mt-b`, the `docker-dev-config.json` entries | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `parity-realm.json`, `.github/docker-dev-config.json` | Claim each with a sentence and its check, or move it to its own change |
| 12 | Stale count "CI builds both" | Substantive | `README.md:59` | Restate it for the five entries |
| 13 | No red run or mutation evidence stated | Substantive | n/a | State the red run for the empty-responses case on `58316ca` |

Not checked: there was no cluster, so nothing ran on Kubernetes and the CI kind jobs were not reproduced. `make test-stand-files` and the transfer image were not built; the chart was rendered from files copied by hand. Whether the `qubership-core-base:2.4.2` entrypoint writes to the root filesystem was not verified. The prose was not reviewed for style alone.
