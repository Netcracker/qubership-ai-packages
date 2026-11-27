I didn't change or commit anything. To render the chart I made scratch copies in the scratchpad. One slip: I briefly added a `git worktree` for the base commit, then removed and pruned it. `git worktree list` and `git status` show the repository as it was.

# Final review: `bd5bf86..HEAD` (Velero termination grace period)

**Inputs.**
- **Diff:** 4 files, 6 lines added and 1 removed: `Chart.yaml`, `templates/deployment.yaml`, `templates/restic-daemonset.yaml` and `values.yaml`.
- **Task statement:** the pull request description you quoted. The commit messages are the other two sources of claims.
- **Pull request start:** not given, and `main` isn't in this clone. So under "The pull request" I only report claims that would be false whatever the start is; none are.
- **Drift script:** ran from the repo root and printed nothing, because it doesn't parse YAML or Helm templates.
- **Change type:** configuration with no code, so I used the configuration analogues from §2a. I loaded `english-developer-style`. No doc-comment or docs-page authoring skill applies.
- **Checks run:** `helm lint` passes. I rendered the chart with `helm template` (Helm v4.3.2) for these cases: the default, `0`, `null`, `""`, `-1`, `abc`, `1000000` from a values file, and a values file with the key missing. I also rendered the base commit for comparison.

## Item 1: comments consistent with the code and with each other

Analogue: the statements in the added `values.yaml` comment, checked against the templates and the comments next to it.

- **`values.yaml:89` "graceful termination of the pod".** The value applies to two kinds of pod: the Velero server pod (`deployment.yaml:61`) and every restic pod (`restic-daemonset.yaml:56`).
  - The neighboring comments all name their target ("for the Velero deployment", "for the Restic daemonset").
  - A reader will think this only changes the server pod.
  - **Request:** fix this together with the shared key under Item 7. If one key stays, the comment says it applies to both the Velero deployment and the restic daemonset.
- **`values.yaml:89–90` "Optional." next to `3600`.** In this file, "Optional" next to an empty default means nothing is rendered unless the user sets a value. Here the template always renders the field, so leaving the key out gives every pod 3600 seconds.
  - The only way back to the Kubernetes default (30 seconds) is `null`; I rendered it and it produces an empty field. The comment doesn't say so.
  - `3600` has no explanation either. It matches the `velero server` default for `resticTimeout` (1h, `values.yaml:289`), but nothing says whether that's on purpose.
  - **Request:** say what the default is and why it was chosen, and that `null` gives the Kubernetes default of 30 seconds. Or make the default `null`/empty, which matches the description's framing; see Item 2.
- **Terms:** the change introduces none.

## Item 2: claimed cases covered

