I've read the whole diff, the deleted manifests, the Makefile before and after, the CI workflow, and the existing render harness. Nothing was run, nothing was changed, and nothing was committed. Here is the plan, written as the message for the PR author.

---

## Tests this change owes

This commit replaces the `kubectl apply` harness with the `authz-test-stand` chart. CI already covers the path where everything works: `kind-e2e` and `kind-parity` install the chart on a fresh kind cluster and run both suites, and the `chart` job lints both values files. The pip-stub change also ships with Go tests (`test/integration/pipstub/main_test.go`). What's missing is everything outside that path: a cluster the old harness already set up, the new wait logic when something fails, and the claims in the commit message that no run checks. Each item below says the level, the starting state, the inputs, and what change would make it fail.

There are three levels below. **Render** means `helm template` with no cluster, in the `chart` CI job; it reads files, so in strict terms it's medium. **Kind** means the repo's kind end-to-end runs. **Go unit** is small.

### 1. A cluster the old harness already set up (kind, run once, output pasted in the PR)

`e2e-cluster` reuses an existing `authz-e2e` cluster, so most local clusters will hit this. The old harness left objects without Helm ownership metadata:
- **`authz-e2e`:** ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`, and the Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`.
- **`authz-parity`:** `pip-mock-config`, the same Secret, and `idp`, `pip-mock` and `entitlements-mock`. `parity-realms` gets orphaned, because the new chart names it `idp-realms`.

The chart renders the same names, so I expect `helm upgrade --install` to refuse with "invalid ownership metadata". Helm's message names the conflicting object but not how to fix it, and no doc mentions this case.

- **Start state:** check out `HEAD~1`, run `make e2e-cluster e2e-images e2e-harness e2e-install`, and do the same for parity. Then check out `HEAD`.
- **Run:** `make e2e-harness` and `make parity-harness`. Paste the output.
- **Owed:** add a fix to `docs/local-integration-tests.md` and `test/k8s/README.md`, for example `make e2e-down`, or deleting both namespaces. Deleting the namespaces also removes the old `authz-agent`, which still holds the old Keycloak keys. Then run that fix on this exact state and continue through `e2e-install e2e-suite` and `parity-suite` to green.
- **Second state:** a stand whose first `helm install --wait` failed. Re-run `make e2e-harness` after fixing the cause. The old `kubectl apply` was idempotent. Show that a retry on a failed release installs, or document the fix.

### 2. Failure runs of the new wait logic (kind, run once; both durations and both outputs in the PR)

The durations below come from reading the code, not from runs. The runs have to confirm them.

| Fault | Old: time and output | New: time and output (from the code) |
| --- | --- | --- |
| A harness Pod never becomes Ready. This is the fault `d0b56ed` fixed: tenant-manager crash-looping. Inject it with `TAG=missing` on one stub. | `rollout status deploy/<stub> --timeout=2m`: about 2 min, names the Deployment | `helm … --wait --timeout 10m`: about 10 min, output still to be captured |
| A Keycloak realm file whose name doesn't match the realm (the other `d0b56ed` fault) | 10 min, names `deploy/keycloak` | 10 min, output to capture |
| The suite Pod is created, but its container never starts (image not side-loaded, or a bad `secretEnv` key) | `wait --for=condition=Ready pod … --timeout=3m`: 3 min | The poll loop takes about 3–4 min, `logs -f` fails, then `wait $helm_pid` blocks until `helm test --timeout 15m` or `activeDeadlineSeconds: 900` ends it: **about 15 min** |
| The suite Pod is never created (a quota or Pod Security rejection; inject with `kubectl create quota … --hard=pods=<current count>`) | `kubectl wait -l job-name=…` with no matching Pod: I expect an immediate error. Verify this. | Each `kubectl logs job/X` waits for a Pod for up to `--pod-running-timeout` (20 s by default), plus `sleep 2`, 90 times: **about 33 min**. That's past the `timeout-minutes: 30` of the `kind-e2e` job. |
| The suite fails, which is the most common outcome | `wait --for=condition=Complete --timeout=1m` waits the full minute and prints "timed out" | `helm test` should return as soon as the Job fails. Confirm, and confirm that `make` exits non-zero. |

