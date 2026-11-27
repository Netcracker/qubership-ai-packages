# Case: review an ADR commit after which the pull request's title names a code the change no longer adds

A regression case for `final-review` on a change with no code, with `apm-authoring` loaded. The input is
[Netcracker/qubership-authz-agent#292][pr] at `b6b79c53`, the commit that dropped `TOKEN_REALM_UNKNOWN` from ADR-0091
and ADR-0095 on top of `08d388ea`. `main` never carried that code: an earlier commit of the same pull request added it.
`final-review` ran on the change before the commit with the diff and the task statement and nothing of the pull request;
after the push the description was rewritten, and the title still ended in "and add `TOKEN_REALM_UNKNOWN`" until a
reviewer pointed it out. A squash merge would have put that title on `main`.

The prompt hands over what the trigger now asks a caller for: the title and the description as GitHub showed them before
the push, both naming `TOKEN_REALM_UNKNOWN`, and the start commit `cd2f261`, the commit of `main` that `08d388ea`
merged.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/292

## Checks

Grade each by reading `result.md`.

1. **The title.** Pass: a substantive finding that the title says the pull request adds `TOKEN_REALM_UNKNOWN`, which its
   diff from `cd2f261` does not add, and a request for a title without it. Partial: the same filed as taste.
2. **The description.** Pass: a substantive finding on the description's sentences that give a token
   `TOKEN_REALM_UNKNOWN` (the R23 item and the line under `**User-visible changes.**`), with a request to rewrite or
   remove them. Partial: the same filed as taste.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over), §2
  item *Claimed cases covered*, the paragraph *The pull request*, and §2a, its analogue
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `08d388eada7b9275a856cc406feabcf2854192c9` (the merge of `main` before the commit), and `b6b79c531dec473a7bd06eeedcbb600212ca8623` (the commit). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the title and the description as GitHub showed them before the push (the description from its edit history, 2026-11-25 07:36 UTC) and the start commit `cd2f261df256068d30736f348fd61ef53193a522`. |
| `<model>/<label>/…` | The outputs of one run. `pr-<n>` ran final-review with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, with the working copy. Use a label that no committed run has: the script replaces the results
of a label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-292-pr-title-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `67598690` (version 1.4.0). The committed tree `f99ddfd4` differs from `67598690` in how
it names and defines the commit the pull request's diff starts from (the merge base of the target branch's tip and the
commit to be pushed, which the base of the change under review is only where the caller says so), in what happens where
none is handed over or the repository does not have it, and in wording; this prompt hands over that merge base, and the
repository has it, so the `pr` results stand for `f99ddfd4`. Opus and Sonnet, two runs each, graded by reading
`result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `pr-1` | pass | pass | 2171 | 1.26 |
| Opus | `pr-2` | pass | pass | 2656 | 1.47 |
| Sonnet | `pr-1` | pass | pass | 2167 | 0.45 |
| Sonnet | `pr-2` | pass | pass | 2752 | 0.41 |

- Every run files the title and the description as substantive: they still name `TOKEN_REALM_UNKNOWN`, the missing-realm
  result, and the R79 refusal that the diff from `cd2f261` no longer has (Sonnet `pr-2`: "Pull request title and
  description describe the removed `TOKEN_REALM_UNKNOWN` design, not the diff").
