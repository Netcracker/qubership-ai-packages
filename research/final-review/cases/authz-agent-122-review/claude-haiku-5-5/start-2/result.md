Final review of `58316ca..HEAD` (three commits, 48 files, mostly Go, Helm, Make and Docker). Nothing was changed or committed, and the repo is clean.

**Basis.** No task statement was handed over, so the claimed cases come from the three commit messages (17b17fc, 9d25da7, 8b85515). There was no previous report. Loaded and cited: `test-authoring` (§§1, 5–7) and `english-developer-style` (§§4–5). The doc-comment skill for Go (`godoc-authoring`) is not among the three skills I was given, so I did not load it and checked Go comments against the English skill and the test skill only.

**Drift script.** Run; it printed nothing. It parses only `.java .kt .kts .groovy .scala`, and this change is Go, Helm, Make and Dockerfiles, so it did not run on the changed code. I did the comment check by hand.

**Checks run.** `go test`, `go vet` and `gofmt` on `test/integration/pipstub` and `testify`: all pass. `helm lint` on the chart with defaults passes. In a scratch copy (`git archive HEAD`, with the generated `files/` copied the same way as the chart-files stage), `helm lint` passes with both kind values files, and `helm template` renders. The realm checksum changes when a realm file's content changes. `make -n` for `e2e-suite`, `parity-suite` and `parity-harness` expands correctly. The `profile` jq function gives the documented names. Not run: a Docker build, `make test-stand-files`, a cluster, Keycloak, and kubectl.

### Item 1: comments consistent with the code and with each other
Substantive (see table): `main.go:36` says "No request path is *", which is false. A request `OPTIONS *` has `URL.Path == "*"`, checked with a small Go program. The conclusion (the default route shadows no real route) still holds, because no configured route is named `*` except the default itself.
Taste: `main.go:32` says "behaviour is exactly as before" for the no-config case. A configured route with no responses used to panic (index -1) and now falls through to 404 or the default. The sentence is true of rules only, so the reader can take it either way.
Other comments checked and true: the `callRecord.RequestURI` comment, the `defaultRoute` comment, the `handlePIP` fall-through, the `LoadConfig` and Dockerfile pointers to `suite.env` and `suite.args`, the values comments, the chart README, the docs, and the Makefile `run-suite` comment. The Keycloak "imported at every start" claims are covered in the substantive table.

### Item 2: claimed cases covered
- 9d25da7 "a route with no responses falls through to the default route, or to 404": the default-route half is tested (`main_test.go:225`). The 404 half is not. No table row has a routed path with empty responses and no default route. The code (`main.go` ~232–240) returns 404 there, so the claim holds but nothing checks it.
- 9d25da7 "a call record keeps the request target ... in requestUri": `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the Go field only, not the JSON key `requestUri` (`main.go:77`). Nothing in the repo reads the key.
- 17b17fc "run the test stand under the restricted Pod Security Standard" and the README claim that the stand starts in such a namespace: no test covers this. No namespace is labelled `pod-security.kubernetes.io/enforce` (`--create-namespace` only, Makefile:86 and :150), and `test/scripts/test-chart-render.sh` is unchanged. A regression would not be caught by any CI job.
- Other claims (default route served in sequence and clamped, reset of `counters` and `routes`, the default-off instances, the realm restart, the suite Job as a `helm test` hook, the tenant map, the M2M Secret, the transfer image, the release list in `docker.cfg`) were checked against the code and rendered output. They hold.

### Item 3: boundaries, partitions, negative control, limits, pre-existing state
- Pip-stub negative control: present (a stub with no default route answers 404, and a routed path keeps its own answer). Partitions: unrouted, routed, routed-but-empty, default present or absent, empty default. The missing 404 row is listed under Item 2.
- Limits: suite `-test.timeout 600s` (inner) fires before `activeDeadlineSeconds: 900`, and `helm test --timeout 15m` equals the deadline. Keycloak `startupProbe` (300s) fits the `--wait --timeout 10m`. The emptyDir `sizeLimit` is taken from the ephemeral-storage limit. None is a finding.
- Pre-existing state, substantive: `make e2e-cluster` reuses an existing kind cluster, and the previous harness created `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, the `keycloak-realms` ConfigMap, the `authz-agent-client-credentials` Secret and the `runtime-suite` ServiceAccount with `kubectl apply`. Helm will not adopt objects it did not create. `make e2e-harness` on that cluster would therefore fail. The change has no run from that state and no documented remedy. (Not run here; no cluster.)
- Keycloak restart, substantive: the base e2e Keycloak set `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` (base `test/k8s/keycloak.yaml:38`). The chart drops it. The H2 database lives on the container filesystem, which survives an in-place container restart, and the default import skips existing realms. So "imported at every start" (`values.yaml:16`, `test/k8s/README.md:16`, commit 8b85515) holds only for a fresh container. Not verified by running Keycloak.

