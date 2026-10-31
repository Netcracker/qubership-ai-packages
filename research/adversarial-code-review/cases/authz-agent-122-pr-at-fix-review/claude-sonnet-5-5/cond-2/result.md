Result: REQUEST_CHANGES (1 blocking, 2 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

The PR text came from the four commit messages. I read the chart, Makefile, Dockerfile, pip-stub, values and docs diffs in full. `helm lint` and `helm template` pass on the chart with the parity values, using a copy of the chart with stand-in files in the session scratchpad. There is no cluster, so the Makefile suite flow and the pods were not run.

## Findings

### [blocking] Unclaimed Keycloak bump in the SVT Compose stack

Confidence: high

`test/svt/common/compose/docker-compose.yml:3`

- Problem: `quay.io/keycloak/keycloak:26.0` changes to `26.3.5@sha256:…`. No commit message or description sentence claims it, and no run on the SVT stack checks it. The commit messages claim only the Kubernetes test stand. Elsewhere this PR notes that Keycloak 26.x versions differ in what they require at password grants, for example the "Account is not fully set up" check handled in `build/authz-agent-transfer/Dockerfile`. This is a runtime dependency version change in a stack the change otherwise leaves alone.
- Proposed solution: Revert the hunk, or move it to its own change with a stated reason and a run of the SVT stack on 26.3.5.

### [non-blocking] Suite wait now fails after 15 minutes with no output when the Job's Pod never starts

Confidence: medium

`Makefile:104-112` (the `run-suite` define)

- Problem: The old flow waited for the Pod to be Ready for up to 3 minutes and then failed. Inside `run-suite`, if the Pod never starts (for example `ErrImagePull`, or a missing local image), the log loop gives up after 3 minutes. `kubectl logs -f` then fails silently, and `wait $$helm_pid` blocks until `helm test --timeout` fires. A Job with `backoffLimit: 0` and a stuck Pod ends only at `activeDeadlineSeconds` (900 s). So the fault now takes about 15 minutes and prints nothing after the polling stops. In the `e2e` and `parity` CI jobs (`timeout-minutes: 30`), that 15 minutes comes on top of the earlier steps, which have their own limits of 10, 5 and 5 minutes.
- Proposed solution: Bound the whole suite run, or fail fast when the Pod is not Ready within a few minutes. Print `kubectl describe job` and `kubectl get pod` when the log never becomes readable.

### [non-blocking] pip-stub rule files are not rolled when they change on `helm upgrade`

Confidence: medium

`helm-templates/authz-test-stand/templates/pip-stub.yaml:27-38`

- Problem: The idp Deployment carries `checksum/realms` so that a changed realm restarts the Pod. The pip-stub Deployment has no checksum annotation for its `<name>-config` ConfigMap, although the stub reads `PIP_STUB_CONFIG` only at start. After `make parity-harness` regenerates the rule files and `helm upgrade` updates the ConfigMap, the running stub keeps its old rules. `make parity-restart` does restart `pip-mock`, which only partly mitigates this.
- Proposed solution: Add a `checksum/config` annotation to the pod template, derived from `$config`, as the idp part does.

## Needed to complete the review

None. The gaps are the Makefile flow and the pods, which need a cluster.
