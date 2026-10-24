I read the skill and opened `references/go/testing.md` and `references/go/testify.md`, since the stand's verdict is the e2e suite's report. The repo has no bash, Make, or Helm reference, so the chart and harness checks below follow `test/scripts/test-chart-render.sh` and the skill's general rules. Nothing was run or changed: there is no cluster or Docker daemon here, so every run below is a plan, and the predictions in it are unverified.

---

**Subject: Tests the kind-harness move owes (33acfe1)**

This commit changes behavior, and it adds no test for the move. The harness objects are now Helm-owned. Waits moved from `kubectl wait` and `rollout status` to `helm --wait` and `helm test`. The stand takes values that the agent charts also read through `E2E_HELM_ARGS`. Realm and stub files are generated. The stand also runs under the restricted Pod Security Standard.

CI today runs `helm lint` on the stand, and `test/scripts/test-chart-render.sh` renders only `authz-agent` and `authz-policy-admin`. A green `kind-e2e` does not show that the checks ran. `go test -run` that matches nothing exits 0, and gated checks skip rather than fail.

**Stack.** `AGENTS.md` has no stack line. Proposed for it, not edited: "Tests: Go `testing` with testify v1.9.0 in `test/integration/testify` and `test/parity/suite`; chart and harness checks are bash in `test/scripts/`."

**Levels.** No small test is possible; every behavior sits in templates, Make, or a cluster. `helm template`, the Docker `chart-files` stage, and `jq` are medium, since they read the local machine. kind runs are large.

### A. Render and generation (medium, bash in `test/scripts/`, reports each failed check under its label and continues)

