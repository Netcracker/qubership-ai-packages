Nothing was run: there is no cluster or Docker daemon here, and no file was changed or committed. I read the skill in full. The planned checks are `helm template` renders and `make` runs, so no engine or assertion reference file applies, and I did not open any. The one Go test the commit touches (`test/integration/pipstub/main_test.go`) belongs to the pipstub change, not the move, and is out of scope here.

---

**Test plan for `33acfe1`: the kind harnesses moved to the test-stand chart**

The commit adds no test for the move, so every item below is owed. Levels follow the skill's definitions. **Render** means `helm template` on the chart in a checkout, with no cluster: it reads the chart from disk and runs a process, so it is medium. **Kind** means a real cluster: large.

The render checks belong in `test/scripts/test-chart-render.sh`. CI already runs that script in the `chart` job after `make test-stand-files`. It covers the agent and policy-admin charts but has no test-stand section, so the new section goes there. `AGENTS.md` has no stack line, and I propose none.

**1. Inherited state (kind, a cluster built from `HEAD^`)**

The old `kubectl apply` and `kubectl create` steps made objects with the same names the chart now creates. Helm does not adopt objects it did not create.

- The e2e namespace has these clashes: ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, ServiceAccount and Job `runtime-suite`.
- The parity namespace has these: Deployments and Services `idp`, `pip-mock`, `entitlements-mock`, ConfigMap `pip-mock-config`, the same Secret, and Job `parity-suite`. The old ConfigMap `parity-realms` is left orphaned.
- **Run:** on a kind cluster from `HEAD^`, run `make e2e` and confirm it passes. Then check out this commit and run `make e2e-harness`. Record the output.
- **Expected today:** an install error naming the first clashing object. No make target names a remedy, and `make e2e-down` appears only as cleanup in the docs.
- **Required outcome:** the change either migrates the state or fails naming the remedy. If the remedy is documented, run it on the old cluster and then run the new harness. Do the same for parity.
- A failed install leaves a `failed` release. A second `make e2e-harness` must fail the same way or succeed after the remedy.

**2. Replaced mechanism: the suite wait (kind, from a stand installed by this commit)**

The old path waited with `kubectl wait --for=condition=Ready pod ... --timeout=3m`, then streamed logs, then waited for `Complete` for one minute. The new path waits on `helm test` with its 15-minute timeout, and the Job has `activeDeadlineSeconds: 900`. Run each fault on both `HEAD^` and `HEAD`, and record both durations and both outputs in the PR.

- **(a) A suite test fails.** Set one suite value that makes a case fail, through the stand install's `E2E_HELM_ARGS`, then run `make e2e-suite`. Expected: both exit non-zero, and the new exit code is `helm test`'s.
- **(b) The pod never starts.** Use a suite image that was not loaded into kind, or a pod that the restricted admission rejects. Old: fails at about 3 minutes. New: `wait --for=create` passes, the 180-second loop expires, `logs -f` fails at once, and `wait $helm_pid` blocks on `helm test` until its 15-minute timeout. Expected: the new run fails about 12 minutes later, with no pod state in its output.
- **(c) No stand installed.** `make e2e-suite` on an empty release. Expected: `helm test` fails at once, but the script first waits two minutes on `wait --for=create`. Record the duration and exit code.
- **Fix for (b):** after the loop, if logs still cannot be read, print `kubectl describe pod`, kill `helm_pid`, and exit 1. That bounds the start at the old three minutes and prints more than the old one did.

**3. Render checks (render, no cluster)**