Claimed cases, with what covers each:
- **"Ability to specify the termination grace period"** (title, description, commit e5632c1). No CI case sets a non-default value: `ci/test-values.yaml` doesn't set the key, so `ct install` only covers 3600. I checked `0`, `null` and a custom value by rendering locally, and the change doesn't report any such run. **Request:** add the key with a non-default value to `ci/test-values.yaml`.
- **"Allow Velero to finish a backup before terminating"** (the description's main use case). Nothing shows this works; see the limits finding under Item 3.
- **Daemonset gets the grace period** (commit 98041d0). Covered by the template render.

Hunks that no sentence claims:
- **The default changes from the Kubernetes 30 seconds to 3600 seconds for every install.** The description calls 30 seconds "previously immutable", which reads as adding a setting, not changing every release's behavior. Neither commit message mentions the new default. **Request:** a sentence that claims and justifies the 3600 default, or a null default.
- **The daemonset hunk is claimed only by its commit message.** The description talks only about Velero finishing a backup. Because the start is missing, I can't say for certain this shows up in the pull request's diff; if it does, the description needs a sentence claiming the restic daemonset.
- **The `Chart.yaml` version bump is not a finding.** chart-testing's `ct lint`, which CI runs, requires the chart version to go up when a chart changes, so the bump belongs to the claimed change.

The change adds no commands.

## Item 3: boundaries, partitions, and the negative control

**Boundaries, from local renders:**
- `0` renders as `0`, which is correct; the template deliberately doesn't wrap the field in `if`, which would drop it.
- `null` or `""` render as an empty field, so Kubernetes applies its 30-second default.
- `-1` and `abc` are rendered as given and only rejected by the API server. That matches the rest of this chart, which has no values schema, so it's not a finding.
- **A large number from a values file renders in scientific notation.** `terminationGracePeriodSeconds: 1000000` in a `-f` file renders as `terminationGracePeriodSeconds: 1e+06`. Helm reads numbers from values files as floats and prints them in this form from 10⁶ up, which an integer field won't accept. `--set` doesn't have this problem. Values that large (about 11.5 days) are unlikely, but it's an invalid rendering. **Request:** `{{ .Values.terminationGracePeriodSeconds | int }}`, guarded so that `null` still renders nothing.

**Existing installs:**
- **`helm upgrade --reuse-values` gives a different result from the other upgrade paths.** The chart README documents that command (`README.md:75`, `:87`). With `--reuse-values`, an existing release keeps its stored values, which have no `terminationGracePeriodSeconds`.
  - I rendered the new templates with values missing the key: the field comes out empty, so the pods keep 30 seconds.
  - A plain `helm upgrade` or a fresh install gives 3600.
  - Nothing tells the user that the outcome depends on which upgrade flags they use. **Request:** a line in the README or the values comment saying an existing release upgraded with `--reuse-values` must set the key explicitly. Or confirm by a run that this is intended.

**Other limits on the same work.**
- **Velero's own response to SIGTERM decides whether this setting has any effect.** That code is in the Velero binary, not in this repository. My recollection is that `velero server` v1.9 cancels its context on SIGTERM and exits without waiting for an in-progress backup, and marks InProgress backups as Failed on the next start. I haven't verified that. If it's right, raising the grace period lets no backup finish.
  - **Request:** a link to the line in `velero server` that waits for a running backup after SIGTERM, or a run where the pod is deleted mid-backup and the backup still completes. The same goes for `velero restic server` in the daemonset.
- **The rollout lets two Velero servers overlap.** The Deployment uses the default RollingUpdate strategy, so with 1 replica the new pod starts before the old one finishes terminating. If Velero does keep working through the grace period, two servers run side by side for up to an hour. The change doesn't say whether that's acceptable.
- **Limits set elsewhere stop the setting from having any effect above them:**
  - cluster-autoscaler's `--max-graceful-termination-sec`, 600 seconds by default, for scale-down evictions;
  - the kubelet's `shutdownGracePeriod`, for node shutdown.
  - **Request:** the values comment names these, so nobody sets 3600 expecting it to apply during autoscaler drains or node shutdown.
- **The default may be too short for what Velero itself allows.** `--restic-timeout` (default 1h, `values.yaml:289`) bounds the pod volume backups inside a backup. A backup that's already under way when SIGTERM arrives can therefore run past 3600 seconds while still inside Velero's own timeout. **Request:** set the default from `resticTimeout` or explain the choice; this is the same comment Item 1 asks for.

## Item 3a: level, placement, and the environment

`none`. For a Helm chart, rendering the template is the smallest test level, and CI's `ct lint` and `ct install` already render it. There is no template unit-test framework to place a test beside. The non-default render is covered under Item 2.

## Item 4: names by content, not by position

`none`. The key name, the comment and the commit messages refer to nothing by position.

## Item 5: the failure report

`none`. Analogue: the change adds no assertions or checks; an invalid value fails at the API server with Kubernetes' own error.

## Item 6: what the writer says it verified

The change states no evidence: no rendered output, no `ct install` result, and no run showing a backup surviving pod termination. The main use case therefore rests on an unverified assumption about Velero's SIGTERM handling (Item 3).

## Item 7: siblings of the change

- **The daemonset reads the server's top-level key.** The chart gives the restic daemonset its own copies of the server's pod settings: `restic.priorityClassName` (`values.yaml:396`), `restic.lifecycle` (`values.yaml:446`), and its own resources and tolerations. This change makes `restic-daemonset.yaml:56` read the top-level `terminationGracePeriodSeconds`, which sits among the "Velero deployment" settings. One value now controls both pods, and the daemonset rollout can take up to 3600 seconds per node. **Request:** add a `restic.terminationGracePeriodSeconds` key and use it in `restic-daemonset.yaml:56`.
- **No other list of values keys needs updating.** The README only points readers to `values.yaml`, and there is no schema. No sentence in the change counts keys.

## Findings index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The comment says "the pod", but the value applies to the Velero pod and every restic pod | Substantive | `charts/velero/values.yaml:89` | 1 |
| "Optional." sits next to an always-rendered 3600; nothing says `null` gives 30s or why 3600 was chosen | Substantive | `charts/velero/values.yaml:89-90` | 1 |
| No CI values file sets a non-default value | Substantive | `charts/velero/ci/test-values.yaml` | 2 |
| The 30s → 3600s default change for every install is claimed nowhere | Substantive | `charts/velero/values.yaml:90` | 2 |
| The description doesn't claim the daemonset hunk (conditional on the missing start) | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 2 |
| A value ≥ 1000000 from a values file renders as `1e+06` | Substantive | `charts/velero/templates/deployment.yaml:61` | 3 |
| `--reuse-values` upgrades keep 30s while other upgrades get 3600s, and nothing says so | Substantive | `charts/velero/values.yaml:90` | 3 |
| Nothing shows Velero keeps a backup running after SIGTERM, which the setting needs to have any effect | Substantive | `charts/velero/templates/deployment.yaml:61` | 3 |
| Autoscaler and kubelet shutdown limits cap the value, and the 3600 default is below what `resticTimeout` allows | Substantive | `charts/velero/values.yaml:89` | 3 |
| The daemonset reads the server's top-level key instead of a `restic.*` key | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 7 |

Three checks couldn't be done:
- The drift script doesn't parse YAML or Helm templates.
- The pull request start wasn't given and `main` isn't in this clone.
- Velero's SIGTERM handling is not in this repository, and I couldn't run anything against a cluster.
