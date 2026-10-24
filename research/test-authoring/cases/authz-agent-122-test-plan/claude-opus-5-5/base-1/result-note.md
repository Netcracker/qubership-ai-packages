I wrote the test plan below as the message for the PR author. I ran no harness, changed no file and committed nothing. The plan's claims about what will happen on a cluster come from reading the diff and the old manifests at `HEAD^`. They are predictions until the runs below are made.

---

**Test plan for "run the kind harnesses on a test-stand chart with stock Keycloak" (354bf31)**

This change can alter behaviour. It replaces how the kind stands are built (`kubectl apply` became `helm upgrade --install`), how the suite runs and reports (`kubectl wait` plus `logs -f` became `helm test` plus a polling loop), and where the realm files come from (a Makefile list became a Docker stage plus a glob). So it owes tests. The green `Kind end-to-end` and `Parity on kind` jobs already cover one path: a fresh install on a new cluster, with every Pod starting under the new security contexts and both suites passing. Please link those two runs in the PR. Everything below covers what those jobs don't.

### A. Render checks (no cluster): a new section in `test/scripts/test-chart-render.sh`

This is the repo's "render assertions" step, run by the `Lint the charts` job after `make test-stand-files`. That script records every mismatch and names each check by its text (`fail`/`pass`, `test/scripts/test-chart-render.sh:51-58`, exit at `:1000-1007`), so each case below is its own `pass`/`fail` line. Take every expected value as a literal from the old manifests at `HEAD^`, never from `helm template` output.

1. **The suite Jobs get the same env and args as the old manifests.** Render with `test/k8s/test-stand-values.yaml`. Compare the Job's env, as a sorted list of `NAME=value`, with the 22 variables of `HEAD^:test/k8s/runtime-suite-job.yaml`, and its args with the old six. Do the same for the parity Job against the 6 variables of `HEAD^:test/k8s/parity/parity-suite-job.yaml`. The list is sorted because the chart ranges over a map, and order isn't behaviour. Catches a variable dropped or misspelled in the move.
2. **Each stub instance keeps its port and rule file.** The four inputs, each a case:
   - e2e `pip-stub`: 8090, no config;
   - e2e `entitlements-mock`: 8090;
   - parity `pip-mock`: 8090, with `PIP_STUB_CONFIG=/etc/pip-stub/requestargs.responses.yaml` and the mount;
   - parity `entitlements-mock`: **8080**.

   For each, check the container port, `PIP_STUB_PORT`, and the Service port. Catches the parity 8080 being lost behind a shared default.
3. **The Keycloak realm ConfigMap has exactly the expected keys.**
   - e2e: the four files the old Makefile listed.
   - parity: `cloud-common`, `parity`, plus the new `parity-mt-b`.

   Also check `KC_HOSTNAME` and the Service name (`keycloak` / `idp`). Catches the glob picking up an extra or missing file, which was the second failure in d0b56ed.
4. **The client-credentials Secret carries the old values.**
   - e2e: `test-app-client` / `test-app-secret`, from the deleted `HEAD^:test/k8s/authn/m2m-credentials/*`.
   - parity: exactly `ParityM2MSecret1!@#`.

   Catches YAML/quoting damage to `!@#`.
5. **Tenant map.** Three cases:
   - e2e values render exactly `TENANT_MANAGER_TENANTS="default=6f1c2a9e-…"`, with the unregistered realm absent;
   - two tenants render `a=1,b=2`;
   - an empty map fails with `tenantManager.tenants is required`.
6. **Errors that name the remedy.** These are the new mechanism's most likely first-run faults, one test each:
   - `idp.enabled` with no `files/realms/<realms>/` fails with the message naming `make test-stand-files`;
   - a stub `config` naming a missing file fails the same way;
   - no `TAG` fails with `TAG is required`.
