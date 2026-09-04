# Research title

Synthesize the findings of passes 1 to 3 into a candidate rule set for documentation pages, organized by reader

## Goal

Produce a synthesis document, not a skill. A later session writes the repository-independent skill from this document;
a house style (a particular field order, a page template, a heading vocabulary) is a per-repository overlay. The
document has to let that session write every rule with its source attached, its reader named, and its basis labeled,
without reopening the research.

Use `phase3_result.md` for the reader model, the option entry, placement, the diff scan list, the troubleshooter's
path, and the structure heuristics; `phase2_result.md` for the rules about what a page may claim, the conflicts already
resolved, the three-bucket split, and the baseline audit; `phase1_result.md` for the candidate inventory. Where a claim
about a source was checked against the primary source during synthesis and found inexact, the synthesis carries the
corrected claim and says what was corrected.

## The readers

The seven readers are fixed by pass 3. Every rule names the reader whose need it exists for, listed first, and any other
reader it also serves.

| Reader | Situation |
| --- | --- |
| D1 Evaluator | Deciding whether to adopt; holds a requirement |
| D2 First-time integrator | Has decided; nothing runs yet |
| D3 Task-doer | Has a working setup and a goal in the product's terms |
| D4 Configurer | Tuning or hardening a running system; holds a configuration and a requirement |
| D5 Troubleshooter | Something failed; holds an error message, an exception, a log line, or a wrong result |
| D6 Upgrader | Moving between two versions |
| D7 Contributor | Wants to change the product; holds a clone and a build |

## Required output

A Markdown document, `phase4_result.md`, under 6000 words, with these sections in this order.

1. **Reader table.** One row per reader: what they hold, what they open, how they enter, what they ask, what they read
   first and where they stop, the sources, and whether the row is studied, stated policy, or asserted. Keep the
   labels pass 3 assigned.
2. **The section and its slots.** The four slots of a section, the test for whether a sentence belongs (the reader and
   the question it answers), and the first-paragraph rules, with the evidence pass 2 attached to them.
3. **The option entry.** The field list with the fields every source carries, the fields a minority carries, the order
   as a house default, the rule for an interaction between options, and the fields that generated reference text
   cannot supply. Every field carries its sources.
4. **Genres and their failure modes.** The weakened genre rule from pass 2, the genre table with the reader each genre
   serves, and the two genres pass 3 added or sharpened: troubleshooting and the migration guide at the D6 boundary.
5. **What a page may claim.** The specification-versus-implementation rule, history and its three homes, identifiers,
   numbers, quoted errors, fenced examples and doctest harnesses, and headings as anchors, each with its pass 2
   sources and basis.
6. **Placement and ownership.** Which copy is the record, what a derived copy carries, where a new section goes, the
   README boundary, and the ordering conventions, with the projects that state each.
7. **What a change owes the documentation.** The eight-item scan list from pass 3 with each item's basis (named or
   inferred), the mechanisms projects use to enforce it, and the reader and page each item serves.
8. **The troubleshooter's path.** The three shapes that make a page findable by an error, what each requires of the
   code, and the default when the code emits neither a code nor a URL.
9. **Structure heuristics.** Table versus list versus prose, heading and page granularity, and progressive disclosure,
   each with its basis and with what remains unmeasured.
10. **The three parties that check a page.** The sweep oracle, the linter or CI job, and the reviewer, with the tools
    named where one exists, from pass 2.
11. **Editing and comparing.** The growth budget, the prose-pass versus structural-revision distinction the trial
    needed, released-entry immutability, and the comparison protocol with the finding taxonomy, from pass 2 and the
    trial.
12. **Conflicts and how they were decided.** Each contradiction between sources, both positions with their sources,
    the reader whose need won, and whether the losing reader is harmed.
13. **Evidence map.** Which rules rest on measured evidence, which on stated policy, which on inference from
    mechanics, and which on assertion. Name the studies and their samples once, here, and list every correction made
    during the verification of passes 2 and 3 against primary sources.
14. **Test of the rule set.** The trial on a real branch (a JDBC driver adding two connection properties, a system
    property and new error messages), with what the reader questions and the scan list demanded, what the pre-trial
    documentation supplied, and what two runs of the skill produced. Then the three pages and two pull requests pass 3
    tested. The purpose is to check that the tests discriminate, not to grade anyone.
15. **Load-bearing versus refinement.** Which rules a compression pass drops first.
16. **What the skill-writing session should be told.** What to do and what not to do: no wording rules, no re-derived
    changelog entry, no promotion of asserted rows to studied, no house field order presented as a rule, no research
    provenance in the skill body.

## Constraints

- Every rule carries its sources, by name and URL. A rule derived from mechanics rather than from a source says
  "derived"; a rule from one repository's practice says "asserted".
- Structural rules only. Wording is owned by `english-developer-style`; the changelog entry and the pull request
  description by `change-description-authoring`. Where a source's rule is wording, leave it out and say so once.
- Do not reopen the conflicts pass 2 resolved: one primary purpose per section, version-marker retention on reference
  pages, no changelog inside a README, the normative distinction without uppercase keywords, released entries as
  immutable except for factual corrections, minimalism for tutorials and how-tos against completeness for reference.
- Where sources disagree, say which reader's need won and why. Do not average.
- Where pass 2 or pass 3 said "asserted", "stated policy", "inferred", or "derived", keep that label.
- Do not sample one project's authors as exemplars. The tests in section 14 check the tests, not the authors.
