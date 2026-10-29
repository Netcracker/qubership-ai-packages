## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

**Scope and analogues.** The change has no code and no tests. It touches `Chart.yaml`, `values.yaml`, `templates/deployment.yaml` and `templates/restic-daemonset.yaml`. Per §2a, I applied each item to the chart analogue (values comments, rendered output, CI values). I loaded `english-developer-style` for the wording. I did not load `test-authoring`, because the change adds no tests. The drift script was run and printed nothing. It parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala`, so no YAML member was parsed. I ran `helm lint charts/velero` (0 failed), and `helm template` with the default value, with `deployRestic=true` and `terminationGracePeriodSeconds=45`, and with the value set empty. There was no previous report, so there is no reshaped/holds table.

### Item 1: comments consistent with the code and with each other
Finding 1 below (`values.yaml:89`). The line `# The number of seconds to allow for graceful termination of the pod. Optional.` is wrong about "Optional". The template always renders the key, and the chart default of 3600 applies unless the user overrides it. Leaving the key unset does not give the pod default. Nothing else in the file or the other comments contradicts it. No comment narrates the change.

### Item 2: claimed cases covered
The claimed cases are: (a) the grace period is settable through the chart, (b) it applies to the Velero pod, (c) Velero can finish a backup before termination. Case (a) has no test. `charts/velero/ci/test-values.yaml` does not set the key, so CI renders only the 3600 default. Case (b) is confirmed by my render (`deployment` at 228 and `DaemonSet` at 143 with 45). Case (c) has no evidence in the change. See finding 3.

### Item 3: boundaries, partitions, and the negative control
Finding 2 below: the empty value is not partitioned. The unguarded render produces `terminationGracePeriodSeconds: ` (null), and the API then treats it as unset, which is the 30 s Kubernetes default. Nothing says so. The change's own default (3600) is the control, and it is present in CI.

**Limits on the same work (item 3 limit paragraph).** The chart sets no other limit on this path: no `activeDeadlineSeconds`, and no `preStop` default. The one that matters is whether the Velero server and the restic node-agent wait for in-flight work on SIGTERM. That behavior lives in the Velero binary, which this repo does not contain. Finding 3 names the run that would settle it.

### Item 3a: level, placement, and the environment
No unit-level test exists for chart values. The only in-repo check is the chart-testing install, which uses `charts/velero/ci/test-values.yaml`, and that file does not set the key. The placement follows the sibling `priorityClassName` pattern in `deployment.yaml` and `restic-daemonset.yaml`. No test is added in a new place, so no fixture is copied.

### Item 4: names by content, not by position
none. The only new names are `terminationGracePeriodSeconds` and the existing keys, and the comment uses no ordinals.

### Item 5: the failure report
none. The change has no assertions. The `helm template` output reads as expected.

### Item 6: what the writer says it verified
None stated. The change, its commit messages and the task statement give no red run, no render check, and no `helm lint` result. The PR description claims behavior (Velero finishes a backup) that nothing in the change verifies. I ran `helm lint` and `helm template` myself as checks. They are consistency evidence, not proof that a backup completes.

### Item 7: siblings of the change
- `upgrade-crds.yaml` and `cleanup-crds.yaml` are `Job`s running kubectl. They get no new key, and the claimed use case does not reach them. This does not apply.
- `restic-daemonset.yaml` is covered by the same change (line 56).
- No helper in `_helpers.tpl` was touched, so there are no other call sites to check.
- Pre-existing, not part of this change: `restic-daemonset.yaml:165-166` guards on `.Values.lifecycle` but renders `.Values.restic.lifecycle`. It is out of scope here, and I am not reporting it as a finding of this change.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. "Optional" is wrong for a key that always renders with a default of 3600. The comment does not say the default changed from Kubernetes' 30 s for every existing install that upgrades. | substantive | `charts/velero/values.yaml:89` | Say the default and what it means, for example "Defaults to 3600. Set 30 for the Kubernetes default." The PR description should also say that upgrades change the default for both the Deployment and the restic DaemonSet. |
| 2. An empty value renders `terminationGracePeriodSeconds: ` (null). The API treats null as unset, so the pod silently reverts to 30 s. The unguarded render and the comment give no hint. Sibling keys use an `if` guard (`deployment.yaml:58`). | substantive | `charts/velero/templates/deployment.yaml:61`, `charts/velero/templates/restic-daemonset.yaml:56` | Either guard the render the way `priorityClassName` is guarded, or state in the comment that an empty value means the Kubernetes default. |
| 3. The claimed cases have no test. No CI value sets the key. The primary use case (Velero finishes a backup before termination) is not shown anywhere in the repo, and the Velero binary's SIGTERM handling is outside it. | substantive | `charts/velero/ci/test-values.yaml` (no entry); PR description | Set a non-default value in `ci/test-values.yaml` so the chart-testing install renders it. For the use case, name a run that sends SIGTERM during a backup and checks that it completes within the grace period, or a line in Velero's shutdown code that waits for in-flight work. |
| 4. The PR description says the 30 s default was "previously immutable". It was not immutable: the pod spec field is settable, and the chart just did not expose it. | substantive (wording in the PR description, not the diff) | PR description, from the task statement | Replace "immutable" with "not exposed by the chart", or the equivalent. |
| 5. Restic gets the same global key while the chart gives restic its own `restic.*` keys for priority class and lifecycle. | taste (I prefer a separate `restic.terminationGracePeriodSeconds`; expect this to be declined, since one knob for both pods is defensible) | `charts/velero/templates/restic-daemonset.yaml:56` | Optional. Keep the global key and state in the PR that restic shares it. |

### What this review did not check
I did not run a test suite, because the chart has none, and I did not run the chart-testing install, which needs a kind cluster that is not available here. I did not check whether the Velero server or the restic node-agent waits for in-flight work on SIGTERM, since that code is outside this repository. I did not check the `helm lint` output for `ci/test-values.yaml`. The drift script parses only JVM languages, so it could not see the YAML changes.
