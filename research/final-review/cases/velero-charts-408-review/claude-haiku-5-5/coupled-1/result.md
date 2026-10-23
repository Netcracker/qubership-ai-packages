Review of `bd5bf865..HEAD` (two commits: `e5632c1`, `98041d0`), done as the fresh reviewer. No files changed, nothing committed.

**Setup.** The change is YAML and Helm templates only, with no code and no tests. I loaded `english-developer-style` for the wording. `test-authoring` does not apply because the change adds no tests. The drift script (`skills/final-review/scripts/comment-drift.py`) exited 0 with no output because it parses no YAML members, so item 1 was done by reading. `helm lint charts/velero` passes. I rendered the chart with `helm template` in the default case and with `terminationGracePeriodSeconds` set to empty, `30`, and default, with `deployRestic=true`. This is the first review of this change, so there is no previous report to compare against.

## Item 1: comments consistent with the code and with each other

Substantive findings are in the table below. The value comment at `charts/velero/values.yaml:89` ("The number of seconds to allow for graceful termination of the pod. Optional.") does not state the default, and the sentence says "Optional" for a key that always renders a value. It also says "the pod" without saying that the restic DaemonSet pods get the same value. The sibling comment for `priorityClassName` says "for the Velero deployment".

## Item 2: claimed cases covered

Substantive. The PR claims the ability to specify the grace period. Nothing exercises a non-default value. `ct install` in `.github/workflows/lint-test.yaml` uses `charts/velero/ci/test-values.yaml`, which does not set the key, so a custom value reaching both pod specs is unverified. The PR's claim that Velero finishes a backup before exiting is about runtime behavior outside this repo, and this review cannot check it.

## Item 3: boundaries, partitions, and the negative control

Substantive. The change sets a duration, so the limits along the path are these:
- The new pod grace period: `values.yaml:90`, default 3600, rendered at `deployment.yaml:61` and `restic-daemonset.yaml:56`.
- `configuration.resticTimeout`: `values.yaml:290`, documented as "`velero server` default: 1h", passed at `deployment.yaml:83-84`.
- The environment: the API server and kubelet impose no cap that I found in the chart. The 30-second Kubernetes default applies only when the field is unset.

At defaults the grace period and the restic timeout are both 3600 seconds, and the chart does not state how they relate. Whether the grace period is actually needed to outlast an in-flight restic run depends on Velero's SIGTERM handling, which this repo does not show. Empty input renders `terminationGracePeriodSeconds: ` (null), which the API server treats as unset. The pod then gets 30 seconds, not 3600. That partition is untested. Also, the change alters the pod template, so `helm upgrade` on an existing release rolls every Velero and restic pod. No upgrade path is considered.

### Item 3a: level, placement, and the environment

Substantive, under item 2. There is no test at any level, and the chart's only install check (`ct install`) does not set the new key. The key sits alphabetically between `priorityClassName` and `tolerations` in `values.yaml`, which matches the file. `helm lint` passes.

## Item 4: names by content, not by position

none. Checked `terminationGracePeriodSeconds` and the comment text, and neither refers by position.

## Item 5: the failure report

none. The change has no assertions. The chart has no failure report of its own.

## Item 6: what the writer says it verified

No evidence stated. The PR description and the two commit messages give no render output, no `helm template` run, and no install. I rendered the chart myself as described under Setup, and the output is consistent with the intent: 3600 by default, 30 when set, and the restic DaemonSet gets the same value.

## Item 7: siblings of the change

none beyond what is covered above. The only other consumer of the key is the restic DaemonSet, which the change already covers. No other chart exists in the repo. `charts/velero/README.md` does not list individual values, so it has no sibling entry to update. `ci/test-values.yaml` is the one sibling that should set the key, covered under item 2.

## Report

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Default 3600 changes termination for every install and upgrade from the 30-second Kubernetes default, and neither the comment nor the PR says so | substantive | `charts/velero/values.yaml:89-90`, `charts/velero/templates/deployment.yaml:61`, `charts/velero/templates/restic-daemonset.yaml:56` | State the default and its effect on upgrades in the comment and the PR description, or set the default to 30 so existing installs do not change |
| The comment says "Optional" and "the pod", but the value always renders, applies to restic pods too, and an empty value silently gives 30 seconds | substantive | `charts/velero/values.yaml:89` | Name the default, that it covers the Velero and restic pods, and what an empty value does |
| The grace period and `resticTimeout` (default 1h) are a limit pair at defaults, and the chart documents neither relation | substantive | `charts/velero/values.yaml:90` and `:290`, `charts/velero/templates/deployment.yaml:83-84` | Document the pair in the comment, or derive one from the other |
| The claimed ability to set the grace period has no test or CI check that sets it | substantive | `charts/velero/ci/test-values.yaml` (not changed) | Set the key in `ci/test-values.yaml`, or add a render check that a custom value reaches both pod specs |

**Not checked:** how Velero handles SIGTERM and whether it needs the longer grace period, because that is outside this repo. The kind install (`ct install`) and `ct lint` did not run, since there is no cluster and `ct` is not available here. I ran `helm lint` and `helm template` only.
