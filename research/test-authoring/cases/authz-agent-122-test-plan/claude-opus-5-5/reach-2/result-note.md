# Test plan for 901c8c9: moving the kind harnesses to the authz-test-stand chart

I didn't run anything: there is no cluster or Docker daemon here. Every "today it…" below comes from reading the diff, the deleted manifests at `HEAD~1`, and the chart. Each item says which run settles it. I changed no files.

## What already covers the change

- **CI `kind-e2e` and `kind-parity`** (`.github/workflows/integration-tests.yaml`) install the chart with each values file on a new cluster and run both suites. Together they cover the success path of a fresh install: Service names, ports, issuer hosts, the Secret and the suite env. Link both green runs from the PR. That covers fresh installs only.
- **CI `chart` job** runs `helm lint` on both values files. It catches a template that fails or a missing `required` value. It asserts nothing about what the chart renders.
- **`test/integration/pipstub/main_test.go`** covers the pip-stub default route (`TestHandlePIP_DefaultRoute…`, `…RecordsTheRequestTargetAsSent`). It owes the red run on `HEAD~1` (§1) and is out of scope here.

Stack line to propose for `AGENTS.md` (not written): *"Tests: Go `testing` for Go code; chart checks are bash in `test/scripts/test-chart-render.sh`, which runs every check and reports each failure by its label (`fail`/`pass`, lines 51–58)."*

## 1. Runs from the state the old harness left behind (large, kind) — the main gap

**What the old version leaves.** Any local cluster that ran `make e2e` before this commit has these objects with no Helm ownership metadata:
- In `authz-e2e`: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; the ConfigMap `keycloak-realms`; the Secret `authz-agent-client-credentials`; the ServiceAccount `runtime-suite`; and the Job `runtime-suite`.
- In `authz-parity`: `idp`, `pip-mock` and `entitlements-mock`; the ConfigMaps `parity-realms` and `pip-mock-config`; and the Secret.

The docs suggest reusing the cluster (`docs/local-integration-tests.md` §6), so this is the normal state for anyone who iterates. CI always starts from a new cluster and never sees it.

**Run.**
1. Check out `HEAD~1` and run `make e2e`.
2. Check out `HEAD` and run `make e2e-harness e2e-install e2e-suite`.
3. Do the same with `make parity`.

**What I expect.** Helm refuses the install with "exists and cannot be imported into the current release: invalid ownership metadata", naming the first object it meets: `keycloak-realms`, `pip-mock-config` or the Secret. Separately, `make e2e-suite` on a namespace that the new harness never installed fails with "release: not found". Neither error tells the developer what to do.

**What the change owes.** It doesn't say what should happen here: keep working, migrate, or fail with a remedy. Pick one:
- **Document a remedy** (`kubectl delete namespace …` or `make e2e-down`) in the Troubleshooting table, and show it run on that state.
- **Migrate**, e.g. `--take-ownership` on the harness install, if Helm v4.3.1 accepts it here. Then the run also shows:
  - the Deployments are adopted, which works only because the selectors kept `app: <name>`;
  - the orphaned `parity-realms` ConfigMap is still there;
  - both suites pass.

## 2. Failure runs of the two replaced mechanisms (large, kind)

For each fault, run `HEAD~1` and `HEAD` and paste both durations and both outputs into the PR.

| Fault | Old (from the code) | New (from the code; the run settles it) |
| --- | --- | --- |
| Stub image not loaded (`ErrImageNeverPull`, the first Troubleshooting row) | `rollout status deploy/pip-stub --timeout=2m` fails at about 2 min and names the Deployment | `helm --wait --timeout 10m` fails at about 10 min, with whatever Helm 4's waiter prints |
| Suite image not loaded | `wait --for=condition=Ready pod … --timeout=3m` fails at 3 min | The log loop runs about 3 min, then `logs -f` prints the waiting reason. `wait $helm_pid` then holds until `helm test --timeout 15m`, which is also the Job's `activeDeadlineSeconds: 900`, so about 15 min |
| A suite test fails (the usual case) | The log streams, then `wait --for=condition=Complete --timeout=1m` fails after 1 min with a timeout message | `helm test` should return non-zero as soon as the Job fails. Assert that `make e2e-suite` exits non-zero and the log was streamed |
| The longest single wait in the loop: API server unreachable mid-run (`docker pause` the control-plane node) | — | `kubectl logs` in the loop and `helm test` have no request timeout, so neither is bounded |

