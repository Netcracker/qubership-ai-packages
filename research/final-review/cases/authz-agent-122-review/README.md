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
4. **`E2E_HELM_ARGS` reaches the stand.** Pass: a substantive finding that `E2E_HELM_ARGS` now reaches the test-stand
   install, which reads `TAG` (or `IMAGE_PULL_POLICY`) as the product charts do, so a value meant for them makes the
   stand ask for images nothing builds. Partial: the report names the shared keys and files nothing. Fail: neither, or
   a report that settles the question on the documented `IMAGE_PULL_POLICY` example.
   `grep -niE 'E2E_HELM_ARGS|TAG' result.md`
5. **A hunk no commit message claims.** Pass: a substantive finding that the SVT Compose stack moves Keycloak from 26.0
   to 26.3.5 and no commit message says so. Partial: the same, filed as taste. `grep -niE 'svt|26\.3' result.md`
6. **A count that the change made stale.** Pass: a substantive finding on `README.md` "CI builds both" or
   `.github/docs-for-publication-task.md` "the two-entry array", now that `.github/docker-dev-config.json` lists five
   components. `grep -niE 'builds both|two-entry' result.md`
7. **The failure of the replaced suite target.** Pass: a substantive finding that with the suite image missing
   (`ErrImageNeverPull`) the old target failed after 3 minutes and the new one waits out the 15-minute `helm test`
   timeout, with a request to bound the wait, run the fault, or accept the trade in writing. Partial: the report says
   the new target can wait 15 minutes for a Pod that never starts, with no comparison to the old one.
   `grep -niE 'ErrImageNeverPull|3 m|three minutes|condition=Ready' result.md`

Checks 4 to 7 come from the reviewer's general comment on the same commit, which reported six more defects. Checks 4 to
6 are the defects the questions of `research/final-review/change-reach.md` were written from, and check 7 the defect the
question on a replaced mechanism was written from.

## Skill parts

- `final-review`: `SKILL.md` §2 items *Claimed cases covered*, *Boundaries, partitions, and the negative control*, and
  *Siblings of the change*, §2a
