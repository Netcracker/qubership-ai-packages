## Final review: `58316ca..HEAD` (three commits)

**Inputs.** No separate task statement was handed over, so the claimed cases come from the three commit messages (`17b17fc`, `9d25da7`, `8b85515`) and the class comments in the Go tests. No previous report exists. The drift script prints nothing: it parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, and this range changes none of those. Go, Helm, Make, Dockerfile, and Markdown have no drift coverage, so the form was run by reading. I loaded `test-authoring` and `english-developer-style` from the given copies. I did not load a Go doc-comment skill, since the task named only these three.

**Checks run (no repo files changed):** `go vet` and `go test` in `test/integration/pipstub` (pass); `helm lint` on both kind value files and `helm template` on a scratch copy of HEAD, with the `chart-files` stage reproduced by hand with local `jq` and `cp`, not Docker; `make -n` on the four new recipes; the profile and duplicate-check steps run on sample users; `url.ParseRequestURI("*")` in a scratch Go program.

The change is mostly sound. The pipstub logic and its tests hold up, the rendered chart has the claimed security context on every container (5 in e2e, 4 in parity), and the realm checksum changes when a realm file does. The findings below are gaps in evidence, a few stale statements, and one state the change does not handle.

### Item 1: comments consistent with code and with each other
Checked the pipstub package comment, `defaultRoute`, `RequestURI`, and the test comments against the code; the chart helper, label, and realm-glob comments; the tenant-manager 404 comment against `main.go`; and the Makefile comments. Findings F4, F5, F6, F7, F13 (substantive), T1 (taste). Narration grep over added lines: only T1.

### Item 2: claimed cases covered
- **Pipstub, covered:** unrouted path gets default (`an unrouted path gets the default answer`); routed keeps own; routed-empty gets default; no default is 404; empty default is 404; sequence clamps across paths (`TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`); `requestUri` kept as sent (`TestHandlePIP_RecordsTheRequestTargetAsSent`).
- **Pipstub, not covered:** "a route with no responses ... falls through to the default route, or to 404". The 404 half has no case (F10).
- **Chart, not covered:** the restricted-PSS claims, off-by-default, labels, the tenant map, the M2M Secret, the hook (F1, F2). `test/scripts/test-chart-render.sh` renders only the agent and policy-admin charts.
- **Build, not covered:** profile fill and "build fails if a user is declared twice" (F11).
- **Commands, each with its outcome:**
  - `make test-stand-files`, `make e2e-harness`, `make parity-harness`, `make e2e-suite`, `make parity-suite`: run by their own targets; expansion checked with `make -n`.
  - `helm lint` on both value files: run in CI, and passes locally.
  - `docker build -t authz-agent-transfer -f build/authz-agent-transfer/Dockerfile .`: run by the `docker-dev-config.json` entry with the same Dockerfile and context.
  - `helm test authz-test-stand --timeout 15m --logs` (chart README:64): none, because Make runs `helm test` without `--logs` (F12).
  - `helm upgrade --install ... ./charts/authz-test-stand --set TAG=... -f my-test-stand-values.yaml` (README:58) and `docker create` / `docker cp` / `docker rm` (README:42-44): none, since no CI job installs from the transfer image (F12).
  - Subset `helm ... upgrade ... --reuse-values --set ...` (`docs/local-integration-tests.md:140`): none. Rendered it: `RUNTIME_SUITE_RUN` and `FULL_RUNTIME_SUITE` come out as intended (F12).

### Item 3: boundaries, partitions, negative control
Pipstub is well partitioned: default nil versus empty, routed with and without responses, and the clamp. The negative control (no `*` configured, 404) is present. Chart empty values fail with clear messages: `tenants: {}`, missing `TAG`, missing files, and missing image. Both pip-stub states are exercised by the kind values (pip-mock with a rule file, pip-stub without). Pre-existing state: F3.

### Item 3a: level, placement, environment
Pipstub tests are in-process at the handler, beside the existing ones and sharing `resetState`, which is the right level and placement. Chart properties have no test at the smallest level (F1), and nothing runs them under an enforcing namespace (F2). No skips.

### Item 4: names by content
None. "A second instance" in `test-stand-values.yaml` names the instance by its endpoint.

### Item 5: failure report
None. All new assertions print got and want.

### Item 6: what the writer says it verified
Not stated, in any of the three commit messages: no red run on the base commit, no mutation verdict, and no run in an enforcing namespace. I did not run the suite to supply it.

### Item 7: siblings
- `routes` readers: `handlePIP`, `handleConfigure`, `loadDefaultRoutes`. `counters` readers: `handlePIP` and `handleReset`. Nothing missed.
- `callRecord` has one producer. `echo` builds its own map, so `requestUri` cannot leak into echo output.
- Every chart object carries the labels, and every pod carries the pod security context.
- No remaining references to the deleted manifests except F5 and `docs/handovers`, which are history.

## Findings

