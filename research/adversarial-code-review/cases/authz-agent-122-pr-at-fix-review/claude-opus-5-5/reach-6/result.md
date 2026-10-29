# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 1 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] `E2E_HELM_ARGS` now sets `TAG` and `IMAGE_PULL_POLICY` on the test stand, where they mean other images

Confidence: high

`Makefile:46-48`, `Makefile:90`, `Makefile:155`

- Problem: `E2E_HELM_ARGS` used to reach only the authz-agent and authz-policy-admin installs. In both of those charts, `TAG` and `IMAGE_PULL_POLICY` select the product images. The test-stand install now receives the same arguments. In that chart, `TAG` and `IMAGE_PULL_POLICY` select `local/pip-stub`, `local/tenant-manager` and the suite image (`templates/pip-stub.yaml:40-41`, `tenant-manager.yaml:34-35`, `suite.yaml:40-41`). An argument meant for the product charts, such as `E2E_HELM_ARGS='--set TAG=<version>'`, makes the stand ask for `local/pip-stub:<version>`, which `e2e-images` never builds, with pull policy `Never`. Likewise `--set IMAGE_PULL_POLICY=Always` makes the node pull `local/...:ci` from a registry. In both cases `e2e-harness` or `parity-harness` waits its full 10 minutes and then fails.
- Proposed solution: Give the test-stand install its own pass-through variable, for example `TEST_STAND_HELM_ARGS`, and leave `E2E_HELM_ARGS` on the two product charts. If both must stay shared, show a run with a non-default `TAG` passed through `E2E_HELM_ARGS`.

### [blocking] The documented way to run a suite past 15 minutes leaves the 600-second `-test.timeout` in place

Confidence: high

`Makefile:49-52`, `helm-templates/authz-test-stand/values.yaml:92-99`, `test/k8s/test-stand-values.yaml:52-58`, `helm-templates/authz-test-stand/README.md:69-70`

- Problem: The last commit says it lets a suite outlast 15 minutes. The Makefile comment and the chart README say to raise `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. Both the chart default and the kind values pass `-test.timeout 600s` in `suite.args`. That limit fires first, so a suite given longer limits that way still panics after 10 minutes.
  - The kind CI jobs set `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml:120,168`). That covers image builds, a 10-minute harness wait and two 5-minute installs, so in CI a raised suite timeout is capped well below what it says.
  - The list of Makefile overrides in `test/k8s/README.md:66-71` does not include the two new variables.
- Proposed solution:
  - Name `-test.timeout` in `suite.args` in the Makefile comment and in the chart README as the setting to raise as well, with the order of the three limits.
  - Mention the CI job limit.
  - Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the override list in `test/k8s/README.md`.

### [non-blocking] The troubleshooting row for the ownership-conflict error gives the e2e step only

Confidence: high

`docs/local-integration-tests.md:190`

- Problem: The row covers a failure of either `make e2e-harness` or `make parity-harness`, but its fix is "Run `make e2e-down` once, then `make e2e`". `e2e-down` deletes the whole kind cluster (`Makefile:135-136`). Someone who hit the error in `parity-harness` is then told to run the e2e flow, not `make parity`. The cause column also names only `make e2e` as having created the objects. `test/k8s/README.md:47` correctly names both `make e2e` and `make parity`.
- Proposed solution: Name `make parity` in both the cause and the fix for the `parity-harness` case.

Checks run:
- Both kind values files lint and render cleanly against chart files generated from the `chart-files` stage. I wrote those files to a scratch copy, not the checkout.
- The `chart-files` stage merges a sample user file and fills in its profile as documented (`parity-r29-level-m2m` becomes `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test`). It fails the build when a user is declared twice.
- `go test` passes for `test/integration/pipstub`.
- The pip-stub and parity-suite images start with a read-only root filesystem, all capabilities dropped, and an arbitrary uid (`1000770000:0`), as OpenShift's restricted SCC would assign. That supports the restricted Pod Security Standard change.
- Not run: anything on a cluster. There was none, so `helm test`, the log streaming in `run-suite`, and Keycloak startup under the new security context were not exercised here.
