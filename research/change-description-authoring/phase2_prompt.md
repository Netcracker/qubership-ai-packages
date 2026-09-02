# Research title

Evaluate the Pass 1 shortlist per reader, and extract the structural rules a change-description skill can apply

## Goal

Pass 1 established that no single source covers the five readers of a change description, that the published corpus is
organized around who writes the message rather than who reads it, and that the on-call reader (R3) is the worst served.
It also found that the category of agent skills for description *structure* is nearly empty.

Pass 2 does not repeat that survey. Its job is to turn the shortlist into **rules an agent can apply**, each attributed
to the reader it serves, with the false-positive risk of applying it outside the project that wrote it. The output feeds
a synthesis document and, later, a skill file. So the unit of the deliverable is not a source summary. It is a rule,
stated once, with the reader it serves, the artifact and slot it belongs to, the source, the basis (measured or
asserted), the workflow the source assumes, and how a reviewer detects a violation.

## The readers

Carry these through every section. A rule that serves none of them is recorded in its own table and marked as such.

| Reader | Situation | What they need to find |
| --- | --- | --- |
| **R1. Reviewing maintainer** | Reading the change now, deciding whether to approve it | What was wrong; why this behavior is the right one; what changed; how it was verified; what is new test coverage; what is deliberately left out; what else touches the same files |
| **R2. Archaeologist** | Running `git blame` or `git log` years later, holding a line of code | Why the change was needed; why this approach rather than the obvious one; which constraint forced it; the issue; the identifiers and error text they will grep for |
| **R3. On-call or support engineer** | During an incident, holding a stack trace or a log line | The symptom as it appears (exception class, message text, error code); the trigger condition; the versions that introduced and fixed it; the workaround or the setting |
| **R4. Upgrading user** | Reading release notes before upgrading | What changed, in terms of what they can observe; whether it is compatible; what they have to do |
| **R5. Release manager or backporter** | Deciding what to cherry-pick into a maintenance branch | Severity; affected versions; dependencies between changes; whether the change is a fix, a feature, or a refactor |

Pass 1's reader table recorded which artifact each reader opens and what they read first, and marked most of it as
asserted or inferred. Pass 2 keeps that table, tightens it where new evidence allows, and does not soften the "asserted"
labels to make the result look better supported than it is.

## Target consumer

The consumer is an LLM agent that both writes and reviews change descriptions inside a repository. Three facts about it
change what counts as a usable rule:

**The agent has the diff, the tests, the issue, and the repository history, and no author to ask.** A rule that depends
on knowing the author's intent cannot be applied. A rule that depends on reading the diff can.

**The agent does not know the repository's workflow in advance.** It has to detect whether the repository squash-merges,
merges with merge commits, or rebases; whether release notes are hand-written, generated from a changelog file, or
generated from commit prefixes; whether there are maintenance branches. Rules therefore need a stated precondition: "in
a squash-merge repository", "where the project maintains release branches", "where a tool reads the commit prefix". A
rule with no precondition is claimed to hold everywhere, and Pass 2 has to defend that.

**Wording is not the agent's problem here.** Sentence-level style is owned by a companion skill
(`english-developer-style`): imperative mood, tense, length, capitalization, trailing period, em-dashes, hedging,
dialect. Do not re-derive any of it. Where a shortlisted source is mostly wording (Beams rules 1 to 6, Pope's 50/72 line
widths), take only the structural part and say in one line what was left out.

## What Pass 1 settled, do not reopen

- Synthesis is required; no single source covers the five readers.
- R2 is the best-served reader, and the "why for `git blame`" claim has measured backing (Tian et al. ICSE 2022; Tao et
  al. FSE 2012). Do not spend budget re-establishing that a body should carry the why.
- R3 is the worst-served reader. The only sources that speak to naming a greppable symptom are CVE "Key Details
  Phrasing", the kernel's "describe user-visible impact, include dmesg excerpts" rule, and Common Changelog's "be
  specific about the symptom". Pass 2 builds the R3 rules from these and says plainly when a rule is inferred rather
  than sourced.
