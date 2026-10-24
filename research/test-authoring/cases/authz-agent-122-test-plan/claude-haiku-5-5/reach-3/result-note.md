I read the skill and `references/go/testing.md`, the only reference the commit's assertion-bearing test needs. I changed no files, committed nothing, and ran nothing: there is no kind cluster or Docker daemon here. What follows is the plan, written to the author of the pull request.

---

**Test plan for `33acfe1`: the kind harnesses on the test-stand chart**

The commit carries three changes: the move to `helm-templates/authz-test-stand`, the `*` default route in pip-stub, and the restricted Pod Security Standard. This plan covers all three.

**What exists.** `test/integration/pipstub/main_test.go` has nine tests, including the default-route and `requestUri` cases. They cover the pip-stub change. Nothing covers the chart, the Makefile move, the generated realm files, the new suite wait loop, or the restricted-PSS settings. The CI addition runs `helm lint` only.

**Stack line (§0).** `AGENTS.md` has no stack line. Proposed for the PR description, not written to the file: *"Tests: Go `testing`, no assertion library, in `test/integration/pipstub`. The Helm chart and the Make harnesses have no unit stack; they are checked by renders and kind runs."*

**Level names.** Small = one process with no network or filesystem. Medium = the local machine, with no cluster. Large = a kind cluster. The Makefile's "e2e" and "parity" names are large.

### A. Renders and generated files (medium, no cluster; run these first)

| # | From state | Inputs | What it shows |
|---|---|---|---|
| R1 | Checkout after `make test-stand-files` | Both `test-stand-values.yaml` files | `helm template` succeeds. Every object keeps its old name (`keycloak`, `keycloak-realms`, `pip-stub`, `entitlements-mock`, `tenant-manager`, the M2M Secret; `idp`, `pip-mock`, `parity-suite` for parity). Keycloak args, pull policy, and Secret keys (`name`, `username`, `password`) are asserted as literals. |
| R2 | Clean clone, no `files/` directory | Same values | Control for R1. The render fails with the message that names `make test-stand-files`. Also one pip-stub instance with `config` and no file. This is the "fails naming the remedy" outcome. |
| R3 | None | The HEAD~1 manifests: `keycloak.yaml`, `pip-stub.yaml`, `entitlements-mock.yaml`, `tenant-manager.yaml`, parity variants, `runtime-suite-job.yaml`, `runtime-suite-rbac.yaml`, and the realm ConfigMap the old Makefile built | Each old object has a new counterpart with the same image, args, env, ports, and `app: <name>` selector. The differences are those the commit names: labels, security context, realm ConfigMap from files, hook annotation. Any other difference is a finding. The old RBAC was a ServiceAccount with no rules and no mounted token; assert the chart's ServiceAccount matches. Reader: T2. |
| R4 | Render with one realm JSON edited in a copy of `files/realms/e2e/` | Control: the same copy with a non-JSON file edited | The `checksum/realms` annotation changes for the JSON edit and not for the control. The checksum hashes `toString` of the Glob result, so the run is what shows it changes at all. |
| R5 | Checkout; `make test-stand-files` (docker, medium), or the same jq 1.8.1 steps run locally | `test/k8s/authn/*-realm.json`, `test/k8s/parity/idp-seed/*`, empty `testdata/realm/` | `files/realms/e2e/` holds the four files the old Makefile listed, byte-identical. `parity-realm.json` equals its input under `jq -S`: jq reformats it, so only layout may differ. `parity-mt-b` lands in `parity/`. `pip-stub/` equals `config/`. |
| R6 | Scratch directory, not the repo | Fixture users for each partition of `profile.jq`: no names or email (`parity-r29-level-m2m` must give `R29LevelM2M`, `parity-r29-level-m2m@example.test`); names already set (kept); no `parity-` prefix; the same username in two files (the build must fail) | Each partition gets what the `profile.jq` header says. No user files exist yet, so this runs only on fixtures. The `jq -e` gates reject duplicates. |
| R7 | Clone at HEAD~1 and HEAD | `authz-agent` and `authz-policy-admin` charts with their e2e values | The rendered output is identical. Neither chart's templates changed, so only the moved `-n` flags could differ. |

