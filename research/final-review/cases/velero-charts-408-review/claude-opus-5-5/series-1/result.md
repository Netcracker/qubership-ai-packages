# Final review: `bd5bf86..HEAD`, "[velero] Add Termination Grace Period Helm Value"

There is no earlier report on this change. The change is Helm templates and values only. The drift script `comment-drift.py bd5bf86 HEAD` printed nothing because it doesn't parse YAML or Go templates, so every item below uses the configuration analogues from §2a. I loaded `test-authoring` and `english-developer-style`.

## Item 1: comments consistent with the code and with each other

The only comment the change adds is at `charts/velero/values.yaml:89`: "The number of seconds to allow for graceful termination of the pod. Optional."

- **Finding (substantive):** "the pod" doesn't say which pod. The key sits among keys whose comments all say "for the Velero deployment" (lines 83–87), so a reader takes it to apply to the Velero server only. In fact `restic-daemonset.yaml:56` reads the same key, so the restic pods get it too. Every other pod-spec setting the daemonset uses has its own `restic.*` key: `restic.priorityClassName` at line 396 and `restic.lifecycle` at line 446.
- **Finding (taste):** "Optional" next to a default of `3600` reads as "leave it out and nothing is set". But the template always renders the field, and leaving it unset needs an explicit `null`, which renders `terminationGracePeriodSeconds: ` (I checked this with `helm template`).
- No comment narrates the change.

## Item 2: claimed cases covered

Claims and what covers each:

| Claim (source) | Covered by |
|---|---|
| A user can set the grace period (PR) | No test; the chart has no unit tests. My `helm template --set terminationGracePeriodSeconds=60` renders `60` in both the Deployment and the DaemonSet. CI's `ct lint`/`ct install` with `ci/test-values.yaml` only exercises the default `3600`. |
| The grace period is applied to the restic daemonset (commit 98041d0) | Same `helm template` runs; restic is rendered with `deployRestic=true` and by CI's test-values. |
| "allow Velero to finish a backup before terminating" past 30 s (PR) | **None.** This is the reason the PR gives for the change. The test that would fail without the design is a backup that is still running when the pod gets SIGTERM, and nothing runs that. See the limits finding under item 3. |

- **Commands documented in changed files:** none.
- **Hunks no sentence claims:**
  - `Chart.yaml` `2.31.8 → 2.31.9`. **Finding (taste):** the repository's `ct lint` version-increment check requires this bump, but no sentence in the description says so.
  - The default changing from Kubernetes' 30 s to **3600 s** for every release. **Finding (substantive):** the PR says it "adds the ability to specify". Nothing says the default for existing users goes from 30 s to one hour, on both the server and every restic pod. The request is either a sentence that claims this, with the reason for choosing 3600, or a default that keeps the old behaviour (30, or leave the field out when it is unset).

## Item 3: boundaries, partitions, and the negative control

- **Values I rendered with `helm template`:** default → `3600`; `60` → `60`; `0` → `0`; `null` and `""` → empty field, which is null and so falls back to the cluster default of 30; `-1` → `-1`; `abc` → `abc`. There is no `values.schema.json`, so invalid values such as `-1` or `abc` only fail at the API server. No other value in this chart has a schema, so I don't file this.
- **Finding (substantive): state left by an earlier install.** The chart README's documented upgrade is `helm upgrade … --reuse-values --set …` (`README.md:75`). With `--reuse-values`, Helm 3 builds the values from the previous release's chart defaults, which don't have this key. The field then renders as null and the pods keep 30 s, so the "Upgrade the configuration" path silently doesn't get the new default. A fresh install gets 3600. The other paths are also untested: an upgrade without `--reuse-values` changes 30 → 3600 and rolls both workloads. The request is a run of `helm upgrade --reuse-values` from 2.31.8, or a template that handles a missing key explicitly, with a note in the README's Upgrading section.
- **Finding (substantive): other limits on the same work.** The grace period only matters if the work continues after SIGTERM:
  - **The `velero server` process.** If it cancels its context on SIGTERM and exits, which is how the 1.9 server shuts down as far as I know (I have not verified it), the pod ends as soon as it exits. In that case any grace period, 30 or 3600, has no effect on an in-progress backup, and the PR's stated purpose isn't met. That code is not in this repository. The request is the line in Velero v1.9.2 showing that the backup controller drains in-flight backups on shutdown, or a run that sends SIGTERM during a backup longer than 30 s.
  - **The preStop hook (`lifecycle`, `values.yaml:84`).** The hook runs inside the same grace window. It is the usual way to make a pod wait, and it is not mentioned.
  - **Limits set by the environment.** Cluster-autoscaler caps graceful termination on scale-down at its `--max-graceful-termination-sec` (default 600 s). `kubectl drain --timeout` and spot or preemptible node notices also end the pod early. So a value of 3600 has no effect on those paths beyond the cap.
  - **`configuration.resticTimeout`.** Its default is 1 h, which equals the new default. It limits a single restic operation, so it doesn't count as a limit on the same work, but the matching number suggests it was the source. The change doesn't say.
