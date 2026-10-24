I've written the plan below from the skill and a full read of `0b2fee2`. Nothing was run, and I changed no file. Where I say "I expect" a result, I'm predicting from the diff; the run is what decides it.

---

## Test plan: run the kind harnesses on a test-stand chart

**What CI already shows.** The `kind-e2e` and `kind-parity` jobs install the chart on a fresh cluster with both values files and run both suites. That covers the success path from a fresh install, so the PR can name those two jobs and needs no other test for it.

**What it doesn't show.** The move replaces three things:
- **Objects already in the namespace.** The old harness made them with `kubectl apply`, and the new install now meets them on a developer's cluster.
- **The waits.** `rollout status` and `wait --for=condition=Ready/Complete` become `helm --wait` and `helm test`.
- **Where `E2E_HELM_ARGS` goes.** It used to reach only the agent charts; it now reaches the stand too.

The change owes a test or a run for each of these, plus render checks of the new chart and checks of the realm-generation stage.

### 1. Render checks: small, in `test/scripts/test-chart-render.sh`

These use `helm template` only, with no cluster. They go in the repository's existing render harness, which the `chart` job runs after `make test-stand-files`.

**Harness behaviour.** Each check calls `pass` or `fail` itself and names itself by its message. The script keeps going after a failure and counts failures at the end (`test/scripts/test-chart-render.sh:51-58` and the last lines). So several checks can share one render, each with its own message.

**Section setup.** Add a section "The test-stand chart" that renders with `-f test/k8s/test-stand-values.yaml` and with `-f test/k8s/parity/test-stand-values.yaml`. If `files/` is missing, the section reports one failure that names `make test-stand-files`, not a failure per check. Renders that need missing files work on a temporary copy of the chart, never on the checkout's `files/`.

1. **Every address the suites and the agent use is a rendered Service on that port.**
   - Hosts come from `suite.env` and from `AUTHZ_TENANT_MANAGER_URL` and the issuer in `test/k8s/values.yaml` and `test/k8s/parity/values.yaml`.
   - Expected values are literals taken from the deleted manifests:
     - e2e: `keycloak:8080`, `pip-stub:8090`, `entitlements-mock:8090`, `tenant-manager:8080`
     - parity: `idp:8080`, `pip-mock:8090`, `entitlements-mock:8080`
   - Breaks on a renamed instance or a port moved in a values file. Show it red once in the PR by rendering with `--set pipStub.instances.entitlements-mock.port=8091`.
2. **The suite Job keeps the old Job's arguments and environment.**
   - Expected names, values and `args` come from `runtime-suite-job.yaml` and `parity-suite-job.yaml` at `d0b56ed`, copied as literals rather than taken from the new render.
   - Compare the environment sorted by name. The chart sorts it, and no value refers to another, so order carries no meaning.
   - Cover each kind of value `--set` can give:
     - `--set suite.env.FULL_RUNTIME_SUITE=false` (a boolean) renders `"false"`.
     - `--set suite.env.KC_EXPIRED_WAIT_SECONDS=10` (an integer) renders `"10"`.
     - `--set suite.env.BASE_URL=http://authz-agent-canary:8080` renders that value. This is what the Makefile now does with `E2E_BASE_URL`.
3. **The client-credentials Secret keeps the old values.**
   - e2e: `name=authz-agent`, `username=test-app-client`, `password=test-app-secret`, from the deleted `m2m-credentials/` files.
   - parity: `parity-m2m` and `ParityM2MSecret1!@#`, from the old `--from-literal`. This shows `!@#` survives quoting.
   - An empty password and an empty username are separate refusal cases, each expecting its `... is required` message.
4. **Each refusal names its remedy, one invalid input per render.**
   - `idp.enabled` with no `files/realms/parity/` names `make test-stand-files`.
   - A `config` naming a missing rule file names that file.
   - `tenantManager.tenants: {}` gives `tenantManager.tenants is required`.
   - `TAG: ''` with a stub instance gives `TAG is required`.
   - The parity values file, which renders, is the control for all four.
