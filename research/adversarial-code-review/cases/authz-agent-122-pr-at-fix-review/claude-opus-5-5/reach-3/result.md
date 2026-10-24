# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 3 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] Hunks that no commit message claims: new parity-realm entities and the SVT Keycloak bump

Confidence: high

`test/k8s/parity/idp-seed/parity-realm.json:29-490`, `test/svt/common/compose/docker-compose.yml:3`

- Problem: `parity-realm.json` gains the roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, the `parity-level-claim` mapper, five clients (`parity-m2m-tenant-a/b/empty/unknown` and `parity-end-user-tenant-a`) with their service-account users, and the users `mt-a`, `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope`. The only commit sentence on this is "The parity realm gains a second tenant realm, parity-mt-b", which describes a separate file. `git grep` finds none of these names in any suite, case or golden. The SVT compose file also moves from `keycloak:26.0` to `26.3.5@sha256:…`, and no commit mentions the SVT stack.
- Proposed solution: Add commit-message sentences that claim these hunks, each with the run that exercises it. Otherwise, move the realm entities (and `parity-mt-b-realm.json`, which nothing uses either) into the change that adds their cases, the same way the pip-stub commit defers its stub instance, and move the SVT bump into its own change.

### [blocking] `E2E_HELM_ARGS` now reaches the test-stand chart, where `TAG` and `IMAGE_PULL_POLICY` mean something else

Confidence: high

`Makefile:46-48`, `Makefile:90`, `Makefile:155`

- Problem: `E2E_HELM_ARGS` used to reach only the agent and policy-admin charts. It is now also appended to the test-stand install. The test-stand chart reads the same top-level keys, `TAG` and `IMAGE_PULL_POLICY`, but applies them to `local/pip-stub`, `local/tenant-manager` and the suite images, which `make e2e-images` builds only as `:ci`. A value meant for the product charts, for example `--set IMAGE_REPOSITORY=ghcr.io/... --set TAG=1.0.0` or `--set IMAGE_PULL_POLICY=Always`, therefore makes the stand request images that nothing builds or provides. `helm template … --set TAG=1.2.3` renders `local/pip-stub:1.2.3` and `local/tenant-manager:1.2.3`, and `--set IMAGE_PULL_POLICY=Always` switches 4 containers to pulling a `local/*` image. `make e2e-harness` or `make parity-harness` then fails after its 10-minute `--wait`.
- Proposed solution: Give the test-stand install its own pass-through variable (for example `TEST_STAND_HELM_ARGS`) instead of `E2E_HELM_ARGS`, or show a run with such a value. Update `test/k8s/README.md:67`, which now says the variable reaches "every chart install, the test stand's included".

### [non-blocking] The suite timeout guidance lets Helm expire first, and CI caps any raise

Confidence: medium

`Makefile:49-52`, `Makefile:104`, `helm-templates/authz-test-stand/README.md:69-70`

- Problem: The Makefile and the chart README say to keep the `helm test` timeout "no shorter than" / "at least as long as" `suite.activeDeadlineSeconds`. Helm's clock starts before the Job exists, so with equal values Helm can time out first. It then reports a Helm timeout while the Job keeps running. In CI, the runtime and parity jobs have `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml:120,168`), and image builds, a harness wait of up to 10 minutes, and two 5-minute installs all come out of that budget first. So the longer suite this commit enables can be cut off by the job limit before either suite limit fires.
- Proposed solution: Require the Helm timeout to be strictly longer than the deadline (the deadline plus a margin). Note in the Makefile or the README that a suite running past roughly 15 minutes also needs the CI `timeout-minutes` raised.

### [non-blocking] The troubleshooting row gives only the e2e step for a parity symptom

Confidence: high

`docs/local-integration-tests.md:190`

- Problem: The row's symptom names both `make e2e-harness` and `make parity-harness`, but the action is "Run `make e2e-down` once, then `make e2e`". A parity user who follows it brings up the e2e stand rather than the parity one.
- Proposed solution: Name both follow-ups, for example "then `make e2e` or `make parity`".

### [non-blocking] The transfer-image install starts from a file that the image does not carry

Confidence: medium

`helm-templates/authz-test-stand/README.md:47-49`

- Problem: The procedure is meant for "a stand that installs them without a checkout", yet step 2 says to start from `test/k8s/parity/test-stand-values.yaml`. The transfer image holds only `/charts/*` (`build/authz-agent-transfer/Dockerfile:52-56`), so that file is not available without a checkout.
- Proposed solution: Ship an example values file inside the chart or the image, or inline the values a stand needs in the README.

Verification done for this review:
- `go test ./...` passes in `test/integration/pipstub`.
- I generated the `chart-files` stage into a scratch copy of the chart. `helm lint` (Helm 4.3.0) passes with both values files.
- `helm template` confirmed the `TAG` and `IMAGE_PULL_POLICY` renderings above, and that the documented `RUNTIME_SUITE_RUN` / `FULL_RUNTIME_SUITE` override renders as intended.
- There was no cluster, so none of the kind runs, the restricted Pod Security admission, or the read-only root filesystems were exercised here.
