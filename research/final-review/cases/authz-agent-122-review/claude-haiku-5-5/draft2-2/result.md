## Final review: `58316ca..HEAD` (three commits: 17b17fc, 9d25da7, 8b85515)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages, the Go test class comments, and the docs the change edits. There is no earlier report, so §4 opens without a table.

**Skills.** `test-authoring` and `english-developer-style` were read from the skills directory. The Skill tool did not know `test-authoring` by name, so I read its file directly. There is no Go doc-comment skill in that directory, so Item 1 used the form's own wording and the wording rules.

**Drift script.** It exited 0 with no output. It parses only Java, Kotlin, Groovy, and Scala, and this change is Go, YAML, Helm, Make, and Dockerfile. Item 1 was therefore done by reading the comments.

**Checks run:**
- `go test -count=1 ./...` in `test/integration/pipstub` passed, including the three new test functions and their five subtests. `go vet` is clean for pipstub and testify, and `gofmt -l` is clean.
- `helm lint` on both values files reported 0 failed. Without the generated `files/`, though, lint passes silently with an INFO line, so the check holds only because CI generates the files first.
- I emulated the `chart-files` stage in the scratchpad with local jq 1.8.2, since docker is not available. The output tree matches the README, and the uniqueness checks pass.
- `helm template` of a scratchpad copy with the generated files renders both values files. The e2e render has 12 objects and the parity render has 10.
- The realm checksum changes when a realm file's content changes.
- `git grep` finds no references to the deleted manifests.
- `httptest` confirms that `OPTIONS *` has `URL.Path == "*"`.

### Item 1: comments consistent with the code and with each other

Partly. The `handlePIP` precedence comment matches the code, and the `LoadConfig` comment matches `suite.env` (every `envOr` name it reads is set there). The chart helper, Keycloak, suite, pip-stub, tenant-manager, and client-credentials comments match the render. Findings are F3, F4, F5, and F10.

### Item 2: claimed cases covered

