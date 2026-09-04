# Research title

Evaluate the Pass 1 shortlist and extract applicable rules for a documentation-page authoring and review skill

# Goal

Pass 1 established that no single source covers the structure and content of developer documentation pages, and that the skill must be synthesised across four literatures: genre frameworks, style-guide structure chapters, standards-body normativity conventions and verifiability tooling, and technical-communication research.

Pass 2 does not repeat that survey. Its job is to turn the shortlist into **rules an agent can apply**, and to settle the questions Pass 1 left open.

The output of this pass feeds directly into a skill file. So the unit of the deliverable is not a source summary — it is a rule, stated once, with a rationale, a source, the genre it applies to, and the way a reviewer detects a violation of it.

# Target domain

The consumer is an LLM agent that both authors and reviews Markdown documentation pages inside a code repository: README files, reference pages, how-to guides, changelog entries, migration guides.

Two facts about the consumer change what counts as a usable rule:

**The agent works without the author.** It reads the page, the diff, and the source code, and it has no one to ask. A rule that depends on knowing the intent behind a page cannot be applied, however sound it is editorially.

**The agent runs inside a sweep with a mechanical oracle.** Pages are edited in batches; a separate program then proves that only prose changed, by stripping the prose and comparing what is left — headings, code fences, front matter, link targets, inline code spans. Anything the oracle protects is a thing the agent may *report* but not *edit*. Rules therefore fall into three buckets, and the report has to say which:

1. rules the agent applies while writing or reviewing;
2. rules a linter or CI job enforces mechanically (markdownlint, link and anchor checking, doctest runners, spell and terminology checks);
3. rules the sweep's oracle already enforces by construction, which the agent only needs to be told about.

# What Pass 1 settled — do not reopen

- Synthesis is required; there is no single base source.
- The category of agent skills for documentation *structure* is nearly empty. Do not spend budget re-searching it. If Pass 2 encounters one that treats a page as a verifiable claim about code, that is a finding worth reporting and it changes the build-from-scratch assumption.
- Sentence-level style is owned by a companion skill (`english-developer-style`) and is out of scope: voice, tone, sentence length, modifier stacks, punctuation policy, AI-writing tells, hedging, dialect, inclusive language, error-message wording, commit-message grammar. Do not re-derive any of it, and do not re-evaluate the Google/Microsoft/GitLab/Atlassian prose chapters.
- The rejects from Pass 1 stay rejected: SEO and link-rot marketing blogs, "docs developers actually read" listicles, documentation tooling comparisons, changelog SaaS pages, docs-as-code introductions on Medium and DEV, and prose-only agent skills.

# Shortlisted candidates from Pass 1

Evaluate these nine. Group members count as one candidate.

1. **Uddin & Robillard, "How API Documentation Fails"** — IEEE Software 32(4):68–75, 2015. `cs.mcgill.ca/~martin/papers/ieeesw2015.pdf`
2. **Aghajani et al., "Software Documentation Issues Unveiled"** (ICSE 2019) and **"Practitioners' Perspective"** (ICSE 2020).
3. **RFC 2119 / BCP 14 with RFC 8174**, and the **OASIS keyword guidelines**.
4. **The doctest family** — rustdoc documentation tests, Python `doctest`, the Sphinx doctest extension, and Sphinx's `versionadded` / `versionchanged` / `deprecated` directives.
5. **Google developer documentation style guide**, structure chapters only: Procedures, Headings, Lists and tables, Prescriptive documentation.
6. **Kubernetes Content Guide and Style Guide** — what a page may not contain; canonical source and dual-sourcing rules.
7. **Keep a Changelog 1.1.0** and **Common Changelog**.
8. **Meng, Steinhardt & Schubert, "How Developers Use API Documentation"** (CDQ 2019) and **Carroll's minimalism** work.
9. **standard-readme** and **purposeful-readme**.

# Specific questions from Pass 1 to investigate

These are the open items. Answer each explicitly, and say when the evidence does not settle it.

## Conflicts Pass 1 identified as live

1. **Diátaxis versus mixture pages.** Diátaxis asserts four and only four types; practitioners report content drift, and a real repository's `docs/` tree contains pages that are plainly mixtures — a README, a migration guide. Does the framework survive contact with a sampled real documentation tree? If it does not, what replaces "one page, one genre": a weaker rule, a per-genre exception list, or a different taxonomy?
2. **Version markers versus bloat.** Keep a Changelog wants an entry for every version; Sphinx maintainers report that accumulated `versionchanged` directives bloat a reference page. Where is the line, and does any project state a retention rule — for example, dropping version markers older than the supported window?
3. **`purposeful-readme`'s "a README must not contain a changelog"** against common practice. Is the rule defensible as stated, or does it need a size threshold?

## The gap Pass 1 could not close

