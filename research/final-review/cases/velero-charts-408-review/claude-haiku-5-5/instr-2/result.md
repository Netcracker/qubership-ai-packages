## Final review: `bd5bf865..HEAD` (Termination Grace Period Helm value)

Two commits, four files: `charts/velero/values.yaml`, `templates/deployment.yaml`, `templates/restic-daemonset.yaml`, and `Chart.yaml`. There is no previous report for this change, so the review opens with the item sections.

**Drift script:** Run as `comment-drift.py bd5bf865 HEAD`. It printed nothing and exited 0, because the chart is YAML with no code members. Items 1 and 3 therefore apply directly to the new values comment and to the template lines.

**Checks I ran myself:** `helm template` with `configuration.provider=aws` and `deployRestic=true`, plus `helm lint`. These are my runs, not evidence the writer stated.
- Default: `terminationGracePeriodSeconds: 3600` in the DaemonSet (rendered line 143) and the Deployment (line 228).
- Override to `60`: reaches both.
- Override to `null`: renders blank, which YAML reads as unset.
- `helm lint`: 0 charts failed.

### Item 1: comments consistent with the code and with each other
Analogue: no code members, so the check runs on the new comment in `values.yaml` and on the templates.
- `values.yaml:89` says "The number of seconds to allow for graceful termination of the pod." That is true, but it does not say which pods. The same key also drives the restic DaemonSet, and the sibling comment on line 86 says "for the Velero deployment." See finding 3.
- No comment narrates the change.
- Nothing else in the change makes a statement about another file.

### Item 2: claimed cases covered
- **Claimed cases:** (a) the value can be set, and (b) it reaches the pod that finishes the backup. No test or run in the change covers either. See finding 7.
- **Commands in changed files:** none.
- **Hunks against claims:** the deployment hunk (`deployment.yaml:61`) is claimed by `e5632c1`. The restic hunk (`restic-daemonset.yaml:56`) is claimed by `98041d0`. The `Chart.yaml:7` version bump (2.31.8 to 2.31.9) is claimed by no sentence. See finding 5.

### Item 3: boundaries, partitions, and the negative control
- **Upgrade state:** the default changes behavior for every existing install. Pod template changes make `helm upgrade` roll out both workloads with a grace period of 3600 s, instead of the Kubernetes default of 30 s. The description says nothing about this. See finding 1.
- **Other limits on the same work:** the Velero server flag `--restic-timeout` is documented in `values.yaml:289-290`, with a default of 1h. At the new default, the grace period and the restic timeout are both 3600 s, so neither fires first. Raising `resticTimeout` past 1h gives the grace period no protection. See finding 2.
- **Empty value:** `null` renders `terminationGracePeriodSeconds: ` with no value, so the setting is silently dropped and the pod gets the 30 s default. The `priorityClassName` lines use an `if` guard, and this one does not. See finding 6.
- **Negative control:** the override to `60` shows the value follows the setting, so the control arm is present in my run only.

### Item 3a: level, placement, and the environment
- The smallest level that can observe the rendered field is `helm template`. The repo has no chart unit test for it, and the CI workflow (`lint-test.yaml`) runs chart-testing lint and a kind install, neither of which asserts this field. See finding 7.
- Placement follows the `priorityClassName` pattern for the Deployment. For the DaemonSet, the key is top-level, not under `restic.` as its siblings are. See finding 4.

### Item 4: names by content, not by position
none. No test names, case ids, or messages were added. The comment and key name the thing directly.

### Item 5: the failure report
none. No assertions were added.

### Item 6: what the writer says it verified
Neither the description nor the commit messages state a red run, a render, or any other check. The writer's evidence is absent. See finding 7.

### Item 7: siblings of the change
- **Values table:** `charts/velero/README.md` has no table of values, so there is no list of keys to update. `ci/test-values.yaml` is the only other values file and needs no change for this key.
- **Restic siblings:** the DaemonSet's siblings (`restic.priorityClassName`, `restic.tolerations`, and so on) live under `restic.`. The new key does not, so a user cannot set a different grace period for restic pods. See finding 4.
- **Upgrade notes:** the README's "Upgrading to v1.9" section lists per-version notes. No note covers the new default. See finding 1.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. The default of 3600 changes behavior for every install on upgrade, and the description does not say so. Pods that were on 30 s are rolled onto 3600 s by `helm upgrade`, with no opt-in. | Substantive | `charts/velero/values.yaml:90` | Add a sentence to the description stating that the default changes for existing installs. Add the same note to the upgrade section of the README. Or set the default to `30`, which keeps the old behavior and makes users opt in. |
| 2. The grace period and `resticTimeout` (the documented server flag, default 1h) are not derived from each other. At defaults both are 3600 s, so neither fires first, and raising `resticTimeout` past 1h has no protection from the grace period. | Substantive | `charts/velero/values.yaml:90` and `:289-290` | State the relation in one sentence: either the grace period must be at least `resticTimeout`, or the two are independent and the reason is given. The comment on the grace period should name the restic timeout it has to exceed. |
| 3. The comment says "the pod", but the key sets the grace period for the restic DaemonSet pods too. The sibling comment on line 86 names the deployment. | Substantive | `charts/velero/values.yaml:89` | Change the comment to name both: "for the Velero deployment and the restic DaemonSet pods." |
| 4. The DaemonSet reads a top-level key, while the restic siblings are under `restic.`. Users cannot set a restic-only grace period. | Taste | `charts/velero/templates/restic-daemonset.yaml:56` | Read `.Values.restic.terminationGracePeriodSeconds` with a fallback to the top-level key, if separate control is wanted. I expect this to be declined, since the PR asks for one value. |
| 5. The `Chart.yaml` version bump is not claimed by the description or any commit message. The bump matches the repo's usual practice for chart changes. | Substantive | `charts/velero/Chart.yaml:7` | Add a sentence to the description that names the bump, or move it to a separate commit. |
| 6. An empty value renders a blank field, which Kubernetes reads as unset. The user gets the 30 s default with no message. | Taste | `charts/velero/templates/deployment.yaml:61` and `restic-daemonset.yaml:56` | Guard the field with `{{- if .Values.terminationGracePeriodSeconds }}`, as `priorityClassName` does. |
| 7. The claimed behavior (the field reaches the pod, and the backup gets the time) has no test and no stated render. The CI workflow does not assert the field. | Substantive | `.github/workflows/lint-test.yaml`; description | Paste the `helm template` output for the default and for an override into the description, or add an assertion to the CI check. |

Not reviewed: no cluster or kind run, no CI job, and no chart-testing run. Whether Velero finishes a backup within 3600 s was not checked. The English wording was checked only where it could mislead, so this is not a style pass.
