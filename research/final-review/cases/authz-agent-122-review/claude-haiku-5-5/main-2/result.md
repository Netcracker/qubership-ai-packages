## Final review: `58316ca6..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages (17b17fc, 9d25da7, 8b85515) and the test class comments. No previous report exists, so §4 has no table of prior findings.

**Skills.** I read `final-review` in full and `test-authoring` (§3–§7, with `go/testing.md` and `go/testify.md`). `english-developer-style` and a Go doc-comment skill are not in the skills directory, so I did not load them. I checked wording only where it changes a sentence's meaning.

**Drift script.** `comment-drift.py 58316ca6 HEAD` printed nothing. It parses only Java, Kotlin, Groovy and Scala, and this change touches Go, Helm, Make, YAML and Markdown. Item 1 for those files was done by reading.

**What I ran (no repo files changed).**
- `go vet` and `go test -count=1 -v` in `test/integration/pipstub`: pass. `go vet` in `test/integration/testify`: clean.
- `helm lint` on the chart with the runtime values: 0 failed. `helm template` failed in place because the realm files are generated. I rendered a copy in the scratchpad with the realm and rule files copied from the repo sources, for both values files. The rendered objects match the claims.
- A `url.ParseRequestURI("*")` check in a scratchpad module, and the `profile.jq` function run through `jq`.

### Item 1: comments consistent with code and each other

Substantive: one comment is false (F1 below). Checked and consistent: the `callRecord.RequestURI` and `defaultRoute` comments, the `handlePIP` route-fallback comments, the new test comments, the `testify/Dockerfile` and `helpers.go` comments (the `suite.args` and `suite.env` they cite exist), the `_helpers.tpl` comments, the `idp.yaml` and `suite.yaml` comments, the `values.yaml` comments, the Makefile recipe comments, and the `test/k8s/README.md`, `docs/local-integration-tests.md` and chart README statements about the rendered objects. One stale doc row is F6.

### Item 2: claimed cases covered

