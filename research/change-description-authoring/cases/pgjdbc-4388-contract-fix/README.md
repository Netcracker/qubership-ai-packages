# Case: pgjdbc#4388, a fix to a broken contract, shown in four lines

The input is the description of [pgjdbc/pgjdbc#4388](https://github.com/pgjdbc/pgjdbc/pull/4388) as posted, 286
words for a fix of 17 lines in one method, with the diff and the task to rewrite it. `BlobInputStream.close()` left the
stream open when the release failed; four lines of the old code (`// throws`, `// never reached`) show it. The fix
makes `read()` after a failed `close()` throw, which a reader could take for a break, but the old behavior broke
`Closeable`, so it is a fix. The posted text also names the review that found the defect, runs the test with a
`./gradlew` command, and narrates which tests fail when the fix is reverted. One test passes without the change; that
is the one fact about the tests the diff and CI do not show.

## Skill parts

- `SKILL.md`: §2 (Pull request description: the break lead and its contract exception; the shape of a small fix;
  What each paragraph must earn: show it, the result not the route, length; Verification), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The old lines are shown** (`snippet_shown_4388`). A fenced block carries `// throws` or `never reached`.
2. **No route** (`no_route_4388`). No adversarial review, Codex, "found by", or the review's other findings
   (`findings`).
3. **No break lead** (`no_break_lead_4388`). The first block does not announce a break.
4. **No test command** (`no_test_command`).
5. **No test narration** (`no_test_narration`). No sentence on what fails when the fix is reverted.
6. **The test that passes without the change is named** (`passes_without_named_4388`, read).
   `closeReportsAFailedRelease` passes either way; read that the description says so, and says nothing of the other
   two tests.
7. **Short** (`prose_at_most_220_words`). At most 220 words outside fenced blocks.
8. **No tool footer** (`no_tool_footer`). The posted text ends in a "Generated with" line; the rewrite drops it.

## Running it

As in [the cases README](../README.md). `controls/as-posted.md` is the description as posted.
`controls/short-draft.md` is a rewrite that told the defect in prose and dropped the snippet. `controls/main-haiku.md`
is a Haiku draft, at effort medium, written under the skill at `main` 4ef3f8c; it leads with a break.

`SKILL.md` quotes the `// throws` and `// never reached` markers `snippet_shown_4388` looks for, so the runs are
open-book: they show the skill's example is followed, not that the rule carries to a pull request it does not quote.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. There are no
baselines for this case.

| Run | Old lines (1) | No route (2) | No break lead (3) | No command (4) | No narration (5) | Passes without (6) | Words (7) | No footer (8) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes | passes | passes | passes: 176 | passes |
| Opus r2 | passes | passes | passes | passes | passes | passes | passes: 170 | passes |
| Haiku r1 | passes | passes | passes | passes | passes | passes | passes: 193 | passes |
| Haiku r2 | passes | fails: "The other findings on `BlobInputStream`" | passes | passes | passes | passes | passes: 208 | passes |
| `controls/as-posted.md` | passes | fails: "Found by" | passes | fails | fails | fails: names the other two tests | fails: 255 | fails |
| `controls/short-draft.md` | fails: told in prose | passes | passes | passes | passes | fails: not named | passes: 81 | passes |
| `controls/main-haiku.md` | fails: no snippet | fails: "adversarial" | fails: "## Breaking changes" | fails | fails | fails: names the other two tests | fails: 373 | passes |

Haiku r2 still points at the review's other findings; Haiku r1 only says other problems are out of scope.
