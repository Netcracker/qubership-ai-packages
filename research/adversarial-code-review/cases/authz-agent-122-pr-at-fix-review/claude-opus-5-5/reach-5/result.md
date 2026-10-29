# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] No commit message claims the new parity-realm fixtures or the SVT Keycloak bump

Confidence: high

`test/k8s/parity/idp-seed/parity-realm.json:27-34, 103-328, 340-363, 448-507`; `test/svt/common/compose/docker-compose.yml:3`

- Problem: `parity-realm.json` gains `ROLE_MT_READER`/`ROLE_MT_ADMIN`, the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, and the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The only sentence about this file is "The parity realm gains a second tenant realm, parity-mt-b", and `git grep` finds none of these names outside `idp-seed/`, so nothing in this change uses them. Separately, the SVT Compose stack moves from `keycloak:26.0` to `26.3.5@sha256:…`, which changes the SVT environment, and no commit mentions SVT.
- Proposed solution: Add commit-message sentences that claim each hunk, naming the cases or run that use them. Otherwise move both hunks to their own changes, for example with the cases that use the fixtures.

### [blocking] Raising the documented limits does not let a suite run past 10 minutes

Confidence: high

`Makefile:49-52`, `helm-templates/authz-test-stand/README.md:65-70`, `helm-templates/authz-test-stand/values.yaml:92-99`, `test/k8s/test-stand-values.yaml:52-58`

- Problem: The last commit is meant to "let a suite outlast 15 minutes". To do that, the Makefile and the chart README say to raise `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. Both suites still pass `-test.timeout 600s` in `suite.args`, so the test binary panics after 10 minutes whatever the other two limits say. The chart README also says to set `--timeout` "at least as long as" `activeDeadlineSeconds`, and the defaults are equal (15m and 900s). Helm's timer starts before the Job exists, so at equal values `helm test` times out first and leaves the Job running.
- Proposed solution: Document `-test.timeout` in `suite.args` as the innermost limit. State the order: test timeout < `activeDeadlineSeconds` < helm `--timeout`, with a margin for Pod start. Make the defaults follow that order.

### [non-blocking] `kubectl wait --for=create` requires kubectl 1.31 or newer

Confidence: medium

`Makefile:108`

- Problem: `run-suite` waits for the Job with `--for=create`, which kubectl added in 1.31. The prerequisites table in `docs/local-integration-tests.md` sets no minimum kubectl version. With kubectl 1.30, the `&&` chain skips the poll loop and `kubectl logs -f` may run before the Job's container exists, so the log is lost. Helm 4 prints nothing for a Job hook. The exit code is still correct because it comes from `wait $helm_pid`.
- Proposed solution: State the kubectl minimum version in the prerequisites table, or wait for the Job with a poll that works on older kubectl (for example `kubectl get job` in the existing loop).

### [non-blocking] The new suite-timeout variables are missing from the list of overrides

Confidence: high

`test/k8s/README.md:66-71`

- Problem: The README lists every Makefile override (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) but not `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`, which the last commit adds. A reader of the harness page cannot find them.
- Proposed solution: Add both variables to that paragraph and say how they relate to `suite.activeDeadlineSeconds` and `-test.timeout`.

Checks run for this review:
- **Generated files:** built the `chart-files` stage into the scratchpad. The generated files went to a scratchpad copy of the chart, so no file in the repository changed.
- **Lint and render:** `helm lint` passed with the default values and with both stand values files. `helm template` rendered both stands.
- **Chart behaviour:** the `checksum/realms` annotation changes when a realm file changes, and the template fails as documented when a pip-stub rule file is missing.
- **pip-stub:** `go test` passes.
- **Read-only root filesystem:** I ran the local `qubership-core-base:2.4.2`-based suite image read-only, with all capabilities dropped. It started both as uid 10001 and as an OpenShift-style random uid with gid 0, so the restricted security context does not break the base image's entrypoint.
- **Not run:** no Kubernetes cluster was available, so the `helm test` flow itself was not run.
