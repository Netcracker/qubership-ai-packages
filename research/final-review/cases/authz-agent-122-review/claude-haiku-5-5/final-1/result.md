## Final review: `58316ca..HEAD` (three commits, 17b17fc, 9d25da7, 8b85515)

**Claimed cases** come from the three commit messages and the test class comments. No task statement was handed over. The change has Go code (pipstub), a Helm chart, Makefile and Dockerfile changes, and docs, so the form ran on both the code analogue and the no-code analogue.

**Skills:** `final-review` and `test-authoring` were loaded from the given directory, and so was `english-developer-style`, which I applied only where wording misleads. The Go doc-comment skill (`godoc-authoring`) is not among the three permitted copies, so I did not load it. The Go comments were checked against the code by hand.

**Previous report:** none exists; this is the first review of this change, so there is no table of prior findings.

**Drift script:** ran with `python3 -I`, exit 0, no output. I did not confirm whether it parses Go or YAML, so I read every changed member by hand.

**Evidence I ran:**
- `go vet` and `go test -count=1 -v ./...` in `test/integration/pipstub`: all pass.
- `helm lint` and `helm template` on the chart with both values files, using a scratch copy with the generated files copied from their sources: both pass; 12 and 10 objects rendered.
- A probe showed Go's `ServeMux` answers `OPTIONS *` with 400 before `handlePIP`, so the comment "No request path is `*`" holds for the served stub. Not a finding.
- `profile.jq` on two sample users gives the documented fields.

---

### Item 1: comments consistent with the code and with each other

Checked the Go doc comments on `handlePIP`, `callRecord.RequestURI`, `defaultRoute`, and the file header against the new code; all agree. The chart comments (`podSecurityContext`, `containerSecurityContext`, the Keycloak `readOnlyRootFilesystem` note, the realm checksum) agree with the rendered output. One taste-level wording issue (T1 below).

### Item 2: claimed cases covered

