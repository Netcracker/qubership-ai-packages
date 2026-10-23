## Final review: `58316ca..HEAD` (three commits, Go, Helm, Makefile)

**Scope and inputs.** There was no task statement, so the claimed cases come from the three commit messages: `9d25da7` (pipstub default route), `8b85515` (test-stand chart and harness targets), and `17b17fc` (restricted Pod Security). This is the first round, so there was no previous report to re-read. The test-authoring and english-developer-style skills were loaded from the given directory. The Go doc-comment skill (`godoc-authoring`) is not in that directory, so Go comments were checked by reading only.

**Drift script.** It ran and printed nothing, which is not evidence of no drift. It parses only `.java .kt .kts .groovy .scala`, and this change touches no such file, so it does not apply. Go comments were read by hand.

**Checks run (no repo file changed, nothing committed):**
- `go test`, `go vet`, and `gofmt -l` on `test/integration/pipstub`: all clean.
- `helm lint` and `helm template` of `helm-templates/authz-test-stand` in a scratch copy, with stub realm and rule files, for both harness values files: both render with exit 0.
- In the rendered output, all five pods and containers have `runAsNonRoot`, `seccompProfile: RuntimeDefault`, `allowPrivilegeEscalation: false`, and `drop: [ALL]`. Only Keycloak is `readOnlyRootFilesystem: false`. No `runAsUser` is pinned.
- The realm checksum annotation changes when a realm file's content changes.
- The `profile.jq` fill-in gives `R29LevelM2M` for `parity-r29-level-m2m`.
- An `OPTIONS *` request reaches the handler with `r.URL.Path == "*"`.

---

### Item 1: comments consistent with the code and with each other
Substantive finding. `test/integration/pipstub/main.go:36` says "No request path is `*`". That is false: an `OPTIONS *` request has path `*` (checked with `httptest`). The effect is harmless, since such a request gets the same default-route answer that any unrouted path gets. The sentence should say that only an `OPTIONS *` request has that path.

Substantive finding in a sibling comment. `test/parity/suite/pip_control.go:30` says path matching has "No wildcards". The default route `*` is now a wildcard for unrouted paths, so the caveat is incomplete. The line citations in that comment were already stale on the base commit; that is not introduced here.

Otherwise the package doc, the `defaultRoute` comment, the `RequestURI` comment, the Makefile `run-suite` comment, and the Dockerfile and values comments agree with the code I checked.

### Item 2: claimed cases covered
- **`9d25da7`, pipstub.** Covered by `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` and `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`. `TestHandlePIP_RecordsTheRequestTargetAsSent` covers `requestUri`.
  - Substantive finding: the claim "a route with no responses falls through to the default route, or to 404" has no 404 row. No table row has a routed path with empty responses and no default route. `test/integration/pipstub/main_test.go:225-245`.
- **`8b85515`, chart.** No CI test covers the claimed behavior. The only CI check is `helm lint` for the test-stand chart (`.github/workflows/integration-tests.yaml:83-84`). `test/scripts/test-chart-render.sh` covers only the two other charts. Claims without a test: instances keyed by Service name, the realm checksum restart, the helm test hook, the tenant map, the M2M Secret, and the parity-mt-b realm. I checked the render and checksum behavior by hand; the claims are not tested in CI.
- **`17b17fc`, security context.** Same gap: the restricted-PSS properties are not asserted anywhere.

