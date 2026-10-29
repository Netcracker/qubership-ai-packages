# Final review: `bd5bf865..HEAD` (Termination Grace Period Helm value)

Two commits, four files: `Chart.yaml`, `deployment.yaml`, `restic-daemonset.yaml`, `values.yaml`. I loaded `english-developer-style` and `test-authoring` from the skills directory. No Helm-chart authoring skill was provided, so the `docs-page-authoring` and `apm-authoring` analogues don't apply. I ran `comment-drift.py bd5bf865 HEAD`, which printed nothing, because the change has no code members to parse. I rendered the chart with `helm template` and `helm lint` (configuration.provider=aws, deployRestic=true). The field renders as `3600` by default and `120` when overridden, in both the Deployment and the DaemonSet. An empty or null value renders an empty field.

## Item 1: comments consistent with the code and with each other

Finding 2 applies. The comment at `values.yaml:89` says "the pod", and the value also governs the restic DaemonSet. The sibling comment at line 86 names "the Velero deployment". Nothing else in the change narrates history. The `Chart.yaml` bump from 2.31.8 to 2.31.9 matches the previous chart commits.

## Item 2: claimed cases covered

The claimed cases are that the value can be set by the user, that it reaches the Velero Deployment (task statement), and that it reaches the restic DaemonSet (commit 98041d0). The change adds no test for any of them. The repository has no chart unit tests. CI runs `ct lint` and `ct install` in kind with `ci/test-values.yaml`, which doesn't set the value, and neither step asserts the field. See finding 3.

## Item 3: boundaries, partitions, and the negative control

- Partitions: the default, a non-default value, and empty/null. Empty/null renders `terminationGracePeriodSeconds: ` (null), so the pod silently gets Kubernetes' 30-second default. The change doesn't claim that case, so I record it without a finding.
- Pre-existing state: an install created by 2.31.8 has no such field. The upgrade changes the pod template of both workloads, so it restarts them. `ct.yaml` sets `upgrade: true`, but nothing asserts the rollout. See finding 1.
- Limits on the same work, each with the place that sets it:
  - `resticTimeout`: `values.yaml:289-290`, Velero default 1h, passed by `deployment.yaml:83-84`. The restic clock starts when a backup starts, before any SIGTERM, so at the defaults it fires first. Raising it above 3600 makes the grace period fire first. See finding 4.
  - The kubelet's graceful node shutdown and the node service manager's stop timeout: outside this repository. They are not verified.
  - Velero's own SIGTERM handling: outside this repository. See finding 5.

## Item 3a: level, placement, and environment

The smallest level that can observe the change is a render with the value set, asserting the field in both pod templates, with no cluster needed. No such check exists. See finding 3. No new tests were added, so there is nothing to place.

## Item 4: names by content

None. The change adds no test names, case ids, or messages.

## Item 5: the failure report

None. The change adds no assertions.

## Item 6: what the writer says it verified

Not stated. Neither commit message nor the PR description carries render output or any other evidence. My own render, described above, covers the default and the override.

## Item 7: siblings of the change

No helper was touched. The other pod templates are `cleanup-crds.yaml` and `upgrade-crds.yaml`, which the test values describe as kubectl upgrade and cleanup jobs. The grace period doesn't apply to them, since the claim is about the Velero server. The restic-specific keys follow the `restic.` prefix, which is taste (finding 7).

## Findings

| # | Label | File and line | Change requested |
|---|---|---|---|
| 1 | Substantive | `values.yaml:89-90`, `deployment.yaml:61`, `restic-daemonset.yaml:56` | The default of 3600 changes the pod template of every existing install from Kubernetes' 30 seconds to 3600, for both workloads. Each upgrade therefore restarts the Velero Deployment and every restic pod. The Deployment sets no `strategy:`, so the old pod may keep running while the new one starts. The PR description should say so and say why 3600. |
| 2 | Substantive | `values.yaml:89` | "the pod" could be read as the Velero pod only, but restic pods get the value too. Name both workloads, and say that the default differs from Kubernetes' 30 seconds. |
| 3 | Substantive | `ci/test-values.yaml`, `ct.yaml` | Both claimed cases (reaches the Deployment, reaches the DaemonSet) have no test. Add a render check that sets the value and asserts the field in both pod templates, or name the CI step that does. |
| 4 | Substantive | `values.yaml:289-290`, `deployment.yaml:83-84` | Raising `resticTimeout` above the grace value makes SIGKILL fire first, so the raised timeout has no effect. Nothing states the relation. Add it to the comment, or derive the default from `resticTimeout`. |
| 5 | Substantive | `values.yaml:89`, PR description | The stated use case (Velero finishes a backup on SIGTERM) depends on Velero's SIGTERM handling, which is outside this repository and unverified here. Cite the Velero line that makes the server wait, or show a run: start a backup, send SIGTERM, and see it complete within the grace period. |
| 6 | Taste | commit `e5632c1` subject | "adding ..." is a gerund label, and `english-developer-style` §Commit messages asks for an imperative. History mixes styles, so amend only if the commits are squashed. |
| 7 | Taste | `restic-daemonset.yaml:56` | Restic-specific settings use `restic.` keys (`restic.priorityClassName`). A `restic.terminationGracePeriodSeconds` key would follow that pattern. I prefer that shape. |

## Not checked

I did not run `ct lint` or `ct install`, since there is no cluster. I ran `helm lint` and `helm template` only. I did not verify Velero's shutdown behavior or the node-level limits, because they are outside this repository. I briefly created and then removed a temporary git worktree for a base render. The repository is back to its original state with no uncommitted changes.
