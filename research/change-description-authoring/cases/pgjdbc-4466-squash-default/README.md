# Case: pgjdbc#4466 under a squash with the default message

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one is a squash merge with GitHub's default message: the classifier prints `merge 0 squash 40 plain 0`, and the
squash bodies are `* subject` bullets. The description is never copied, and the first commit carries the reason into
`git log`. The case is the negative control for `pgjdbc-4466-squash-title-description`: a writer that shapes every
description as a commit body drops the pull request template here, where it belongs.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, template headings), §4
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`). The output carries a `User-visible:`
   label or a "User-visible changes" heading, and a line under it or under "Breaking changes" names the new default
   value and the condition (`ApplicationName` unset). No such line carries a SQLState, an exception class, or another
   error code: the outcome emits none. Question: does a
   line give the value, and does any line carry an identifier the outcome does not emit?
2. **The first commit carries the why** (`first_commit_full_with_issue`). The first surviving commit has a body that
   states the problem (which driver version a connection uses cannot be seen in `pg_stat_activity`) and references
   `#2404`. Under the default message the body of a multi-commit squash is the list of commit messages, so this body
   is what `git log` keeps.
3. **The title is a subject** (`title_is_subject`). `feat:` or another prefix, then a lowercase imperative verb, no
   trailing period.
4. **The template stays** (`template_headings_kept`). The description uses at least one of the template's headings.
   The description is not copied under this setting, so nothing argues for stripping the template, and §2 says a
   repository's template supplies the headings.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it, with the real
pull request title and description.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | First commit (2) | Title (3) | Template (4) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | passes |
| Haiku r1, r2 | passes | passes | passes | passes |
| Opus baseline | fails: outcomes under "Behavior change", no label | passes | passes | passes |
| Haiku baseline | fails: no label | passes | passes | passes |
| `controls/as-pushed.md` | fails | fails: no `#2404`, no reason | fails: `Include` | fails |
