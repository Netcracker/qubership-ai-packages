# Test plan for "run the kind harnesses on a test-stand chart"

I wrote this after reading the diff. I also checked a few things without a cluster: `make -n` on the new targets, and `helm template` (Helm 4.3.0) on a copy of the chart in my scratchpad, with the realm and rule files copied in by hand. I changed no file in the repository. Durations marked "by count" are my arithmetic from the timeouts and still need the run.

**What already covers the change:** `kind-e2e` and `kind-parity` in `integration-tests.yaml` install the chart on a fresh cluster and run both suites green. They also cover the read-only root filesystems, `runAsNonRoot` (the kubelet enforces it anyway), the new `parity-mt-b` realm import, and the M2M Secret matching the realms. The pipstub default-route change has its own tests in `test/integration/pipstub/main_test.go`. The items below are what those runs cannot show: none starts from an earlier harness, none makes the harness fail, and none runs in a namespace that enforces the restricted Pod Security Standard.

## 1. Starting from a cluster the old harness set up (large, a run)

A developer's kind cluster still has the objects that `kubectl apply` created. Helm will not adopt objects without its ownership metadata, so I expect `make e2e-harness` to stop with `… exists and cannot be imported into the current release: invalid ownership metadata`. These names collide:

- **`authz-e2e`:** ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`, and the Deployment and Service of `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`.
- **`authz-parity`:** ConfigMap `pip-mock-config`, Secret `authz-agent-client-credentials`, and the Deployment and Service of `idp`, `pip-mock` and `entitlements-mock`. The old ConfigMap `parity-realms` would be left behind, because the new one is `idp-realms`.

- **Run:** check out `HEAD~1` and run `make e2e` and `make parity`. Then check out this commit and run `make e2e-harness e2e-install e2e-suite`, and the same three targets for parity.
- **Shows:** what this state does to the harness. The change promises no outcome for it today. Either automate the takeover, or document a remedy in `docs/local-integration-tests.md` §8 (for example, delete the namespace or run `make e2e-down`) and show that remedy run on this state.

## 2. The replaced wait in `e2e-suite` / `parity-suite` (large, runs of the failure paths)

The old target waited at most 3 minutes for the Job's Pod to be Ready, then failed with `timed out waiting for the condition on pods/runtime-suite-…`. For each fault below, run it on `HEAD~1` and on this commit, and put both durations and both outputs in the PR.

1. **Job Pod stuck on `ErrImageNeverPull`.** The docs' troubleshooting table lists this as the usual failure.
   - Input: `--set suite.imageRepository=local/missing` on the stand (on `HEAD~1`, the same image name in the Job manifest).
   - By count: each `kubectl logs` fails at once, so the loop ends after about 3 minutes. `logs -f` then fails too, and `wait $helm_pid` blocks until `helm test --timeout 15m` or the Job's 900 s deadline. That is about 15 minutes, against 3 before.
2. **The Job exists but no Pod is ever created.** This is where one attempt waits longest. Inputs: a ResourceQuota that admits no Pod, or a Pod Security violation in an enforcing namespace.
   - `kubectl logs job/…` waits `--pod-running-timeout` (20 s by default) for a Pod on every attempt. By count that is 90 × (20 s + 2 s) ≈ 33 minutes, plus 20 s for `logs -f`. The CI job's `timeout-minutes: 30` kills it first.
   - The comment "polls for up to three minutes" does not hold here. The wait needs a deadline over the whole loop at the old 3 minutes, last attempt included, or a stated reason.
3. **A release with no test hook** (`--set suite.enabled=false`).
   - By my reading, `kubectl wait --for=create` fails after 2 minutes, `logs -f` fails, and the target exits with `helm test`'s status. That status is 0 when the release has no tests.
   - The run shows whether `make e2e-suite` goes green without running any suite. The expected outcome is a non-zero exit that names the missing Job.
4. **A suite that fails on purpose.** This shows the harness can go red, which no run so far has shown.
   - Inputs: `RUNTIME_SUITE_RUN` set to a test that fails, or `suite.env.BASE_URL=http://nowhere:1`.
   - Expected: the log streams, and `make e2e-suite` exits non-zero. Repeat with `PARITY_AC_BASE_URL` for parity.

## 3. The replaced wait in `e2e-harness` / `parity-harness` (large, runs of the failure paths)

The old target ran `rollout status` with 2 minutes per stub and 10 minutes for Keycloak, and each failure named the Deployment. The new one is a single `helm --wait --timeout 10m` over everything.

- **Fault A, a stub image missing from the node:** the old harness failed in 2 minutes at `deploy/pip-stub`. The new one should take 10 minutes; record what Helm prints and whether it names the Deployment.
- **Fault B, Keycloak never Ready** (an unpullable `idp.image`): 10 minutes in both. Record both outputs.
- **Docs:** the troubleshooting row still cites `rollout status deploy/keycloak`. Replace it with what the new run prints.

## 4. `E2E_HELM_ARGS` now reaches the test stand (medium, in `test/scripts/test-chart-render.sh`)

**Names both consumers read:**
- `TAG`: the agent's `values.yaml:5`, the stub chart's `values.yaml:5`, and the stand's `values.yaml`.
- `IMAGE_PULL_POLICY`: the agent's `:88`, the stub chart's `:50`, and the stand's.

The documented example, `IMAGE_PULL_POLICY=Never`, means the same to every chart, so it settles nothing. `TAG` does not. I rendered `-f test/k8s/test-stand-values.yaml --set TAG=dev` and got `local/pip-stub:dev`, `local/tenant-manager:dev` and `local/authz-runtime-suite:dev`. `e2e-images` builds only `:ci` and the pull policy is `Never`, so a user who retags the agent build now gets a harness that times out after 10 minutes.

