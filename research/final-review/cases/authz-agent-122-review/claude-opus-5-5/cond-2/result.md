# Final review: `58316ca..HEAD` (three commits)

There was no task statement, so the claimed cases for item 2 come only from the three commit messages, the test comments, and the docs the change edits. The drift script ran over the range and printed nothing, so I found the changed comments by hand. That covers `pipstub/main.go`, `testify/helpers.go`, the testify `Dockerfile`, the Makefile, the chart, and the docs.

What I ran, without changing the repository:
- `go test` in `test/integration/pipstub`: ok.
- `helm lint` and `helm template` (Helm v4.3.0) on a copy of the chart in the scratchpad, with hand-made `files/` and both values files: clean.
- The `chart-files` jq pipeline, run locally (jq 1.8.2) on a sample user file and on a duplicate user.
- I read `GetPodLogs` in the Helm v3.15.2 module cache.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104`**, the `e2e-harness` row. It says the install covers "…the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so `upgrade --install` never creates it and `--wait` never waits on it. `test/k8s/README.md:53` and `:72` say the opposite: "installing the stand does not start it". A reader would expect the suite to run during the harness step. **Request:** drop "and the suite Job" from that row.
- **`test/integration/pipstub/main.go:38-39`**, the package doc. "…answers an unrouted request 404, as it did before the default route existed" tells the history of the change in a package comment. **Request:** end the sentence at "404". (Taste.)
- **`values.yaml:9-11`**. "the images this repository builds, pip-stub, authz-parity-suite, and tenant-manager" leaves out `authz-runtime-suite`, which the e2e values run under the same `TAG`. (Taste.)

Every other changed comment I read agrees with its code: the `callRecord.RequestURI` comment, the step-2 comment in `handlePIP`, the `LoadConfig` comment, the `_helpers.tpl` blocks, and the Makefile `run-suite` and `test-stand-files` comments.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| A path with no route of its own gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/"an unrouted path gets the default answer"` |
| A routed path keeps its own answer (control) | the same test, `"a routed path keeps its own answer"` |
| A route with no responses falls through to the default, or to 404 (the old index −1) | `"a routed path with no responses gets the default answer"`, `"…with an empty default route is 404"` |
| With no `*` route, an unrouted path is 404 as before | `"an unrouted path without a default route is 404"` |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| **`/pip-stub/configure` accepts the path `*`** | **none.** Every test writes `routes[defaultRoute]` directly; none goes through `handleConfigure`. |
| Profile fields filled in for users under `testdata/realm/`; the build fails on a duplicate user or id | **none in the repository.** The directory holds only `README.md`, so CI never runs the merge or `profile.jq`. I ran it locally: `parity-r29-level-m2m` → `R29LevelM2M`, and a duplicate `parity-reader` makes `jq -e` exit 1. The writer states no such run. |
| The stand starts in a namespace that enforces the restricted Pod Security Standard (commit 17b17fc, chart README) | **none.** Both harnesses use `--create-namespace` with no `pod-security.kubernetes.io/enforce` label (`Makefile:86`, `:150`). No render assertion checks the security contexts either. |
| Lint of the chart after `make test-stand-files` | `integration-tests.yaml:65-75` |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | jobs `kind-e2e` and `kind-parity` |

Commands the change tells someone to run:

| Command | Outcome it promises | What runs the same form |
| --- | --- | --- |
| `docker create … authz-agent-transfer:<version> true` / `docker cp` (`authz-test-stand/README.md:42-44`) | the charts are copied out | none. `docker create` does not check that `true` exists in a `FROM scratch` image, so the outcome holds. |
| `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml` (README `:58`) | the stand is installed | none. It renders with `helm template`. |
| **`helm test authz-test-stand --timeout 15m --logs`** (README `:64`) | runs the suite and prints its log | **none.** In Helm v3 (v3.15.2 `pkg/action/release_testing.go`, `GetPodLogs`), `--logs` asks for a Pod named after the hook, `parity-suite`. A Job's Pod is `parity-suite-xxxxx`, so the call errors with `unable to get pod logs for parity-suite`, and `helm test` exits non-zero even when the suite passes. The v4.3.0 binary contains `job-name=` and `POD LOGS: %s (%s)`, so v4 probably handles Jobs. No page names a minimum Helm version. |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` (`docs/local-integration-tests.md:136-141`) | the suite runs a subset | none. The values reach the hook Job's env. It needs `files/` to exist, which an earlier `make e2e-harness` leaves behind. |

