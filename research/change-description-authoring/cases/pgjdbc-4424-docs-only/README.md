# Case: pgjdbc#4424, a change with no tests

The input is the diff of [pgjdbc/pgjdbc#4424](https://github.com/pgjdbc/pgjdbc/pull/4424), which rewrites the JUnit 4
instructions in `TESTING.md` and the test items of the pull request template, with the commit message and the checks
its author ran; the posted description is withheld. The first descriptions of this change had no verification,
justified as "documentation only", and the description that was posted links the edited sections at the merge base.
The case tests the rules #109 added: verification for a change with no tests, headings as the exception, a section
cited by its heading text, and links at the commit that has the content.

## Skill parts

- `SKILL.md`: §2 (Pull request description: headings and lead-in labels; Verification, "A change with no tests still
  fills the slot"), §5 (Identifiers: a section of a document, links), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Verification names the checks** (`no_test_verification_named`). The description says how its two claims about
   the code were checked: the `git grep` that finds no JUnit 4 test under `pgjdbc/src/test`, and the
   `pgjdbc/build.gradle.kts` lines that reject `junit:junit`. "Documentation only" alone fails.
2. **No headings** (`no_headings`). The repository's template is not used for this description, so it is prose.
3. **A section cited by its heading text** (`section_heading_text`). `TESTING.md` section 5 appears as
   `Extending the test suite with new tests`, not as `§5` alone.
4. **The edited sections link at the head** (`changed_files_link_at_head`). The description links the rendered
   `TESTING.md` section the change edits, and every link into `TESTING.md` or the template is at the head commit
   `e6bf0181251063d4cb2fc8324e28fc4f6cde1313`, except a link to `#new-feature-submissions`, a section only the merge
   base has, which is at the merge base.
5. **Unchanged code links at the merge base** (`unchanged_code_link_at_merge_base`). The `build.gradle.kts` lines are
   linked at `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7` with a line range.
6. **No lead-in labels** (`no_lead_in_labels`). The change has no break, no deliberate gap, no related pull request,
   and no question for a maintainer, so neither `**Breaking changes.**` nor `**Scope.**` appears. This is the noise
   input for the lead-in rule that `pgjdbc-4370-verbose` check 9 tests where the label is owed.

## Running it

As in [the cases README](../README.md). `controls/posted.md` is the description as posted on GitHub;
`controls/documentation-only.md` is `haiku/result-2.md` with its verification paragraph replaced by "Documentation
only; no code changes." `controls/empty-scope-label.md` is `opus/result.md` as committed before 2026-11-01 with a
`**Scope.**` paragraph added that names no gap; it fails check 6, which no result fails.

## Results

Tree `27b2445d` adds the `Implements:` and `Defers:` trailers to §2 (Scope), the §5 trailer table, and the §8
checklist, for a repository whose decision records number their rules. This input has no decision records, so the
change does not reach this case, and the results below stand for `27b2445d` as they stand for the tree before it.

Opus r1 and r2 were re-run on 2026-11-01 on tree `c99e1c77`, graded by reading. That tree differs from this change's in
places this case does not reach: a widening of the §2 translation rule to a comment the diff removes or rewrites, left
out because it changed no output on a description of pgjdbc/pgjdbc#4412; two example template headings since dropped
from one sentence; and where the break lead-in and a Scope lead-in under a template go, which needs a break or a
template with headings, and this case has neither. Both pass every check, check 6 included, at 255 and 242 words. The
other rows stand for the trees they ran on.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Verification (1) | No headings (2) | Heading text (3) | Edited sections at head (4) | Unchanged code at merge base (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | passes | passes |
| Haiku r1, r2 | passes | passes | passes | passes | passes |
| Opus baseline | passes | fails: three headings | fails | passes | passes |
| Haiku baseline | passes | passes | fails | fails: no link | fails: no link |
| `controls/posted.md` | passes | passes | passes | fails: four links at the merge base | passes |
| `controls/documentation-only.md` | fails | passes | passes | passes | fails |

Opus r2 links the removed `#new-feature-submissions` section at the merge base and the new `#tests-and-style` at the
head, which is what the rule asks.

Tree `9fe02a7c` (2026-11-06) marks the outcome block with `**User-visible changes.**` and `**Not changed.**`, keeps each
outcome on one line that is not wrapped, says a lead-in opens its paragraph, and says what a description that becomes a
commit body keeps. This case was not re-run on it: its Opus results carry no outcome block, any `**Scope.**` lead-in in
them already opens its paragraph, and no check reads either. The rows stand for the trees they ran on.
