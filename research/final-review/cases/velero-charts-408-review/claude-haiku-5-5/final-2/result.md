## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

Scope: two commits, four files. `Chart.yaml` bumps the chart to 2.31.9. `values.yaml` adds `terminationGracePeriodSeconds: 3600`. `deployment.yaml` and `restic-daemonset.yaml` each add one line that renders it into the pod spec. No tests, no helper changes, no docs changes.

Loaded: `final-review`, `english-developer-style` and `test-authoring`, all from the skills directory you named. No doc-comment skill applies, because the change has no code comments. The drift script ran and printed nothing. That is expected: it parses code members, and YAML and Helm templates have none. No file was changed and nothing was committed.

Checks run: `helm lint` passes. `helm template` with a provider and `deployRestic=true` renders 3600 in the Deployment and the DaemonSet. Overrides of 7200, 0 and `--set-string 120` render as given. An empty value renders a null field. I extracted the base chart to `.../scratchpad/base` and diffed the renders. The only differences are the chart label bumps and the new line in each pod template.

### Item 1: comments consistent with code and each other
`values.yaml:89-90`: the comment "The number of seconds to allow for graceful termination of the pod. Optional." matches the code. It does not state the default, 3600, or that the same value also applies to the restic DaemonSet. The neighbouring `priorityClassName` comment has the same style, so this is a taste item. No comment narrates the change. Result: none substantive.

### Item 2: claimed cases covered
The claims come from the PR text and the commit messages: the value can be specified; it lets Velero finish a backup before termination; the restic DaemonSet gets it. No test or check in the repo asserts any of them.
- CI (`lint-test.yaml`) runs `ct lint` and `ct install` on kind. `ct install` uses `ci/test-values.yaml`, which sets `deployRestic: true` (line 63). So the default 3600 is accepted by the API on the DaemonSet and the Deployment in CI. No CI case sets a non-default, so the override path is not checked anywhere.
- The "finish a backup before terminating" claim depends on Velero's SIGTERM handling, which lives in the Velero binary, not in this repo. The binary is PID 1 (`command: /velero`), so the signal does reach it. Nothing here shows that an in-flight backup completes within the grace period.

Result: substantive findings S1 and S4 below.

### Item 3: boundaries, partitions, negative control
- Partitions: the value 0 renders `0`; a custom value renders as given; an empty value renders a null field. I did not check the API handling of 0 or null on a cluster.
- Negative control: the default was 30 s before the change. No test or run exercises that case.
- Limits on the same quantity (the outer limit is the pod's grace period):
  - Helm's `--timeout` (5m0s by default, set in the Helm CLI, not in this repo) bounds `helm upgrade --wait`. The upgrade now rolls both pod templates (see S2). If an old pod is mid-backup, the rollout can wait up to 3600 s. The DaemonSet's default rolling strategy is not in the chart's templates, so it is not verified here; I assume the default `RollingUpdate` with `maxUnavailable: 1`. The request is a run of `helm upgrade --wait` with a backup in flight, or the Helm source line that sets the default.
  - Velero's own shutdown behavior is in the Velero binary (not in this repo), and I cannot check it from here. The request is the Velero source line that handles SIGTERM, or a run that reaches it.
- Pre-existing state: the upgrade from 2.31.8 meets existing Deployments and DaemonSets. The render diff shows the pod-template change, so every install rolls its Velero pod and every restic pod on upgrade, even with no value set. No run starts from that state.

Result: substantive findings S2 and S3.

### Item 3a: level and placement
The smallest level that observes the change is a `helm template` render with a non-default value, which needs no cluster. Nothing in the repo runs it. The natural placement is a non-default value in `ci/test-values.yaml`, so that `ct install` exercises the override through the API. Result: part of S1.

### Item 4: names by content
No names or identifiers were added. Result: none.

### Item 5: failure report
No assertions were added. Result: none.

### Item 6: what the writer says it verified
Neither the commit messages nor the change state any verification, and there is no red run because there is no test. I ran `helm lint` and `helm template` myself. That is a consistency check, not the writer's evidence. Result: the writer's verification is not stated.

### Item 7: siblings
- No helper changed.
- Pod-spec sites in the chart: `deployment.yaml` and `restic-daemonset.yaml` (both changed); `upgrade-crds.yaml:18,91` and `cleanup-crds.yaml:20,68` (Jobs with `restartPolicy: OnFailure`). The Jobs run CRD work, not backups, so the defect does not apply to them. They have no grace setting, which is consistent with the PR's scope.
- Restic has its own overrides for other pod settings: `restic.priorityClassName` (`values.yaml:396`), `restic.tolerations` (`:408`), and `restic.lifecycle` (`:446`). The new value is top-level only, so restic pods cannot get a different grace period. This is a taste item (T2).
- The chart README does not list values, so no docs sibling needs an update.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| S1. No test or check covers the value's rendering or override. CI accepts only the default, and only on kind. | substantive | `charts/velero/ci/test-values.yaml` (new value near `:63`); `charts/velero/values.yaml:90` | Set a non-default value in `ci/test-values.yaml` so `ct install` exercises the override. Optionally, add a `helm template` assertion that both workloads carry it. |
| S2. The new default of 3600 changes every install and rolls the Velero pod and every restic pod on upgrade. Neither the PR text nor the comment says so. | substantive | `charts/velero/values.yaml:89-90`; PR description | State the default and its upgrade effect in the PR description, or change the default. |
| S3. Helm's `--timeout` (5m0s) can end `helm upgrade --wait` before a long restic termination finishes. | substantive | `charts/velero/templates/restic-daemonset.yaml:56`; Helm CLI default (not in repo) | Provide a run of `helm upgrade --wait` with a backup in flight, or the Helm source line for the default. Or document the `--timeout` needed. |
| S4. The stated purpose, finishing an in-flight backup on SIGTERM, has no evidence in the repo. | substantive | `charts/velero/templates/deployment.yaml:61`; Velero binary (not in repo) | Provide the Velero source line that handles SIGTERM, or a run where a backup started before the signal completes. |
| T1. The comment does not state the default or that restic shares the value. | taste | `charts/velero/values.yaml:89` | Add the default and the restic scope, for example "Defaults to 3600. Also applies to the restic daemonset." |
| T2. The value is top-level only. Restic cannot get its own grace period, unlike `priorityClassName`, `tolerations` and `lifecycle`. | taste | `charts/velero/values.yaml:396,408,446`; `restic-daemonset.yaml:56` | Add `restic.terminationGracePeriodSeconds`, falling back to the top-level value, or name the single shared value in the PR. |

No churn items were reported.

Not checked: the PR description and commit-message wording (outside this form, and the developer-style pass was not run); the Velero binary's SIGTERM behavior; Kubernetes API handling of 0 and null on a real cluster; any run on a cluster, which this environment does not have.