Commit 9d25da7:
- `/pip-stub/configure` takes `*`: no test. The new tests write `routes[defaultRoute]` directly and never reach `handleConfigure` (F1).
- Unconfigured stub answers 404: `an unrouted path without a default route is 404`.
- Route with no responses falls through to the default: `a routed path with no responses gets the default answer`.
- Route with no responses falls through to 404: only the empty-default case is covered, not "no default route" (F2).
- `requestUri` kept as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`. The JSON key `requestUri` is not checked (F1).
- Legacy and rule fallback: existing `TestHandlePIP_RuleThenLegacyFallback` and `TestHandlePIP_RespondSequence`.
- "The stub instance itself comes with the cases that use it": no case in this change uses `*`, so this refers to later work.

Commit 17b17fc: the render confirms the security context on every container, `runAsNonRoot` and `RuntimeDefault` on every Pod, labels on every object, and selectors kept at `app: <name>`. Keycloak's numeric `USER` could not be checked offline (F7).

Commit 8b85515, the chart and realms:
- Keycloak imports at start and restarts on realm change: render plus the checksum test.
- pip-stub instances, tenant-manager, client-credentials Secret, and the suite as a `helm test` hook: render.
- `make test-stand-files` writes the tree: emulated stage.
- `parity-mt-b` realm present and copied.
- Release publishes three images, and tenant-manager and the runtime suite are not published: `.qubership/docker.cfg`.
- The agent and policy-admin resource profiles are unchanged: the diffstat has no changes there.

The profile fill-in function gives the stated values on a sample user, but no user file exists, so no run covers it (F9).

Command lines the change tells someone to run:

| Command | Where | CI job running the same form | Outcome |
|---|---|---|---|
| `make test-stand-files` | Makefile, READMEs | `integration-tests.yaml` "Generate the test-stand files" | Tree written; emulated, not run |
| `helm lint` on both values files | CI | same | 0 failed; meaningful only after generate |
| `make e2e-harness`, `make parity-harness` | READMEs | `kind-e2e`, `kind-parity` | Not run here, no cluster |
| `make e2e-suite`, `make parity-suite`, `make e2e-logs`, `make parity-logs` | READMEs | same jobs | Not run here |
| `make e2e-restart`, `make parity-restart`, `make e2e-images e2e-suite` | `docs/local-integration-tests.md` §6, `test/parity/README.md` | none | Not run; target names match the render |
| `helm upgrade ... --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...` | `docs/local-integration-tests.md:139` | none | Not run (F8) |
| transfer image: `docker create`, `docker cp`, `helm upgrade --install ./charts/...`, `helm test ... --logs` | `helm-templates/authz-test-stand/README.md:40-66` | none (F8) | Not run |
| `kubectl port-forward svc/authz-agent`, `svc/keycloak` | `docs/local-integration-tests.md` §6 | none | Service names match the render; not run |

### Item 3: boundaries, partitions, and the negative control

The Go cases cover the boundary of the sequence clamp and the empty default route. The negative control is the unconfigured stub. The missing partition is a routed path with no responses and no default route (F2).

Pre-existing state: the change replaces manifests applied with `kubectl` in the kind harness. `e2e-cluster` reuses an existing cluster, and every run starts from a fresh one in CI. A developer's surviving `authz-e2e` cluster would meet objects Helm does not own (F6).

### Item 3a: level, placement, and environment

The Go tests run in-process through `httptest`, at the smallest level, in `main_test.go` beside the existing tests, sharing `resetState`. The chart has no render-level test at all (F7).

### Item 4: names by content

None. No new name or message refers by ordinal. The values comment "the binary is the first argument" describes an argv convention, not a referent.

### Item 5: the failure report

None. Every new assertion prints both operands, in got-then-want order. The `if status != tc.wantStatus || body != tc.wantBody` condition is the comparison itself, which `test-authoring` §6 allows.

### Item 6: what the writer says it verified

Not stated. No commit message carries a red run or a mutation verdict, and I did not run the suite to supply one. By reading the base code, the new test `a routed path with no responses gets the default answer` would hit `Responses[-1]` on the base commit, but that evidence is the writer's to state.

### Item 7: siblings of the change

- Go: the path-keyed readers are `main.go` lines 158, 168–169, 234–250, 375–383 (reset), and 398 (configure). The default key goes through the same maps, so reset covers `counters`. `matchRule` does not consult the default route, which the precedence comment says is by design. No other site applies.
- Chart: every Deployment and the Job use the security helpers. The reset target's list of local Deployments names objects the stand renders. No stale references to deleted manifests. `.gitignore` and `.dockerignore` both exclude `files/`.
- Values comment: F4 is a sibling of the release list.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | `/pip-stub/configure` with `*` and the `requestUri` JSON key have no test. | substantive | `test/integration/pipstub/main_test.go:214-286`; `main.go:385-403`, `main.go:70-80` | PUT a `*` route through `handleConfigure` and assert an unrouted path gets its answer. Marshal a `callRecord` and assert the `requestUri` key. |
| F2 | Claimed "or to 404" for a routed path with no responses and no default route has no case. | substantive | `main_test.go:228-241` | Add the case `a routed path with no responses and no default route is 404`. |
| F3 | "No request path is `*`" is false: `OPTIONS *` reaches the handler with path `*`. "No route of its own" also hides the empty-route case the code treats as absent. | substantive | `main.go:35-36`, `main.go:122-123` | Say that a request for `*` is answered by the default route. Reword "no route of its own" to "no route with responses of its own". |
| F4 | `values.yaml` says tenant-manager is among the images released at the release version. Tenant-manager is not published. | substantive | `helm-templates/authz-test-stand/values.yaml:9-10` | Remove tenant-manager from that sentence and say its image takes `TAG` from the kind build. |
| F5 | `REALM-DESCRIPTION.md` lists two realms for the e2e harness. The glob imports four, including the default tenant realm `6f1c2a9e…`, which the suite's tenant URL uses. | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:81-82`; `templates/idp.yaml:3` | List all four realms, or say every realm file under `files/realms/e2e/`. |
| F6 | No remedy for a surviving kind cluster that holds kubectl-era objects. `e2e-cluster` reuses it. Helm refuses to adopt objects without its ownership metadata (from Helm's rule; not run). | substantive | `Makefile:59`; `docs/local-integration-tests.md`; `test/k8s/README.md` | Document the remedy (`make e2e-down`, or delete the objects in `authz-e2e` and `authz-parity`). |
| F7 | The restricted Pod Security claim has no assertion and no enforcing run. No namespace in the repo carries a `pod-security` label. | substantive | `test/scripts/test-chart-render.sh` (run by CI "Render assertions") | Add render assertions over the test stand's `helm template` output: `allowPrivilegeEscalation: false`, `drop: ALL`, pod `runAsNonRoot` and `RuntimeDefault`, and `readOnlyRootFilesystem: true` except Keycloak. |
| F8 | Documented forms no job runs: the transfer-image install, the subset recipe, and the restart recipes. No CI job builds the transfer image. | substantive | `helm-templates/authz-test-stand/README.md:40-66`; `docs/local-integration-tests.md:139-141` | Add a CI step that builds the transfer image and renders `/charts/authz-test-stand` from it. Run the subset recipe on the kind stand, or mark both as not verified in the docs. |
| F9 | The profile fill-in path has no run. No user file exists, so the function never runs in any check. | substantive | `build/authz-agent-transfer/Dockerfile` comment; `test/parity/suite/testdata/realm/README.md:6` | Record a run of the stage with one sample user file, or add that fixture before claiming the fill-in. |
| F10 | Comment narrates the change: "as it did before the default route existed". | taste | `main.go:37-38` | Write: "An unrouted request gets 404 when no default route is configured." |
| F11 | `handleReset` does not clear `routes`. A `*` route survives `/pip-stub/reset` and answers later unrouted paths until the stub restarts. The commit's "a stub nobody configures with `*` answers 404" holds per stub, not per case. | taste | `main.go:375-383` | Prefer: reset clears the default route with the routes, or the commit states that the route persists. |

Churn: none reported.

**Not checked:** no cluster or kind run; no docker build; the Keycloak image's numeric `USER` (not verifiable offline); runtime `readOnlyRootFilesystem` for pip-stub, tenant-manager, and the suite (read from the templates, not run); `helm test`; the runtime and parity suites were not run, and `test/parity/suite` was not vetted.
