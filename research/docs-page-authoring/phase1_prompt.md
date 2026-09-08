# Research title

Find proven rules for the structure and content of developer documentation pages, above the level of the sentence

# Goal

Run a broad discovery pass to find candidate sources for an LLM skill that writes and reviews **documentation pages** in a code repository: README files, reference pages, how-to guides, changelog entries, migration guides, and the docs sets that ship alongside a library.

The target is everything above the sentence. Sentence-level style is already solved by a companion skill and is explicitly out of scope (see *Out of scope* below). What is missing is guidance on:

- what a page is for, and what happens when one page tries to do two jobs
- what belongs in a section, and in what order
- how a page states a contract a reader may rely on, rather than describing how today's code happens to work
- when describing past behaviour is legitimate and when it is a defect
- how a documentation claim is checked against the code it describes, mechanically or by review
- how documentation goes stale, which parts go first, and what practices slow that down
- how headings behave as URL anchors, and what renaming one costs
- what review rubrics and defect taxonomies exist for documentation

This is Pass 1 only. The goal is discovery and classification, not final ranking.

# Important framing

Do not search for sources that merely match the baseline skill included at the end of this prompt. That skill is a starting point written from practice, not the target. Prefer sources that improve on it, contradict it usefully, or take a different approach.

It is acceptable to conclude that no single authoritative source covers this domain. In that case, identify the strongest reusable rule sources and explain how they could be combined.

The consumer of the result is an LLM agent that both authors and reviews pages, so prefer sources that state a rule **and** its rationale over sources that give a checklist. A rule an agent cannot apply without the author present is not useful here.

Two properties matter more than they usually do in a style guide, because the consumer is an agent working inside a repository:

- **Detectability.** For each rule, can a reviewer tell that it was violated without reading the whole page? Sources that describe how a defect is spotted are worth more than sources that describe the ideal.
- **Verifiability against code.** Documentation in a code repository can be wrong in a way that prose style cannot. Sources that treat a page as a claim about a system, rather than as writing, are the ones this pass is looking for.

# Out of scope

The following is already covered by a companion skill (`english-developer-style`) and must not be restated or re-derived:

- voice, tone, and person; sentence length; paragraph craft
- modifier stacks, noun piles, and over-compressed constructions
- em-dash, hyphen, and serial-comma policy
- LLM writing tells and how to avoid them
- hedging and certainty; present tense; `currently`; bare `will`
- British / US dialect policy and spelling
- inclusive language
- error-message and log-message wording
- commit-message grammar and Conventional Commits
- the Google, Microsoft, GitLab, Atlassian, and Wikipedia rule families those come from

Treat sentence-level style as settled. If a source's only contribution is sentence-level, classify it as a reject and say so in one line. A source may still be included when its *structural* chapters are strong even though its prose chapters duplicate the above — say which chapters matter.

Also out of scope: documentation *tooling* comparisons (Hugo versus Docusaurus versus MkDocs), documentation hosting, search infrastructure, and localisation workflow. Include a tool only where it enforces or checks a content rule.

# Questions the pass should answer

Use these to steer the search. Pass 1 does not have to answer them fully; it has to find the sources that can.

