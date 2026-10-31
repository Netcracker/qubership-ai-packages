# Final review of `58316ca..HEAD`

**Inputs.** I used no task statement and took the claimed cases from the four commit messages: `8b85515` (test-stand chart), `9d25da7` (pip-stub default route), `17b17fc` (restricted Pod Security Standard) and `5dcb6be` (suite timeout and run notes). I also read the tests' comments. I loaded `test-authoring` and read `english-developer-style` for wording only.

**Drift script.** It exited 0 and printed no member list, so it does not parse these Go files. I read the Go comment changes by hand: the `main.go` header, `callRecord`, `defaultRoute`, `LoadConfig` and the Testify Dockerfile comment. The `*` comment holds: Go's `ServeMux` answers `OPTIONS *` with 400 before `handlePIP` runs.

**What I ran.**
- `go test` in `test/integration/pipstub` passes.
- `helm lint` passes for both values files on a scratchpad copy of the chart with stand-in `files/`.
- `helm template` gives `emptyDir.sizeLimit` 256Mi and `activeDeadlineSeconds` 900.
- `make -n e2e-suite E2E_SUITE_TIMEOUT=30m` passes `--timeout 30m`.
- I could not run `docker build`, `kubectl` or `helm test`, so the `make test-stand-files` output, the `run-suite` loop and the suite Job are unrun.

## Item 1: comments consistent with the code and with each other

None. I read the `main.go` header, `callRecord.RequestURI`, `defaultRoute`, the `run-suite` comment, the chart helper comments, the Dockerfile and `profile.jq` comments, and the README text on `--timeout`, `kubectl logs` and `make e2e-down`. All are true of the new code. No comment narrates the change.

## Item 2: claimed cases covered

