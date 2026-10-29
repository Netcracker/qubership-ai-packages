I have everything I need. Here is the plan, written as the review message for the pull request author.

---

**Test plan for `0b2fee2` (moving the kind harnesses onto the `authz-test-stand` chart)**

This change moves the kind harnesses onto a chart, so its users now start from new states, pass new values and meet new failure modes. A green CI run checks only one of these: a fresh cluster with default settings where nothing goes wrong. The plan covers the rest. Each item says its level, the state it starts from, its inputs, and what it shows. The `pipstub` changes already have small Go tests in `test/integration/pipstub/main_test.go`, so they are not repeated here.

**1. One-time run: does the chart render the deleted stand? (no cluster needed)**
- **Inputs:** `helm template` the chart with `test/k8s/test-stand-values.yaml` and with `test/k8s/parity/test-stand-values.yaml`.
- **Compare against:** the manifests deleted from `HEAD~1`, plus the ConfigMaps and Secrets the old Makefile built. These come from the earlier version, not from the new chart.
- **Fields to compare:** object names, images, args, env, ports, probes, volumes, resources, and the Secret's `username`/`password`.
- **Put in the PR:** every difference, each named as intended or as a bug. Known ones so far:
  - `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` is gone from the e2e Keycloak.
  - `--health-enabled=true` became `KC_HEALTH_ENABLED`.
  - The Keycloak image is now pinned by digest.
  - `parity-realms` became `idp-realms`.
  - The `parity-mt-b` realm and new parity users were added.
  - The security contexts and labels were added.
- **Check:** the parity password `ParityM2MSecret1!@#` renders unchanged.
- This is evidence for the PR, not a committed test, because a committed whole-render diff would fail on every intended change.

**2. Large: the CI kind runs, compared between base and head**
- `kind-e2e` and `kind-parity` must pass, but passing is not enough. Go exits 0 with `testing: warning: no tests to run` when `-test.run` matches nothing. That would happen here if `$(RUNTIME_SUITE_RUN)` stopped expanding in `args`.
- **Compare:** the sets of `--- PASS`, `--- SKIP` and `--- FAIL` test names in the head run's Job log against the same sets from the base commit's CI run.
- **Expected:** the sets match. For example, the `m2m_keycloak` steps still run rather than skip. Any difference should be named in the PR.
- Nothing in the suites uses the new parity users or `parity-mt-b` yet. This run shows only that they import, so say so in the PR.

**3. Medium (kind): starting from a cluster the old harness set up**
- **State:** run `make e2e-harness parity-harness` at `HEAD~1` on a kind cluster, then run `make e2e-harness parity-harness` at head on the same cluster.
- **Objects left behind with no Helm ownership:**
  - e2e namespace: the Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; the ConfigMap `keycloak-realms`; the Secret `authz-agent-client-credentials`; the ServiceAccount `runtime-suite`.
  - parity namespace: `idp`, `pip-mock`, `entitlements-mock`, the ConfigMap `pip-mock-config` and the same Secret.
- **What I expect:** Helm refuses to adopt these objects ("invalid ownership metadata"), and that error does not name a fix.
- **What the PR owes**, one of:
  - a documented fix, run on this state and shown working (`make e2e-down`, deleting the two namespaces, or `--take-ownership`); or
  - the harness adopting the objects itself.
- The troubleshooting table in `docs/local-integration-tests.md` should get that row. Its row about `rollout status deploy/keycloak` is out of date too.

**4. Medium (kind): runs where the new wait and test steps meet a fault**
For each fault below, state in the PR the old duration and output next to the new ones.
- **Missing stub image** (the most common fault, from the troubleshooting table): skip `kind load` for `local/pip-stub:ci`.
  - Old: `rollout status deploy/pip-stub` failed after about 2 minutes with "timed out waiting for the condition".
  - New: `helm --wait --timeout 10m` fails after up to 10 minutes. Capture what Helm 4.3.1 prints.
- **Missing suite image:**
  - Old: `wait --for=condition=Ready` failed after 3 minutes.
  - New: the log loop runs about 90 × (one `kubectl logs` call + 2 s), and then `wait $helm_pid` lasts until `activeDeadlineSeconds` (900 s) or `helm test --timeout 15m`. That is about 15 minutes.
  - In CI the steps add up past the job budget: harness 10 min + installs 2 × 5 min + suite 15 min = 35 min against `timeout-minutes: 30`. Either bound this wait or say in the PR why the trade is worth it.
- **Longest single attempt of the loop:** the polled `kubectl logs` has no `--request-timeout`, so one attempt has no bound. Fault to run: pause the kind control-plane container right after the Job is created. Add `--request-timeout` to the call, or justify leaving it out.
- **A suite that fails** (for example, `E2E_BASE_URL` pointing at a host that does not answer): `make e2e-suite` must exit non-zero, with the log streamed. This shows that `wait $helm_pid` passes the exit code through.
- **Cite, don't run:** the `kubectl` version in CI and the minimum version in the docs. `kubectl wait --for=create` needs kubectl 1.31 or later. On an older kubectl, `&&` skips the loop and no log is streamed.
- **Limits on the same work:** a small check that `helm test --timeout` is greater than `activeDeadlineSeconds`, which is greater than `-test.timeout` (900 s, 900 s and 600 s today). Today the first two are equal, so which one fires first depends on timing. Then one run with a hung test, showing the 600 s Go timeout fires first and its stack dump reaches the streamed log.

