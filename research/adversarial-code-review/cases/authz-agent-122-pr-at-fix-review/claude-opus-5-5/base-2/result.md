# PR/MR review

Result: APPROVE (0 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [non-blocking] The guidance for longer suites leaves out `-test.timeout 600s` and the 30-minute CI job limit

Confidence: high

`Makefile:49-52`, `helm-templates/authz-test-stand/values.yaml:92-99`, `helm-templates/authz-test-stand/README.md:69-70`

- Problem: The Makefile tells a longer suite to raise `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` "together with suite.activeDeadlineSeconds". The README says the same about `--timeout`. But `suite.args` in both values files still passes `-test.timeout 600s`. Followed as written, a suite therefore still fails at 10 minutes, with a Go test-timeout panic, before either of the raised limits applies. In CI, the `kind-e2e` and `kind-parity` jobs also have `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml`). That limit covers the image build, a harness wait of up to 10 minutes and two installs of up to 5 minutes each, so raising the suite timeout above roughly 15 minutes is cut off by the job limit there. Separately, at the defaults `helm test --timeout 15m` starts counting before the Job's 900 s deadline does, so it is in fact slightly shorter than that deadline, not "no shorter".
- Proposed solution: Name `-test.timeout` in `suite.args` as the innermost limit that has to be raised first, require each outer limit (`activeDeadlineSeconds`, then the helm `--timeout`) to be larger than the one inside it, and state that CI's `timeout-minutes: 30` caps the total.

### [non-blocking] `run-suite` needs kubectl 1.31 or later, which the docs do not say

Confidence: medium

`Makefile:108`, `docs/local-integration-tests.md:37`

- Problem: `kubectl wait --for=create` exists only in kubectl 1.31 and later. The prerequisites table lists kubectl with no version. With an older client the `&&` chain stops at once, `kubectl logs -f` can run before the Pod exists, and the suite log may never be streamed. Helm 4 prints nothing for a Job hook either, so the run can end with only an exit code. The exit code itself stays correct because of `wait $helm_pid`.
- Proposed solution: State kubectl ≥ 1.31 in the prerequisites, or replace `--for=create` with a poll loop like the existing log loop.

Verification run for this review:
- `go test ./...` in `test/integration/pipstub` passed.
- I generated the chart files locally with the Dockerfile's jq merge and `profile.jq`. `helm lint` passed for both harness values files, and `helm template` rendered both, plus the chart with its default values.
- The `checksum/realms` annotation changes when a realm file's content changes.
- `make -n` shows that `run-suite` and `parity-harness` expand as intended.
- The documented `--set suite.env.RUNTIME_SUITE_RUN=…` subset form renders as intended.

Not verified (no cluster here):
- Pod Security admission and read-only root filesystems at runtime.
- How `helm test` handles the Job hook.
- How the release actions treat `build_context` per component.