1. **Genre.** Which taxonomies of developer documentation exist (tutorial, how-to, reference, explanation, README, changelog, migration guide, ADR, runbook)? Diátaxis is the obvious framework — find its critics and find where practitioners deviate from it. What is claimed about the cost of mixing two genres in one page, and is any of it studied rather than asserted?
2. **Specification versus implementation.** What guidance exists on documenting the contract rather than the current behaviour of the code? What can a project-level guide borrow from how standards bodies separate normative from informative text (RFC 2119 / BCP 14, JSR specifications, W3C, POSIX)?
3. **Historicity.** What is the guidance on describing past behaviour? Where is it legitimate — changelog, release notes, migration guide, deprecation notice, `Since X.Y` markers — and where is it a defect? How do large projects mark version-dependent behaviour on a reference page?
4. **Verifiability.** Which practices make documentation checkable against the code: doctests, tested examples (Go `Example` functions, Rust doc-tests, Python `doctest`, Sphinx doctest, mdBook, mdoc), literate or generated documentation, descriptions generated from a schema? What is the evidence on how quickly prose documentation goes stale, and which parts go first?
5. **Section structure.** What guidance exists on the first paragraph of a page and of a section, on heading design, on ordering within a section, and on when a table beats prose? What is known empirically about how developers read documentation — search-entry rather than top-entry, scanning, task-driven reading?
6. **Anchors and link rot.** What is the practice on treating headings as stable URL anchors, on renaming a heading in a published page, on explicit anchor IDs and redirects, and on measuring link rot inside and across documentation sets?
7. **Minimalism.** What does the minimalist documentation tradition (John Carroll and successors) claim about instruction length and completeness, and what is the current evidence for or against it in developer documentation?
8. **Review.** Which documentation review rubrics exist — in style guides, in open-source contribution guides, in technical-communication literature? Which defect taxonomies are in use (inaccurate, incomplete, outdated, unfindable, unusable)? What can be checked mechanically, and what needs a human or a model?
9. **Agent-authored documentation.** Is there any existing skill, rule file, or system prompt that governs documentation *structure* for an LLM agent, as opposed to prose style? If the category is empty, say so — that is a useful finding.

# Search scope

## 1. Documentation frameworks and taxonomies

Diátaxis, the Divio documentation system, and their critics and forks. Anything that classifies documentation by the job it does rather than by its format.

## 2. Structure chapters of editorial style guides

The Google developer documentation style guide, the Microsoft Writing Style Guide, the Red Hat and IBM style guides, and any other guide with substantial page-structure, procedure-structure, or reference-structure chapters. Only the structural chapters count here.

## 3. Documentation contribution guides of large open-source projects

Kubernetes, Rust, Django, PostgreSQL, Python, Go, Linux kernel, GitLab, Ansible, Prometheus. Look for rules that constrain content rather than wording: what a page must contain, what may not go on it, how versions are marked, how a page is reviewed before it merges.

## 4. Documentation testing and generation

Tooling and practices that make examples executable or descriptions generated: doctest families, tested snippets, literate programming, OpenAPI and JSON Schema description conventions, docs linters that check links and anchors, and any tool that flags a documentation claim against source.

## 5. Technical-communication research

Minimalism (Carroll and successors), studies of API documentation use, documentation staleness and drift studies, empirical work on how developers search and read, and defect taxonomies for documentation quality.

## 6. Documentation review practice

Review rubrics, docs-as-code review checklists, documentation quality models (for example anything descending from ISO/IEC 26514 or similar), and published post-mortems of documentation failures.

## 7. Agent skills and rule files for documentation

Claude Code skills, Cursor / Continue rules, and system prompts that govern documentation authoring. Report honestly if this category is thin.

# Freshness

Prefer sources updated in 2024 or later where the subject is agent-authored documentation or tooling. Older sources are acceptable, and expected, where they are established, authoritative, still cited, and about how people read and use documentation — the technical-communication research in scope here is mostly older, and that is fine.

# What counts as evidence

Treat these as scoring signals, not hard filters:

- adopted by a known engineering organisation or a large open-source project
- authored by a named technical writer, docs team, or researcher
- actively maintained
- ships with concrete before/after examples
- states a rationale, not only a rule
- independent evaluation, criticism, or measured results
- public issue discussions showing real-world trade-offs

Prefer sources with human editorial authority over anonymous prompt snippets. Prefer a studied claim over a widely repeated one, and say which is which.

# Exclusions

Exclude:

- sentence-level style guidance (see *Out of scope*)
- documentation tooling and hosting comparisons
- marketing and content-marketing writing guidance
- SEO guidance, except where it bears directly on headings as anchors and on search-entry reading
- courseware and academic-writing guidance with no developer-documentation application
- anonymous prompt lists with no evidence of use
- generic "how to write good docs" listicles with no rationale and no source

# Required output for Pass 1

Produce a discovery report under 2500 words. Do not deeply analyse every candidate yet; the purpose is to build a strong candidate pool for Pass 2.

## 1. Executive summary

Answer briefly:

