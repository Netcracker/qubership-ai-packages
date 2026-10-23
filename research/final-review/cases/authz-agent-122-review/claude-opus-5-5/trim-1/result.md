# Final review of `58316ca..HEAD` (3 commits)

**Inputs.** No task statement was given, so the claimed cases come only from the three commit messages and the test comments. No earlier report exists. The drift script printed nothing and exited 0, because it only parses Java, Kotlin, Groovy and Scala. I checked the Go members by hand (the package comment, `callRecord`, `defaultRoute`, `handlePIP`) and also the chart templates, the Makefile and the docs. Loaded skills: `final-review`, `test-authoring` with `references/go/testing.md`, and `english-developer-style`. There is no Go doc-comment skill in the provided set. `AGENTS.md` has no test-stack line. Proposed line: `Tests: Go testing (engine and assertions) for test/integration/pipstub; testify for test/integration/testify`.

## Item 1: comments consistent with the code and with each other
- **`test/integration/pipstub/main.go:34-36` and `:122-123`.** Both comments say the default route answers "every request whose path has no route of its own". The code (`handlePIP`, `!ok || len(route.Responses) == 0`) and the commit message also send a routed path whose route has no responses to the default route. Both comments leave that case out.
- **`main.go:37`.** "…answers an unrouted request 404, as it did before the default route existed" describes the change's history in a package comment.
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`.** The comment says "The selectors keep the single label app: <name>, so the Makefile's deploy/<name> … address a part by its Service name". `deploy/<name>` addresses the Deployment by its object name, not through its selector, so the reason given is false. The real constraint goes unstated: `spec.selector` of a Deployment cannot be changed, so a `helm upgrade` from the commit-8b85515 release would fail if the selector changed.
- **`Makefile:96`.** "`helm test` … prints the log only at the end". Without `--logs`, which this target does not pass, `helm test` prints no log at all.
- **`test/parity/suite/pip_control.go:29-30`** (an unchanged file that describes pip-stub). "Path matching is strictly literal … No wildcards / regex / templates." This is now contradicted by the catch-all `*` route.
- **`helm-templates/authz-test-stand/README.md:8`.** "Every Pod runs as the non-root user its image names" is not true on OpenShift, where the restricted SCC assigns the uid. The helper comment and the commit message both say so.

## Item 2: claimed cases covered
Claims from commit 9d25da7, each with the test that covers it:

| Claim | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through **to 404** when there is no default route (on the base commit this indexed `Responses[-1]` while holding `mu`) | **none** |
| A stub not configured with `*` answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves a sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The call record keeps the request target in **`requestUri`** | `TestHandlePIP_RecordsTheRequestTargetAsSent` reads the Go field `RequestURI`. The JSON name served by `/pip-stub/calls` is not asserted, so a wrong tag would pass. |

Claims from commit 17b17fc:

| Claim | Test |
| --- | --- |
| The stand starts in a namespace that enforces the restricted Pod Security Standard | **none**. Neither kind job labels its namespace `pod-security.kubernetes.io/enforce=restricted`, and no render assertion checks the security contexts. |
| Every object carries the `app.kubernetes.io/*` and `helm.sh/chart` labels | No test. I confirmed it by rendering both values files: all 12 e2e objects and all 10 parity objects carry them. |
| A read-only root filesystem for every container except Keycloak, plus `/tmp` as an emptyDir | No test. The render matches the claim. |

Claims from commit 8b85515:

| Claim | Test |
| --- | --- |
| Each part is off by default | No test. Rendering with default values gives 0 objects. |
| Keycloak restarts when a realm file changes | No test. A `checksum/realms` annotation is present. |
| The jq stage fills in the profile fields and fails when a user is declared twice | **none**. There are no user files yet, so `profile` and the two `jq -e` checks never run on any input. |

Command lines in the changed files, their claimed outcomes, and what runs them:

| Command | What runs the same form |
| --- | --- |
| `make test-stand-files` | The CI lint job |
| `make e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | The CI kind jobs, on Helm v4.3.1, from a fresh cluster |
| `docker create/cp/rm` of the transfer image | none. `docker create` on a `scratch` image with the command `true` does not run that command, so it succeeds. |
| `helm upgrade --install … ./charts/authz-test-stand --set TAG=<version>` | none, though it is close to the Makefile form |
| `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (docs) | none. The value contains no comma or backslash, so `--set` parses it as one value. |
| **`helm test authz-test-stand --timeout 15m --logs`** (README:64), promising "Run the suite and print its log" | **none**. The Makefile drops `--logs`. |

The `--logs` outcome depends on the hook being a **Job**, not a Pod. Helm 3.15.2, `pkg/action/release_testing.go:127`, calls `Pods().GetLogs(h.Name)` with the hook's name, `parity-suite`. No Pod has that name, so the command returns `unable to get pod logs for parity-suite` and exits non-zero even when the suite passes. Helm 4 has a different format string (`POD LOGS: %s (%s)`), but I could not read its source offline. The README names no supported Helm version.

## Item 3: boundaries, partitions, and the negative control
- **pip-stub.** The partitions are: route with responses, route without responses, no route; and default route present, empty, or absent. All combinations are tested except "route without responses × no default route", which is listed under item 2. The control "a routed path keeps its own answer" is present and holds on the base commit.
- **State an earlier version left behind (commit 8b85515).** A developer cluster where `make e2e-harness` or `parity-harness` ran at the base commit holds kubectl-applied `deploy/keycloak`, `pip-stub`, `idp`, `pip-mock`, the `keycloak-realms` and `pip-mock-config` ConfigMaps, the Secret, and `sa/runtime-suite`. `helm upgrade --install authz-test-stand` will refuse to adopt these objects because of their ownership metadata. The docs give no remedy, such as `make e2e-down` or deleting the namespace. Every CI run starts from a fresh cluster.
- **Upgrade over the commit-8b85515 release (commit 17b17fc).** The new labels and securityContext change Keycloak's Pod template. A plain re-run of `make e2e-harness` therefore replaces the Keycloak Pod, which mints new realm keys. `docs/local-integration-tests.md:127` tells the reader to restart the agent only "after a change to a realm file". With `helm.sh/chart` in the Pod template, every chart version bump of a transfer-image stand does the same.

## Item 3a: level, placement, and the environment
- **Go tests.** They sit in `main_test.go` beside the neighbouring tests, use `resetState`, and use the `t.Run` table form. `go test ./...` and `go vet` pass, and CI runs the package (`go-build.yaml:63`). No finding.
- **Chart.** The security-context claim has no small test. The natural place is a `helm template` assertion in `test/scripts/test-chart-render.sh`, which already covers the other two charts. Actual admission under the Pod Security Standard can only be checked across the cluster boundary, and no kind job enforces it. I could not check whether the `qubership-core-base:2.4.2` entrypoint, used by pip-stub and both suites, writes outside `/tmp` under a read-only root. The policy-admin comment vouches only for `alpine-2.5.8`.

## Item 4: names by content, not by position
None. Test names, case names and doc references all refer to content. The `$(1)`/`$(2)`/`$(3)` parameters of the Make macro are positional by language and are documented. The line references in `pip_control.go` predate this change.

## Item 5: the failure report
None. Every `t.Errorf` prints the input, got and want. Cases are named by condition, `t.Fatalf` is used only before an index into `calls`, and no boolean is wrapped around a comparison.

## Item 6: what the writer says it verified
Nothing is stated: no red run on the base commit for the `Responses[-1]` fix, no mutation verdict, and no kind run under an enforcing namespace or with a read-only root.

## Item 7: siblings of the change
- `handleConfigure`, `handleReset` and `handleCalls` need no change: reset clears the `*` counter along with the others.
- `pip_control.go` `ResetPinnedRoutes` re-pins paths to an explicit 404. A pinned `*` becomes a 404 catch-all, which is the intended result. Its package note is stale, as listed under item 1.
- `PipStubCall` has no `requestUri` field. The commit defers that to "the cases that use it".
- All five templates call the `_helpers.tpl` helpers, and no Pod or object is missing them (checked by render).

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| `helm test … --logs` with a Job hook fails on Helm 3, and Helm 4 behaviour is unverified; no job runs this form | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run that form on each supported Helm version, or replace it with the Makefile form (`helm test` plus `kubectl logs job/<name>`) |
| The restricted Pod Security Standard claim is not covered by any test or run | Substantive | `templates/_helpers.tpl`, `.github/workflows/integration-tests.yaml` | Add a render assertion for pod and container securityContext, and label the kind namespaces `enforce=restricted` |
| No test for a routed path with no responses and no default route returning 404 (the old `-1` index) | Substantive | `test/integration/pipstub/main_test.go:225` | Add a case to the table, and show it red on the base commit |
| The `requestUri` JSON name is untested | Substantive | `main_test.go:276` | Assert the field through `handleCalls` output |
| The default-route comments omit routes with no responses | Substantive | `main.go:34-36`, `:122-123` | Name both cases |
| The selector comment gives a false reason | Substantive | `_helpers.tpl:2-4` | Give the real reason: an existing Deployment's selector cannot be changed on `helm upgrade` |
| "It prints the log only at the end" is false without `--logs` | Substantive | `Makefile:96` | Say that `helm test` prints no log, so the target streams it |
| The pip-stub note says "No wildcards", but `*` now exists | Substantive | `test/parity/suite/pip_control.go:29-30` | Mention the `*` default route |
| A cluster left by the base commit's kubectl-applied harness blocks the Helm install, and no remedy is documented | Substantive | `docs/local-integration-tests.md`, `test/k8s/README.md` | Document `make e2e-down` or namespace deletion, verified on that state |
| A template or version change restarts Keycloak, but the docs say only realm-file changes do | Substantive | `docs/local-integration-tests.md:127` | Widen the sentence, or drop `helm.sh/chart` from the Pod template labels |
| The jq profile fill and the duplicate check never run on any input | Substantive | `build/authz-agent-transfer/Dockerfile:39-46` | Run the stage once on a fixture with a duplicate user |
| History narrated in the package comment ("as it did before…") | Taste | `main.go:37` | State the current behaviour only |
| "Every Pod runs as the non-root user its image names" is false on OpenShift | Taste | `README.md:8` | Add the condition "on Kubernetes" |
| `kubectl wait --for=create` needs kubectl 1.31 or later, and the prerequisites table names no version | Taste | `Makefile:103`, `docs/local-integration-tests.md:37` | Name the minimum version |

Not checked: nothing ran on a cluster (there was none), so admission under the Pod Security Standard, the base-image entrypoint under a read-only root, and Helm 4's `--logs` behaviour are unverified. The kind and parity suites were not run; I ran only the pip-stub unit tests, `go vet`, `helm lint` and `helm template` with placeholder `files/`. The realm JSON files were not reviewed, and no style-only pass was made over the prose.
