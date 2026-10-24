# PR/MR review

Result: REQUEST_CHANGES (1 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] The documented way to run a suite past 15 minutes still stops it at 10 minutes

Confidence: high

`Makefile:49-52`, `helm-templates/authz-test-stand/values.yaml:92-99`, `test/k8s/test-stand-values.yaml:52-58`, `helm-templates/authz-test-stand/README.md:69-70`

- Problem: The Makefile comment says a longer suite raises `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` "together with suite.activeDeadlineSeconds". However, both suites' `suite.args` also contain `-test.timeout 600s`, so the Go test panics at 10 minutes whatever those two settings say. Commit 5dcb6be states the goal "let a suite outlast 15 minutes", and the documented steps do not achieve it. At the defaults the three limits are not ordered either. `helm test --timeout 15m` starts counting before the Job exists, so it reaches its limit at or before `activeDeadlineSeconds: 900`. Even so, the README advises "at least as long as `suite.activeDeadlineSeconds`", and an equal value is not enough.
- Proposed solution: Name `-test.timeout` in `suite.args` as the third setting to raise, in the Makefile comment and the chart README. Keep the limits in this order: `-test.timeout`, then `activeDeadlineSeconds`, then the helm wait, which should exceed the deadline by a margin for Job creation and image pull. Either change the defaults to match, or document the margin.

### [non-blocking] `make e2e-suite`/`parity-suite` now need kubectl 1.31 or later, and the prerequisites don't say so

Confidence: medium

`Makefile:108`, `docs/local-integration-tests.md:37`

- Problem: `run-suite` uses `kubectl wait --for=create`, which kubectl added in 1.31. The prerequisites table lists kubectl without a version. With an older client the `&&` chain skips the poll loop, and `kubectl logs -f` runs before the Job exists. The run can then lose the streamed log; the exit code still comes from `helm test`.
- Proposed solution: State the minimum kubectl version in the prerequisites table, or wait for the Job with a poll loop that works on older clients.

### [non-blocking] The parity realm gains tenant fixtures that no case in this change uses

Confidence: medium

`test/k8s/parity/idp-seed/parity-realm.json:27-330`, `test/k8s/parity/idp-seed/parity-mt-b-realm.json:1-98`

- Problem: The change adds the realm `parity-mt-b`, the clients `parity-m2m-tenant-*` and `parity-end-user-tenant-a`, the users `mt-a`/`mt-a-admin`/`parity-r29-scope`/`parity-r30-scope`, and the `parity-level-claim` mapper on `parity-end-user`. No file in `test/parity/suite` refers to any of them. The pip-stub commit holds back its stub instance until the cases that use it arrive, and these fixtures don't follow that rule. Unused fixtures cannot be checked against what they claim; the tenant-B `tenant-id` claim is one example.
- Proposed solution: Move these fixtures into the change that adds their cases, or say in the commit message which follow-up uses them.

What I ran during the review:
- `go test` and `go vet` for `test/integration/pipstub`: both pass.
- `helm lint` and `helm template` (Helm 4.3.0) on a scratch copy of the chart, with `files/` copied from the source files rather than produced by the Dockerfile stage. Both harness values files and the defaults render cleanly.
- `checksum/realms` changes when a realm file's content changes.
- `profile.jq` turns `parity-r29-level-m2m` into the last name `R29LevelM2M`, as documented.

The cluster-dependent behaviour (`helm test` with a Job hook, the restricted Pod Security admission) was not run; there is no cluster here.
