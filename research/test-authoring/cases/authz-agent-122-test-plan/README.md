# Case: plan the tests qubership-authz-agent#122 owes

A regression case for `test-authoring` on a deployment change: Kubernetes test harnesses, a Helm chart, and a Makefile,
with no code a unit test reaches. The input is the three commits of
[Netcracker/qubership-authz-agent#122][pr] up to `17b17fcf37`, the head a human reviewer read, squashed into one commit
on `58316ca6`. The pull request moves the kind test harnesses from manifests applied with `kubectl apply` to a Helm
test-stand chart; the diff is 48 files, +1531 −791. The session writes the test plan, not the tests: the harnesses need
a kind cluster and a Docker daemon, which the case does not provide.

Two defects of the pull request are the subject of `test-authoring` §3 rules:

1. **Inherited state** ([comment][c1]). On a kind cluster an earlier `make e2e` set up, the chart meets objects the old
   harness created with `kubectl apply`, and Helm refuses to adopt them for missing ownership metadata.
2. **`E2E_HELM_ARGS` reaches the stand** ([general comment][g]). The Makefile passed `E2E_HELM_ARGS` to the
   `authz-agent` and `authz-policy-admin` installs; the change passes it to the `authz-test-stand` install too. The
   stand reads `TAG` and `IMAGE_PULL_POLICY`, as the product charts do, so `--set TAG=x` meant for the product charts
   makes the stand pull `local/pip-stub:x`, which nothing builds. Every run before the review used no value or the
   documented example, `--set IMAGE_PULL_POLICY=Never`, which means the same to all three charts.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[c1]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358379561
[g]: https://github.com/Netcracker/qubership-authz-agent/pull/122#issuecomment-6362443580

## What it exercises

Whether the plan asks for a test or a run with the values users already pass through a setting that now reaches
another consumer, and whether that rule leaves the inherited-state case in place.

## Checks

Grade each by reading `result-note.md`; the grep only finds the candidates. `result.diff` is expected to be empty.

1. **`E2E_HELM_ARGS` reaches the stand, the check the rule exists for.** Pass: the plan says that `E2E_HELM_ARGS` now
   reaches the test-stand install, names `TAG` as a key the stand shares with the product charts, says what a `TAG`
   value meant for the product charts does to the stand (images nothing builds), and asks for a test or a run with
   that value, or calls it a defect of the change. Partial: it names the reach and the shared keys and plans only the
   documented `IMAGE_PULL_POLICY` example. Fail: neither.
   `grep -niE 'E2E_HELM_ARGS|\bTAG\b' result-note.md`
2. **Inherited state, the control.** Pass: a test or a run that starts from a cluster the old harness set up, naming
   the objects it left and Helm's refusal to adopt them, or a documented remedy run on that state.
   `grep -niE 'ownership|cannot be imported|kubectl apply|e2e-down|old harness' result-note.md`

## Skill parts

- `SKILL.md`: §3, §10, §11

The results in `<model>/run-1` and `run-2` ran at skill tree `00b85c9`, test-authoring 1.2.0. They also stand for
`b11951c`, which changed only when §0 proposes a stack line where the repository already has one, and this repository
has none.

## Files

| File | What it is |
| --- | --- |
| `repo`, `base` | The repository and `58316ca6ca5d0d91932873de01fb40397d5dd4df`, the parent of the pull request's first commit. |
| `change.patch`, `change-message.txt` | The diff from `base` to `17b17fcf373d8d3716aa45bd7a66b5fa2d4aba9c` and the three commit messages, without their trailers. |
| `production-paths` | `.`: the session changes no file. |
| `build.sh` | Prints `git status --short`, since there is nothing to build. |
| `prompt.md` | The task, with `<skill>` replaced by `run-case.sh`. |
| `<model>/<arm>-<n>/` | The outputs of one run. `base-<n>` ran the skill at `387297b`, before the rule on values users already pass; `draft-<n>` with a first wording of the rule, which named one fix and no control, on an earlier base; `reach-<n>` with a twelve-sentence wording that named three fixes, the control, and what a test after a translation asserts; `trim-<n>` with the committed five-sentence wording; `run-<n>` with test-authoring 1.2.0. |

## How to run

From the repository root, once per arm and run, moving `<model>/` to `<model>/<arm>-<n>/` after each:

```bash
CYBER_FERRET_SKIP=1 research/test-authoring/cases/run-case.sh research/test-authoring/cases/authz-agent-122-test-plan <model> <rev>
```

The realm files of the change hold addresses under `example.test`, which a secret scanner on the host's commit hook may
block when the runner commits the change; the variable skips that scanner.

## Results, 2026-10-24

| Model | Arm | Check 1 | Check 2 | Cost, USD | Turns | Minutes |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | base | fail, fail | pass, pass | 1.65, 1.74 | 21, 17 | 4.4, 6.0 |
| Opus | draft | pass, pass | pass, pass | 1.64, 1.62 | 13, 14 | 5.2, 5.4 |
| Opus | reach | pass, pass | pass, pass | 1.59, 1.52 | 18, 17 | 4.2, 4.6 |
| Haiku | reach | partial, partial, pass | pass, pass, pass | 0.14, 0.11, 0.10 | 14, 12, 16 | 3.5, 3.3, 3.0 |
| Haiku | trim | pass, pass, partial | pass, pass, pass | 0.17, 0.23, 0.17 | 16, 19, 17 | 4.5, 4.9, 4.2 |

- **Check 1, `base`.** Neither run mentions `E2E_HELM_ARGS`. `base-1` names `TAG` only as a value the stand requires,
  and `base-2` only as `TAG=missing`, to inject a Pod that never becomes ready.
- **Check 1, `draft` and `reach`.** All four runs name `TAG` and `IMAGE_PULL_POLICY` as keys the stand shares with the
  product charts, take a `TAG` value meant for the product charts, and say the stand then pulls `local/…` images that
  `make e2e-images` does not build. Each calls it a defect of the change and proposes a setting of the stand's own, or
  stopping the pass-through, with a check that a `TAG` passed through `E2E_HELM_ARGS` no longer changes the stand's
  images. Both `reach` runs cite the lines of both charts that read the keys, say the documented
  `IMAGE_PULL_POLICY=Never` settles nothing, and add the control that wording asks for: a value passed through
  the stand's own variable still reaches it. `reach-2` also finds that `--timeout 3m` passed through `E2E_HELM_ARGS`
  overrides the stand's `--timeout 10m`.
- **Check 2.** All six runs plan a run from a cluster the old harness set up and name the objects it left; the new
  paragraph did not crowd it out.
- **Check 1, Haiku.** `reach-1` names the reach and plans only the documented `IMAGE_PULL_POLICY` example, leaving the
  list of shared names to be written. `reach-2` sets `TAG=1.2.3` and expects the stand's images to carry it, without
  saying that nothing builds them. `trim-3` lists the shared names with their lines and sets only `TAG=ci`, the tag
  `make e2e-images` builds. The other three runs set a `TAG` meant for the product charts and say the stand then
  pulls images nothing builds. No Haiku run plans the control that a value of the stand's own setting still reaches it.

## Results, 2026-10-31

Test-authoring 1.2.0 at skill tree `00b85c9`, two runs per model, in `<model>/run-1` and `run-2`.

| Model | Check 1 | Check 2 | Cost, USD | Turns | Minutes |
| --- | --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, pass | 1.74, 1.61 | 17, 20 | 13.6, 11.1 |
| Sonnet | partial, fail | fail, fail | 1.30, 1.33 | 34, 25 | 12.1, 7.2 |

- **Opus.** Both runs keep what `reach` found: the keys the stand shares with the product charts, a `TAG` meant for
  those charts, and the control for a fix that keeps `E2E_HELM_ARGS` away from the stand. Both plan the run from a
  cluster the old harness set up. `run-1` proposes a stack line to the user only, for the chart-render script.
- **Sonnet**, with no earlier runs to compare. `run-1` names the reach and the shared keys, then sets `TAG=smoke` and
  expects the stand's images to carry it, without saying that nothing builds them. `run-2` mentions neither
  `E2E_HELM_ARGS` nor `TAG`. Neither run plans a start from the old harness's state.