| Claim (commit) | Test or check |
|---|---|
| `*` answers an unrouted path (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, "an unrouted path gets the default answer" |
| Routed path keeps its own answer | same test, "a routed path keeps its own answer" |
| Route with no responses falls through to the default (9d25da7) | same test, "a routed path with no responses gets the default answer" |
| Route with no responses falls through to 404 (9d25da7) | **not covered**, see F3 |
| Default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| No `*` configured gives 404 | same test, "an unrouted path without a default route is 404" |
| `/pip-stub/configure` takes path `*` (9d25da7) | **not covered through the endpoint**, see F2 |
| Call record keeps `requestUri` as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Keycloak dev mode, realm import at each start, restart on change (8b85515) | rendered: `start-dev --import-realm`, `checksum/realms` annotation |
| Stub instances keyed by Service name, M2M Secret, suite as `helm test` hook (8b85515) | rendered in both value files |
| Three images published, tenant-manager and runtime suite not (8b85515) | `.qubership/docker.cfg` matches |
| `profile.jq` fills first name, last name, email (8b85515) | **no test**, see F5 |
| Restricted PSS run of the stand (17b17fc subject) | **nothing enforces it**, see F4 |

Rendered security settings: runtime has 5 containers and parity has 4. All carry `runAsNonRoot`, `RuntimeDefault` seccomp, `allowPrivilegeEscalation: false` and `drop: [ALL]`. Only Keycloak has a writable root filesystem. No `runAsUser` anywhere.

### Item 3: boundaries, partitions, negative control

Covered: the unrouted, routed, routed-empty, no-default and empty-default partitions, with the no-default case as the control that is green on the base. Missing: the routed-empty path with no default (F3), and a request whose path is `*` (F1).

### Item 3a: level, placement, environment

- The pipstub tests are in-process through `httptest`, which is the smallest level. They sit in the same file beside the existing tests and share `resetState`. No skips.
- The chart has no in-process test. CI lints and renders it, and the kind jobs run it. The restricted-PSS claim is not exercised by any of those (F4).

### Item 4: names by content

No ordinal test names or case ids. One comment refers to a second instance by position where the key `entitlements-mock` names it (taste T1).

### Item 5: failure report

Every `Errorf` and `Fatalf` prints its operands. The `if` comparisons print both values. No findings.

### Item 6: what the writer says it verified

Neither commit message states a red run on the base commit or a mutation verdict. The `-1` index defect in 9d25da7 would have been a natural red run, and it is not stated. The chart has no test that can go red, so the 17b17fc claims rest on reading and render only.

### Item 7: siblings

- `route.Responses` is read in one function (`handlePIP`, `main.go:236-251`), and all three sites are guarded. The rule path (`matchRule`, `main.go:276-281`) already guards `len > 0`, so the `-1` defect has no sibling there.
- `counters["*"]` is cleared by `handleReset`.
- The `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` names match the rendered Deployments. `e2e-logs` uses `deploy/pip-stub`, which exists.
- No remaining references to the deleted manifests except F6.
- The parity suite writes `*.observed.json` into `testdata` on mismatch, and the write errors are discarded. With the read-only root filesystem this write fails, but it already fails because `testdata` is root-owned in the image. No new failure.
- `test/svt/common/compose/docker-compose.yml` moves Keycloak from 26.0 to 26.3.5 pinned by digest. No commit message names it. It matches the chart's image, so the writer should name it in the next commit message.

### Findings

| # | Label | File and line | Change requested |
|---|---|---|---|
| F1 | substantive | `test/integration/pipstub/main.go:36` | The comment says "No request path is \*". False: an asterisk-form request (`OPTIONS *`) gives `r.URL.Path == "*"`, which I confirmed with `url.ParseRequestURI`. A configured default route answers and records it. Correct the sentence, and either exclude `*` from the default route or say it answers that request too. |
| F2 | substantive | `test/integration/pipstub/main_test.go:249`, `:263` | The claim that `/pip-stub/configure` takes path `*` has no test through the endpoint; the tests write `routes[defaultRoute]` directly. Add an in-process test that PUTs `[{"path":"*",...}]` to `handleConfigure` and then requests an unrouted path. |
| F3 | substantive | `test/integration/pipstub/main_test.go:237` | Claimed "or to 404" for a route with no responses and no default is not covered. Add the case to `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, with `defaultResponses` nil. |
| F4 | substantive | `Makefile` (`e2e-harness`, `parity-harness`); `helm-templates/authz-test-stand/templates/_helpers.tpl:19` | No target, workflow or namespace label enforces `pod-security.kubernetes.io/enforce: restricted`; grep of Makefile, `.github`, `test/k8s` and the chart finds none. The subject line "run the test stand under the restricted Pod Security Standard" is therefore not checked by any run. Label the namespace before the install, or reword the claim to "the manifests carry the restricted settings". |
| F5 | substantive | `build/authz-agent-transfer/profile.jq:4-10` | The fill rules have no test, and no user file exists, so the function never runs. I ran it by hand: `parity-r29-level-m2m` gives `lastName` `R29LevelM2M`, and a declared `firstName` is kept, so the comment's example is right today. Nothing keeps it right. Add a fixture run in CI, or a user file with a test. |
| F6 | substantive | `docs/local-integration-tests.md:190` | The troubleshooting row says `make e2e-harness` times out at `rollout status deploy/keycloak`. The target no longer runs `rollout status`; it runs `helm --wait --timeout 10m`. Rewrite the row to the symptom the helm wait prints. |
| T1 | taste | `test/k8s/test-stand-values.yaml:21` | "A second instance" names an entry by position. Naming it `entitlements-mock`, the key on the next line, would be by content. The writer may decline. |
| T2 | taste | `test/integration/pipstub/main.go:31-32` | "behaviour is exactly as before": a route with no responses now gets 404 where it used to panic on index `-1`. The writer may keep the sentence. |
| T3 | taste | `helm-templates/authz-test-stand/templates/idp.yaml:64-65` | "the startup probe allows five" means five minutes (60 × 5 s). A reader may take it as five attempts. |

No churn reported.

### What this review did not check

The suite was not run and nothing was deployed: no kind cluster, no `make test-stand-files` (the Docker build), no `helm test`, and no execution of the Makefile recipes. The chart was rendered from a scratchpad copy with stand-in realm files, not the Docker stage's output. The Go, Helm, Make and YAML files were read by hand, because the drift script does not parse them. Wording was checked only where it changes a sentence's meaning, and `english-developer-style` was not available.