4. **Headings as anchors, and renaming a published one.** Pass 1 found only general link-rot figures, nothing specific to a documentation set. Search specifically for: project policies on renaming a published heading; explicit anchor-ID mechanics (`{#id}`, Hugo aliases, Docusaurus `id:` front matter, Sphinx `:target:` and `autosectionlabel`); redirect conventions in documentation sites; and any measurement of intra-doc-set link rot or anchor breakage. If the area is genuinely unstudied, say so plainly — a rule asserted from mechanics is still usable, and mislabelling it as evidence is not.

## The area Pass 1 called thinnest and most on-brief

5. **Tools that diff documentation prose against source code.** Pass 1 saw citations to DocRef and Fraco. Establish what exists, whether any of it is maintained and usable, what precision it achieves, and what class of claim it can check — identifier existence, signature agreement, code-example compilation, configuration-key existence. Include documentation-defect detection research if it produces a usable heuristic. This is the highest-value question in the pass: it is the difference between an agent that reviews prose and one that checks claims.

## Applicability questions

6. **Can RFC 2119 normativity be borrowed without turning a page into an RFC?** Uppercase MUST under a boilerplate is right for a protocol specification and absurd in a README. Determine what transfers: the *distinction* between normative and informative, section-level marking, a convention for what a reader may rely on, or nothing but the vocabulary. Find projects outside the standards world that adopted the distinction for ordinary documentation, and report how they marked it.
7. **Which defects are detectable without reading the whole page?** Take the Uddin & Robillard ten problems and the Aghajani taxonomy, and classify each defect as: mechanically detectable by a linter; detectable by an agent from the page and the diff alone; detectable only by an agent that also reads the source; or needing a human. This classification is the single most useful thing Pass 2 can produce.
8. **Minimalism against reference completeness.** Carroll's minimalism argues for brevity and action-first instruction; a reference page is judged by exhaustiveness, and Uddin & Robillard rank incompleteness among the severest defects. Establish where each applies, per genre, and whether either literature acknowledges the other.
9. **Is there any source-backed rule about editing text that has already shipped?** The baseline claims that a changelog entry under a released version is not to be reworded, by analogy with a released string that has been quoted, translated, and linked. Find out whether any project or guide states this, and what exceptions they allow.

# Required output

Produce a research report under 3500 words. Cite sources with URLs; prefer primary sources, official documentation, and issue trackers over commentary. Do not re-explain general technical-writing principles unless they change the skill's design.

## 1. Executive summary

Answer directly:

- Which sources survive as *rule contributors*, and which drop to background?
- Which of the nine open questions did the evidence settle, and which stayed open?
- Does the tooling in question 5 exist in usable form?
- What is the recommended split across the three buckets — agent skill, linter or CI, sweep oracle?
- Does the Pass 1 four-stage recommendation still hold, and if not, what replaces it?

## 2. Deep candidate evaluation

One compact table row per candidate:

- name and URL
- disposition: rule contributor / supporting / background only / reject
- strongest contribution, in one line
- main weakness
- evidence: studied or asserted, and the sample or basis where studied
- maintenance status
- worked examples available: yes / no / partial
- false-positive risk when applied mechanically: low / medium / high
- portability into a compact skill: easy / medium / hard

## 3. Extracted rules

This is the core deliverable, and it should carry most of the word budget. Produce a table of 25 to 40 rules. One row per rule:

| Column | Content |
| --- | --- |
| Rule | One sentence, imperative, applicable without the author present |
| Rationale | Why, in one sentence — the reason a reader is harmed when it is broken |
| Source | Which candidate, with a URL or citation |
| Basis | Studied (name the study and sample) or asserted (name who asserts it) |
| Genre | All, or the genres it applies to |
| Detection | How a reviewer knows it was broken: a linter check, a pattern in the page, a comparison with the diff, a comparison with the source code, or whole-page judgement |
| Repair | What the reviewer tells the author to do |
| Bucket | Agent skill / linter or CI / sweep oracle |

Rules must not overlap. Where two sources state the same rule, merge them and cite both. Where they state it differently, keep the sharper formulation and note the difference in the conflicts section rather than emitting two rows.

## 4. Worked examples

For at most eight of the rules — the ones whose violation is hardest to recognise — give a short before/after drawn from real documentation, with the source named. Two or three sentences each. Say when a source has no examples of its own.

## 5. Pitfalls and false positives

For each rule you marked medium or high risk: what does mechanical application break? Give the case where following the rule makes the page worse. A rule with no failure mode is either trivial or under-analysed — say which.

## 6. Conflicts, resolved

For each conflict in questions 1 to 3, and any further conflict you find: state both positions with their sources, say which is better supported, and recommend what the skill should say. Where the honest answer is "it depends on the project", say what the project has to decide and what the default should be.

## 7. The three-bucket split

List what belongs in the agent skill, what belongs in a linter or CI job, and what the sweep's oracle already enforces. For the linter bucket, name the tool and rule where one exists (markdownlint rule numbers, Vale, a link checker, a doctest runner). Justify anything you leave to the agent that a tool could do instead — the default is that a mechanical check beats a prompt.