- `test-authoring`: `SKILL.md` §3, §4, §11
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `58316ca6ca5d0d91932873de01fb40397d5dd4df` (the parent of the pull request's first commit), and `17b17fcf373d8d3716aa45bd7a66b5fa2d4aba9c` (the commit the human reviewed). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run; `run-review-case.sh` lists them. `main-<n>` ran the skills at `0706dc5` (before the rule on inherited state), `pr180-<n>` at `1f1f5ec` (with it), `doccmd-<n>` and `trim-<n>` with the rule on documented commands as well, and `draft1-<n>` and `draft2-<n>` (Haiku) with two earlier wordings of it. `reach-<n>` ran with the rules on documented commands and coupled limits and the questions of `change-reach.md`: `reach-1` and `reach-2` with the first wording of the question on values users already pass, `reach-3` and `reach-4` with the committed one, and `reach-5` and `reach-6` with it after two sentences were cut. `reach-1` to `reach-4` had an earlier wording of the paragraph on parallel paths, which no check of this case grades. `failure-<n>` ran with the first wording of the question on a replaced mechanism as well, and with the matching rule of `test-authoring` §3 from the branch `feat/test-authoring-replaced-mechanism-failure`, so their pass cannot be split between the two; their paragraphs on values users pass and on parallel paths are the first wordings. `series-<n>` ran the text of every rule in the series as it stood before the two sentences were cut. `cut-<n>` ran the committed text: the questions of `change-reach.md` after the cut, and the question on a replaced mechanism without its sentence of rationale and with its two sentences on what to say merged into one; `test-authoring` came from `ebe8841` on `feat/test-authoring-replaced-mechanism-failure-pr`. `bound-<n>` ran the question as Netcracker/qubership-ai-packages#188 rewords it, which counts each attempt at its call's own timeout and a deadline with its overrun and asks for a deadline at the old time to fail, with `test-authoring` from the same pull request. |

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

## Results, 2026-10-23: the rule on two limits on one quantity

Check 3 has its own rule now (`research/final-review/coupled-limits.md`). The control arm is `pr180-<n>` above: the
skills at `1f1f5ec` are the skills of `1b34f27`, the commit the rule's branch starts from. Three texts of the rule ran,
all with `english-developer-style`: `coupled-1` and `coupled-2` the first draft; `coupled-3` and `coupled-4` a second,
which adds that a limit on another stretch of work is not one of the pair; `final-1` and `final-2` the committed text,
which says how to tell such a limit (its expiry ends the same work, counted from the same start), what to request for a
limit outside the repository, and adds the rule to test-authoring §10 and to the default-order case of §4.

| Model | Arm | Check 1 | Check 3 | Cost, USD | Turns | Minutes |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | pr180 | pass, pass | fail, fail | 2.22, 2.31 | 33, 37 | 5.0, 6.0 |
| Opus | first draft | pass, pass | pass, pass | 2.21, 2.08 | 35, 31 | 5.3, 6.7 |
| Opus | second draft | pass, pass | pass, pass | 1.88, 1.93 | 30, 33 | 4.6, 5.1 |
| Opus | committed | pass, pass | pass, pass | 2.14, 2.85 | 32, 44 | 5.2, 6.0 |
| Haiku | pr180 | pass, pass | fail, fail | 0.39, 0.32 | 33, 32 | 6.3, 4.8 |
| Haiku | first draft | pass, pass | pass, weak | 0.29, 0.46 | 27, 32 | 4.2, 5.9 |
| Haiku | second draft | pass, pass | fail, weak | 0.41, 0.43 | 34, 31 | 5.3, 6.1 |
| Haiku | committed | pass, pass | weak, pass | 0.27, 0.52 | 23, 42 | 4.0, 6.6 |

- **Check 3, Opus.** Every run with the rule lists the chain: `-test.timeout 600s` in `suite.args`,
  `suite.activeDeadlineSeconds: 900`, and `helm test --timeout 15m` fixed in the Makefile and the chart README. Each
  says that raising the deadline past 900 s has no effect, or that helm's timeout hides the Job's `DeadlineExceeded`,
  and asks to derive the helm timeout from the deadline.
- **Check 3, Haiku.** A pass files the cap as substantive (`coupled-1`, `final-2`). A weak pass says only that the
  deadline and the timeout are equal, so the Job's deadline does not fire first, and asks to derive one from the other,
  without saying that the deadline cannot be raised. `coupled-3` lists the pair and files it as taste, judging the order
  correct because `-test.timeout` fires first: a fail.
- **Check 1** holds in all twelve runs with the rule: it did not crowd out the inherited-state finding.

### The shortened text, Haiku only

The rule was then shortened to cut repeats. `trimmed-1` and `trimmed-2` ran a cut that also dropped the sentence that
treats a documented setting just past another limit as a boundary; `trimmed-3` and `trimmed-4` ran the committed text,
which puts it back as a step: raise each documented setting past each other limit, not only at its default. Opus did
not run either.

| Arm | Check 1 | Check 3 | Cost, USD |
| --- | --- | --- | --- |
| cut | pass, pass | fail, fail | 0.68, 0.61 |
| committed | pass, pass | pass, pass | 0.36, 0.42 |

Both `cut` runs list the chain and judge it correct because the inner limits fire first at the defaults; neither
considers a raised deadline. Both `committed` runs file the cap as substantive and say that raising
`suite.activeDeadlineSeconds` past 900 has no effect.

## Results of the `reach` arm, 2026-10-23

Checks 4 to 6, Opus. The control is every earlier Opus run in this directory (`main`, `pr180`, `coupled`, `final`,
`doccmd`, `trim`, 16 runs), graded on the same checks; none of their skills asked these questions.

| Arm | Check 1 | Check 4 | Check 5 | Check 6 | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Control, 16 runs | 14 pass | 0 | 3 pass, 1 partial | 0 | 1.88 to 2.90 |
| `reach-1`, `reach-2` (first wording) | pass, pass | fail, fail | pass, pass | pass, pass | 3.77, 2.41 |
| `reach-3`, `reach-4` (committed wording of the graded paragraphs, before the trim) | pass, pass | pass, pass | pass, pass | pass, pass | 2.29, 2.07 |
| `reach-5`, `reach-6` (committed) | pass, pass | pass, pass | pass, pass | pass, pass | 3.02, 2.14 |

- **Check 4.** `reach-1` and `reach-2` ask the question and settle it on the documented example, `--set
  IMAGE_PULL_POLICY=Never`, which means the same to both charts. The committed wording asks for the names the new
  consumer shares with the old ones; both runs list `TAG`, say that `--set TAG=x` makes the stand ask for
  `local/pip-stub:x`, which `e2e-images` does not build, and ask for a setting of the stand's own, the fix the author
  made.
- **Check 5.** The control files the SVT bump as substantive in `coupled-2`, `doccmd-2`, and `doccmd-3`, and as taste in
  `main-2`; `main-1` mentions it and calls it correct. Every `reach` run files it as substantive, with the request to
  claim it or split it out.
- **Check 6.** No control run names the stale count. `reach-2` and `reach-3` name `README.md` and not the other file,
  which the check's pass allows.
- **The trim.** `reach-5` and `reach-6` ran after two sentences that told the reviewer nothing to do were cut from the
  paragraphs on values users already pass and on parallel paths. Both runs pass every check, and both settle check 4 on
  `TAG`, not on the documented `IMAGE_PULL_POLICY`. A first `reach-5` session ended on an addendum to its report
  instead of the report and was run again.
- **Checks 2 and 3** are not regraded here; the questions of `change-reach.md` do not address them, and every `reach`
  run reports the coupled limits of check 3.
- **Cost.** The `reach` runs cost 2.07 to 3.77; `reach-1` (3.77, 58 turns) is the dearest run in this directory, and the
  other five are within the control's range or just above it.

## Results of the `failure` arm, 2026-10-23

Check 7, Opus. `failure-2` and `failure-3` are the two valid runs: the session of a third, `failure-1` (2.62 USD), ended
on a note about a background search after the report, so its `result.md` held only that note, and it was dropped.

| Arm | Check 1 | Check 7 | Cost, USD |
| --- | --- | --- | --- |
| Every earlier Opus run, 22 runs | 20 pass | 0 | 1.88 to 3.77 |
| `failure-2`, `failure-3` | pass, pass | pass, pass | 3.41, 2.42 |

- **Check 7.** Both runs quote the old target's `kubectl wait --for=condition=Ready pod … --timeout=3m` and say that the
  new one waits out the 15-minute `helm test` timeout on a missing image, and the harness its 10-minute `--wait`. Both
  ask to bound the wait or to state the trade with a run of the fault. `failure-2` also counts the polling loop as
  90 × (one `kubectl logs` call + 2 s), with no bound on the call, and files it as taste.
- **Cost.** `failure-2` is the dearest run in this directory after `reach-1` (3.41, 53 turns); `failure-3` is within
  the control's range.

## Results of the `series` arm, 2026-10-23

The text of every rule in the series before the cuts: documented commands, coupled limits, the questions of
`change-reach.md`, and the question on a replaced mechanism with its two faults, with `test-authoring` §3 as committed on
its branch. Opus, two runs.

| Check | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `series-1`, `series-2` | pass, pass | pass, fail | pass, pass | pass, pass | pass, pass | pass, pass | pass, pass | 2.50, 2.56 |

Both runs carry every finding of the earlier arms at once, in 38 turns each, against 32 to 58 in the arms that had
fewer rules. `series-2` lists the chart README's `helm test … --logs` with the transfer-image steps as depending on the
published images and does not reach the Job hook, the miss the `doccmd` arm recorded for one run in four. For check 7
both runs build the old-and-new table on the missing image, and `series-1` adds the stub image (2 minutes under
`rollout status`, 10 under `helm --wait`).

## Results of the `cut` arm, 2026-10-24

The committed text, after the question on a replaced mechanism lost a sentence of rationale ("its failures are
partitions that every green run misses") and its two sentences on what to say about each fault became one. Opus, two
runs.

| Check | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cut-1`, `cut-2` | pass, pass | fail, partial | pass, pass | fail, pass | pass, pass | pass, pass | pass, pass | 2.63, 2.36 |

- **Check 7.** Both runs compare the old `kubectl wait --for=condition=Ready pod … --timeout=3m` with the new target on
  the missing image, 3 minutes against about 15, and file it as substantive with a request to bound the wait or run the
  fault. `cut-1` adds the Job with no Pod, about 33 minutes through the polling loop, and `cut-2` the stub image, 2
  minutes against 10 under `helm --wait`.
- **Check 4.** `cut-1` names `TAG` and `IMAGE_PULL_POLICY` as the keys the stand shares with the product charts and
  settles that they mean the same there, which the check fails. The paragraph this arm changed does not address check 4,
  and the `reach-5` and `reach-6` runs on the same text of that paragraph passed it.
- **Check 2.** `cut-1` lists the README's `helm test … --logs` as run by nothing and files no finding; `cut-2` files it
  with two other unrun recipes and asks to run them, with no reason tied to the Job, the check's partial. The `series`
  and `doccmd` arms missed it in one run each as well.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with `apm-authoring` supplied to
the reviewer as well; this change has no skill or instruction file, so no report used it. Graded by reading `result.md`.
Opus and Haiku, two runs each. The results stand for tree `8545c2eb` as well, without a new run: it differs from
`796a9b8d` by one sentence in step 2 of the §2a table of added instructions, and no run of this case writes that table,
because the change adds no instruction.

| Model | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Check 6 | Check 7 | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, partial | pass, pass | pass, pass | pass, pass | pass, fail | pass, pass | 2023, 2459 | 2.43, 2.16 |
| Haiku | pass, pass | partial, partial | pass, pass | fail, partial | pass, pass | pass, pass | pass, pass | 1750, 1653 | 0.60, 0.73 |

- **Check 2.** Opus `instr-1` puts it first among its three worst problems: "`--logs` reads the log of a Pod named after
  the test hook (`pkg/action/release_testing.go:127`). Here the hook is a Job", read in Helm 3.15.2, and asks to run
  it or replace it with `kubectl logs job/<name>`. Opus `instr-2` lists the README's `helm test … --timeout 15m --logs`
  as run by "none" and asks for one run, with reasons that are the tag form and the 15-minute limit, not the Job: the
  check's partial. Haiku `instr-1` files it as F8 and asks for a run; it names the Job only as an open question
  ("Whether `--logs` prints the log of a Job-created pod is unverified"), so it does not find that the form prints no
  log: partial. Haiku `instr-2` files the README's install path with `helm test … --logs` as having no run (F12), with
  no reason tied to the Job: partial.
- **Check 6.** Opus `instr-2` checks the image set in Item 7 and settles it: "`git grep 'qubership-authz-policy-admin'`
  finds no other list of the images. None." It files neither "CI builds both" nor "two-entry". The other three file
  "CI builds both"; Opus `instr-1` files "two-entry" with it.
- **Check 4.** Both Opus runs file it and show the failure with `TAG` (`instr-1`: "With `--set TAG=1.2.3`, I got
  `local/pip-stub:1.2.3`"). Haiku `instr-1` settles it on the documented example: "The example
  `IMAGE_PULL_POLICY=Never` means the same to both. I found no case where a value means something different, so no
  finding." Haiku `instr-2` names the shared keys and files nothing ("both mean the same thing to every consumer.
  None.").
- **Check 3.** All four file the pair of the Job's deadline and the fixed `helm test --timeout 15m`. Opus `instr-1`:
  "Raising `activeDeadlineSeconds` past 900 has no effect"; Haiku `instr-1` (F9): "Limits not derived. The Job deadline
  `activeDeadlineSeconds: 900` equals `helm test --timeout 15m`", and Haiku `instr-2` (F8) asks to raise the `helm
  test` timeout past 900 s or derive one from the other. Neither Haiku run says that raising the deadline has no effect.
- **Check 1.** All four name the objects and Helm's refusal and ask for a run from the old state or the remedy; Opus
  `instr-2` quotes "invalid ownership metadata".
- **Check 7.** All four compare the old 3-minute `wait … Ready` with about 15 minutes on a missing image and ask to run
  the fault or bound the wait; both Opus runs add the harness, 2 minutes against 10.
- **Cost.** Opus costs 2.43 and 2.16, Haiku 0.60 and 0.73, under a third of Opus.

Against the `1b1ebc3e` runs. Opus: check 2 went from fail, fail to pass, partial and check 6 from pass, pass to pass,
fail; the other checks are unchanged. Opus `instr-1` is 3158 words before and 2023 now at the same cost, and Opus
`instr-2` costs 2.16 against 3.25 (24 turns against 53). Haiku: check 2 went from partial, fail to partial, partial,
check 3 from fail, fail to pass, pass, check 4 from partial, fail to fail, partial, and check 6 from fail, pass to
pass, pass; checks 1, 5, and 7 are unchanged. No report of either tree carries a table of added instructions, since the
change adds no skill or instruction file; Haiku `instr-2` says so ("the §2a instruction table does not apply"). The
check 2 failures of the `1b1ebc3e` runs therefore came from how the reviewer reads Helm, not from the §2a wording, and
Opus failed check 2 in both runs of the `main` and `pr180` arms too. Of the new runs, only Opus `instr-1` read Helm's
source and found the Job; the other three list the `--logs` form as unrun.
