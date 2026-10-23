# Final review: `bd5bf86..HEAD` (velero chart: `terminationGracePeriodSeconds`)

The two commits add one top-level value, `terminationGracePeriodSeconds`, with a default of `3600`. Both the Velero Deployment and the restic DaemonSet now always render it, and the chart version goes from 2.31.8 to 2.31.9. The change has no code, only YAML and Go templates, so the review used the §2a analogues. The drift script ran and returned nothing (exit 0) because it doesn't parse YAML or Helm templates, so I compared the comments against the templates by hand. I loaded `test-authoring` and `english-developer-style` from the given skills directory.

## Item 1: comments consistent with the code and with each other

**Analogue used:** the `values.yaml` comment against the templates that read the value, and against the comments next to it.

- **`charts/velero/values.yaml:89`, "the pod".** The comment says "The number of seconds to allow for graceful termination of the pod." It sits in the block of top-level keys whose comments all say "for the Velero deployment" (lines 83, 86, 92, 95, 98). The restic settings live under `restic.*` with their own comments, such as `restic.priorityClassName` and `restic.lifecycle`. A reader will take this key as server-only. In fact `restic-daemonset.yaml:56` reads it too, so changing it also changes every restic pod. The comment should name both workloads.
- **The same line, "Optional."** In this file, "Optional" goes with keys whose empty default emits nothing (`priorityClassName: ""` behind an `if`). This key has a non-empty default, and both templates emit it unconditionally. I rendered it: `--set terminationGracePeriodSeconds=null` and `--set-string ...=` both produce `terminationGracePeriodSeconds:` with no value, which Kubernetes treats as unset (30 s). So "Optional" holds only by accident. The comment also doesn't give the Kubernetes default (30), which is the fact that explains why `3600` was chosen.
- No comment narrates the change.

## Item 2: claimed cases covered

**Analogue used:** each claim against the section of the change that handles it, and the evidence that it works.

| Claimed case | Source | Covered by |
|---|---|---|
| The value can be set | PR description, commit 1 | Templates render it. I checked `helm template` with 3600 (default), 86400, `null` and `""`. **No CI values file sets a non-default value**, so `ct lint` and `ct install` only render the default. |
| Velero gets to finish a backup that runs longer than 30 s before it terminates | PR description (the stated reason for the change) | **Nothing.** A longer grace period only helps if the `velero server` process keeps running after SIGTERM until its backup completes. The repository doesn't contain that program. The change neither cites where Velero handles SIGTERM nor shows a run where a pod outlived 30 s mid-backup. If Velero cancels its context and exits right away on SIGTERM, which is what I remember of v1.9 but did not verify, the setting has no effect on the stated use case. |
| The restic DaemonSet honors the value | Commit 2 | Rendered (line 247 of the CI render). It is not mentioned in the PR description or in `values.yaml`. |
| Unclaimed: **the default moves from 30 s to 3600 s** for every install and upgrade, on both workloads | Not claimed anywhere | The PR describes the change as "the ability to specify". The diff also changes the behavior of anyone who doesn't specify. Neither the commit messages nor the README say so. |

## Item 3: boundaries, partitions, and the negative control

- **Value partitions.** Default, large (86400), `null` and empty all render; `null` and empty fall back to the Kubernetes default. `0` is valid Kubernetes (immediate kill) and renders as `0`. Negative or non-integer values would fail at the API server, not at lint. That is acceptable for this chart's style. **None** requested here.
- **Inherited state.** `helm upgrade` from 2.31.8 silently changes running pods from 30 s to 3600 s and rolls both workloads. The README's "Upgrading" section (`README.md:90+`) says nothing about it. This is a finding: either keep the old default or document the change.
- **Other limits on the same work** (the time from SIGTERM until the backup or pod is gone):
  1. **Velero's own SIGTERM handling** (in the `velero` binary, outside this repo). This is the inner limit that decides whether 3600 has any effect. The request is the evidence: the line in `pkg/cmd/server` that waits for in-flight backups, or a run that shows it.
  2. **Deployment rollout.** No `strategy` is set, so the Kubernetes default RollingUpdate (maxSurge 1, maxUnavailable 0, one replica) applies. If the old pod does linger, the old and new Velero servers run side by side for up to an hour, and v1.9 has no leader election. Worth stating if (1) shows the process lingers.
  3. **DaemonSet rollout combined with `helm upgrade --wait`** (default `--timeout 5m`). On each node the new restic pod starts only after the old one is gone. If a restic pod lingers, `--wait` fails at 5 min, long before 3600 s.
  4. **Environment:** kubelet `shutdownGracePeriod` on node shutdown, and the `kubectl drain --timeout` an operator passes. Both can end the pod before the setting does, with no error from the chart.

  The request is to document this set of limits next to the value, or at least the dependency on (1).