Where the new mechanism fails later than the old one (the first two rows), the PR has two choices:
- Bound the wait at the old time. For example, give the stub check its own short wait, and stop waiting on `helm test` once `logs -f` has reported that the container cannot start.
- Or say why the longer wait is acceptable. The CI jobs have `timeout-minutes: 30`, and in the worst case the image build plus 10 m plus 5+5 m plus 15 m doesn't fit, so the job timeout fires first. Say which limit fires and what the log shows.

**Limits on the same work (§4).**
- At the defaults, `-test.timeout 600s` must fire before `activeDeadlineSeconds: 900` and `helm test --timeout 15m`, and print Go's panic with the running tests. Run one case with a hanging test to show it.
- `activeDeadlineSeconds` and the `helm test` timeout are both 15 min. Run one case with `suite.activeDeadlineSeconds` set past 900 and record which one fires and what the user sees.

## 3. `E2E_HELM_ARGS` now reaches the test-stand chart (small render first, then one kind run)

Values both kinds of chart read:
- `TAG`: `authz-agent/templates/deployment.yaml:153`, `authz-policy-admin/templates/deployment.yaml:79`, and in the test stand `pip-stub.yaml:40`, `suite.yaml:40` and `tenant-manager.yaml:34`.
- `IMAGE_PULL_POLICY`: the next line in each.
- The flags `--timeout` and `--wait`.

The documented example, `--set IMAGE_PULL_POLICY=Never`, settles nothing: it means the same thing to every chart.

**Small render.** `helm template` the test stand with `-f test/k8s/test-stand-values.yaml --set TAG=dev`. I expect `local/pip-stub:dev` and `local/authz-runtime-suite:dev`, and `make e2e-images` builds neither. Likewise, `IMAGE_PULL_POLICY=Always` points the stand at `docker.io/local/...`.

**Run.** Run `make e2e-harness E2E_HELM_ARGS='--set TAG=dev'` with the agent images built as `:dev`. Show the result: the harness stalls for 10 min on the stubs. Also show that `E2E_HELM_ARGS='--timeout 3m'` overrides the harness's 10 min while Keycloak is still being pulled.

If the run confirms this, the bug is in the change, not the test. Fix it by giving the stand its own variable, or by not passing `E2E_HELM_ARGS` to it. The same render then shows that `--set TAG=dev` no longer changes the stand's images, and that the stand's own variable still reaches it.

## 4. Chart render checks (small: a new section of `test/scripts/test-chart-render.sh`)

These follow the file's shape: each check has a literal expectation and a `pass`/`fail` label. Logic checks use a temporary copy of the chart with hand-written `files/`, so they don't depend on `make test-stand-files`.

- **Realm ConfigMap and missing files.**
  - With `idp.realms=e2e`, the ConfigMap keys are exactly the four `*-realm.json` names.
  - With `parity`, the keys are the three parity names.
  - With an empty or unknown directory, the render fails and the error names `make test-stand-files`.
- **Restart on change.** In the copy, edit one byte of a realm file and `checksum/realms` changes. The control: two renders with no edit give the same checksum.
- **pip-stub instances.**
  - An instance with `config` renders the ConfigMap, the mount and `PIP_STUB_CONFIG`.
  - An instance without it renders none of the three.
  - A missing rule file fails, naming the file.
  - A missing `port` fails with its `required` message.
- **tenant-manager.**
  - `tenants: {b: 2, a: 1}` renders `TENANT_MANAGER_TENANTS="a=1,b=2"`.
  - An empty map fails.
  - An empty `imageRepository` fails.
- **Secret value.** The parity password `ParityM2MSecret1!@#` reaches `stringData.password` unchanged. That is the value the old harness passed with `--from-literal`, and YAML treats `!` and `#` specially, so this checks it survives.
- **Suite env.**
  - `FULL_RUNTIME_SUITE: "true"`, `AUTHZ_PAP_CLIENT_PULL_INTERVAL: "2"` and a `--set suite.env.FULL_RUNTIME_SUITE=false` without `--set-string` all render as quoted strings.
  - `$(RUNTIME_SUITE_RUN)` survives in `args`.
  - `--set suite.env.BASE_URL=http://x:1` overrides the value, which is the Makefile's path.
  - `secretEnv` renders `secretKeyRef`.
  - The `/tmp` `sizeLimit` follows the `ephemeral-storage` limit and falls back to `256Mi` when the limit is absent.
