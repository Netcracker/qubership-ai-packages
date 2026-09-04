# Research title

Close the reader gap: who opens a documentation page, what they hold, and what a change owes each of them

# Goal

Passes 1 and 2 produced a rule set for documentation pages that is strong on *what a page may claim* (specification
rather than implementation, named version markers, verified identifiers, executable examples, headings as anchors) and
on *how to review an edit* (the fact ledger, the finding taxonomy, the three-bucket split). A skill was written from
them and tried on a real branch. The trial exposed what the two passes never asked: the rules say how a sentence may be
wrong, but not **which reader a section exists for, where in a documentation set that reader looks, and what a code
change owes the documentation before it merges**.

Pass 3 closes that gap. It is a targeted deep-research pass, not a re-survey. Its deliverable is evidence for, against,
or beyond a candidate reader model and three candidate procedures, so that a later synthesis can write them into the
skill with their sources attached and their basis labeled.

The consumer is unchanged: an LLM agent working inside a code repository, without the author present, that both writes
and reviews Markdown pages. The most common task it faces is not "write a page" but "a branch changed the product;
update the documentation so that it answers the questions users now have." The pass has to serve that task.

# What Passes 1 and 2 settled, and this pass does not reopen

- Synthesis across four literatures is required; no single source covers the domain.
- Sentence-level style belongs to a companion skill (`english-developer-style`) and is out of scope: voice, tense,
  sentence length, punctuation, AI-writing tells, hedging, dialect, inclusive language, error-message wording.
- The changelog entry and the pull request description belong to a second companion skill
  (`change-description-authoring`), which fixes five readers of a *change*: the reviewing maintainer, the archaeologist
  at `git blame`, the on-call engineer holding a stack trace, the upgrading user reading release notes, and the
  backporter. Do not re-derive the changelog entry. Where a documentation reader coincides with one of those five, say
  so and stop at the boundary.
- "One page, one genre" is demoted to "one primary purpose per section"; the genre failure modes stay as detection
  heuristics.
- Executable examples, identifier verification, the anchor rule, released-entry immutability, and the normative versus
  informative distinction are settled as stated in Pass 2. Cite them; do not re-argue them.
- The rejects from Passes 1 and 2 stay rejected: SEO and link-rot marketing, "docs developers love" listicles,
  tooling comparisons, changelog SaaS pages, docs-as-code introductions on Medium and DEV, prose-only agent skills.

# The candidate reader model

The companion skill for change descriptions was built around a fixed reader table, and that structure is what made its
rules applicable without the author present: every rule names the reader whose question it answers. The documentation
skill has no such table. The candidate below was written from practice and is the object of this pass. Confirm each
row, refute it, split it, or add a row, and label the result *studied* or *asserted*.

| Reader | Situation | Holds | Opens | Enters by | Asks |
| --- | --- | --- | --- | --- | --- |
| **D1 Evaluator** | Deciding whether to adopt | A requirement or a comparison | README, landing page | Repository root, package registry, search on the product name | What is this? Does it do X? Is it maintained? What does trying it cost? |
| **D2 First-time integrator** | Has decided; nothing runs yet | An empty project, a dependency line | Getting-started page, tutorial | Link from the README | What is the shortest path to something that works? |
| **D3 Task-doer** | Has a working setup and a goal | A goal in the product's terms ("stream replication", "use COPY", "connect through a proxy") | Feature page, how-to guide | Site navigation, search on the feature name | How do I do X with this? What do I set, call, or run? |
| **D4 Configurer** | Tuning or hardening a running system | A configuration file, a connection string, a deployment manifest, and a requirement (memory, latency, a limit) | The reference entry for one option | Search on the option name, a link from the feature page, the table of options | What does it control? Default, range, syntax, scope? What happens at the limit? How does it interact with Y? Since when? |
| **D5 Troubleshooter** | Something failed | An error message, an exception class, a log line, or a wrong result | Whatever the search engine returns for the literal string | Web search on the message text, a URL inside the message, an issue tracker | What does this mean? What causes it? Is it my configuration? What do I change? |
| **D6 Upgrader** | Moving between two versions | The version they run and the one they want | Migration guide, version markers on reference pages, the changelog | Release announcement, link from the changelog | What changed that I can observe? Must I act? Which option replaces the one I had? |
| **D7 Contributor** | Wants to change the product | A clone and a build | Development and contributing pages | Link from the README or the pull request template | How do I build, test, and submit? Which conventions apply? |

