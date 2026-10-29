## Final review: `bd5bf865..HEAD` (Helm value `terminationGracePeriodSeconds`)

**Scope.** Two commits: `Chart.yaml` version 2.31.8 → 2.31.9, the new key in `values.yaml`, and a `terminationGracePeriodSeconds` line in `deployment.yaml` and `restic-daemonset.yaml`. The change has templates, so the code form applies, not §2a. The drift script ran (`comment-drift.py bd5bf86 HEAD`) and printed nothing, because it parses no YAML or template members. Item 1 was therefore done by reading each comment against its template. No previous report of this form exists.

**Checks I ran:** `helm lint` passes. `helm template` renders `terminationGracePeriodSeconds: 3600` by default, `30` when overridden, and an empty line (a null field) when set to empty or `null`.

### Item 1: comments consistent with the code and with each other
Finding F2 below. The first sentence of the new comment at `values.yaml:89` is accurate for the deployment, but it says "the pod" and does not cover the restic daemonset, which the same key also sets. No other comment in the file contradicts it, and "Optional." is accurate because a default exists. The chart README has no values table to update, so no other comment is affected.

### Item 2: claimed cases covered
The PR claims the value is configurable and reaches the Velero pod. No test or render check names either case. `ci/test-values.yaml` does not set the key, and `lint-test.yaml` runs `ct lint` and `ct install` on kind, which would not assert the field. See F4.

### Item 3: boundaries, partitions, and the negative control
- Partitions present: default (3600), explicit value (30), and empty or null (renders a null field). None is tested. See F6.
- Limit on the same quantity: `resticTimeout`, documented at `values.yaml:289-290` as the `velero server` default of 1h, bounds the restic work that this grace period is meant to let finish. At the defaults both are 3600 s. A `resticTimeout` raised above the grace period cannot let an in-flight backup finish, because SIGKILL arrives first. See F3.
- Pre-existing state: an existing release upgraded to this chart gets 3600 s with no value set, a change in behavior nobody asked for. No run starts from that state. See F1 and F5.
- Environment limit I could not verify offline: the kubelet's graceful node shutdown may cap the total grace time on node shutdown.

### Item 3a: level, placement, and the environment
The smallest level that observes the behavior is a render of the chart with the value set. No such check is committed, so the request is F4. The new key sits in `values.yaml` beside `priorityClassName` and has no test of its own, so there is no sharing question.

### Item 4: names by content, not by position
none. No new name, case id, or message refers by position.

### Item 5: the failure report
none. No assertion was added.

### Item 6: what the writer says it verified
Neither a red run nor a render result is stated in the PR description or the commits. The chart has no tests to go red. See F4.

### Item 7: siblings of the change
- The key is read at exactly two sites, `deployment.yaml:61` and `restic-daemonset.yaml:56`. The other `terminationGracePeriodSeconds` hits are in `crds/restores.yaml` and are unrelated.
- `cleanup-crds.yaml` and `upgrade-crds.yaml` are Jobs with pod specs. I did not read them in full. A Job's pod runs to completion, so the default does not have the same effect on it.
- The version bump follows the repository's convention, as the previous commit did.
- The `restic` block already splits `priorityClassName` per component (`values.yaml:395-396`, `restic-daemonset.yaml:53-54`). The new key does not follow that pattern. See T1.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The default moves from the Kubernetes 30 s to 3600 s for every install, including upgrades of existing releases, and the PR does not say so. A pod that ignores SIGTERM now holds a rollout or drain for up to an hour. | substantive | `charts/velero/values.yaml:89-90`, `templates/deployment.yaml:61` | Name the new default and the upgrade effect in the PR description, or pick the default that matches the stated behavior. |
| F2 | The comment says "the pod", but the key also sets the restic daemonset pods. Neither the comment nor the PR says so. | substantive | `charts/velero/values.yaml:89`, `templates/restic-daemonset.yaml:56` | Name both workloads in the comment. |
| F3 | The pair with `resticTimeout` is undocumented. At defaults both are 3600 s, and the grace period caps any `resticTimeout` raised past it for a backup in flight at termination. | substantive | `charts/velero/values.yaml:90`, `values.yaml:289-290` | Document the pair, or derive one default from the other. |
| F4 | The claimed cases (configurable, reaches both pods) have no test. Nothing renders the field or asserts it, and CI does not check it. The PR states no verification at all. | substantive | `charts/velero/ci/test-values.yaml`, `.github/workflows/lint-test.yaml` | Add a `helm template` check that asserts the field for the default and an override, or state in the PR what was rendered. |
| F5 | No run starts from the state an earlier release leaves behind (a Deployment with no grace field). The behavior change on upgrade is unverified. | substantive | `ct.yaml` (`upgrade: true`) | Run an upgrade from 2.31.8 with default values and check the rendered field. I did not verify whether `ct install` reaches a release installed from the base chart. |
| F6 | The empty and null partition renders `terminationGracePeriodSeconds:` with no value. Its effect on the API server is unverified, and no comment or test states it. | substantive | `charts/velero/values.yaml:90` | Add the case to the render check in F4, and state its effect in the comment. |
| T1 | The key is top-level and shared by two workloads, while `priorityClassName` is split per component. | taste | `charts/velero/values.yaml:90`, `values.yaml:395-396` | Prefer `restic.terminationGracePeriodSeconds`. Expect this to be declined if the shared key is intended, and say so in the PR. |

### What this review did not check
- I did not run any cluster, so the Kubernetes behavior of a null field, the kubelet's graceful node shutdown, and Velero's own behavior on SIGTERM are unverified.
- I did not verify `ct install`'s `upgrade: true` semantics.
- I did not read `cleanup-crds.yaml` or `upgrade-crds.yaml` in full.
- The PR description's prose was not checked for style; this form covers wording only where a sentence reads wrongly.