Hunks no commit message claims:
- **`test/svt/common/compose/docker-compose.yml:3`** moves the SVT stack's Keycloak from `26.0` to `26.3.5@sha256:…`. No sentence in commit 8b85515 mentions the SVT compose stack, and nothing in the change runs it. **Request:** add a sentence that claims it, with the SVT run that checks it, or move it to its own change.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The partitions are covered: routed, unrouted, empty routed sequence, empty default, no default, and the sequence clamp. The control (the routed path keeps its own answer) is there. none.
- **Pre-existing state: substantive.** A developer's kind cluster from before this change has, in `authz-e2e`, the kubectl-applied `deploy/keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, the matching Services, `secret/authz-agent-client-credentials`, and `serviceaccount/runtime-suite`. `authz-parity` has the same set. `helm upgrade --install authz-test-stand` refuses objects that exist without Helm's ownership metadata, so `make e2e-harness` fails on such a cluster. Every CI run starts from a fresh cluster, and no page gives the remedy. **Request:** one line in `test/k8s/README.md` and in the docs page ("on a cluster from before the chart, run `make e2e-down` or delete the namespace first"), checked on such a cluster. Or make the targets delete the old objects.
- **Values users already pass: substantive.** `E2E_HELM_ARGS` now reaches the test-stand install too (`Makefile:86`, `:150`). The keys both the agent and test-stand charts read are `TAG` and `IMAGE_PULL_POLICY`.
  - `--set IMAGE_PULL_POLICY=…` is harmless: the local images are already loaded into the node.
  - `--set TAG=<x>` has a real effect. It is the way to override `TAG: ci` from `test/k8s/values.yaml` for the agent. It would now also point the stand at `local/pip-stub:<x>`, `local/tenant-manager:<x>`, and `local/authz-runtime-suite:<x>`, which `e2e-images` does not build. With `IfNotPresent` or `Never` the Pods cannot start, and `--wait` runs to its 10-minute timeout.
  - **Request:** give the stand its own variable (for example `TEST_STAND_HELM_ARGS`), or a run with `--set TAG=…`.
- **Replaced mechanism (`e2e-suite`, `parity-suite`): substantive.** Fault: the suite Pod cannot start (`ErrImageNeverPull` or `ImagePullBackOff`).
  - **Old:** `kubectl wait --for=condition=Ready pod … --timeout=3m` failed after 3 minutes with `timed out waiting for the condition`.
  - **New:** `wait --for=create` succeeds at once. The log loop runs for at least 180 s, then `logs -f` prints that the container is waiting to start. Then `wait $helm_pid` blocks until `helm test --timeout 15m`, or the Job's `activeDeadlineSeconds: 900`, fires. The target fails after about 15 minutes instead of 3, and no sentence accepts that.
  - **Request:** a run of this fault with its duration and output, plus a deadline on the whole wait. For example, wait for the Pod to be Ready with `--timeout=3m` and kill `helm test` when that wait fails.
