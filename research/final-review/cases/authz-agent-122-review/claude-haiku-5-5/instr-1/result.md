# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages and the test class comments. The drift script printed nothing: it parses only JVM files, and this change has none. I read the Go comments by hand. The skills I loaded are `test-authoring` (§§1, 3, 5, 7) and `english-developer-style` (§§4, 7). The Go doc-comment skill and `change-description-authoring` are not among the copies provided, so I did not load them. No previous report exists, so §4's table is empty.

**Checks I ran.** Nothing in the repository was changed or committed.
- `go test ./...` in `test/integration/pipstub`: passes.
- `helm lint` on the chart, with `files/` generated in a scratch copy, for both values files: passes.
- `helm template` renders 12 objects (e2e) and 10 (parity). Every Pod has `runAsNonRoot`, `seccompProfile: RuntimeDefault`, `allowPrivilegeEscalation: false` and `drop: ALL`. `readOnlyRootFilesystem` is `false` only for Keycloak.
- The `generate` stage's jq steps, run by hand on two dummy user files in scratch: the profile fill and the duplicate check behave as the comments say.
- Scratch dir: `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-T9sP8rHJIR-repo/f36c2cfd-5ae9-4602-8243-61f80034c540/scratchpad`

## Item 1: comments consistent with the code and with each other
Four comments are wrong or incomplete, and one comment is ambiguous. The Go doc comments in `main.go` match their code. Findings F10, F11, F13 and F14 cover the rest of this item, and F15 is taste.

