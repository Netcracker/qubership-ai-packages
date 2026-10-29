# Final review: `58316ca..HEAD` (3 commits)

There was no separate task statement. The claimed cases come from the three commit messages and from the comments on the new tests. No previous report of this form exists. `comment-drift.py` printed nothing because it parses JVM sources only (`EXT = (".java", ".kt", …)`), so I listed the changed Go members by hand. The rest of the change is Helm, Make, a Dockerfile, jq, and Markdown, and I reviewed those through the no-code analogues in final-review §2a.

What I ran: `go test ./...` in `test/integration/pipstub` passes. I copied the chart to the scratchpad and built its `files/` by hand, the way the `chart-files` stage would. On that copy, `helm lint` and `helm template` pass with both values files (Helm 4.3.0), and changing a realm file changes `checksum/realms`. I also ran `profile.jq` and the duplicate check against jq 1.8.2.

Stack line (test-authoring §0): `AGENTS.md` has none. I propose `Tests: Go standard testing engine and assertions; no testify in test/integration/pipstub`.

## Item 1: comments consistent with the code and with each other

Go members changed: the package doc, `callRecord.RequestURI`, `defaultRoute`, and the inline comment in `handlePIP`.

- **`test/integration/pipstub/main.go:19-20`** (left above the changed code): "Responses are served sequentially per path (clamped to the last)." The new paragraph at `:34-36` says the default route serves "in sequence like any other route". A reader of both expects one counter per request path. The code keeps a single counter under `*` for every unrouted path, and `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` asserts `/a, /b, /a → 503, 200, 200`. → substantive.
- **`main.go:37-38`**: "as it did before the default route existed" describes the history of the change. → taste.
- **`test/k8s/parity/idp-seed/parity-realm.json`**: the `ROLE_MT_READER` description cites `TestTenantScopedDecisions`, but no such test exists in the repository (`git grep` finds nothing). A reader who follows the reference finds nothing. → substantive.
- **`docs/local-integration-tests.md`, row `e2e-harness`**: "installs the test-stand chart: … and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test`, so the install neither creates it nor waits for it. `test/k8s/README.md` and the chart's comment describe this correctly. → substantive.
- **`test/k8s/parity/idp-seed/README.md:9-12`**: the sentence about `parity-m2m-tenant-b` follows the description of `parity-mt-b-realm.json`, but that client is defined in `parity-realm.json:160`. Its claim value (`parity-mt-b`) is correct. → taste: say which realm holds it.
- The other cross-file statements are consistent with the files they describe: the Dockerfile header against its `RUN`, the realm README, `test/k8s/README.md`, `values.yaml`, `_helpers.tpl`, the `suite.yaml` hook comment, `helpers.go`, the `testify/Dockerfile` reference, and the `profile.jq` example (`parity-r29-level-m2m` → `R29LevelM2M`, which I checked by running it).

## Item 2: claimed cases covered

