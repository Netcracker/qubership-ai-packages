## Final review: `bd5bf865..HEAD` (termination grace period Helm value)

Two commits, four files: a chart version bump (2.31.8 to 2.31.9), a new `terminationGracePeriodSeconds` value (default 3600) in `values.yaml`, and the field rendered in `templates/deployment.yaml:61` and `templates/restic-daemonset.yaml:56`. The change has no code and no tests, so the form ran through the section 2a analogues. I loaded `english-developer-style` for wording. I did not load `test-authoring`, since no test changed. The drift script ran and printed nothing: it parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, so it checked nothing here.

Verification I ran: `helm lint` passes. `helm template` with `ci/test-values.yaml` renders `terminationGracePeriodSeconds: 3600` in both the Deployment and the DaemonSet. With `--set terminationGracePeriodSeconds=120` it renders 120. With an empty value it renders a null (`terminationGracePeriodSeconds: `). With `0` it renders `0`.

No previous report exists, so there is no table of prior findings.

### Item 1: comments consistent with the code and with each other
Analogue: the comment in `values.yaml:89`. The templates carry no comments.
- The first sentence ("The number of seconds to allow for graceful termination of the pod.") states what the key is. It does not state the default or that the restic DaemonSet shares the value. See T1.
- "Optional." is wrong about the unset case: the key always renders, so an install that never sets it gets 3600 s, not the Kubernetes default of 30 s. See S1.
- No comment narrates the change.

### Item 2: claimed cases covered
Analogue: the claimed cases are the PR's "ability to specify the termination grace period" and the commit's restic DaemonSet case.
- No test sets a non-default value. `ct.yaml` runs `ct install` with `charts/velero/ci/test-values.yaml`, which sets no `terminationGracePeriodSeconds`, so CI renders only the default. See S3.
- The changed files contain no command lines for a reader to run: none.

### Item 3: boundaries, partitions, and the negative control
- Partitions: the default is rendered by CI. Override, empty, and `0` are not run by any test, and the empty case is not documented. See S3 and T2.
- Pre-existing state: an existing install upgraded from 2.31.8 with default values gets a changed pod template for both workloads, so every install restarts on upgrade. `ct.yaml` sets `upgrade: true`, so CI does run an upgrade on default values, but nothing measures how long termination takes. See S2.
- Limits on the same work: the claim that Velero "finishes a backup" rests on Velero's SIGTERM handling, which is in the Velero binary, not in this repo. The kubelet's node-level `shutdownGracePeriod` also caps pod grace during node shutdown, but only where an operator sets it, and it is off by default. See S4.
- Item 3a, level and placement: the only level here is the chart CI (`ct lint`, `ct install` on kind). The new key sits beside `priorityClassName` and `tolerations`, matching its siblings. Any test belongs in the existing fixture `charts/velero/ci/test-values.yaml`, not in a new file.

### Item 4: names by content, not by position
none. The change adds no names or ordinals.

### Item 5: the failure report
none. The change adds no assertions.

### Item 6: what the writer says it verified
Not stated. The writer gives no render check, no CI run, and no evidence the value takes effect. The render results above are my checks, not the writer's evidence.

### Item 7: siblings of the change
- The value is set in both the Deployment and the restic DaemonSet, which are the two workloads that carry this pod spec. The two `Job` templates (the `ct` render shows them at lines 299 and 350) do not get the field. The claim does not cover them: none.
- The `Chart.yaml` bump follows the repo's practice. The lifecycle-hooks feature got a patch bump (`cdfb950`, "Bump chart version to 2.31.5"): none.
- `charts/velero/README.md` points to `values.yaml` and has no value table to update: none.
- Outside this change, `templates/restic-daemonset.yaml:165` guards on `.Values.lifecycle` but renders `.Values.restic.lifecycle`. That predates this diff and is not part of this review.

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| "Optional." misdescribes the default. The key always renders, so an install that never sets it gets 3600 s, not the Kubernetes default of 30 s, and the comment does not say so. | substantive | `charts/velero/values.yaml:89-90` | State the default and what it changes in the comment. Keeping 3600 or choosing 30 is the writer's call. |
| The default changes termination for every existing install on upgrade, and the PR description does not say so. The restic DaemonSet sets no `updateStrategy`, so a rollout goes one node at a time, and a restic pod that does not exit on SIGTERM holds the rollout for up to an hour per node. | substantive | `charts/velero/values.yaml:90`, `templates/restic-daemonset.yaml:56` | Name the default change and its rollout effect in the PR description. Show a run from a 2.31.8 install upgraded with default values, or record that the rollout time is unmeasured. |
| The claimed ability to specify the value has no test. `ci/test-values.yaml` sets nothing, so CI renders only the default. | substantive | `charts/velero/ci/test-values.yaml` (no key today) | Add `terminationGracePeriodSeconds` with a non-default value to the existing CI fixture, so `ct install` renders it in both workloads. |
| The PR's purpose, a backup that finishes before termination, is not shown. The repo does not contain Velero's SIGTERM handling, and the kubelet's `shutdownGracePeriod` can cap the grace on node shutdown. | substantive | `charts/velero/templates/deployment.yaml:61` | Name the Velero line that waits on SIGTERM, or run a Velero pod through a termination during a backup and record the result. Name the kubelet cap as an unverified limit. |
| The comment does not say the value also governs the restic DaemonSet, and restic has no per-workload override, unlike its `restic.priorityClassName` and `restic.lifecycle` siblings. | taste | `charts/velero/values.yaml:89` | Say "and the restic DaemonSet" in the comment. A separate `restic.terminationGracePeriodSeconds` is the other reading; I prefer the comment. |
| An empty value renders `terminationGracePeriodSeconds: ` (a null), and the comment does not say what empty means. | taste | `charts/velero/values.yaml:89` | Say what empty means, or guard the template with `with`. |

## Not checked
The drift script produced no output because it parses only JVM languages. There is no cluster, so the null-as-unset behavior, the Velero SIGTERM behavior, and the rollout time are all unverified. The `ct install` CI job was not run. The `test-authoring` skill was not loaded because no test changed.
