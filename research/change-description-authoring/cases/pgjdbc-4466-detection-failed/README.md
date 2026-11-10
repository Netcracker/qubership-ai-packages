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

- `SKILL.md`: §2 (Commit body, slot 4; Pull request description: a break leads the description, headings, the
  lead-in paragraph, reviewer-only content), §4, §5 (links in a commit body)
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
5. **Outcome lead-ins, not labels** (`no_plain_outcome_labels`). The description, written to
   stand as a commit body (§4, default when detection fails), has no line that opens with `User-visible:`
   or `Not changed:`; its outcomes sit under `**User-visible changes.**` and `**Not changed.**`.
6. **Break lead-in first** (`break_lead_in_before_headings`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md): the new default breaks code that
   matches the old `application_name`, so the description opens with `**Breaking changes.**`.
7. **One line per outcome** (`outcome_lines_unwrapped`), as in the squash-default case.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Command (1) | Outcome (2) | Every commit (3) | Body shape (4) | Verification in one sentence (4, read) |
| --- | --- | --- | --- | --- | --- |
| Opus r1 (`9fe02a7c`) | passes | passes | passes | passes | passes: one sentence |
| Opus r2 (`9fe02a7c`) | passes | passes | passes | passes | passes: none |
| Opus r1 (`f03479c0`) | passes | passes | passes | passes | fails: two sentences |
| Opus r2 (`f03479c0`) | passes | passes | passes | passes | passes |
| Haiku r1 | passes | passes | passes | fails: the whole template, nine headings and checkboxes | fails: two sentences, the second a precondition |
| Haiku r2 | passes | passes | passes | fails: six headings | fails: two sentences, the second a precondition |
| Opus baseline | fails: types `upstream/master` | fails | passes | fails | fails |
| Haiku baseline | fails: types `upstream/master` | fails | passes | fails | fails |
| `controls/as-pushed.md` | fails: no command | fails | fails | passes | passes |

Both Opus runs add `git fetch upstream` and `git remote set-head upstream --auto` above the block, which type the
remote, not a branch. Haiku r1 and r2 keep a separate test commit; Haiku r1 gives it a body that references #2404.

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first two rows), graded by reading, and pass every
check, checks 5 to 7 included. Both commits write the outcome lead-ins in the §6 form, `User-visible changes.` and
`Not changed.`, with each outcome on one line; both descriptions open with `**Breaking changes.**` and use the bold
outcome lead-ins. Of the re-runs on `0d0fa5fa`, r2 wrapped its outcome lines at 72 columns, which check 7 now catches.
The Opus results of `f03479c0` failed check 5 (r2) and check 6 (both); the Haiku results, both baselines, and the
control fail check 6, and check 7 fails Haiku r1.