### Item 3a: level and placement
The new pip-stub tests are in-process (`httptest`), appended to `main_test.go` beside the existing ones, and `go-build.yaml:63` runs that package in CI. Chart behaviour is covered only by `helm lint` in CI and by the kind jobs. The restricted-PSS claim has no check (see Item 2). Helpers: the new `serve` helper is used by three tests and is not a copy of an existing one.

### Item 4: names by content
Taste: `test/k8s/test-stand-values.yaml:21` says "A second instance for the entitlements endpoint." The instance has a content name right beside it (`entitlements-mock`), so the ordinal can go. Other ordinals found in the diff are about fields (first name, last name) or are paired with a name, so they are not findings.

### Item 5: failure report
None. The Go assertions print both operands (`t.Errorf("GET %s = %d %s, want %d %s", ...)`, `reflect.DeepEqual` with the values printed). The `if ... != ... { t.Errorf }` form is the assertion itself, as §6 allows.

### Item 6: what the writer says it verified
None of the three commit messages states a red run on the base commit or a mutation verdict. Stated: no evidence. 9d25da7 fixes a panic (index -1), so the empty-responses test should be red on the base, but that is not recorded. I did not run the suite to supply it.

### Item 7: siblings
`routes`, `counters` and `ruleCounter` are the only indexed stores. `handleReset` clears `counters`, which includes the `*` key, and `resetState` clears `routes`, so the default route does not leak between tests. The rule sequence path already guards `len(RespondSequence) > 0`, so it does not repeat the -1 defect. `run-suite` serves both harnesses. The e2e-logs and parity-logs targets still name existing deployments. No sibling defect found.

### Report

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| Restricted-PSS claim has no check: no namespace enforce label and no render assertion | substantive | `Makefile:86`, `:150`; `helm-templates/authz-test-stand/README.md:9`; `test/scripts/test-chart-render.sh` (unchanged) | Label the namespaces in both harness targets with `pod-security.kubernetes.io/enforce=restricted`, or assert the rendered security contexts in `test-chart-render.sh` |
| Install over objects the previous harness created: Helm will not adopt them, and the kind cluster is reused | substantive | `Makefile:81–87` (`e2e-cluster`, `e2e-harness`); base `test/k8s/keycloak.yaml` and `runtime-suite-rbac.yaml` | Document the remedy (`make e2e-down`, or delete the old objects) in `docs/local-integration-tests.md` and the commit, or run the install from that state |
| Keycloak OVERWRITE_EXISTING dropped; "imported at every start" holds only for a fresh container | substantive | `helm-templates/authz-test-stand/values.yaml:16`; `test/k8s/README.md:16`; base `test/k8s/keycloak.yaml:38` | Restore the migration strategy for the e2e stand through a value, or reword the claim to "at every start of a fresh container" |
| Missing test: routed path with empty responses and no default route is 404 | substantive | `test/integration/pipstub/main_test.go:225–258` (table); code `main.go` ~232–240 | Add the row `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, ...}` |
| `requestUri` JSON key not asserted | substantive | `main.go:77`; `main_test.go:276–288` | Marshal the record in the test and assert the `requestUri` key, or drop the name from the claim |
| "No request path is *" is false (`OPTIONS *` gives Path `*`) | substantive | `main.go:36` | Replace with "No configured route is named *, so the default route answers a request for `*` like any unrouted path" |
| "behaviour is exactly as before" no longer holds for a configured route with no responses | taste | `main.go:32` | Scope the sentence to rules, or name the empty-responses fix |
| "A second instance" uses an ordinal | taste | `test/k8s/test-stand-values.yaml:21` | "The entitlements instance" (expected to be declined) |

**Not checked:** the Docker build of the transfer image and the `make test-stand-files` stage; the kind suites and Keycloak behaviour (the restart and the adoption conflicts are reasoned from Helm and Keycloak behaviour, not run); PSS admission; the Go doc-comment rules (`godoc-authoring` not loaded); and the drift script does not parse Go, Helm or Make.
