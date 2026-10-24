# Case: review vmware-tanzu/helm-charts#408, a grace period the application caps

A case for `final-review` on the rule about two limits on one quantity (`research/final-review/coupled-limits.md`),
not derived from `authz-agent-122-review`. The input is [vmware-tanzu/helm-charts#408][pr], two commits on top of
`bd5bf865`: the velero chart gets a `terminationGracePeriodSeconds` value, default `3600`, on the server Deployment and
the restic DaemonSet. The diff is 4 files, +6 −1. The prompt quotes the pull request description as the task statement,
because the commit messages say nothing about the purpose.

The description says the value is there "to allow Velero to finish a backup before terminating". It cannot do that past
30 seconds: velero v1.9.2, the chart's `appVersion`, builds its manager with `ctrl.NewManager` and no
`GracefulShutdownTimeout` (`pkg/cmd/server/server.go:315`), and controller-runtime v0.10.2, the version its `go.mod`
pins, defaults that to `defaultGracefulShutdownPeriod = 30 * time.Second` (`pkg/manager/internal.go:54`). The process
exits at 30 seconds whatever the pod's grace period is. Nobody noticed in the review of the pull request; a user
reported it four years later in [velero-io/velero#10437][issue], with the log line `failed waiting for all runnables to
end within grace period of 30s`.

The hidden limit is in the application the chart starts, not in this repository, and the session has no network. So the
reviewer can find it only by asking which limit inside velero bounds the same shutdown.

## Checks

1. **The limit inside the application.** Pass: a substantive finding that the grace period helps only if the velero
   server itself waits that long on SIGTERM, with a request for evidence (a run, or velero's shutdown code). Strong pass:
   the finding names a shutdown limit inside velero or its controller-runtime manager. Fail: neither.
   `grep -niE 'SIGTERM|shutdown|controller-runtime|graceful' result.md`
2. **No false pair.** Note any finding that pairs the grace period with a limit on another stretch of work, such as
   `resticTimeout`, which bounds one restic operation, and claims one caps the other. It counts against the run.

## Skill parts

- `final-review`: `SKILL.md` §2 item *Boundaries, partitions, and the negative control*, §2a; item *Claimed cases
  covered* also reaches check 1
- `test-authoring`: `SKILL.md` §4, §11
- `english-developer-style`: loaded, not checked

## Files

`repo`, `base`, `head`, `prompt.md`, and `<model>/<label>/…`, as in `authz-agent-122-review`. `main-<n>` ran the skills
at `1b34f27` (before this rule), `coupled-<n>` at the working copy of the branch that adds it.

[pr]: https://github.com/vmware-tanzu/helm-charts/pull/408
[issue]: https://github.com/velero-io/velero/issues/10437

## Results, 2026-10-23

`coupled-1` and `coupled-2` ran the first draft of the rule, `coupled-3` and `coupled-4` the second, `final-1` and
`final-2` the committed text; `authz-agent-122-review` says how they differ.

| Model | Arm | Check 1 | Check 2 (false pair) | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | main | pass, pass | none, none | 0.39, 0.49 |
| Opus | first draft | pass, strong | filed, none | 0.49, 0.48 |
| Opus | second draft | pass, strong | none, none | 0.47, 0.93 |
| Opus | committed | strong, strong | none, none | 0.58, 0.50 |
| Haiku | main | fail, fail | none, none | 0.03, 0.02 |
| Haiku | first draft | partial, fail | filed, filed | 0.02, 0.02 |
| Haiku | second draft | partial, fail | filed, filed | 0.03, 0.05 |
| Haiku | committed | strong, strong | none, none | 0.02, 0.07 |

- **Opus without the rule already passes**: item *Claimed cases covered* asks what covers "allow Velero to finish a
  backup", and both `main` runs ask for evidence that velero keeps working after SIGTERM. With the rule the question
  becomes a limit in the list: `coupled-2` names the controller-runtime manager's graceful-shutdown timeout and guesses
  its 30 s default, unverified, and `coupled-4` and both `final` runs name velero's own shutdown handling as the inner
  limit that decides whether the setting has any effect. The `final` runs ask for the line in velero that waits for an
  in-flight backup, or a run that shows it. Most runs with the rule also list the outer limits the environment imposes
  (cluster-autoscaler's `--max-graceful-termination-sec`, `kubectl drain --timeout`, the kubelet's
  `shutdownGracePeriod`), which no `main` run does.
- **Haiku finds the application's limit only with the committed text.** With either draft it paired the grace period
  with `resticTimeout`, which bounds one restic operation, and filed the pair as substantive in all four runs. Both
  `final` runs name velero's own shutdown handling as the inner limit and ask for its source line or a run, and
  `final-1` says `resticTimeout` "starts inside the backup, not from the same start, so the form does not count it".

### The shortened text, Haiku only

`authz-agent-122-review` describes the two shortened texts. Both `trimmed-1` and `trimmed-2` (the cut) and `trimmed-3`
and `trimmed-4` (the committed text) pass check 1 by naming velero's own SIGTERM handling as a limit outside the
repository, and none pairs `resticTimeout`; two say it ends one operation and does not count. Costs 0.03, 0.02, 0.04,
0.05 USD.

## Results of the `series` arm, 2026-10-23

`series-<n>` ran every rule in the series that adds the questions of `research/final-review/change-reach.md` and the
question on a replaced mechanism, in the wording of 2026-10-23: before two sentences were cut from the paragraphs on
values users already pass and on parallel paths, and before the question on a replaced mechanism was shortened. Opus,
two runs, as a no-regression check against the arm named below.

| Check | `series-1` | `series-2` | `final` |
| --- | --- | --- | --- |
| 1 | strong | strong | strong, strong |
| 2 | none | none | none, none |

Unchanged. The new questions find that `helm upgrade --reuse-values`, which the README documents, never gets the new
default, and that `restic.*` has no counterpart of the new key. `series-2` also lists the restic DaemonSet hunk as
unclaimed, which commit `98041d0` does claim. Cost 0.45 and 0.55 USD against 0.58 and 0.50.
