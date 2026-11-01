# Case: pgjdbc#4501, a one-line fix checked by hand

The input is the description of [pgjdbc/pgjdbc#4501](https://github.com/pgjdbc/pgjdbc/pull/4501) as posted, 80 words
for a one-line fix in a shell script, with the diff and the task to rewrite it. No test covers the script; the
description's evidence is a manual run and the `docker ps` output it gave. The posted text also carries a search
result (`which nothing else in the repository uses`), bookkeeping about the pull request it was split from (`which no
longer carries this commit`), and a tool footer. A maintainer reviewing the first batch kept the manual check as
written and asked for those three to go; a rewrite that replaced the output with "each replica on its own port" lost
the evidence.

## Skill parts

- `SKILL.md`: §2 (Pull request description: the What slot; Verification, a manual check and its literal output; What
  each paragraph must earn: show it, the result not the route, length), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The manual check stays literal** (`manual_check_literal_4501`). The command with
   `PG_REPLICA_TWO_PUBLISH_PORT=25434` and the output `25433->5433` and `25434->5434` are still there.
2. **No route** (`no_route_4501`). Neither "nothing else in the repository uses" nor "no longer carries".
3. **No tool footer** (`no_tool_footer`). No "Generated with" line.
4. **Short** (`prose_at_most_110_words`). At most 110 words outside fenced blocks; the posted text is 80.
5. **The change is named** (`change_named_4501`). Apart from the command, the description names the variable the
   script reads after the change, `PG_REPLICA_TWO_PUBLISH_PORT`; the check does not count the name where `=` follows
   it. A description made of the "Checked by" paragraph alone passes checks 1 to 4 and fails this one. A bare name
   inside that paragraph passes too; only reading tells whether such a description says what the script now reads.

## Running it

As in [the cases README](../README.md). `controls/as-posted.md` is the description as posted.
`controls/short-draft.md` is the rewrite that dropped the output. `controls/main-haiku.md` is a Haiku draft, at
effort medium, written from the same description and diff under the skill at `main` 4ef3f8c.

`SKILL.md` quotes this case's `25433->5433` output and both phrases `no_route_4501` bans, so the runs are open-book:
they show the skill's examples are followed, not that the rule carries to a pull request it does not quote.

`controls/checked-by-only.md` is the "Checked by" paragraph alone.

`controls/opus-one-paragraph.md` is `opus/result.md` with its two paragraphs joined into one.

`controls/tested-by-two-paragraphs.md` is the verification as two paragraphs. These two controls keep the layout fix
from regressing.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. There are no
baselines for this case.

| Run | Manual check literal (1) | No route (2) | No footer (3) | Words (4) | Change named (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes: 54 | passes |
| Opus r2 | passes | passes | passes | passes: 54 | passes |
| Haiku r1 | passes | passes | passes | passes: 62 | passes |
| Haiku r2 | passes | passes | passes | passes: 90 | passes |
| `controls/as-posted.md` | passes | fails: "nothing else in the repository uses" | fails | passes: 80 | passes |
| `controls/short-draft.md` | fails: no command, no output | passes | passes | passes: 62 | passes |
| `controls/main-haiku.md` | passes | fails: "Nothing else in the repository uses" | fails | fails: 136 | passes |
| `controls/checked-by-only.md` | passes | passes | passes | passes: 15 | fails: name only in the command |
| `controls/opus-one-paragraph.md` | passes | passes | passes | passes: 54 | passes |
| `controls/tested-by-two-paragraphs.md` | passes | passes | passes | passes: 17 | fails: name only in the command |

Tree `9fe02a7c` (2026-11-06) marks the outcome block with `**User-visible changes.**` and `**Not changed.**`, keeps each
outcome on one line that is not wrapped, says a lead-in opens its paragraph, and says what a description that becomes a
commit body keeps. This case was not re-run on it: its Opus results carry no outcome block, any `**Scope.**` lead-in in
them already opens its paragraph, and no check reads either. The rows stand for the trees they ran on.