| Claimed case (from the commit) | Test or check |
| --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through **to 404** when there is no default route | **none.** `…an_empty_default_route_is_404` empties the default route, not the routed path. This is the base-commit panic (index −1) with no default configured. → substantive |
| A stub nobody configures with `*` answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves in sequence, clamped | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `/pip-stub/configure` takes the path `*` | Not tested through `handleConfigure`. The tests write `routes[defaultRoute]` directly, and `handleConfigure` treats `*` like any other path. → taste |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Every Pod is non-root with RuntimeDefault seccomp; every container drops all capabilities, cannot escalate, and has a read-only root filesystem except Keycloak; the stand starts under the restricted Pod Security Standard | **none.** No render assertion covers it, and no namespace runs with `pod-security.kubernetes.io/enforce=restricted`. `--create-namespace` creates the namespace unlabeled, so CI would stay green with every `securityContext` removed. I checked the rendered output by eye only. → substantive |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app: <name>` | none (rendered output checked by eye) |
| Keycloak restarts when a realm file changes | none in the repository (I checked it by hand) |
| Every part is off by default | none (`helm template t chart` renders nothing, checked by hand) |
| `profile.jq` fills the profile fields; the build fails on a duplicate user | **none.** `testdata/realm/` holds no `*.json`, so neither the merge, `profile`, nor either `jq -e` check ever runs on input. I ran them by hand: the profile is right and a duplicate fails with exit 1. → substantive |
| The tenant-manager emulator and the runtime suite stay unpublished | `.qubership/docker.cfg` and `docker-dev-config.json` agree |

**Commands the change tells someone to run:**

| Command | Where | Runs in |
| --- | --- | --- |
| `make test-stand-files` | Makefile, READMEs | CI job "Chart lint and render" |
| `make e2e-harness` / `e2e-suite` / `parity-harness` / `parity-suite` | docs, READMEs | CI jobs `kind-e2e` and `kind-parity` (Helm v4.3.1) |
| `helm lint helm-templates/authz-test-stand -f …` (both values files) | workflow | CI; I also ran it locally |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` | Dockerfile header | dev image build (`docker-dev-config.json`) |
| `docker create … transfer:<version> true; docker cp; docker rm` | chart README | none. The image is `FROM scratch`. `create` does not run the command and `cp` works on a created container, so the outcome holds. No finding |
| `helm upgrade --install authz-test-stand ./charts/… --set TAG=<version> -f my-values` | chart README | none. It depends on the published images; nothing runs it |
| **`helm test authz-test-stand --timeout 15m --logs`** | chart README | **none.** See below. → substantive |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` | `docs/local-integration-tests.md` | none. `--reuse-values` keeps `suite.env` in Helm 3 and 4, so the outcome holds. No finding |

**The `--logs` command.** The property that decides its outcome is that this chart's test hook is a **Job**, not a Pod. In Helm v3.15.2, `pkg/action/release_testing.go:127` runs `client.CoreV1().Pods(ns).GetLogs(h.Name, …)` for every test hook. That asks for a Pod named `parity-suite`, which does not exist. It returns `unable to get pod logs for parity-suite`, and `helm test` then exits non-zero even when the suite passed. The README states no Helm version, and the transfer image is meant for stands outside this repository. I did not check Helm 4's source. The request: run the documented form on a stand with Helm 3 and Helm 4, or replace it with the Makefile's form (`helm test` without `--logs`, plus `kubectl logs job/<name>`).

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The controls are present: a routed path keeps its own answer, no default gives 404, and an empty default gives 404. The partition "empty routed responses × no default route" is missing (Item 2).
- **Inherited state.** `make e2e-harness` and `make parity-harness` are now `helm upgrade --install` into namespaces where the previous Makefile ran `kubectl apply`. A developer's existing kind cluster still holds those objects:
  - e2e: Deployment `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`.
  - parity: Deployment `idp`, `pip-mock`, `entitlements-mock`; ConfigMap `pip-mock-config`; the Secret.

  The chart renders objects with those same names, and Helm refuses to adopt objects that lack its ownership annotations ("exists and cannot be imported into the current release"). CI always starts from a fresh kind cluster, and neither the docs nor the commit names the fix (`make e2e-down`, or deleting the namespaces). → substantive. The request: a run of `make e2e-harness` over a namespace the base commit's `e2e-harness` set up, or a documented remedy that has been run on that state.
- **Restricted Pod Security Standard.** No run starts from a namespace that enforces it (Item 2).

## Item 3a: level, placement, and the environment

- **pip-stub:** the tests are small, in-process tests that sit beside the existing `TestHandlePIP_*` tests and reuse `resetState`. Good.
- **Chart:** `test/scripts/test-chart-render.sh` is where the repository's render-level checks live; it already asserts the agent chart's `seccompProfile` (`:831`) and `readOnlyRootFilesystem`. The new chart gets no render assertion there. That covers the security context of every Pod, the labels, the checksum changing with realm content, empty output by default, and the `required`/`fail` messages. → substantive. The request: add those assertions to `test-chart-render.sh`. The job runs after `make test-stand-files`, so the files exist.
- **The `profile.jq` stage:** one fixture user file would exercise it at build time, or a separate small check could run `jq` on a fixture. → part of the Item 2 finding.

## Item 4: names by content, not by position

none. I checked the test and subtest names, the helper names (`serve`), the Makefile comments, and the README headings. Every reference names a thing by its content.

## Item 5: the failure report

none. Each `t.Errorf` prints got and want in Go's order with the input (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = …`, `requestUri %q, path %q, want …`). `t.Fatalf` is used only before indexing `calls[0]`, and the subtests are named by condition.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit or a mutation verdict. On the base commit, the "routed path with no responses" case would panic at index −1, but the commit only asserts that. For the chart and Makefile commits, there is no stated run of the restricted PSS, nor of an upgrade over the earlier harness.

