# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 3 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] `E2E_HELM_ARGS` now reaches the test-stand chart, which also reads `TAG` and `IMAGE_PULL_POLICY`

Confidence: high

`Makefile:90`, `Makefile:155` (comment at `Makefile:45-48`, `test/k8s/README.md:67`)

- Problem: `E2E_HELM_ARGS` used to reach only the agent and policy-admin installs. It now also reaches the test-stand install. The test-stand chart reads the same top-level keys as those charts: `TAG` and `IMAGE_PULL_POLICY` (`templates/pip-stub.yaml`, `suite.yaml`, `tenant-manager.yaml`). Suppose someone passes `--set TAG=<version>` to test published agent images. The stand then asks for `local/pip-stub:<version>`, `local/tenant-manager:<version>` and `local/authz-runtime-suite:<version>` with `IMAGE_PULL_POLICY: Never`. None of these is built, so `make e2e-harness` waits its full 10 minutes and fails. With `--set IMAGE_PULL_POLICY=Always`, the stand tries to pull `local/...` images from a registry. Only the documented example (`IMAGE_PULL_POLICY=Never`) has the same meaning in both places.
- Proposed solution: Give the test-stand install its own pass-through variable, such as `TEST_STAND_HELM_ARGS`, and keep `E2E_HELM_ARGS` on the two product charts. If `E2E_HELM_ARGS` is kept on all three installs, add a run that sets `TAG` through it.

### [blocking] Hunks that no commit message claims

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json:27-36,104-330,341-500`, `.github/docker-dev-config.json:12-26`

- Problem: The SVT compose stack moves from Keycloak `26.0` to `26.3.5@sha256:…`, which changes the SVT environment. No commit mentions SVT. The commits also add a lot to the existing `parity` realm: roles `ROLE_MT_READER`/`ROLE_MT_ADMIN`, the `parity-level-claim` mapper, clients `parity-m2m-tenant-a`/`-b`/`-unknown`/`-empty` and `parity-end-user-tenant-a`, and users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The only matching sentence is "The parity realm gains a second tenant realm, parity-mt-b", and a search of the repository finds no test that uses these clients or users. `.github/docker-dev-config.json` adds three images to the CI dev build, but the commit message names only `.qubership/docker.cfg`.
- Proposed solution: Add a commit-message sentence for each of these hunks, naming the run that checks it, such as the SVT run on 26.3.5 and the cases that use the new parity clients and users. Otherwise move the hunks to their own changes.

### [non-blocking] A missing image now fails much later

Confidence: medium

`Makefile:89-90`, `Makefile:105-112`

- Problem: The troubleshooting table names "Job Pod … `ErrImageNeverPull`" as a known fault.
  - **Suite image missing:** the old `e2e-suite` failed after 3 minutes, on `wait --for=condition=Ready pod --timeout=3m`. The new `run-suite` polls for about 3 minutes, `kubectl logs -f` fails, and then `wait $helm_pid` blocks until the Job's `activeDeadlineSeconds` or `--timeout`. That is about 15 minutes, inside a CI job capped at `timeout-minutes: 30`.
  - **Stub or emulator image missing:** the old `rollout status --timeout=2m` failed after 2 minutes. The single `helm --wait --timeout 10m` now fails after 10 minutes.
- Proposed solution: Either state in writing that the slower failure is accepted, or end the suite wait early when `kubectl logs -f` fails because the container never started. One way is to check the Pod's waiting reason and kill `helm_pid`.

### [non-blocking] Prose still counts two dev images

Confidence: high

`README.md:59`, `.github/docs-for-publication-task.md:77`

- Problem: `.github/docker-dev-config.json` now lists five images. `README.md:59` still says "CI builds both via `.github/docker-dev-config.json`", and `docs-for-publication-task.md:77` still describes "The two-entry array".
- Proposed solution: Update both sentences to the new set, or say that the test-stand images are built too.

### [non-blocking] `E2E_BASE_URL`/`PARITY_AC_BASE_URL` no longer take effect at `e2e-suite`/`parity-suite`

Confidence: high

`Makefile:90`, `Makefile:155`, `test/k8s/README.md:68-71`

- Problem: Before this change, `make e2e-suite E2E_BASE_URL=…` passed the address into the Job. Now the value is baked into the release at harness time, and the same command silently uses the old address. The README documents this, but nothing warns someone who uses the old invocation.
- Proposed solution: Pass the address at suite time, for example with `helm upgrade --reuse-values --set suite.env…` inside `e2e-suite`/`parity-suite`. Alternatively, have the suite targets refuse a value that differs from the release's.

Checks run during this review:
- `go test` in `test/integration/pipstub` passes.
- `docker build --target chart-files` generates the expected files, writing to a scratch directory rather than the checkout.
- `helm lint` and `helm template` (Helm 4.3.0) pass for both test-stand values files.

The chart was not installed on a cluster, and `helm test` was not run.
