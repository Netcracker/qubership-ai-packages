# Final review: `bd5bf86..HEAD`, "[velero] Add Termination Grace Period Helm Value"

The change has no code and no tests. It edits a Helm chart: `values.yaml`, two templates and `Chart.yaml`. So I filled the form through the analogues in final-review §2a, and I name the analogue under each item. The drift script ran but printed nothing, because it does not parse YAML or Go templates. I loaded `test-authoring` and `english-developer-style` from the skills directory; there is no doc-comment skill for Helm values. There was no previous report.

I checked against the PR description, the two commit messages ("adding termination grace period seconds Helm value" and "adding specification of termination grace period to restic daemonset") and `charts/velero/ci/test-values.yaml`.

## Item 1: comments consistent with the code and with each other
**Analogue used:** the comments in `values.yaml`, and the statements the PR makes about the chart.

- **`charts/velero/values.yaml:89`** says "The number of seconds to allow for graceful termination of the pod. Optional." There are two problems with this comment:
  - **"the pod" doesn't say which pod.** Every other top-level comment around it names its target ("for the Velero deployment"). Every Restic setting lives under `restic.*` with its own comment ("for the Restic daemonset", lines 395–454). But this one top-level value also sets the Restic DaemonSet (`restic-daemonset.yaml:56`). A reader of `values.yaml` would conclude it affects only the Velero Deployment, and would look for `restic.terminationGracePeriodSeconds` to tune Restic.
  - **"Optional." is true but hides the default.** The default is now 3600, while Kubernetes' own default (and the chart's behavior until now) is 30. The comment doesn't state either number, so nobody reading it learns that upgrading changes the grace period by a factor of 120.
- **The PR says the 30 seconds were "previously immutable".** That is true of the chart: on the base commit `git grep` finds no `terminationGracePeriodSeconds` in the templates. No finding.
- No comment narrates the change.

## Item 2: claimed cases covered
**Analogue used:** each case the PR claims, matched against the place that handles it and the place that checks it.

