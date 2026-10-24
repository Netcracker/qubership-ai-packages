The plan below is what to run and why. I did not run anything, and I did not change or commit any file. The stack is bash with `helm template`, Make, Helm, and jq, plus the Go suites this move does not touch. No `references/` file covers bash, and I planned no Go assertion, so I opened no reference file.

---

**Test plan: move of the kind harnesses to the test-stand chart (33acfe1)**

**Stack line (proposed, §0).** `AGENTS.md` has no stack line. Proposed: "Tests: bash with `helm template` for chart renders (`test/scripts/test-chart-render.sh`); Go `testing` for `test/integration/pipstub`; Testify for `test/integration/testify`." This edits no file.

**What the move owes (§3).** It replaces a mechanism (`kubectl apply` and a wait loop become `helm upgrade` and `helm test`). It changes what an earlier version left in the namespace. It sends `E2E_HELM_ARGS` to a second chart. It changes the transfer Dockerfile. The commit adds no test for any of these.

**Levels.** Medium means `helm`, `jq`, or `docker` on the local machine with no cluster. Large means kind.

**Bucket.** Each item is a run, unless marked as a judgment.

---

### 1. Chart renders (medium; checks in the shape of `test/scripts/test-chart-render.sh`, run in its CI step)

Each check gets its own `pass`/`fail` line, as the neighboring checks do.

- **1a. Defaults deploy nothing.** State: a checkout after `make test-stand-files`. Input: no values file. Shows: zero `kind:` objects. Fails when: a default turns a part on.
- **1b. Missing generated files fail and name the remedy.** State: no `files/` directory. Inputs: `test/k8s/test-stand-values.yaml` (idp on) and `test/k8s/parity/test-stand-values.yaml` (pip-mock with `requestargs.responses.yaml`). Shows: each failure text carries the template's own `make test-stand-files` remedy.
- **1c. Realm set is the old set.** State: generated files. Inputs: both value files. Shows: the e2e `keycloak-realms` ConfigMap holds the four files the old target listed (`authz-test-realm.json`, `cloud-common-realm.json`, `6f1c2a9e-…-realm.json`, `0d9e8f7a-…-realm.json`). The parity ConfigMap holds `cloud-common`, `parity-mt-b` (new and deliberate), and `parity`. Fails when: a realm is dropped or a stray file is picked up.
- **1d. A realm edit restarts Keycloak.** State: a scratch copy of `files/` with one byte changed in one realm. Inputs: render the original twice, then the edited copy. Shows: the `checksum/realms` annotation is identical for identical bytes and differs for the edit. Fails when: the checksum ignores content, so an edited realm never restarts Keycloak. The checksum hashes `toString` of a `Files` object, so this run verifies that it covers the bytes.
- **1e. Restricted-profile fields and selectors are in every render.** Inputs: both value files. Shows, for each container: `runAsNonRoot: true`, `seccompProfile: RuntimeDefault`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, and `readOnlyRootFilesystem: true` except Keycloak. No `runAsUser` anywhere. The suite Job mounts an `emptyDir` at `/tmp`. Every workload selector is `app: <name>`. Fails when: a container loses one of these. This checks the render only; 3c checks the cluster.
- **1f. Shared keys reach the new chart with their old meaning.** `E2E_HELM_ARGS='--set IMAGE_PULL_POLICY=Never'` goes to every install, the stand's included. Shows: the pip-stub, tenant-manager, and suite images carry `Never`, and Keycloak keeps `idp.imagePullPolicy`. The rule in §3 also needs the full list of names both charts read (`TAG`, `IMAGE_PULL_POLICY`, and any others), each with the file and line that reads it. I did not check the agent or policy-admin charts for these keys, so that list is still to be written. Bucket: run plus citation.

### 2. Generated files and the transfer image (medium; scratch worktree; nothing committed)

- **2a. Generation is a no-op on the current inputs.** Run `make test-stand-files`, then compare the generated `parity-realm.json` with the source after `jq -S .` on both. Shows: equal. `git status` is clean, because `.gitignore` covers `files/`. Fails when: the `profile` step rewrites fields on a realm with no user files.
- **2b. The user-file path has no run behind it.** The Dockerfile merges every `*.json` under `test/parity/suite/testdata/realm/` and reads each file as an array of users (`.[1:][][]`). The repo has no such file, so the merge, `profile`, and both duplicate checks never run. Put one fixture user file in the scratch worktree, then check:
  - User `{"username": "parity-r29-level-m2m"}`. Expected: `firstName` `Parity`, `lastName` `R29LevelM2M`, `email` `parity-r29-level-m2m@example.test`.
  - User with `"firstName": ""`. `//=` keeps the empty string, so the profile stays incomplete, while the Dockerfile says Keycloak refuses such a user. **Judgment:** the result either treats `""` as missing or the Dockerfile says a name must be non-empty. This is a candidate defect.
  - Username also in `parity-realm.json`. `jq -e` must fail and the build must stop.
