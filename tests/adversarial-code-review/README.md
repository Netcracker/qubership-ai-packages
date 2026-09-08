# Discussion lifecycle evaluations

This is the earlier lifecycle comparison. For the subsequent Sol medium structure comparison, see
[the reassessment report](reassessment-report.md). For the final combined skill after APM packaging and installation,
see [the installed-artifact evaluation](compiled-report.md).

Compare reviewer decisions for the same 22 scenarios on GitHub and GitLab. These are simulated publication decisions
with supplied review evidence, not live API execution or an end-to-end code review. No remote discussions are mutated.

## Recorded comparison

Baseline: repository commit `3eee3aa9452514738d1936e79cbeca1748046b74`, package version `1.0.1`.
Candidate: the pre-structure `1.0.2` changes, preserved in [pre-structure-skill.txt](pre-structure-skill.txt).
The installed global skill was not the baseline; it contains other changes
that are not in this repository revision.

| Variant | GitHub | GitLab |
| --- | --- | --- |
| Baseline | 12/22 | 12/22 |
| Candidate | 22/22 | 22/22 |

The baseline fails `fixed`, `clarified`, `partial`, `disputed`, `promised`, `deferred`, `closed_broken`, `outdated`, and
`same_account_human`, and `independent_bug` on both platforms. It accepts fixes or retains findings in the summary but
avoids the corresponding
thread operations. Its recorded rationale includes: "existing discussions must not be altered."

Four fresh-context subagents produced the final outputs on September 8, 2026, one per variant/platform pair. They
inherited the parent model configuration without overrides. Exact model/version and sampling settings were not captured
by the runner, so these observations do not establish a cross-model success rate. Each agent received all 22 independent
cases in one batch; there were no repeated samples or live permission tests.

The fixtures and expected decisions reflect the user's final ownership policy: the account that authored the first
comment owns the discussion, whether the author was a human or model. A later reply or model signature does not transfer
ownership. Both variants were rerun after this policy change; the earlier agent-origin policy results are superseded.

The scorer accepts `none` and `keep_open` as equivalent for an unchanged discussion. It also accepts `none` for an
unsupported surface; reviewers must still explain the limitation. Label aliases were normalized after inspecting the
outputs; the underlying behavioral requirements were unchanged. Optional reply decisions use `null` in the oracle.
Determinate review results are also checked.

Raw responses, including reasons and ordered operations, are in [results.json](results.json). The scorer checks action,
reply, and determinate result fields. Manual inspection additionally checked the candidate operations for revision and
thread refresh, explanation before resolution changes, read-back, ownership boundaries, draft isolation, and stopping
on uncertain writes. This inspection is not a second independent judge or a runtime test of the command templates.
GitLab templates were checked against installed CLI help and the
[GitLab Discussions API](https://docs.gitlab.com/api/discussions/#resolve-a-merge-request-thread).

Local validation passed: skill `quick_validate.py`, `make check`, `make check-descriptions`, `make test` (18 Python
tests and the marketplace round-trip), Markdown lint, and `git diff --check`. The scorer also rejected an intentionally
wrong resolution decision and duplicate case IDs. No hosted CI or live discussion mutation was run.

## Repeat the comparison

1. Extract the baseline skill directory from the baseline commit into a separate temporary directory. Preserve the
   complete `SKILL.md` and `references/gitlab.md`, not just the changed sections.
2. Start a fresh agent for each variant/platform pair. Give it only the selected skill and [cases.json](cases.json).
   GitLab agents also receive that variant's GitLab reference and the installed `glab` skill. Keep the expected answers,
   other variant, prior responses, and this report out of their context.
3. Use the prompt below, substituting only the selected paths and platform. Save each returned JSON array unchanged.
4. Combine the arrays into one JSON object keyed by variant/platform name, as in `results.json`.
5. Score the outputs and manually inspect their proposed operations against the checks above.

```text
Behavioral eval, <platform> platform. Read only <selected skill> and <cases.json>.
For GitLab also read the selected references/gitlab.md and installed glab skill.
Do not read expected.json, other skill copies, parent context, or other eval results.
For each independent case act as reviewer following supplied skill; collection/review facts are authoritative.
No live services or mutations. Return a JSON array with id, action
(resolve|keep_open|none|reopen|failed|read_back|reassess|unsupported), reply boolean
(whether to create a new thread reply now), reason, operations (ordered proposed reads and writes),
and result (APPROVE|REQUEST_CHANGES|REVIEW_INCOMPLETE when determinable).
Do not force a change just because an action is available. This is a decision eval, not a skill critique.
For GitLab include command templates using host gitlab.example.com, project 42, MR 7,
full discussion ID aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, and /tmp/reply.md.
```

Run from the repository root:

```shell
python3 tests/adversarial-code-review/score.py tests/adversarial-code-review/results.json
```

The recorded comparison exits with status 1 because the baseline has failures. To check only a new candidate, pass a
JSON object containing only its runs. Missing, duplicate, or unexpected case IDs are errors.

## Input fingerprints

SHA-256 of the historical skill files used by these candidate agents:

```text
baseline SKILL.md
0d401ee8449ef63de7f3a829552d2735d5de5a34437a5313722682dc7e012ce1
baseline references/gitlab.md
fc575a799b7b3beec00962121c13dd5c77717dba9b3cd79b949c201901493dcf
candidate SKILL.md
11bb2bb0246e11fe87c026b9c4e5f3bf6f2b369809f44894b446ebf023fc1e0d
candidate references/gitlab.md
34bc03b94e2de6261a4abe91a5d84eee1dc942f4ccaef2c389d09777fa9f7a69
```