R7's claim is that neither chart's output moved; the cheap way to confirm it is a render diff.

### B. Kind runs (large; need Docker, a kind cluster, and `make e2e-images`)

| # | From state | Inputs | What it shows |
|---|---|---|---|
| K1 | Fresh kind cluster | `make e2e` at HEAD~1 and at HEAD | The runtime suite passes the same test IDs in the same count. This is the base-commit comparison: the move changes no behavior. |
| K2 | Fresh cluster | `make parity` at both commits | Same comparison for parity. It exercises `parity-mt-b`, the default route, and `requestUri` through the chart. |
| K3 | Namespace where HEAD~1's `make e2e` ran (objects applied with `kubectl`) | HEAD's `make e2e-harness` | Inherited state. Expected: Helm refuses to adopt objects it did not create, naming the first one. This must be confirmed. Then the remedy, `make e2e-down` followed by `make e2e`, is run on this same state and must pass. The PR must document that remedy; `docs/local-integration-tests.md` is the place. If the author prefers migration, this test changes. Repeat for the parity namespace. |
| K4 | Stand installed by K1 | `make e2e-harness` unchanged; then with one realm JSON edited. Control: a non-JSON edit | Unchanged input: Keycloak keeps its pod UID. Edited input: Keycloak restarts and imports the edited realm. Then a second `make e2e-suite` passes, showing the hook is recreated. |
| K5 | Stand installed | `make e2e-harness E2E_BASE_URL=http://nowhere:8080`, then `make e2e-suite` | The suite fails on purpose. The log streams, `make` exits non-zero, and helm's status comes back through `wait $helm_pid`. Compare exit code, log, and duration with the base commit on the same failure. The URL goes in at harness time, because `e2e-suite` no longer sed-substitutes it. |
| K6 | Stand installed, `local/authz-runtime-suite:ci` not side-loaded | `make e2e-suite` | Replaced-mechanism fault, where one attempt waits longest. At HEAD~1 this fails in about 3 minutes at `wait --for=condition=Ready`. At HEAD, `kubectl wait --for=create` passes, the poll loop gives up after about 3 minutes, and `wait $helm_pid` blocks on `helm test`. That runs until the Job's `activeDeadlineSeconds` (900) or helm's 15-minute timeout. Expected: the new one fails later. Per §3, bound the whole wait at the old time to fail, and state both durations and both outputs in the PR. Also confirm the kubectl the harness uses supports `--for=create`. |
| K7 | Fresh namespace labelled `pod-security.kubernetes.io/enforce=restricted` | The e2e stand install. Control: HEAD~1's `kubectl apply` manifests into the same labelled namespace | Every test-stand Pod is Ready, Keycloak starts with a writable root filesystem, and the suite Job completes using the `/tmp` emptyDir. The control must be rejected by admission, which proves the label is enforced. No OpenShift SCC run is possible here, so the no-`runAsUser` claim stays unverified until someone runs on OpenShift. |
| K8 | Stand not installed | `E2E_HELM_ARGS='--set IMAGE_PULL_POLICY=Never'` (the documented example), and `--set TAG=other` | `E2E_HELM_ARGS` now reaches the test stand too. Both keys are read by the suite, pip-stub, and tenant-manager, and `TAG` by the agent chart as well. The `IMAGE_PULL_POLICY` example should show a sensible effect (render, medium). `TAG=other` makes the stand request images nothing built, so it fails at pull (kind). Decide: give the stand its own setting, or document that the flag reaches it. |

### Order and gaps

1. R1–R7 (no cluster), then K1 and K2 for the baseline.
2. K3, K5, K6, K7, K8, with K4 after the baseline. K3 and K6 are the slow ones.

Not covered by any run here: OpenShift, and the tenant-manager emulator's behavior beyond what the suites exercise.

The commit body names three changes, and the PR should say which test covers which. Only the pip-stub change has tests today.
