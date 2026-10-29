# Final review: `bd5bf86..HEAD` ([velero] Add Termination Grace Period Helm Value)

**Inputs.** I read the two commits (e5632c1, 98041d0), which have one-line messages and no body. The task statement is the PR description. The drift script ran and printed nothing, because the change is Helm templates and YAML and the script parses neither. That makes this a change with no members, and every item below says which reading of §2a I used. There is no previous report. I loaded `test-authoring` and `english-developer-style`. A chart has no doc-comment skill, so the `values.yaml` comments stand in for the doc comments. I ran `helm template` and `helm lint` locally with helm v4.3.0; CI pins v3.8.1.

What I rendered, using `-f ci/test-values.yaml --set deployRestic=true`:

| Value passed | Deployment and DaemonSet render |
|---|---|
| (default) | `terminationGracePeriodSeconds: 3600` in both |
| `null`, or `--set-string ...=` | `terminationGracePeriodSeconds: ` (YAML null; Kubernetes then uses 30) |
| `0` | `0` |
| `-1` | `-1` |
| `abc` | `abc` |

`helm lint` reported 1 chart linted, 0 failed.

## Item 1: comments consistent with the code and with each other
I checked the `values.yaml` comments (in place of doc comments) against the templates. There are three findings.

- **`values.yaml:89`**, "The number of seconds to allow for graceful termination of the pod. Optional."
  - "the pod" is singular, but the value also reaches the restic DaemonSet (`restic-daemonset.yaml:56`). The comments around it each name their target ("for the Velero deployment"), and the restic settings live under `restic:` with "Restic daemonset" in their comments. A reader would conclude this key only affects the Velero server.
  - "Optional" sits on a key whose default is 3600, not unset. Its neighbors (`priorityClassName: ""`, `tolerations: []`) are "Optional" because they render nothing by default. This one changes every install, and to turn it off you have to pass `null`, which the comment doesn't say.
- No comment narrates the change ("now", "no longer"). None found.

## Item 2: claimed cases covered
Here a claimed case is something the description says the change covers, and its "test" is the place in the code or in CI that would show it holds.

| Claimed case | Covered by |
|---|---|
| Users can set the grace period | `deployment.yaml:61` renders the value. Covered by my rendering; the chart has no test that asserts it. |
| "allow Velero to finish a backup before terminating" | **None.** See item 3. Nothing in the chart, and no line cited from Velero, shows the server keeps a backup running after SIGTERM. If it exits at once, a longer grace period changes nothing. |
| "previously immutable, 30 seconds" | The default is now 3600, not 30. The description says the setting is new, not that the default for every install moves to 1 hour. **No sentence claims that change.** |

**Command lines.** The change adds no new commands. The existing README command `helm upgrade ... --reuse-values` now reaches this value; see item 3.

**Hunks no sentence claims:**
- **The restic DaemonSet hunk (commit 98041d0).** The description is about the Velero server finishing a backup and says nothing of the restic pods.
- **`Chart.yaml` version 2.31.8 → 2.31.9.** The repository's lint expects this bump, but no sentence mentions it.

## Item 3: boundaries, partitions, and the negative control
The partitions here are the values a user can pass, the state left by an earlier install, and the other limits on the same work.

- **Invalid values are not rejected.** As the table above shows, `-1` and `abc` render as written and only fail when the API server rejects them. The chart has no `values.schema.json`, so this matches its other keys. Taste.
- **The empty-value case is fine.** `null` renders a null field, which falls back to Kubernetes' 30 s. That is the only way to get the old behavior back, and nothing documents it (see item 1).
- **State from an earlier install.**
  - Every existing install that upgrades to 2.31.9 gets a changed pod template, which means a rollout, and both workloads move from 30 s to 3600 s. Nothing says this.
  - The Deployment has `replicas: 1` and the default RollingUpdate strategy, so maxSurge is 1. On that upgrade the new Velero pod starts while the old one is terminating. If Velero really does keep working after SIGTERM, which is the premise of the PR, two Velero servers run side by side for up to an hour. Velero 1.9 has no leader election.
  - For users who follow the README's `--reuse-values` command, Helm 3 reuses the old chart's values. The key would then be missing and render null (30 s), so the documented upgrade path never gets the 3600 default. I worked this out from Helm's reuse-values behavior; I could not run it without a cluster.
  - The request: a run that upgrades from 2.31.8 both ways, or a README note on both outcomes.
- **Other limits on the same work.** The grace period is only an upper bound. What actually decides how long a backup gets is:
  - **Velero's own SIGTERM handling.** This is in Velero, not in this repository. The request is the line in Velero 1.9 that waits for in-flight backups, or a run that shows a backup surviving `kubectl delete pod`.
  - **The `lifecycle` preStop hook.** It defaults to `{}`, so nothing delays SIGTERM.
  - **Limits in the environment that fire before 3600.**
    - Cluster-autoscaler's `--max-graceful-termination-sec` defaults to 600.
    - kubelet's `shutdownGracePeriod` applies on a node shutdown.
    - `kubectl drain --timeout` applies when a node is drained.

  The PR doesn't mention any of these. Raising the value past 600 has no effect under a default cluster-autoscaler.
