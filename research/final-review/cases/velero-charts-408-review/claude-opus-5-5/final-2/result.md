# Final review: `bd5bf86..HEAD` ([velero] Add Termination Grace Period Helm Value)

This change has no code in the drift script's sense. It touches YAML and Go templates in `charts/velero` across 2 commits. I ran `comment-drift.py bd5bf86 HEAD` and it printed nothing (exit 0), so for each item I used the analogue from §2a ("a configuration, a deployment definition") wherever the literal wording didn't fit. I loaded `test-authoring` and `english-developer-style`. There is no doc-comment skill for Helm templates, so none was loaded.

What I ran: `helm lint` and `helm template` with `ci/test-values.yaml --set deployRestic=true`. The default and boundary values I rendered are listed under item 3.

## Item 1: comments consistent with the code and with each other
Analogue used: the statements `values.yaml` makes about the templates.

- **`values.yaml:89`** says: "The number of seconds to allow for graceful termination of the pod. Optional."
  - **"the pod" is wrong.** The value is used for two different pods: the Velero Deployment (`deployment.yaml:61`) and the restic DaemonSet (`restic-daemonset.yaml:56`). The comment sits among top-level keys whose comments all say "for the Velero deployment". The restic block (`values.yaml:392–452`) has its own `priorityClassName`, `lifecycle` and so on, and its own comments. A reader would conclude this key affects only the Velero pod. Rendering with `--set restic.terminationGracePeriodSeconds=60` confirms there is no restic-specific key: both pods still render `3600`.
  - **"Optional." misleads.** The field is always rendered, with no `if` guard, and the shipped default is 3600, not unset. Setting it to `null` renders `terminationGracePeriodSeconds:` with an empty value, which Kubernetes treats as its default of 30. That works, but nothing tells the reader that `null` is how to get the old behavior back.
- No comment describes the change itself ("now", "no longer").

## Item 2: claimed cases covered
The cases come from the PR description and the two commit subjects:

| Claimed case | Covered by |
|---|---|
| A user can set the grace period through a Helm value | Rendered correctly (`helm template`). No test sets a non-default value: `ci/test-values.yaml` doesn't set the key. |
| The grace period applies to the restic DaemonSet (commit 98041d0) | Rendered correctly. It reuses the Velero value (item 1). |
| The stated reason: "allow Velero to finish a backup before terminating" | **No test and no evidence.** This only works if the Velero v1.9.2 server, on SIGTERM, keeps a running backup going until it finishes and only then exits. If the server cancels its context and exits right away, any grace period has no effect, and the old default of 30 s would have been enough too. That behavior is in Velero itself, outside this repository. See item 3. |
| "previously immutable, 30 seconds" | The previous behavior was the Kubernetes default of 30 s. The change does more than make it settable: it **changes the default to 3600 for every install**, and the description doesn't say so. |

## Item 3: boundaries, partitions, and the negative control
Rendered values (both pods give the same output):

| Value | Rendered as | Effect |
|---|---|---|
| Default | `3600` | |
| `0` | `0` | Valid: immediate kill |
| `null` or `""` | Empty field | Kubernetes falls back to 30 |
| `abc` | `abc` | Lint passes; the API server would reject it |
| `10000000` (from a values file) | `1e+07` | **Not a valid integer for the API server.** Helm turns large numbers into floats. Only values of about 1,000,000 s (≈11.5 days) and above are affected, which is unlikely in practice. A fix such as `int64` would also turn `null` into `0`, so the guard has to come first. |

- **Negative control / default.** Before this change, every install got 30 s. After it, every install gets 3600 s, and upgrading re-rolls both workloads. A default that keeps 30, or leaving the field out unless the value is set, would keep existing installs unchanged.
- **Pre-existing state.** `ct.yaml` has `upgrade: true`, so `ct install` in CI upgrades from the previous chart version on kind. That covers "upgrade still installs". It doesn't cover any behavior that depends on the grace period.
- **Other limits on the same work** (the life of a pod after SIGTERM, counted from the delete):
  - **Velero server shutdown on SIGTERM.** Set in the Velero program, outside this repo. This decides whether the setting has any effect at all. The request is evidence: the lines in Velero v1.9.2 (`pkg/cmd/server/server.go`, the signal handling and how the backup controller stops) showing that an in-flight backup is waited for, or a run where a backup survives a pod delete.
  - **Restic server shutdown on SIGTERM.** Same question for `velero restic server`, also outside this repo. Same request for evidence.
  - **Limits set by the environment.**
    - The Cluster Autoscaler's `--max-graceful-termination-sec` defaults to 600 s, so a scale-down caps the grace period at 10 minutes and the 3600 default has no effect there.
    - The kubelet's `shutdownGracePeriod` caps it when a node shuts down.
    - `kubectl drain --timeout` can cap it if the operator sets one.

    None of these is documented next to the value.
  - **`configuration.resticTimeout`** (`deployment.yaml:83`) limits a single pod-volume backup inside a backup. By §4 of `test-authoring` that is not one of the limits in question.
