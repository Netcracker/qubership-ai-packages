# Final review: `bd5bf86..HEAD` ([velero] Add Termination Grace Period Helm Value)

There is no previous report for this change. I used the task statement quoted in the request, the two commit messages, and the diff.

The change is a Helm chart with no code. It adds one value, uses it in two templates, and bumps the chart version. So I filled the form through the §2a analogues and say which one under each item. I loaded `english-developer-style` and `test-authoring`. No `docs-page-authoring` or chart-authoring skill was available, so none was loaded.

I ran the drift script `comment-drift.py bd5bf86 HEAD`. It exited 0 and printed nothing, because it does not parse YAML or Go templates. I checked the comments by hand instead.

## Item 1: comments consistent with the code and with each other
(Analogue: the statements the changed files make.)

- **`charts/velero/values.yaml:89`.** The new comment says "the pod". It sits among sibling comments that all say "for the Velero deployment" (lines 84, 86, 92, 95, 98), and the restic block has its own per-component comments (`restic.priorityClassName`, `restic.lifecycle`). Yet `templates/restic-daemonset.yaml:56` also reads this top-level value. A reader would conclude that the value affects only the Velero server pod, and would not know that it also changes the grace period of every restic pod.
- **The same comment says "Optional."** It does not say what happens when the value is left empty. Rendering it with `--set terminationGracePeriodSeconds=null` gives `terminationGracePeriodSeconds:` (YAML null), so Kubernetes applies its default of 30 s. A reader also cannot tell from the comment that the chart default of 3600 differs from the Kubernetes default of 30.
- There is no narration such as "now" or "no longer" in the comment.

## Item 2: claimed cases covered
(Analogue: the section of the change that handles each claimed case.)