| ID | Label | File and line | Change requested |
|---|---|---|---|
| F1 | substantive | `test/scripts/test-chart-render.sh:25-26`; `helm-templates/authz-test-stand/templates/_helpers.tpl:17-40` | Add render assertions for the test stand: per-container security context, pod seccomp and non-root, labels, nothing rendered by default, and the realm checksum. The properties hold today on my render, but nothing keeps them. |
| F2 | substantive | `Makefile:86`, `Makefile:150`; `_helpers.tpl:17-21` | The claim that the stand starts under `restricted` has no run. The kind namespaces carry no enforce label. Run `make e2e-harness` in a namespace labelled `pod-security.kubernetes.io/enforce: restricted`, or state that it was not run. |
| F3 | substantive | `Makefile:85-86` (`e2e-harness`); `docs/local-integration-tests.md` (cluster notes) | A standing kind cluster holds the objects the old `kubectl apply` made: Deployments, the `keycloak-realms` ConfigMap, the client-credentials Secret, Services, and the `runtime-suite` ServiceAccount. They lack Helm ownership metadata, so `helm upgrade --install` should refuse them. Not run here, since there is no cluster. Run `e2e-harness` over the base manifests and document the remedy (`make e2e-down`, or deleting those objects). |
| F4 | substantive | `docs/local-integration-tests.md:104` | The `e2e-harness` row says it installs "the suite Job". The Job is a `helm test` hook (`suite.yaml:19-22`) that only `helm test` creates, as `test/k8s/README.md` and the chart README say. Remove "and the suite Job". |
| F5 | substantive | `README.md:59` | "CI builds both" is stale: `.github/docker-dev-config.json` now lists five images. Name the images CI builds. |
| F6 | substantive | `helm-templates/authz-test-stand/values.yaml:9-10` | "the release version" is stated for tenant-manager, which is not published. Say it takes `TAG` but has no release. |
| F7 | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | The sentence says `make e2e-harness` runs Keycloak with two realm files. The chart imports all four of `files/realms/e2e/`, including the two tenant realms. |
| F8 | substantive | `test/k8s/parity/idp-seed/parity-realm.json:30`; `test/parity/README.md:71` | The realm cites `TestTenantScopedDecisions`, which exists nowhere in the repo. The README says cases "that need those users run on the kind harness", but `testdata/realm/` holds only a README. Remove the reference, or add the cases in this change. |
| F9 | substantive | commit `8b85515` message | It says only that the parity realm "gains a second tenant realm". The realm diff adds 8 users, 5 clients, 2 roles, and a `parity-level-claim` mapper, and no file in the tree uses them. Name those additions in the message, or move them to the change that consumes them. |
| F10 | substantive | `test/integration/pipstub/main_test.go:225-245` | Add the claimed case "a routed path with no responses and no default route is 404" (empty routed list, nil default). |
| F11 | substantive | `build/authz-agent-transfer/Dockerfile:32-47` | The profile fill and the duplicate check are claimed but never run, since `testdata/realm/` has no user file. I ran them by hand: the profile values are right, and the duplicate check exits non-zero. Add a sample-user run, or state the run. |
| F12 | substantive | `helm-templates/authz-test-stand/README.md:58, 64` (and `:42-44`); `docs/local-integration-tests.md:140` | No target runs `helm test ... --logs`, the transfer-image install, or the subset upgrade. Whether `--logs` prints output for a Job hook is unverified. The subset command renders correctly. Run each on kind, or replace it with the make target that runs the same form. |
| F13 | substantive (minor) | `test/integration/pipstub/main.go:36` | "No request path is \*" is false: an `OPTIONS *` request has path `*` (checked). Say that the default route answers `*` and that no real route is shadowed. |
| F14 | substantive (minor) | `test/k8s/authn/REALM-DESCRIPTION.md:82` and `test/parity/README.md:71` | Covered under F7 and F8. |
| T1 | taste | `main.go`, the package comment after line 35 | "as it did before the default route existed" narrates the change. Drop the clause. |
| T2 | taste | `templates/pip-stub.yaml:31-33` | Realm changes restart Keycloak through a checksum (`idp.yaml:34-35`). Rule-file changes do not restart the stub. Add the same annotation, or say in the README that a rule change needs a restart. |
| T3 | taste | `test/svt/common/compose/docker-compose.yml:3` | The Keycloak pin changed from 26.0 to 26.3.5 with a digest, and no commit message mentions it. Mention it. |

Not changed: the Keycloak `JAVA_OPTS_APPEND` drop, which is harmless because the container filesystem is fresh on each start; the "allows five" probe comment, which is churn.

**What the review did not check:** no cluster, so no kind install, `helm test`, PSS enforcement, or upgrade-from-manifests run (F2, F3, F12); the Docker build of the transfer stage (I replicated its steps with local `jq` and `cp`, not the pinned `jq` 1.8.1); Keycloak's writable paths under `/opt/keycloak`; `kubectl wait --for=create`, which needs kubectl 1.31 or later; the parity and runtime suites, which were not run; and no red run on the base commit. The scratch chart for the render checks is at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-ugaDtV2O9L-repo/34de474a-70ee-482f-8b98-0cee0a93a106/scratchpad/chart`.