Two boundary notes for the pass to test. D6 overlaps the upgrading user of the change-description skill; the candidate
split is that the changelog *entry* belongs there and the migration guide, the deprecation notice, and the version
marker on a reference page belong here. D5 is the reader the current documentation rules serve worst: nothing in Pass
2 says that a page must be findable by the error text a product emits, although the change-description skill says
exactly that about the changelog entry.

# Questions

Answer each explicitly, and say when the evidence does not settle it.

## A. The reader model

1. **Is any of this studied?** Pass 1 found one observation study of API documentation use (Meng, Steinhardt and
   Schubert, 2019: systematic, opportunistic and pragmatic strategies) and two defect taxonomies. Those describe
   *strategies* and *defects*, not *situations*. Find work that observes or surveys documentation readers by the task
   they arrived with: developer web-search studies (what developers search for, how often the query is an error
   message, what they do with the result), API learning-obstacle studies (Robillard's line of work), studies of
   Stack Overflow questions as evidence of what documentation failed to answer, and any industry user research a docs
   team has published (Google, Stripe, Twilio, GitLab, Microsoft Learn, Write the Docs surveys). For each reader row,
   report the strongest evidence that the situation is common and the strongest evidence for how that reader enters
   the documentation.
2. **Which readers do the frameworks already name?** Diátaxis names four needs; DITA names three topic types; the Good
   Docs Project ships templates per page type; Google's and Microsoft's guides have audience sections; the Kubernetes
   site has "page types" and "user roles". Map each framework's categories onto the candidate table and report what
   the mapping loses in each direction.
3. **What does each reader read first, and where do they stop?** For each row, what the evidence says about the entry
   point (top of page, a heading reached by search, a table row, a code block) and about the moment the reader
   leaves. This decides what the first paragraph of a section owes and whether a table beats prose for that reader.

## B. The reference entry for a configuration item

The most common user-facing documentation item in a library, a driver, a server or a CLI is the entry for one option:
a connection property, a configuration key, a command-line flag, an environment variable, a system property. Pass 2
has rules about identifiers and numbers inside such an entry and nothing about its shape.

4. **What fields does a mature reference entry carry, and in what order?** Survey the conventions of projects whose
   option documentation is widely read and long maintained: PostgreSQL's runtime configuration reference (name, type,
   unit, default, context, description), the `man-pages(7)` conventions for OPTIONS, Git's `config.txt`, OpenSSH's
   `ssh_config(5)`, systemd's directive pages, the Kubernetes component flag references and API field conventions,
   Spring Boot's configuration metadata, Terraform provider schema documentation, the OpenAPI parameter object, and
   the reference chapters of the Google and Microsoft style guides. Report the union of fields, which fields every
   source carries, the order each source uses, and the rationale where one is stated. Candidate fields to test for:
   name as the code spells it; type; syntax and valid values; default, with its unit; scope (per process, per
   connection, per request); when it is read (startup, reload, each call); what it controls, as the claim; what
   happens at the limit or on an invalid value, including the literal error the reader will see; interactions with
   other options and with modes; since which version; deprecation and replacement.
5. **How do those projects document an option that interacts with another** (one option's effect depends on another,
   a mode switches a set of them off, a global setting overrides a per-connection one)? Report the placement each
   project chooses: in both entries, in one with a link, or in a separate section. This is the case the trial branch
   hit and the current skill has no rule for.
6. **Which of these fields does tooling generate or check?** Spring Boot's metadata, Kubernetes' generated flag
   references, Sphinx's `confval` directive, Rust's clap-derived help, Go's `flag` package help text: where the entry is
   generated from code, what remains for a hand-written page to say, and what the generated text gets wrong that a
   reviewer must still read for.

## C. Placement and ownership across a documentation set

A repository documents the same fact in several places: a docstring or Javadoc that ships as generated reference, a
README table, a reference page, a feature page, a changelog. Pass 2 settled that dual-sourced content should link to a
canonical source, as a rule for a page. It said nothing about how to act when the set already dual-sources by
convention, which is the normal state of a mature project.

7. **What do projects say about which copy is the record?** Search contribution guides and documentation policies for
   a stated source of truth for option documentation and for API documentation, and for the rule that derived copies
   summarize and link. Report which projects generate the derived copies, which maintain them by hand, and any stated
   rule about the order of entries in a table or list (alphabetical, by topic, by introduction date).