Where the new logic fails later than the old, give it a deadline on the whole wait, last attempt included, at the old time. For the suite, that could be `--pod-running-timeout=2s` on each poll plus an overall 3-min limit that kills `helm test` and prints the Job's conditions. For the harness, that could be per-Deployment `rollout status` after `helm upgrade` without `--wait`. Alternatively, give the reason it's acceptable in the PR.

### 3. Timeouts that bound the same suite run

The suite run is bounded by four limits:
- `-test.timeout 600s` (`suite.args`)
- `activeDeadlineSeconds: 900` (`values.yaml`)
- `helm test --timeout 15m` (`run-suite` in the `Makefile`)
- CI's 30-minute job limit

The middle two are equal, so they race. Two cases are owed:
- **At the defaults:** a suite that hangs should hit Go's timeout first, so the streamed log shows "test timed out after 10m0s" with the goroutine dump. To keep it short, scale the run down: `-test.timeout 30s`, `activeDeadlineSeconds=60`, and `helm test --timeout 2m`.
- **Just past:** a suite that outlives its own timeout, for example with `suite.args` set to sleep. Which fires, the Job deadline or Helm's timeout, and what does the user see? I'd recommend making Helm's timeout strictly longer than the deadline.

Add a permanent render check that `activeDeadlineSeconds` exceeds `-test.timeout` in both values files.

### 4. One-time comparison with the deleted manifests (render plus a diff, pasted in the PR)

The earlier version's objects are the deleted `test/k8s/*.yaml` and `test/k8s/parity/*.yaml`, plus the ConfigMaps and Secret that the `HEAD~1` Makefile generates with `--dry-run=client -o yaml`. Render `HEAD` with each values file and the Makefile's `--set`. Compare each object by kind and name on:
- images and args
- env, sorted
- ports and Service ports
- probes, mounts and resources
- `serviceAccountName`
- ConfigMap keys and contents, and the decoded Secret data

List every expected difference, and treat any other difference as a finding. Ones I already see:
- **Dropped Keycloak option:** e2e Keycloak lost `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`. State why that's harmless, or restore it.
- **Health flag:** `--health-enabled=true` is now `KC_HEALTH_ENABLED`.
- **Parity realms:** the ConfigMap is renamed `parity-realms` → `idp-realms` and gains `parity-mt-b-realm.json`.
- **Keycloak image:** now pinned by digest.
- **Security and scratch space:** the restricted security contexts and the `/tmp` emptyDir are new.

### 5. Permanent render checks

Put these in `test/scripts/test-chart-render.sh` or a script beside it in the same `chart` job. Use its `pass`/`fail` style: each check gets its own label and the script keeps going after a failure. Reuse `fail`, `pass`, `field` and `kinds_of`. Don't add a near-copy of `deployment_of`; if you need a third render helper, give the existing ones the chart as an argument.

- **The `checksum/realms` annotation, three cases on a copy of the chart with its generated `files/`:**
  - Two renders with nothing changed give the same value. This is the control: if the checksum isn't deterministic, every `e2e-harness` restarts Keycloak, which mints new keys, and the suite fails at `setup.wait_for_agent`.
  - One byte changed in one realm file changes it. This fails if the checksum covers file names only.
  - An added realm file changes it.
- **Missing generated files:**
  - With no `files/` and `idp.enabled=true`, the render fails and the error contains `make test-stand-files`. Match on that part only, not the whole message.
  - A pip-stub instance with a `config` fails the same way.
  - `idp.realms` naming a directory that doesn't exist fails the same way.
  - Control: an instance without `config`, with idp turned off, renders without `files/`.
- **Pod security, over every part:** go through every Pod template in each values file's render. Each must have `runAsNonRoot`, a `RuntimeDefault` seccomp profile, `allowPrivilegeEscalation: false`, and `drop: [ALL]`. Each container must have `readOnlyRootFilesystem: true`, except `keycloak`. Read the list of parts from the render rather than hard-coding it, so a future template that skips the shared helpers fails the check.

