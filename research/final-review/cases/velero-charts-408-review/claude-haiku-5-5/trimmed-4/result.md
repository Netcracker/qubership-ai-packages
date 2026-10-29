## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

Scope: two commits, four files. Chart version 2.31.8 to 2.31.9, a new `terminationGracePeriodSeconds: 3600` in `values.yaml`, and the field added to the Velero Deployment and the restic DaemonSet. The task statement is the PR text quoted in the brief. No prior report exists, so the table of earlier findings is omitted.

Checks run: `helm lint` passes. `helm template` with `configuration.provider` set (the Deployment is gated on it, so the default render shows no Deployment) and `ci/test-values.yaml` gives `3600` in both pods, and overrides of `120` and `0` render as written. `null` and `""` render an empty value. `comment-drift.py` exits 0 with no output. It parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, so it had nothing to read in this YAML-only change, and I read the YAML comments by hand.

### Item 1: comments consistent with the code and with each other
Finding below (`values.yaml:89`). The only comment in the diff is the new values comment. The drift list is empty, so no code member changed under an unchanged comment. Nothing narrates the change.

### Item 2: claimed cases covered
- Claim: the value reaches the Velero Deployment. No test. The only exercise is `ct install` in `.github/workflows/lint-test.yaml`, and `ci/test-values.yaml` does not set the value, so CI only ever sees the default. See finding 4.
- Claim (commit message): the restic DaemonSet gets the value. No test. See finding 4.
- Claim (PR text): Velero can finish a backup before termination. No test or run in the change. See finding 5.
- Not claimed, but the diff changes it: the default moves from the Kubernetes 30 seconds to 3600 for both pods on upgrade. The PR text does not say so. See finding 3.

### Item 3: boundaries, partitions, and the negative control
- Boundaries: `0` renders `0`. Null or empty renders `terminationGracePeriodSeconds: ` with no value, which the API server reads as unset, so the pod falls back to the 30-second default. See finding 2.
- Negative control: none. The change has no test at all.
- Limits on the same work: the restic timeout (`values.yaml:290`, `deployment.yaml:83-84`) ends one restic operation, not the server's work, so it does not count under this form. The `lifecycle` preStop hook (`values.yaml:84`) runs inside the grace period, so a long hook shortens the time left for the server. That is a fact for the description, not a defect. Velero's own handling of SIGTERM sits in the 1.9.2 binary, outside this repository. See finding 5.
- Pre-existing state: an install made by 2.31.8 is upgraded in place, and no run starts from that state. See finding 3.

#### Item 3a: level, placement, and environment
The smallest level that observes the change is a render through `helm template`, which needs no server. Nothing runs at that level. The only server-level check does not set the value. See finding 4.

### Item 4: names by content, not by position
none. The new text names nothing by position.

### Item 5: the failure report
none. The change has no assertions.

### Item 6: what the writer says it verified
Neither a red run nor a mutation verdict is stated, and the change carries no test that could fail. The `ct install` in CI is a consistency check, not that evidence.

### Item 7: siblings of the change
none. The Jobs in `upgrade-crds.yaml` and `cleanup-crds.yaml` do not carry `priorityClassName` either, and the PR does not claim them. The only pod templates that take the value are the two the PR names.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| 1. The comment says "the pod", but the value also sets the restic DaemonSet pods, so a reader setting it for Velero would not know restic is affected. | substantive | `charts/velero/values.yaml:89` | Name both: "the Velero and restic pods." |
| 2. The template has no guard. An empty or null value renders an empty `terminationGracePeriodSeconds:`, which the API server reads as unset, so the pod gets the 30-second default the PR is meant to replace. A plain `{{- if }}` would also drop `0`. | substantive | `charts/velero/templates/deployment.yaml:61`, `charts/velero/templates/restic-daemonset.yaml:56` | Fail the render on an empty value with `required`, so the error shows instead of silent 30 seconds. Keep `0` rendering. |
| 3. The default changes from 30 seconds to 3600 for every install on upgrade, for both the Velero and restic pods. Nothing in the PR text or the commit messages says so, and no run starts from a 2.31.8 install. | substantive | `charts/velero/values.yaml:90` | State the default change in the PR description, with the reason for 3600. Add an upgrade run from 2.31.8 on kind, or name the remedy. |
| 4. No test or CI case sets the value. `ci/test-values.yaml` leaves the default, so `ct install` never applies an override. The override path and the restic path are unexercised. | substantive | `charts/velero/ci/test-values.yaml` (no entry); `.github/workflows/lint-test.yaml` | Set `terminationGracePeriodSeconds` in `ci/test-values.yaml` so `ct install` applies a non-default value on each kind version. |
| 5. The PR's stated use case, finishing a backup before termination, has no evidence in the change. Whether the server waits for in-flight work on SIGTERM is in the Velero binary. I did not verify it. | substantive | PR description; `charts/velero/templates/deployment.yaml` | Either state in the PR that this is unverified, or cite a run where a backup in progress survives the pod deletion with the value set. |

### What the review did not check
I did not run `ct lint` or `ct install`, since there is no kind cluster. I did not confirm on a cluster that a null `terminationGracePeriodSeconds` falls back to 30 seconds. I did not check Velero's SIGTERM behavior in the 1.9.2 binary. I did not run an upgrade from 2.31.8. Nothing was changed or committed.
