# Case: pgjdbc#4424, a change with no tests

The input is the diff of [pgjdbc/pgjdbc#4424](https://github.com/pgjdbc/pgjdbc/pull/4424), which rewrites the JUnit 4
instructions in `TESTING.md` and the test items of the pull request template, with the commit message and the checks
its author ran; the posted description is withheld. The first descriptions of this change had no verification,
justified as "documentation only", and the description that was posted links the edited sections at the merge base.
The case tests the rules #109 added: verification for a change with no tests, headings as the exception, a section
cited by its heading text, and links at the commit that has the content.

## Skill parts

- `SKILL.md`: §2 (Pull request description: headings; Verification, "A change with no tests still fills the slot"),
  §5 (Identifiers: a section of a document, links), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Verification names the checks** (`no_test_verification_named`). The description says how its two claims about
   the code were checked: the `git grep` that finds no JUnit 4 test under `pgjdbc/src/test`, and the
   `pgjdbc/build.gradle.kts` lines that reject `junit:junit`. "Documentation only" alone fails.
2. **No headings** (`no_headings`). The description has no fenced command, names no several tests, and has no stacked
   pull request, so it is prose.
3. **A section cited by its heading text** (`section_heading_text`). `TESTING.md` section 5 appears as
   `Extending the test suite with new tests`, not as `§5` alone.
4. **The edited sections link at the head** (`changed_files_link_at_head`). The description links the rendered
   `TESTING.md` section the change edits, and every link into `TESTING.md` or the template is at the head commit
   `e6bf0181251063d4cb2fc8324e28fc4f6cde1313`, except a link to `#new-feature-submissions`, a section only the merge
   base has, which is at the merge base.
5. **Unchanged code links at the merge base** (`unchanged_code_link_at_merge_base`). The `build.gradle.kts` lines are
   linked at `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7` with a line range.

## Running it

As in [the cases README](../README.md). `controls/posted.md` is the description as posted on GitHub;
`controls/documentation-only.md` is `haiku/result-2.md` with its verification paragraph replaced by "Documentation
only; no code changes."

## Results

Runs of 2026-10-20 on the skill whose tree id is in `<model>/skill-tree` (`e4c81d96`, `main` at 2cee8a6), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Verification (1) | No headings (2) | Heading text (3) | Edited sections at head (4) | Unchanged code at merge base (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | passes | passes |
| Haiku r1 | passes | passes | passes | fails: the edited section is not linked | passes |
| Haiku r2 | passes | passes | passes | passes | passes |
| Opus baseline | passes | fails: three headings | fails | passes | passes |
| Haiku baseline | passes | passes | fails | fails: no link | fails: no link |
| `controls/posted.md` | passes | passes | passes | fails: four links at the merge base | passes |
| `controls/documentation-only.md` | fails | passes | passes | passes | fails |

Opus r2 links the removed `#new-feature-submissions` section at the merge base and the new `#tests-and-style` at the
head, which is what the rule asks.