- Agent skills for description structure are template-shaped and reader-blind. Do not re-search the category. If Pass 2
  encounters one that attributes a slot to a downstream reader, report it; that changes the build-from-scratch
  assumption.
- The rejects stay rejected: prefix-vocabulary debates, Beams listicles, changelog SaaS marketing, commit-message
  generation papers that did not measure content, generic changelog blog advice.

## Shortlisted candidates from Pass 1

Evaluate these ten. Group members count as one candidate.

1. **Linux kernel**: "Describe your changes" in `submitting-patches`, the `Fixes:` and `Link:` trailer rules, and
   `stable-kernel-rules`. <https://www.kernel.org/doc/html/latest/process/submitting-patches.html>,
   <https://www.kernel.org/doc/html/latest/process/stable-kernel-rules.html>. The tip-tree handbook is a supporting
   member for its worked examples: <https://www.kernel.org/doc/html/latest/process/maintainer-tip.html>.
2. **Google eng-practices, "How to write good CL descriptions"** and "Small CLs".
   <https://google.github.io/eng-practices/review/developer/cl-descriptions.html>,
   <https://google.github.io/eng-practices/review/developer/small-cls.html>.
3. **Tian et al., "What Makes a Good Commit Message?" (ICSE 2022)** and **Tao et al., "How Do Software Engineers
   Understand Code Changes?" (FSE 2012)**. <https://arxiv.org/abs/2202.02974>; find the canonical URL for Tao et al.
4. **Li and Ahmed, "Commit Message Matters" (ICSE 2023)**. <https://dl.acm.org/doi/10.1109/ICSE48619.2023.00076>.
5. **Keep a Changelog 1.1.0** and **Common Changelog**. <https://keepachangelog.com/en/1.1.0/>,
   <https://common-changelog.org/>. Bi et al. (TSE 2020) and Abebe et al. (EMSE 2016) are supporting members for what
   release notes contain and what users want from them.
6. **CVE "Key Details Phrasing"**. <https://cveproject.github.io/docs/content/key-details-phrasing.pdf>.
7. **Kubernetes**: the release-notes guide, the fenced `release-note` block in the PR template, and the cherry-pick
   guide. <https://www.kubernetes.dev/docs/guide/release-notes/>,
   <https://github.com/kubernetes/community/blob/master/contributors/guide/release-notes.md>,
   <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md>.
8. **towncrier** and **release-please**, as the two ends of the tooling design space.
   <https://towncrier.readthedocs.io/>, <https://github.com/googleapis/release-please>. Conventional Commits 1.0.0 is a
   supporting member here, evaluated only for what a tool extracts from it:
   <https://www.conventionalcommits.org/en/v1.0.0/>.
9. **`git interpret-trailers`** and **GitHub closing keywords and squash-merge behavior**.
   <https://git-scm.com/docs/git-interpret-trailers>,
   <https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue>,
   <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges>.
   Include GitLab's equivalent squash and closing-pattern behavior so the rules are not GitHub-specific.
