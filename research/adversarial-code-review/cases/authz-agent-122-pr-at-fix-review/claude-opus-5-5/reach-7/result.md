# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 3 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] The parity realm gains clients, users, roles and a mapper that no commit message mentions and nothing uses

Confidence: high

`test/k8s/parity/idp-seed/parity-realm.json:29-500` (also `test/k8s/parity/idp-seed/parity-mt-b-realm.json`)

- Problem: The only commit sentence covering this data is "The parity realm gains a second tenant realm, parity-mt-b." However, `parity-realm.json` also gains:
  - the roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`;
  - the mapper `parity-level-claim`;
  - the clients `parity-m2m-tenant-a`, `-tenant-b`, `-tenant-unknown`, `-tenant-empty` and `parity-end-user-tenant-a`, with their service-account users;
  - the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`.

  None of these names appear anywhere in the repository outside `idp-seed/`. The `TestTenantScopedDecisions` case that the role description cites does not exist. This changes the realm that the 135 parity goldens run against, and no run is attached that checks the change.
- Proposed solution: Either add a commit sentence that claims these realm additions and attach a parity run on them, or move the additions and `parity-mt-b-realm.json` into the change that adds the cases that use them.

### [blocking] Unclaimed Keycloak upgrade in the SVT Compose stack

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`

- Problem: The SVT Compose Keycloak moves from `quay.io/keycloak/keycloak:26.0` to `26.3.5@sha256:…`. No commit message mentions the SVT stack, and the change attaches no SVT run. A Keycloak minor-version change can alter the tokens and timings that SVT measures.
- Proposed solution: Either add a commit sentence that claims the bump and attach an SVT run on 26.3.5, or move the hunk to its own change.

### [non-blocking] With a missing image, `make e2e-suite` / `make parity-suite` now fail after about 15 minutes instead of 3

Confidence: medium

`Makefile:105-111`

- Problem: The troubleshooting table names `ErrImageNeverPull` as a known fault.
  - **Old flow:** `kubectl wait --for=condition=Ready pod … --timeout=3m` failed at 3 minutes.
  - **New flow:**
    1. The log poll runs 90 × (2 s + a failing `kubectl logs`), about 3 minutes.
    2. `kubectl logs -f` then prints the waiting reason.
    3. `wait $helm_pid` blocks until the Job's `activeDeadlineSeconds: 900` or `helm test --timeout 15m` expires, which is about 15 minutes in total.

  The CI jobs `kind-e2e` and `kind-parity` have `timeout-minutes: 30`, and the image builds, the harness install and the chart installs run before this step. The slower failure can therefore push the job close to that limit. The change does not accept the slower failure in writing.
- Proposed solution: Bound the wait once the log poll fails, for example by stopping `helm test` and returning non-zero. Otherwise, state in writing that the slower failure is accepted and attach a run of this fault showing its duration and output.

### [non-blocking] The documented way to give a suite more time misses the suite's own `-test.timeout 600s`

Confidence: high

`Makefile:49-52` (also `helm-templates/authz-test-stand/values.yaml:96-99`, `test/k8s/test-stand-values.yaml:56`, `helm-templates/authz-test-stand/README.md:69-70`)

- Problem: The Makefile comment says a longer suite "raises this together with suite.activeDeadlineSeconds". However, `suite.args` in both values files passes `-test.timeout 600s`, so the Go test binary aborts at 10 minutes. Raising the two documented limits past that does not let a suite run longer, which is the symptom the last commit says it fixes.
- Proposed solution: Name `-test.timeout` in `suite.args` in the Makefile comment and in the chart README as the third limit to raise. Alternatively, derive it from one setting.

### [non-blocking] The new Makefile overrides are missing from the overrides list in test/k8s/README.md

Confidence: high

`test/k8s/README.md:66-71`

- Problem: The paragraph listing the Makefile overrides (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) does not mention `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`. No other page mentions them either.
- Proposed solution: Add both variables to that paragraph. Say that each must be at least the suite's `activeDeadlineSeconds`.

No files were changed. Verification done during this review:
- `go test` for `test/integration/pipstub`: passes.
- Generated the `chart-files` stage into a copy of the chart under the scratchpad.
- `helm lint` with both stand values files: passes.
- `helm template` with both values files and with defaults: renders.
- pip-stub and parity-suite images: started locally with a read-only root filesystem, all capabilities dropped and an arbitrary UID; both start.