- **The restic DaemonSet shares the same 3600.** During a node drain or a DaemonSet rolling update, a node-agent pod that doesn't exit promptly can hold each node for up to an hour, one node at a time. Whether that happens depends on how restic handles SIGTERM, which nothing here shows.
- **The negative control** (a value the user leaves unset still gives the old behavior) does not exist, because the default changed.

## Item 3a: level, placement, and the environment
- **The smallest test level is a template render.** The repository has no helm-unittest or golden render tests, and the gate is `ct lint` plus `ct install` on kind 1.16–1.25. That install only proves 3600 is accepted. It never terminates a pod during a backup, so the claimed behavior isn't exercised by any job.
- **Placement.** The DaemonSet reads the top-level key instead of a `restic.terminationGracePeriodSeconds`. Every other per-workload pod setting in the chart has its own `restic.*` copy (`priorityClassName`, `tolerations`, `lifecycle`, `podSecurityContext`, `nodeSelector`). Substantive.

## Item 4: names by content, not by position
None. The new key and its comment name things by content, and there are no ordinals or position words.

## Item 5: the failure report
None, because there are no assertions. As the analogue: no check exists to detect a wrong value, so nothing would report a failure (see item 3a).

## Item 6: what the writer says it verified
Nothing. Neither the commits nor the description give a rendered output, a run, or evidence that a backup survives termination.

## Item 7: siblings of the change
- **Sibling sets I checked.**
  - The other pod-spec keys (`priorityClassName`, `tolerations`, `lifecycle`) each exist both top-level and under `restic.`. The new key exists only top-level, so the restic sibling is missing (the same finding as in item 3a).
  - The README has no values table, so no list of keys is missing this one.
  - `ci/test-values.yaml` doesn't set the key, so CI only covers the default.
- **A pre-existing defect next to the change, not caused by it.** `restic-daemonset.yaml:165` checks `if .Values.lifecycle` but renders `.Values.restic.lifecycle`. It matters here because a preStop hook is the usual partner of a longer grace period. Worth naming as a follow-up.
- **Velero's own `resticTimeout`** (`values.yaml:290`, default 1h) also happens to be 3600 s. It only ends one pod-volume operation, so it isn't a limit on the same work. I'm noting it because a reader may assume the two values are linked.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| Default moves every install from 30 s to 3600 s, causing a rollout on upgrade; no sentence claims it | Substantive | `values.yaml:90` | Either default to unset (render the field only when set, like `priorityClassName`), or state the new default and its upgrade effect in the description and README |
| Nothing shows Velero keeps a backup running after SIGTERM, so the claimed use case is unverified; preStop hook and cluster-autoscaler's 600 s cap not addressed | Substantive | `deployment.yaml:61` | Cite the Velero 1.9 code that drains on SIGTERM, or a run where a backup survives pod deletion; document the cluster-autoscaler and drain limits |
| RollingUpdate plus a 1 h grace period lets two Velero servers overlap during upgrades | Substantive | `deployment.yaml:24`, `:61` | Say how this is safe, or set `strategy: Recreate` when the grace period is raised |
| DaemonSet reuses the top-level key instead of its own `restic.*` key; restic hunk not claimed by the description | Substantive | `restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds` with its own default, and a sentence that claims it |
| Comment says "the pod" and "Optional" but the key applies to two workloads, has a 3600 default, and needs `null` to restore 30 s | Substantive | `values.yaml:89` | Name both workloads (or only the Deployment, after the split), the default, and how to unset it |
| `--reuse-values` upgrade (README) never picks up the new default | Substantive (worked out from Helm's behavior, not run) | `README.md:75`, `:87` | Run the upgrade from 2.31.8 with and without `--reuse-values`, or document the outcome |
| No evidence the change was exercised | Substantive | — | Attach `helm template` output and the backup-survives-termination run |
| Chart version bump not mentioned | Taste | `Chart.yaml:6` | One sentence in the description |
| Negative or non-integer values render unchecked | Taste | `values.yaml:90` | Optional schema or `int` cast |
| Pre-existing `if .Values.lifecycle` / `.Values.restic.lifecycle` mismatch | Taste (follow-up) | `restic-daemonset.yaml:165` | Name it as a follow-up |

**Not checked:** nothing ran on a Kubernetes cluster, so `ct install`, the upgrade from 2.31.8, and Velero's actual SIGTERM behavior are unverified. I rendered only with helm v4.3.0, not CI's v3.8.1. The drift script doesn't parse Helm templates. I did not do a style pass over the prose.
