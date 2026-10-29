## Final review: `bd5bf865..HEAD` (Helm: termination grace period value)

Scope: two commits, `e5632c1` and `98041d0`. Four files: `Chart.yaml` (version 2.31.8 → 2.31.9), `values.yaml`, `templates/deployment.yaml`, and `templates/restic-daemonset.yaml`. No previous report exists for this change. The drift script printed nothing, which is expected: it parses only Java, Kotlin, Groovy, and Scala, and this change has none. Per §2a, the analogues below replace the code items. I loaded `test-authoring` (§3's "change in a configuration default" row) and `english-developer-style`. The doc-comment skill does not apply, since there is no Java or similar doc comment.

Checks I ran (nothing was changed or committed): `helm lint charts/velero` passes. `helm template` with a full set of required values renders `terminationGracePeriodSeconds: 3600` on the Deployment (`deployment.yaml:61`) and on the restic DaemonSet. With `=30` it renders 30. With `=null` it renders an empty value. With `=""` it renders `terminationGracePeriodSeconds: ""`.

### Item 1: comments consistent with the code and with each other
Finding (S1 below). The `values.yaml:89` comment's first sentence states what the key does, and it stands alone. But it ends in "Optional.", and the key always renders a value (3600). A reader would take omitting it to mean the Kubernetes default of 30 seconds. No other comment in the file or sibling comments are affected. No narration words.

### Item 2: claimed cases covered
- Claim: the Helm value sets the Velero pod's termination grace period (PR). Checked by render, but no test exists. Finding S4.
- Claim: the restic DaemonSet gets the same value (commit `98041d0`). Checked by render. Not in the PR description, which says only "Velero". Finding S1.
- Claim: Velero can finish a backup longer than 30 seconds before terminating (PR). Depends on Velero's SIGTERM behavior, which I cannot check offline. See S3.

### Item 3: boundaries, partitions, negative control
- Partitions not tested: unset (renders 3600), `0`, a positive integer, `null`, and `""`. The empty string renders `terminationGracePeriodSeconds: ""` on the Deployment and is an invalid int field. Finding S2. `null` silently falls back to 30 seconds. Also a finding in S2.
- Pre-existing state: an existing install upgraded to this chart rolls every Velero pod and restic pod to 3600 seconds, with no opt-in. Finding S1.
- Limits on the same quantity: `resticTimeout` (`values.yaml:289–290`, documented default 1h, passed as `--restic-timeout` at `deployment.yaml:83–84`) equals the new default of 3600. Finding S3.

### Item 3a: level, placement, environment
No test exists at any level. The smallest observable level is a render check (`helm template`), which runs offline. The CI gates are `ct lint` and `ct install` on kind. `ct install` does not assert the field, and `charts/velero/ci/test-values.yaml` does not set it. Finding S4.

### Item 4: names by content
none. Checked the three new lines, the comment, and the chart version.

### Item 5: failure report
none. The change adds no assertion. Chart-level analogue: the render output is the only observable, and no test checks it.

### Item 6: what the writer says it verified
The change and both commit messages state no evidence: no render check, no run, no red-run analogue. My renders above are the reviewer's checks, not the writer's evidence.

### Item 7: siblings
- No helper changed.
- `priorityClassName` is the sibling pattern. The deployment guards it with `{{- if }}` (`deployment.yaml:58`), and the restic DaemonSet does the same with `restic.priorityClassName` (`restic-daemonset.yaml:53`). The new key is unguarded in both places, so the S2 defect applies to the sibling pattern's convention. Finding S2.
- Chart Jobs `upgrade-crds.yaml` and `cleanup-crds.yaml` also have pod templates. Checked: the PR's use case concerns the long-running Velero server, and these are one-shot CRD jobs, so the defect does not apply and I did not raise them.
- `schedule.yaml` is a Schedule resource, not a pod, so it does not apply.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| S1 | The default of 3600 changes termination for every existing install, and for restic pods too. The PR description states neither, and the "Optional." comment hides it. | substantive | `charts/velero/values.yaml:89–90`; PR description | Either keep the Kubernetes default of 30 when unset, or state the default change, the restic effect, and the 30-second Kubernetes default in the comment and the PR description. |
| S2 | `terminationGracePeriodSeconds: ""` renders an invalid int and the API server rejects it. The chart's own convention for an unset optional value (`priorityClassName: ""`) produces exactly this. `null` silently means 30 seconds. | substantive | `charts/velero/templates/deployment.yaml:61`, `charts/velero/templates/restic-daemonset.yaml:56` (sibling guard at `deployment.yaml:58`) | Guard the render the way `priorityClassName` is guarded, and keep `0` valid, since a guard on truthiness would drop it. |
| S3 | `resticTimeout` (default 1h) equals the new default of 3600 seconds. If a restic backup can outlive the grace period, the grace period is the outer limit and `resticTimeout` the inner. At the defaults the inner limit does not reliably fire first, and raising the grace period past 1h has no effect on a restic backup that `resticTimeout` cuts off. This is conditional on Velero waiting for in-flight work on SIGTERM, which the PR assumes and which I cannot verify offline. | substantive (conditional) | `charts/velero/values.yaml:289–290`, `charts/velero/templates/deployment.yaml:83–84` | Document the pair in the comment, or derive one limit from the other. |
| S4 | No test or CI check shows that the override reaches the rendered pod spec. The `ct install` job does not assert the field. | substantive | `charts/velero/ci/test-values.yaml`, `.github/workflows/lint-test.yaml` | Set a non-default value in `ci/test-values.yaml`, plus a render assertion on both pod specs, or name a render check as the test. |
| T1 | The restic DaemonSet shares the global key, while the chart gives restic-specific settings a `restic.*` key (`restic.priorityClassName`). | taste (the reviewer prefers a `restic.` key; expect it to be declined) | `charts/velero/templates/restic-daemonset.yaml:56` | Either add `restic.terminationGracePeriodSeconds`, or state in the values comment that the global key also applies to restic. |

### Not checked
- Velero's own SIGTERM behavior (the basis of S3 and the PR's use case) could not be checked: no Velero source and no network.
- The CI `ct install` on kind was not run: no cluster.
- Applying the rendered manifests to a cluster was not done. S2's rejection by the API server is from the int field type, not from a live apply.
- The drift script was not applicable (no Java, Kotlin, Groovy, or Scala).
- The English wording was checked only where it could change what a sentence means. Style alone was not reviewed, as §the closing sentence of the form requires.
