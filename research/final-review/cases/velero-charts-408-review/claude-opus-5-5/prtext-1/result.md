# Final review: `bd5bf86..HEAD` ("[velero] Add Termination Grace Period Helm Value")

This is a configuration change: a Helm values key and two template lines. I filled the form with the analogues from §2a; item 3 applies as written for a configuration. The drift script ran (exit 0) and printed nothing, because it does not parse YAML or Helm templates. I loaded `test-authoring` and `english-developer-style`. No doc-comment skill applies, and `apm-authoring` covers only skills and instruction files, so I didn't load it. There is no previous report. I couldn't read the pull request on the platform (gh was not allowed), so its title and description are the text you quoted.

## Item 1: comments consistent with the code and with each other

Analogue: the one added comment, `charts/velero/values.yaml:89`, checked against the two templates that read the key.

**Finding (substantive).** The comment is `# The number of seconds to allow for graceful termination of the pod. Optional.` A reader would get two things wrong:
- **Which pods.** "The pod" sits among neighbors that all say "for the Velero deployment" (`values.yaml:86`, `:92`). But `restic-daemonset.yaml:56` reads the same key, so the value also sets the grace period of every restic pod. The comment doesn't say so.
- **What "Optional" means.** It suggests that leaving the key alone gives the Kubernetes default. In fact the chart now sets 3600. To get the Kubernetes default of 30 you have to set the key to `null`; I checked that this renders `terminationGracePeriodSeconds:` with no value.

