# Documentation page authoring: research

An editorial pipeline that collects evidence for a repository-independent skill on **documentation pages**: README
files, reference pages, option and configuration references, feature pages and how-to guides, troubleshooting pages,
migration guides. This folder is the audit trail; the skill itself is written from the synthesis and kept canonical in
its package.

The pipeline reuses the method of [`english-developer-style`](../english-developer-style/) and
[`change-description-authoring`](../change-description-authoring/). The unit of evaluation is a rule an agent can apply
without the author present: stated once, with its rationale, the genre it applies to, and the way a reviewer detects a
violation. Two properties weigh more than they do in a style guide, because the consumer works inside a repository:
whether a violation is detectable without reading the whole page, and whether a claim can be checked against the code
it describes.

Wording is out of scope. Sentence-level style is owned by `english-developer-style`; the changelog entry and the pull
request description are owned by `change-description-authoring`. Every phase keeps only the rules above the sentence.

## Method

| Step | Artifacts | What happened |
| --- | --- | --- |
| Seed | the *Baseline skill* section of `phase1_prompt.md` | A skill written from one repository's documentation set and generalized by hand. Its own flagged weaknesses: the genre table, the claim about how readers enter a page, and nothing about testable examples. |
| Phase 1: shortlist | `phase1_prompt.md`, `phase1_result.md` | Deep-research pass over genre frameworks (Diátaxis), style-guide structure chapters, project contribution guides, verifiability tooling (doctest families), technical-communication research, review rubrics, and agent skills. Output: 25 candidates, a shortlist of 9, and the finding that no single source covers the domain. |
| Phase 2: rules | `phase2_prompt.md`, `phase2_result.md` | Per shortlisted source: disposition, evidence basis, false-positive risk. Output: 35 extracted rules with detection and repair, worked examples, the resolved conflicts, the three-bucket split (agent, linter, sweep oracle), and an audit of the baseline. |
| Phase 3: readers | `phase3_prompt.md`, `phase3_result.md` | A targeted pass on what phases 1 and 2 never asked: which reader a section exists for and how they enter, the shape of an option entry, where a fact lives when a docs set carries it in several places, what a change owes the documentation, and how a troubleshooter finds a page by the error text. |
| Phase 4: synthesis | `phase4_prompt.md`, `phase4_result.md` | Synthesis document, not a skill: reader table, slots per genre and per option entry, the diff scan list, placement rules, conflicts and their resolution, evidence map. The skill is written from it. |

Phases 1 and 2 were executed as manual deep-research sessions on 2026-08-25; the prompts are what was pasted in, and
the result files are what came back, unedited. A first skill was written from the phase-2 result the same day and
tried on a real branch that added connection properties, a system property, and new error messages to a JDBC driver.
The trial is what motivated phase 3.

## Files

```text
phase1_prompt.md, phase1_result.md     shortlist of sources; the baseline skill as seed
phase2_prompt.md, phase2_result.md     extracted rules, conflicts resolved, three-bucket split, baseline audit
phase3_prompt.md, phase3_result.md     readers by situation, option entry shape, placement, what a change owes the docs
phase4_prompt.md, phase4_result.md     synthesis: candidate rule set with sources
phase4_verification.md                 the three verification reports the synthesis folded in
```

The phase prompts use one H1 and H2 sections; the result files are pasted unedited and are excluded from markdownlint
by `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, as the other research directories are.

## Findings

- No single source covers page structure and content above the sentence. Diátaxis classifies pages by the job they do
  but says nothing about whether a page is true; editorial style guides treat documentation as writing; standards
  bodies have the only mature discipline for separating a contract from an implementation; the research literature
  supplies the only measured claims but no authoring rules.
- The baseline's central rule, that a page states the specification rather than the current implementation, survives
  the audit and is the load-bearing contribution. It maps onto the normative versus informative distinction of
  RFC 2119 and RFC 8174, minus the uppercase keywords, which OASIS tells non-standards documents to avoid.
- "One page, one genre" does not survive contact with a repository: a README and a migration guide are mixtures, and
  Diátaxis calls itself a guide, not a plan. The rule is weakened to one primary purpose per section; the per-genre
  failure modes stay as detection heuristics.
- Executable examples are the one mechanism that turns a fenced code block from an unchecked claim into a checked one.
  Where no doctest harness covers a file, the fence is prose that rots in silence.
- Outdated code-element references are common enough to be a named research target; research tools that diff prose
  against source mostly do not work outside narrow slices, so an agent reading the page and the source together is the
  practical substitute, not a stopgap.
- Intra-documentation anchor rot is unstudied. The heading-as-anchor rule rests on how links work, not on a number.
- Phases 1 and 2 produced no reader model. The trial on a real branch showed that the rules say how a sentence may be
  wrong but not which reader a section exists for, where in the set that reader looks, or what a diff owes the
  documentation. Phase 3 carries a candidate table of seven readers (evaluator, first-time integrator, task-doer,
  configurer, troubleshooter, upgrader, contributor) and the three procedures the trial needed.
- Phase 3 confirmed all seven reader rows as an asserted partition, with studied support for how common two of the
  situations are: the troubleshooter searching an error string and the integrator learning an API. The option entry
  converges on four fields every source carries (name, type and values, default, what it controls); the fields most
  often missing are the error at the limit and the version. OpenStack's `DocImpact` trigger list is the clearest
  statement of what a change owes the documentation, and the two pull requests tested showed the scan list
  discriminates.
- The trial on the JDBC branch, run twice and judged blind, went from 9 of 14 assertions with the phase-2 rules alone
  to 13 of 14 with the reader table, the option entry, the scan list, and the placement rules added.

## Status

All four phases complete. Phases 1 to 3 were manual deep-research sessions (phases 1 and 2 on 2026-08-25, phase 3 on
2026-09-03); the phase-4 synthesis was run by the coding agent over the three results, after three parallel
verification passes over the papers, the project policies, and the pull requests and issues they cite, with the
corrections carried into the synthesis and listed in its section 13 (the reports are in `phase4_verification.md`).
The synthesis runs to about 6,600 words including its tables. It was the input for the skill,
which lives in the APM package [`docs-page-authoring`](../../agent-packages/docs-page-authoring/) and is kept
canonical there, not duplicated here.