- **Security context and labels over every rendered object, all parts enabled.** This is an open set: enumerate the Pod templates and containers from the render, not from a list, so a part added later without them fails the check.
  - Every Pod has `runAsNonRoot` and the `RuntimeDefault` seccomp profile.
  - Every container has `allowPrivilegeEscalation: false` and `drop: [ALL]`.
  - `readOnlyRootFilesystem` is true on every container except `keycloak`.
  - Every object carries the `app.kubernetes.io/*` labels and `helm.sh/chart`.
  - Every selector is exactly `app: <name>`.
- **Default images against `.qubership/docker.cfg`.** Every non-empty default `imageRepository` in `values.yaml` is `ghcr.io/netcracker/<a name docker.cfg publishes>`. Compare the two sets, so an unpublished default fails.

## 5. Generating the realm files (small for `profile.jq`, medium for the merge)

There are no user files under `testdata/realm/` yet, so no CI run goes through this code.

**Small: `jq -L build/authz-agent-transfer 'include "profile"; map(profile)'` on literal users.** Compare expected values with the stand the goldens were recorded on, not with `profile.jq`'s own output.

| Case | Expected |
| --- | --- |
| `parity-r29-level-m2m` with no profile fields | `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test` (the values the comment cites) |
| A plain word list, e.g. `parity-order-reader` | `OrderReader` |
| No `parity-` prefix, e.g. `admin` | `Admin` |
| Regex boundary `^[a-z][0-9]+$`: `r29`, `ab12`, `r29x` | `R29` / `Ab12` / `R29x` |
| A user that declares all three fields (control) | Its fields are kept |
| `firstName: ""` | Kept as `""` by `//=`, but Keycloak 26 refuses an empty first name. Is this a bug or intended? |

**Medium: `docker build --target chart-files` from a temporary context.** Build a context with the copied inputs and two user files.
- A username repeated across files fails the build.
- An `id` repeated across files fails the build.
- Two users without an `id` pass.
- A user that repeats one already in `parity-realm.json` fails.

## 6. Transfer image (medium, Docker, no cluster)

1. Put a stale extra file in `helm-templates/authz-test-stand/files/`.
2. Build the image and `docker cp /charts` out of it.
3. Show that `files/realms/parity/` holds exactly the three generated realms. `.dockerignore` should keep the stale file out.
4. Follow README step 2 (the parity values minus the kind keys, `--set TAG=1.2.3`) and show that `helm template` renders `ghcr.io/netcracker/qubership-authz-pip-stub:1.2.3` and `…-parity-suite:1.2.3`.

## 7. Restricted Pod Security Standard and realm restart (large, kind)

**Restricted PSS.** The PSS claim is untested: `--create-namespace` creates the namespace without labels.
1. Create both namespaces with `pod-security.kubernetes.io/enforce=restricted`.
2. Run `make e2e` and `make parity`, and show that every Pod is admitted and both suites pass. The kubelet's numeric-user check for `runAsNonRoot` only shows up in a run.
3. Control: the `HEAD~1` harness in the same namespace is rejected, which shows the label is enforced.

The OpenShift SCC claim stays unverified unless an OpenShift stand runs it; the PR should say so.

**Realm restart.**
1. Edit a realm file and rerun `make e2e-harness`. Show that the Keycloak Pod is replaced and serves the change (the new realm's `/.well-known/openid-configuration` returns 200).
2. Control: rerun with no edit and show the Pod keeps its UID.

## 8. A one-time diff against the deleted manifests (judgment, pasted into the PR)

Render both values files and diff them against the manifests at `HEAD~1`, with labels and security contexts stripped. Explain each remaining difference. Those I already see:
- The e2e Keycloak loses `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`.
- `--health-enabled` became `KC_HEALTH_ENABLED`.
- The Keycloak image is now pinned by digest.
- The parity realm ConfigMap is renamed `parity-realms` → `idp-realms` and gains `parity-mt-b`.
- The parity suite env keeps all six values.

Separately, the Troubleshooting row "times out at `rollout status deploy/keycloak`" in `docs/local-integration-tests.md` names a command the Makefile no longer runs.