| Claim | Test |
|---|---|
| Unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` |
| Routed path keeps its own answer | same, case 2 |
| Route with no responses falls through to the default | same, case 3 |
| No default route, or empty default, gives 404 | same, cases 4 and 5 |
| Default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Route with no responses, no default, gives 404 | **no test** (S6) |
| `/pip-stub/configure` takes `*` | **no test drives `handleConfigure`** (S7) |
| Transfer stage fills profile fields | **no test; no user file exists** (S8) |
| Stub runs under the restricted PSS | **no enforcement or check** (S4) |
| Chart security context, labels, realm restart | **no render assertion** (S5) |

### Item 3: boundaries, partitions, negative control

The pipstub suite has the negative control (no default route gives 404) and the sequence clamp boundary.

**Limits, listed by where each is set:**
- `go test -test.timeout 600s`: `suite.args`, `test/k8s/test-stand-values.yaml`.
- `suite.activeDeadlineSeconds: 900`: `helm-templates/authz-test-stand/values.yaml:99`.
- `helm test --timeout 15m`: `Makefile:102`, in `run-suite`.
- Keycloak startup probe, 60 × 5 s = 300 s, inside `helm upgrade --wait --timeout 10m`: fine.

The inner test timeout fires first at the defaults. The Job's own deadline does not (S2).

**Pre-existing state:** the change replaces objects that the old harness created with `kubectl apply`, under the same names (S3).

### Item 3a: level, placement, environment

The pipstub tests are in-process, sit beside the existing tests, and run in CI through `go-build.yaml`. The chart changes are covered only by `helm lint`. `test/scripts/test-chart-render.sh` does not render `authz-test-stand` (S5).

### Item 4: names by content

One ordinal: `test/k8s/test-stand-values.yaml:21` (T1).

### Item 5: failure report

All new assertions print their operands, and none uses an `and` name or an index id. None.

### Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict is stated for the regression case (the `-1` sequence index). The commit messages give none. The stated evidence is absent.

### Item 7: siblings

- **Stale references:** `git grep` finds no remaining references to the deleted manifests or the removed Make variables.
- **Config sibling:** the Keycloak Deployment has `checksum/realms`, but the pip-stub Deployments have no config checksum. The stub reads its rule file once at start (`main.go:136-160`), so re-running the harness after an edit to `requestargs.responses.yaml` leaves the old rules running (S1). This is the same defect the change fixes for Keycloak.
- **Pipstub callers:** `routes[` and `counters[` are touched in `handlePIP` (lines 235–250), `handleConfigure` (398), and `loadDefaultRoutes` (168). `handleReset` resets `counters`, which the sequence test relies on. Consistent.

---

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| S1. pip-stub Deployments have no config checksum, so a rule-file edit does not reach a running stub. | Substantive | `helm-templates/authz-test-stand/templates/pip-stub.yaml:39` (pod template); compare `idp.yaml:35` | Add a `checksum/config` pod annotation per instance, as `idp.yaml` does for realms. |
| S2. Inner Job deadline does not fire before the outer helm timeout at the defaults. The Job's 900 s counts from Job start, after helm's 15 m clock starts. | Substantive | `Makefile:102` (`--timeout 15m`); `values.yaml:99` (`activeDeadlineSeconds: 900`) | Set the Job deadline below the helm timeout, or derive one from the other. |
| S3. Earlier harness objects (`keycloak`, `keycloak-realms`, `authz-agent-client-credentials`, the stubs, `runtime-suite`) share names with the chart's objects. `e2e-cluster` reuses an existing cluster, and Helm refuses to adopt objects without release metadata (not run here). No remedy is documented. | Substantive | `Makefile:59` (`e2e-cluster`); `docs/local-integration-tests.md` | Document the remedy (`make e2e-down`, or delete the old objects) and run `e2e-harness` once over the old state. |
| S4. The restricted-PSS claim is not enforced: no `pod-security.kubernetes.io/*` label anywhere in the repo, and no check. | Substantive | `helm-templates/authz-test-stand/README.md:9`; commit 17b17fc title; `Makefile` `e2e-harness` | Label the namespace `enforce: restricted` in the harness, or reword the claim to "compliant with". |
| S5. Security context, labels, and realm checksum have no render assertion. CI runs only `helm lint` on the stand. | Substantive | `test/scripts/test-chart-render.sh` (no `authz-test-stand`); `.github/workflows/integration-tests.yaml` lint step | Add `helm template` assertions for `runAsNonRoot`, `readOnlyRootFilesystem` (false only for Keycloak), no `runAsUser`, and the checksum. |
| S6. No case for a routed path with empty responses and no default route, which the commit says gives 404. | Substantive | `test/integration/pipstub/main_test.go:225-260` (case table) | Add the case. |
| S7. No test drives `handleConfigure` with path `*`; the tests write `routes` directly. | Substantive | `main_test.go:247-263`; `main.go:385-402` | Add a case that PUTs `[{"path":"*",...}]` to `handleConfigure` and then requests an unrouted path. |
| S8. The `profile.jq` stage has no case: no user file exists (`testdata/realm/` has only a README). The commit says "none so far". | Substantive | `build/authz-agent-transfer/Dockerfile:39` and the `profile` stage | Run the stage on one checked-in sample user, or state in the commit that the path is unexercised. |
| T1. "A second instance" refers by ordinal; the instance is named on the next line. | Taste | `test/k8s/test-stand-values.yaml:21` | Name it: "The entitlements-mock instance." Expect this to be declined. |

**Item 6, stated for the writer:** the red run or mutation verdict for the regression case is not in the change.

**What this review did not check:** I did not run the Makefile recipes, Docker, kind, or the Keycloak and suite images, so the claims about Helm refusing to adopt the old objects (S3), the `helm test` timeout behavior (S2), and the Keycloak health path are read from the manifests, not observed. The transfer stage was checked only on sample users, not through Docker. The drift script produced no output, and I did not confirm whether it parses Go or YAML. I wrote nothing into the repository; the probe programs and the scratch chart copy are in the scratchpad directory.