## Item 2: claimed cases covered
- **Command lines:**
  - `make test-stand-files`, `e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` and `helm lint` run in CI with the same flags. Outcome: covered.
  - `helm test authz-test-stand --timeout 15m --logs` (chart README:64) has no run; see F8.
  - `helm upgrade --install … -f my-test-stand-values.yaml` (chart README) has no namespace flag and no run.
  - `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (`docs/local-integration-tests.md`) has no run.
  - `docker create … true` and `docker cp` (chart README) have no run.
- **Claims without a test:** the restricted Pod Security claims (F3), the default route's `configure` path and the 404 case (F4), and the profile and duplicate checks (F5).
- **Hunks no sentence claims:** F6.
- **Commit 9d25da7, last sentence:** F13.

## Item 3: boundaries, partitions, and the negative control
- **Pre-existing state (F1):** the base commit created the Keycloak, stub, tenant-manager and ServiceAccount objects with `kubectl apply`, under the same names the chart now renders. No migration note and no run starts from that state.
- **Replaced mechanism (F2):** the `run-suite` replacement fails about five times later than the old `wait Ready` for a pod that never starts.
- **Limits (F9):** the derivation is missing.
- **Setting reaching a new consumer:** `E2E_HELM_ARGS` now reaches the test stand. The names it shares with the old consumers are `TAG` and `IMAGE_PULL_POLICY`. The example `IMAGE_PULL_POLICY=Never` means the same to both. I found no case where a value means something different, so no finding.
- **Pipstub negative control:** present. The stub with no default route answers 404, and the routed path keeps its own answer.

### Item 3a: level, placement, environment
The pipstub tests run in-process and sit beside the existing tests, with the shared `resetState`. The chart has no test at the smallest level (`helm template` with `test/scripts/test-chart-render.sh`), so its claimed defaults and security context are asserted nowhere (F3).

## Item 4: names by content, not position
One taste finding (F15).

## Item 5: the failure report
None. The Go assertions print both operands. The `if got != want { t.Errorf }` form is the Go idiom the skill keeps.

## Item 6: what the writer says it verified
Neither commit states a red run on the base commit or a mutation verdict. The skill says to say so, so this is F12. I did not run mutations, because the evidence is the writer's to state.

## Item 7: siblings
- The README still says "CI builds both" after `docker-dev-config.json` grew to five images (F7).
- I searched for references to the deleted manifests (`keycloak.yaml`, `runtime-suite-job.yaml`, and the others) and found none.
- The image lists in `test/k8s/README.md` and `docs/local-integration-tests.md` include the new images.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | On a kind cluster built by the base commit, `make e2e-harness` and `make parity-harness` will hit Helm's ownership check. Objects created outside Helm (`keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `keycloak-realms`, `pip-mock-config`, `authz-agent-client-credentials`, `runtime-suite` SA) are not adopted. `e2e` reuses an existing cluster, so a developer hits this. Not run: no cluster. | substantive | `Makefile:84-88`, `:146-151`; base `test/k8s/keycloak.yaml`, `test/k8s/runtime-suite-rbac.yaml` | Run the harness from the base commit's state, or add the documented remedy (`make e2e-down`, or delete the namespace) to `docs/local-integration-tests.md` and name the objects in it. (test-authoring §3) |
| F2 | A pod that never starts (`IMAGE_PULL_POLICY: Never` with an image not loaded) now fails after about 15 min. The old `wait Ready --timeout=3m` failed at 3 min. The new loop is silent for about 3 min, `logs -f` then prints the waiting reason, and `wait $helm_pid` blocks until `helm test --timeout 15m`. No sentence accepts the later failure. | substantive | `Makefile:100-106` (`--timeout=2m` at :103) | Bound the wait at about 3 min, or add a sentence that accepts 15 min. Then run the fault on the new target and state both durations and outputs. (test-authoring §3) |
| F3 | The restricted Pod Security claim is not run. No namespace is labeled `pod-security.kubernetes.io/enforce: restricted` (`git grep` finds none). `test/scripts/test-chart-render.sh` is unchanged and asserts nothing about the chart. The title "run the test stand under the restricted Pod Security Standard" overstates. I confirmed the rendered output, not the admission. | substantive | `17b17fc` title; `_helpers.tpl:17-27`; chart `README.md:8-11`; `test/scripts/test-chart-render.sh` | Add render assertions for each Pod and container security context in both values files, and label the kind namespaces `enforce=restricted`, or retitle the claim. (test-authoring §3, level) |
| F4 | Two `9d25da7` claims have no test. (a) `/pip-stub/configure` takes `*` as the default route: no test calls `handleConfigure`. (b) "A route with no responses falls through to the default route, or to 404": the 404 variant (routed path, empty responses, no default) has no case. | substantive | `main.go:385-398`; `main_test.go:225-258` | Add a case that POSTs `[{"path":"*",…}]` to `handleConfigure` and then GETs an unrouted path, and a case for an empty routed path with no default expecting 404. (test-authoring §3, §4) |
| F5 | The profile fill and the duplicate-user check are claimed, but no run in the repo executes them: no user file exists yet. My scratch run shows they work. | substantive | `build/authz-agent-transfer/Dockerfile:39-47`; `test/parity/suite/testdata/realm/README.md:3-7` | Run the stage with one fixture user file, in a test or in CI, or state that the check is verified only by hand. (test-authoring §3) |
| F6 | Hunks no sentence claims: `test/svt/common/compose/docker-compose.yml:3` (Keycloak 26.0 to 26.3.5 digest, unrelated to the stand); `.github/docker-dev-config.json` (+3 images); `.github/workflows/integration-tests.yaml:76-84` (generate step and two lint lines); comment-only edits in `test/integration/testify/helpers.go` and `Dockerfile`; `test/k8s/values.yaml` comment; deletion of `test/k8s/authn/m2m-credentials/*` (values moved to `test/k8s/test-stand-values.yaml:37-40`). | substantive | as listed | A sentence in a commit message that claims each, or move the svt pin to its own change. (final-review §2 item 2) |
| F7 | "CI builds both via `.github/docker-dev-config.json`" is a stale count: the file lists five images. | substantive | `README.md:59` | "CI builds the images `.github/docker-dev-config.json` lists." (english-developer-style §7, provenance) |
| F8 | `helm test … --logs` is documented but no target runs it. The repo's `run-suite` streams with `kubectl logs`. Whether `--logs` prints the log of a Job-created pod is unverified (no cluster). `helm test --help` says it dumps "logs from test pods". | substantive | `helm-templates/authz-test-stand/README.md:64` | Run it on a cluster, or document the form `run-suite` uses. (test-authoring §10) |
| F9 | Limits not derived. The Job deadline `activeDeadlineSeconds: 900` equals `helm test --timeout 15m`. Helm's timer starts before the Job exists, so Helm fires first and the Job's own outcome is never reported. The CI kind job has `timeout-minutes: 30`, which encloses image build, harness (`--timeout 10m`), install (2 × 5 min) and suite (15 min). The stated limits add to 35 min. | substantive | `suite.yaml:25`; `values.yaml:99`; `Makefile:102`; `.github/workflows/integration-tests.yaml:120` | Derive the suite's limit from the job budget left after earlier steps. Set the Job deadline below Helm's timeout, or state the job budget. (test-authoring §4, §10) |
| F10 | "It prints the log only at the end" is false for the form used. `helm test` without `--logs` prints no log. | substantive | `Makefile:96` | "It prints no log unless `--logs` is given, so `run-suite` streams the log with `kubectl logs`." |
| F11 | The sentence "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`" is incomplete: the chart imports all four realms of `authn/`, including the two tenant realms the tenant checks use. | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82`; `Dockerfile:27`; `test/k8s/test-stand-values.yaml:82-83` | Name the four, or say "the realms of `authn/`." |
| F12 | No red run on the base commit and no mutation verdict is stated for the pipstub tests. | substantive | commit `9d25da7` | State the red run on the base commit, with the failing output. (test-authoring §1) |
| F13 | "The stub instance itself comes with the cases that use it" reads as delivered. This change adds no instance (`test-stand-values.yaml:17-24` has only pip-stub and entitlements-mock) and no case uses one. | substantive | commit `9d25da7` | State that the instance and its cases are a follow-up, or add them. |
| F14 | The `TAG` comment lists the images the repo builds as pip-stub, parity suite and tenant-manager. It omits `authz-runtime-suite`, which the same tag reaches through `suite.yaml:40`. | substantive | `values.yaml:9-10` | Add the runtime suite to the list. |
| F15 | "A second instance for the entitlements endpoint" and "own image and pull policy below" refer by position where the key has a name. | taste | `test/k8s/test-stand-values.yaml:21`; `values.yaml:11` | Name the instance and the `idp` block. Expect this to be declined. |

**Not checked.** The Go doc-comment and change-description skills were not loaded, since no copies were provided. I ran no cluster, so F1, F2, F3 (admission), F8, and the image user of Keycloak (`runAsNonRoot` needs a numeric user, not confirmed) are unverified. I did not run the `generate` stage in Docker, only its jq steps. The `kubectl wait --for=create` version requirement is unchecked. The drift script produced no output because the change has no JVM files, and the Go, Helm and Makefile comments were checked by reading.
