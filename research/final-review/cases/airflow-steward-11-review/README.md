# Case: review apache/airflow-steward#11, a script documented for macOS that calls GNU-only tools

A regression case for `final-review`, not derived from the case it was written next to
([`authz-agent-122-review`](../authz-agent-122-review/)). The input is [apache/airflow-steward#11][pr], merged as
`1b569a83`, one commit on top of `2efe27f4`. It adds a secure setup for running Claude Code: a setup page with install
steps for Debian, Fedora, and macOS, a manifest of pinned tool versions, and
`tools/agent-isolation/check-tool-updates.sh`, which the page tells the maintainer to run before every bump, and to
schedule weekly.

The script calls `tac` and `date -d "<RFC 2822 date>"`, both GNU-only. On macOS, where the page says the setup runs,
`date -d` fails; the script hides the failure behind `2>/dev/null || continue` and reports `upstream lookup failed` for
socat. The later commit [`a9dbf6a9`][fix] (#26) replaced both calls and says it was verified on macOS. No target or CI
job in `1b569a83` runs the script; the commit message pastes one run, from a host it does not name.

[pr]: https://github.com/apache/airflow-steward/pull/11
[fix]: https://github.com/apache/airflow-steward/commit/a9dbf6a9ff94dba66b9c6b2d48ca1dc288742c22

## What it exercises

Whether the reviewer treats a command the change tells someone to run as a claimed case, and asks what its outcome
depends on, here a platform the change documents and a tool the script calls in turn. It is the same class as defect 2
of `authz-agent-122-review` (`helm test --logs` on a Job hook), with no Helm and no Kubernetes in it.

## Checks

Grade by reading `result.md`; the grep only finds the candidates.

1. **GNU-only calls on a documented platform.** Pass: a substantive finding that `check-tool-updates.sh` calls
   `date -d` (or `tac`), which macOS does not provide, while the setup page covers macOS, so the documented run fails
   or reports a false lookup failure there; the request is a run on macOS or a portable call. Partial: the report says
   the documented script was never run, or not on macOS, without naming a call that breaks there. Fail: neither.

   ```bash
   grep -niE 'date -d|\btac\b|gnu|bsd|macos|darwin' result.md
   ```

## Skill parts

- `final-review`: `SKILL.md` §2 item *Claimed cases covered*, §2a
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `2efe27f4b3ddb1b2a6cf75cadd39b1e2f078bdf8` (the parent of the merge commit), and `1b569a837831da11870aa77475aa94238a85a88a` (the change). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run; `run-review-case.sh` lists them. `pr180-<n>` ran the skills at `b3cc1f2` (without the rule on documented commands), `doccmd-<n>` at final-review tree `5086111` (with it, before a later edit that only split two sentences of the rule). |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/airflow-steward-11-review <model> <label> <rev>
```

The session needs no network. It runs on the machine that starts it, so on macOS it can observe `date -d` fail.

## Results, 2026-10-23

Two runs per model and arm.

| Model | Arm | Check 1 | Cost, USD |
| --- | --- | --- | --- |
| Opus | pr180 | pass, pass | 1.66, 1.35 |
| Opus | doccmd | pass, pass | 1.33, 1.34 |
| Haiku | pr180 | pass, pass | 0.19, 0.29 |
| Haiku | doccmd | pass, pass | 0.26, 0.32 |

The case does not tell the arms apart. Every run files the GNU-only calls as substantive, with or without the rule, and
most say they ran `date -d` on the macOS host and saw `illegal option -- d`. A defect that a local run of one call
exposes is found without a rule that asks for the run. The rule matters where the outcome depends on what a tool does
with the configuration and the reviewer cannot run it, as in `authz-agent-122-review`. This case stays as the check that
the rule costs nothing where the reviewer finds the defect anyway.
