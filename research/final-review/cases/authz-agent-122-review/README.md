# Case: review qubership-authz-agent#122 at the commit a human reviewed

A regression case for `final-review`, with `test-authoring` loaded as the skill whose rules it checks. The input is
[Netcracker/qubership-authz-agent#122][pr] at `17b17fcf37`, the head a human reviewer read: three commits on top of
`58316ca6`. The pull request moves the kind test harnesses from manifests applied with `kubectl apply` to a Helm
test-stand chart; the diff is 48 files, +1531 −791.

Before the human review, the author's runs and two automated passes, `final-review` and a Codex plus Claude
cross-review, all used a fresh cluster and did not report the first defect below. The human reviewer reported three:

1. **Inherited state** ([comment][c1], posted on `5dcb6be8` about the templates of `17b17fcf`). On a kind cluster an
   earlier `make e2e` set up, the install fails: the old harness created `keycloak`, `pip-stub`, the
   `authz-agent-client-credentials` Secret, and other objects with `kubectl apply`, they carry no Helm ownership
   metadata, and Helm stops with `exists and cannot be imported into the current release: invalid ownership
   metadata`. The `parity-harness` target fails the same way.
2. **`helm test --logs` prints no suite log** ([comment][c2]). The suite is a Job, and Helm reads logs only from
   test hooks that are Pods.
3. **A fixed `helm test` timeout** ([comment][c3]). The Makefile passes 15 minutes, while the Job's own limit comes
   from `suite.activeDeadlineSeconds`, so a longer suite cannot be configured through the values alone.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[c1]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358379561
[c2]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358379572
[c3]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358379579

## What it exercises

Whether the reviewer asks which pre-existing state the change will meet: `final-review` item *Boundaries, partitions,
and the negative control* and its analogue for a change with no code, and `test-authoring`'s rule on state an earlier
version left behind. Since the `doccmd` arm, check 2 also exercises `final-review`'s rule that a command the change
tells someone to run is a claimed case, covered by a script or CI job that runs that exact form. Check 3 measures the
review as a whole.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **Inherited state, the check the rule exists for.** Pass: a substantive finding that the chart will meet objects
   an earlier `kubectl apply` harness created, that Helm will not adopt them (ownership metadata, `cannot be
   imported`), and a request for a run from that state, a cleanup, or a documented remedy such as `make e2e-down`
   first. Partial: the report asks about an upgrade or a cluster from before the change, without naming the objects
   or the adoption failure. Fail: neither. The candidates:

   ```bash
   grep -niE 'ownership|cannot be imported|kubectl apply|already exist|e2e-down|pre-existing|inherited' result.md
   ```

2. **`helm test --logs` and a Job hook.** Pass: a finding that the documented `--logs` prints no suite log, or fails,
   because the hook is a Job. Partial: a substantive finding that no target or CI job runs the README's
   `helm test … --logs`, which the Makefile runs without `--logs`, and a request to run that form or replace it with the
   Makefile's, with no reason tied to the Job. Fail: neither, or a report that settles it because the flag exists.
   `grep -niE -- '--logs' result.md`
3. **The fixed timeout.** Pass: a finding that the 15-minute `helm test` timeout does not follow
   `suite.activeDeadlineSeconds`. `grep -niE '15m|timeout|activeDeadline' result.md`

## Skill parts

- `final-review`: `SKILL.md` §2 items *Claimed cases covered* and *Boundaries, partitions, and the negative control*,
  §2a
- `test-authoring`: `SKILL.md` §3, §4, §11
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `58316ca6ca5d0d91932873de01fb40397d5dd4df` (the parent of the pull request's first commit), and `17b17fcf373d8d3716aa45bd7a66b5fa2d4aba9c` (the commit the human reviewed). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run; `run-review-case.sh` lists them. `main-<n>` ran the skills at `0706dc5` (before the rule on inherited state), `pr180-<n>` at `1f1f5ec` (with it), `doccmd-<n>` and `trim-<n>` with the rule on documented commands as well, and `draft1-<n>` and `draft2-<n>` (Haiku) with two earlier wordings of it. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-122-review <model> <label> <rev>
```

The session needs no cluster and no build; it may run `helm template` and `go` where they are installed.

## Results, 2026-10-23

Two runs per model and arm, skills at `0706dc5` (`main-<n>`) and `1f1f5ec` (`pr180-<n>`). In these eight runs the
runner did not copy `english-developer-style` (the package directory is `english-us-developer-style`; fixed since),
so the sessions ran without it, in both arms alike. No check grades wording.

| Model | Arm | Check 1 | Check 2 | Check 3 | Cost, USD | Turns | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | main | fail, fail | fail, fail | fail, fail | 2.79, 2.19 | 47, 39 | 6.5, 5.4 |
| Opus | pr180 | pass, pass | fail, fail | fail, fail | 2.22, 2.31 | 33, 37 | 5.0, 6.0 |
| Haiku | main | fail, fail | fail, fail | fail, fail | 0.41, 0.48 | 45, 50 | 5.6, 6.5 |
| Haiku | pr180 | pass, pass | fail, fail | fail, fail | 0.39, 0.32 | 33, 32 | 6.3, 4.8 |

- **Check 1.** Every `pr180` run files it as the first substantive finding: it lists the objects the old
  `kubectl apply` harness created, says Helm will refuse them for missing ownership metadata, notes that CI starts
  from a fresh cluster, and asks for `make e2e-down` or a documented and run remedy. The Opus runs say they derived
  the refusal from Helm's adoption rule and did not run it. No `main` run mentions a cluster from before the change,
  not even as an upgrade question; the closest is a finding that a troubleshooting row still names `rollout status`.
- **Checks 2 and 3.** No run in either arm finds them. Haiku `pr180-1` mentions `--logs` only to say the recipe streams
  the log instead. The rule on inherited state does not address either defect, and neither arm got worse on them.
- **Cost.** Opus costs 2.19 to 2.79 per run and Haiku 0.32 to 0.48, about six times less; the `pr180` arm is not
  dearer. The whole matrix cost 11.11.

The case comes from the incident the rule was written from, and the rule names objects created by `kubectl apply`, so
a pass shows that the reviewer applies the rule, not that it generalizes to a configuration file, a key, or a schema.

## Results of the `doccmd` arm, 2026-10-23

Skills at the working copy of the branch that adds the rule on documented commands to `final-review` item *Claimed
cases covered* (final-review tree `5086111`, before a later edit that only split two sentences of the rule). The
control is the `pr180` arm above. Its skill trees match apart from that rule, and the `pr180` runs also had no
`english-developer-style`, which the runner now copies.

| Model | Arm | Check 1 | Check 2 | Check 3 | Cost, USD | Turns | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | doccmd | pass ×4 | pass, partial, fail, pass | fail ×4 | 2.83, 2.22, 2.35, 2.46 | 50, 35, 33, 40 | 8.4, 6.2, 6.2, 6.2 |
| Haiku | doccmd | pass, pass | partial, fail | fail, fail | 0.71, 0.60 | 53, 42 | 8.2, 7.5 |
| Opus | trim | pass, pass | pass, pass | fail, fail | 2.90, 2.28 | 41, 40 | 6.1, 5.5 |
| Haiku | trim | pass, pass | fail, partial | fail, fail | 0.63, 0.97 | 44, 66 | 6.8, 10.0 |
| Haiku | draft1 | pass, pass | fail, fail | fail, fail | 0.88, 0.70 | 62, 45 | 8.9, 8.2 |
| Haiku | draft2 | pass, pass | partial, partial | fail, fail | 0.62, 0.48 | 45, 38 | 7.8, 6.8 |

- **Check 2.** The two Opus passes read `GetPodLogs` in the Helm v3.15.2 source, found in the Go module cache of the
  machine that ran the case, and report that it asks for a Pod named after the hook, so on a Job hook the command
  fails and `helm test` exits non-zero. Neither could read Helm 4's source, and both mark it as not verified. One
  guesses from strings in the binary that Helm 4 finds the Job's Pods by label; in v4.3.0, `GetPodLogs` skips every
  hook whose kind is not `Pod`, so the command prints no suite log. A pass therefore depends on the host having a Helm
  source at hand. The partials list the README's `helm test … --logs` as a form no target or CI job runs and ask for a
  run or the Makefile's form, which would have removed the defect, without naming the Job. The fails list it as `none`
  and stop: Opus `doccmd-3` calls the outcome "Helm's documented behavior", and Haiku `doccmd-2` notes that the flag
  exists, the shortcut the rule names.
- **Wording.** `draft1` named no list, and one run settled the command because its flags exist. `draft2` asked for
  the list with a runner or `none` per command, and both runs put `--logs` in it. The final wording adds that the
  reviewer reads what the help text, reference, or source says the flag acts on; `helm test --help` says
  `dump the logs from test pods`, and no Haiku run used it. The sentence is not shown to help: no Opus run used
  `draft2`.
- **Trim.** The `trim` runs use the committed wording (final-review tree `72d37b4`). It drops sentences no run relied
  on: an explanation of why the outcome depends on the tool, the file-layout and called-script examples, and the
  instruction to mark an unread answer as not verified. The list with a runner or `none`, the rule that a differing form
  is `none`, and the warning against settling a command by its flag are kept. Both Opus runs pass. Haiku `trim-2` files
  the form as unrun and says its output for a Job hook is unverified; `trim-1` lists it as `none` and files nothing.
- **Side findings.** Opus `doccmd-2` and `doccmd-3` and Haiku `doccmd-2` report that the Makefile's comment above
  `run-suite` says `helm test` prints the log at the end, while the recipe passes no `--logs`; Haiku `pr180-1` said
  the same without the rule. It is the same class, in the same pull request.
- **Cost.** Haiku takes 53 and 42 turns in `doccmd` against 33 and 32 in `pr180`, and Opus 33 to 50 against 33 and
  37. The `doccmd` runs also loaded `english-developer-style`, so the extra turns are not the rule's alone.