- **Limits: substantive.**
  - On the suite's work: the Go `-test.timeout 600s` (in `suite.args`), the Job's `activeDeadlineSeconds` (the documented `suite.activeDeadlineSeconds`, default 900), `helm test --timeout 15m` (hard-coded at `Makefile:196` and README `:64`), and the CI job's `timeout-minutes: 30`.
  - `helm test`'s clock starts before the Job exists. Raise `suite.activeDeadlineSeconds` to 1200 and `make e2e-suite` still fails at 15 minutes, so the raised value has no effect.
  - **Request:** derive the `helm test` timeout from the value, for example a Makefile variable that also sets `--set suite.activeDeadlineSeconds`, or say in `values.yaml` that it is capped by the 15-minute `helm test` timeout.
  - The Keycloak startup probe (5 minutes) fires inside the 10-minute `--wait`, so it fires first at the defaults; fine.

## Item 3a: level, placement, and the environment

none. The pip-stub behavior is tested in process through `handlePIP`, in `main_test.go`, next to the existing `TestHandlePIP_*` tests and sharing `resetState`. The chart behavior exists only on a cluster, and the kind jobs install it. The gap is the restricted-PSS enforcement, filed under item 2.

## Item 4: names by content, not by position

none. The case names (`"a routed path with no responses gets the default answer"`, and the rest) and the doc cross-references name things by content.

## Item 5: the failure report

none. Each check prints its operands: `GET %s = %d %s, want %d %s`; `statuses of /a, /b, /a = %v, want %v`; `requestUri %q, path %q, want %q and %q`. The cases are named, not indexed.

## Item 6: what the writer says it verified

Nothing is stated. None of the three commit messages gives a red run on the base commit, a mutation verdict, or a kind run under an enforcing namespace.

## Item 7: siblings of the change

none.
- `run-suite` serves both suites.
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` still name the Deployments the chart creates.
- `e2e-logs` and `parity-logs` address `deploy/pip-stub` and `deploy/pip-mock`, which still exist.
- The three new images appear in both `.qubership/docker.cfg` and `.github/docker-dev-config.json`, and in `README.md` and the `docker-release.yaml` header.
- A search for the old counts ("two images", "both images", "both chart installs") and for the removed manifest names finds no stale sentence outside the excluded `docs/handovers` and a generic skill example.
- `handleConfigure` stores any path, and `handleReset` leaves routes alone, so `*` behaves like every other route.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The `e2e-harness` row says the harness installs and waits for the suite Job, which is a test hook | Substantive | `docs/local-integration-tests.md:104` | 1 |
| Package doc narrates the change ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:38` | 1 |
| `TAG` comment leaves out the runtime-suite image | Taste | `helm-templates/authz-test-stand/values.yaml:9` | 1 |
| `/pip-stub/configure` with path `*` has no test | Substantive | `test/integration/pipstub/main_test.go:500` | 2 |
| The user merge and `profile.jq` are never exercised: `testdata/realm/` has no user file | Substantive | `build/authz-agent-transfer/Dockerfile:340` | 2 |
| The restricted-PSS claim is not exercised: no namespace enforces it, no render check | Substantive | `Makefile:86` | 2 |
| `helm test --logs` reads a Pod named after the Job in Helm v3; not run anywhere, no Helm version stated | Substantive | `helm-templates/authz-test-stand/README.md:64` | 2 |
| Unclaimed SVT Keycloak bump from 26.0 to 26.3.5 | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Harness install fails on a cluster with the old kubectl-applied objects; no remedy documented | Substantive | `Makefile:86` | 3 |
| `E2E_HELM_ARGS='--set TAG=…'` now retags the stand's local images, which nothing builds | Substantive | `Makefile:126` | 3 |
| Suite target now fails after about 15 minutes instead of 3 when the suite Pod cannot start | Substantive | `Makefile:194` | 3 |
| Raising `suite.activeDeadlineSeconds` past 900 has no effect under the fixed `helm test --timeout 15m` | Substantive | `helm-templates/authz-test-stand/values.yaml:99` | 3 |

Two checks could not be done as the form describes. The drift script printed nothing for this range, so item 1 relied on reading the diff. There is no cluster, so the chart was only linted and rendered with Helm v4.3.0, and the `helm test --logs` behavior in v4 was judged from strings in the binary.