7. **The restart checksum follows file contents.** Render twice from the same files: the `checksum/realms` annotation is equal. Then use a temporary copy of the chart with one byte of one realm file changed: the checksum differs. Also add a file: it differs. This is the evidence for "restarting when one changes".
8. **Restricted PSS, enumerated from the render.** For every Pod and container in both harness renders, check:
   - `runAsNonRoot: true`, seccomp `RuntimeDefault`;
   - `allowPrivilegeEscalation: false`, `drop: [ALL]`;
   - `readOnlyRootFilesystem: true` everywhere except the `keycloak` container.

   Read the set of containers from the render rather than listing it by hand, so a part added later without the helpers fails.
9. **Off by default, and selectors unchanged.**
   - `helm template` with no values renders no objects.
   - Every Deployment selector is exactly `app: <name>`. It is immutable on objects that already exist, and `deploy/<name>` and `-l app=` in the Makefile depend on it.
10. **The base URL override lands once.** `--set suite.env.BASE_URL=http://example:1` renders one `BASE_URL` with that value. This replaces the old `sed`.

### B. Generated files (medium: a Docker build, no cluster)

11. **With no user files, the parity realm is unchanged.** Run `make test-stand-files`, then compare `jq -S . files/realms/parity/parity-realm.json` with `jq -S . test/k8s/parity/idp-seed/parity-realm.json`: they are equal. The `e2e/` and `pip-stub/` files are byte-identical to their sources. This is today's only input, and it catches `.[1:][][]` or `profile` corrupting the realm.
12. **One user file is merged and completed.** In a scratch worktree, add one `testdata/realm/*.json` with:
    - `parity-r29-level-m2m`, no profile fields, which must come out `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test` (the value the commit message gives);
    - a user that declares its own `lastName`, which must be kept.

    The expected names come from the stand the goldens were recorded on. No golden in the repo carries `given_name`/`family_name`, so any further username shape needs its value from that stand, not from running `profile.jq`.
13. **Duplicates fail the build.** Two files declare the same username: the build fails. A separate case: the same `id` fails. Also check that a user that duplicates a username already in `parity-realm.json` fails.
14. **The transfer image path from the chart README.** Build the final stage and follow README steps 1–2: copy `/charts` out, then run `helm lint` and `helm template` on `/charts/authz-test-stand` with `--set TAG=x` and the parity values minus the kind keys. Shows that `files/` is in the image even though `.dockerignore` excludes it from the context.

### C. Runs on kind (large), from the state an earlier version left behind

