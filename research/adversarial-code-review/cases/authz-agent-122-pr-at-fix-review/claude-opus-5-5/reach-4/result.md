# PR/MR review

Result: REQUEST_CHANGES (3 blocking, 1 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] `E2E_HELM_ARGS` now reaches the test-stand chart, which reads `TAG` and `IMAGE_PULL_POLICY` differently

Confidence: high

`Makefile:44-48`, `Makefile:90`, `Makefile:155`

- Problem: `E2E_HELM_ARGS` used to go only to the authz-agent and authz-policy-admin installs. It now also goes to `authz-test-stand`, which reads two of the same top-level keys. In the product charts, `TAG` is the tag of one product image (`local/authz-agent:ci`). In the test-stand chart, `TAG` sets the tag of `local/pip-stub`, `local/tenant-manager` and `local/authz-runtime-suite`/`authz-parity-suite`, all with `IMAGE_PULL_POLICY: Never`. So `E2E_HELM_ARGS='--set TAG=dev'` or `--set IMAGE_PULL_POLICY=Always`, used to test a rebuilt or released agent, now makes the harness ask for images that nothing builds or loads. The harness then fails its `--wait`.
- Proposed solution: Give the test stand an argument of its own (for example `TEST_STAND_HELM_ARGS`) and stop passing `E2E_HELM_ARGS` to it. If you keep passing it, show a run with `--set TAG=<other>` and document the shared keys.

### [blocking] The way to run a suite longer than 15 minutes leaves out `-test.timeout 600s`, which fires first

Confidence: high

`Makefile:49-52`, `Makefile:103-104`, `helm-templates/authz-test-stand/README.md:69-70`, `helm-templates/authz-test-stand/values.yaml:92-99`, `test/k8s/test-stand-values.yaml:52-58`

- Problem: Commit 5dcb6be says a suite "given a longer deadline in its values" can now outlast 15 minutes if you raise `suite.activeDeadlineSeconds` together with `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT`. Both suites' `suite.args` also pass `-test.timeout 600s`. That limit stops the Go test binary after 10 minutes, below the 900 s Job deadline at the defaults, and before either of the two limits the remedy tells you to raise. If you follow the Makefile comment or the chart README, the suite still dies after 10 minutes with "test timed out". At the defaults, Helm's 15m timer starts before the Job exists, so it fires at or before the Job's own 900 s deadline. That does not match "no shorter than its suite.activeDeadlineSeconds".
- Proposed solution: Name all three limits in the Makefile comment and the chart README (`-test.timeout` in `suite.args` < `suite.activeDeadlineSeconds` < helm `--timeout`). Or derive one from another, so that raising them as documented really extends the run.

### [blocking] Hunks that no commit message claims: SVT Keycloak image bump and new parity-realm fixtures

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json:27-35,100-331` and the user additions

- Problem: The SVT Compose stack moves from `quay.io/keycloak/keycloak:26.0` to `26.3.5@sha256:…`. That changes the SVT benchmark environment, and no commit sentence mentions SVT. `parity-realm.json` gains `ROLE_MT_READER`/`ROLE_MT_ADMIN` and the `parity-level-claim` mapper on `parity-end-user`. It also gains the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, and the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. Commit 8b85515 only claims "a second tenant realm, parity-mt-b". Outside fixture docs, nothing in the repository refers to these new identities (a repo-wide grep finds only realm files and READMEs).
- Proposed solution: Add commit sentences that claim these hunks, with the SVT/parity run that checks them. Or move the hunks into the changes that bring their consumers.

### [non-blocking] The troubleshooting row names both harnesses but gives only the e2e rerun

Confidence: high

`docs/local-integration-tests.md:190`

- Problem: The symptom covers both `make e2e-harness` and `make parity-harness`, and the cause names only "an older `make e2e`". The action is "`make e2e-down` once, then `make e2e`". A parity user who follows it reruns the wrong flow. `make e2e-down` deletes the whole cluster, so `make parity` has to rebuild it. `test/k8s/README.md` already names both `make e2e` and `make parity` as the cause.
- Proposed solution: Name both causes and both reruns (`make e2e` or `make parity`).

What I checked locally: `go test` for `test/integration/pipstub` passes. The `chart-files` Docker stage builds. With an empty `testdata/realm/`, the merged parity realm is identical to the seed file. `helm lint` and `helm template` (Helm 4.3.0) pass for both test-stand values files. The `qubership-core-base:2.4.2` entrypoint completes with a read-only root filesystem, all capabilities dropped and an arbitrary UID. I did not run anything on a Kubernetes cluster.
