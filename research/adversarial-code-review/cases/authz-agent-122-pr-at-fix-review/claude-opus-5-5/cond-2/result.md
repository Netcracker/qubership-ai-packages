# PR/MR review

Result: REQUEST_CHANGES (1 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] Unclaimed Keycloak version change in the SVT compose stack

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`

- Problem: The SVT load-test stack moves from `quay.io/keycloak/keycloak:26.0` to `26.3.5@sha256:…`, but none of the four commit messages mentions SVT or this compose file. `.github/workflows/svt-load-test.yaml` starts this stack, so the change alters a runtime dependency version outside the kind harnesses the PR describes. Nothing shows the SVT scenarios were run against 26.3.5.
- Proposed solution: Either add a sentence to a commit message that claims the bump, with an SVT run on the new image as evidence, or move the hunk to its own change.

### [non-blocking] Raising the suite timeouts as documented does not let a suite run past 10 minutes

Confidence: high

`Makefile:48-52`, `helm-templates/authz-test-stand/values.yaml:92-99`, `helm-templates/authz-test-stand/README.md:69-70`, `test/k8s/README.md` (the override list under "Run")

- Problem: The Makefile comment and the chart README say a longer suite should raise `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. But `suite.args` in both `values.yaml` and `test/k8s/test-stand-values.yaml` passes `-test.timeout 600s`, so the test binary panics after 10 minutes whatever the other two limits say. The commit's stated aim, letting a suite outlast 15 minutes, is therefore not reachable by following the docs. Also, the list of Makefile overrides in `test/k8s/README.md` (`KIND_CLUSTER`, `E2E_NAMESPACE`, …, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) does not include the two new variables.
- Proposed solution: Name `-test.timeout` in `suite.args` as the third limit to raise, keep it below `activeDeadlineSeconds` in the guidance, and add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the override list in `test/k8s/README.md`.

### [non-blocking] A suite Pod that never starts now fails after about 15 minutes instead of about 3

Confidence: medium

`Makefile:100-115`

- Problem: The old `e2e-suite`/`parity-suite` stopped after `kubectl wait --for=condition=Ready pod … --timeout=3m` when the suite Pod could not start: `ErrImageNeverPull`, which the troubleshooting table lists, or a missing Secret. In the new `run-suite`, the log-polling loop gives up after about 3 minutes and `kubectl logs -f` fails at once. `wait $helm_pid` then blocks until `helm test --timeout 15m` expires or the Job hits `activeDeadlineSeconds: 900`. The same fault now uses about 15 minutes of the 30-minute `timeout-minutes` budget of the `kind-e2e`/`kind-parity` CI jobs, after image builds, the 10-minute harness wait and the installs. No commit accepts this slower failure.
- Proposed solution: Provide a run of this fault (for example, a suite image not loaded into kind) showing duration and output, and either accept the slower failure in writing or bound the start-up phase, for example by failing when the Pod is not running within the old 3 minutes.

What I ran and checked:
- **pip-stub:** `go test` and `go vet` pass.
- **Chart:** I generated `files/` with the `chart-files` stage into a scratchpad copy of the chart. With those files, `helm lint` and `helm template` pass for both harness values files.
- **Restricted Pod Security Standard:** every image sets a numeric non-root `USER` (pip-stub, tenant-manager and both suites use 10001; the stock Keycloak image uses 1000, from my knowledge rather than a file in this repo), so `runAsNonRoot` without `runAsUser` is valid.
- **Upgrading an old cluster:** the "invalid ownership metadata" remedy, `make e2e-down`, deletes the whole kind cluster, so it covers the e2e and parity namespaces.

I did not change or commit anything in the repository.