- **Overlap during a rollout.** The Deployment uses the default RollingUpdate strategy, and Velero v1.9 has no leader election. If the old pod does keep working during its grace period, it runs next to the new pod for up to an hour, and both controllers act on the same Backup objects. The new default makes this more likely if the Velero premise holds. Either document this or consider `strategy: Recreate`.

## Item 3a: level, placement, and the environment
Analogue used: where the rule lives and the repository's own gate.

- The smallest level that can observe this is `helm template`. The repo has no helm-unittest suite, so the gate is `ct lint` and `ct install` (`.github/workflows/lint-test.yaml`). `helm lint` passes locally. I didn't run `ct`.
- The value is placed in the pod spec next to `priorityClassName` in both templates, which matches the siblings.
- The value's placement in `values.yaml` doesn't match the siblings: restic settings live under `restic.*` (item 1).

## Item 4: names by content, not by position
None. I checked the key name, the comment and both commit subjects. None of them refers to anything by position.

## Item 5: the failure report
Analogue used: what a bad value tells the user. A non-numeric or huge value passes `helm lint` and fails only at apply time, with an API-server error. There is no `values.schema.json` that would catch it. Anything beyond that is taste.

## Item 6: what the writer says it verified
Nothing is stated. Neither the PR nor the commits mention a run showing that a backup survives a pod delete under the new grace period, or any check of Velero's SIGTERM handling.

## Item 7: siblings of the change
- I grepped every pod spec in `templates/`. The two long-running workloads are both changed.
- The CRD upgrade and cleanup Jobs are short-lived hooks and don't need the setting.
- One pre-existing sibling of the "restic reads a top-level value" pattern: `restic-daemonset.yaml:165` guards on `.Values.lifecycle` but renders `.Values.restic.lifecycle`. This change didn't introduce it, but it's the same mix-up. Worth naming as a follow-up.
- `Chart.yaml` was bumped to 2.31.9. The README doesn't list values, so nothing to update there.

## Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| The default changes from Kubernetes' 30 s to 3600 s for every install, and the description doesn't say so | Substantive | `values.yaml:90` | Default to unset or 30 and render the field only when set, or state the new default and why in the PR and the comment |
| No evidence that Velero v1.9.2 (server and restic) waits for an in-flight backup on SIGTERM; without that the setting does nothing | Substantive | `deployment.yaml:61`, `restic-daemonset.yaml:56` | Cite the Velero source lines, or show a run where a backup survives a pod delete |
| The comment says "the pod", but the value also drives the restic DaemonSet; restic has no key of its own | Substantive | `values.yaml:89`, `restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds`, or say in the comment that it applies to both pods |
| "Optional." while the field is always rendered with 3600; `null` restores 30 but isn't documented | Substantive | `values.yaml:89` | Wrap in `{{- with }}`/`if`, or document `null` |
| Environment caps aren't documented: Cluster Autoscaler at 600 s, kubelet `shutdownGracePeriod` | Substantive | `values.yaml:89` | One sentence in the comment |
| Old and new Velero pods can run side by side during a rollout for up to the grace period, with no leader election | Taste | `deployment.yaml` | Document it, or use `strategy: Recreate` |
| Values ≥ 1e6 render as `1e+07` | Taste | `deployment.yaml:61`, `restic-daemonset.yaml:56` | Guard for `nil`, then use `int64` |
| No CI values case sets a non-default grace period | Taste | `ci/test-values.yaml` | Add e.g. `terminationGracePeriodSeconds: 120` |
| `.Values.lifecycle` guard around the restic lifecycle | Follow-up (pre-existing) | `restic-daemonset.yaml:165` | Name it in the description as follow-up |

This review didn't run `ct lint` or `ct install`, didn't install on a cluster, didn't read the Velero source (Velero's SIGTERM behavior is unverified), and didn't do a style-only pass over the prose.