8. **How does a project decide what a change owes the documentation?** Search for the mechanisms: pull request
   template questions ("does this introduce a user-facing change?", "additional documentation"), labels and review
   gates (`needs-docs`, `docs-required`, a documentation checklist in a merge request template, "documentation is part
   of the definition of done"), commit conventions that require the documentation change in the same commit
   (PostgreSQL, Git, Django with `versionadded`), release-note tooling that reads a block from the pull request, and
   historical tags such as OpenStack's `DocImpact`. Report what each mechanism asks the author to enumerate, and
   derive from them the list of *promise-changing* changes an agent should scan a diff for: a new or removed option, a
   changed default, a new error message or exception, a changed limit, a new mode, a deprecation, a changed
   behavior of an existing option. Say which items the sources name and which are inferred.
9. **Where does the answer to an error go?** For the troubleshooter reader: survey how projects make a page findable by
   the literal error text. Candidates: error messages that carry a URL or a code the documentation indexes
   (`rustc --explain`, Next.js error pages, PostgreSQL's `HINT` and `DETAIL` fields, Kubernetes event reasons,
   Microsoft Learn error-code pages, Red Hat's Environment / Issue / Resolution / Root Cause article shape, Google's
   troubleshooting-page guidance), reference entries that quote the error the option triggers, and dedicated
   troubleshooting pages with a stated template. Report which shapes exist, what each requires of the code (a stable
   message, a code, a URL), and whether any evidence shows one shape being found more often than another.

## D. Structure heuristics the current rules lack

10. **When does a table beat prose, and when does a list beat both?** The structure chapters of the Google and
    Microsoft guides, Redish's *Letting Go of the Words*, and any measured reading study. State the rule as a test an
    agent can apply to a paragraph: the number of items, whether the reader compares them, whether each item has the
    same fields.
11. **When does a topic earn its own heading, and when its own page?** Headings are anchors that search and links
    reach (Pass 2, settled). What is the guidance on granularity: one question per heading, one task per page, page
    length limits, "if a reader would search for it, it has a heading"? Report stated rules and their rationale, and
    what the Kubernetes, Google and Diátaxis materials say about splitting a long page.
12. **Progressive disclosure inside a page.** For an option with a simple common case and a complex rare one (a
    default that fits nearly everyone, and an escape hatch for the rest), what do the sources say about ordering:
    common case first, the escape hatch under its own heading, a table for the rare interactions? Report any evidence
    that burying the common case behind the complete case costs readers.

# Evidence to prefer

Primary sources, official documentation, and issue trackers over commentary. A rule stated with its rationale over a
checklist. A studied claim over an asserted one, and say which is which. For each reader row and each candidate
procedure, the pass must say whether the evidence is a measurement, a stated policy of a named project, or an
inference from mechanics.

# Required output

A research report under 4000 words, with these sections in this order.

## 1. Executive summary

- Which rows of the reader table survive, which change, which are added, and on what basis.
- Whether the reference-entry shape converges across projects, and the fields every source carries.
- Whether any project states a "what a change owes the documentation" rule, and the list that follows from the
  mechanisms found.
- Which of the twelve questions the evidence settled, and which stayed open.

## 2. The reader table, revised

One row per reader: situation, what they hold, what they open, how they enter, what they ask, what they read first,
where they stop, sources, and the basis (studied, with the study and its sample; stated policy, with the project;
asserted). Keep the D-numbering for rows that survive so that the synthesis can cite them.

## 3. The reference entry

The field list with order, the sources that carry each field, the rationale where stated, and the rule for documenting
an interaction between options. Give two worked entries from real projects, quoted with their source, that carry most of
the fields, and one that omits a field the reader needs, with the field named.

## 4. Placement and the documentation a change owes

The source-of-truth findings, the ordering conventions, the mechanisms projects use to enforce documentation on a
change, and the derived scan list for a diff, with each item marked as named by a source or inferred. Then the
troubleshooter's path: the shapes that make a page findable by an error, what each requires of the code, and the
default to recommend when the code carries neither a code nor a URL.

## 5. Structure heuristics

The table-versus-prose test, the heading and page granularity rules, and the progressive-disclosure ordering, each with
sources and basis.

## 6. Test of the reader model

Apply the reader questions to three real documentation pages from different projects: one reference page of options,
one feature page, and one README. For each page, say which readers it serves, which question of theirs it answers in
the first paragraph of the relevant section, and which reader would leave without an answer. Then take two real merged
pull requests that added a configuration option in different projects, list what the scan list in section 4 would have
demanded, and report what the pull request actually changed in the documentation. The purpose is to check that the
questions discriminate, not to grade the projects.

## 7. Conflicts

Where sources disagree (a field's position, whether an interaction is documented in both entries, whether the README
carries the option table at all), both positions with their sources, which is better supported, and the default to
recommend, with what a project has to decide for itself.

## 8. What the synthesis should be told

What to carry into the skill, in which section, and what not to do: no wording rules, no re-derivation of the changelog
entry, no promotion of asserted rows to studied, no house style (a particular field order or template) presented as a
rule where the sources differ.
