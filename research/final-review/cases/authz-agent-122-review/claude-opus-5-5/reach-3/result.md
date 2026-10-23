# Final review: `58316ca..HEAD` (three commits)

There was no task statement, so the claimed cases come from the three commit messages alone: 8b85515 (test-stand chart), 9d25da7 (pip-stub default route) and 17b17fc (restricted Pod Security Standard). No previous report exists.

I loaded `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. No doc-comment skill for Go was supplied, so Item 1 rests on the form's own questions.

`comment-drift.py` printed nothing. It only parses `.java`, `.kt`, `.kts`, `.groovy` and `.scala` (`EXT`, line 29), so it saw none of this Go, YAML and template change, and I read every changed comment by hand.

What I ran, all outside the repository's tracked files:
- `go test ./...` in `test/integration/pipstub`: passes.
- `helm lint` and `helm template` (Helm v4.3.0) on a copy of the chart in the scratchpad, with `files/` filled by hand to match the `chart-files` stage: both value files lint and render.
- The Dockerfile's jq merge and `profile.jq`, simulated with jq 1.8.2.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38` (package comment) and `:122-123` (`defaultRoute`).** Both say the default route answers "every request whose path has no route of its own". The code at `main.go:235-237` also sends a path to the default route when its route has **no responses** (`len(route.Responses) == 0`). The commit message and the test comment (`main_test.go`, above `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`) both state that second case. A reader of the package doc who configures an empty route to force a 404 would get the default answer instead. **Substantive.**
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`.** "The selectors keep the single label app: <name>, so the Makefile's deploy/<name> … address a part". `deploy/<name>` addresses the Deployment by its object name, not by a label. The reason a selector has to stay put is that it is immutable on upgrade: 17b17fc changed the Pod labels of releases installed from 8b85515. **Taste.**
- Every other changed comment matches its code:
  - `callRecord.RequestURI`, `handlePIP` step 2
  - `helpers.go:77-81`, `testify/Dockerfile:34-36`
  - the Makefile `run-suite`, `test-stand-files` and harness comments
  - the transfer Dockerfile header (the realm lists match what the stage copies)
  - `values.yaml`, `idp.yaml:34,52-54,64-65,77-78`, `suite.yaml:12-13,60-61`
  - `docker-release.yaml:1-12`

  None narrates the change ("now", "no longer").

## Item 2: claimed cases covered

| Claimed case (commit) | Covering test or run |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer | `…/a routed path keeps its own answer` |
| Without `*`: 404 as before | `…/an unrouted path without a default route is 404` |
| Route with no responses falls through to the default route | `…/a routed path with no responses gets the default answer` |
| Route with no responses falls through **to 404** (the index −1 defect) | **none.** No case has an empty route **and** no default route. |
| `/pip-stub/configure` takes `*` | Indirect only: the tests write `routes[defaultRoute]` directly, and `handleConfigure` is unchanged and stores any path. Taste. |
| Call record keeps the target "in requestUri" | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field only. The JSON key `requestUri`, which consumers of `/pip-stub/calls` read, is not asserted. A renamed tag would pass. |
| Restricted Pod Security Standard (non-root, RuntimeDefault, drop ALL, no escalation, read-only root filesystem except Keycloak) | **none.** No render assertion. No kind namespace carries `pod-security.kubernetes.io/enforce=restricted`, and `--create-namespace` adds no label. |
| app.kubernetes.io labels and `helm.sh/chart` | none; seen only in my render |
| Merge of user files and the profile fill-in for Keycloak 26 | **none in the repository.** CI covers only the empty partition ("none so far"). My simulation: 0 user files gives 14 users and `true`; one file adds `parity-new`, and `profile` filled it in correctly; a duplicate `parity-reader` makes `jq -e` exit 1. Not in any test. |
| Release publishes three more images | `.qubership/docker.cfg` and `.github/docker-dev-config.json` entries; not run here |
| Parity realm gains `parity-mt-b` | `test/k8s/parity/idp-seed/parity-mt-b-realm.json`; the CI `kind-parity` job imports it |

### Commands the change documents

| Command | Outcome promised | What runs it |
| --- | --- | --- |
| `make test-stand-files` | files generated | CI `chart` job (`integration-tests.yaml:76-77`) |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | stand up, suite streamed, exit status is the suite's | CI `kind-e2e` and `kind-parity`, on a fresh cluster only |
| `helm lint helm-templates/authz-test-stand -f …` (both value files) | lint passes | CI `chart` job; I ran it too: passes |
| `helm test authz-test-stand --timeout 15m --logs` (chart `README.md:64`) | the suite runs and its log is printed | **none** |
| `docker create/cp/rm`, then `helm upgrade --install … --set TAG=<version>` (chart `README.md:42-58`) | the stand installs from the transfer image | **none** |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (`docs/local-integration-tests.md`) | `make e2e-suite` runs the subset | **none** |
| `docker build -t authz-agent-transfer -f build/authz-agent-transfer/Dockerfile .` | the image builds | the dev build through `docker-dev-config.json`, same Dockerfile and context |

**The `--logs` row is a substantive finding.** The outcome depends on the kind of object the test hook is: here it is a Job, not a Pod.
- **Helm 3.15.2** (`pkg/action/release_testing.go:127`, from the module cache): `GetPodLogs` reads the logs of a **Pod named after the hook**, `GetLogs(h.Name, …)`. Here that is `parity-suite`. The Job's Pod is `parity-suite-xxxxx`, so the lookup fails with "unable to get pod logs for parity-suite", and `helm test` exits non-zero even when the suite passed.
- **Helm 4.3:** I could not read its source offline. It either fails the same way or skips the Job; neither prints the log.

The Makefile avoids `--logs` and streams `kubectl logs` itself. The request is a run of the README form on Helm 3 and 4, or replacing it with the Makefile's `kubectl logs job/<name>` form.

The other two `none` rows are lower risk:
- **`--reuse-values`:** the recipe reuses the release's last values, so `suite.env.BASE_URL`, which `e2e-harness` set, survives.
- **Transfer-image install:** it depends on the published `ghcr.io` images, which nothing here can check.

### Hunks no commit sentence claims (substantive)

- **`test/svt/common/compose/docker-compose.yml:3`:** the SVT Keycloak moves from `26.0` to `26.3.5@sha256:…`.
- **`test/k8s/parity/idp-seed/parity-realm.json`, +318 lines:** clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, their service-account users, and users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The commit message names only the new realm `parity-mt-b`; only the idp-seed README mentions `mt-a`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions** (route present, empty or absent × default present, empty or absent). Covered:
  - present/present
  - absent/present
  - empty/present
  - absent/absent (the control, green on base)
  - absent/empty

  **Missing: empty/absent.** This is the input that indexed the sequence at −1 on base, so the "falls through … or to 404" outcome is unasserted (substantive, already noted under Item 2). The sequence across paths is covered (`…ServesItsSequenceAcrossPaths`). `/pip-stub/reset` clearing `counters["*"]` is not covered (minor).
- **Inherited state (substantive).** An existing kind cluster from before this change has, in `authz-e2e`, kubectl-applied Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`, plus the Secret `authz-agent-client-credentials`, the ServiceAccount `runtime-suite` and the ConfigMap `keycloak-realms`. In `authz-parity` it has `idp`, `pip-mock`, `entitlements-mock` and the same Secret. `helm upgrade --install authz-test-stand` creates objects of the same names, and Helm refuses to adopt objects without its ownership annotations. Every CI run starts from a fresh cluster, and the docs name no remedy such as `make e2e-down`, deleting the namespace, or `kubectl delete -f` of the old manifests. The request is the documented remedy, run on such a cluster.
- **Pass-through values (substantive).** `E2E_HELM_ARGS` now also reaches the test stand. The test-stand chart shares two of the product charts' value keys:
  - `IMAGE_PULL_POLICY`, the documented example: harmless.
  - `TAG`: `--set TAG=x`, meant for `local/authz-agent:x`, makes the stand ask for `local/pip-stub:x`, `local/tenant-manager:x` and `local/authz-*-suite:x`. `e2e-images` builds only `:ci`, and with `IMAGE_PULL_POLICY: Never` the Pods stay in `ErrImageNeverPull` until `--wait --timeout 10m` runs out.
  - A `-f` file meant for the agent chart would also reach the stand.

  The request is a variable of the stand's own, or a sentence that documents the shared keys.