- **A1. Default render.** Input: no values file. Expect zero objects and no error. Shows the "every part off by default" promise in `values.yaml`. (T2)
- **A2. Object set per harness.** State: after `make test-stand-files`. Inputs: the e2e and parity values files. Expect these literal sets. E2e: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`; Job `runtime-suite` carrying the `helm.sh/hook: test` annotation. Parity: `idp`, `idp-realms`, `pip-mock`, `pip-mock-config`, `entitlements-mock`. These are the names B1 depends on. (T2, T4)
- **A3. Missing generated files.** Input: no `files/` directory. Expect a failure that names `make test-stand-files` (`idp.yaml:4`, `pipstub` check in `pip-stub.yaml`). Control: with `files/` present, the same render succeeds. (T1)
- **A4. Required keys.** Inputs: suite enabled with `TAG` unset; `clientCredentials` enabled with an empty username; `tenantManager` enabled without `imageRepository`. Expect each named error. Control: each with its key set renders. (T1)
- **A5. Realm restart.** State: a copy of the chart in a temp directory. Render, render again unchanged, change one byte of one realm file, render again. Expect the `checksum/realms` annotation (`idp.yaml:35`) equal for the unchanged pair, different after the change, and no other change in the Keycloak Pod spec. This is the claim the `e2e-harness` comment makes. (T2)
- **A6. Generated realms.** State: Docker, after `make test-stand-files`. Expect `files/realms/e2e/` to hold four files, each byte-equal to its source in `test/k8s/authn/` and the same four names the old harness applied (`git show HEAD~1:Makefile`, line 76). Expect `parity-realm.json` equal to its source, since no user files exist. Negative: two user files with one username must fail the stage's `jq -e` uniqueness check. (T2)
- **A7. `profile.jq`.** State: the file copied to a temp `HOME` as `.jq`, as the stage does. Inputs: user `parity-r29-level-m2m` with no names. Expect `firstName` Parity, `lastName` R29LevelM2M, `email` parity-r29-level-m2m@example.test. Control: a user declaring all three keeps them. No user file exists in the repo, so this is the only test of that path. (T2)
- **A8. Pass-through, render.** Input: e2e values plus `--set IMAGE_PULL_POLICY=Never --set TAG=x`. Expect the pip-stub, tenant-manager, and suite images and pull policies to take both values, and `idp` to keep its own pull policy. Control: no `--set`. The same keys are read by the agent (`deployment.yaml:153-154`) and policy-admin (`deployment.yaml:79-80`). (T2, T4)
- **A9. Names the Makefile depends on.** Input: e2e values render. Expect every name in `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` to be a Deployment in the render. (T4)

### B. Runs on kind (large). Each run states its times and output in the PR.

- **B1. Inherited state (required by §3).** State: a cluster built by the parent commit's `make e2e`, plus its parity objects in `authz-parity`. Action: `make e2e-harness` at HEAD. Prediction, unverified: Helm refuses at install, naming the first object it cannot adopt. The current message names no remedy. Then run the documented remedy at HEAD (`make e2e-down`, then `make e2e`), and expect it to pass. The remedy must be written in `test/k8s/README.md`; `docs/local-integration-tests.md:193` documents `make e2e-down` only for a leftover cluster. (T1)
- **B2. Harness failure, old against new.** Fault 1: `pip-stub` image not loaded. Old: `rollout status deploy/pip-stub --timeout=2m` fails at about 2 minutes. New: `helm --wait --timeout 10m` fails at 10. Fault 2: Keycloak never ready. Old: `rollout status deploy/keycloak --timeout=10m`, after three 2-minute waits. New: one 10-minute wait for everything. The new one fails later on fault 1, so the PR must bound the harness wait at the old time or give a reason. (T1)
- **B3. Suite pass.** Expect exit 0, and the log's `--- PASS` count to match the top-level tests of `TestRuntimeSuite`. Expect no `--- SKIP` for the M2M checks, since `M2M_KEYCLOAK_PROFILE` and `FULL_RUNTIME_SUITE` are set. (T1)
- **B4. Suite fails.** Input: `E2E_HELM_ARGS='--set suite.env.KC_PASSWORD=wrong'`. Expect `helm test` to exit non-zero, the log to name the failing test, and `make` to exit non-zero. Old: `logs -f`, then `wait --for=condition=Complete --timeout=1m` fails. (T1)
- **B5. Pod never starts.** Fault: suite image not loaded. Old: `wait --for=condition=Ready pod --timeout=3m` fails near 3 minutes. New: the poll loop passes and `wait $helm_pid` blocks until `helm test`'s 15-minute timeout. Prediction: about 15 minutes. The PR bounds it at the old time or gives a reason. (T1)
- **B6. API server silent during the poll.** Action: `docker pause` the kind control-plane container during the loop. `kubectl logs` has no default request timeout, and the loop runs in the foreground while `helm` runs in the background. Prediction: `make e2e-suite` passes `helm`'s 15-minute deadline and ends only on unpause or at CI's 30-minute job timeout. The old `logs -f` had the same unbounded call, but the new loop adds more. The PR bounds the calls, for example with `--request-timeout`. (T1)
- **B7. Restricted Pod Security Standard.** State: a new namespace labeled `pod-security.kubernetes.io/enforce=restricted`, with the stand alone and `suite.enabled` false. Expect every Pod admitted, `--wait` successful, and no `forbidden` events. Keycloak's image user is not in the repo, so this run is the only evidence for it. The agent and policy-admin charts are not restricted-compliant, and Services resolve only inside a namespace, so this proves the stand, not the suite. (T1)
- **B8. Lifecycle targets.** Run `make e2e-restart` after `make e2e-images`, then `make e2e-logs`. Expect every restarted Deployment Ready, and `kubectl exec deploy/pip-stub -- wget` to work under the read-only root filesystem. (T1)
- **B9. Pass-through run.** Run `make e2e-harness E2E_HELM_ARGS='--set TAG=x'` after `make e2e-images`, which tags the images `:ci`. Prediction: the stand's Pods fail with `ImagePullBackOff`, and `--wait` runs 10 minutes before it fails. The documented `IMAGE_PULL_POLICY=Never` must still install. The fix is to keep `TAG` for the stand out of `E2E_HELM_ARGS` or to document it. (T1)

### C. Checked from the diff (no run)

- The M2M values now in `test/k8s/test-stand-values.yaml` (`test-app-client` and `test-app-secret`) equal the old `m2m-credentials` files at `HEAD~1`.
- Every environment name in the old `runtime-suite-job.yaml` is in the new values, including `M2M_KEYCLOAK_PROFILE`.
- The four e2e realm files the glob copies are the four the old ConfigMap listed.
- The three local images declare `USER 10001:10001`, so `runAsNonRoot` is satisfiable.
- `docs/local-integration-tests.md:126` says a changed chart value takes `make e2e-install e2e-suite`. For the stand that is `make e2e-harness`. Fix it in this PR.

### D. Not in this plan

- The pip-stub default route and its `main_test.go` are in the same commit and were not reviewed here.
- Installing from the transfer image needs published images, which CI does not run. The release owes one run.

**Summary.** Items A2, A4, A9, and C are from the diff. B1 through B9 are runs, and their predictions must be checked before the PR claims them. Medium is the level for the render checks, and the level choice is a judgment, stated here.
