# Final review: 58316ca..HEAD (3 commits)

**Claims source:** the three commit messages and the class comments of `test/integration/pipstub/main_test.go`. No task statement was handed over. No earlier report exists, so §4's table is not needed. I changed no files and made no commits.

**Skills:** `test-authoring` and `english-developer-style` from the skills directory. The Go doc-comment skill (`godoc-authoring`) is not in that directory, so Go comments were checked against the form and the repository's own comments.

**Drift script:** ran `comment-drift.py 58316ca HEAD`. It printed nothing because it parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, and this change touches none of them. Every comment was read by hand.

**Checks run locally:** `gofmt -l` is clean; `go test ./...` passes in `test/integration/pipstub`; `helm lint` passes for both test-stand values files and `helm template` renders 12 and 10 objects. Those runs used a copy of the chart with the generated `files/` staged by hand, under `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-J5KLWfEHf7-repo/cc2b03d0-fdd0-4009-ba13-2efce11217b3/scratchpad/chart`. In the render, every object carries the labels, every Pod has `runAsNonRoot` and `RuntimeDefault`, and the realm checksum changes with file content. The user-merge `jq` step gives `R29LevelM2M` and rejects a duplicate username. `make -n` expands `run-suite` as intended.

## Item 1: comments consistent with code and each other

Findings F1, F7, and T1 to T3 below. Checked and consistent: the `LoadConfig` comment (every address variable is set in `suite.env`), the testify Dockerfile comment (`suite.args` exists), the `idp.yaml` and `_helpers.tpl` comments, the realm and tenant facts in `idp-seed/README.md` (checked against the JSON), and the `test/parity/README.md` import list. No comment narrates the change (no `now`, `no longer`, or `used to`).

## Item 2: claimed cases covered

- **9d25da7:** the default-route match, the sequence across paths, `requestUri`, and the "routed path with no responses" case are covered by named tests. The `/pip-stub/configure` claim (F2) and the 404 half of the no-responses claim (F3) are not.
- **17b17fc:** the labels, selectors, and per-container settings are verified by render. The restricted Pod Security Standard claim has no enforcement (F6).
- **8b85515:** realm import with restart on change, keyed pip-stub instances, the tenant emulator, the M2M Secret, the `helm test` hook, `make test-stand-files`, and the published images all match the diff. The resource profiles were confirmed by reading the diff only.

Commands the change tells someone to run:

| Command | Where | Same form run elsewhere | Result |
|---|---|---|---|
| `make test-stand-files` | chart README, Makefile | CI step "Generate the test-stand files" | none |
| `make e2e-harness`, `e2e-install`, `e2e-suite`, `e2e-logs` | docs, `test/k8s/README.md` | CI Kind job | none |
| `make parity-harness`, `parity-install`, `parity-suite`, `parity-logs` | `test/parity/README.md` | CI Parity job | none |
| `make e2e`, `make parity` | `test/k8s/README.md` | the same steps, run one at a time in CI | none |
| `make e2e-down`, `e2e-restart`, `parity-restart` | READMEs | the Makefile target itself, not run in CI | none |
| `kubectl ... rollout restart deploy/authz-agent` | docs | `e2e-restart` uses the same form | none |
| Subset: `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...` | docs, "A subset" | none | F8 |
| `helm upgrade --install ... --set TAG=<version> -f my-test-stand-values.yaml` | chart README, step 2 | none (the transfer image is not run in CI) | F8 |
| `helm test authz-test-stand --timeout 15m --logs` | chart README, step 3 | `run-suite` runs the same without `--logs` | F8 |
| `docker create`, `docker cp`, `docker rm` | chart README, step 1 | none | F8 |

## Item 3: boundaries, partitions, and the negative control

- The default-route cases include controls: a routed path keeps its own answer, and no default route gives 404 (F3 notes the missing 404 corner). The sequence test clamps to the last response.
- **Pre-existing state:** F5. Every CI run starts from a new kind cluster, and no test or documented remedy covers a stand installed by the earlier targets.
- **Limits:** the Job `activeDeadlineSeconds` is 900 s; `helm test --timeout` is 15 min; `-test.timeout` is 600 s; the Keycloak startup probe is 300 s inside `--wait --timeout 10m`; `kubectl wait` is 2 min followed by a 180 s log loop. At the defaults the inner limits fire first (600 s before 900 s, 300 s before 600 s). The 15-minute `helm test` wait equals the Job deadline, but the Job's clock started earlier, so the Job's deadline fires first. None.

## Item 3a: level, placement, and environment

The new Go tests are in-process and small. They sit in `main_test.go` beside the existing tests and use the existing `resetState`. The chart has no in-process level. CI covers lint and the kind harness, but nothing covers the security settings (F6).

## Item 4: names by content, not by position

None. The "second instance" phrases in `test-stand-values.yaml` and the docs also name the instance by its content (the entitlements endpoint). Removing the ordinal would lose nothing.

## Item 5: the failure report

None. The `if got != want` assertions print both operands. Each `Errorf` names the operands in got-before-want order.

## Item 6: what the writer says it verified