- **Limits on the suite run (substantive).** Three limits bound the same work:

  | Limit | Where it is set | Value |
  | --- | --- | --- |
  | `-test.timeout` | `suite.args`, a documented value | 600 s |
  | Job `activeDeadlineSeconds` | `suite.activeDeadlineSeconds`, a documented value | 900 s |
  | `helm test --timeout` | fixed in the Makefile `run-suite` (line ~103) and chart `README.md:64` | 15 m |

  At the defaults the inner limit fires first, which is fine. The outer two are equal, though. Raising `suite.activeDeadlineSeconds` (or `-test.timeout`) past 900 s has no effect: Helm's fixed 15 m ends the wait first, and its "timed out" hides the Job's `DeadlineExceeded`. The request is to derive the Helm timeout from the value, or to document the pair.

  The other waits only end one operation inside the run, so they are not limits on it:
  - `kubectl wait --for=create --timeout=2m`
  - the 90 × 2 s log poll
  - `--timeout 10m` against the Keycloak startup probe's 5 minutes
- **Chart-input boundaries.** None of these is tested:
  - `tenantManager.tenants` empty → `fail`
  - `pipStub.instances.<x>.port` missing → `required`
  - `files/` missing → `fail`, with the message the chart README quotes

  Taste, since `helm lint` in CI renders only the happy path.

