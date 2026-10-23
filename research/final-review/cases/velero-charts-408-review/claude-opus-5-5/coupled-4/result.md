# Final review: `bd5bf86..HEAD` ([velero] termination grace period value)

The search for a local Velero source checkout has finished and found nothing. Velero's SIGTERM handling is still unverified, so the report is unchanged.

This change has no code and no tests. It edits a Helm chart: `values.yaml`, two templates, and `Chart.yaml`. So I filled the form with the §2a analogues for a configuration, and each item says which one it used. I didn't run the drift script on a members list. I did run it, and it printed nothing because it doesn't parse YAML or Go templates, so I found the members by hand. I loaded `english-developer-style` and `test-authoring`. No authoring skill exists for a Helm chart.

Evidence I ran: `helm template` with `ci/test-values.yaml` at the default and at `0`, `null`, an empty string, `999999`, `1000000` and `10000000`; `helm template --set deployRestic=false`; `helm lint`, which passed.

## Item 1: comments consistent with the code and with each other
*Analogue: every statement the changed files make about the chart.*

- `charts/velero/values.yaml:89` says "The number of seconds to allow for graceful termination of the pod. Optional." This is wrong in two ways.
  - **It names one pod, but the value drives two workloads.** `templates/deployment.yaml:61` and `templates/restic-daemonset.yaml:56` both read it. The comment sits among values whose comments say "for the Velero deployment" (lines 83, 86, 93). A reader will assume it doesn't touch the restic DaemonSet.
  - **"Optional" hides a default change.** The default is `3600`. Before this change the field wasn't rendered, so the Kubernetes default of 30 applied. Every upgrade now gets 3600 on both workloads without setting anything.
- The neighboring values split per workload: `priorityClassName` and `restic.priorityClassName`, `lifecycle` and `restic.lifecycle`. The new value doesn't follow that pattern.
- No comment narrates the change. `README.md` has no values table that would owe an entry.

## Item 2: claimed cases covered
*Analogue: the claimed cases come from the PR description and the two commit subjects.*

| Claimed case | What covers it |
| --- | --- |
| "Adds the ability to specify the termination grace period" | Covered. `--set terminationGracePeriodSeconds=0` and `=10000000` render in both workloads. |
| "previously immutable, 30 seconds" | Not stated as kept. The chart now changes it to 3600 by default; the description says nothing about a new default. |
| "allow Velero to finish a backup before terminating" | **Not covered.** A longer grace period helps only if the Velero server keeps running an in-progress backup after SIGTERM, instead of cancelling its context and exiting. Nothing in the change or the description shows this. Velero marks `InProgress` backups as `Failed` on restart, so if the process exits right away the new value changes nothing. |
| Commit 2: "specification of termination grace period to restic daemonset" | Covered by rendering. `deployRestic=false` leaves only the Deployment's field. The PR gives no reason why the DaemonSet needs it. |

## Item 3: boundaries, partitions, and the negative control
*Analogue: the partitions are the values a user can set, plus the state an earlier chart version left behind.*

- **Boundaries:**
  - `0` renders `0` (immediate kill).
  - `null` and an empty string render `terminationGracePeriodSeconds: ` with no value. That's null, so the API server's default of 30 applies. Acceptable, but the values comment doesn't say so.
  - **An integer of 1000000 or more in a values file renders in scientific notation.** `999999` renders as is, while `1000000` renders `1e+06` and `10000000` renders `1e+07`. `--set` doesn't have this problem. The API server probably rejects that as an int64 field, but I had no cluster to confirm it. Real grace periods won't reach 11.5 days, so this is minor.
