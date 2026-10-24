# Test plan for 2b53abd: the kind harnesses on the authz-test-stand chart

The commit replaces how the harness reaches its state. Before, `kubectl apply` applied loose manifests, `rollout status` waited on each Deployment, and `kubectl wait` watched the Job. Now `helm upgrade --install --wait` installs one release and `helm test` runs the suite. The change also builds the realm and rule files in a Dockerfile stage, adds restricted Pod Security contexts, and sends `E2E_HELM_ARGS` to one more chart. Each of these can change behavior, so the change owes tests.

The only test file the commit adds is `test/integration/pipstub/main_test.go`, which covers the pip-stub change and not the move. I ran nothing: there is no kind cluster or Docker daemon here. Anything below that says what a run will print is an expectation the run has to confirm.

Levels, in the repository's terms:
- **Render checks** run `helm template` in `test/scripts/test-chart-render.sh` (small).
- **Generation checks** run `docker build --target chart-files` (medium).
- **kind runs** use the Makefile targets (large).

Each step below gets the smallest level at which its behavior is visible.

## 1. Starting from a cluster the old harness set up

**State left behind.** Anyone who keeps their kind cluster between runs, as `e2e-restart` and the docs expect, has objects that `kubectl apply` made and that have no Helm ownership labels or annotations.
- **`authz-e2e`:** Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; ConfigMap `keycloak-realms`, which has the same name the chart now renders; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`; Job `runtime-suite`.
- **`authz-parity`:** `idp`, `pip-mock`, `entitlements-mock`, `pip-mock-config`, the same Secret, and Job `parity-suite`. `parity-realms` is left as an orphan.

**Run (large).**
1. Check out HEAD~1 and run `make e2e` and `make parity`.
2. Check out HEAD without `e2e-down` and run `make e2e-harness e2e-install e2e-suite`, then the parity targets.

**What I expect.** `helm upgrade --install` should refuse at once with `… exists and cannot be imported into the current release: invalid ownership metadata`. The commit and the docs promise nothing for this case.

**What the change owes.** Pick one outcome, and the run shows it on that state:
- **It keeps working:** the harness targets delete the old objects, or pass `--take-ownership`.
- **It fails and names the fix:** for example "delete the namespace or run `make e2e-down`". Add that fix to `test/k8s/README.md`, and show it run on the state above.

## 2. `E2E_HELM_ARGS` now also goes to the test-stand chart

`Makefile:86` and `Makefile:150` pass it to the stand. The keys the stand reads that the agent and policy-admin charts also read:
- `TAG`: test-stand `values.yaml:12`; agent `templates/deployment.yaml:153`; policy-admin `templates/deployment.yaml:79`.
- `IMAGE_PULL_POLICY`: test-stand `values.yaml:13`; agent `:154`; policy-admin `:80`.

The documented example, `--set IMAGE_PULL_POLICY=Never`, means the same thing to all three charts, so it proves nothing.

**Render check (small).** Render the stand with `-f test/k8s/test-stand-values.yaml --set TAG=pr123`. That is a value someone passes to run the agent images they loaded under their own tag.

**What I expect.** It renders `local/pip-stub:pr123`, `local/tenant-manager:pr123` and `local/authz-runtime-suite:pr123`. `make e2e-images` only builds `:ci`, so `--wait` would sit for 10 minutes on `ErrImageNeverPull`. That is a bug in the change, not in a test.

**Fix.** Give the stand its own argument, for example a `TEST_STAND_HELM_ARGS`, or stop passing `E2E_HELM_ARGS` to it. After the fix, the same check shows two things:
- `--set TAG=pr123` passed through `E2E_HELM_ARGS` leaves the stand on `:ci`.
- A value passed through the new argument still reaches it.

## 3. The waits that replaced `rollout status` and `kubectl wait` (large runs)

For each fault, report the time to fail and the output, old and new.

**a. A stub image that was never loaded into kind** (start from `e2e-images` without `kind load` for `pip-stub`). This is the fault the old per-Deployment waits handled.
- **Old:** `rollout status deploy/pip-stub --timeout=2m` fails after about 2 minutes and names `pip-stub`.
- **New:** expected to fail after 10 minutes (`--wait --timeout 10m`), and the output should be read for whether it names the Deployment.
- **Owed:** a bound at the old time, or a reason in the PR. Then re-run `make e2e-harness` after fixing the image, to show that `upgrade --install` gets past the failed first release.

**b. A suite Pod that never starts** (skip loading `authz-runtime-suite`). This is the fault on which one wait runs longest.
- **Old:** `wait --for=condition=Ready pod --timeout=3m` fails after 3 minutes, and make stops.
- **New:** `wait --for=create` succeeds. The loop then runs 90 rounds of `kubectl logs` plus `sleep 2`, about 3–4 minutes. `logs -f` fails, and `wait $helm_pid` blocks until `helm test --timeout 15m` gives up, around 15 minutes. That leaves about 15 minutes of a 30-minute CI job.
- `kubectl logs` has no `--request-timeout`, so strictly the loop has no upper bound at all.
- **Owed:** a deadline over the whole step at about 3 minutes, last attempt included, and a message that names the Pod's waiting reason.

**c. A suite that fails** (the common case).
- **Shows:** `make e2e-suite` exits non-zero, after the log has streamed.
- **Control:** a passing run exits 0.
- The same run shows that the CI runner's kubectl accepts `--for=create`, which needs kubectl 1.31 or later.

**d. `make e2e-suite` with no release installed.**
- **Expect:** helm fails at once, but `kubectl wait --for=create --timeout=2m` still waits its full 2 minutes before make fails. Report both times.

## 4. Render checks to add to `test/scripts/test-chart-render.sh` (small)

The script's `fail` keeps going and labels each check with its message (`test-chart-render.sh:51-54`). So one render can carry several checks, as long as each message names its object.

| Check | Inputs | What it shows |
| --- | --- | --- |
| Every address the suites and the agent values use matches a rendered Service and port | Both `test-stand-values.yaml` files. Host:port pairs are written as literals from `suite.env` and from `test/k8s/values.yaml` / `parity/values.yaml` (`keycloak:8080`, `idp:8080`, `pip-stub:8090`, `pip-mock:8090`, `entitlements-mock:8090` for e2e and `:8080` for parity, `tenant-manager:8080`) | Catches a renamed instance or a swapped port, the one thing the deleted manifests pinned by hand |
| The Job has the env vars and args of the old Job | The old Job's names and values, written as literals from `HEAD~1:test/k8s/runtime-suite-job.yaml` and `parity/parity-suite-job.yaml` | Catches a lost or misspelled variable. Expected values come from the earlier version, not from the chart |
| `--set suite.env.BASE_URL=http://authz-agent:8080` renders exactly that | The value the Makefile passes | The `sed` → `--set` move kept the value as it was |
| The Secret is created with exactly the given username and password | Parity values, password `ParityM2MSecret1!@#` | Quoting kept the `!@#` that `--from-literal` used to pass through |
| A missing generated file fails the render with the fix in the message | A copy of the chart without `files/`, with `idp.enabled`; separately, a `pipStub` instance whose `config` names a file that does not exist | The message contains `make test-stand-files`; the lint step's normal render is the control |
| Nothing renders by default | No values | No objects. Control: `idp.enabled=true` renders the idp objects |
| The realm checksum follows the file contents | The same files twice gives the same `checksum/realms`; one realm file changed by one byte gives a different one | The promise that the Pod restarts on a change, and only on a change |
| Every Pod spec meets the restricted profile | All parts on. The check walks every rendered Pod template, not a fixed list | `runAsNonRoot`, `RuntimeDefault`, `drop: [ALL]` and `allowPrivilegeEscalation: false` on every container. It fails for the next part someone adds without them |

