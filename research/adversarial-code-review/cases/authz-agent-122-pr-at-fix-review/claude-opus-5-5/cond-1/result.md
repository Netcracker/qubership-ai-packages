# PR/MR review

Result: REQUEST_CHANGES (1 blocking, 3 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] The SVT Keycloak version bump is not claimed by any commit

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`

- Problem: Commit 8b85515 changes the SVT compose stack's Keycloak image from `quay.io/keycloak/keycloak:26.0` to `26.3.5@sha256:…`. None of the four commit messages mentions the SVT stack: 8b85515 describes Keycloak only as part of the new test-stand chart. This is a runtime dependency version change in a load-test environment the PR otherwise leaves alone, so the SVT results can change without anything saying so.
- Proposed solution: Add a sentence to the commit message that claims the bump and cites an SVT run on 26.3.5 (for example `svt-load-test.yaml` or `test/svt/scripts/up`), or move the hunk to its own change.

### [non-blocking] The documented way to run a longer suite misses `-test.timeout`, and the new variables are not in the override list

Confidence: high

`Makefile:49-52`, `helm-templates/authz-test-stand/README.md:69-70`, `test/k8s/README.md:66-67`

- Problem: 5dcb6be says it lets a suite outlast 15 minutes by raising `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. But `suite.args` in `values.yaml:95-96` and `test/k8s/test-stand-values.yaml:55-56` passes `-test.timeout 600s`, so the Go binary aborts at 10 minutes whatever those two settings say. Raising them as documented has no effect. Separately, `test/k8s/README.md` lists the Makefile overrides (`KIND_CLUSTER`, `E2E_NAMESPACE`, …, `E2E_HELM_ARGS`, `E2E_BASE_URL`) but not the two new variables.
- Proposed solution: Name `-test.timeout` in `suite.args` in the Makefile comment and the chart README as the third limit to raise, and add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the override list in `test/k8s/README.md`.

### [non-blocking] A suite Pod that never starts now fails after about 15 minutes instead of 3

Confidence: medium

`Makefile:105-112`

- Problem: The troubleshooting table names the most common fault: the Job Pod stays `Pending` or reports `ErrImageNeverPull`.
  - The old recipe failed after 3 minutes at `kubectl wait --for=condition=Ready pod … --timeout=3m`.
  - The new recipe polls logs for about 3 minutes, then `kubectl logs -f` fails, then `wait $helm_pid` blocks. Helm returns only when `helm test --timeout 15m` expires or the Job hits `activeDeadlineSeconds: 900`, so the failure arrives about 15 minutes after the Job is created.
  - That is inside the 30-minute `timeout-minutes` of `kind-e2e`/`kind-parity`, together with the image build, harness and install steps. No commit message accepts the later failure.
- Proposed solution: Bound the whole wait at the old time to fail. For example, end the run (stop helm and exit non-zero) when the Pod is not Running once the log poll has run out. Or state in writing that the slower failure is accepted, and attach a run of this fault showing its duration and output.

### [non-blocking] `kubectl wait --for=create` needs kubectl 1.31+, and the prerequisites do not say so

Confidence: medium

`Makefile:108`, `docs/local-integration-tests.md:37`

- Problem: The `create` condition of `kubectl wait` first appeared in kubectl 1.31. With an older client, `--for=create` fails at once, the `&&` skips the log poll, and `kubectl logs -f` can run before the container starts. The suite log is then never streamed, and Helm 4's `helm test` prints none either, so a failed run shows only its exit status. The prerequisites table lists kubectl with no minimum version.
- Proposed solution: State kubectl ≥ 1.31 in the prerequisites table, or use a wait that older clients support, such as polling `kubectl get job/<name>`.

Verification done during this review:
- `go test` in `test/integration/pipstub` passes.
- With the `chart-files` stage reproduced locally with jq in a scratch copy of the chart, `helm lint` (Helm 4.3.0) passes for both values files, and `helm template` renders.
- Changing the content of one realm file changes `checksum/realms`.
- No repository file was modified.
