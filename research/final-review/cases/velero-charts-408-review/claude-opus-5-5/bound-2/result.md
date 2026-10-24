# Final review: `bd5bf86..HEAD`, "[velero] Add Termination Grace Period Helm Value"

**Summary:** the setting is wired up and renders correctly. It needs changes before merge, for three reasons:
- **New default for every install.** The default goes from 30 seconds to 3600, and the description doesn't mention it.
- **One key for two workloads.** The Velero key also controls the restic daemonset, and nothing says so.
- **Unconfirmed use case.** Nothing shows that Velero keeps a backup running after it receives SIGTERM, which is the whole point of the change.

**Inputs:**
- **Diff:** four hunks across `Chart.yaml`, `templates/deployment.yaml`, `templates/restic-daemonset.yaml` and `values.yaml`.
- **Commit messages:** "adding termination grace period seconds Helm value" and "adding specification of termination grace period to restic daemonset".
- **Task statement:** the PR description quoted in the request.
- **No previous report.**
- **Drift script:** run, with empty output. It doesn't parse YAML or Go templates, so I checked comments by hand.
- **Skills loaded:** `test-authoring` and `english-developer-style`. There is no doc-comment skill for Helm or YAML.

## Item 1: comments consistent with the code and with each other
**Analogue used:** the `values.yaml` comments. This is a config change, with no members to compare.
- `charts/velero/values.yaml:89`: "The number of seconds to allow for graceful termination of the pod. Optional." The comment sits among keys documented as "for the Velero deployment" (lines 83 and 86) and doesn't say which pod.
  - The value also sets the restic daemonset's pods (`restic-daemonset.yaml:56`), so a reader would think it only affects the Velero server. **Substantive.**
- "Optional." conflicts with the template, which always writes the field, with 3600 by default. Setting it to `null` or `""` does fall back to the Kubernetes default (checked below), but the comment doesn't give that default or say how to get it.
- Nothing narrates the change.

## Item 2: claimed cases covered
**Claimed cases:**
1. The grace period can be set through a Helm value. Only the default value is ever rendered: `ci/test-values.yaml` doesn't set the key, so `ct install` only deploys 3600. No CI case renders a value the user sets. Manually, `helm template ... --set terminationGracePeriodSeconds=null` renders `terminationGracePeriodSeconds:` (an empty value) on both pods, which Kubernetes treats as unset. **Substantive (weak):** no CI values file sets a non-default value.
2. The motivating case is letting Velero finish a backup that takes longer than 30 seconds. Nothing exercises it, and it depends on how Velero reacts to SIGTERM (see Item 3). No claim is covered by a test or a run that would fail without the change.
3. The second commit claims the restic daemonset uses the value. It does (`restic-daemonset.yaml:56`), and the default render shows it.

**Commands:** none of the changed files tells anyone to run a command.

**Hunks no sentence claims:**
- **Default changed from 30 to 3600** (`values.yaml:90`). The description says "allow… to finish", which reads as opt-in. In fact every existing install gets a one-hour grace period on upgrade, on both the Deployment and every restic pod. **Substantive:** either state it and justify it, or default to 30 (or leave it unset).
- **`Chart.yaml` 2.31.8 → 2.31.9.** No sentence claims it. `ct lint` requires a version bump by default, so it's needed. **Taste:** mention it in one line.

## Item 3: boundaries, partitions, and the negative control
- **Partitions.** I rendered the default (3600), `null` and `""` by hand. The CI values cover none of the non-default cases, and nothing checks that the field is left out when unset. The control here would be rendering 30 or unset to show nothing else changed; nothing provides it.
- **Existing state.** An install made with 2.31.8 has no explicit grace period, so Kubernetes uses 30. Upgrading it moves both workloads to 3600 without a word (see Item 2). `ct.yaml` has `upgrade: true`, so CI runs the upgrade but only checks that it succeeds.
- **A value users already pass now reaches a new consumer.** `terminationGracePeriodSeconds` is a top-level Velero key. The restic daemonset now reads it too. A user who raises it for long Velero backups also raises it for every node's restic pod, and there's no separate setting. Every comparable setting in this chart has its own `restic.*` key: `priorityClassName`, `lifecycle`, `tolerations`, `resources`. **Substantive:** add `restic.terminationGracePeriodSeconds`, or explain why they share one.
- **Other limits on the same work:**
  - **Velero's own handling of SIGTERM.** This is set in the Velero server, which isn't in this repo. A grace period only helps if the process keeps working after SIGTERM. If `velero server` cancels its context and exits on SIGTERM (as I remember 1.9 doing), the pod exits within seconds and 3600 has no effect. This is the stated use case. **Substantive:** cite the line in Velero v1.9.2 that waits for an in-progress backup on shutdown, or show a run where a pod deleted mid-backup finishes the backup. The other option is a `preStop` hook through the existing `lifecycle` value, documented with this key.
  - **Pod-level limits:**
    - Cluster-autoscaler scale-down caps graceful termination at `--max-graceful-termination-sec`, 600 seconds by default. Any value above that has no effect there.
    - The kubelet's `shutdownGracePeriod` caps node shutdown in the same way.
    - `kubectl drain --timeout`, if set, ends the drain earlier.
    - Restic pods are DaemonSet pods, so `drain --ignore-daemonsets` doesn't evict them at all.
    - **Substantive:** document these caps next to the key. The 3600 default is above the autoscaler's default.
  - **The work's own timeout.** `configuration.resticTimeout` defaults to 1h in the server (`values.yaml:290`), and this one-hour grace period starts only at SIGTERM. That's consistent, not a finding.

