# PR/MR review

Result: REQUEST_CHANGES (1 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

I used the commit messages for intent, since the GitHub integration was unavailable. I read the Makefile, the new chart, the transfer Dockerfile, the pip-stub changes and the docs. I rendered the chart with both values files in a scratch copy. Both render, with the realm and rule files copied by hand because the generation step needs Docker. I did not run the `jq` stage, `helm test`, or anything on a cluster.

## Findings

### [blocking] Unclaimed Keycloak version bump in the SVT compose stack

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`

- Problem: The image changes from `quay.io/keycloak/keycloak:26.0` to `26.3.5@sha256:3578…`. This is a runtime version change in a stack the PR otherwise doesn't touch. No commit message claims it, and no run of the SVT stack on the new version is cited. The commits describe only the kind harnesses and the new chart.
- Proposed solution: Move the hunk to its own change, or add a sentence to the commit message that claims it, together with a run of the SVT stack on 26.3.5.

### [non-blocking] A suite Pod that never starts now fails after about 15 minutes with little output

Confidence: medium

`Makefile:105-113` (`run-suite`, used by `e2e-suite` and `parity-suite`)

- Problem: The old targets ran `kubectl wait --for=condition=Ready pod` with a 3 minute timeout, so a Pod stuck in `ErrImageNeverPull`, `ImagePullBackOff` or `Pending` failed after 3 minutes. Now `helm test` is backgrounded and the log loop gives up after 3 minutes. `kubectl logs -f` then prints one error, and `wait $helm_pid` blocks until `--timeout 15m` or the Job's `activeDeadlineSeconds` (900). Nothing else is printed in that time. The 30-minute CI job limit is not reached, but the failure comes about five times later and says less. The two limits are also equal, so `helm test` can time out first with a generic message.
- Proposed solution: If the Pod never has a readable log after the 3 minute poll, kill the `helm test` process and exit non-zero with the Pod status (`kubectl describe pod -l job-name=…`). Alternatively, state in writing that the slower failure is accepted.

### [non-blocking] No render assertions for the new chart's security contract

Confidence: medium

`.github/workflows/integration-tests.yaml:83-84`

- Problem: The PR's main claim is that every Pod meets the `restricted` Pod Security Standard (non-root, seccomp, all capabilities dropped, no privilege escalation). CI only runs `helm lint` on the new chart. `test/scripts/test-chart-render.sh` has no reference to `test-stand`, so a regression in `_helpers.tpl` would pass.
- Proposed solution: Add render assertions for the Pod and container security contexts. They should also cover the Keycloak exception, where `readOnlyRootFilesystem` is false.