| Claim | Test or check |
| --- | --- |
| Unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, case "an unrouted path gets the default answer" |
| Routed path keeps its own answer | case "a routed path keeps its own answer" |
| No default configured answers 404 | case "an unrouted path without a default route is 404" |
| Route with no responses falls through to the default | case "a routed path with no responses gets the default answer" |
| Route with no responses and no default answers 404 | none (finding 7) |
| Default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `/pip-stub/configure` takes `*` | none through `handleConfigure`; the tests set `routes[defaultRoute]` directly |
| `requestUri` kept as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| pip-mock and entitlements-mock behave as before | the existing tests, unchanged |
| Pods run under the restricted Pod Security Standard | none (finding 3) |
| Labels, selectors, `helm.sh/chart` | `helm lint` only; no assertion |
| `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait | no test; `make -n` shows the flag |
| A suite given a longer deadline passes after 15 minutes | not true at the shipped args (finding 2) |
| Realm and rule files are generated; the user merge fills the profile | no run here; the CI chart job runs `make test-stand-files` |

Commands the change tells someone to run, and what runs them:

| Command | Runs it |
| --- | --- |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | CI e2e and parity jobs, same flags |
| `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite` (chart README) | none. The make form differs: the stream runs concurrently, `-n` is set, and the timeout is a variable. |
| `helm upgrade ... --reuse-values --set suite.env.RUNTIME_SUITE_RUN=... --set-string suite.env.FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md:140`) | none |
| `make e2e-down` once, then `make e2e`, to clear the "invalid ownership metadata" failure | none. CI always starts from a fresh kind cluster. |
| `kubectl wait --for=create` inside `run-suite` | CI, on its runner's kubectl |

What the `none` rows depend on:
- **Chart README `helm test` line.** The outcome depends on the suite being a Job, not a Pod. The commit states what Helm 4.3.1 and 3.22.1 do with it. No run on this configuration is shown.
- **`--reuse-values` recipe.** The outcome depends on the release's stored values plus the new `--set`. I could not verify its behaviour across the supported Helm versions here. See finding 8.
- **`kubectl wait --for=create`.** The condition arrived in kubectl 1.31, as far as I know. The docs' tool table sets no kubectl minimum. See finding 8.

Hunks beyond the claim: `test/svt/common/compose/docker-compose.yml:3` moves Keycloak from `26.0` to `26.3.5@sha256…`. No commit message claims it, and it changes the SVT stack. See finding 4.

## Item 3: boundaries, partitions, and the negative control

- **Control and boundaries (pip-stub).** The control is present: the no-default case stays green on the base commit, and the empty default route is tested. Missing: a routed path with no responses and no default must answer 404. That is the `-1` index case the commit names, in its 404 arm. See finding 7.
- **Pre-existing state.** The commit and the docs name the remedy for a cluster from an older `make e2e`. No test or run starts from that state. CI is always fresh. The `keycloak-realms` ConfigMap and the Services collide by name, so the failure is real. A run is owed, or the remedy shown on such a cluster.
- **Pass-through values.** `E2E_HELM_ARGS` now reaches the test-stand chart too. That chart reads `TAG` and `IMAGE_PULL_POLICY`, as the agent and policy-admin charts do. The documented example, `--set IMAGE_PULL_POLICY=Never`, is harmless there. `--set TAG=<x>` aimed at the agent now also retags `local/pip-stub`, `local/authz-runtime-suite` and the others to `<x>`. `make e2e-images` builds only `:ci`, so Pods fail to start. Before this change the harness manifests had fixed `:ci` tags. See finding 5.
- **Replaced mechanism: `e2e-suite` and `parity-suite`.** Faults compared:
  - **Image that cannot be pulled** (the usual kind fault):
    - Old: `wait --for=condition=Ready pod` timed out in 3 minutes with a kubectl timeout message.
    - New: the Job has `backoffLimit: 0` and `activeDeadlineSeconds: 900`. A Pod stuck in `ErrImagePull` never fails the Job.
    - New timeline: the 90-iteration log poll takes up to 3 minutes and prints nothing. `logs -f` then fails once. `wait $helm_pid` blocks until `helm test --timeout 15m` expires, so the failure comes at about 15 minutes.
    - No sentence in the change accepts this. See finding 1.
  - **Hook never created:** `wait --for=create` bounds it at 2 minutes, then the helm status is returned. That is acceptable.
- **Limits on the same work.**
  - **Go test timeout.** `-test.timeout 600s` is fixed in `values.yaml:96` and `test-stand-values.yaml:56`. It is inside the Job. The chart's `suite.activeDeadlineSeconds` defaults to 900s. `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` default to 15m, and the README's `--timeout 15m` matches. `helm test --timeout` and the Job deadline both enclose the suite.
  - **Raising the documented settings.** Raising only the deadline and the make variable past 600s has no effect, because the Go timeout kills the suite at 10 minutes first. This is the commit's headline claim. See finding 2.
  - **Defaults.** At the defaults the inner limit (600s) fires first, which is correct.

## Item 3a: level, placement, and the environment

The pip-stub behaviour is tested in-process, beside the existing tests and sharing `resetState`. The chart has no test of its own: `test/scripts/test-chart-render.sh` never mentions the test-stand chart, and CI only runs `helm lint` on it. That is why the restricted-Pod-Security-Standard claim has no coverage (finding 3). No skip policy applies.

## Item 4: names by content, not by position

None. The test and case names are by content, and the headings and cross-references are too.

## Item 5: the failure report

None. The assertions are equality-style `t.Errorf` calls that print the operands. Subtest ids are sentences. `serve` returns the status and body together, so one message prints both.

## Item 6: what the writer says it verified

No commit message or report states a red run on the base commit or a mutation verdict for the new pip-stub tests, the chart, or the Makefile. The pip-stub tests are plausible red-on-base, but that is not stated.

## Item 7: siblings of the change

- **`callRecord` readers.** I searched for `DisallowUnknownFields` and for readers of `/pip-stub/calls`. The Testify and parity callers decode leniently. The new `requestUri` field breaks none of them.
- **The set `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`.** `test/k8s/README.md:66-71` lists the other overrides (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) and omits the two new ones. See finding 6.
- **Removed manifests.** A search for the deleted manifest names finds no stale reference outside `docs/handovers`.
- **Counts.** Prose that still says "two images" or "both charts" is already updated.
- **Hook policy and logs.** Of the sibling readers, only the chart README and the Makefile deal with the log of a kept test Job; both are handled.

## Added instructions

Not applicable: this change has no skill or instruction file.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| 1. `run-suite` fails at about 15 minutes on an unpullable image, where `e2e-suite` and `parity-suite` failed at 3 minutes. It prints nothing in between. Request: bound the whole wait (poll, `logs -f` and helm) near the old time to fail, or run that fault and state the duration and output. | Substantive | `Makefile:105-112` | 3 |
| 2. The shipped `-test.timeout 600s` caps the suite, so raising only `suite.activeDeadlineSeconds` and `E2E_SUITE_TIMEOUT` does nothing past 10 minutes. This contradicts the `5dcb6be` claim, and the Makefile comment tells only to raise the deadline. Request: derive the `-test.timeout` argument from `activeDeadlineSeconds` (for example minus a margin), or name `-test.timeout` in the Makefile comment and the README. | Substantive | `helm-templates/authz-test-stand/values.yaml:96`, `test/k8s/test-stand-values.yaml:56`, `Makefile:48-51` | 3 |
| 3. The restricted-Pod-Security-Standard claim has no test or run. No namespace is labelled `pod-security.kubernetes.io/enforce=restricted`, and no render assertion covers the contexts or labels. Request: label the harness namespaces in CI, or add render assertions to `test-chart-render.sh` for the test-stand chart. | Substantive | `17b17fc`, `test/scripts/test-chart-render.sh` | 2, 3a |
| 4. The SVT compose Keycloak moves from 26.0 to 26.3.5 with no sentence claiming it. Request: claim it in a message with a run of that stack, or move it to its own change. | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| 5. `E2E_HELM_ARGS` with `--set TAG=<x>` now retags the stand's local images, which nothing builds. Request: give the stand its own tag key, or document that `TAG` must stay `ci`. | Substantive | `Makefile:46-48`, `helm-templates/authz-test-stand/values.yaml:12` | 3 |
| 6. `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are missing from the override list. | Substantive | `test/k8s/README.md:66-71` | 7 |
| 7. No test covers a routed path with no responses and no default route, which must answer 404. No test calls `handleConfigure` with `*`. Request: one more case in the table, and one `handleConfigure` test that posts `*` and then serves an unrouted path. | Substantive | `test/integration/pipstub/main_test.go:226-250` | 2, 3 |
| 8. The `--reuse-values` subset recipe and `kubectl wait --for=create` (kubectl ≥ 1.31, if I recall correctly) run nowhere and carry no stated version. Request: run the recipe on the supported Helm versions, or state the minimum kubectl in the docs' tool table. | Substantive | `docs/local-integration-tests.md:140`, `Makefile:108` | 2 |

Checks the form asked for that I could not do:
- I did not run the Docker build or any cluster step.
- The drift script produced no output on Go files.
- I did not run the CI jobs.
