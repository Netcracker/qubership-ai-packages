I've written the plan from the last commit (026520b) without running anything, changing any file, or using gh, a browser, or curl.

One fact about this repository's own test harness, for you alone: `test/scripts/test-chart-render.sh` reports every failed check and names each one by its message. `fail()` at line 51 counts the failure and carries on, and the script exits non-zero only at the end (line 1002). Should I add that to `AGENTS.md` as a line describing the test stack? I'll only edit the file if you say yes.

Here is the plan, written as the message for the pull request's author:

---

**Test plan for "run the kind harnesses on a test-stand chart with stock Keycloak"**

**Already covered.** On this pull request, the CI jobs `kind-e2e` and `kind-parity` (`.github/workflows/integration-tests.yaml`) are the large tests of a fresh install that passes. They cover a new cluster, the chart installed with each values file, and each suite run through `helm test`. The pip-stub default route is covered by the three new tests in `test/integration/pipstub/main_test.go`. Everything below is what the move still owes. "Render" means a medium test added to `test/scripts/test-chart-render.sh`, next to the existing chart checks. "Kind run" means a run you make once, with its output pasted into the pull request.

**1. Show that the move kept the stand the same (one-time run, medium).**
- **Starting state:** a checkout of this commit after `make test-stand-files`.
- **Inputs:** `helm template` with each values file, plus the `--set suite.env.*` that the Makefile passes. Compare with the deleted manifests from `git show HEAD~1:test/k8s/...`, and with the old ConfigMaps and Secret, which you can regenerate from the old Makefile lines using `--dry-run=client -o yaml`.
- **Compare each workload:**
  - Service names and ports
  - image and pull policy
  - container env (name and value)
  - args and probes
  - volume mounts
  - Job `backoffLimit`, `activeDeadlineSeconds`, `restartPolicy` and `serviceAccountName`
- **Compare the data:**
  - the keys and contents of the realm ConfigMap
  - `pip-mock-config`
  - the decoded Secret: `password` must be exactly `ParityM2MSecret1!@#`, and `name=authz-agent`
- **What it shows:** paste the diff and account for each line that differs. These differences should appear, and nothing else:
  - the labels, security contexts and the `checksum/realms` annotation
  - `--health-enabled` is now `KC_HEALTH_ENABLED`
  - the e2e Keycloak loses `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`
  - the image is pinned by digest
  - the parity realm ConfigMap is renamed to `idp-realms` and gains `parity-mt-b-realm.json`
  - the parity `entitlements-mock` container is renamed from `entitlements-mock` to `pip-stub`
- **Not a permanent test:** keeping literals copied from the values files in the render script would only detect that the values files changed.

**2. Start from what the old harness left behind (§3, kind run).** CI always starts from a fresh cluster, so it never tests this case. A developer's cluster does.
- **Starting state:** check out `HEAD~1` and run `make e2e-cluster e2e-images e2e-harness e2e-install e2e-suite` and `make parity-harness parity-install parity-suite`. This leaves objects that `kubectl apply` created, with no Helm ownership metadata:
  - Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`
  - ConfigMap `keycloak-realms`
  - Secret `authz-agent-client-credentials`
  - ServiceAccount `runtime-suite`
  - Job `runtime-suite`
  - in the parity namespace: `idp`, `pip-mock`, `entitlements-mock`, `pip-mock-config` and `parity-realms`
- **Then:** check out this commit and run `make e2e-harness e2e-suite` and `make parity-harness parity-suite`.
- **What I expect:** Helm refuses to install with "invalid ownership metadata" on the first of those objects. Nothing in the docs names a remedy except `make e2e-down`, which deletes the whole cluster.
- **What is owed:** pick one outcome and show it run on this state:
  - **Remedy:** document `make e2e-down` (or `kubectl delete ns`), then run it and a green `make e2e` / `make parity`.
  - **Adoption:** `E2E_HELM_ARGS=--take-ownership`, run to a green suite. Also check that after the upgrade, the parity `entitlements-mock` Pod has exactly one container, named `pip-stub`. A container renamed while Helm takes over a client-side-applied Deployment can leave the old container in place as well. `parity-realms` is left behind but harmless.

**3. Values meant for the other charts now reach the stand through `E2E_HELM_ARGS` (§3, render, then kind run).**
- **Names that the test stand and the old consumers both read:**
  - `TAG`: `helm-templates/authz-agent/templates/deployment.yaml:153`, `authz-policy-admin/templates/deployment.yaml:79`, and in the stand `pip-stub.yaml:40`, `suite.yaml:40`, `tenant-manager.yaml:34`
  - `IMAGE_PULL_POLICY`: agent `:154`, policy-admin `:80`, and in the stand `pip-stub.yaml:41`, `suite.yaml:41`, `tenant-manager.yaml:35`
- **Inputs:** render the stand with `-f test/k8s/test-stand-values.yaml --set TAG=1.4.0`. That is what someone passes to test a published agent version.
- **Assert:** the pip-stub, suite and tenant-manager images. Today they render as `local/pip-stub:1.4.0`, which `make e2e-images` never builds, so the harness waits out its 10 minutes.
- **Second case:** `--set IMAGE_PULL_POLICY=Always`. Assert that the Keycloak `imagePullPolicy` is still `IfNotPresent`, because it has its own key.
- **Why not the documented example:** `--set IMAGE_PULL_POLICY=Never` means the same thing to every chart, so it settles nothing.
- **If you fix it by keeping `E2E_HELM_ARGS` away from the stand:** add the control case. `--set suite.env.BASE_URL=http://x:1` from `E2E_BASE_URL` must still reach the Job's env.