## Item 7: siblings of the change

- **`/pip-stub/configure`** has 6 callers outside pipstub (`git grep`). The integration tests' 5 calls pin concrete paths with non-empty responses, so the default route does not change their outcome. **`test/parity/suite/pip_control.go:181` `ResetPinnedRoutes`** resets each pinned path to a fixed `404 {"error":"reset"}`. Once a stub has a `*` route, a reset path stays shadowed with 404 and no longer gets the default answer. Since an empty `responses` now falls through, `Responses: []` is the reset that restores the default. → substantive: fix it, or name it as follow-up for the commit that adds the stub's cases.
- **Call-record readers:** `PipStubCall` in the parity suite does not decode `requestUri` yet. It does not apply until a case reads it.
- **Read-only root filesystem:** `test/parity/suite/compare.go:145` writes `*.observed.json` beside the goldens and ignores the error. In the Job this write now fails silently. It does not apply: the file was never retrievable from a finished Job Pod anyway.
- **Makefile references by name:** `E2E_LOCAL_DEPLOYMENTS`, `PARITY_LOCAL_DEPLOYMENTS`, `e2e-logs`, and `parity-logs` match the Deployment names the chart renders.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Package doc says responses are served "per path"; the default route shares one counter across paths | substantive | `test/integration/pipstub/main.go:19-20, 34-36` | State that the default route keeps one sequence for every path it answers |
| No case for a routed path with no responses and no default route (404, the old panic) | substantive | `test/integration/pipstub/main_test.go:236` | Add that row |
| `ResetPinnedRoutes` pins a 404 that shadows a default route | substantive | `test/parity/suite/pip_control.go:181` | Reset with empty responses, or name it as follow-up |
| `helm test … --logs` with a Job hook fails in Helm 3 (`Pods().GetLogs(<job name>)`) | substantive | `helm-templates/authz-test-stand/README.md` "Run the suite" | Run that form on Helm 3 and 4, or document `helm test` plus `kubectl logs job/…` |
| `helm upgrade --install` over a namespace the old harness `kubectl apply`'d fails on ownership | substantive | `Makefile` `e2e-harness`, `parity-harness`; `docs/local-integration-tests.md` | A run over the old state, or a documented and tried remedy (`make e2e-down` or deleting the namespace) |
| No check that the stand meets the restricted PSS, labels, checksum, or default-off | substantive | `test/scripts/test-chart-render.sh`; Makefile namespace creation | Render assertions for the test-stand chart, and/or label the kind namespaces `enforce=restricted` |
| `profile.jq`, the merge, and the duplicate checks never run on any input | substantive | `build/authz-agent-transfer/Dockerfile:39-46` | A fixture user file, or a check that runs the stage on one, including a duplicate |
| Realm role description cites the nonexistent `TestTenantScopedDecisions` | substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | Name a test that exists, or drop the name |
| Docs say `e2e-harness` installs the suite Job and waits for it | substantive | `docs/local-integration-tests.md`, row `e2e-harness` | Say that `helm test` creates the Job |
| "as it did before the default route existed" describes the change | taste | `main.go:37-38` | State the behavior without the history |
| `/pip-stub/configure` with `*` is not tested through the handler | taste | `main_test.go` | A request through `handleConfigure` |
| `parity-m2m-tenant-b` reads as part of the mt-b realm | taste | `test/k8s/parity/idp-seed/README.md:11-12` | Say it lives in `parity-realm.json` |

I did not run the kind harnesses or check CI results (there is no cluster). I did not read Helm 4's source for `--logs`, did not build the Docker stages (I reproduced them by hand), and did not do a style-only pass over the prose.
