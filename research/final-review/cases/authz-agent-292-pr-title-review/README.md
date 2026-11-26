# Case: review an ADR commit after which the pull request's title names a code the change no longer adds

A regression case for `final-review` on a change with no code, with `apm-authoring` loaded. The input is
[Netcracker/qubership-authz-agent#292][pr] at `b6b79c53`, the commit that dropped `TOKEN_REALM_UNKNOWN` from
ADR-0091 and ADR-0095 on top of `08d388ea`. `main` never carried that code: an earlier commit of the same pull request
added it. `final-review` ran on the change before the commit, with the diff and the task statement and nothing of the
pull request. After the push, the description was rewritten for the new diff, and the title still ended in "and add
`TOKEN_REALM_UNKNOWN`" until a reviewer pointed it out the next day. A squash merge would have put that title on `main`.

The case gives the reviewer the title and the description as GitHub showed them when that review ran, before the push:
both name `TOKEN_REALM_UNKNOWN`. A reviewer that reads the description and not the title fails check 1.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/292

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **The title.** Pass: a substantive finding that the title says the pull request adds `TOKEN_REALM_UNKNOWN`, which
   its diff against `origin/main` does not add, and a request for a title without it. Partial: the same filed as
   taste. `grep -niE 'TOKEN_REALM_UNKNOWN|title' result.md`
2. **The description.** Pass: a substantive finding on the description's sentences that give a token
   `TOKEN_REALM_UNKNOWN` (the R23 item and the line under `**User-visible changes.**`), with a request to rewrite or
   remove them. Partial: the same filed as taste.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description), §2 item *Claimed cases
  covered*, the paragraph *The pull request*, and §2a, its analogue
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `08d388eada7b9275a856cc406feabcf2854192c9` (the merge of `main` before the commit), and `b6b79c531dec473a7bd06eeedcbb600212ca8623` (the commit). |
| `pr-target`, `gh/pr-view.json` | `main` at `cd2f261d`, the commit that `08d388ea` merged, which `run-review-case.sh` sets as `origin/main`; and the title and the description of the pull request before the push, as `gh pr view --json state,title,body,baseRefName,baseRefOid` prints them, the description taken from its edit history (the edit of 2026-11-25 07:36 UTC). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. It does not say that the branch has a pull request: it says that gh cannot reach GitHub, and that where a skill asks for a gh command, its saved output is under `<gh>`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-292-pr-title-review <model> <label> [<rev>]
```

## Results, 2026-11-26

`pr-<n>` ran final-review tree `63a559df` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0). The committed
tree `2a8a0411` differs from `63a559df` in which commit the pull request's diff starts from (the fetched tip of the base
branch, or offline the newer of the remote-tracking copy and `baseRefOid`, rather than `baseRefOid` alone), in the
wording of two sentences, and in the wrapping of one bullet in §1. Here `origin/main` and `baseRefOid` are the same
commit, so the diff is the same, and the results stand for `2a8a0411`. Opus and Sonnet, two runs each, graded by reading
`result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | 1688 | 1.21 |
| Opus | `base-2` | pass | pass | 1711 | 1.03 |
| Opus | `pr-1` | pass | pass | 1997 | 1.18 |
| Opus | `pr-2` | pass | pass | 2030 | 1.07 |
| Sonnet | `base-1` | pass | pass | 1390 | 0.42 |
| Sonnet | `base-2` | pass | pass | 2173 | 0.42 |
| Sonnet | `pr-1` | pass | pass | 1513 | 0.41 |
| Sonnet | `pr-2` | pass | pass | 1729 | 0.33 |

- **The tree before the paragraph passes too**, for the reasons `textkit-pr-title-stale-review` gives: every `base` run
  reads `gh/pr-view.json` and files the title and the description as substantive. Sonnet `base-2` files it under item
  7, as a sibling of the change.
- **What the paragraph changes.** The `pr` runs compare the text with the diff from `cd2f261` (Opus `pr-1`,
  `result.md:48`: "I read the PR diff as `git diff cd2f261 HEAD`"), and three of four give a new title; the `base`
  runs compare it with the commit and ask to "rewrite the title". Sonnet `pr-1` says it "could not fetch `baseRefOid`"
  and did not read the merge-base diff, although the commit is in the clone as `origin/main`; its finding rests on the
  commit. Opus `pr-1` names the pull request `#289`, the issue its description closes.