## Item 3a: level, placement, and the environment

**Analogue used:** where the setting lives, and what the repository's gate runs.

- The repository has no template-unit-test harness (no helm-unittest). The gate is `ct lint` plus `ct install` on kind across k8s 1.16–1.25 using `ci/test-values.yaml`. I ran `helm lint . -f ci/test-values.yaml` offline: 1 chart linted, 0 failed.
- `ci/test-values.yaml` sets annotations, labels and resources for both workloads to exercise non-default render paths. Following that pattern, a non-default `terminationGracePeriodSeconds` there would have the CI install exercise the configured path. This is a finding of the same substance as item 2's first row.
- Placement matches the neighbors in both templates, directly after `priorityClassName`.

## Item 4: names by content, not by position

None. I checked the key name, the comment and both commit subjects; nothing refers to anything by position.

## Item 5: the failure report

**Analogue used:** what CI would print if this broke. With no assertions and no explicit `ci` value, the only failure is a schema rejection from `ct install`, for example a non-integer value. That message names the field, which is adequate. No separate finding beyond item 3a.

## Item 6: what the writer says it verified

Neither the commits nor the PR description state any evidence: no rendered output, no run where a pod outlived 30 s during a backup, and no citation of Velero's shutdown path. I didn't run the CI suite to supply it.

## Item 7: siblings of the change

- **Pod-producing templates:** `deployment.yaml`, `restic-daemonset.yaml`, `upgrade-crds.yaml` and `cleanup-crds.yaml`. The two Jobs are short-lived Helm hooks with no backup work, so the defect doesn't apply to them.
- **Per-component keys.** `restic.*` already carries its own `priorityClassName`, `lifecycle`, `tolerations` and so on, but the restic DaemonSet now reads the server's top-level key. There is precedent for sharing top-level keys: `restic-daemonset.yaml:34-37` reads top-level `podLabels` and `podAnnotations`. Either form is defensible (taste).
- **A pre-existing defect of the same class, not introduced by this change:** `restic-daemonset.yaml:165` tests `.Values.lifecycle` but renders `.Values.restic.lifecycle`. Worth naming as a follow-up because it is another place where the top-level and restic values are mixed up.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The default changes from 30 s to 3600 s for every install and upgrade, on both workloads; the PR, commits and README don't say so | Substantive | `charts/velero/values.yaml:90` | Keep the previous behavior by default (emit nothing unless set), or state the new default in the PR description and in the README "Upgrading" section |
| The stated purpose (letting a backup finish) depends on Velero waiting on SIGTERM, which nothing shows | Substantive | `charts/velero/values.yaml:89` | Cite the line in the Velero server that drains in-flight backups on SIGTERM, or show a run where it does. Otherwise drop the purpose from the description, or pair the value with a `lifecycle.preStop` example |
| The comment says "the pod", but the value also governs the restic DaemonSet | Substantive | `charts/velero/values.yaml:89` | Name both: "…for the Velero deployment and the restic daemonset" |
| Other limits that end the same work are not documented: `helm --wait` (5 m) on the DaemonSet rollout, kubelet `shutdownGracePeriod`, `kubectl drain --timeout`, and an hour of two concurrent Velero servers during a rolling update | Substantive | `charts/velero/values.yaml:89` | Document these limits next to the value, or derive a smaller default |
| CI never renders a non-default value | Substantive | `charts/velero/ci/test-values.yaml` | Set a non-default value (e.g. `120`) there, as is already done for labels and resources |
| "Optional" for a key whose non-empty default is always emitted | Taste | `charts/velero/values.yaml:89` | Guard it with `{{- with }}`/`if` and default to unset, or drop "Optional" and state the Kubernetes default (30) |
| One shared key versus `restic.terminationGracePeriodSeconds` | Taste | `charts/velero/templates/restic-daemonset.yaml:56` | Prefer a `restic.*` key to match the restic block's other pod-level keys |
| Patch bump (2.31.9) for a change of default behavior | Taste | `charts/velero/Chart.yaml:6` | Prefer a minor bump |
| Pre-existing: `restic-daemonset.yaml:165` checks `.Values.lifecycle` but renders `.Values.restic.lifecycle` | Taste (follow-up, out of scope) | `charts/velero/templates/restic-daemonset.yaml:165` | Name it as a follow-up |

Not checked: the `ct install` suite on kind was not run (there is no cluster), Velero's SIGTERM behavior was not read from source (it is outside the repository and I had no network access), and the prose was not reviewed for style.
