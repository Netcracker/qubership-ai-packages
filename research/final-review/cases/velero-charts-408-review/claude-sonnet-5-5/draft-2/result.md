# Final review: `bd5bf86..HEAD` (velero chart, termination grace period)

**Inputs.** I read the whole diff (2 commits, 4 files) and the task statement (the PR description). The chart has no unit tests and no test class, so for item 2 I used the commit messages and the PR description. I loaded `english-developer-style`. `test-authoring` does not apply: there is no test code. The drift script printed nothing, because the change is YAML and Helm templates and has no members to parse. For the same reason I used the no-code analogues of §2a. The one chart-level check I ran offline was `helm lint .`, which passed.

## Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about each other.

Finding (taste): `values.yaml:89`, "The number of seconds to allow for graceful termination of the pod. Optional." The comment does not say that the value reaches two pods, the Velero server deployment and the restic daemonset. It also does not say that the default is 3600, not Kubernetes' 30. `helm template --set deployRestic=true` renders `terminationGracePeriodSeconds: 3600` in both. The neighbouring comments say "for the Velero deployment" and "for the Restic daemonset", which are separate keys. A reader of this one comment would take it to apply to Velero only. A sentence such as "Applies to the Velero deployment and, when `deployRestic` is true, the Restic daemonset" would help. This is a style-level preference, but it is on the same fact as the substantive finding under item 2.

No other comment or statement is affected. Neither the chart README (grep for `grace` and `priorityClass` finds nothing) nor the other templates make claims about this value. No comment narrates the change.

## Item 2: claimed cases covered

Analogue: cases named by the PR description. The task claims "the ability to specify the termination grace period" so that "Velero [can] finish a backup before terminating in case it takes more than the default, previously immutable, 30 seconds".

| Claimed case | Covering evidence |
| --- | --- |
| The value is configurable for the Velero server | `deployment.yaml:61` reads `.Values.terminationGracePeriodSeconds`. `helm template` shows 3600 in the Deployment. No override run is recorded. |
| The restic daemonset gets it too (commit 2) | `restic-daemonset.yaml:56`, and it renders with `deployRestic=true`. The PR description does not mention restic. |
| Backups longer than 30 s can finish | The default is raised to 3600. Nothing in the change states or checks this. |
| No test or CI value exercises a non-default value | `ci/test-values.yaml` is untouched. |

Commands the change tells someone to run: none.

Findings:

1. **Substantive.** The default is `3600`, not 30 or unset, and the description does not claim it. `values.yaml:90`. The description says the grace period becomes *specifiable* and calls 30 s the "previously immutable" default. The hunk instead changes the behavior of every existing install on upgrade, which goes from 30 s to one hour. The two pod types behave differently under that:
   - Deployment: a stuck Velero pod now takes up to an hour to be force-killed on rollout, `kubectl delete`, or node drain.
   - Restic daemonset: the same applies, and `node drain` can be blocked per node by the restic pod.

   Request: add a sentence to the description that claims the 3600 default and says why that value was chosen. Alternatively, keep the old behavior as the default (omit the field when the value is unset, and render it with `{{- if }}` or `| default`) so the setting stays opt-in.

2. **Substantive.** Applying one key to the restic daemonset is a design choice the description never claims. `restic-daemonset.yaml:56`. The use case in the description is the Velero server finishing a backup. The restic daemonset has its own values block (`restic:`, with its own `priorityClassName`, `resources`, and so on), and the sibling convention in `values.yaml:396` is a per-component key. Request: either claim the shared key in the description and the `values.yaml` comment, or add a `restic.terminationGracePeriodSeconds` key. The second option fits the pattern used for `priorityClassName`.

3. **Substantive.** The template renders the field unconditionally. `deployment.yaml:61` and `restic-daemonset.yaml:56`. Anyone who sets `terminationGracePeriodSeconds: null` or `""` (a normal way to say "use the cluster default") gets `terminationGracePeriodSeconds:` with an empty value. I rendered this with `--set terminationGracePeriodSeconds=null`, and the field came out empty. In Kubernetes an empty value is treated as unset, so the result is the 30 s default. This works by accident rather than by design, and `0` renders as `0`, which means immediate kill. Request: guard with `{{- if kindIs "invalid" ... }}`/`hasKey`, or state in the values comment that the key must be an integer.