## Item 3a: level, placement, and the environment

- **pip-stub:** the tests are in-process `httptest` tests in `main_test.go`, beside the existing `TestHandlePIP_*` tests and sharing `resetState`. That is the right level and placement, and CI runs them (`go-build.yaml:63`).
- **Restricted PSS (substantive).** It is observable at the render level, and the repository already asserts the same securityContext fields for the agent chart in `test/scripts/test-chart-render.sh:788-843` (seccomp, `readOnlyRootFilesystem`). The stand gets no such assertion. The request is a render assertion in that script, run over both value files: every Pod has `runAsNonRoot` and `RuntimeDefault`, and every container has `drop: [ALL]`, `allowPrivilegeEscalation: false`, and `readOnlyRootFilesystem: true` except `keycloak`. Optionally, the kind namespaces could also be labeled `enforce=restricted`.

## Item 4: names by content, not by position

None. Subtest names describe their condition ("a routed path with no responses gets the default answer"). The `$(1)`, `$(2)`, `$(3)` parameters of `run-suite` are positional by Make syntax, and the comment names each one. No "above", "below" or ordinal references appear in the changed prose.

## Item 5: the failure report

None. Every check prints both sides:
- `GET %s = %d %s, want %d %s`
- `statuses of /a, /b, /a = %v, want %v`
- `requestUri %q, path %q, want %q and %q`

`t.Fatalf` is used only before indexing `calls[0]`, and the table cases carry descriptive names.

## Item 6: what the writer says it verified

Not stated. No commit message gives a red run on the base commit or a mutation verdict. From the code, the empty-route case would panic on base (`idx = -1`), but nobody ran it.

The commits also give no run of the kind harnesses and no `helm test` run. The CI kind jobs would supply those, but the commits don't say they passed.

## Item 7: siblings of the change