### 6. The "restricted Pod Security Standard" claim (kind, run once)

- **Run:** create a namespace labelled `pod-security.kubernetes.io/enforce=restricted`, install the stand there with `test-stand-values.yaml` and `--wait`, and show that every Pod becomes Ready.
- **Control:** apply the `HEAD~1` manifests to the same namespace and show that their Pods are refused. This shows the check can fail.

Use a separate namespace, because the agent and policy-admin charts aren't part of this claim. The OpenShift restricted-SCC claim is untested: run it there, or mark it unverified in the PR.

### 7. Realm user merge and `profile.jq` (small, plus one Docker build run)

The merge never runs today, because there are no user files yet. It has a specification, though: the comment in `profile.jq` and `testdata/realm/README.md`.

- **`profile`, called through `jq -L build/authz-agent-transfer 'include "profile"; …'` with literal expected values:**
  - `parity-r29-level-m2m` gives `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test`. That one name covers a letter+digits segment, a plain word, and `m2m`.
  - A user that already declares all three fields keeps them unchanged.
  - A name without the `parity-` prefix.
  - The edge of the pattern: `ab2` gives `Ab2`, not `AB2`.
  - Open question: `"email": ""` is kept as empty, because `//=` only fills null. Should it be?
- **The merge, run with `docker build --target chart-files` on a context holding fixture user files (it lives in the Dockerfile's `RUN`):**
  - Two files with the same username fail the build.
  - A file repeating a username already in `parity-realm.json` fails.
  - A repeated `id` fails.
  - Control: distinct users merge, and the count is the base count plus the added users.
  - With no user files, the generated `parity-realm.json` equals the source under `jq -S`. That's today's case, and it's cheap enough to keep permanently.

The end-to-end claim ("Account is not fully set up" no longer happens) is owed with the first real user file.

### 8. Transfer image and released images (run once)

- **Transfer image:** build it, copy out `/charts`, and run `helm template` on the copied test-stand chart with the parity values. It should render without the "no realm files" error, and `files/realms/{e2e,parity}` and `files/pip-stub` should hold the expected files.
- **Released images:** do a release dry-run, so the three new images build for `linux/amd64,linux/arm64`.
- **SVT Keycloak bump:** `test/svt/common/compose/docker-compose.yml` moves Keycloak from 26.0 to 26.3.5. That's a version bump, so either bring up the SVT stack once and paste the result, or state that SVT isn't exercised by this PR.

### 9. Docs and the realm-reload path (kind, run once)

- Change one realm file and run `make e2e-harness`. The Keycloak Pod should be replaced and the change should be visible.
- Run `make e2e-harness` again with nothing changed. The Pod UID should stay the same.
- Run the documented subset flow (`helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` then `make e2e-suite`). The log should show only the selected group, and `make e2e-harness` should restore the full run.

### 10. pip-stub (Go unit, adds to the existing table)

The pip-stub change already has tests: the table `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` plus the sequence and `requestUri` tests. The table is missing one partition, which is also the bug the commit message names: **a routed path with no responses and no default route** should answer 404. On the base commit it indexes the response list at -1.

Write it as its own test that doesn't reference `defaultRoute`. Then it compiles on `HEAD~1`, and its red run shows the panic, which is the actual symptom. Every existing new case fails on the base commit only because `defaultRoute` doesn't exist there.

### Owes nothing

The README and doc rewrites, the comment updates in `testify/Dockerfile` and `helpers.go`, the `.gitignore` and `.dockerignore` entries, and the `values.yaml` comment can't change behavior.

### Stack line (a proposal only; no file was edited)

`AGENTS.md` doesn't say which test tools the repo uses. You could add a line like: "Tests: Go `testing` (no testify) in `test/integration/pipstub`; chart behavior through bash render checks in `test/scripts/test-chart-render.sh`, whose `fail` keeps going and names each check by its label."
