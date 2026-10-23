# Final review: `bd5bf865..HEAD`, termination grace period Helm value

**Scope:** 2 commits, 4 files: `charts/velero/Chart.yaml`, `templates/deployment.yaml`, `templates/restic-daemonset.yaml`, `values.yaml`. No code and no tests, so each item uses the §2a analogue. The drift script ran (exit 0) and printed nothing, because the diff has no members to parse. This is the first review, so there is no previous report.

**Checks I ran:** `helm lint charts/velero` passes with 0 failures. `helm template` with `configuration.provider=aws` (the Deployment does not render without it):
- The default renders `terminationGracePeriodSeconds: 3600` in the Deployment and, with `deployRestic=true`, in the restic DaemonSet.
- `terminationGracePeriodSeconds=120` renders `120` in the Deployment.
- An empty string or a null value renders `terminationGracePeriodSeconds: ` with no number, and helm exits 0.

### Item 1: comments consistent with the code and each other
Finding 2. The comment at `values.yaml:89` says "of the pod", which reads as the Velero pod. The same key also sets the restic DaemonSet pod (`restic-daemonset.yaml:56`). The sibling comments name their workload: `values.yaml:86` says "for the Velero deployment", and `values.yaml:395` says "for the Restic daemonset".

### Item 2: claimed cases covered
The claimed cases are that a user can set the value through Helm, that it applies to the Velero pod, and that it applies to the restic DaemonSet (commit `98041d0`). None has a test or a render check in the repository. `ci/test-values.yaml` does not set the key, and `ct.yaml` runs chart-testing lint, which does not assert rendered fields. Finding 3.

### Item 3: boundaries, partitions, and the negative control
The partitions are unset (the 3600 default), a set value, and empty or null. None is tested, and the old 30 s behavior is not present as a control. The pre-existing state is an installed Deployment with no such field (the Kubernetes default of 30 s), and a `helm upgrade` moves it to 3600 s. No run starts from that state. Finding 1.

Other limits on the same work: the chart sets no `activeDeadlineSeconds` and no preStop hook. A hook from the `lifecycle` value would run inside the same period, not as a separate limit. Velero's own shutdown behavior is in a program this repository does not contain (finding 4).

### Item 3a: level, placement, and the environment
The behavior is observable with no cluster, as a rendered manifest. §3's configuration-default row asks for a small check through the value and a larger check where the default is read at deployment. Neither exists. Finding 3.

### Item 4: names by content
none. The diff has no names, ordinals, or positional references.

### Item 5: the failure report
none. The change has no assertions.

### Item 6: what the writer says it verified
Neither a red run, a mutation verdict, nor a render check is stated in the commits or the PR text. The `helm template` runs above are my own checks, not the writer's evidence.

### Item 7: siblings
The chart has four pod templates. `deployment.yaml:62` and `restic-daemonset.yaml:74` are covered by the change. `upgrade-crds.yaml:64` and `cleanup-crds.yaml:40` are Jobs that run no backup, so the defect does not apply to them. The new line sits where `priorityClassName` sits in both covered templates. The `Chart.yaml` bump from 2.31.8 to 2.31.9 matches commit `56d5a0d`, which also bumped the chart version when it added a value. `charts/velero/README.md` has no values table to update.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | The default changes for every install and for restic, and the PR text and commit message do not say so. Upgrades move the Deployment and the DaemonSet from 30 s to 3600 s, so a pod that ignores SIGTERM now waits up to an hour. | substantive | `values.yaml:90`, `restic-daemonset.yaml:56` | Name the default change, and its effect on upgrades, in the PR and the commit. Either keep 3600 and justify it in the comment, or make the default 30 so the upgrade path is unchanged. |
| 2 | The comment "of the pod" misstates the scope, because the value also applies to the restic pods. | substantive | `values.yaml:89-90` | Name both workloads in the comment. The sibling pattern (`restic.priorityClassName`, `restic.tolerations`) suggests a `restic.` key as the cleaner design, which is the reviewer's preference. |
| 3 | The claimed setting and the default have no check in the repository, and the PR does not state the manual render as its evidence. | substantive | `ci/test-values.yaml`; `deployment.yaml:61`; `restic-daemonset.yaml:56` | Add a render check that sets a non-default number and asserts the field in both workloads, or state in the PR that the only evidence is a manual `helm template`. |
| 4 | The PR's purpose rests on Velero finishing a backup when it receives SIGTERM. Nothing in this change or repository shows that. | substantive (unverified here) | PR description; `deployment.yaml:61` | Cite the Velero line that waits for in-flight backups on SIGTERM, or show a run where a backup longer than 30 s completes within the new grace period. |
| 5 | The new line is not guarded like its sibling. An empty or null value renders a null field. | taste | `deployment.yaml:61` (sibling guard at `deployment.yaml:58`) | Wrap the line in `{{- if .Values.terminationGracePeriodSeconds }}`. Two readings are right here, and the reviewer prefers the guard. Expect it to be declined without discussion. |
| 6 | The PR calls the old 30 s value "immutable", which can read as a Kubernetes constraint rather than an unset chart value. | taste | PR description (not in the diff) | Replace "immutable" with wording such as "not configurable through the chart". |

**Not checked:** the wording pass of `english-developer-style` was not done beyond the commit subjects, and both use the gerund "adding" where that skill asks for an imperative subject, which is noted as wording outside this form. No cluster, upgrade, or Velero source was available, so finding 4 is unverified.