- **2c. The transfer image renders the same chart.** Build the `scratch` final stage. Run `helm template` on the image's `/charts/authz-test-stand` and on the checkout after `make test-stand-files`, with the same values. Shows: identical output. Fails when: the two routes to `files/` diverge.

### 3. Kind (large)

- **3a. Both stands pass on a fresh cluster.** Run `make e2e` and `make parity`. Shows:
  - The runtime suite passes, and its log has no skipped `m2m_keycloak` steps (the values say they are real only with `M2M_KEYCLOAK_PROFILE`).
  - The unregistered realm `0d9e8f7a-…` is refused.
  - The parity suite passes; the `*` default route answers the access-control call; the `parity-mt-b` discovery document answers.
  - Run `make e2e-suite` a second time: the Job is deleted, recreated, and passes.
- **3b. Keycloak under the new arguments.** Shows: the readiness probe on `/auth/health/ready` (management port) passes within the startup probe's five minutes. That confirms `KC_HEALTH_ENABLED` replaced `--health-enabled=true`, and that the relative path applies to management. The commit also drops `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` without a sentence. **Judgment:** either the PR says why it has no effect on a dev-mode H2 database that is fresh at each start, or the option comes back.
- **3c. Restricted Pod Security Standard.** State: a namespace pre-labelled `pod-security.kubernetes.io/enforce=restricted`, which `--create-namespace` leaves alone, and `make e2e-harness` into it. Shows: every stand Pod starts. The kubelet refuses `runAsNonRoot` for an image whose `USER` is a name, so the images must name numeric users, and this run shows whether they do. Covers the stand only; the agent chart is outside this change.
- **3d. Inherited state (the largest gap).**
  - State: at 58316ca, run `make e2e` through `e2e-suite`. This leaves, in `authz-e2e`, the Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, and `tenant-manager`; the ConfigMap `keycloak-realms`; the Secret `authz-agent-client-credentials`; and the ServiceAccount and Job `runtime-suite`.
  - Action: check out 33acfe1 and run `make e2e-harness`.
  - Expected: Helm refuses to adopt the unowned objects. Quote the exact output in the PR.
  - Current state: the commit has no remedy. The Makefile does not delete the old objects, and no doc names a step. `e2e-cluster` reuses a cluster, so a developer's kept cluster hits this, while CI, which starts clean, does not.
  - Required: either a documented remedy, such as `make e2e-down` first or deleting the named objects, verified on this state, or an automated step that does it once. Then `make e2e-harness` and `make e2e-suite` must pass.
  - Parity has the same issue with `parity-realms`, `pip-mock-config`, `authz-agent-client-credentials`, and the parity suite's Job.
- **3e. Failure runs for the replaced suite mechanism (§3).**
  - **Fault 1: the image is absent** (skip `kind load` for `local/authz-runtime-suite:ci`). Run the old target at 58316ca and the new at 33acfe1 on this fault, and record each duration and output.
    - Old: `kubectl wait --for=condition=Ready pod … --timeout=3m` fails after about 3 minutes, and `make` stops.
    - New: the `wait --for=create` passes at once. The log loop runs about 3 minutes. `logs -f` fails. `wait $helm_pid` returns only when `helm test` gives up, at its 15-minute timeout or the Job's `activeDeadlineSeconds: 900`, whichever fires first. Both are 15 minutes, so which one fires is part of the result.
    - Expected: the new one fails about 12 minutes later and prints less. §3 requires either a deadline that bounds the whole wait at about the old 3 minutes, or a reason in the PR.
  - **Fault 2: the suite fails a case** (a scratch install with a wrong credential). Shows: `make e2e-suite` exits non-zero, since the recipe's last command is `wait $helm_pid`, and the log is streamed. Fails when: the exit status is lost.

### 4. Not owed here

- The pip-stub default route and its tests are in `test/integration/pipstub/main_test.go`; the parity run in 3a exercises the route.
- The §1 red run does not apply: the move fixes no bug. Each check above names the change it would catch.

**For the PR description:** the run outputs, with the durations for 3e; the inherited-state remedy for 3d; decisions on `JAVA_OPTS_APPEND` (3b) and on `""` names (2b); the stack-line proposal; and a sentence on each judgment above.
