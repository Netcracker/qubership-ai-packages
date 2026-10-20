# Case: pgjdbc#4370, a description a maintainer called verbose

The input is the description of [pgjdbc/pgjdbc#4370](https://github.com/pgjdbc/pgjdbc/pull/4370) as posted, about
730 words of prose by `check.py`'s count for a fix in one class, with the task to rewrite it. A version that keeps
every fact a reviewer decides on is about 420 words (`claude-skills-research/change-description-authoring/2026-09-11-pgjdbc-review-window-corpus.md`).
The case tests the length signal and the verification rules #109 and #113 added: the property the tests establish
rather than their construction, which tests are new, and the coverage a narrowed test loses. Headings stay, because
the description carries a fenced command and two overlapping pull requests.

## Skill parts

- `SKILL.md`: §2 (Pull request description: headings; What each paragraph must earn, length; Verification), §5
  (links), §7a
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Shorter** (`prose_at_most_500_words`). At most 500 words outside fenced blocks. The skill's signal is about 400;
   the margin leaves room for the outcome lines it excludes from the count.
2. **Facts kept** (`facts_kept_4370`). `SocketTimeoutException`, `#4358`, `#4359`, `75 ms`, `149 ms`, and
   `EOFException` are still there.
3. **The new test is marked new** (`new_test_marked`).
4. **The coverage lost is named** (`coverage_lost_named`, read). One sentence says that no test now limits how many
   reads a long discard makes, or that `skipDoesNotFallBackToReadingByteByByte` is dropped.
5. **No construction in verification** (`no_construction_in_verification`). The verification slot does not list the
   counts (`0, -1, -2`, `Long.MIN_VALUE`, `Long.MAX_VALUE`), the 8192-byte buffer, or "one byte short".
6. **Headings stay** (`headings_present`). The negative control for "headings are the exception".
7. **Links at the merge base** (`links_at_merge_base`). Every link into pgjdbc code is at
   `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7`.
8. **No narrated command** (`no_narrated_command`). No sentence beside the `./gradlew` command says what the command
   runs, which the command names already.

## Running it

As in [the cases README](../README.md). `controls/trimmed-wrong.md` is `opus/result.md` with the headings removed,
the links moved to `master`, `(new)` dropped, the sentence on the lost coverage and the `#4359` bullet deleted, the
two timings replaced by "half the time", and "The command runs both test classes." added after the command.

## Results

Runs of 2026-10-20 on the skill whose tree id is in `<model>/skill-tree` (`e4c81d96`, `main` at 2cee8a6), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Prose words (1) | Facts (2) | New marked (3) | Coverage lost (4) | No construction (5) | Headings (6) | Links (7) | Command (8) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | fails: 732 | passes | passes | passes | fails: the count list | passes | passes | passes |
| Opus r2 | fails: 697 | passes | passes | passes | fails: the count list | passes | passes | passes |
| Haiku r1 | fails: 762 | passes | passes | passes | fails | passes | passes | passes |
| Haiku r2 | fails: 648 | passes | passes | passes | fails | passes | passes | passes |
| Opus baseline | fails: 721 | passes | passes | passes | fails | passes | passes | passes |
| Haiku baseline | fails: 766 | passes | passes | passes | fails | passes | passes | passes |
| `controls/trimmed-wrong.md` | fails: 671 | fails | fails | fails | fails | fails | fails | fails |

Without the "User-visible changes" lines, which the skill leaves out of the count, Opus wrote about 671 words in both
runs: the length signal did not shorten the rewrite, and every run kept the case list of the new test.
