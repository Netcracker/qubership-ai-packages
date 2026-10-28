# Case: pgjdbc#4370, a description a maintainer called verbose

The input is the description of [pgjdbc/pgjdbc#4370](https://github.com/pgjdbc/pgjdbc/pull/4370) as posted, about 730
words of prose by `check.py`'s count for a fix in one class, with the task to rewrite it. A version that keeps every
fact a reviewer decides on is about 420 words
(`claude-skills-research/change-description-authoring/2026-09-11-pgjdbc-review-window-corpus.md`). The case tests the
length signal and the verification rules: the description carries what the diff and CI do not show, so no test
construction, no mark on the new test, no command that runs tests CI runs, and no narrated failure without the change,
while the coverage a narrowed test loses stays.

## Skill parts

- `SKILL.md`: §2 (Pull request description: headings; What each paragraph must earn, length, the result not the
  route; Verification), §5 (links), §7a
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Shorter** (`prose_at_most_500_words`). At most 500 words outside fenced blocks. The skill now asks a fix in one class
   for about 250 words of prose; the check keeps the earlier 500 so the runs before and after compare.
2. **Facts kept** (`facts_kept_4370`). `SocketTimeoutException`, `#4358`, `#4359`, `75 ms`, `149 ms`, and
   `EOFException` are still there.
3. **No test is marked new** (`new_test_not_marked`). The diff shows the new file.
4. **The coverage lost is named** (`coverage_lost_named`, read). One sentence says that no test now limits how many
   reads a long discard makes, or that `skipDoesNotFallBackToReadingByteByByte` is dropped.
5. **No construction in verification** (`no_construction_in_verification`). The verification slot does not list the
   counts (`0, -1, -2`, `Long.MIN_VALUE`, `Long.MAX_VALUE`), the 8192-byte buffer, or "one byte short".
6. **Links at the merge base** (`links_at_merge_base`). Every link into pgjdbc code is at
   `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7`.
7. **No test command** (`no_test_command`). No `./gradlew … test` block: CI runs the tests.
8. **No test narration** (`no_test_narration`). No sentence counts the cases that fail against the old code or the
   tests that pass.

Headings are no longer checked: the skill allows them for the two overlapping pull requests and no longer requires
them for a fenced command.

## Running it

As in [the cases README](../README.md). `controls/trimmed-wrong.md` is `controls/main-opus.md` with the headings
removed, the links moved to `master`, `(new)` dropped, the sentence on the lost coverage and the `#4359` bullet deleted,
the two timings replaced by "half the time", and "The command runs both test classes." added after the command.
`controls/main-opus.md` is the Opus result of 2026-10-20, written when the skill asked for the new test to be marked and
for the command.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Prose words (1) | Facts (2) | New not marked (3) | Coverage lost (4) | No construction (5) | Links (6) | No command (7) | No narration (8) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | fails: 541 | passes | passes | passes | passes | passes | passes | passes |
| Opus r2 | fails: 658 | passes | passes | passes | fails: "the counts -1, -2, and `Long.MIN_VALUE`" | passes | passes | fails: "5 of the 15 cases fail" |
| Haiku r1 | fails: 585 | passes | passes | passes | fails: "the counts -1, -2, and `Long.MIN_VALUE`" | passes (no links) | passes | fails: "fails five of its 15 cases" |
| Haiku r2 | fails: 641 | passes | passes | passes | fails: "the counts -1, -2, and `Long.MIN_VALUE`" | passes | passes | fails: "Five of the fifteen cases … fail" |
| Opus baseline | fails: 721 | passes | fails: "is new" | passes | fails | passes | fails | fails: "5 of its 15 cases fail" |
| Haiku baseline | fails: 766 | passes | fails: "(new)" | passes | fails | passes | fails | fails: "5 of its 15 cases fail" |
| `controls/trimmed-wrong.md` | fails: 677 | fails | passes | fails | fails | fails | fails | fails |
| `controls/main-opus.md` | fails: 732 | passes | fails: "(new)" | passes | fails | passes | fails | fails: "Its cases cover" |

The script passes the Haiku narration check by its regular expression; the spelled-out "five of its 15 cases" is the
same sentence the check rules out. The new runs no longer mark the test new or give the command, but all four stay
above 500 words (Opus r1 comes closest, at 541) and three of four still list the counts and the failing cases.