- Does any single source cover page structure and content for developer documentation, or is synthesis required?
- Which source category looks strongest, and which is weakest or most polluted?
- Is there any existing agent skill for documentation structure, as opposed to prose style?
- Which of the nine questions above look answerable from existing sources, and which look under-served?
- Should Pass 2 concentrate on frameworks, project contribution guides, research, or tooling?

## 2. Candidate inventory

Produce a table with 15–25 candidates. For each:

- name
- URL
- category: framework / style-guide chapter / project contribution guide / tooling / research / review rubric / agent skill
- author or organisation
- which of the nine questions it speaks to (list the numbers)
- best use: authoring / reviewing / mechanical checking / background research
- evidence strength: strong / medium / weak, and whether its central claim is studied or asserted
- maintenance status: active / stale / unclear
- one line on why it is worth considering

## 3. Promising shortlist for Pass 2

Select 7–10 candidates. For each, in 2–4 sentences: why it is promising, which rules it may contribute, whether it suits authoring or reviewing, and whether it converts into a compact rule an agent can apply without the author present.

## 4. Obvious rejects

List 5–10 sources or categories that looked relevant but should be excluded, with a one-line reason each.

## 5. Gaps and questions for Pass 2

List the main uncertainties. Include at least these, and add your own:

- which rules have a detectable violation, and which need the whole page read
- which sources conflict with each other, and on what
- whether any source addresses documentation as a claim about code rather than as writing
- whether the genre taxonomy survives contact with a repository's actual docs directory, where a page is often a mixture
- what is left that only a human can judge

# Baseline skill

Use the following skill only as context, and as a snapshot of what practice has already produced. Do not treat it as the target, and do not limit the search to sources that agree with it. Where a source contradicts it, that contradiction is a finding worth reporting.

The baseline was written for one repository's documentation set and generalised by hand. Its weakest parts, and the ones most in need of external evidence, are: the genre table in §4, the claim in §3 about how readers enter a page, and the absence of anything about testable examples.

---

<!-- Snapshot of ~/.claude/skills/docs-page-authoring/SKILL.md at the time this pass was run. -->

# Authoring a documentation page

This skill governs **what a page says, in what order, and what it may not claim**. Wording, tone, sentence length and dialect belong to `english-developer-style`. Layout that a linter settles — line length, one H1, named links, a language tag on every fence — belongs to the repository's markdownlint configuration.

## 1. The correction that matters most

**A page states the specification, not the implementation.** The reader is deciding what they may rely on. Everything else is a fact about today's code that a safe refactoring is free to break, and once it breaks the page is wrong without anyone editing it.

The test: *could this sentence stop being true without any caller noticing a behavior change?* If it could, it describes the implementation.

- *Implementation:* "The driver builds a `PreparedStatement` after the fifth execution and caches it on the connection."
- *Specification:* "A statement is prepared on the server after `prepareThreshold` executions. Set `prepareThreshold=0` to disable that."

This is not a ban on mechanism. A reference page explains mechanism whenever the mechanism is the thing a caller has to reason about. What it must not do is describe the current code path as though it were the promise.

**A page describes the state that holds, not the route to it.** "This used to return `null`, but after the fix in 42.7.5 it throws" is two versions in a sentence, and the reader has one. `now`, `no longer`, `used to`, `previously` and `instead of the old` are the tells.

Three places make history legitimate: a changelog entry or release note; a migration or upgrade guide; a version marker on a reference page (`Since 42.8.0`, a deprecation notice, a compatibility table), where the version is named rather than narrated.

## 2. The slots of a section

A section has at most four slots, in this order: **Claim** (what is true, or what does this do — always present), **Contract** (what may the reader rely on, and what do they owe), **Rationale** (why, when the way is surprising), **Use** (what the reader types or calls next).

The claim comes first because a reader who arrived from a search engine decides within a line whether this section is the one they wanted. Rationale comes after contract because a reader who accepts the contract can stop reading.

An example is not a slot: it belongs to whichever slot it serves.

## 3. The first paragraph carries the section

Nobody enters a documentation set at the top. They arrive at a heading from a search engine, from another page, or from a link in an error message, and they read one paragraph before deciding.