### Item 3: boundaries, partitions, and the negative control
- Boundaries covered: zero responses vs one; sequence clamp to the last response across paths. The negative control is present: a stub with no default route answers 404.
- Substantive finding, pre-existing state. The chart replaces objects that the old kubectl manifests created in the same namespace: `keycloak`, `keycloak-realms`, `authz-agent-client-credentials`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `pip-mock`, `pip-mock-config`, `idp`, `parity-realms`. `e2e-cluster` reuses an existing cluster. No test or run starts from that state, and the docs give no remedy beyond `make e2e-down` under "Cluster left behind" (`docs/local-integration-tests.md:193`). I did not run this. Helm 3 is expected to refuse to adopt unlabelled objects, but there is no cluster here to confirm it.
- Substantive finding, a limit that another limit caps. `suite.activeDeadlineSeconds: 900` (`helm-templates/authz-test-stand/values.yaml:99`) is capped by `helm test ... --timeout 15m` in the `run-suite` define (`Makefile:100-108`). Raising the deadline past 15 minutes has no effect.
- Limits on the same path, for the record: the Go `-test.timeout 600s` in `args` fires before the Job deadline at defaults. `kubectl wait --for=create` is 2 minutes, and the log poll is 3 minutes. Keycloak's startup probe allows 5 minutes inside `--wait --timeout 10m`.

### Item 3a: level, placement, and the environment
The pipstub tests are in-process through `httptest`, which is the smallest level. They sit beside the existing tests and reuse `resetState`. No skips were added. The chart has no test at any level beyond lint (see Item 2).

### Item 4: names by content
Taste finding: `test/k8s/test-stand-values.yaml:21` says "A second instance for the entitlements endpoint". Name the instance `entitlements-mock`. Test names are content-named and the table cases are named by condition.

### Item 5: the failure report
None. The new `t.Errorf` and `t.Fatalf` calls print both operands. The `reflect.DeepEqual` check prints the got and want values.

### Item 6: what the writer says it verified
Neither a red run on the base commit nor a mutation verdict is stated in any of the three commits. The `9d25da7` routed-empty case would panic on the base commit, so the red run is the evidence to state. The gap is stated here, not supplied by this review.

### Item 7: siblings of the change
- The stub's `callRecord` is mirrored by `PipStubCall` in `test/parity/suite/pip_control.go`. The new field is additive, so that is fine. The `pip_control.go` comment is the sibling that needs the `*` wording (Item 1).
- `containerSecurityContext` is used in all five containers and `podSecurityContext` in all four pods. The render confirms it.
- The restart target names in the Makefile match the chart's Deployment names.
- A grep for references to the deleted manifests found none left.

---

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| "No request path is `*`" is false: `OPTIONS *` has path `*` | substantive | `test/integration/pipstub/main.go:36` | Say only an `OPTIONS *` request has that path, and it gets the default route's answer |
| No case for a routed path with empty responses and no default route → 404, which 9d25da7 claims | substantive | `test/integration/pipstub/main_test.go:225-245` | Add a row; it panics on the base commit |
| "No wildcards" caveat is now incomplete because `*` is a default route | substantive | `test/parity/suite/pip_control.go:30` | State that a route registered as `*` answers unrouted paths |
| Upgrading a stand that the old manifests created is untested and undocumented | substantive | `Makefile` `e2e-harness` (line 85) and `parity-harness` (line 149); `docs/local-integration-tests.md:193` | Run `make e2e-harness` over the old state, or document the remedy (`make e2e-down`, or delete the named objects) |
| `activeDeadlineSeconds` is capped by `helm test --timeout 15m` | substantive | `helm-templates/authz-test-stand/values.yaml:99`; `Makefile:100-108` | Derive the helm timeout from the deadline, or document the pair |
| No CI assertion for the security context, realm checksum, test hook, or instance names | substantive | `.github/workflows/integration-tests.yaml:83-84`; `test/scripts/test-chart-render.sh` | Add render assertions for the claimed properties |
| No red run or mutation verdict stated for `9d25da7` | substantive | commit `9d25da7` | State the red run on the base commit |
| "A second instance" names an entry by ordinal | taste | `test/k8s/test-stand-values.yaml:21` | Name it `entitlements-mock` |

**Not checked:** the parity and runtime suites were not run, nothing ran on a kind cluster, and the README and docs prose was checked only for stale references. The Go doc-comment skill was not available, and the style pass was limited to wording that changes meaning.
