## Final review: `58316ca..HEAD` (three commits)

No task statement was handed over, so the claimed cases come from the three commit messages. The drift script ran but printed nothing: it parses only Java, Kotlin, Groovy and Scala, and this change is Go, Helm, Make, Dockerfile and Markdown. Item 1 was therefore done by reading the diffs and the rendered chart. I loaded `test-authoring` and `english-developer-style` as the skill directs. The Go doc-comment skill was not in the supplied set, so Go comments were checked against the code. Nothing in the repository was changed or committed.

Checks run: `go vet` and `go test -count=1` for `test/integration/pipstub` (pass), `go vet` for `test/integration/testify`, `gofmt -l` on the three Go packages (clean), `helm lint` and `helm template` for both stand values files on a scratch copy of the chart with `files/` populated from the same sources the Dockerfile uses, and a local jq run of the transfer-image merge steps on a scratch copy.

### Item 1: comments consistent with the code and each other
Findings: the `main.go` header (finding 3). The default-route paragraph narrates the change ("as it did before the default route existed"), and the "behaviour is exactly as before" sentence is conditioned only on `PIP_STUB_CONFIG`. A default route set through `/pip-stub/configure` changes unrouted answers with `PIP_STUB_CONFIG` unset, so that sentence is now incomplete. The `callRecord.RequestURI`, `defaultRoute` and precedence comments match the code. The chart comments match the rendered output, and the realm-description and idp-seed claims match the realm JSON (checked with jq). I considered "imports the realms at every start" and did not raise it: in Kubernetes a container restart gets a fresh writable layer, so the dev-mode database is re-created and the claim holds.

### Item 2: claimed cases covered
- **9d25da7, Go:** each claim has a named test in `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` (five cases), `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`, and `TestHandlePIP_RecordsTheRequestTargetAsSent`. The one uncovered claim is that `/pip-stub/configure` takes `*` (finding 8).
- **8b85515 and 17b17fc, chart:** no test or render check covers them (finding 2). Only `helm lint` runs.
- **Commands the change tells someone to run, and their CI counterparts:**
  - `make test-stand-files`, `e2e-harness`, `e2e-install`, `e2e-suite`, `parity-harness`, `parity-suite`, `parity-logs`, `e2e-logs` and both `helm lint` lines: run by `integration-tests.yaml`.
  - `helm test authz-test-stand --timeout 15m --logs` (chart README): the flag exists in helm 4.3.0, but no CI job runs this form (finding 6).
  - `docker create` / `docker cp` / `helm upgrade ... ./charts/authz-test-stand --set TAG=... -f my-test-stand-values.yaml` (chart README): `none`, since the transfer image is built only by the release workflow (finding 6).
  - `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...` (`docs/local-integration-tests.md:139`): `none` (finding 6).

### Item 3: boundaries, partitions, negative control
The default-route tests cover unrouted, routed, routed-with-no-responses, no default route, and empty default route, with the routed-path answer as the control. Sequence clamping is covered. The Helm side has no partitions to test. Pre-existing state: a stand built from the base commit's `kubectl` manifests still has the `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `runtime-suite` and realm objects. Nothing in the change handles them (finding 1). Every run in CI starts from a fresh cluster.

### Item 3a: level, placement, environment
The Go tests are in-process, sit in `main_test.go` beside the existing `TestHandlePIP_*` tests, and reuse `resetState`. The chart behavior is observable in one process through `helm template`, so the smallest level for it is a render check, which is missing (finding 2).

### Item 4: names by content
Checked every new test and subtest name and the Make and chart comments. None refers by position or ordinal.

### Item 5: failure report
Every new Go assertion prints its operands, either with `t.Errorf` and `want`, or by comparing values in the message. None found.

### Item 6: what the writer says it verified
Neither a red run on the base commit nor a mutation verdict is stated in any of the three commit messages. The default-route tests cover new behavior rather than a regression, so a red run would show the 404 on base. The `go test` run above is a consistency gate, not that evidence.