- Open with the claim, not with the topic.
- Name the subject in the first sentence, so the paragraph survives being read on its own.
- Put the qualification after the claim.

## 4. Genre

**One page, one genre.** A page that teaches and specifies at once fails both readers. When a page does both, the repair is a link, not a merge.

| Genre | Its job | Its characteristic failure |
| --- | --- | --- |
| Reference | State the contract, exhaustively, in a searchable order | Drifting into the current implementation; prose where a table would answer faster |
| How-to guide | Carry a reader with a stated goal from start to done | Explaining why, at length, mid-procedure |
| Tutorial | Teach by a path guaranteed to work | Completeness — every option offered is a chance to fail |
| Explanation | Give the model behind the design | Turning into reference |
| README | What this is, who it is for, the shortest thing that works | Becoming the manual |
| Changelog | Name what changed, per version, in the reader's terms | Paraphrasing the diff instead of the behavior change |
| Migration guide | Carry a reader across a break | Assuming the reader knows what broke |

A reference page inherits the code's vocabulary: name a property, class or flag exactly as the code names it. A changelog entry names the behavior change, not the patch.

## 5. Links, and headings as anchors

**A heading is a URL anchor**, addressed from other pages, from issues, and from links nobody in the repository can see. Rewording one breaks every inbound link silently: no build fails and the page still renders. So a heading rename is a separate change, with redirects, never a side effect of a wording pass.

Two exceptions: a heading this branch introduced has no inbound links yet, and a site that pins anchors explicitly has already separated the words from the address.

Link text names the destination; a link to source names the symbol rather than a line number.

## 6. Text a tool reads, not a human

Front matter (`aliases` are live URLs), fenced code blocks including the info string, shortcodes and directive comments, inline code spans and issue references. Rewording any of it is a behavior change.

**Code in a fence is a claim nobody checks.** Unless the project compiles or runs its examples, a snippet is prose that looks authoritative and goes stale in silence. Do not edit a snippet as part of a wording pass, and when a snippet contradicts the code, report it as a bug.

## 7. When to write nothing

Every page is a claim somebody has to keep true. Do not write a page that restates a generated API reference, a section explaining what the signature already shows, a rationale for a decision nobody would question, or a note a changelog entry already carries. The question is not "did the code change" but "did the promise change".

## 7a. Editing an existing page

- **Budget the net delta at zero.** Restructuring is free; growth is paid for by a fact the old version did not carry, and you name the fact.
- **Check every name the section mentions.** Grep each one. A name that resolves to something private means the page is describing the implementation.
- **Prefer deleting.** A limitation that was lifted, an option that was removed, a workaround for an unsupported version.
- **A released entry is not yours to edit.** A changelog entry under a shipped version has been read, quoted and possibly translated. Fix a factual error; leave the wording.
- **Do not edit the skeleton** — headings, code blocks, front matter, inline code spans.

## 7b. Comparing two versions

The new version will read better; it was written second. Reading forward finds nothing, because a fact that vanished leaves no trace in the text that replaced it. So: read the old version first, and reach the verdict last.

1. List the old version's facts before reading the new one. One fact is one bound, default, required call, ordering constraint, version, failure mode, identifier, link target, or guarantee.
2. Mark each fact present, restated, or absent. Absent needs a defense: the fact was wrong, it moved and you can point at the sentence, or it belongs to another genre and moved to the page that owns it. Not accepted: the code implies it, the new wording covers it, it was obvious.
3. Only now count the delta.
4. Check what the new version asserts without support. Every claim traces to the code, the old page, or a linked contract. The commit message is not a source.
5. Check the claims against the code, not against the old page. For each identifier the section mentions, find it, then ask whether the sentence around it is still true. This is the step a page needs and a comment does not, because a comment sits next to its subject and a section names its subject through identifiers.
6. Name the changes that bought nothing.
7. A new section runs on a different rubric: implementation, history, genre drift, staleness.
8. Prove the skeleton did not move, mechanically.
9. Say which finding it is, not whether the page got better: lost fact, unpaid growth, unsupported claim, implementation stated as contract, history narration, stale identifier, contradicted by the code, genre drift, churn, reworded skeleton, edited released entry.
