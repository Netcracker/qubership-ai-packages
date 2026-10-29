# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages and the class comments of the tests. There is no previous report, so §4 has no table. The drift script ran and printed nothing, because it parses only Java, Kotlin, Groovy and Scala. The changed Go, Helm, Makefile, YAML and Markdown were read by hand. I loaded `test-authoring` and `english-developer-style`. The doc-comment skill for Go (`godoc-authoring`) is not in the skills directory and was not loaded, so the Go comment rules were applied from this form alone. The change has code, so §2a does not apply.

**What I ran.** `go test -count=1 ./...` and `gofmt -l` in `test/integration/pipstub` and `testify` (both clean). `helm lint` and `helm template` on a copy of the chart in the scratchpad, with the generated `files/` staged by hand, using both `test-stand-values.yaml` files. I checked the `OPTIONS *` URL parse with a small Go program. I did not run the transfer Dockerfile (no Docker), the kind suites, or `helm test`.

**Checked and holding:**
- Every Pod has `runAsNonRoot` and the seccomp profile. Every container drops `ALL`, sets `allowPrivilegeEscalation: false`, and is read-only except Keycloak. This is a static check of the render, not an admission test.
- The pipstub, tenant-manager, parity-suite and testify Dockerfiles all set `USER 10001:10001`.
- `$(RUNTIME_SUITE_RUN)` in `args` is expanded by the kubelet from the container's own env, so it is not a bug.
- The subset-run override (`suite.env.RUNTIME_SUITE_RUN`, `FULL_RUNTIME_SUITE`) renders into the Job env.
- No stale references to the removed `test/k8s/*.yaml` manifests remain in `HEAD`.

## Item 1: comments consistent with code and with each other

Findings below. The drift script gave no output, so I read every changed comment on the Go members, the chart helpers and templates, the Makefile, and the docs. The comments on the test cases and on the `callRecord` field, and the `LoadConfig` and Dockerfile cross-references (`suite.env`, `suite.args`), hold.

## Item 2: claimed cases covered

