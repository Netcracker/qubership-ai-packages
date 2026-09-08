# Research title

Synthesize the Pass 2 findings into a candidate rule set for change descriptions, organized by reader

## Goal

Produce a synthesis document, not a skill. A later session writes the repository-independent skill from this document; a
house style (prefix vocabulary, template, trailer set) is a later, per-repository overlay. The document has to let that
session write every rule with its source attached and its reader named, without reopening the research.

Use `phase2_result.md` as the main source and `phase1_result.md` for the reader table and the candidate inventory. Where
a Pass 2 claim about a source was checked against the primary source during synthesis and found inexact, the synthesis
carries the corrected claim and says what was corrected.

## The readers

The five readers are fixed. Every rule names the reader whose need it exists for, listed first, and any other reader it
also serves.

| Reader | Situation |
| --- | --- |
| R1 Reviewing maintainer | Reading the change now, deciding whether to approve it |
| R2 Archaeologist | Running `git blame` or `git log` years later, holding a line of code |
| R3 On-call or support engineer | During an incident, holding a stack trace or a log line |
| R4 Upgrading user | Reading release notes before upgrading |
| R5 Release manager or backporter | Deciding what to cherry-pick into a maintenance branch |

## Required output

A Markdown document, `phase3_result.md`, under 6000 words, with these sections in this order.

1. **Reader table.** One row per reader: the artifact they open, what they read first, the question they bring, the
   sources, and whether the claim is measured or asserted. Keep "asserted" where Pass 2 left it.
2. **Artifacts and slots.** For each artifact (commit subject, commit body, trailers, PR title, PR body, changelog
   entry): the slots in order; what each slot owes; which reader it serves; and the test for whether a sentence belongs,
   phrased as the reader and the question it answers. Every slot carries its sources.
3. **Greppability.** The trailer and identifier rules that make text searchable: issue references, `Fixes:` and its
   relatives, error text quoted verbatim, class and method names, version numbers. State which tool, if any, consumes
   each trailer, and which reader benefits.
4. **Squash-merge repositories.** The rules for a repository where the PR title seeds the commit subject and the PR body
   seeds or becomes the commit body. Mark each rule cited or derived from platform mechanics. Include what the agent has
   to detect and the default when detection fails.
5. **The changelog entry as the on-call reader's artifact.** The order of its parts, the reader each part serves, and
   what Pass 2 found no project doing (recording the introducing version in the entry).
6. **Workflow gating.** The rules that are bound to a workflow, the precondition under which each applies, the
   false-positive risk elsewhere, and the principle that transfers when the mechanism does not.
7. **Rules no reader needs.** The prescriptions that serve a tool or a process rather than a reader, with the decision
   to mention as a house-style option or to drop.
8. **Conflicts and how they were decided.** Each contradiction between sources, both positions with their sources, the
   reader whose need won, why, and whether the losing reader is harmed.
9. **Anti-patterns.** Each anti-pattern a source names, the source, and the reader it fails.
10. **Evidence map.** Which rules rest on measured evidence and which on assertion, so the skill does not present an
    asserted rule as measured. Name the studies and their samples once, here.
11. **Test of the rule set.** Apply the slot tests to a few real public changes drawn from different workflows (an
    email-patch project, a back-patching project, a squash-merge repository, a hand-written changelog). For each: which
    slots are present, which are absent, and whether the test told the reader something the raw text did not. The
    purpose is to check that the tests discriminate, not to grade the authors.
12. **Load-bearing versus refinement.** Which rules a compression pass drops first.
13. **What the skill-writing session should be told.** What to do, and what not to do: no wording rules, no reopening
    the settled conflicts, no promotion of asserted rules to measured, no house style in the core.

## Constraints

- Every rule carries its sources, by name and URL. A rule derived from mechanics rather than from a source says
  "derived".
- Structural rules only. Wording (tense, mood, length, punctuation, dialect, hedging) is owned by
  `english-developer-style` and is out of scope; where a source's rule is wording, leave it out and say so once.
- Do not sample one repository's authors as exemplars. The test in section 11 checks the tests, not the authors, and
  draws on several projects.
- Where sources disagree, say which reader's need won and why. Do not average.
- Where Pass 2 said "asserted" or "inferred", keep that label.
