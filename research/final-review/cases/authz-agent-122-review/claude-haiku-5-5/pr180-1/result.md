# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No previous report exists, so there is no substantive-finding table to open with. No task statement was handed over, so the claimed cases come from the three commit messages and the test class comments. Item 2 is answered from those alone.

**Skills.** I read `final-review/SKILL.md` in full and loaded `test-authoring/SKILL.md` and `test-authoring/references/go/testing.md`. The `english-developer-style` skill and the Go doc-comment skill are not in the skills directory, so wording was not reviewed.

**Drift script.** It ran and printed nothing. It parses only Java, Kotlin, Groovy and Scala, so none of the changed Go, Make, YAML and Dockerfile code was parsed. Every comment check below was done by reading.

**Checks run.** `go vet` and `go test` pass for `test/integration/pipstub`. `helm template` and `helm lint` pass with the generated files staged in a scratch copy, and the Keycloak checksum changes when a realm file changes. The `profile.jq` filter gives the output the Dockerfile comment describes, on two samples.

## Item 1: comments consistent with the code and with each other

Findings 2, 3, 5 and 10 below. The package doc in `main.go` (rules, then legacy routes, then default route, then 404), the `defaultRoute` and `RequestURI` comments, and the test comments match the code. The `idp.yaml` "no bootstrap admin" comment holds, because `KC_ADMIN_USERNAME` is a realm user in the token requests.

## Item 2: claimed cases covered

| Claim (commit) | Test | Status |
|---|---|---|
| Unrouted path gets the default answer; routed path keeps its own (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` | covered |
| Route with no responses falls through to default, or to 404 | same test, but only the default-present case | partly, finding 7 |
| Empty default route and no default route both give 404 | same test | covered |
| Default route serves its sequence across paths, clamped | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` | covered |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` | covered at struct level |
| `/pip-stub/configure` takes `*` | none; every test writes `routes` directly | finding 6 |
| Chart: off by default, restricted security context, realm restart on change, suite as helm test hook | none in the repo; `test-chart-render.sh` renders only the agent charts | finding 9 |
| `make test-stand-files` merges user files and fails on duplicates | none; no user files exist yet | finding 9 |

## Item 3: boundaries, partitions, negative control

The default-route tests cover the boundary (last response clamped), an empty routed route, an empty default, and no default. Finding 8 is the missing control for rule precedence. The pre-existing-state question is answered by finding 1.

## Item 3a: level and environment

The pipstub tests are in-process, and `go-build.yaml:63` runs them in CI. The chart behaviour has no test below the kind harness (finding 9). The CI lint step is weak (finding 11). I could not run the kind harness, so nothing was verified on a cluster.

## Item 4: names by content

Finding 5: the `pip_control.go` note cites `main.go` by line. Those citations were already wrong at base (base `main.go:52` is the `pipResponse` type), and the change moved them further. No new test or case name uses an ordinal.

## Item 5: failure report

None. The `Errorf` calls print got before want, and the subtests are named by condition.

## Item 6: what the writer says it verified

Neither a red run on the base commit nor a mutation verdict is stated in any of the three commit messages. The Go tests would fail on base only by compile error, since `defaultRoute` and `RequestURI` do not exist there. No run in a restricted namespace is stated for the Pod security claims, and I could not run one.

## Item 7: siblings

- The Makefile and docs no longer reference the deleted manifests, apart from finding 2 and finding 3.
- `handlePIP`'s other callers and the ResetPinnedRoutes flush are unaffected.
- `compare.go` writes to the container root (finding 4). Other writers in the pipstub, tenant-manager and testify code were not found.
- No file in the repo configures the `*` route yet. That matches the commit message, which says the stub comes with the cases that use it.

## Findings

| # | Label | File and line | Change requested |
|---|---|---|---|
| 1 | substantive | `Makefile:85-86`, parity harness at `:149` | On a namespace holding the objects the old `kubectl apply` harness created (same names: `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `idp`, `pip-mock`, `pip-mock-config`, the client-credentials Secret, the `runtime-suite` and `parity-suite` Jobs), `helm upgrade --install` should fail, because Helm 3 refuses to adopt objects without its ownership metadata. I could not run this here. No test starts from that state and no remedy is documented. Run `e2e-harness` on such a namespace, and document the remedy (delete the namespace or those objects) in the commit or the docs. |
| 2 | substantive | `test/k8s/README.md:53` | The `e2e-harness` row says install creates the suite Job. A `helm test` hook is created only by `helm test`, so drop "and the suite Job" from the row. |
| 3 | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`" leaves out the two tenant realms the e2e stand imports (`files/realms/e2e` holds four). Name all four, or say "the realms of `authn/`". |
| 4 | substantive | `test/parity/suite/compare.go:139-146` | `writeObservedSidecar` writes next to the golden file inside the image's read-only root, and its error is discarded. Under `readOnlyRootFilesystem` the sidecar is silently not written, and the commit makes `/tmp` the only writable path without mentioning this. Write under `/tmp`, or name it as a follow-up. Practical impact is small, because `parity-logs` does not copy sidecars out. |
| 5 | substantive | `test/parity/suite/pip_control.go:18-30` | The note says path matching has "No wildcards", but this change adds a `*` default route to the same surface. The line citations (`main.go:50-183`, `:52`, `:110`, `:152-160`) are already stale at base and now more so. Mention the default route, and cite `handleConfigure` and `handlePIP` by name. |
| 6 | substantive | `test/integration/pipstub/main_test.go` (no test) | The commit says `/pip-stub/configure` takes `*`, but no test calls `handleConfigure`. Add a test that PUTs `[{"path":"*",...}]` and then requests an unrouted path. |
| 7 | substantive | `main_test.go:225-260` | The claim "falls through to the default route, or to 404" has no case for a routed path with no responses and no default route, which should give 404. |
| 8 | substantive | `main_test.go` (no test) | The package doc says rules run before the legacy routes and the default route, but no test has a rule match while a default route is configured. Add that control. |
| 9 | substantive | `helm-templates/authz-test-stand` (no test); `build/authz-agent-transfer/Dockerfile` | Add render assertions for the stand to `test-chart-render.sh`: checksum changes with a realm file, and every container but Keycloak has `readOnlyRootFilesystem`. Add a fixture user file so the merge and the duplicate check are exercised. |
| 10 | taste | `Makefile:95-96` | "It prints the log only at the end" is ambiguous: `helm test` prints logs only with `--logs`, which the recipe does not use. Say why the recipe streams instead. |
| 11 | taste | `.github/workflows/integration-tests.yaml:83-84` | `helm lint` exits 0 when the templates fail on the missing generated files (it logs `funcMap fail` at INFO). Adding `helm template` to the step would make it fail. CI generates the files first, so this matters only for a checkout without them. |

## Not checked

- I did not run a kind cluster, `make test-stand-files` (Docker), the restricted Pod Security admission, or either suite.
- I staged a copy of the chart with generated files under the scratchpad, not in the repo. The repo is unchanged, and nothing was committed.
- I did not read the full `REALM-DESCRIPTION.md` or the `fixtures/smoke` file that mentions a default route.
- Wording was not reviewed (no developer-style skill was available).