### Item 7: siblings
- `podSecurityContext` is used at all four pod sites (idp, pip-stub, suite, tenant-manager). `containerSecurityContext` is used at all five container sites, with `false` only for idp. Every rendered object carries the labels helper.
- Consumers of `/pip-stub/calls` (`test/parity/suite/pip_control.go:162`, `test/integration/testify/pip_admin_test.go:128`, `entitlements_test.go:244`) decode the record additively. None compares whole records, so `requestUri` breaks no golden.
- Every `routes[...]` read site (`main.go:168`, `235`, `398`) was checked.
- Every name in `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` exists in the rendered output.
- No live reference to a deleted manifest remains. `docs/handovers/done/` mentions them as history, which is fine.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | `helm upgrade --install` cannot adopt objects that the base commit's `kubectl apply` created (Deployments `keycloak`/`pip-stub`/`entitlements-mock`/`tenant-manager`, Services, ConfigMaps, the Secret, ServiceAccount `runtime-suite`). Helm's ownership check will refuse them, and no doc names a remedy. Not run: no cluster. | substantive | `Makefile:85` (`e2e-harness`), `Makefile:149` (`parity-harness`), `docs/local-integration-tests.md:127` | Document the remedy (`make e2e-down`, or deleting the old objects) and name it in the commit description, or run `make e2e-harness` once on a cluster built by the base commit. |
| 2 | No render assertion for the test-stand chart. The restricted-PSS fields, labels, the realm checksum, the hook annotation, and `readOnlyRootFilesystem` are asserted by nothing except `helm lint`, although `test/scripts/test-chart-render.sh` already renders the other charts. | substantive | `test/scripts/test-chart-render.sh` (no test-stand section); `helm-templates/authz-test-stand/templates/*.yaml` | Add render checks for both values files: `drop: ALL` and `allowPrivilegeEscalation: false` on every container; `readOnlyRootFilesystem: false` only on idp; `checksum/realms` changes when a realm file changes; `helm.sh/hook: test` on the Job; no `runAsUser`. |
| 3 | The `main.go` header narrates the change ("as it did before the default route existed") and says behaviour is "exactly as before" when `PIP_STUB_CONFIG` is unset, which a default route configured through `/pip-stub/configure` breaks. | substantive | `test/integration/pipstub/main.go:31-32`, `:36-38` | Replace with the condition: "A stub with no default route configured answers an unrouted request 404." Drop the history clause, and qualify "exactly as before" by the default route. |
| 4 | "CI builds both" is false: `.github/docker-dev-config.json` now lists five components. | substantive | `README.md:59` | Name the images the dev config builds, or say "the images in `.github/docker-dev-config.json`". |
| 5 | Keycloak in the SVT compose stack moves from `26.0` to `26.3.5`, pinned by digest. No commit message names this. | substantive | `test/svt/common/compose/docker-compose.yml:3` | Name it in the `8b85515` description, or split it into its own commit with its reason. |
| 6 | Documented procedures with no run: the subset `helm upgrade --reuse-values` command, and the install from the transfer image (`docker create`, `docker cp`, `helm upgrade` with hand-edited values). The final stage of the transfer Dockerfile is built only by the release workflow. | substantive | `docs/local-integration-tests.md:139`; `helm-templates/authz-test-stand/README.md:42-58`; `build/authz-agent-transfer/Dockerfile:52-56` | Run the subset command on a kind stand, and the transfer-image install, or mark both in the docs as not exercised by CI. |
| 7 | The transfer-image merge (profile fill-in and duplicate refusal) is claimed but has no run, because no user file exists yet. My local simulation with one sample user (`parity-r29-level-m2m`) filled in `Parity`, `R29LevelM2M` and the email as documented, and exited 1 on a duplicate username. The logic holds; the claim is untested. | substantive (low) | `build/authz-agent-transfer/Dockerfile:40-47`; `test/parity/suite/testdata/realm/README.md:4-7` | A committed run of the `chart-files` stage with one sample user file and one duplicate, or the README stating it is untested until a user file exists. |
| 8 | No test drives `/pip-stub/configure` with path `*`. The handler stores any path (checked by reading `handleConfigure`), so the claim is true but untested. | substantive (low) | `test/integration/pipstub/main.go:385-403`; `main_test.go` | A test that posts `[{"path":"*",...}]` to the handler and then reads the default answer. |

Taste: none. Churn: none.

**Not checked:** no cluster was available, so Pod Security admission, the Keycloak start and its `runAsNonRoot` acceptance (the 26.3.5 image's user is unverified), the Helm adoption conflict in finding 1, the `helm test` log loop, and the transfer image's final stage were not run. The item 6 evidence is stated as absent, not reproduced.