- **Earlier state:** `ct.yaml` sets `upgrade: true`, so CI's `ct install` upgrades from the previous chart version. That covers the inherited Deployment and DaemonSet. The upgrade changes the pod template and rolls both workloads; the old pods still terminate under their old 30 s.
- **Other limits on the same work:**
  - **The Velero process's own shutdown behavior.** Whether it waits for the running backup on SIGTERM is set in the Velero binary, not in this chart. It is the limit that decides whether this setting has any effect. Nobody has stated it (see Item 2).
  - **`lifecycle` (`values.yaml:84`).** A `preStop` hook spends time from the same grace period. That pair isn't documented.
  - **`configuration.resticTimeout` (`values.yaml:290`).** It's empty in the chart, so Velero's default applies, which I believe is 4 h; I didn't verify that. It bounds one pod-volume backup inside a backup, so it is not strictly the same stretch of work. Still, at the defaults a restic backup that is within its timeout can be killed at 3600 s.
- **The DaemonSet partition:** a 3600 s grace on restic pods on every node can stretch node drains and rollouts by up to an hour, if restic doesn't exit promptly. No run checks this either way.

## Item 3a: level, placement, and the environment
*Analogue: where the setting lives, whether it matches the chart's layout, and the repository's gate.*

- `helm lint` passes. CI runs `ct lint` and `ct install` (`.github/workflows/lint-test.yaml`, Kubernetes 1.16–1.25).
- `ci/test-values.yaml` doesn't set the value, so CI exercises only the default of 3600.
- Placement: a top-level value read by the restic template breaks the `restic.*` layout. That's the substance of finding 2.

## Item 4: names by content, not by position
*Analogue: unchanged.* None. The value name matches the Kubernetes field name, and nothing refers to anything by position.

## Item 5: the failure report
*Analogue: what a user sees when the value is wrong.* A value of 1000000 or more from a values file renders `1e+06` with no error at render time. Any rejection would appear only at apply time, and I couldn't confirm that the API server rejects it. Nothing else to report.

## Item 6: what the writer says it verified
Nothing is stated. There is no rendered output in the description, and no run showing that a backup survives SIGTERM past 30 s.

## Item 7: siblings of the change
*Analogue: other places that read or route the same values.*

- `git grep -n 'Values.lifecycle'` finds a related bug that predates this change. `templates/restic-daemonset.yaml:165` gates `restic.lifecycle` on the top-level `.Values.lifecycle`, so the restic hook renders only when the deployment's hook is also set. It's the same pattern of a top-level value leaking into the restic template, and I'd name it as follow-up rather than fix it here.
- No other workload template (jobs, hooks) needed the field. Upgrade and cleanup jobs are short-lived.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The default moves from the Kubernetes 30 s to 3600 s for every install, while the PR says "adds the ability to specify" and the comment says "Optional". | Substantive | `charts/velero/values.yaml:90` | Default to 30, or leave it unset and render the field only when set (`{{- with }}`). Otherwise state the new default and its effect on both workloads in the description and the comment. |
| 2 | One top-level value drives both the Deployment and the restic DaemonSet, but the comment says "the pod" and sits among the deployment's values. | Substantive | `charts/velero/values.yaml:89`, `charts/velero/templates/restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds` to match `restic.priorityClassName` and `restic.lifecycle`. Otherwise name both workloads in the comment and say why restic needs it. |
| 3 | The stated purpose depends on the Velero server not exiting on SIGTERM while a backup runs, and there's no evidence of that. | Substantive | PR description | State the Velero version's SIGTERM behavior with a source reference, or a run where a backup finished after SIGTERM. Note that a `lifecycle` `preStop` hook uses the same budget. |
| 4 | A values-file integer of 1000000 or more renders as `1e+06`. | Taste | `charts/velero/templates/deployment.yaml:61`, `charts/velero/templates/restic-daemonset.yaml:56` | Render with `int64` inside a `with` or `if`. A bare `int` would turn `null` into `0`. |
| 5 | The restic `lifecycle` is gated on the top-level `.Values.lifecycle` (predates this change). | Taste (follow-up) | `charts/velero/templates/restic-daemonset.yaml:165` | Name it as follow-up in the description. |

I did not run `ct install` or touch any cluster, and I found no Velero source, so the API server's handling of `1e+06` and the effect of the grace period on running backups are unverified. I did not do a style-only pass over the prose.