15. **Old harness first, new one over it.** Check out `HEAD^` and run `make e2e`, then check out `HEAD` and run `make e2e-harness e2e-install e2e-suite`. Repeat with `make parity` and the parity targets.
    - **What the old version leaves:** unmanaged Deployments and Services (`keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; parity: `idp`, `pip-mock`, `entitlements-mock`), the ConfigMap `keycloak-realms` (same name as the chart's) and `pip-mock-config`, the Secret `authz-agent-client-credentials`, the ServiceAccount `runtime-suite`, and the Job.
    - **Prediction:** Helm refuses with `… exists and cannot be imported into the current release: invalid ownership metadata`. That message names the object but not the remedy.
    - **What the PR must pick:** keeps working (the Makefile adopts or deletes the old objects), or fails naming the remedy. For a dev harness, documenting `make e2e-down` (or deleting the two namespaces) in `docs/local-integration-tests.md` is enough, but run that remedy on this state and paste the output.
16. **Re-running the harness on the new chart's own release.**
    - Run `make e2e-harness` twice with no realm change: the Keycloak Pod UID is unchanged.
    - Change one realm file (for example, add a user) and run it again: the UID is new, and a password grant for the new user succeeds.
    - Then the documented agent restart is needed before `make e2e-suite` passes.
17. **Re-running after a failed install.** Make `make e2e-harness` fail once (fault 18), fix the cause, and re-run it. Record whether `upgrade --install` proceeds on a release whose only revision failed under Helm v4.3.1, or what it prints.

### D. The replaced mechanisms, run on their faults

For each fault, put both durations and both outputs in the PR.

18. **Harness wait: a part that never becomes Ready.** This is the old mechanism's recorded fault (d0b56ed: "the kind harness never became ready"). Reproduce it faithfully with `local/tenant-manager:ci` built from `d0b56ed^`, which crash-loops on `TENANT_MANAGER_PORT`.
    - **Old:** `rollout status deploy/tenant-manager --timeout=2m` failed after about 2 min plus the stub waits, naming the Deployment.
    - **New:** one `helm --wait --timeout 10m` (`Makefile:86`, `:150`).
    - **Prediction:** it fails at about 10 min, and Helm's message may not name which part.

    Either bound it nearer the old time or give the reason (Keycloak's cold start needs a long bound), and make the output name the unready part.
19. **Suite run: the Pod never starts.** For example, drop `local/authz-runtime-suite:ci` from the node so the Pod hits `ErrImageNeverPull`.
    - **Old:** `wait --for=condition=Ready … --timeout=3m` failed at about 3 min with "timed out waiting for the condition".
    - **New:** the loop's 90 `kubectl logs` attempts fail, then `logs -f` fails, then `wait $helm_pid` (`Makefile:102-106`) blocks until `helm test --timeout 15m` or the Job's `activeDeadlineSeconds: 900` fires.
    - **Prediction:** about 15 min.
20. **Suite run: the fault where one attempt waits longest.** Counting attempts as the skill asks:
    - `kubectl logs job/…` sets no `--request-timeout`, so each attempt counts as never returning; with one, an attempt is up to `--pod-running-timeout` (20 s default) plus the request timeout, plus the 2 s sleep.
    - `delete job --wait` has no timeout either.

    So the recipe as a whole has no bound except CI's. Run it with the kind control-plane container paused mid-loop and record it. Then add one deadline over the whole wait, last attempt included.

### E. Limits on the same work, cited by file and line

21. The suite runs under four limits:
    - `-test.timeout 600s` (`values.yaml:96`);
    - `activeDeadlineSeconds: 900` (`values.yaml:99`), counted from Job start;
    - `helm test --timeout 15m` (`Makefile:102`), counted from before the Job exists, and not configurable;
    - the CI job's `timeout-minutes: 30` (`integration-tests.yaml:120`, `:168`).

    At the defaults, Go's 600 s fires first. That is right, and a citation of these lines is enough. Two cases need a run:
    - `--set suite.activeDeadlineSeconds=1000` with a suite that hangs (for example, `suite.args` running `sleep 1200`): record which limit fires and what the user sees.
    - At the defaults, Helm's 15 min and the Job's 900 s race. Helm's probably wins and hides the Job's `DeadlineExceeded`.

    Also note that 10 m (harness) + 2 × 5 m (installs) + 15 m (suite), plus image builds, exceeds the CI job's 30 m. CI can cancel before Helm reports anything, so confirm that `e2e-logs` still collects in that case.
22. **Restricted PSS on a real cluster.** Label the namespace `pod-security.kubernetes.io/enforce=restricted` before `make e2e-harness` and `make parity-harness`. Every Pod is admitted and Ready, and both suites pass. The render check (8) can't show that the images run as non-root and work with a read-only root filesystem.

### One line each in the PR (no test owed)

- The doc, README and comment edits, and the testify `helpers.go`/`Dockerfile` comment changes, cannot change behaviour.
- `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` was dropped from the e2e Keycloak. Every Pod and container start begins with a fresh H2 database, so the import never meets an existing realm. That makes the drop equivalent; say so.
- The new `docker.cfg` and release entries are covered only by the release job's own build. Name that surface.

### Stack line proposal

`AGENTS.md` names no test stack. Proposed line, to be added only if a maintainer agrees: `Tests: Go testing (unit), testify suites (test/integration/testify, test/parity/suite); chart render checks in test/scripts/test-chart-render.sh, which report every failed check by its text.`

---

Each item is settled by a different kind of evidence:
- **Read off the diff:** items 1–10 (render checks).
- **Need a run:** 11–20 and 22. The kind runs in 15–20 and 22 were all out of reach here, with no kind cluster or Docker.
- **Need file and line citations:** 21, plus runs for its two racing cases.
- **Judgment calls stated above:** the equivalence of the dropped `OVERWRITE_EXISTING`, and documenting a remedy for item 15 rather than adopting the old objects.

The commit also carries the pip-stub default route and its own `main_test.go`. That isn't part of the move, so I didn't review it here.