- **R1 Defaults.** `helm template` with no values emits no objects. Control: `idp.enabled=true` with realms present emits the Keycloak objects. Shows that every part is off until a stand turns it on.
- **R2 Object set.** Render the e2e values and the parity values. Compare names and kinds with what `HEAD^`'s manifests and Makefile created. Shows that nothing is dropped or renamed. The one expected difference is `parity-realms`, which becomes `idp-realms`.
- **R3 Environment.** For each old manifest (`HEAD^`'s `runtime-suite-job.yaml`, `parity-suite-job.yaml`, `keycloak.yaml`, `pip-stub.yaml`, `entitlements-mock`, `tenant-manager`), each name and value must match the render. The two `BASE_URL` values are substituted by the make targets, so exclude them. Expected difference: Keycloak no longer sets `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`.
- **R4 Selectors.** Each Deployment's `spec.selector.matchLabels` must equal `app: <name>` from `HEAD^`. Selectors are immutable on upgrade.
- **R5 Secret literal.** The parity password `ParityM2MSecret1!@#` from the values file must render to the same bytes the old `--from-literal` passed.
- **R6 Generated files.** After `make test-stand-files`, `files/realms/e2e` holds the four names from `HEAD^`'s `--from-file` list. `files/realms/parity` holds `cloud-common`, `parity-mt-b`, and `parity`. Each rendered ConfigMap is under 1 MiB. This step needs Docker.
- **R7 Required values.** Each case below must exit non-zero, and its message must name the value or the remedy. Control: the same case with the value supplied must render.
  - `idp` enabled with no realm files, naming `make test-stand-files`.
  - A pip-stub config file missing.
  - `tenantManager` enabled with no tenants.
  - `suite` enabled with an empty `TAG`.
  - `clientCredentials` with no password.
  - `tenantManager` enabled with no `imageRepository`.
- **R8 Realm checksum.** Render twice: the checksum is the same. Change one realm JSON: `checksum/realms` changes. Add a non-JSON file to `files/realms/e2e`: it does not change. The checksum hashes `toString` of the glob result, so this test is what shows it tracks content.
- **R9 Security context.** Every Pod has `runAsNonRoot: true` and the `RuntimeDefault` seccomp profile. Every container has `allowPrivilegeEscalation: false`, drops `ALL`, and has `readOnlyRootFilesystem: true` except Keycloak. No `runAsUser` appears anywhere.
- **R10 Pass-through (skill §3).** `E2E_HELM_ARGS` now reaches the stand install. Both `TAG` and `IMAGE_PULL_POLICY` are read by the agent, the policy-admin, and the stand. With `--set TAG=1.2.3`, the pip-stub, tenant-manager, and suite images must carry `1.2.3`, and Keycloak must keep its pinned digest. With `--set IMAGE_PULL_POLICY=Always`, the stand's images must use `Always`.
- **R11 Packaged chart.** `helm package` the chart after `make test-stand-files`, then `helm template` from the `.tgz`. Keycloak must render with its realms. This shows that `.helmignore` does not drop `files/`.
- **R12 Issuer.** `idp.hostname` (`http://keycloak:8080/auth` for e2e, `http://idp:8080/auth` for parity) must equal the issuer prefix in `test/k8s/values.yaml`'s identity provider URL and in the parity values' trusted-providers entry.

**4. Kind runs (large)**

- **K1 Fresh e2e.** From an empty kind cluster, run `make e2e`. The suite must pass, and its set of PASS and FAIL test names must equal the `HEAD^` run. Check that the CI runner's kubectl supports `wait --for=create` (1.31 or later). The run also covers the suite's temp-dir tests on the read-only root.
- **K2 Fresh parity.** `make parity`, with the same comparison. The parity realm changed, so this run is what shows the parity cases still hold.
- **K3 Restricted namespace.** Label the e2e namespace `pod-security.kubernetes.io/enforce: restricted` before the harness installs. Every stand Pod must become Ready. For each image (Keycloak, pip-stub, tenant-manager, suite), `docker image inspect` must show a numeric `User`, since `runAsNonRoot` rejects a non-numeric name. The agent and policy-admin share the namespace, so their Pods must also pass.
- **K4 Realm change restarts Keycloak.** After K1, change `accessTokenLifespan` in one realm JSON, run `make test-stand-files` and `make e2e-harness`, and check that the Keycloak Pod was replaced. The token response's `expires_in` must change. Control: a second `make e2e-harness` with no change leaves the same Pod running.
- **K5 Restart after the move.** `make e2e-images` followed by `make e2e-restart` must roll the helm-owned Deployments and leave them Ready.
- **K6 Second run.** Run `make e2e-suite` twice. The second run must pass, with no "already exists" error from the hook or the Job.
- **Failure runs.** Section 2 above.
- CI's `kind-e2e` and `kind-parity` jobs run these targets, so the PR's own CI run is the large-level evidence once items 1 and 2 are settled.

**5. Behavior changes to name in the PR description**

- The `OVERWRITE_EXISTING` migration option is dropped from Keycloak.
- The suite Job gets `activeDeadlineSeconds: 900`. The old Job had none.
- Every Pod runs as non-root, with a read-only root filesystem except Keycloak and the `RuntimeDefault` seccomp profile. Images must have numeric users.
- Every object gains the `app.kubernetes.io/*` and `helm.sh/chart` labels. Selectors are unchanged.
- Keycloak is pinned by digest and restarts when a realm file changes.
- The parity realm gains `parity-mt-b` and merged users. The ConfigMap is renamed to `idp-realms`.
- Item 1's remedy is required before anyone upgrades an existing cluster.

I found no existing test whose expectation moved, because none of the repo's tests reach the harness, so the PR has nothing to name there.
