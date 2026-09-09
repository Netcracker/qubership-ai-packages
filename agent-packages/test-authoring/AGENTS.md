# Editing the test-authoring package

The skill under `.apm/skills/test-authoring/` states one rule in up to five places: the section body of `SKILL.md`,
the bucket row in §10, the checklist item in §11, the reference file of every library that restates it, and the
bullet in `README.md`. Six rounds of review of the first version found the same three defects each time, and each is
a rule that moved in one place and not the others. The rules below exist so that the next edit does not repeat them.

## What an edit to a rule owes

- **A rule moves in all of its places in the same change.** Before editing, list them: `grep -rn "§N\b"` over
  `SKILL.md` and `references/` for the section's number, and a search for the rule's own words over the same files
  and the README. An exception added in §7 that the §11 checklist still flags is the defect, not a follow-up.
- **A carve-out ships with the check that tells it from the thing it is carved out of.** "Where the relation between
  the calls is the behavior" is not a rule until the next sentence says what the reviewer looks at (the test fails
  when the relation is violated). A rule the reviewer cannot check from the diff is not a rule; §1 of the skill says
  so, and applies to the skill's own text.
- **A cross-reference names the row or the bullet by its content, never by its ordinal.** `§5's row *An assertion on
  the mock*`, not `§5's fifth row`. An insertion in the middle of a table breaks every ordinal silently.
- **A renamed term is swept out of the tables and the README, not only the prose.** The tables are what an agent
  reads first and copies. Add the old spelling to the retired-terms list in `scripts/check-skill.sh` so that it
  cannot come back.
- **A fact removed from a sentence is replaced by a fact, not by a tautology.** Dropping a figure is fine; "because
  the fix belongs there whenever the test found a real race" restates the instruction as its own reason and carries
  nothing. Cut the clause rather than fill it.
- **A new fact gets its own sentence.** It is not spliced into a sentence that already worked; a paragraph that grows
  past 30 words a sentence is split, and the paragraph is rewrapped whole, at 120 columns, so that no line is left
  short in the middle of it.
- **A reference file carries one role and names no version.** An engine file says nothing about which assertion
  prints the operands; an assertion file says nothing about how a case is named; neither names a minor version or a
  "measured on" line. Every failure message a reference quotes is measured, and the raw output with its version goes
  to `research/test-authoring/framework_output.md`.
- **The description of `SKILL.md` lists the situations that call for the skill**, not what the skill does, and stays
  under the limit `make check-descriptions` enforces.

## Before publishing an edit

1. Run `scripts/check-skill.sh --index` before the edit: it prints, per section, every line in the package that
   cites it, which is the list of places the edit has to visit. Run it again after: it fails on an ordinal
   cross-reference, a retired term, a version number in a reference, or a short line followed by a continuation.
   `make test` runs it over this package and over `final-review`, which shares the rules.
2. Run `make check-descriptions` and the markdownlint configuration the repository's CI uses.
3. For every rule the edit touched, answer in the pull request which of its five places moved, and why the others
   did not need to.
4. For every exception the edit added, name the sentence that says what the reviewer checks.
5. Run `final-review` in a fresh subagent over the diff of the skill text, with this file as the task statement. Its
   item 1 is checks 3 and 4 above, read by someone who did not write the edit.

## What is decided and not reopened

The reference files stay split by role, grouped by ecosystem. The §11 checklist stays: the trials in
`research/test-authoring/` show the models act on it. The `owe` metaphor stays. The skill carries no study figure and
no citation; a rule stands on its own detection and repair, and the evidence is in `research/test-authoring/`.
