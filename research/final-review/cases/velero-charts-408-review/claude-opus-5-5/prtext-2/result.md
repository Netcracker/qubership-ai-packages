# Final review: `bd5bf86..HEAD` ([velero] Add Termination Grace Period Helm Value)

The change has five substantive findings and one taste finding. The two that matter most: it raises the grace period for every user from 30 s to one hour without saying so, and it uses one key for both the Velero deployment and the restic daemonset.

Inputs: I read the diff of both commits in full. The task statement is the pull request description you quoted, and I read both commit messages. I could not read the live pull request (no `gh`), so item 2 uses the quoted text. The drift script printed nothing, because it does not parse Helm templates or YAML. I checked the one changed comment (`values.yaml:89`) by hand. I ran `helm lint` (it passes) and `helm template` with `ci/test-values.yaml`, `deployRestic=true`, and the values listed under item 3. I changed no files.

Skills loaded: `english-developer-style` (§4 and §4a) and `test-authoring` (§3 and §4). Helm has no doc-comment skill, so I checked the values comments against the style skill.

## Item 1: comments consistent with the code and with each other

**Finding 1 (substantive), `charts/velero/values.yaml:89`.**
- The comment says "of the pod", but the value now applies to two kinds of pod: the Velero server deployment (`deployment.yaml:61`) and the restic daemonset (`restic-daemonset.yaml:56`).
- Every neighboring top-level key reads "for the Velero deployment", and the restic daemonset has its own `restic:` block. A reader will conclude this key only affects the server.
- **Request:** split the key, as item 3 asks. If it stays shared, the comment should say "of the Velero server pod and the restic daemonset pods".

No term is coined: "graceful termination" is the Kubernetes word. The comment does not narrate the change.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| A user can set the grace period on the Velero pod (PR description, commit `e5632c1`) | No test. `ci/test-values.yaml` does not set the key, so `ct install` only runs the default. I checked it by hand with `helm template`. |
| A user can set the grace period on the restic daemonset (commit `98041d0`) | No test (same as above). |
| The design reason: Velero finishes a backup before it terminates | No test, and no evidence that Velero v1.9 waits for an in-progress backup after SIGTERM. Item 3 has the request. |

**Finding 2 (substantive), the claims read the other way, `values.yaml:90`.**
- The default is `3600`. Before this change the field was not rendered, so Kubernetes used 30 s.
- Upgrading from 2.31.8 to 2.31.9 therefore raises every user's grace period, for both pod types, from 30 s to one hour.
- Neither the description nor the commit messages say so. The description calls 30 s the previous value and says only that the setting becomes specifiable.
- **Request:** either default to `30`, so that the bump is a no-op, or add a sentence to the description, and a line under *Upgrading* in the README, that claims the new one-hour default.

**Finding 3 (substantive), the description.**
- Its title and body say "Velero" and "allow Velero to finish a backup". The restic daemonset hunk is claimed only by commit `98041d0`.
- **Request:** a sentence in the description that names the restic daemonset, or the split from Finding 4.

The `Chart.yaml` version bump is the release output chart-testing requires, so it is claimed with the change.

## Item 3: boundaries, partitions, and the negative control

**Finding 4 (substantive), a value now reaches a consumer it was not meant for.**
- The new top-level key sits among the Velero-deployment keys, but the restic daemonset also reads it.
- A user who raises it so that a long server backup can finish also gives every restic pod a one-hour grace period. That pod has a different shutdown profile.
- The chart's existing pattern gives restic its own key: `restic.priorityClassName`, `restic.tolerations`, `restic.lifecycle`.
- **Request:** add `restic.terminationGracePeriodSeconds` and have `restic-daemonset.yaml:56` read it.

**Finding 5 (substantive), the change exposes a limit while others still bound the same work.**
- **Velero's own shutdown path** (the velero server binary, which is not in this repository). The grace period only helps if the server keeps the backup running after SIGTERM. If it cancels its context and exits, the value has no effect.
- **Cluster autoscaler scale-down.** Its `--max-graceful-termination-sec` defaults to 600, which caps any value above that.
- **Node-level and drain limits.** The kubelet's `shutdownGracePeriod` and `kubectl drain --timeout` also cap it.
- **The `lifecycle` preStop hook.** It runs inside this same budget.
- **Request:** the line in Velero v1.9 that waits for an in-progress backup on SIGTERM, or a run that shows a backup completing after SIGTERM. Also a sentence in the `values.yaml` comment naming the autoscaler cap.

**Pre-existing state.** An existing install has no such key and was getting 30 s. Finding 2 already covers what an upgrade does to it.

**Boundaries.** I rendered these with `helm template`:

| Value | Rendered as |
| --- | --- |
| default | `3600` in both templates |
| `--set ...=60` | `60` |
| `null` or empty | `terminationGracePeriodSeconds:` with no value, so the API server falls back to 30 |
| `10000000`, given in a values file | `1e+07` |

**Finding 6 (taste), `deployment.yaml:61` and `restic-daemonset.yaml:56`.** The `1e+07` rendering happens because Helm reads YAML numbers as float64, and the API server would reject that for an int64 field. It only starts at 1,000,000 s, so it is unlikely to bite. Piping through `int` (`{{ .Values.terminationGracePeriodSeconds | int }}`) or wrapping the line in `{{- if }}` would remove it.

## Item 3a: level, placement, and the environment

None. The repository has no template unit-test framework. Rendering with `helm template` is the smallest level that can see the change, and `ct lint`/`ct install` in `lint-test.yaml` is the existing gate. `helm lint` passes locally. I could not run `ct` because it is not installed.

## Item 4: names by content, not by position

None. The key and the comment refer to nothing by position.

## Item 5: the failure report

None. The change adds no assertions.

## Item 6: what the writer says it verified

Nothing is stated: there is no rendered output, no run, and no evidence that a backup survives SIGTERM.

## Item 7: siblings of the change

- Templates with pod specs: `deployment.yaml`, `restic-daemonset.yaml`, `upgrade-crds.yaml`, `cleanup-crds.yaml`. The two CRD files are short-lived hook Jobs that are not touched during a backup, so the defect does not apply to them.
- Places that list the chart's keys: `values.yaml` only. The README has no values table, and `ci/test-values.yaml` lists only some keys.
- The restic sibling key is filed as Finding 4.

## Findings index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| 1. The comment says "the pod", but the key also sets the restic daemonset's grace period | Substantive | `charts/velero/values.yaml:89` | 1 |
| 2. The default raises every user's grace period from 30 s to 3600 s, and nothing claims it | Substantive | `charts/velero/values.yaml:90` | 2 |
| 3. The description does not claim the restic daemonset hunk | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 2 |
| 4. The restic daemonset reads the Velero deployment's key instead of a `restic.*` key | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 3 |
| 5. No evidence Velero waits on SIGTERM; the cluster autoscaler (600 s), kubelet, and drain limits can cap the value | Substantive | `charts/velero/templates/deployment.yaml:61` | 3 |
| 6. Values of 1,000,000 or more from a values file render as `1e+06` and up | Taste | `charts/velero/templates/deployment.yaml:61` | 3 |

The drift script does not parse Helm or YAML, the open pull request could not be read without `gh`, and `ct` was not available locally.