## Item 3: boundaries, partitions, and the negative control

Analogue: configuration, deployment definition, and package installed over an earlier version.

- Partitions claimed: default, overridden, and `deployRestic` on and off. Only the default was rendered here. Neither a non-default value nor `deployRestic=false` (which renders no daemonset) is exercised by `ci/test-values.yaml` or any other file. Substantive, under finding 3 above for the empty and `0` boundary. I ran the default and `deployRestic=true` myself, and the others are not in the change.
- Pre-existing state: an upgrade meets running pods and the old 30 s value. Because the field lives in a pod template, a rolling upgrade restarts both pods once. This is normal for Helm chart changes and not a finding, but it also means the first terminating pod after upgrade is the first one to use the new period.
- Limits on the same work (the other termination-related limits): the Velero server's backups run inside the pod's lifetime, so the effective cap is the smaller of this value and anything in the enclosing node drain (`--timeout` on `kubectl drain`, the autoscaler's own grace limit for scale-down, typically 600 s in cluster-autoscaler). A raised value above those has no effect. The change does not mention this. Taste: a note in the values comment.
- The chart's `upgrade-crds` and `cleanup-crds` jobs are Jobs with their own pods and are untouched. Not a finding.

## Item 3a: level, placement, and the environment

Analogue: where the rule lives and whether the repository's gate covers it. The change sits in `values.yaml` and the two templates, beside the equivalent `priorityClassName` settings, and so matches the siblings' layout. `ct.yaml` and `ci/test-values.yaml` exist and are the repository's gate, but the change adds no value to the CI file, so a lint run would not render a non-default value. `helm lint` passes on the default. Substantive only in combination with item 3's missing partitions; no separate finding.

## Item 4: names by content, not by position

none. The key `terminationGracePeriodSeconds` matches the Kubernetes field name. No ordinal or positional references appear in the diff.

## Item 5: the failure report

none. There are no assertions or parameterized cases in the change. The commit subjects are descriptive. Their wording ("adding … Helm value") is not imperative, but the repository's recent subjects follow the same style, so I treat it as churn and do not report it.

## Item 6: what the writer says it verified

No evidence is stated in the change or the commit messages (no rendered output, no `helm template` run, no mutation or red run). I did not supply any. In my own checks, the rendered output matches the diff and the lint passes.

## Item 7: siblings of the change

- Other pod templates in the chart: `upgrade-crds.yaml` and `cleanup-crds.yaml` are Jobs and need no grace period. No other Deployment or DaemonSet exists (`git grep` of `kind:`). Not findings.
- The set that gains a member is the top-level values keys. The chart README (`charts/velero/README.md`) was grepped for `priorityClassName`, the nearest existing key, and for `grace`. Neither appears, so there is no list of overrides to extend and no sentence that counts the keys.
- Chart version: `Chart.yaml` moves 2.31.8 to 2.31.9, which is the chart's normal bump for a change and is claimed by the change itself. Not a finding.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| `values.yaml` comment omits that the key reaches both the Velero deployment and the restic daemonset, and that the default is 3600 | Taste | `charts/velero/values.yaml:89` | 1 |
| Default changed from 30 s to 3600 s for all installs, which the description does not claim (it describes only making the value specifiable) | Substantive | `charts/velero/values.yaml:90` | 2 |
| Restic daemonset takes the same key, which is not claimed and departs from the per-component `restic.*` convention | Substantive | `charts/velero/templates/restic-daemonset.yaml:56` | 2 |
| The field is rendered unconditionally, so `null`/empty renders an empty field and `0` means immediate kill; no non-default or `deployRestic=false` case is in the CI values | Substantive | `charts/velero/templates/deployment.yaml:61` | 2, 3 |
| Node-drain and autoscaler limits can cap the raised value, and the comment does not say so | Taste | `charts/velero/values.yaml:89` | 3 |

Checks not done: the drift script is not applicable to YAML (it listed nothing); no cluster was available, so I did not test eviction or drain behavior, and the drain and autoscaler limits above come from general Kubernetes behavior, not from this repository.
