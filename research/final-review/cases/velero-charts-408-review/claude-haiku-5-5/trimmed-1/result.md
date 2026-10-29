## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

**Scope.** Two commits (`e5632c1`, `98041d0`) touching four files: `charts/velero/Chart.yaml`, `values.yaml`, `templates/deployment.yaml`, and `templates/restic-daemonset.yaml`. No code, no tests. The form runs through the §2a analogues. I loaded `english-developer-style`. I did not load `test-authoring` because the change adds no tests. No previous report exists.

**Drift script.** Run; empty output. It parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, so the empty result says nothing about the YAML.

### Item 1: comments consistent with code and each other
The one comment is `values.yaml:89`, "The number of seconds to allow for graceful termination of the pod." It is true of both templates. It does not say that the value also covers the restic daemonset (see T1). Otherwise **none**.

### Item 2: claimed cases covered
Claimed cases: (a) the value can be set through Helm; (b) Velero can finish a backup before termination. Neither has a test or a checked run. (a) and (b) are findings S4 and S3.

### Item 3: boundaries, partitions, control
- The earlier release has no key. A `helm upgrade` from 2.31.8 moves existing pods from 30 s to 3600 s (S1). No test starts from that state.
- `resticTimeout` (`values.yaml:290`, Velero default 1h) is a per-operation limit, so it does not count under the limits paragraph. Its default equals the new 3600 s, and the PR does not say why 3600 was chosen.
- Velero's SIGTERM handling is in a program this repository does not contain. The request is the line that handles it, or a run (S3).

### Item 3a: level, placement, environment
The behaviour can be observed offline with `helm template`; no test exists at any level. Whether the CI lint job renders with a non-default value is **not checked** (see the last section).

### Item 4: names by content
**None.** No ordinals or positional references in the new text.

### Item 5: failure report
**None.** The change adds no assertions.

### Item 6: what the writer says it verified
The PR description and both commits state **no evidence**: no render, no lint, no run. My own checks, which are not the writer's:
- `helm lint charts/velero`: passes.
- `helm template … -f charts/velero/ci/test-values.yaml`: `terminationGracePeriodSeconds: 3600` appears in both the Deployment and the DaemonSet.
- `--set terminationGracePeriodSeconds=120` and `=30`: both values reach both workloads.
- `--set terminationGracePeriodSeconds=null`: renders an empty value, which Kubernetes treats as unset, so the pod silently gets 30 s.

### Item 7: siblings
Pod-bearing templates: `deployment.yaml` and `restic-daemonset.yaml` (both now set), and the `upgrade-crds.yaml` and `cleanup-crds.yaml` Jobs (not set). The Jobs run no backup and the change does not claim them, so they keep the Kubernetes default. **None.**

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| S1. The new default of 3600 s changes behaviour for every existing install on upgrade. The PR names the old 30 s limit but not the new default, and the chart gets only a patch bump (`Chart.yaml:7`). If Velero does not exit on SIGTERM, the old pod keeps running beside the new one for up to an hour. | Substantive | `charts/velero/values.yaml:90` | Default to 30 (opt-in), or name the default change in the PR and bump the chart's minor version. Say why 3600 was chosen. |
| S2. The restic daemonset also gets the value (commit `98041d0`). The PR and the values comment cover only the Velero pod, so restic pods now also wait up to an hour. | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | State the restic change in the PR description. |
| S3. "Lets Velero finish a backup before terminating" has no evidence in the repository: no code path showing that SIGTERM waits for an in-flight backup, and no run. | Substantive | `charts/velero/templates/deployment.yaml:61` | Cite the Velero line that handles SIGTERM, or run a backup, delete the pod with the new value, and confirm the backup completes. |
| S4. The claimed Helm setting has no test or render check. `ci/test-values.yaml` does not set the key. | Substantive | `charts/velero/ci/test-values.yaml` | Set a non-default value in the CI values, or add a render assertion. |
| T1. The comment says "the pod", but the key now drives two workloads. | Taste | `charts/velero/values.yaml:89` | Name both: "the Velero deployment and the restic daemonset." |
| T2. The restic daemonset cannot be tuned separately. Its sibling keys sit under `restic:` (`restic.priorityClassName`, `restic.tolerations`). | Taste | `charts/velero/values.yaml:396` | Add `restic.terminationGracePeriodSeconds` if the two should differ. Otherwise leave it. |
| T3. A `null` value silently falls back to 30 s. | Taste | `deployment.yaml:61`, `restic-daemonset.yaml:56` | Guard with `with`, which also drops a value of 0. Decide which matters more. |

**Not checked:** no cluster, so I did not run Velero or observe its SIGTERM behaviour. I did not run chart-testing or read `.github/workflows/lint-test.yaml`. The drift script does not parse YAML. Prose was checked only for sentences that could be misread, not for style. No files were changed and nothing was committed.
