# Final review of `58316ca..HEAD`: three commits (test-stand chart, pip-stub default route, restricted Pod Security)

There was no separate task statement, so the claimed cases come from the three commit messages and the test comments. The drift script ran and printed nothing, because it only parses `.java/.kt/.kts/.groovy/.scala` files. I did item 1 by hand for the Go files, the chart and the docs.

The Go side is solid. The weak points are things nothing runs: no test or harness namespace enforces the restricted policy, a README command whose result depends on the Helm version, and a kind cluster left over from before this change. Nine findings are substantive; none of them is a broken run on a fresh kind cluster.

What I ran:
- `go test ./pipstub/` passes.
- `helm lint` and `helm template` pass on both harness values files, with the generated `files/` put into a scratchpad copy of the chart. `kubeconform -strict` accepts 10 and 12 resources.
- A script checked every rendered Pod against the restricted fields: non-root, `RuntimeDefault` seccomp, no privilege escalation, `drop: [ALL]`, and only allowed volume types. Every stand Pod passes, and so do the agent and policy-admin charts with their kind values.
- The cached local images run under `docker run --read-only --cap-drop ALL --security-opt no-new-privileges`, as uid 10001 and as uid 1000660000:0. I mounted the image's declared `VOLUME`s read-only, as Kubernetes would leave them. All of them start.
- The transfer image builds, and README steps 1 and 2 render with the published image names.
- `profile.jq` does what its comment says on a synthetic user file, and the duplicate check exits 1.

## Item 1: comments consistent with the code and with each other
- **`main.go` package comment, `defaultRoute`, `callRecord.RequestURI`, test comments:** all match the code. The precedence order (rules, then path routes, then `*`, then 404) is what `handlePIP` does.
- **`docs/local-integration-tests.md:104`:** says `e2e-harness` installs "…and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so the install does not create it. `test/k8s/README.md:31-32` says "installing the stand does not start it", and the README row at line 53 leaves the Job out. The two docs contradict each other, and the first one is wrong.
- **`docs/local-integration-tests.md:127` and the `Makefile:116` comment:** both say the Keycloak Pod is replaced only "after a change to a realm file". In fact any change to the Keycloak Pod template replaces it, and commit 17b17fc is one such change (security context and labels). A developer who re-runs `e2e-harness` over a stand from 8b85515 gets new realm keys, sees no restart warning in the docs, and the suite fails at `setup.wait_for_agent`.
- **`values.yaml`, `_helpers.tpl`, chart README:** consistent with the templates.