**5. `E2E_HELM_ARGS` now reaches the test-stand install**
- **Settings both charts read:** `TAG` and `IMAGE_PULL_POLICY`.
- **A value users pass for the old charts:** `E2E_HELM_ARGS='--set TAG=dev'`, to install a differently tagged agent.
- **What it now does to the stand:** the stand renders `local/pip-stub:dev`, `local/authz-runtime-suite:dev` and `local/tenant-manager:dev`. `make e2e-images` builds none of these, so the stand fails with `ErrImageNeverPull` after a 10-minute wait. `IMAGE_PULL_POLICY=Always` breaks the stand the same way.
- This is a bug in the change, not a gap in the tests. The fix is a variable of the stand's own, for example `E2E_TEST_STAND_HELM_ARGS`. The test then shows that `--set TAG=dev` passed through `E2E_HELM_ARGS` no longer changes the stand's images.

**6. Small: render checks in `test/scripts/test-chart-render.sh`**
These go next to the existing render checks, using its `pass`/`fail` helpers. Every check reports with its own label and the script keeps going after a failure (`test-chart-render.sh:51-58`). CI already generates the files before this step runs.
- **Which realms are loaded:**
  - `idp.realms=e2e`: the ConfigMap's keys are exactly the four files the old Makefile listed.
  - `parity`: `cloud-common`, `parity-mt-b` and `parity`.
- **The realm checksum** (each check renders into a temporary copy of the chart):
  - The same files render the same `checksum/realms`, so a harness rerun does not restart Keycloak and rotate its keys.
  - Changing one byte of an e2e realm changes the checksum.
  - Changing a parity realm leaves the e2e checksum alone.
  - Then one kind run of the same sequence, comparing the Keycloak Pod UIDs.
- **Missing generated files:**
  - With an empty `files/`, the render fails and the error names `make test-stand-files`, both for the realms and for `pip-mock`'s rule file.
  - Control: the same render with the files present succeeds.
- **Base URL override:** `--set suite.env.BASE_URL=http://elsewhere:9` gives the Job that `BASE_URL`, with exactly one such entry. The same for `PARITY_AC_BASE_URL`. This replaces the old `sed`.
- **Tenant map:**
  - With e2e values, `TENANT_MANAGER_TENANTS` is `default=6f1c2a9e-…`, the literal from the deleted manifest.
  - Two tenants render sorted by name, joined with a comma.
  - `tenants: {}` fails with `tenantManager.tenants is required`.
- **Value types in `suite.env`:** one case each for a string, a quoted number, an unquoted integer and a boolean. Also try an integer of 1000000 or more, which Helm's `toString` can render as `1e+06`.

**7. Generated files and the transfer image**
- **Small: `profile.jq`**, run through `jq -L build/authz-agent-transfer 'include "profile"; …'` on literal users:
  - `parity-r29-level-m2m` with no profile fields gives `Parity`, `R29LevelM2M` and `parity-r29-level-m2m@example.test`.
  - Each of the three fields, when declared, is kept.
  - A username without the `parity-` prefix.
  - The parts `r`, `29`, `ab12` and `m2m`, on each side of the regex `^([a-z][0-9]+|m2m)$`.
  - Open question: should a declared empty `lastName` be kept? Today it is.
- **Medium: `docker build --target chart-files`** on a temporary build context:
  - No user files: the merged realm's users equal the source realm's users. This is the control.
  - One user file: the user is appended, with the profile filled in.
  - A username that already exists: the build fails.
  - An id that already exists: the build fails.
  - Two users without ids: the build passes. This is the control for `select(.)`.
  - Running the first user file through a password grant on kind is owed when the first such file lands.
- **Medium: the transfer image**:
  - Make the checkout's `files/` stale on purpose, build the image, and copy `/charts` out as the README says.
  - `helm template` the stand with the README's edited parity values and `--set TAG=1.2.3`.
  - Assert the images are `ghcr.io/netcracker/qubership-authz-pip-stub:1.2.3` and `qubership-authz-parity-suite:1.2.3`.
  - Assert the realm ConfigMap matches freshly generated files, not the stale ones. This shows `.dockerignore` works.
- **Release:** a dry run of `docker-release.yaml` that builds the three new images.

**8. Medium: the restricted Pod Security Standard**
- **Case:** in a namespace labelled `pod-security.kubernetes.io/warn=restricted`, run `helm template … | kubectl apply --dry-run=server` for both values files, including the suite Job. Expect no "would violate PodSecurity" warning.
- **Control:** a Deployment with no security context in the same namespace does produce the warning.
- The green kind run already covers what only a real start shows: `runAsNonRoot` against each image's user, and the read-only root filesystem.
- OpenShift's restricted SCC is not tested anywhere. The PR should say so.

**9. Other**
- The SVT compose file moves Keycloak from `26.0` to `26.3.5`. That is a version bump, so the PR should name what the green suite covers for it, or include one SVT start.
- `AGENTS.md` has no line naming the test stack. I propose adding one: `Tests: Go testing; chart checks in test/scripts/test-chart-render.sh, which reports every failed check by its label and continues`.

I changed no file and ran nothing. Every duration above is an estimate from the configured timeouts. The PR should carry the measured ones.