**4. The checksum restarts Keycloak exactly when a realm file changes (render).**
- **Case:** copy the chart to a temporary directory, change one byte of `files/realms/e2e/authz-test-realm.json`, and render `checksum/realms` (`idp.yaml:35`) before and after. Assert that the two values differ.
- **Second case:** add a new `*-realm.json` file and assert the checksum changes.
- **Control:** render twice with nothing changed and assert the checksum is the same.
- **Kind run for the docs claim:** edit a realm (add a user), run `make e2e-harness`, and show that the Keycloak Pod UID changed and the new user gets a token. Then rerun `make e2e-harness` with no change and show the Pod UID stays the same, so the realm keys don't rotate.

**5. Error paths of the chart (render, one invalid input per check).** For each, assert that the render fails and that the error names its remedy:
- `idp.enabled` with no `files/realms/<realms>/` fails with `run \`make test-stand-files\``. Use a chart copy without `files/`.
- A pip-stub instance whose `config` names a missing file fails with `no file files/pip-stub/<file>`. Control: the same instance without `config` renders.
- `tenantManager.enabled` with no tenants fails with `tenantManager.tenants is required`.
- An empty `TAG` fails with `TAG is required`.

**6. The new waits fail on time and say why (§3, kind runs).** Inject each fault on a running stand. Each kind run below injects one fault; state both durations and both outputs in the pull request.
- **The harness wait.** The old code ran `rollout status` on each Deployment: 2 minutes for each stub, 10 for Keycloak. The new code runs one `helm --wait --timeout 10m` (Makefile:86, :150).
  - **Fault:** a stub image that isn't loaded, via `--set pipStub.imageRepository=local/missing`.
  - **Old:** fails at about 2 minutes with `deployment "pip-stub"` named in the output.
  - **New:** expect about 10 minutes. Record what Helm 4 prints.
  - Also run a Keycloak that never becomes ready, via a broken realm file: both versions should fail at about 10 minutes.
  - **Then:** fix the fault and rerun `make e2e-harness`. Show that it succeeds over the failed release without `helm uninstall`. `kubectl apply` never had this problem.
- **The suite wait: the fault the old code met most often, a failing test.** Inject it with `helm upgrade --reuse-values --set suite.env.KC_PASSWORD=wrong`.
  - **Old:** streamed the log, then waited the full minute for `Complete`, then failed with "timed out waiting for the condition on jobs/runtime-suite".
  - **New:** `helm test` should return as soon as the Job fails, with a non-zero exit. Show the exit code, the elapsed time, and that the log appears in the output.
- **The suite wait: the fault on which one attempt waits longest, a suite Pod that never starts.** Inject it with `suite.imageRepository=local/missing`.
  - **Old:** failed at 3 minutes on the `Ready` wait.
  - **New, counted from Makefile:101–106:**
    - `wait --for=create` succeeds at once.
    - The `logs` loop takes 90 × (one `kubectl logs` + 2 seconds), at least 3 minutes. Nothing sets `--request-timeout`, so an API server that stops answering makes this unbounded.
    - `logs -f` fails at once.
    - `wait $helm_pid` then blocks until `helm test --timeout 15m` or the Job's `activeDeadlineSeconds: 900` runs out.
  - **Expected:** about 15 minutes against the old 3.
  - **What is owed:** either a deadline that stops `helm test` once the Pod hasn't started within the old 3 minutes, or a reason in the pull request. If it prints less than the old wait did, also print the Pod's waiting reason, for example with `kubectl get pod -l job-name=…`.