10. **PostgreSQL Commit Message Guidance** and its back-branch practice, with **Zulip commit discipline** as a second
    rebase-workflow source. <https://wiki.postgresql.org/wiki/Commit_Message_Guidance>,
    <https://wiki.postgresql.org/wiki/Committing_checklist>,
    <https://zulip.readthedocs.io/en/latest/contributing/commit-discipline.html>. For PostgreSQL, also establish how the
    release notes are produced from the commit log (Bruce Momjian's process) and what that forces a commit message to
    carry.

Git's `SubmittingPatches` (<https://git-scm.com/docs/SubmittingPatches>) and Bosu et al. (MSR 2015) are supporting
sources; cite them where they sharpen a rule, do not evaluate them separately.

## Specific questions to investigate

Answer each explicitly, and say when the evidence does not settle it.

## Contradictions Pass 1 identified as live

1. **Issue link versus inline why.** Tian et al. accept an issue or PR link as a way of supplying the why; Li and Ahmed
   found that such links often fail to deliver it. Pass 1 proposed deciding for R2 and R3: write a one-line why and the
   identifiers into the message, and treat the link as supplementary. Confirm or refute this from the two papers' actual
   findings (what fraction of links failed, and how). State what the rule should say, and what the minimum inline
   content is when an issue exists.
2. **Who owns the `Fixed` entry: R4 or R3.** Most changelog guidance serves the upgrading user; CVE phrasing and Common
   Changelog lean toward the operator with a stack trace. Settle whether one entry can serve both, and if so in what
   order the symptom, the trigger, the fix, and the compatibility statement appear. Find any project whose `Fixed`
   entries name the exception or the error text, and any that forbid it, and record what each says the reason is.
3. **Body order: problem first or change first.** The kernel orders problem, then user-visible impact, then solution.
   Google orders "what is being done and why", first line summarizing the change. Conventional Commits and
   release-please read only the subject and the footers. Which order does each reader need, and does any source say why?
   Where the readers disagree, name the reader whose need wins for each artifact (commit body, PR description, changelog
   entry) and say why the other reader is not harmed.
4. **Verification in the permanent record or not.** The kernel's `---` separator keeps test notes out of the commit;
   Google's guidance and most PR templates put a test plan in the description; in a squash-merge repository the
   description becomes the commit body. Decide where "how it was verified" lives in each workflow, and whether it
   belongs in `git log` at all. This is R1's need against R2's noise.

## Transfer risk

5. **Which rules are workflow-bound?** For each rule you extract, name the workflow the source assumes (email patches,
   Gerrit, GitHub merge commits, GitHub squash, rebase-and-merge, monorepo) and rate the false-positive risk of applying
   it elsewhere. Pay particular attention to: patch-series rules, the `---` separator, `Cc: stable`, `Change-Id`, the
   Kubernetes `/kind` and `release-note` labels, Conventional Commits prefixes, and the 50-character subject limit
   versus GitHub's title truncation. Where a rule does not transfer but its *principle* does, state the principle and
   the mechanism a squash-merge repository would use instead.
6. **The squash-merge case.** Pass 1 found that platform behavior is documented (PR title and body seed the squash
   commit, PR number appended) but author guidance is nearly absent. Establish exactly what GitHub and GitLab put in the
   squash commit under each of their settings, and what the merging maintainer can edit. Then derive the rules for a
   repository where the PR title becomes the subject and the body becomes the commit body: what goes in the title, what
   goes in the body, where the reviewer-only content (checklist, screenshots, test plan, review round history) goes so
   that it does not end up in `git log`, and what happens to `Closes #` and `Co-authored-by` trailers. Mark these rules
   as derived from mechanics rather than cited, where that is the truth.

## The under-served readers

7. **R3, the on-call reader.** From CVE Key Details Phrasing, the kernel's impact rule, Common Changelog, and any
   security-advisory convention you find (GitHub Security Advisories, distribution security teams, OpenSSF), derive the
   content an on-call reader needs and where it goes: exception class or error text quoted verbatim, the trigger
   condition, the version that introduced the defect, the version that fixes it, the workaround or setting. Say which of
   these belong in the commit body, which in the changelog entry, and which in both. Find whether any project records
   the introducing version in the changelog rather than only in a `Fixes:` trailer, and whether any measures how
   operators search release notes.
8. **R5, the backporter.** From stable-kernel-rules, the `Fixes:` trailer, PostgreSQL's back-patch lines, Kubernetes
   cherry-picks, and Python's backport labels, extract what a description must carry so that a backporter can decide
   without reading the diff: severity, affected versions or the introducing commit, dependencies on other changes,
   whether the change is a fix or a feature. Say which of these are trailers, which are labels the platform holds
   outside the message, and which are prose. Note where the signal lives outside the description entirely, because the
   skill cannot write it there.

## Evidence

9. **What readers read first.** Pass 1 found only Tao et al. (single company) and no observation of on-call engineers or
   backporters. Search once more, specifically, for eye-tracking or think-aloud studies of code review, for studies of
   how developers navigate commit history, and for release-note reading studies. Report what you find and label the
   reader table's cells accordingly. If the area stays unstudied, say so.
10. **Which slots does the empirical work support?** Map Tian et al.'s Why and What categories and Tao et al.'s ranked
    information needs onto the candidate slots (problem, cause, change, verification, scope left out, alternatives
    rejected). Which slots have measured support, which are asserted by guides, and which appear in neither?

## Required output

Produce a research report under 4500 words. Cite sources with URLs; prefer primary sources, official documentation, and
issue trackers over commentary. Do not re-explain general commit-message advice unless it changes the skill's design.

## 1. Executive summary

Answer directly:

- Which sources survive as rule contributors, and which drop to supporting or background?
- Which of the ten questions did the evidence settle, and which stayed open?
- For each reader, R1 to R5, the single most important rule and its source.
- Which rules are workflow-bound and how the skill should gate them.
- What the split is between rules the agent applies, checks a linter or platform enforces, and judgments left to a
  human.

## 2. Reader table, revised

Pass 1's table with the "measured or asserted" column updated from question 9. One row per reader: the artifact they
open, what they read first, the sources, and the basis. Keep "asserted" where it is true.

## 3. Deep candidate evaluation

One compact table row per candidate:

- name and URL
- disposition: rule contributor / supporting / background only / reject
- readers served
- workflow assumed
- strongest structural contribution, one line
- what it prescribes that no reader needs, one line
- main weakness
- evidence: measured or asserted, and the sample where measured
- worked examples available: yes / no / partial
- false-positive risk outside the home workflow: low / medium / high
- portability into a compact rule: easy / medium / hard

## 4. Extracted rules

This is the core deliverable and should carry most of the word budget. Produce a table of 30 to 45 rules. One row per
rule:

| Column | Content |
| --- | --- |
| Rule | One sentence, imperative, applicable by an agent holding the diff and no author |
| Reader | R1 to R5, one or several; the first listed is the one whose need the rule exists for |
| Artifact and slot | Commit subject, commit body (which slot), trailer, PR title, PR body (which section), changelog entry |
| Rationale | Why, in one sentence: what the named reader fails to find when the rule is broken |
| Source | Candidate, with URL |
| Basis | Measured (name the study and sample) or asserted (name who asserts it) |
| Workflow | The workflow the source assumes, and the precondition under which the rule applies elsewhere |
| Detection | How a reviewer knows it was broken: a pattern in the text, a comparison with the diff, a comparison with the issue, a tool check |
| Bucket | Agent skill / linter, commitlint, or platform check / human judgment |

Rules must not overlap. Where two sources state the same rule, merge them and cite both. Where they state it
differently, keep the sharper formulation and record the difference in the conflicts section rather than emitting two
rows. Where a rule is wording rather than structure, leave it out and do not count it.

## 5. Rules no reader needs

A second, shorter table: prescriptions the shortlisted sources make that serve none of the five readers, or serve only
the source's own tooling. One row each: the prescription, the source, whom it actually serves (a tool, a mailing-list
workflow, a maintainer's habit), and whether the skill should mention it as a house-style option or drop it.
Conventional Commits prefixes, the 50-character subject, `Signed-off-by`, and `Change-Id` are candidates for this table;
decide each on the evidence.

## 6. Worked examples

For at most eight of the rules, the ones whose violation is hardest to recognize, give a short before and after drawn
from the source's own examples or from a real public commit, with the source named. Two or three sentences each. Say
when a source has no examples of its own. Do not invent a "real" commit; if you construct one, say so.

## 7. Pitfalls and false positives

For each rule you marked medium or high risk: what does applying it outside its home workflow break? Give the case where
following the rule makes the description worse for one of the readers. A rule with no failure mode is either trivial or
under-analyzed; say which.

## 8. Conflicts, resolved

For each conflict in questions 1 to 4 and any further conflict you find: state both positions with their sources, name
the reader whose need decides it and why, say whether the losing reader is harmed, and recommend what the skill should
say. Where the honest answer is "it depends on the workflow", say what the agent has to detect and what the default
should be when detection fails.

## 9. Baseline audit

The baseline is included below. Go through its claims and report, for each:

- claims the evidence supports, with the source;
- claims the evidence contradicts;
- claims that are neither supported nor contradicted, and are therefore one team's practice;
- what is missing that the sources say should be there, per reader.

Pay particular attention to the four the baseline itself flags as weak: the three-section PR body in the order why,
what, how to verify; the absence of an R3 rule beyond "name the symptom"; the absence of any R5 rule; and the
artifact-level table, which asserts what each artifact carries without a source. Do not be polite about it. A rule that
survives this audit unchanged should survive because the evidence backs it.

## 10. Recommended synthesis

- The slots of each artifact (commit subject, commit body, trailers, PR title, PR body, changelog entry), in order, with
  the reader each slot serves and the test for whether a sentence belongs in it.
- The trailer and identifier rules that make text greppable, as a single list.
- The rules for a squash-merge repository, as a single list, each marked cited or derived.
- The changelog entry as the artifact R3 and R4 share, with the order of its parts.
- The anti-patterns each source names, with the reader each one fails.
- Which rules are load-bearing and which are refinements, so that a compression pass knows what to drop first.
- What a Pass 3 synthesis prompt should be told to do, and what it should be told not to do.

## Baseline

The same snapshot Pass 1 used. Use it as context and as the object of the section 9 audit, not as the target. Where a
source contradicts it, that contradiction is the finding.

---

**Commit messages.** Subject in the form `type(scope): summary`, at most 72 characters. The body, after a blank line,
explains why the change was needed and notes anything non-obvious: migration risk, performance trade-off, related
incident. Reference issues by ID. Do not paraphrase the diff.

**PR titles.** About 100 characters; below that ceiling accuracy wins over brevity, because the title is read in a list
and searched. Where a project squash-merges, the title seeds the commit subject rather than becoming it: the merging
maintainer edits the line and the platform may append or strip the number.

**PR descriptions.** Three short sections, in order: **Why** (the problem or constraint that forced the change),
**What** (the behavioral change, not the changed files), **How to verify** (commands, and what each one establishes).
Call out breaking changes, migrations, and follow-up work where there are any; an absent section is not a gap to fill. A
reviewer decides and does not re-investigate: carry what changes that decision (what was wrong, why this behavior is
right, what changed, how it was checked, what scope or risk is left). Ask of every paragraph which review decision
becomes harder if it disappears. Name what the tests establish rather than transcribing them; say which tests are new. A
rejected alternative a reviewer would propose goes in a collapsed block with a mechanism or a measurement. Related or
stacked pull requests are described as scope: where they overlap and whether one is a dependency. Quoted diagnostics are
literals, reproduced exactly.

Each artifact has a primary level of detail:

| Artifact | Its level |
| --- | --- |
| the diff | implementation detail |
| the tests | individual cases, fixtures, parameter matrices, failure output |
| the doc comment | the durable API contract |
| the commit message | why the change was needed, for whoever runs `git blame` years later |
| the changelog | the released, user-visible symptom |
| the PR | the problem, the decision, the scope, and a verification summary |

**Changelog and release notes.** Group under `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`, `Security` (Keep a
Changelog). One sentence per entry by default. Name the symptom a reader will search for, such as the exception class or
the error text, even at the cost of a second sentence. Link to the PR or commit. Breaking changes get their own block at
the top of the version.
