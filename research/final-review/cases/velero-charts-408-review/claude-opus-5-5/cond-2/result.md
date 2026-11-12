# Final review: `bd5bf86..HEAD` ([velero] Add Termination Grace Period Helm Value)

The change adds a Helm value and a chart version bump, with no code, so I filled the form through §2a's analogues for a configuration. The drift script printed nothing because it doesn't parse YAML or Go templates; I matched the values comment against the templates by hand. I loaded `english-developer-style` and `test-authoring`. The chart has no doc-comment skill.

What I ran:
- **Lint:** `helm lint charts/velero -f charts/velero/ci/test-values.yaml` passes.
- **Default:** `helm template` with the CI values gives `terminationGracePeriodSeconds: 3600` in both the Velero Deployment and the restic DaemonSet.
- **Other values:** `--set terminationGracePeriodSeconds=null`, `=` and `--set-string …=60` render an empty field (Kubernetes then uses 30) or `60`.

This was Helm v4.3.0 locally. CI pins v3.8.1.

### Item 1: comments consistent with the code and with each other

**Substantive (two problems in one comment), `charts/velero/values.yaml:89`:** "The number of seconds to allow for graceful termination of the pod. Optional."

- **Where it applies.** The comment says "the pod" and sits among the "Velero deployment" settings (lines 86–98). But `restic-daemonset.yaml:56` reads the same key. A reader would think the restic pods keep Kubernetes' 30 s, when they get 3600 s on every node.
- **"Optional".** Elsewhere in this file, "Optional" goes with an empty default, which means the chart sets nothing. Here the default is 3600, 120 times the Kubernetes default. Nothing says how to get the old behavior back: an explicit `null` or empty value omits the field, which I checked above.
- **Request:** say that the value applies to both the Velero server pod and the restic pods, and that `null` keeps the Kubernetes default of 30 s. Alternatively, drop "Optional".

### Item 2: claimed cases covered

| Claimed case | Source | Covered by |
| --- | --- | --- |
| A grace period can be set through a Helm value | PR description, commit e5632c1 | Only the default renders: `ci/test-values.yaml` doesn't set the key, so `ct lint` and `ct install` only ever see 3600. I checked a non-default value by hand, but no repository run does. |
| Velero gets to finish a backup that runs past 30 s | PR description | `none`. See item 3 for what this depends on. |
| The restic DaemonSet gets the grace period | commit 98041d0 | Rendered (CI values set `deployRestic: true`). |

The change adds or edits no commands. The chart version bump to 2.31.9 is the release step `ct lint` requires, so it counts as claimed.

**Read the other way, Substantive, `charts/velero/values.yaml:90`:** the default of `3600` changes behavior for every existing and new install. Both the Velero Deployment and the restic DaemonSet go from 30 s to 1 h. Changing the pod template also rolls every restic pod on upgrade. The description says the change "adds in the ability to specify" the value, which reads as opt-in, and no sentence claims the new default.

**Request:** a sentence in the description that claims the new default for both workloads, or a default that keeps today's behavior (`null`, or no key with a `{{- with }}` guard).

**Substantive, `charts/velero/ci/test-values.yaml`:** the "ability to specify" case has no run. **Request:** set a non-default value (for example `terminationGracePeriodSeconds: 120`) in `ci/test-values.yaml`, so that `ct install` renders and applies a user value.

### Item 3: boundaries, partitions, and the negative control

**Partitions.** I checked by hand:
- **Default, explicit integer, `--set-string` integer:** all render correctly.
- **`null` or empty:** the field is omitted, so Kubernetes uses 30. This is the control, and the repository doesn't exercise it.

**Earlier state.** Releases upgraded with `helm upgrade --reuse-values`, as the chart README shows at lines 75 and 87, have no `terminationGracePeriodSeconds` in their stored values. With Helm 3.8 and later versions that predate `--reset-then-reuse-values`, the key renders empty and these releases keep 30 s. This is safe: it's the old behavior. But such users don't get the new default, which the description doesn't say. No finding; it's for the description's information.

**Other limits on the same work** (a backup in progress when the pod gets SIGTERM):
1. **Velero server shutdown, outside this repository (`velero server`, v1.9.2).** The 3600 s only helps if the server keeps processing the backup in flight after SIGTERM, instead of cancelling its context and exiting. If it exits right away, the grace period does nothing and the "previously immutable 30 seconds" was never the limit. Neither commit nor the description shows this.
   - **Substantive, `charts/velero/templates/deployment.yaml:61`.** Request: a run that starts a backup longer than 30 s, deletes the Velero pod, and shows the backup finishing, or a link to the server code that waits on shutdown.