- **Case:** that render, asserting the image list you intend.
- **If you keep the value away from the stand** (for example, with a separate variable): the case falls silent, and it owes a control. A tag given through the stand's own channel still reaches it.

## 5. `E2E_BASE_URL` / `PARITY_AC_BASE_URL` no longer reach `*-suite` (a decision, then docs or a check)

`make -n e2e-suite E2E_BASE_URL=http://elsewhere:9999` prints no such URL. The value is now applied at `e2e-harness` (`--set suite.env.BASE_URL`), so `make e2e-suite E2E_BASE_URL=…` runs against the default without saying so. Either document that it is set at harness time, or pass it at suite time and show it arriving with the same `make -n`.

## 6. Render cases for the chart (medium, beside the existing ones in `test-chart-render.sh`)

These use the file's `fail`/`pass` helpers. The CI `chart` job already runs `make test-stand-files` first. Each expected value is a literal.

- **Defaults:** every part is off, so the render produces no objects. I checked this: 0 objects.
- **Generated files missing:**
  - `idp.enabled`: the render fails with `no realm files under files/realms/e2e/: run \`make test-stand-files\`…`. I checked this message.
  - A pip-stub instance with `config`: the render fails with `no file files/pip-stub/<file>`.
  - Control for both: the same values render once the files exist.
- **Required values, one test each:** `TAG`, `clientCredentials.username`, `clientCredentials.password`, `tenantManager.tenants`, `tenantManager.imageRepository`, `pipStub.instances.<name>.port`.
- **Parity Secret:** the password renders as `ParityM2MSecret1!@#`. The old Makefile passed this value as a shell literal; it is now plain YAML. I checked that it renders correctly.
- **Realm ConfigMap keys:** the four e2e file names for `realms: e2e`, and the three parity names including `parity-mt-b-realm.json` for `realms: parity`.
- **`checksum/realms`:**
  - It changes when one realm file changes; I saw it change on my copy.
  - It stays the same when nothing changes.
  - It stays the same when only a pip-stub rule file changes.
  - These are three tests.
- **pip-stub instances:**
  - With `config` (`pip-mock`): the ConfigMap, `PIP_STUB_CONFIG` and the volume are rendered.
  - Without it (`pip-stub`): none of the three.
- **Suite env:** `--set suite.env.FULL_RUNTIME_SUITE=false` and a numeric value both render as quoted strings, and `$(RUNTIME_SUITE_RUN)` in `suite.args` stays literal.

Do not assert the security contexts field by field: that restates the template. Item 8's run is the oracle for them.

## 7. That the move preserved the parts (a one-time run, results in the PR, not kept as a test)

Render both values files and compare each object with its deleted manifest from `HEAD~1`: image, args, env, ports, probes, resources and selector.

Expected differences, each named in the PR:
- labels and security contexts;
- the Keycloak image pinned by digest;
- `--health-enabled` replaced by `KC_HEALTH_ENABLED`;
- `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` dropped from e2e, with a sentence on why a fresh dev-mode database makes it unnecessary;
- the parity realm ConfigMap renamed, and the added `parity-mt-b` realm;
- env order now alphabetical.

Anything else is a defect.

## 8. The restricted Pod Security Standard (large, a run)

`--create-namespace` labels nothing, so CI never enforces the restricted standard.

- **Run:** create `authz-e2e` and `authz-parity` with `pod-security.kubernetes.io/enforce=restricted`, then run `make e2e` and `make parity`. Every Pod should start and both suites should pass.
- **Red on the base commit:** `HEAD~1`'s harness in the same namespace should be rejected with `violates PodSecurity "restricted…"`.
- **OpenShift:** the PR describes behavior under OpenShift's restricted SCC, which none of these runs checks. Say so in the PR.

## 9. Keycloak restarts when a realm changes (large, a run)

After a green `make e2e`:
- **Case:** add a user to `test/k8s/authn/authz-test-realm.json` and run `make e2e-harness`. The Keycloak Pod's UID changes, and the new user gets a token. Then follow the documented agent restart (docs §6); `make e2e-suite` should be green.
- **Control:** run `make e2e-harness` again with nothing changed. The Pod UID stays the same. Otherwise every rerun of the harness rotates the realm keys and breaks the agent, as §6 warns.

## 10. Generating the files

- **Small, a new script beside the others in `test/scripts/`:** load `profile.jq` with `jq -L build/authz-agent-transfer 'include "profile"; …'` and run it on users written as literals. I checked that this loads locally.
  - A user with no names gets `Parity`, `R29LevelM2M` and `parity-r29-level-m2m@example.test` (the example in the Dockerfile's comment).
  - A declared `firstName`, `lastName` or `email` is kept.
  - A username without the `parity-` prefix.
  - One segment per partition: a letter followed by digits (`r29` → `R29`), `m2m`, a plain word, and the neighbor `ab1` → `Ab1`, which does not match the pattern.
- **Medium, `make test-stand-files` with local Docker:**
  - With today's empty `testdata/realm/`, the generated parity realm equals the seed under `jq -S`.
  - A user file that adds a new user: the user is merged into the parity realm, with its profile filled in.
  - A user file that repeats an existing username: the build fails. Repeat this case for a duplicate `id`.
  - A user file holding one object instead of an array, which `.[1:][][]` does not reject: decide what it should do, and assert that.