- **Sequence indexing in pip-stub.** The rule engine's `respondSequence` already guards against an empty list (`main.go:275`). `ResetPinnedRoutes` in `test/parity/suite/pip_control.go:185` configures 404 responses, never empty ones, so the fall-through does not change it. No other path indexes `Responses`.
- **Stale count (substantive).** `README.md:58` still says "CI builds **both** via `.github/docker-dev-config.json`". That file now lists five images.
- **Wrong description of `e2e-harness` (substantive).** `docs/local-integration-tests.md`, the `e2e-harness` row, says it installs "… and the suite Job; waits until they are Ready". The Job is a `helm test` hook: `upgrade --install` does not create it, and `--wait` does not wait for it. The same row in `test/k8s/README.md` gets this right.
- **Resource names checked.** `E2E_LOCAL_DEPLOYMENTS`, `PARITY_LOCAL_DEPLOYMENTS` and `e2e-logs`/`parity-logs` (`deploy/pip-stub`, `deploy/pip-mock`) match the Deployment names the chart renders. `git grep` finds no stale reference to the deleted manifests outside `docs/handovers` and `docs/plans`.
- **Image lists checked.** `.qubership/docker.cfg` and `docker-dev-config.json` both list the three new images, and the release workflow comment counts them. The SVT compose Keycloak bump is the unclaimed sibling noted under Item 2.

## Findings

| # | Finding | Label | Where | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `helm test --logs` reads a Pod named after the Job hook; it fails on Helm 3.15.2 and is unverified on Helm 4 | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run that form on Helm 3 and 4, or replace it with the Makefile's `kubectl logs job/<name>` form |
| 2 | Restricted-PSS claim has no render assertion and no namespace enforcing it | Substantive | `templates/_helpers.tpl:23-40`; `test/scripts/test-chart-render.sh` | Add stand assertions beside the agent's at lines 788-843, over both value files |
| 3 | No run or remedy for a cluster that still holds the kubectl-applied harness objects | Substantive | `Makefile` `e2e-harness`, `parity-harness`; `test/k8s/README.md` | Document the remedy (`make e2e-down` or namespace delete) and run it on such a cluster |
| 4 | Empty route with no default route → 404 is untested | Substantive | `test/integration/pipstub/main_test.go`, the `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` table | Add the case `a routed path with no responses and no default route is 404` |
| 5 | Package and `defaultRoute` comments omit the empty-route fall-through | Substantive | `test/integration/pipstub/main.go:34-38`, `:122-123` | Name the second case in both comments |
| 6 | `helm test --timeout 15m` is fixed where `suite.activeDeadlineSeconds` (900) cannot reach it; the two limits are equal | Substantive | `Makefile` `run-suite`; `values.yaml:99`; chart `README.md:64` | Derive the Helm timeout from the value, or document the pair |
| 7 | `TAG` passed via `E2E_HELM_ARGS` now reaches the stand and asks for images nothing builds | Substantive | `Makefile:86,150`; `test/k8s/README.md:63` | Give the stand its own args variable, or document the shared keys |
| 8 | The user-file merge and `profile.jq` are exercised only on the empty partition | Substantive | `build/authz-agent-transfer/Dockerfile:39-46`; `profile.jq` | Add a fixture user file, or a jq check run in CI, including the duplicate case |
| 9 | Hunks no commit sentence claims: SVT Keycloak pin; tenant clients and users in `parity-realm.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json` | Claim them in the message with their run, or move them to their own change |
| 10 | `README.md` still says CI builds "both" images | Substantive | `README.md:58` | Update the count |
| 11 | Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop the Job from that row, as `test/k8s/README.md` does |
| 12 | `requestUri` JSON key not asserted | Substantive | `main_test.go`, `TestHandlePIP_RecordsTheRequestTargetAsSent` | Assert through `handleCalls` output, or marshal the record |
| 13 | The given reason for keeping `app:` selectors is not the real one (selectors are immutable) | Taste | `templates/_helpers.tpl:2-4` | State the immutability reason |
| 14 | `*` is never configured through `/pip-stub/configure` in a test | Taste | `main_test.go` | Configure it through `handleConfigure` in one case |
| 15 | Chart `fail`/`required` paths are not rendered by any test | Taste | `templates/idp.yaml:3-5`, `pip-stub.yaml:2-7`, `tenant-manager.yaml:6-8` | Add negative render cases to the render script |

This review did not include a kind or Kubernetes run, `make test-stand-files`, a Docker build, the e2e or parity suites, a style pass over the prose, or any check of Helm 4's `--logs` source. Only the pip-stub Go suite, `helm lint` and `helm template` on a scratch copy, and the jq merge were run.