| Claimed case | Handled at | Checked by |
|---|---|---|
| The grace period can be set via a Helm value | `deployment.yaml:61`, `values.yaml:90` | Nothing in the change. `ci/test-values.yaml` doesn't set it, so CI only renders the default. I rendered 120 by hand: it reaches both pod specs. |
| The Restic DaemonSet uses it (second commit) | `restic-daemonset.yaml:56` | Nothing. CI has `deployRestic: true`, so the default reaches it, but no CI run sets a value. |
| Velero gets to finish a backup that takes longer than 30 s before it is killed (the design's reason) | Not in the chart. It depends on the Velero server not exiting at once on SIGTERM and continuing an in-flight backup until it is done. | Nothing. The change gives no evidence that Velero 1.9.2 uses the extra time; I could not check without the Velero source or a cluster. If Velero exits right away on SIGTERM, the value changes nothing for backups. |

The second and third rows are substantive: the stated reason has no evidence, and the claimed setting has no case that sets it.

## Item 3: boundaries, partitions, and the negative control
**Analogue used:** the values a user can pass, plus the state an earlier chart version left behind.

Rendered with `helm template -f ci/test-values.yaml`:

| Value | Renders as | Effect |
|---|---|---|
| default | `3600` | |
| `120` | `120` | as expected |
| `0` | `0` | valid: kill immediately |
| `null` or `""` | `terminationGracePeriodSeconds: ` | the API reads it as unset, which gives 30 |
| `-5`, `abc`, `1.5` | the same text, unchanged | the chart accepts them; only the API server rejects them at install time |

- **Upgrade from 2.31.8 (substantive).** This is the pre-existing state the change will meet:
  - **Upgrade without `--reuse-values`:** the grace period on both workloads goes from 30 to 3600. This is a silent behavior change in a patch bump (2.31.8 → 2.31.9).
    - Velero rollouts: a rolling update may keep the old Velero pod for up to an hour.
    - `kubectl drain`: it may wait up to an hour per node on the Restic pod, if Restic doesn't exit promptly on SIGTERM.
  - **Upgrade with `--reuse-values`, the command the README itself shows (`README.md:75`, `:87`):** Helm reuses the old release's values, so the new key is likely missing and renders as null, which keeps 30. That comes from my reading of Helm 3's reuse-values merge; I did not run it, because there is no cluster.

  So the same chart version yields 30 or 3600 depending on the upgrade flag. Nothing in the change tests or documents either path.
- **Negative control (substantive).** There is no case that keeps the old behavior: nobody shows that setting 30, or leaving the value unset, restores the base commit's pod spec.
- **Invalid values (taste).** Negative and non-integer values pass through to the API with no chart-side guard. There is no `values.schema.json` in the chart, so this matches the rest of the chart.

## Item 3a: level, placement, and the environment
**Analogue used:** where each value and line lives, and whether the repository's gate passes.

- **Gate.** `helm lint . -f ci/test-values.yaml` passes ("1 chart(s) linted, 0 chart(s) failed"). The CI gate (`ct lint`, `ct install` with `ci/test-values.yaml`) would only exercise the default of 3600.
- **Placement (substantive).**
  - The Restic DaemonSet reads the top-level value. The convention for every other Restic pod setting (`restic.priorityClassName`, `restic.tolerations`, `restic.lifecycle`, …) is a key under `restic.*`.
  - The two workloads have different needs: a backup on the Velero server versus a Restic pod on a draining node. Yet one knob ties them together.
  - The second commit's message says it adds the setting "to restic daemonset", which reads as a separate setting.
- **Template placement (taste).** The template line sits next to `priorityClassName` in both pod specs, as its siblings do. Unlike them it has no `{{- if }}` guard, so a null value renders an empty key. That is harmless, and a guard would have to use `hasKey` or `kindIs` so it does not drop `0`.

## Item 4: names by content, not by position
**Analogue used:** the new key and the commit and PR wording.

None. The key `terminationGracePeriodSeconds` matches the Kubernetes field name, and nothing refers to anything by position.

## Item 5: the failure report
**Analogue used:** what tells a user a bad value is wrong.

There is no chart-side check. A bad value such as `abc` or `-5` renders and fails only at the API server, with the server's own validation message. That matches the rest of the chart, which has no schema. Nothing to request beyond the taste point in Item 3.

## Item 6: what the writer says it verified
None stated. The PR and the commits don't mention a `helm template` render, an install, or a run showing that a backup longer than 30 s survives a pod termination with the new value and fails without it.

## Item 7: siblings of the change
**Analogue used:** other places that read the value, and other pod specs in the chart.

- `git grep terminationGracePeriodSeconds -- charts` finds only the two templates and `values.yaml`. The matches in `crds/restores.yaml` belong to the vendored pod schema and are not relevant.
- The chart's other pod specs are the CRD-upgrade and cleanup Jobs. These are short-lived hook Jobs that the claim doesn't reach, so the defect doesn't apply to them.
- The README has no values table, so there is nothing there to update. Its Upgrading section is where the 30 → 3600 default change would belong (see Item 3).

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The default changes from 30 to 3600 for every upgrade without `--reuse-values`, silently, in a patch bump; with `--reuse-values` it likely stays 30 | Substantive | `values.yaml:90`, `Chart.yaml:6` | Either default to 30 (or leave the value unset) so upgrades keep their behavior, or document the change under README "Upgrading" and bump the version accordingly. |
| One top-level value also sets the Restic DaemonSet, against the `restic.*` convention, and the comment says only "the pod" | Substantive | `restic-daemonset.yaml:56`, `values.yaml:89` | Add `restic.terminationGracePeriodSeconds` with its own comment, or at least say in the comment that the value applies to both the Velero Deployment and the Restic DaemonSet. |
| The comment doesn't state the default or Kubernetes' default of 30 | Substantive | `values.yaml:89` | Name the default and what an unset value means. |
| The reason for the change (Velero finishes a backup within the grace period) has no evidence | Substantive | PR description | State a run showing that Velero 1.9.2 keeps working on an in-flight backup after SIGTERM, or narrow the claim. |
| CI never sets a non-default value and has no control case | Substantive | `ci/test-values.yaml` | Set a non-default value (for example 120) in the CI values so `ct install` exercises it. |
| No `if` guard: an unset value renders an empty key | Taste | `deployment.yaml:61`, `restic-daemonset.yaml:56` | Optionally guard with `hasKey`, keeping `0` valid. |

Not checked: no install or upgrade on a cluster (there was none), so the `--reuse-values` outcome and Velero's and Restic's SIGTERM handling are inferred, not observed. The drift script parses no YAML or templates. I did no style-only pass over the prose.
