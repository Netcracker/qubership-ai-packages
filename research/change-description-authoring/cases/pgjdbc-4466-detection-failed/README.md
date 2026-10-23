# Case: pgjdbc#4466 before anyone has read the history

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

Here nobody has run the detection: the contributor's clone has `origin` on the fork and `upstream` on pgjdbc/pgjdbc,
and the pull request is not open yet. The output owes the detection command as §4 prints it, with `remote=upstream`
set and no branch name typed into the command, and, until the command has run, the artifacts under §4's default when
detection fails: every commit full with the issue number, and a description that can stand as a commit body. The shell
side of the command, a branch name that carries `;` or `$(`, is tested by
[`../check-classifier-target-ref.sh`](../check-classifier-target-ref.sh); this case tests that the writer sets the
remote and leaves the branch name to the variable.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request description, headings and reviewer-only content), §4, §5 (links
  in a commit body)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The command** (`detection_commands`). A fenced block sets `remote=upstream`, passes the branch to `git log` as
   `"$target" --`, and types no branch name (`master`, `upstream/master`) into the `git log` or `target=` lines.
2. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
3. **Every commit stands alone** (`every_commit_full_with_issue`), as in
   [`pgjdbc-4466-squash-or-rebase`](../pgjdbc-4466-squash-or-rebase/README.md).
4. **The description can stand as a commit body** (`description_as_commit_body`): no heading, no checkbox, no URL to
   the repository's code.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-20 on the skill whose tree id is in `<model>/skill-tree` (`e4c81d96`, `main` at 2cee8a6), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Command (1) | Outcome (2) | Every commit (3) | Body shape (4) | Verification in one sentence (4, read) |
| --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes | fails: three sentences |
| Opus r2 | passes | passes | passes | passes | fails: two sentences |
| Haiku r1 | passes | passes | passes | fails: two headings | fails: three sentences |
| Haiku r2 | passes | passes | passes | fails: the whole template, nine headings | fails: four sentences |
| Opus baseline | fails: types `upstream/master` | fails | passes | fails | fails |
| Haiku baseline | fails: types `upstream/master` | fails | passes | fails | fails |
| `controls/as-pushed.md` | fails: no command | fails | fails | passes | passes |

Both Opus runs add `git fetch upstream` and `git remote set-head upstream --auto` above the block, which type the
remote, not a branch.