| Claim (commit) | Test or check |
| --- | --- |
| Unrouted path gets the default answer (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, "an unrouted path gets the default answer" |
| Routed path keeps its own answer | same test, "a routed path keeps its own answer" |
| Route with no responses falls through to the default route | same test, "a routed path with no responses gets the default answer" |
| Route with no responses falls through to **404** | **none** (finding 1) |
| No default route, or an empty one, gives 404 | same test, two cases |
| Sequence across unrouted paths, clamped to the last | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes the path `*` | **none** (finding 2) |
| Restricted Pod Security Standard (17b17fc) | **none** (finding 3) |
| Make targets and CI jobs for the harnesses (8b85515) | `kind-e2e` and `kind-parity` in `integration-tests.yaml` run them |

Commands in changed files. Each entry gives the form, the matching target, and the result.
- `make e2e-harness`, `make parity-harness`, `make e2e-suite`, `make parity-suite`, `make test-stand-files`: targets exist, and CI runs them.
- `make e2e-images e2e-suite`, `make e2e-images e2e-restart e2e-suite`, `make e2e-install e2e-suite`, `make parity-install parity-suite`, `make e2e-images parity-restart parity-suite`: all targets exist.
- `kubectl … rollout restart deploy/authz-agent` (docs line 132): the same command runs inside `e2e-restart`.
- `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …` (docs lines 139–140): `none`, no target runs it. Rendering with helm v4.3.0 locally shows the override in the Job env. Helm v4.3.1 is what CI uses, and the `--reuse-values` path was not run on a cluster.
- `helm test --logs` (chart README line 64): `none`, because `run-suite` streams the log with `kubectl logs` instead. The flag exists in helm v4.3.0.
- `helm upgrade --install … ./charts/authz-test-stand --set TAG=…` and `docker create` / `docker cp` (chart README lines 42–58): `none`, no target. Not run.
- `kubectl … delete namespace authz-parity` (parity README line 60): `none`, no target. The namespace deletion removes the release. Not run.
- `cd test/integration/pipstub && go test -count=1 ./...`: run by `go-build.yaml` line 63, and I ran it here.

**Item 6: red run or mutation verdict.** None of the three commit messages states a red run on the base commit or a mutation verdict. Finding 1 requests one for the `-1` regression.

## Item 3: boundaries, partitions, negative control

- The default route's partitions are covered except one: a route with no responses and no default.
- The control "a stub with no default route stays 404" exists and holds.
- Pre-existing state: see finding 4.

## Item 3a: level, placement, environment

- The pipstub tests are in-process and small. `go-build.yaml` runs them.
- The new tests sit beside the existing ones in `main_test.go` and reuse `resetState`. No test was skipped.
- The chart's runtime properties (security contexts, the `helm test` hook, the restricted profile) have no test that a reader can point to, other than the `kind` jobs. Those jobs use an unlabelled namespace (finding 3).

## Item 4: names by content

None found in the new test names or the new comments.

## Item 5: failure report

The new assertions print their operands (`t.Errorf` with got and want). None found.

## Item 6: evidence

Neither a red run nor a mutation verdict is stated in the commits. Finding 1 asks for the red run on the base commit for the `-1` regression.

## Item 7: siblings

- The pod security helper is used by all four pod specs. The container helper's flag is set correctly on all five containers.
- The labels helper is used on every object.
- Instance names agree across `pipStub.instances`, `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS`.
- Parity's `WriteFile` call next to the goldens is a sibling write that the read-only root now breaks silently (finding 5).

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The claim "a route with no responses falls through … to 404" has no test. This is the case that used to panic on index `-1`. No red run is stated. | substantive | `test/integration/pipstub/main_test.go:225–259`; `main.go:236–245` | Add a case: a routed path with `[]pipResponse{}` and no default, expecting 404. Show it red on the base commit, or name the red run. |
| 2 | `/pip-stub/configure` taking `*` is never exercised. The tests write `routes[defaultRoute]` directly. | substantive | `main.go:385–400` | Add a test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then GETs an unrouted path. |
| 3 | The restricted Pod Security Standard claim is not enforced by any test or CI step. `e2e-harness` and `parity-harness` create the namespace with no PSS label. | substantive | `Makefile:85–86`, `:149–150`; `.github/workflows/integration-tests.yaml:117–175`; `helm-templates/authz-test-stand/README.md:9` | Label the namespace `pod-security.kubernetes.io/enforce: restricted` in the harness targets, or in CI, and run it. Otherwise say the restricted claim is unverified. |
| 4 | Pre-existing state is not handled. A kind cluster built by the previous Makefile holds objects created by `kubectl apply`: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Job and ServiceAccount `runtime-suite`; and for parity `idp`, `pip-mock`, `entitlements-mock`, `parity-realms`, `pip-mock-config`. Helm should refuse to adopt them, which I did not run. Neither the commit nor the docs mention it, and the troubleshooting table has no row for it. CI uses fresh clusters, so CI does not catch it. | substantive | `docs/local-integration-tests.md:185–193`; commit 8b85515 | Name the remedy (`make e2e-down`, or delete the listed objects) in the docs and in the commit description. Run `e2e-harness` on a cluster that holds the old objects, or name that run as not done. |
| 5 | Under the read-only root, parity's `writeObservedSidecar` silently fails. It writes next to the goldens under the module root, which is `/app/test/parity/suite` in the image, and it discards the error with `_ =`. The parity suite's own failure still fires, so this costs the sidecar only, and no target collects it. | substantive | `test/parity/suite/compare.go:87`, `:139–147`; `helm-templates/authz-test-stand/templates/suite.yaml:56–64` | Mount an emptyDir at the golden root for the observed output, or name the loss as a follow-up in the description. |
| 6 | "No request path is `*`" is false. `OPTIONS *` gives `URL.Path == "*"`, which I confirmed. The default route answers such a request, as it does any unrouted path, so behavior is fine. The sentence is wrong. | substantive | `main.go:34–36` | Replace with: "An `OPTIONS *` request also has the path `*`, so it reaches the default route like any other unrouted path." |
| 7 | "as it did before the default route existed" narrates the change, which Item 1 forbids outside a regression test's comment. | substantive | `main.go:37–38` | "A stub with no default route answers an unrouted request 404." |
| 8 | The package comment's precedence (rules, then legacy routes, then the default route) has no test that a matching rule beats the default route. | substantive | `main.go:29–32` | Add a test: a rule matching an unrouted path, with a default route set, returns the rule's answer. |
| 9 | "the M2M client-credentials Secret the chart expects the platform to provision" is wrong for this stand. The chart creates the Secret here. | substantive | `Makefile:81–84`; `test/k8s/test-stand-values.yaml:37–40` | Say the chart creates the Secret on the kind stand, and that a real stand provisions it. |
| 10 | The import-procedure sentence names two realm files. The e2e stand imports four: `authz-test`, `cloud-common`, and the two tenant realms. | substantive (minor) | `test/k8s/authn/REALM-DESCRIPTION.md:81–82` | Name all four, or write "among others". |
| 11 | "It prints the log only at the end" describes `helm test --logs`, which `run-suite` does not pass. Without the flag, helm prints no log. | substantive (minor) | `Makefile:95–98` | Describe what the recipe does: it streams the log with `kubectl logs -f`. |
| 12 | "the startup probe allows five" is ambiguous. It is 60 × 5 s. | taste | `idp.yaml:64–65` | "allows five minutes". |
| 13 | The image list omits `authz-runtime-suite`, which also takes `TAG`. | taste | `values.yaml:9–11` | Add it to the list. |

**Churn:** none reported.

**Not checked:** the kind suites and `helm test` (no cluster); the Keycloak image's numeric user; the transfer image build and its jq merge (no Docker); the "19 groups" expectation in the docs. A style pass over the prose was not done.