## Item 3a: level, placement, and the environment
**Analogue used:** placement and repo checks.
- The smallest level is a template render. The repo has no helm-unittest; its tests are `ct lint` and `ct install` with `ci/test-values.yaml`. The right place for a non-default value is that file (or a second `ci/*-values.yaml`). It isn't changed. This is part of the Item 2 finding.
- The new lines sit next to `priorityClassName` in both templates, which matches the chart's layout.
- `helm lint charts/velero -f charts/velero/ci/test-values.yaml` (Helm v4.3.0) passes.

## Item 4: names by content, not by position
None. I checked the key name and the comment; neither refers to anything by position.

## Item 5: the failure report
None applicable. The change has no assertions. CI's only check is whether `ct install` succeeds, which can't tell a dropped or wrong value from a correct one.

## Item 6: what the writer says it verified
The PR and commits state no evidence: no render showing the value, no run where a pod is terminated during a backup.

## Item 7: siblings of the change
- **Other settings that apply to both workloads.** Settings like `priorityClassName`, `lifecycle` and `tolerations` exist twice, once at the top level and once under `restic.`. The new key exists only once, and two templates read it (Item 3).
- **Lists of settings.** I searched for two existing keys (`priorityClassName`, `lifecycle`) in `README.md`, `values.yaml` and the templates. The README has no table of settings, so no list is missing the new key. `values.yaml` lists it among the Velero settings but not among the restic ones; that's the same finding.
- **Other pods.** The `kubectl` upgrade and CRD-cleanup Jobs are short-lived, so a grace period isn't relevant there. Not a finding.
- **Next to the change, not part of it.** `restic-daemonset.yaml:165` checks `.Values.lifecycle` (the top-level key) but renders `.Values.restic.lifecycle`. This bug was already there; I'm noting it, not asking for it in this change.

## Findings
| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Default changes from 30 seconds to 3600 for every install and upgrade; no sentence says so | Substantive | `charts/velero/values.yaml:90` | Default to 30 or leave it unset (the field is then omitted or empty); or state the new default and the reason in the description |
| Restic daemonset reads the Velero key; no `restic.terminationGracePeriodSeconds` | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds`, like the other restic settings |
| Comment says "the pod" among Velero-only settings, but the value also sets restic pods; "Optional" with no fallback given | Substantive | `charts/velero/values.yaml:89` | Name both workloads (or only one, after the fix above) and say what unset means |
| The use case depends on Velero continuing a backup after SIGTERM; nothing shows it does | Substantive | `charts/velero/templates/deployment.yaml:61` | Cite the Velero v1.9.2 shutdown code that waits for a backup, or show a run where a pod deleted mid-backup finishes; otherwise document a `preStop` hook through `lifecycle` |
| Outer limits (autoscaler 600 seconds, kubelet `shutdownGracePeriod`, `drain --timeout`) override larger values | Substantive | `charts/velero/values.yaml:89` | Mention the caps in the comment |
| No CI values file sets a non-default value | Substantive | `charts/velero/ci/test-values.yaml` | Set a non-default value (and one unset case) in a CI values file |
| No evidence of verification stated | Substantive | PR description | Paste the `helm template` output for a set value and for unset |
| Chart version bump not mentioned | Taste | `charts/velero/Chart.yaml:6` | One line in the description ("chart version bump, which `ct lint` requires") |

I ran `helm template` and `helm lint` locally with Helm v4.3.0 rather than CI's v3.8.1. There was no cluster, so `ct install`/`ct upgrade` and real pod termination weren't run. I didn't check Velero's shutdown behavior against its source, which isn't in this repo; that claim comes from memory. I didn't review the prose for style.