## 5. The restricted Pod Security Standard on kind (large)

**Run.** Create both namespaces with `pod-security.kubernetes.io/enforce=restricted`, then run the full `e2e` and `parity` targets.

**Shows.**
- Every Pod is admitted, the suite Job's Pod included.
- pip-stub, tenant-manager and the two suites start with a read-only root filesystem. pip-stub and the suites still run the `qubership-core-base` entrypoint, which the tenant-manager Dockerfile says loads certificates. Only a run shows whether it writes outside `/tmp`.

Put the label into the CI kind jobs, so this stays a standing large test and not a one-off run.

## 6. File generation (medium, `docker build --target chart-files`)

`test/parity/suite/testdata/realm/` is empty today, so nothing exercises the merge or `profile.jq`. Add fixture user files to a temporary copy of the build context, one case each:

**Last-name derivation.** One username per segment type, with expected values from the comment in `profile.jq`:
- `parity-r29-level-m2m` → `R29LevelM2M`
- a plain word segment → capitalized
- a username without the `parity-` prefix

**Other cases.**
- A user who already has `firstName`, `lastName` and `email` keeps them.
- Two users with the same `username` fail the build.
- Two users with the same `id` fail the build.
- **Control:** two users without an `id` pass.
- With no user files at all, the generated `parity-realm.json` equals the source under `jq -S .`.

## 7. Fresh install and the transfer image

**Fresh install (large).** The CI jobs `kind-e2e` and `kind-parity` already cover it. Cite their green run on this commit, linked, in the PR.

**Transfer image (medium).** Build the transfer image and follow steps 1–2 of `helm-templates/authz-test-stand/README.md` on its `/charts`, then `helm lint` and `helm template` the stand with the parity values minus the kind keys.

**Shows.**
- The image carries `files/`, even though `.dockerignore` keeps it out of the build context.
- The default image repositories match the names in `.qubership/docker.cfg`.

## For the PR description

- **Behavior that moved on purpose:**
  - `E2E_BASE_URL` and `PARITY_AC_BASE_URL` now take effect at `*-harness`, so `make e2e-suite E2E_BASE_URL=…` is ignored without warning.
  - Keycloak lost `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`.
  - The parity realms gained `parity-mt-b`.

  No test encoded the old behavior, but the PR should say so in a sentence each.
- **pip-stub:** its new table test includes "a routed path with no responses gets the default answer". Paste its failure on HEAD~1, the index of -1.
- **Proposed stack line for `AGENTS.md`:** "Tests: Go `testing` with testify in the runtime and parity suites; chart renders in `test/scripts/test-chart-render.sh`, whose `fail` continues and names each check by its message; kind runs through the Makefile `e2e-*` and `parity-*` targets." This is a proposal only; no file was edited.