None stated. The commit messages record no red run on the base commit and no kind run. The "routed path with no responses" case would panic on the base commit, so a red run there would be cheap to state (9d25da7's `-1` bug).

## Item 7: siblings of the change

- `callRecord` is built at one site (`main.go:212`). `handleReset` clears `counters` (`main.go:377`), so the default route's sequence resets with the others.
- The echo rule writes its own map (`main.go:349`), so its output and the parity goldens do not change. The parity `PipStubCall` mirror omits `requestUri` on purpose, as its comment says.
- Every removed manifest and object name has no remaining reference in `HEAD`, apart from the historical handover docs.
- Other writes under the read-only root: none found in the three images except F4.
- `test/svt/common/compose/docker-compose.yml` pins Keycloak to 26.3.5 by digest. No commit message mentions it (T4).

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | "No request path is `*`" is false. An asterisk-form request (`OPTIONS * HTTP/1.1`) has `URL.Path == "*"` (checked with `http.ReadRequest`), so it reaches the default route. | substantive | `test/integration/pipstub/main.go:36` | Say that an asterisk-form request reaches the default route, or stop it before the default-route lookup. |
| F2 | The claim that `/pip-stub/configure` takes `*` has no test through the handler. The cases write `routes[defaultRoute]` directly. A change that rejects `*` at configure time keeps every test green. | substantive | `main_test.go:225-259`; `main.go:385` | Add a case that PUTs `[{"path":"*", ...}]` to `handleConfigure`, then serves an unrouted path. |
| F3 | The 404 half of "a route with no responses falls through to the default route, or to 404" has no case. The base commit panics there, so the case is also the regression test for `-1`. | substantive | `main_test.go:234-241` | Add a routed path with `[]` responses and no default route, expecting 404. |
| F4 | The observed sidecar is written under `testdata/golden`, which is read-only in the Job. The error is discarded, so the diagnostic is lost on every golden mismatch while the failure still prints. | substantive | `test/parity/suite/compare.go:87`, `:139-147`; `templates/suite.yaml:60-68` | Write the sidecar under a path the Job can write, or report the error. Show in a run that a mismatch leaves the file. |
| F5 | A stand installed by the earlier targets has unowned objects with the chart's names (e2e: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`. Parity: Deployments and Services `idp`, `pip-mock`, `entitlements-mock`; ConfigMap `pip-mock-config`; the same Secret). `helm upgrade --install` refuses to adopt them. Nothing documents a remedy, and `e2e-cluster` reuses an existing kind cluster. | substantive | `Makefile:85-86`, `:149-150`; `docs/local-integration-tests.md` section 8 | Document the remedy (`make e2e-down`, or deleting the listed objects), or run `make e2e-harness` on a cluster built by the old targets. Not run here. |
| F6 | 17b17fc claims the stand runs under the restricted Pod Security Standard. Nothing enforces it: no namespace label, no render assertion, no CI check. | substantive | `Makefile:85-86`; `.github/workflows/integration-tests.yaml:118-151`; `test/scripts/test-chart-render.sh` | Assert the security fields in the render check, or label the namespace. Pod Security is namespace-wide, so check that the agent charts pass first. Otherwise drop the claim from the message. |
| F7 | The troubleshooting row names `rollout status deploy/keycloak` as the `e2e-harness` symptom. That command no longer runs; the target now uses `helm --wait`. | substantive | `docs/local-integration-tests.md:190` | Name the symptom `helm upgrade --install --wait` produces. |
| F8 | Four documented forms have no CI or Makefile counterpart: the subset `helm upgrade --reuse-values`, the transfer-image install with `--set TAG`, `helm test ... --logs`, and the `docker create` and `docker cp` steps. | substantive | `docs/local-integration-tests.md`, "A subset"; `helm-templates/authz-test-stand/README.md:39-65` | Run each once on the kind stand or against the published transfer image, and say so. Or replace each with the form CI runs. |
| T1 | "the release version" for tenant-manager, which is not published. | taste | `helm-templates/authz-test-stand/values.yaml:9-10` | Name pip-stub and the parity suite as the release-versioned images, and say the stand sets the tenant-manager tag. |
| T2 | "the startup probe allows five" leaves the unit to the reader. | taste | `templates/idp.yaml:65` | "allows five minutes (60 checks, 5 seconds apart)". |
| T3 | "the M2M client-credentials Secret the chart expects the platform to provision" reads as if this stand does not create it, but the values turn it on. | taste | `Makefile:83` | Say the platform provisions it on a real stand. |
| T4 | The Keycloak pin in the SVT compose file changed (26.0 to 26.3.5 by digest), and no message says so. | taste | `test/svt/common/compose/docker-compose.yml:4` | Name it in 8b85515's message, or split it into its own commit. |

Not checked: no cluster was available, so the kind suites, the Keycloak and stub behavior under a read-only root, the Keycloak `/auth` management path, the Helm adoption failure in F5, and the `kubectl wait --for=create` flag against the CI kubectl version are unverified; the `docker build --target chart-files` stage was not run (I staged its output by hand and ran only the `jq` step); the Go doc-comment rules were not loaded; and no wording pass was made beyond the sentences that mislead.