5. **The tenant map becomes `TENANT_MANAGER_TENANTS`.**
   - One tenant renders `default=6f1c2a9e-3b4d-4e8f-9a1b-2c3d4e5f6a7b`, the old manifest's literal.
   - Two tenants given in the order `b`, `a` render `a=1,b=2`.
6. **A stub with a rule file next to one without, in one render.** In the parity render, `pip-mock` gets the `pip-mock-config` ConfigMap with key `requestargs.responses.yaml`, `PIP_STUB_CONFIG=/etc/pip-stub/requestargs.responses.yaml` and the mount. `entitlements-mock` gets none of the three.
7. **Re-running the harness restarts Keycloak only when a realm file changes.**
   - Two renders from the same files give the same `checksum/realms`. This is what stops a plain re-run of `e2e-harness` from replacing Keycloak and rotating its keys under the agent.
   - On a temporary copy, one byte changed in one realm file gives a different checksum. A realm file added does too.
8. **The restricted Pod Security Standard, checked on every Pod the chart renders.**
   - Find every Pod template in both renders (the Deployments and the Job) from the render itself, not from a hand-written list. Each must have `runAsNonRoot: true`, `seccompProfile: RuntimeDefault` and no `runAsUser`.
   - Every container must have `allowPrivilegeEscalation: false` and `drop: [ALL]`, and a read-only root filesystem except `keycloak`.
   - In the same pass, every object must carry the `app.kubernetes.io/*` labels and `helm.sh/chart`, and every selector must be exactly `{app: <name>}`.
   - This fails on the next part someone adds without the helpers.
9. **The time limits on the suite run are in order.** `-test.timeout 600s` must be less than `activeDeadlineSeconds: 900`, which must be less than `helm test --timeout 15m` in the Makefile. **I expect the second comparison to fail:** 900 s and 15 m are equal, so whether the Job's `DeadlineExceeded` or Helm's timeout fires first is a race. Fix it by raising the Helm timeout above the deadline plus scheduling time, or by lowering the deadline.
10. **The `/tmp` size limit.** `limits.ephemeral-storage: 256Mi` renders `sizeLimit: 256Mi`. `--set suite.resources.limits=null` falls back to `256Mi`.

### 2. Realm generation: medium (a `docker build`), a new `test/scripts/test-stand-files.sh`

The merge is written inline in the Dockerfile, and a test that copied the jq expression would only test the copy. So the script builds the real `chart-files` stage. It uses a temporary build context holding the paths the Dockerfile copies, plus hand-written user files under `test/parity/suite/testdata/realm/`, and runs `--output` to a temporary directory. Expected values come from the commit message and the realm README, not from the stage's output.

1. **No user files, as today.**
   - `realms/e2e/` holds the four `authn/` realms, byte-for-byte.
   - `realms/parity/` holds cloud-common, parity-mt-b and parity. The parity realm must equal `idp-seed/parity-realm.json` under `jq -S`.
   - `pip-stub/` equals `test/integration/pipstub/config/`.
2. **A user without profile fields gets them filled in, in one build with its control.**
   - The user `parity-r29-level-m2m` gets `Parity`, `R29LevelM2M` and `parity-r29-level-m2m@example.test`.
   - Control: a user that declares all three keeps its own values.
3. **How the last name is built, one user per case, all in one build, each with its own message.**
   - `r29` becomes `R29`, `m2m` becomes `M2M`, and `level` becomes `Level`.
   - At the edges of `^[a-z][0-9]+$`: `r2d` becomes `R2d` and `x` becomes `X`.
   - A name without the `parity-` prefix: `auditor` becomes `Auditor`.
4. **Refusals, one build each.**
   - A username in both a user file and `parity-realm.json` makes the build fail.
   - The same `id` in two user files makes it fail.
   - Control: users with no `id` at all build.
