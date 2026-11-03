# Case: pgjdbc#4501, a one-line fix checked by hand

The input is the description of [pgjdbc/pgjdbc#4501](https://github.com/pgjdbc/pgjdbc/pull/4501) as posted, 80 words
for a one-line fix in a shell script, with the diff and the task to rewrite it. No test covers the script; the
description's evidence is a manual run and the `docker ps` output it gave. The posted text also carries a search
result (`which nothing else in the repository uses`), bookkeeping about the pull request it was split from (`which no
longer carries this commit`), and a tool footer. A maintainer reviewing the first batch kept the manual check as
written and asked for those three to go; a rewrite that replaced the output with "each replica on its own port" lost
the evidence.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Verification, a manual check and its literal output; What each paragraph
  must earn: show it, the result not the route, length), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The manual check stays literal** (`manual_check_literal_4501`). The command with
   `PG_REPLICA_TWO_PUBLISH_PORT=25434` and the output `25433->5433` and `25434->5434` are still there.
2. **No route** (`no_route_4501`). Neither "nothing else in the repository uses" nor "no longer carries".
3. **No tool footer** (`no_tool_footer`). No "Generated with" line.
4. **Short** (`prose_at_most_110_words`). At most 110 words outside fenced blocks; the posted text is 80.

## Running it

As in [the cases README](../README.md). `controls/as-posted.md` is the description as posted.
`controls/short-draft.md` is the rewrite that dropped the output. `controls/main-haiku.md` is a Haiku draft, at
effort medium, written from the same description and diff under the skill at `main` 4ef3f8c.

`SKILL.md` quotes this case's `25433->5433` output and both phrases `no_route_4501` bans, so the runs are open-book:
they show the skill's examples are followed, not that the rule carries to a pull request it does not quote.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. There are no
baselines for this case.

| Run | Manual check literal (1) | No route (2) | No footer (3) | Words (4) |
| --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes: 54 |
| Opus r2 | passes | passes | passes | passes: 54 |
| Haiku r1 | passes | passes | passes | passes: 62 |
| Haiku r2 | passes | passes | passes | passes: 90 |
| `controls/as-posted.md` | passes | fails: "nothing else in the repository uses" | fails | passes: 80 |
| `controls/short-draft.md` | fails: no command, no output | passes | passes | passes: 62 |
| `controls/main-haiku.md` | passes | fails: "Nothing else in the repository uses" | fails | fails: 136 |