## Item 2: claimed cases covered
| Claimed case | Covered by |
| --- | --- |
| An unrouted path is answered by `*` | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A route with no responses falls through to `*`, or to 404 | `/a routed path with no responses…`, `/an unrouted path with an empty default route is 404` |
| With no `*`, an unrouted path is 404 as before | `/an unrouted path without a default route is 404` |
| `*` serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| A rule wins over `*` (new sentence in the package comment) | **none.** `TestHandlePIP_RuleThenLegacyFallback` sets no `*` |
| `/pip-stub/configure` accepts the path `*` | **none.** The tests write `routes` directly, not through `handleConfigure` |
| Every part is off by default | not a repo test; checked by hand (`helm template` renders nothing) |
| A changed realm file restarts Keycloak (checksum) | **none** |
| Make targets: `test-stand-files`, `e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | CI jobs in `integration-tests.yaml` (lines 77, 145, 151, 191, 197) |
| User files get the profile fields; a duplicate fails the build | **none.** No user files exist, so the merge never runs; I checked it by hand |
| The stand starts under enforced restricted Pod Security | **none.** No kind namespace has `pod-security.kubernetes.io/enforce=restricted`. The kind run only exercises what the kubelet enforces anyway (non-root, read-only root) |
| An OpenShift-assigned uid works | **none.** Not run; pip-stub starts as uid 1000660000 in my docker check |
| `app.kubernetes.io/*` and `helm.sh/chart` on every object | not a repo test; checked by rendering |

Documented commands that no CI job runs:
- **`helm test authz-test-stand --timeout 15m --logs` (chart `README.md:64`):** promises the suite's log. `--logs` asks for the log of a Pod named after the hook, but the hook here is a Job (`parity-suite`). Helm v3.15.2's `GetPodLogs` (`pkg/action/release_testing.go:127`) calls `Pods().GetLogs(h.Name)` and fails with `unable to get pod logs for parity-suite`, so `helm test` exits non-zero even when the suite passes. The Helm v4.3.0 binary contains `job-name=` and `failed to stream pod logs for pod: %s, container: %s`, which suggests Helm 4 finds Job Pods by label. **Not verified** by a run. The README does not say which Helm version it needs.
- **The subset recipe, `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`):** depends on `--reuse-values` keeping the Makefile's `--set suite.env.BASE_URL`, and on `helm test` running the hook as last upgraded. Not run.
- **The README `docker create`/`docker cp` step:** I ran it, and it works.

## Item 3: boundaries, partitions, and the negative control
- **pip-stub:** covers no route, a route with no responses, a route with responses, no `*`, and an empty `*`. The 404 case with no `*` is the control. Clamping is covered across paths. Complete except the rule-versus-`*` partition in item 2.
- **State left on an existing cluster:** `e2e-cluster` reuses an existing kind cluster. A namespace set up by the base commit's `kubectl apply` still holds `Deployment keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`, the `keycloak-realms` ConfigMap, the `authz-agent-client-credentials` Secret and `ServiceAccount runtime-suite`. The parity namespace holds its own set. Helm refuses to adopt objects it doesn't own ("invalid ownership metadata", known behavior, not run here), so `make e2e-harness` and `make parity-harness` fail on such a cluster. Every run in the change starts from a fresh cluster, and no doc names the fix (`make e2e-down`, or deleting the two namespaces).
- **Upgrading the chart from 8b85515 to 17b17fc:** the selectors are unchanged (`app` only), so the upgrade is safe. The Keycloak restart it causes is the doc issue in item 1.

## Item 3a: level, placement, and the environment
- **Go tests:** small, in-process, next to the existing `handlePIP` tests, using `resetState`. Good.
- **Chart:** the security contexts and labels can be seen with `helm template` alone, with no cluster. `test/scripts/test-chart-render.sh` (CI "Render assertions") has no test-stand case. The only coverage is the kind run, which does not check admission.

## Item 4: names by content, not by position
None. Subtest names, test names and comments all name cases by what they contain ("a routed path with no responses…").

## Item 5: the failure report
None. Every `t.Errorf` prints the actual and expected values, and the table subtests carry descriptive names, not indexes.

## Item 6: what the writer says it verified
No red run on the base commit, mutation verdict or run log is stated in any commit. The new tests use `defaultRoute` and `RequestURI`, so they would not compile on the base commit; that shows nothing about the behavior.

## Item 7: siblings of the change
- **Template helpers:** `authz-test-stand.labels`, `podSecurityContext` and `containerSecurityContext` reach every object and every Pod in all five templates (checked in the render).
- **Rule engine:** `matchRule` already guards an empty `RespondSequence` (`main.go:275`), so the empty-sequence defect does not repeat there.
- **Readers of `callRecord`:** `pip_control.go` decodes it as JSON, and the added field is harmless.
- **Image entrypoints:** pip-stub and both suite images keep the base image's `/usr/bin/entrypoint.sh`. Under a read-only root it now logs `Failed to open temporary file /etc/ssl/certs/bundleXXXXXX` and `ERROR Error updating CA certificates store` on every start (seen in my docker check). With a random uid it also logs `WARN Can't create appuser entry`. The siblings avoid this by making the binary the `ENTRYPOINT`: `build/authz-agent/Dockerfile:23-26` says so in a comment, and the tenant-manager Dockerfile does the same.
- **References to the deleted manifests:** none left (`git grep`).

## Findings
| Finding | Label | Location | Change requested |
| --- | --- | --- | --- |
| The restricted-policy claim has no test and no harness check | Substantive | `17b17fc`; `Makefile` `e2e-harness`/`parity-harness`; `test/scripts/test-chart-render.sh` | Label both kind namespaces `pod-security.kubernetes.io/enforce=restricted` (the agent and policy-admin charts already comply), and/or add render assertions for the security contexts |
| `helm test … --logs` is in no job; on Helm 3 it fails for a Job hook | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run that exact form on Helm 4 and state the Helm version the README needs, or switch to the Makefile's `kubectl logs job/<name>` form |
| A kind cluster set up by the base commit makes `e2e-harness`/`parity-harness` fail on Helm ownership | Substantive | `Makefile` `e2e-harness`, `parity-harness`; `docs/local-integration-tests.md` | Document the fix (`make e2e-down` or delete the namespaces), shown run on such a cluster |
| The docs say a Keycloak restart happens only after a realm change; any template change (this commit) restarts it, and the agent then needs a restart | Substantive | `docs/local-integration-tests.md:127`, `Makefile:116` | Say "after a change to a realm file or to the Keycloak template" |
| The `e2e-harness` row says it installs "the suite Job; waits until they are Ready" | Substantive | `docs/local-integration-tests.md:104` | Match `test/k8s/README.md`: the Job is a test hook that the install does not create |
| The rule-before-`*` precedence is claimed but untested | Substantive | `test/integration/pipstub/main.go:28-30`; `main_test.go` | Add a row with a matching rule and `*` both set, expecting the rule's answer |
| The user-file merge, profile fill and duplicate check never run in the repo | Substantive | `build/authz-agent-transfer/Dockerfile:35-46` | A CI step that runs `chart-files` with a fixture user file, and one with a duplicate expecting failure |
| The subset recipe is in no job | Substantive | `docs/local-integration-tests.md` (subset bullet) | Run it once on kind and record the result, or have the Makefile take `RUNTIME_SUITE_RUN` |
| No red run or mutation evidence stated | Substantive | commits `9d25da7`, `17b17fc` | State the base-commit red run, for example by temporarily stubbing `defaultRoute` |
| The read-only root makes every pip-stub and suite Pod log `ERROR Error updating CA certificates store` | Taste | `test/integration/pipstub/Dockerfile`, `test/parity/suite/Dockerfile`, `test/integration/testify/Dockerfile` | Make the binary the `ENTRYPOINT` as the agent and tenant-manager images do, or note the expected line in the chart README |
| `/pip-stub/configure` with `*` is tested only by writing to the map | Taste | `main_test.go` | One case that goes through `handleConfigure` |

Not checked: nothing was installed on a real cluster or on OpenShift, Helm 4's `--logs` behavior was not run, and the Keycloak 26.3.5 image's user was not inspected (the local 26.7 image has the numeric `USER 1000`). I did not do a prose-style pass.