**7. Limits on the suite Job (§4).** Four limits now bound the same Job:
- `-test.timeout 600s` (`values.yaml:95`)
- `activeDeadlineSeconds: 900` (`values.yaml:99`)
- `helm test --timeout 15m`, hard-coded in Makefile:102
- the CI job's `timeout-minutes: 30`

Cases:
- **Defaults:** assert, by citing the configured values, that the Go timeout fires first. A hung suite should end in Go's "test timed out after 10m0s" panic in the streamed log, not in a Helm timeout.
- **900 seconds against 15 minutes:** the two limits are equal, so whichever fires first wins a race, and the user sees a different message depending on which. Helm's clock also starts before the Pod is scheduled.
- **Changed limit past the fixed one:** `--set suite.activeDeadlineSeconds=1800` makes `helm test` give up at 15 minutes while the Job keeps running. The values file documents this setting as configurable, so the defect is the fixed 15 minutes in the Makefile and in the README's `helm test` line. Derive the Helm timeout from the same value, or document the limit.

**8. The restricted Pod Security Standard (kind run; CI doesn't test this).** `--create-namespace` adds no `pod-security` label, so CI never checks the claim.
- **Run:** install the stand alone into a namespace labelled `pod-security.kubernetes.io/enforce=restricted`, for example with `helm install --wait`, then run `helm test`.
- **Expected:** every Pod, the suite Pod included, is admitted, and the suite passes.
- **Red on the base commit:** the `HEAD~1` manifests applied there are rejected, and the warnings name the missing fields.
- The full green runs of `kind-e2e` and `kind-parity` show that the read-only root filesystem breaks no test.
- **Silent loss to state:** the parity suite's `.observed.json` sidecar (`test/parity/suite/compare.go:146`) now fails to write and nothing reports it.

**9. Generated files (medium: `docker build --target chart-files` on a temporary directory laid out like the repository, using the real Dockerfile).**
- **No user files (today's state):** `parity-realm.json` in the output equals `idp-seed/parity-realm.json` when both are compared with `jq -S`.
- **One user file with a user who has no profile fields:** the user is in the realm with first name, last name and email.
  - Take the expected values from the stand the goldens were recorded on. Example: `parity-r29-level-m2m` → `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test`. Don't take them from what `profile.jq` produces.
  - Add a case for a username without the `parity-` prefix where the recorded stand has one. Where it doesn't, the expected value is open: say so.
- **A user that declares all three fields:** keeps them.
- **The same username in two files:** the build fails. Do the same for the same `id`.
- **Control:** two different users, and two users with no `id`, both build.

**10. The transfer image and its README procedure (medium, Docker).**
- **Build:** `build/authz-agent-transfer/Dockerfile`, with a stale `helm-templates/authz-test-stand/files/realms/e2e/stale-realm.json` left in the checkout.
- **Assert, in one listing:**
  - `/charts/authz-test-stand/files/realms/e2e/` holds exactly the four realms of `test/k8s/authn/`, so `.dockerignore` keeps the stale file out
  - `files/realms/parity/` holds three realms
  - `files/pip-stub/requestargs.responses.yaml` is present
- **Then follow README steps 1–2 literally:** `docker cp`, then the parity values with `TAG`, `IMAGE_PULL_POLICY` and both `imageRepository` keys deleted, plus `--set TAG=1.4.0`. `helm template` must render `ghcr.io/netcracker/qubership-authz-pip-stub:1.4.0` and `…-parity-suite:1.4.0`.
- **Release:** a dry run of `docker-release.yaml` builds the three new images for both platforms.

**11. Changed documented procedure (kind run).**
- **Run:** follow the subset recipe in `docs/local-integration-tests.md`: `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` with `FULL_RUNTIME_SUITE=false`, then `make e2e-suite`.
- **Expected:** the log shows only `TestCheckResource`.
- **Then:** `make e2e-harness` restores the full run.

A failing pull request needs four things: items 4 and 5 in the render script, the item 1 diff, the item 2 outcome, and the item 6 durations and outputs. Items 3 and 7 point at defects to fix or document rather than tests to add.