Request: `# Grace period, in seconds, for the pods of the Velero deployment and the restic DaemonSet. The chart sets 3600; set null to use the Kubernetes default of 30.` (Change the first part if item 7's separate key is adopted.) The change coins no terms.

## Item 2: claimed cases covered

| Claimed case | Source | Evidence |
| --- | --- | --- |
| The grace period can be set through a Helm value | PR title and description, `e5632c1` | Only the default goes through CI: `ct install` renders `ci/test-values.yaml`, which leaves the value at 3600. I ran `helm template --set terminationGracePeriodSeconds=60`, and it rendered `60` in the Deployment and the DaemonSet. No test or CI run sets a value other than the default. |
| The restic DaemonSet gets the value | `98041d0` | `ci/test-values.yaml` doesn't set `deployRestic`, so CI never renders the DaemonSet. I rendered it locally with `--set deployRestic=true`. |
| The design reason: "allow Velero to finish a backup before terminating" | PR description | **None.** |
| Chart version 2.31.8 → 2.31.9 | Required by `ct lint` (version-increment check, `ct.yaml`) | Comes with the claimed change, so no finding. |

**Finding (substantive): the stated reason has no evidence.** A longer grace period only helps if the server keeps a running backup going after SIGTERM. That is behavior of `velero server` v1.9.2, which this repository doesn't contain. If the server stops its controllers and exits as soon as it gets SIGTERM, the backup is lost exactly as before, and 3600 changes nothing.

There's also a consequence to rule out. The Deployment has no `strategy` block, so it uses RollingUpdate with a surge of 1. If the old pod does keep running, the new and old Velero servers run side by side for up to an hour.

Request: a run on v1.9.2 that sends SIGTERM to the server pod in the middle of a backup and reports the backup's final phase. Or cite the server code that keeps the backup running after SIGTERM.

**Finding (substantive): the default changes for every existing install, and nothing says so.** The description says the change "adds in the ability to specify" the grace period. In fact every upgrade moves both the Velero pod and the restic pods from 30 s to 3600 s, whether or not the user sets anything. A server or a `lifecycle.preStop` hook that hangs on shutdown now holds a rollout or a node shutdown for up to an hour, not 30 s.

Request: one of these:
- a default that keeps the old behavior: `null`, or the field left out when the key is unset, as `priorityClassName` does at `deployment.yaml:58`;
- or a sentence in the description that claims the new 3600 default and gives the reason for it.

## Item 3: boundaries, partitions, and the negative control

What I rendered with `helm template -f ci/test-values.yaml --set deployRestic=true`:

| Value | Renders as | Result |
| --- | --- | --- |
| default | `3600` | fine |
| `60` | `60` | fine |
| `null` | an empty value | Kubernetes uses its default of 30 |
| `""` (via `--set-string`) | an empty value | Kubernetes uses its default of 30 |
| `-1` | `-1` | the chart passes it through; whether the API server rejects it is the API server's decision |
| `1000000` via `--set` | `1000000` | fine |
| `1000000` from a values file | **`1e+06`** | not an integer, so the int64 field is unlikely to accept it |

**Finding (substantive, but rarely reached).** Values of a million seconds (about 11.6 days) or more, given in a values file, render in scientific notation. Request: `{{ .Values.terminationGracePeriodSeconds | int64 }}` inside a `with` or `if` guard, so that `null` still leaves the field out.

**Starting state.** The new field is a plain pod-spec field and persists nothing. `ct install` runs with `upgrade: true`, so CI does cover an upgrade from the earlier chart, for the Deployment.

**One key, two consumers.** The new key reaches both the Deployment and the restic DaemonSet. A value someone picks for the server's backups also governs the restic pods. Filed under item 7.

**Finding (substantive): other limits on the same work aren't named.** These limits also bound the termination this value controls:
- **resticTimeout:** the server default is 1h (`values.yaml:289`). It limits each restic backup, which is the work being protected, and it equals the new default of 3600.
- **preStop hook:** the `lifecycle` value (`values.yaml:84`) adds a hook whose run time comes out of the same grace period.
- **Outside the chart:**
  - When cluster-autoscaler scales a node down, its `--max-graceful-termination-sec` (600 by default) caps the grace period, so raising the value above 600 does nothing there.
  - kubelet's graceful node shutdown (`shutdownGracePeriod`) also limits how long the pods get.
  - `kubectl drain --timeout` limits the whole drain.

Request: a sentence in the values comment naming the environment limits that cap this value, especially the cluster-autoscaler one. Or a run showing that a value above those caps takes effect.

## Item 3a: level, placement, and the environment

Analogue: where the setting lives, and the repository's own check. The repository has no template unit tests; its check is `ct lint` and `ct install` in `.github/workflows/lint-test.yaml`. Both template lines sit beside the neighboring pod-spec fields (`priorityClassName`), which is consistent placement. `helm lint` passes with and without `ci/test-values.yaml`. The gap is that `ci/test-values.yaml` doesn't enable `deployRestic`, so CI never renders the DaemonSet half of the change. That is already in item 2's table, so there's no separate finding here.

## Item 4: names by content, not by position

None. I checked the key name, the comment, and both commit messages; none of them refers to anything by position.

## Item 5: the failure report

None. The change adds no assertions or checks. Its only failure signal is `helm lint`/`ct`, which this change doesn't alter.

## Item 6: what the writer says it verified

Neither the commits nor the description state any evidence: no render with a non-default value, and no run of a backup across a pod termination. The writer hasn't shown that the setting changes the outcome it was added for.

## Item 7: siblings of the change

**Finding (substantive).** Every other pod-level setting of the restic DaemonSet has its own key under `restic:`, for example `restic.priorityClassName` (`values.yaml:395`) and `restic.lifecycle` (`:445`). The new setting has no `restic.` sibling; the DaemonSet reads the Deployment's top-level key at `restic-daemonset.yaml:56`. The same mix-up already exists before this change at `restic-daemonset.yaml:165`, which checks `.Values.lifecycle` but renders `.Values.restic.lifecycle`.

Request: add `restic.terminationGracePeriodSeconds` and read it at `restic-daemonset.yaml:56`. Fix line 165 here or name it as follow-up in the description.

`charts/velero/README.md` has no values table, so no other list of values needs the new key.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The comment says "the pod" and "Optional", but the key also governs restic pods and defaults to 3600, not 30 | Substantive | `charts/velero/values.yaml:89` | 1 |
| No evidence that Velero v1.9.2 keeps a running backup going after SIGTERM | Substantive | `charts/velero/templates/deployment.yaml:61` | 2 |
| The default moves from 30 s to 3600 s for every install; the description doesn't claim it | Substantive | `charts/velero/values.yaml:90` | 2 |
| Values ≥ 1,000,000 in a values file render as `1e+06` | Substantive | `charts/velero/templates/deployment.yaml:61`, `restic-daemonset.yaml:56` | 3 |
| Other limits (resticTimeout, the preStop hook, the cluster-autoscaler 600 s cap, node shutdown, drain timeout) aren't named | Substantive | `charts/velero/values.yaml:89` | 3 |
| The DaemonSet reads the Deployment's top-level key instead of a `restic.` key; same mix-up at line 165 | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 7 |

I couldn't do two checks: the drift script doesn't parse YAML or Helm templates, and Velero's SIGTERM handling is outside this repository, so I couldn't confirm it here.
