# Change description authoring: research

A four-step editorial pipeline that collects evidence for a repository-independent skill on **change descriptions**:
the commit subject and body, the pull request title and description, and the changelog or release-note entry. This
folder is the audit trail; the skill itself is written in a later session from the phase-3 synthesis.

The pipeline reuses the method of [`english-developer-style`](../english-developer-style/) and
[`docs-page-authoring`](../docs-page-authoring/). What is different here is the unit of evaluation. The question is not
which style guide is popular or best, but **what each reader needs** and which parts of which sources supply it. Five
readers are fixed before the first search and carried through every phase:

| Reader | Situation |
| --- | --- |
| R1 Reviewing maintainer | Reading the change now, deciding whether to approve it |
| R2 Archaeologist | Running `git blame` or `git log` years later, holding a line of code |
| R3 On-call or support engineer | During an incident, holding a stack trace or a log line |
| R4 Upgrading user | Reading release notes before upgrading |
| R5 Release manager or backporter | Deciding what to cherry-pick into a maintenance branch |

Wording is out of scope. Sentence-level style is owned by `english-developer-style`, so every phase separates
structural rules (what goes where, in what order, with which identifiers) from wording rules and keeps only the
structural ones.

## Method

| Step | Artifacts | What happened |
| --- | --- | --- |
| Seed | the *Baseline* section of `phase1_prompt.md` | The structural part of the commit, PR, and changelog modules of `english-developer-style`, with wording removed. |
| Phase 1: shortlist | `phase1_prompt.md`, `phase1_result.md` | Deep-research prompt seeded with project guides (kernel, git, PostgreSQL, OpenStack, Google, Kubernetes, Rust, Go, Mozilla), essays, formats (Conventional Commits, Keep a Changelog), platform behavior, and the empirical literature. Output: reader table, candidate inventory, shortlist. |
| Phase 2: deep evaluation | `phase2_prompt.md`, `phase2_result.md` | Per source: what it prescribes per reader, what it prescribes that no reader needs, where sources contradict and which reader decides, and the false-positive risk outside the home workflow. |
| Phase 3: synthesis | `phase3_prompt.md`, `phase3_result.md` | Synthesis document, not a skill: reader table, slots per artifact, trailer and identifier rules, squash-merge rules, the changelog as the on-call artifact, anti-patterns with the reader each fails. Every rule carries its sources. |

Phases 1 and 2 were executed as manual deep-research sessions on 2026-09-02; the prompts here are what was pasted in,
and the result files are what came back, unedited. Phase 3 was run by the coding agent over the phase-2 result. Before
writing it, the agent checked the Pass 2 quotes and numbers against the primary sources (three parallel verification
passes over the papers, the project guides, and the specifications and platform docs) and carried the corrections into
the synthesis, marked *corrected* where they appear and listed in its section 10.

## Files

```text
phase1_prompt.md, phase1_result.md     shortlist of sources, reader table
phase2_prompt.md, phase2_result.md     deep evaluation, contradictions, transfer risk
phase3_prompt.md, phase3_result.md     synthesis: candidate rule set with sources, and a test on real changes
```

The phase prompts use one H1 and H2 sections; the result files are pasted unedited and are excluded from markdownlint
by `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, as the other research directories are.

## Findings

- No single source serves all five readers. Project guides written for email and Gerrit workflows serve R1, R2, and R5;
  changelog specifications serve R4; R3 is served only by CVE Key Details Phrasing, the kernel's user-visible-impact
  rule, and Common Changelog, and no study observes an on-call engineer reading release notes.
- The one baseline claim with measured backing is that the commit body carries the *why* for a later `git blame`
  reader: Tao et al. (FSE 2012, 180 respondents) rank rationale as the most important information need, and Tian et
  al. (ICSE 2022, 1,597 messages) find about 44% of messages lack What or Why. Li and Ahmed (ICSE 2023, 611 linked
  messages) measure that 15% of issue links fail to supply the why, which settles "link or inline" in favor of inline.
- The subject is change-first and the body is problem-first; the two serve different reading moments, so the kernel
  and Google agree once the artifacts are separated.
- The changelog entry serves R3 and R4 in a fixed order: observable change, verbatim symptom and trigger, references,
  compatibility. No project was found recording the introducing version inside the entry; that rule is derived.
- Squash-merge guidance for authors is nearly absent from the literature; the rules are derived from GitHub and GitLab
  mechanics. The test on real changes found two failures no source names: in a merge-commit repository the pull request
  description never reaches `git log`, and under GitHub's default squash setting the body is the list of branch
  commits, so a rich description can leave `git log` with `Fix lint` and nothing else.
- Conventional Commits prefixes, the 50-character subject, `Change-Id:`, `Signed-off-by:`, and Prow commands serve a
  tool or a process, not a reader. They are house options gated on workflow detection, not core rules.
- Two baseline claims were contradicted by the sources: Keep a Changelog 1.1.0 does not ask for a separate
  breaking-changes block, and 2.0.0 argues against one; and the `type(scope):` prefix plus a fixed 72-character limit
  is a linter's job, not a reader's need.

## Status

All three phases complete. The synthesis in `phase3_result.md` was the input for the skill, which lives in the APM
package [`change-description-authoring`](../../agent-packages/change-description-authoring/) and is kept canonical
there, not duplicated here. The research files in this folder are frozen as the audit trail. The prose of the synthesis
runs to about 4,700 words, plus tables.