- **Negative control:** nothing renders the chart without the field. With `null` the output is an empty field rather than no field at all.

## Item 3a: level, placement, and the environment

The smallest level that can observe the change is a render. The repository has no helm-unittest suite and no other render-assertion tests, so I don't owe a request for one; the change's rendering was checked only by my `helm template` runs. `helm lint` passes. CI's `ct install` runs on a kind cluster with `ci/test-values.yaml` (`deployRestic: true`), so it does install both changed objects with `3600`, but it never sends SIGTERM to a pod. The template lines sit beside the other pod-spec fields in the right place. Finding: none beyond item 3.

## Item 4: names by content, not by position

None. The change adds one key name and one comment, and neither refers to anything by position.

## Item 5: the failure report

None. The change adds no assertions. As a §2a analogue: a bad value fails only at the API server, with the server's own message.

## Item 6: what the writer says it verified

Neither the commits nor the PR say anything was run: no `helm template` output, no install, no backup interrupted by SIGTERM. **Finding (substantive):** the PR's stated purpose has no evidence (see item 3).

## Item 7: siblings of the change

- **Other readers of the setting:** `git grep terminationGracePeriodSeconds -- charts` finds only the two templates (the CRD hits are restore-spec schemas, unrelated). The other pod templates are the `upgrade-crds.yaml` and `cleanup-crds.yaml` hook Jobs. They are short-lived and don't need it. None.
- **Sets the new key joins:** the per-workload pod-spec keys come in pairs (`priorityClassName` / `restic.priorityClassName`, `lifecycle` / `restic.lifecycle`, tolerations, nodeSelector). This key has no `restic.*` counterpart, and the restic template reads the server's key. **Finding (substantive):** server and restic can't be tuned separately. A one-hour grace period on every restic pod also slows DaemonSet rolling updates and node drains, if those pods do wait out SIGTERM. The request is a `restic.terminationGracePeriodSeconds` key, or a sentence in the values comment saying the key is shared on purpose.
- **Lists of values:** the README doesn't keep a table of values, so there's no list to update. None.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The default changes from 30 s to 3600 s for all releases (server and restic), and no sentence claims it | Substantive | `charts/velero/values.yaml:90` | State it in the description with the reason, or keep the 30 s default or leave the field out when unset |
| No evidence that Velero keeps backing up after SIGTERM; if the server exits right away, the grace period does nothing | Substantive | `charts/velero/templates/deployment.yaml:61` | The Velero v1.9.2 shutdown line, or a SIGTERM-during-backup run |
| Other limits on the same shutdown (preStop `lifecycle`, cluster-autoscaler 600 s cap, drain timeout) are not mentioned | Substantive | `charts/velero/values.yaml:89` | Say which limit wins, or derive one from the other |
| An upgrade with the README's `--reuse-values` renders a null field and keeps 30 s; no upgrade path was run | Substantive | `charts/velero/README.md:75`, templates | A `--reuse-values` upgrade run from 2.31.8, or explicit handling of a missing key plus an upgrade note |
| The restic daemonset reads the server key, while its sibling settings have `restic.*` keys | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds` |
| "the pod" in the values comment hides that the key also sets the restic pods | Substantive | `charts/velero/values.yaml:89` | Name both workloads, or split the key |
| Nothing stated as run or verified | Substantive | the PR | Post the `helm template`/install runs and the backup test |
| "Optional." next to a 3600 default that is always rendered | Taste | `charts/velero/values.yaml:89` | Drop "Optional" or explain the effect of `null` |
| The chart version bump isn't claimed in the description | Taste | `charts/velero/Chart.yaml:6` | One sentence: "bump chart version per ct lint" |

I didn't install anything on a cluster or run a backup, I didn't read the Velero server source (it isn't in this repository), I didn't run `ct lint`/`ct install`, and I didn't review the prose for style.
