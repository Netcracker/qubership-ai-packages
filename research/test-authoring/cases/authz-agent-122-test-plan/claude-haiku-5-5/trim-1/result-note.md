I read the skill, `go/testing.md` and `go/testify.md`, and the harness files at HEAD and HEAD~1. I ran nothing and changed no file.

**Message for the author of the pull request**

This change moves the kind harnesses from `kubectl apply` to `helm-templates/authz-test-stand` and adds no test for the move. What it owes, by the test-authoring rules:

**Stack (proposed, not added to `AGENTS.md`):** Go `testing` with testify for the Go suites; the chart and generate-stage checks as shell scripts beside `test/scripts/test-chart-render.sh`, run with helm and jq 1.8.1 (the version the transfer image pins), with the same fail-counter-and-continue shape. No reference file covers helm or make, so those checks take their report from the tools themselves.

Levels follow §3: "medium" means it uses the local machine (helm, jq, docker). "Large" is what the Makefile calls e2e.

**Owed now, no cluster needed**

1. **Render: a stand with nothing turned on renders nothing.** Medium. Inputs: no values file; then `test/k8s/test-stand-values.yaml`; then `test/k8s/parity/test-stand-values.yaml`. Assert: with no values, nothing is rendered. With the e2e values, exactly Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMaps `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`; Job `runtime-suite` carrying `helm.sh/hook: test`; every selector `app: <name>`. Fails when a part renders by default, when the hook annotation goes (the suite would then start on every install), or when a selector drifts from `app: <name>`, which the Makefile's `deploy/<name>` lookups depend on.

2. **Missing realm files fail with the remedy.** Medium. Input: a copy of the chart with `files/` empty and `idp.enabled` true. Assert: the render fails and the message contains `make test-stand-files`. The control is item 1 with the files present. Fails when the guard in `idp.yaml` is removed and Keycloak starts with no realms and no error.

3. **Checksum follows content.** Medium. Render a temporary copy of the chart twice with identical realm files, then once with one realm file edited. Assert the identical renders give the same `checksum/realms` and the edited one differs. Fails when the hash covers file names but not content, so an edited realm never restarts Keycloak.

4. **Restricted Pod Security on the rendered manifests.** Medium. Inputs: both stand values files. Loop over every Pod and every container in the render, and report each failure with the container's name (§7, principle 1). Assert `runAsNonRoot: true` and `seccompProfile: RuntimeDefault` on each Pod. On each container assert `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, and `readOnlyRootFilesystem: true`, except Keycloak, which must be `false`. The Keycloak case is the control that the exemption belongs to Keycloak alone. This checks the properties; R3 checks admission.

5. **The realm profile fills what a password grant needs.** Medium, with jq 1.8.1 and fixtures. Expectations are literals derived from the rules in `profile.jq`, not pasted from jq's output. `parity-r29-level-m2m` with no names gives firstName `Parity`, lastName `R29LevelM2M`, email `parity-r29-level-m2m@example.test`. A user that already sets firstName keeps it. Control: unique usernames pass the `jq -e` guard, and two users with one username fail it. Fails when the letter-plus-digit or `m2m` branch is wrong or a guard is removed. Note: `test/parity/suite/testdata/realm/` holds only a README, so `profile` runs on no user today and this test is its only check.

6. **With no user files, the parity realm is unchanged.** Medium. Compare `jq -S .` of the generated `parity-realm.json` with `test/k8s/parity/idp-seed/parity-realm.json`, and `cmp` the copied e2e files. Expected: identical. Fails when the transform rewrites a field (number format, a dropped key), which would change the parity realm on every run.

**Owed on kind (large; not runnable here)**

- **R1. The move keeps suite outcomes.** On a fresh cluster, run `make e2e` on HEAD and on HEAD~1 (the kubectl-apply path). Assert the `--- PASS/FAIL/SKIP` lines of the two suite logs are the same set, and that the `m2m_keycloak` steps are not SKIP (`M2M_KEYCLOAK_PROFILE` is on). Also check the hook: after `make e2e-harness` alone, no `runtime-suite` Job or Pod exists. Repeat with `make parity`, which should also show `parity-mt-b` imported.

- **R2. A changed realm reaches Keycloak; an unchanged one does not restart it.** On a running stand, change one claim value in an `authn/` realm file and run `make e2e-harness`. Assert the Keycloak Pod is replaced and a token carries the new claim. Run it again with no change and assert the Pod name stays. Fails when the checksum is stale or the import is ignored.

- **R3. Restricted Pod Security admits the stand, and the suite passes under it.** Run `kubectl label namespace authz-e2e pod-security.kubernetes.io/enforce=restricted --overwrite`, then `make e2e-harness`, `make e2e-install`, `make e2e-suite`. Also check that the Keycloak image's user is numeric: `docker image inspect quay.io/keycloak/keycloak:26.3.5 --format '{{.Config.User}}'`. `runAsNonRoot` refuses a non-numeric name. The repository's own images run as 10001:10001. If the agent install is refused under `restricted`, the PR narrows its claim to the stand. Fails when admission rejects a Pod (the event names the field) or the suite writes outside `/tmp`.