- **"Specify the termination grace period":** handled by `values.yaml:90` and `deployment.yaml:61`. `helm template` renders 3600 by default, 7200 when set to 7200, and null when set to null.
- **Restic daemonset (second commit's message):** handled by `restic-daemonset.yaml:56`, which renders 3600.
- **"Allow Velero to finish a backup before terminating":** nothing in the change shows this. A longer grace period only helps if the Velero server, on SIGTERM, keeps running the backup in progress instead of exiting. Neither the change nor the PR description shows that Velero v1.9.2 does this. I had no Velero source to check it against.
  - Velero's controller-runtime manager may also enforce its own graceful-shutdown timeout, which I believe defaults to 30 s; I could not verify this.
  - This is the case the PR exists for, and it has no evidence (see item 6).
- **Unstated change to the default:** the PR says the old default was "immutable, 30 seconds". It does not say the new default is 3600, so every install changes behavior on upgrade. That is a claimed-and-hidden case; see item 3.

## Item 3: boundaries, partitions, and the negative control

- **Pre-existing state.** A release installed from 2.31.8 that runs `helm upgrade`, with or without `--reuse-values`, moves from 30 s to 3600 s without anyone choosing it.
  - The Deployment sets no `strategy`, so it defaults to RollingUpdate. With one replica, maxSurge rounds up to 1 and maxUnavailable rounds down to 0.
  - During a rollout, the new Velero pod starts while the old one may stay in Terminating for up to an hour. If the old process honors the grace period (the premise of the PR), two Velero servers run against the same cluster at the same time. That is a mode Velero is not built for.
  - Every restic pod on every node also gets up to an hour to drain.
  - The request: keep the default at the Kubernetes value (30, or null), state the new default in the description, or add `strategy: Recreate`.
- **Other limits on the same quantity:**
  1. **Velero's own shutdown behavior (inner limit):** possibly a fixed timeout; it is not set by the chart and is unverified.
  2. **The environment (outer limits):**
     - Cluster Autoscaler scale-down caps graceful termination at `--max-graceful-termination-sec`, default 600.
     - The kubelet's `shutdownGracePeriod` applies on node shutdown.
     - Spot or preemptible nodes give about 30 s.
     - `kubectl drain --timeout` applies when one is set.

  Any value past 600 has no effect under Cluster Autoscaler, and the chart default of 3600 is already past it. The request is to document these limits next to the value.
- **Invalid partitions.** The chart has no `values.schema.json` and no guard in the template:
  - `--set terminationGracePeriodSeconds=abc` renders `terminationGracePeriodSeconds: abc`.
  - `-1` renders `-1`.

  The API server rejects both at install time, not at template time. Siblings such as `priorityClassName` are wrapped in `{{- if }}`. This one is not, which is fine for null, but there is no type check. I filed this as taste.
- **Negative control:** the empty value renders null, so Kubernetes uses 30 s. I checked this by hand; nothing in the change exercises it.
- **Restic disabled:** with `--set deployRestic=false`, only the Deployment carries the field. That is correct.

## Item 3a: level, placement, and the environment
(Analogue: rule placement and the repository gate.)

- The value sits next to `priorityClassName` in the Velero-deployment block, which is consistent with its siblings.
- There is no per-component `restic.terminationGracePeriodSeconds`, although the restic block mirrors `priorityClassName`, `lifecycle`, and `tolerations`. A user cannot give the server an hour without also giving it to restic. The daemonset already shares top-level `podLabels` and `podAnnotations`, so there is precedent both ways; filed as taste.
- `helm lint . -f ci/test-values.yaml` passes.
- `ci/test-values.yaml` does not set the value, so CI's `ct install` exercises only the default. No CI case sets a non-default value or null.

## Item 4: names by content, not by position
None. The one new key and its comment refer to nothing by position.

## Item 5: the failure report
(Analogue: what a bad value reports.)

There is no validation. A non-integer value surfaces only as an API-server rejection at install time, not as a chart error naming the value. This is covered under item 3.

## Item 6: what the writer says it verified
Neither the commits nor the PR description state any evidence:

- **That the template renders:** no `helm template` output is quoted.
- **The PR's premise:** there is no run showing a backup surviving a SIGTERM longer than 30 s.

## Item 7: siblings of the change
(Analogue: the places that read the same setting or enumerate the chart's values.)

- **`templates/restic-daemonset.yaml:56`:** covered by the second commit, and it shares the top-level value (items 1 and 3a).
- **`charts/velero/README.md`:** has no values table (line 27 points at `values.yaml`), so nothing is owed there.
- **`ci/test-values.yaml`:** not updated (item 3a).
- **Other workloads that already set this field:** `git grep terminationGrace` finds no other templates. The kubectl upgrade and cleanup Jobs are not long-running, so they don't apply.
- **Related pre-existing bug, outside this change:** `restic-daemonset.yaml:165` tests `.Values.lifecycle` but renders `.Values.restic.lifecycle`. It is the same kind of mix-up between top-level and restic values that this change risks. It could be named as follow-up.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The default changes from 30 to 3600 for every existing release on upgrade, and the PR doesn't say so. With RollingUpdate and maxSurge 1, two Velero servers can overlap for up to an hour. | Substantive | `charts/velero/values.yaml:90`, `templates/deployment.yaml:24` | Default to null or 30, or state the new default and add `strategy: Recreate`. |
| The comment says "the pod" among "Velero deployment" siblings, but the value also drives the restic daemonset. It doesn't say that empty means the Kubernetes default of 30. | Substantive | `charts/velero/values.yaml:89` | Say it applies to both the Velero deployment and the restic daemonset, and that empty uses the Kubernetes default (30 s). |
| Outer limits make values past them useless (Cluster Autoscaler 600 s, kubelet node shutdown, spot nodes), and the default 3600 is past the first one. | Substantive | `charts/velero/values.yaml:89` | Document the limits next to the value, or pick a default under them. |
| Nothing shows that the Velero server or restic waits for an in-progress backup on SIGTERM, which is the PR's stated purpose. | Substantive | PR description | State the evidence: a run, or a reference to Velero's shutdown code. |
| CI covers only the default; no case sets a value or null. | Substantive | `charts/velero/ci/test-values.yaml` | Add a non-default value, for example 120, to the CI values. |
| There is no per-component `restic.terminationGracePeriodSeconds`, unlike `restic.priorityClassName` and `restic.lifecycle`. | Taste | `templates/restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds`, falling back to the top-level value. |
| There is no type check, so `abc` or `-1` render and fail only at the API server. | Taste | `templates/deployment.yaml:61` | Add `values.schema.json` with an integer type and minimum 0, or use `int` in the template. |

I did not check four things:

- How Velero v1.9.2 and restic actually handle SIGTERM; there was no source or cluster.
- `ct install` against a kind cluster.
- A style-only pass over the prose.
- The change itself through the drift script, which does not parse YAML or Go templates.