## 8. Baseline audit

The baseline skill is included below. Go through its sections and report, for each:

- claims the evidence supports;
- claims the evidence contradicts;
- claims that are neither supported nor contradicted, and are therefore asserted from one repository's practice;
- what is missing that the sources say should be there.

Pay particular attention to the three the baseline itself flags as weak: the genre table in §4, the claim in §3 about how readers enter a page, and the absence of anything about testable examples. Do not be polite about it — a rule that survives this audit unchanged should survive because the evidence backs it.

## 9. Recommended synthesis

- What the skill's section structure should be, and whether it should keep the numbering it shares with the companion comment-authoring skill.
- Target length, and what gets cut if the rules do not fit.
- Which rules are load-bearing and which are refinements, so that a compression pass knows what to drop first.
- What a Pass 3 synthesis prompt should be told to do.

# Baseline skill

The same snapshot Pass 1 used. Use it as context and as the object of the §8 audit, not as the target. Where a source contradicts it, that contradiction is the finding.

---

## 1. The correction that matters most

**A page states the specification, not the implementation.** The reader is deciding what they may rely on. Everything else is a fact about today's code that a safe refactoring is free to break, and once it breaks the page is wrong without anyone editing it. The test: *could this sentence stop being true without any caller noticing a behavior change?*

- *Implementation:* "The driver builds a `PreparedStatement` after the fifth execution and caches it on the connection."
- *Specification:* "A statement is prepared on the server after `prepareThreshold` executions. Set `prepareThreshold=0` to disable that."

**A page describes the state that holds, not the route to it.** `now`, `no longer`, `used to`, `previously` and `instead of the old` are the tells. Three places make history legitimate: a changelog entry or release note; a migration or upgrade guide; a version marker on a reference page (`Since 42.8.0`, a deprecation notice, a compatibility table), where the version is named rather than narrated.

## 2. The slots of a section

At most four, in order: **Claim** (always present), **Contract**, **Rationale** (only when the way is surprising), **Use**. The claim comes first because a reader who arrived from a search engine decides within a line whether this section is the one they wanted. An example is not a slot; it belongs to whichever slot it serves.

## 3. The first paragraph carries the section

Nobody enters a documentation set at the top. Open with the claim, not the topic; name the subject in the first sentence; put the qualification after the claim.

## 4. Genre

**One page, one genre.** Reference (state the contract exhaustively; fails by drifting into implementation), how-to guide (fails by explaining why mid-procedure), tutorial (fails by completeness), explanation (fails by turning into reference), README (fails by becoming the manual), changelog (fails by paraphrasing the diff instead of the behavior change), migration guide (fails by assuming the reader knows what broke). A reference page inherits the code's vocabulary: name a property, class or flag exactly as the code names it.

## 5. Links, and headings as anchors

**A heading is a URL anchor**, addressed from other pages, from issues, and from links nobody in the repository can see. Rewording one breaks every inbound link silently: no build fails and the page still renders. A heading rename is a separate change, with redirects, never a side effect of a wording pass. Two exceptions: a heading this branch introduced has no inbound links yet, and a site that pins anchors explicitly has already separated the words from the address.

## 6. Text a tool reads, not a human

Front matter (aliases are live URLs), fenced code blocks including the info string, shortcodes and directive comments, inline code spans and issue references. **Code in a fence is a claim nobody checks.** Unless the project compiles or runs its examples, a snippet is prose that looks authoritative and goes stale in silence. Do not edit a snippet as part of a wording pass; when a snippet contradicts the code, report it as a bug.

## 7. When to write nothing

Every page is a claim somebody has to keep true. Do not write a page that restates a generated API reference, a section explaining what the signature already shows, a rationale for a decision nobody would question, or a note a changelog entry already carries. The question is not "did the code change" but "did the promise change".

## 7a. Editing an existing page

Budget the net delta at zero; growth is paid for by a fact the old version did not carry. Check every name the section mentions, and treat a name that resolves to something private as evidence the page describes the implementation. Prefer deleting. A released changelog entry is not yours to reword — fix a factual error and leave the wording. Do not edit the skeleton.

## 7b. Comparing two versions

The new version will read better; it was written second. So read the old version first and reach the verdict last. (1) List the old version's facts. (2) Mark each present, restated, or absent; absent needs a defense, and "the code implies it" is not one. (3) Only now count the delta. (4) Check what the new version asserts without support; the commit message is not a source. (5) Check the claims against the code, not against the old page — the step a page needs and a comment does not, because a comment sits next to its subject while a section names its subject through identifiers. (6) Name the changes that bought nothing. (7) A new section runs on a different rubric: implementation, history, genre drift, staleness. (8) Prove the skeleton did not move, mechanically. (9) Say which finding it is: lost fact, unpaid growth, unsupported claim, implementation stated as contract, history narration, stale identifier, contradicted by the code, genre drift, churn, reworded skeleton, edited released entry.