- **R4. Inherited state: a cluster the manifests built.** Start from HEAD~1's `make e2e-harness` and `make e2e-suite` on a live cluster, and `make parity` for its namespace. Then run HEAD's `make e2e-harness`. Expected: Helm refuses to adopt the pre-existing objects (`invalid ownership metadata`), starting with Deployment `keycloak`, which the commit does not mention. Per §3 the change owes the documented remedy, run on this state. `make e2e-down` is documented (`docs/local-integration-tests.md:193`, `test/k8s/README.md:44`). Either the PR says so and the run shows `make e2e` passing afterwards, or the chart adopts the objects. Note that `make e2e-down` deletes the whole cluster, including `authz-parity`; no parity target does the same.

- **R5. A failing case fails the harness, and an empty run does not pass.** (a) Set a value a case reads wrong, such as `E2E_HELM_ARGS='--set suite.env.KC_PASSWORD=wrong'`. `make e2e-suite` must exit non-zero, and the log must name the failed test. (b) Set `--set suite.env.RUNTIME_SUITE_RUN=^NoSuchTest$`. I believe Go exits 0 when `-test.run` matches nothing, so the Job completes and the harness passes with zero tests. The PR must either assert that the log contains `--- PASS: TestRuntimeSuite`, or count the tests run.

- **R6. The replaced waits, each fault run on HEAD~1 and on HEAD, with both durations and both outputs in the PR (§3).**
  - **F1, suite image absent** (no `local/authz-runtime-suite:ci` loaded; `IMAGE_PULL_POLICY: Never`). Old: `kubectl wait --for=condition=Ready ... --timeout=3m` fails at about 3 minutes. New: `wait --for=create` passes, the 90-iteration loop runs about 180 seconds, `logs -f` fails, and `wait $helm_pid` returns only when `helm test` exits. That happens at the Job's `activeDeadlineSeconds`, 900 in `helm-templates/authz-test-stand/values.yaml`, which the e2e values do not override. So the new one fails about 12 minutes later. Bound it at the old 3 minutes, or give a reason.
  - **F2, a stub never Ready** (a `pip-stub` image tag absent). Old: `rollout status deploy/pip-stub --timeout=2m` fails at 2 minutes. New: one `helm --wait --timeout 10m` covers every part, so about 10 minutes. Bound the stubs at 2 minutes or give a reason. Check that Helm's error names the Deployment that is not ready and its last state (§8).
  - **F3, an API call that never returns.** Pause a kind node container once a suite Pod runs. `kubectl logs` has no request timeout by default, so one attempt can outlast the loop's 180-second budget. The old `logs -f` had no bound either. Measure how long a call takes to give up, and set `--request-timeout` on each call so the loop's bound holds.

- **R7. The value users pass reaches the stand.** `E2E_HELM_ARGS` goes to the stand, agent, and policy-admin installs. Both consumers read two names: `TAG` (`authz-test-stand/values.yaml:12`, `authz-agent/values.yaml:5`, `authz-policy-admin/values.yaml:5`) and `IMAGE_PULL_POLICY` (`:13`, `:88`, `:50`). Run (a) `--set IMAGE_PULL_POLICY=Never`, the Makefile's documented example: the stand's images get `Never`, and Keycloak keeps `idp.imagePullPolicy`. Run (b) `--set TAG=<a release tag>`, as a user would for the agent: `helm template` shows the stand's images at that tag, which `e2e-images` never builds, so the stand cannot pull. The PR must decide: the stand keeps `ci`, or every chart install takes the same tag and the PR says so.

**Changed behavior to confirm in the PR**

- The old Keycloak manifest set `JAVA_OPTS_APPEND` (`test/k8s/keycloak.yaml:38`); `idp.yaml` does not. Say whether that was dropped on purpose.
- The M2M values moved from the deleted `test/k8s/authn/m2m-credentials/` files into `test-stand-values.yaml`. They match (`test-app-client`, `test-app-secret`), and R1's `m2m_keycloak` steps check them.
- The restricted-PSS paragraph of the commit message has no test; it is item 4 and R3.
- The pip-stub default-route paragraph has its own file, `test/integration/pipstub/main_test.go`. I did not assess it.

**Not owed:** a coverage figure (§1). A mutation run, since no mutation tool is configured for charts or make. `helm lint` in CI is a parse check, not a test of behavior; it stays as it is.

**Not checked here:** the kind runs and the Docker builds (no daemon), the exact Helm ownership message, the Keycloak image's user, kubectl's default request timeout (I believe it is unlimited), and Go's exit status when no tests match (I believe 0). Each is one command on the stand.
