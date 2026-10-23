## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

No previous report exists for this change, so there is no table of prior findings. The change is YAML and Helm templates, so the drift script was run but produced no output, since it does not parse YAML. `test-authoring` was not loaded because the change adds no tests. `english-developer-style` was loaded for wording, and the form's analogue rules were used for a change with no code.

**Checks run:** `helm lint charts/velero` passes. `helm template` with `ci/test-values.yaml` and `deployRestic=true` renders `terminationGracePeriodSeconds: 3600` on both the Deployment (`deployment.yaml:61`) and the restic DaemonSet (`restic-daemonset.yaml:56`). An empty value renders a null line, and `abc` renders unquoted. I made no changes; my only scratch render went to a file that I removed, and `git status` is clean.

### Item 1: comments consistent with the code and with each other
Finding (taste): `values.yaml:89` says "Optional." Empty renders `terminationGracePeriodSeconds: ` (null), not an omitted field, so "Optional" reads as if the key disappears. The comment also does not say the default is 3600, which is a change from the Kubernetes default of 30 seconds. Suggested: name the default and the 30-second behavior it replaces.

### Item 2: claimed cases covered
The PR claims the Velero deployment can wait longer than 30 seconds before termination. No test covers it; the only automated check is `ct lint` and `ct install` in `.github/workflows/lint-test.yaml`, which asserts nothing about this field. Finding (substantive): the claimed case has no test. The restic DaemonSet change is not claimed in the PR text, but the commit `98041d0` claims it, and it is also untested.

### Item 3: boundaries, partitions, and the negative control
Finding (substantive, the limit pair): the grace period is a limit on the same quantity as `resticTimeout`. `values.yaml:289-290` documents the `velero server` default for `resticTimeout` as 1h, which equals the 3600-second grace period. At defaults the outer SIGKILL and the inner restic timeout arrive together, so the restic timeout does not fire first and its report may be hidden. Raising `resticTimeout` above 1h has no effect, because the pod is killed at 3600 seconds. The request is to derive one from the other, or to document the pair.

Finding (substantive, the default): the default changes every existing install of the Deployment and the restic DaemonSet from 30 seconds to 3600 seconds. The PR describes an opt-in use case, and it does not mention this. The request is to state the default change in the PR and the values comment, or to set the default to the Kubernetes value and leave the opt-in to users.

No negative control exists, since no test varies the value.

Pre-existing state: `helm upgrade` changes the pod template, so existing pods roll with the new value. This is expected and is not a finding.

### Item 3a: level, placement, and the environment
Finding (substantive): the smallest level that can observe this is `helm template` with a value override. The repository has no template test harness, and the only CI check that renders the chart does not assert the field. The request is to name the check that would fail if the field were dropped.

### Item 4: names by content, not by position
none. The diff adds no names, cases, or messages that use ordinals or positions.

### Item 5: the failure report
none. The diff adds no assertions.

### Item 6: what the writer says it verified
The PR states no verification evidence. Nothing shows a rendered check or a cluster run. I ran `helm lint` and `helm template` above, but those results are mine, not the writer's.

### Item 7: siblings of the change
The change adds no helper and touches no helper's call sites. Sibling setting: each pod setting in the restic block has its own `restic.*` key, for example `restic.priorityClassName` and `restic.tolerations`. The restic DaemonSet instead reads the top-level key, so its grace period cannot be set separately from the Velero Deployment's. Finding (substantive, the same defect as Item 3): the restic DaemonSet now waits up to an hour per pod on rolling updates, and the PR does not say so. The request is to name this in the PR, or to add a `restic.` key if the two should differ.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| Default 3600 changes every existing install from 30 seconds, and the PR does not say so | substantive | `charts/velero/values.yaml:90` | State the default change in the PR and the comment, or reconsider the default |
| `resticTimeout` default of 1h equals the 3600-second grace period, so the inner limit does not fire first; a larger `resticTimeout` is silently capped | substantive | `charts/velero/values.yaml:289-290`, `deployment.yaml:61` | Derive one limit from the other, or document the pair |
| Restic DaemonSet inherits the grace period from the top-level key, with no `restic.` key, and its rolling updates can now wait up to an hour per node | substantive | `charts/velero/templates/restic-daemonset.yaml:56` | Name it in the PR, or add `restic.terminationGracePeriodSeconds` |
| Claimed case has no test; the restic DaemonSet change is also untested | substantive | none (no test file exists) | Name the check that fails if the field is dropped |
| "Optional" implies omission, but empty renders a null line; the default is not named | taste | `charts/velero/values.yaml:89` | Name the default and the 30-second behavior it replaces |

Not checked: I did not run a cluster or `ct install`, so the kind job was not exercised. I did not verify Kubernetes' handling of a null grace period beyond what `helm template` renders. The drift script does not parse YAML, so comment drift was not checked. I did not do a wording pass beyond the rules that change meaning. Also, my first scratch file went to `/tmp` instead of the scratchpad directory; it holds only helm stderr and is outside the repository.
