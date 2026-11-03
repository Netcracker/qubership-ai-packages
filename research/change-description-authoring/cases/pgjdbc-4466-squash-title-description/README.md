# Case: pgjdbc#4466 under a squash that copies the description

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one is a squash merge whose message is the pull request title and description, the setting uber/NullAway uses
(its last 40 first-parent commits are all squashes whose bodies are descriptions, template checklist included,
checked on 2026-10-20). §4 rule 5 makes the description the body of the one commit that lands: no headings, no
reviewer-only content, verification in one line, and no URL to this repository's code.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, reviewer-only content), §4,
  §5 (links in a commit body)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
2. **The title is a subject** (`title_is_subject`). It becomes the subject of the squash commit.
3. **The description is a commit body** (`description_as_commit_body`). No Markdown heading, no checkbox, no URL to
   `github.com/pgjdbc/pgjdbc/blob/…`. Question for the reader: is verification at most one sentence naming what the
   tests establish?

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | Title (2) | Body shape (3) | Verification in one sentence (3, read) |
| --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes: one sentence |
| Opus r2 | passes | passes | passes | fails: two sentences |
| Haiku r1 | passes | passes | passes | fails: three sentences |
| Haiku r2 | passes | passes | fails: six headings | fails: a heading and two bullets |
| Opus baseline | fails | passes | fails: headings, checkboxes, a URL | fails |
| Haiku baseline | fails | passes | fails: headings, checkboxes, a URL | fails |
| `controls/as-pushed.md` | fails | fails | passes | passes: no verification at all |