5. **A user file holding one object instead of an array.** The README asks for arrays, and `.[1:][][]` would walk the object's field values. Expected: the build fails and names the file. **I expect it to build with bogus users, or to fail with a jq type error that names no file.** If so, the stage needs a type check.
6. **The transfer image.**
   - A stale `files/realms/parity/leftover.json` in the checkout must not reach `/charts/authz-test-stand/files/`, because `.dockerignore` excludes it.
   - The image's `files/` must equal the `chart-files` output.
   - Rendering the copied-out chart with the README's step-2 edits and `--set TAG=1.2.3` must give `ghcr.io/netcracker/qubership-authz-pip-stub:1.2.3` and `...-parity-suite:1.2.3` with `IfNotPresent`.

### 3. Runs on kind: large, run once by hand, output pasted in the PR

1. **Starting from what the old harness left behind.** Neither the docs nor the harness handle this today.
   - **What's there.** A developer's cluster from `d0b56ed` holds:
     - in `authz-e2e`: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`; Job `runtime-suite`.
     - in `authz-parity`: `idp`, `pip-mock` and `entitlements-mock`; ConfigMaps `parity-realms` and `pip-mock-config`; the Secret; Job `parity-suite`.
   - **The conflict.** None of these carry Helm's ownership metadata, and most have names the chart renders. With `idp.name: keycloak` the chart's ConfigMap is also called `keycloak-realms`.
   - **How to get a faithful copy.** Check out `d0b56ed`, run `make e2e parity`, then check out this branch and run `make e2e-harness e2e-install e2e-suite` and the three parity targets.
   - **What I expect.** `helm upgrade --install` stops with `... exists and cannot be imported into the current release: invalid ownership metadata`.
   - **What the PR has to promise.** Either the harness migrates (deletes or adopts the old objects), or `docs/local-integration-tests.md` and `test/k8s/README.md` name the remedy (`make e2e-down`, or deleting both namespaces). In the second case the PR shows that remedy run on this cluster, followed by both suites passing.
2. **Re-running on the new chart.**
   - Case: `make e2e-harness` twice with no file changed keeps the Keycloak Pod (same UID), and `make e2e-suite` then passes without restarting the agent.
   - Control: change one realm file and re-run. The Pod is replaced, and the suite fails at `setup.wait_for_agent` until the documented agent restart, then passes.
3. **The restricted standard, for real.** Label both namespaces `pod-security.kubernetes.io/enforce=restricted` before the harness. Every stand Pod must be admitted and become Ready, and `helm test` must pass. Only real admission shows that Keycloak 26.3.5 and the four local images, with `USER 10001`, satisfy `runAsNonRoot`. If the agent charts don't pass the restricted standard, say so as outside this change.
4. **A failed suite fails `make`.**
   - Case: `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN='^TestRuntimeSuite$/^TestCheckResource$'` with `FULL_RUNTIME_SUITE` left `true`. The coverage checks then fail, as the docs say. `make e2e-suite` must exit non-zero, with the `FAIL` lines in the streamed log.
   - For parity: point `PARITY_AC_BASE_URL` at a host that doesn't exist.
   - Control: CI's green run exits 0.
5. **How the replaced waits fail.** Run each fault on `d0b56ed` and on this branch, and put both durations and both outputs in the PR.
   - **A local stub image missing on the node.** This is the fault the old harness met most often. Skip `kind load` for `pip-stub`, or `crictl rmi` it on the node, then run `e2e-harness`.
     - Old: `rollout status deploy/pip-stub --timeout=2m` fails after about 2 min and names `pip-stub`.
     - New: **I expect it to take about 10 min** under the single `--wait --timeout 10m`, with a Helm message that may not name the Deployment or `ErrImageNeverPull`.
   - **The suite image missing, then `e2e-suite`.**
     - Old: `wait --for=condition=Ready pod --timeout=3m` fails after about 3 min.
     - New: the log loop runs 90 times, each attempt a 2 s sleep plus one `kubectl logs` call bounded only by kubectl's own default timeout. That is about 3 min or more. Then `logs -f` fails, and `wait $helm_pid` waits for `helm test`. It returns when the 900 s Job deadline or the 15 m Helm timeout fires. **I expect about 15 min, with nothing naming the pull failure.**
   - **The longest single attempt.** Run `e2e-suite` with no release installed, or with `suite.enabled=false`. `helm test` fails at once, but `kubectl wait --for=create ... --timeout=2m` waits the full 2 min first.
   - **Older kubectl.** `--for=create` needs kubectl 1.31 or later. On an older kubectl the `&&` skips the log loop: the log is lost, but the exit code still comes from Helm. State in the PR which kubectl CI uses.
   - **The CI job limit.** The kind jobs stop at `timeout-minutes: 30` (`integration-tests.yaml:120,168`). A harness fault (10 min), both installs (up to 2 × 5 min) and a suite fault (about 15 min) together exceed that. The report then becomes GitHub's "exceeded the maximum execution time" instead of the cause. Either bound the new waits close to the old ones (for example, `rollout status` per part, and a log loop that stops on `ErrImagePull`, `ImagePullBackOff` or `ErrImageNeverPull`), or state in the PR why the trade is worth it.
6. **`E2E_HELM_ARGS` now reaches the stand.**
   - **The shared keys.** `TAG` and `IMAGE_PULL_POLICY` are top-level keys in all three charts.
   - **First, small renders:** `-f test/k8s/test-stand-values.yaml`, followed by each value users pass for the agent charts.
     - `--set TAG=1.2.3`, to try a published agent build. **I expect** `local/pip-stub:1.2.3`, `local/tenant-manager:1.2.3` and `local/authz-runtime-suite:1.2.3` with `Never`. Nothing builds these images, so the harness waits out its 10 minutes.
     - `--set IMAGE_PULL_POLICY=Always`, to force a fresh pull of the agent. **I expect** the stand's `local/*` images to try docker.io and fail.
     - `--set IMAGE_PULL_POLICY=Never`, the example in the docs, renders the same as without it, so it proves nothing.
     - `--set LOG_LEVEL=debug` renders the same as without it. This is the control.
   - **Then one large run** with `TAG=1.2.3`, to show what the user sees.
   - **If the predictions hold**, the defect is in the change. The fix is a setting of the stand's own, such as `TEST_STAND_HELM_ARGS`, or not passing `E2E_HELM_ARGS` to the stand. A render check in §1 then asserts the stand's images keep `:ci` when `E2E_HELM_ARGS` carries `TAG`.

### 4. Outside these tests, but the PR should say so

- **No test owed.** The comment and doc edits (`helpers.go`, the testify Dockerfile comment, the READMEs, the `values.yaml` comment) can't change behavior. One line in the PR.
- **Moved behavior to name.**
  - The e2e Keycloak no longer sets `keycloak.migration.strategy=OVERWRITE_EXISTING`.
  - Health is now turned on with `KC_HEALTH_ENABLED` instead of the `--health-enabled` flag.
  - The Keycloak image is pinned by digest.
  - Every object carries the new labels.
  - `E2E_BASE_URL` and `PARITY_AC_BASE_URL` now take effect at `*-harness`, not at `*-suite`. `make e2e-suite E2E_BASE_URL=…` is silently ignored.
- **The SVT compose Keycloak, 26.0 → 26.3.5.** This is a dependency bump that the kind suites don't cover. Name the job that runs the compose stack in `test/svt/common/compose/`, or run it once and show Keycloak healthy with its realms imported.
- **The release config.** `.qubership/docker.cfg` and `docker-dev-config.json` add three images. Paste a `docker-release` dry-run log that builds all three from the contexts those files name.
- **`parity-mt-b`.** Name the parity case that uses it, or say none does yet.
- **pip-stub's default route.** It has its own tests in `test/integration/pipstub/main_test.go`; this plan doesn't cover it.

**Suggested stack line.** `AGENTS.md` doesn't list the test stack. I suggest adding one line, after you agree: `Tests: Go testing with testify where a package imports it; chart renders in test/scripts/test-chart-render.sh, where every check reports on its own and names itself by its message; kind harnesses via make e2e and make parity.`
