## Final review: `58316ca..HEAD` (3 commits, Go pipstub, Helm test-stand chart, Makefile, CI)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages, as the skill allows. The drift script printed nothing: it parses only Java, Kotlin, Groovy and Scala, so it says nothing about this Go and Helm change. Loaded: `test-authoring` with its `go/testing.md` and `go/testify.md`, and `english-developer-style`. The Go doc-comment skill (`godoc-authoring`) is not in the skills directory, so Go doc-comment rules were not applied. No previous report exists, so there is no §4 table.

**Ran:** `gofmt -l` (clean), `go vet` and `go test -count=1 ./test/integration/pipstub/` (pass), `helm lint` and `helm template` on a scratch copy with the generated `files/` filled in (both values files lint clean and render 12 and 10 objects). Two probes ran in a scratch copy of the pipstub package. The repository was not changed.

### Item 1: comments consistent with the code and with each other
Findings: F6 (false claim about `*`) and F7 (`helm test` log sentence). Otherwise none: the `callRecord.RequestURI`, `defaultRoute`, and `handlePIP` comments match the code; `values.yaml` keys that comments cite (`suite.env`, `suite.args`) exist; the Keycloak `/opt/keycloak` comment matches the read-only-root exemption; the helper and label comments match the rendered output.

### Item 2: claimed cases covered
Findings: F1, F2, F3, F4. The rest is covered: the default route, the sequence across paths, the request target as sent, and the `app.kubernetes.io` labels on every rendered object (checked in the render).

### Item 3: boundaries, partitions, negative control, pre-existing state
Findings: F5 (pre-existing cluster state). For the suite-run limits: `go test -test.timeout 600s` fires before `activeDeadlineSeconds: 900` and the `helm test --timeout 15m`, so the ordering holds at the defaults. The 900 s and 15 m settings are one quantity set in two places; see T1. The negative control exists (the routed path keeps its answer, and an unrouted path without a default is 404).

### Item 3a: level and placement
None. The pipstub tests are in-process (`httptest`), sit beside the existing `handlePIP` tests, share `resetState`, and `go-build.yaml` runs the package. The chart claims are checkable offline, which is the gap in F3.

### Item 4: names by content
None. Case names and comments carry no ordinals or positions.

### Item 5: failure report
None. Every `Errorf` and `Fatalf` prints its operands in got/want order.

### Item 6: what the writer says it verified
F8. No commit message states a red run on the base commit or a mutation verdict. On the base commit the new test file would not compile (`defaultRoute` and `RequestURI` are undefined), so a red run would show a build failure, not the symptom. The regression that matters here is the zero-response route that used to panic with index -1.

### Item 7: siblings
None beyond the chart claims. No stale references to the deleted `test/k8s/*.yaml` manifests remain. The `pip-stub` call-record consumers in `test/parity/suite/pip_control.go` mirror the struct, and the new `requestUri` field is additive. The parity suite's observed-sidecar write fails under a read-only root, but the image already ships root-owned testdata, so that is not a regression.

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. The table in `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` has no case for a routed path with no responses and no default route. Commit 9d25da7 claims "falls through to the default route, or to 404"; I probed it and it does return 404. | substantive | `test/integration/pipstub/main_test.go:225-258` (cases at 237-241) | Add the case "a routed path with no responses and no default route is 404". It is the case that used to panic. |
| F2. The commit claims `/pip-stub/configure` now takes `*`. No test calls `handleConfigure`; every test writes `routes` directly. | substantive (low) | `test/integration/pipstub/main.go:385`; `main_test.go` | Post `[{"path":"*",...}]` to `handleConfigure`, then serve an unrouted path. |
| F3. Commit 17b17fc claims seccomp `RuntimeDefault`, `runAsNonRoot`, `drop: ALL`, `allowPrivilegeEscalation: false`, a read-only root filesystem on every container except Keycloak, the `/tmp` emptyDir, and the labels. No assertion checks any of it. `test/scripts/test-chart-render.sh` already renders charts offline in CI for `authz-agent`. | substantive | `helm-templates/authz-test-stand/templates/*.yaml`; `test/scripts/test-chart-render.sh`; `.github/workflows/integration-tests.yaml:86` | Add render assertions for the test stand, run after `make test-stand-files` in the same CI job. |
| F4. Subject line 17b17fc says "run the test stand under the restricted Pod Security Standard". Nothing labels a namespace `pod-security.kubernetes.io/enforce`, and `--create-namespace` creates an unlabeled one. No CI run enforces restricted. The body says only that the stand *could* start there. | substantive | `Makefile:85` (`e2e-harness`), `Makefile:149` (`parity-harness`); commit subject | Reword the subject, or enforce `restricted` on the kind namespace. Check the `authz-agent` chart in that namespace first. |
| F5. Objects named `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `keycloak-realms`, and `authz-agent-client-credentials` were created by `kubectl`, not Helm. On a kind cluster left by the earlier Makefile, `make e2e-harness` will likely be refused, since Helm 3 will not take over objects it did not create. I did not run this (no cluster). CI creates a fresh cluster, so no run reaches this state, and no remedy is documented for it. | substantive | `Makefile:85-87`, `Makefile:149-151`; `docs/local-integration-tests.md:193` | Document the remedy (delete the named objects, or `make e2e-down`). Run it on a cluster built by the earlier harness. |
| F6. The header says "No request path is `*`". Probe: `OPTIONS *` arrives with path `*` and gets the default answer (status 299). The sentence "it never shadows a real route" stays true. | substantive (low) | `test/integration/pipstub/main.go:36` | Reword: "Only the asterisk-form request (`OPTIONS *`) has path `*`, and it gets the default answer." |
| F7. "It prints the log only at the end" implies `helm test` prints the Job log. It prints it only with `--logs` (`helm test --help`), and the recipe does not pass that flag. | substantive (low) | `Makefile:96` | Say the log comes from `kubectl logs -f`, and that `helm test` prints none here. |
| F8. No red run on the base commit and no mutation verdict is stated (see Item 6). | substantive | commit messages of 9d25da7 | State the red run for the zero-response case. On the base it panics with index -1. |
| T1. `activeDeadlineSeconds: 900` (chart default) and `helm test --timeout 15m` are one quantity set twice. Ordering is correct at the defaults. | taste | `helm-templates/authz-test-stand/values.yaml:99`; `Makefile` `run-suite` | Derive one from the other, or document the pair. |
| T2. "the startup probe allows five." leaves the unit out. | taste | `helm-templates/authz-test-stand/templates/idp.yaml:65` | "allows five minutes". |
| T3. The `values.yaml` header lists tenant-manager among images on "the release version". The commit says it is not published, and the runtime suite is missing from the list. | taste | `helm-templates/authz-test-stand/values.yaml:9-10` | Name the images that take `TAG`, and say which are not released. |

**Not checked:** the suites and `make e2e`/`parity` (no cluster); `golangci-lint`; the transfer-image build and `make test-stand-files` (need Docker); `test/scripts/test-chart-render.sh` (not changed, not run); the Keycloak and Job images' numeric `USER` (the test-stand images have numeric `USER`s, but I did not check the public Keycloak image); the Go doc-comment rules (no skill provided).