2. **`configuration.resticTimeout`, `values.yaml:290`.** Its comment says the `velero server` default is 1 h, the same as the new grace period. If a user raises `resticTimeout` past 1 h, a shutdown during a long restic backup is still cut off at 3600 s. If a user raises the grace period past `resticTimeout`, the backup gives up on restic first and ends PartiallyFailed, so the extra grace does nothing for pod-volume backups.
   - **Substantive, `charts/velero/values.yaml:90`.** Request: state the relation in the comment (the grace period should be at least `resticTimeout` plus the non-restic part of a backup), or derive one from the other in the template.
3. **The environment.** Cluster Autoscaler scale-down caps a pod's grace period at `--max-graceful-termination-sec`, which defaults to 600. A `kubectl drain --timeout` or a managed node-group drain timeout can fire first too. Above those limits, the setting has no effect during autoscaler scale-down.
   - **Taste.** Mention it in the comment. These limits live outside this repository, and the PR names no environment.

### Item 3a: level, placement, and the environment

none. The smallest level for a chart is `helm template` and `helm lint`, and `ct lint` and `ct install` run them in CI. The repository has no helm-unittest. The new key sits beside the other pod-spec keys in `values.yaml` and in each template's pod spec.

### Item 4: names by content, not by position

none. The key name, the comment and the commit subjects refer to the setting by what it is.

### Item 5: the failure report

none. I used the analogue: the change has no assertions. The only check is `ct install` failing on an invalid pod spec, and that prints the API server's error.

### Item 6: what the writer says it verified

Neither the description nor the commit messages say anything was run. There's no rendered output, and no evidence that a backup survives pod termination with the new value and fails with 30 s. Item 3 asks for that run.

### Item 7: siblings of the change

I searched for `priorityClassName` and `lifecycle`, which are set for both workloads. Each has a top-level key for the Velero Deployment and a `restic.*` key for the DaemonSet (`values.yaml:87/396`, `values.yaml:84/446`).

**Substantive, `charts/velero/templates/restic-daemonset.yaml:56`:** the restic DaemonSet reads the top-level `terminationGracePeriodSeconds` instead of a `restic.terminationGracePeriodSeconds` in the `restic:` block, where every other restic pod setting lives.
- **Effect:** users can't keep a long grace for the Velero server and a short one for restic pods. Restic pods run on every node, and their 1 h grace slows any node drain whose restic pod doesn't exit promptly.
- **Request:** add `restic.terminationGracePeriodSeconds` with its own comment, and render it in the DaemonSet.

The Jobs in `cleanup-crds.yaml` and `upgrade-crds.yaml` don't do backup work, so they don't need the key. The README has no values table that lists keys, so there was no list to update.

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The comment says "the pod" and sits among Deployment settings, but the key also sets the restic DaemonSet; "Optional" sits on a 3600 default, with no way to get 30 back stated | Substantive | `charts/velero/values.yaml:89` | 1 |
| The 3600 default changes both workloads from 30 s to 1 h, and the description doesn't claim it | Substantive | `charts/velero/values.yaml:90` | 2 |
| CI values don't set the key, so only the default is ever rendered or installed | Substantive | `charts/velero/ci/test-values.yaml` | 2 |
| Nothing shows that the Velero 1.9.2 server keeps processing a backup after SIGTERM, which is what the grace period depends on | Substantive | `charts/velero/templates/deployment.yaml:61` | 3 |
| The grace period and `configuration.resticTimeout` (default 1 h) bound the same work with no stated relation | Substantive | `charts/velero/values.yaml:90` | 3 |
| Cluster Autoscaler's `--max-graceful-termination-sec` (default 600) caps the value during scale-down | Taste | `charts/velero/values.yaml:89` | 3 |
| The restic DaemonSet reads the top-level key instead of a `restic.*` sibling like `restic.priorityClassName` and `restic.lifecycle` | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 7 |

Two checks couldn't be done: the drift script doesn't parse YAML or Helm templates, and without a cluster or the Velero source I couldn't confirm what `velero server` v1.9.2 does on SIGTERM.
