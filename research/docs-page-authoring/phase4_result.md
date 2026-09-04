# Pass 4: A candidate rule set for documentation pages, by reader

This is a synthesis document, not a skill. It carries the evidence a later session needs to write a
repository-independent skill for user-facing documentation pages in a code repository: README, reference and option
pages, feature pages and how-to guides, tutorials, troubleshooting pages, migration guides. Every rule names the
reader whose need it exists for and the source it rests on. A house style (a field order, a page template, a heading
vocabulary) is a per-repository overlay and is kept out of the core.

Sources are `phase1_result.md`, `phase2_result.md`, and `phase3_result.md`. During synthesis the pass 2 and pass 3
claims about primary sources were checked against those sources in three parallel verification passes (the research
papers, the project policies and style guides, the pull requests and issues); the corrections are marked *corrected*
where they appear and collected in section 13.

Wording is out of scope throughout: voice, tense, sentence length, punctuation, hedging, dialect, and AI-writing tells
belong to `english-developer-style`. The changelog entry and the pull request description belong to
`change-description-authoring`; this document stops at that boundary and says so where it reaches it.

## 1. Reader table

No study observes documentation readers partitioned by the situation they arrived with. The table is an *asserted*
structuring device; two rows carry *studied* support for how common the situation is, and the entry points are
inferred from how search engines, tables of contents, and links work.

| Reader | Holds | Opens | Enters by | Asks | Reads first, stops when | Basis |
| --- | --- | --- | --- | --- | --- | --- |
| **D1 Evaluator** | A requirement or a comparison | README, landing page | Repository root, package registry, search on the product name | What is this? Does it do X? Is it maintained? What does trying it cost? | The first paragraph; stops at "no" or "not yet" | *Asserted*; supported indirectly by the README-scope conventions of standard-readme and purposeful-readme (pass 2) |
| **D2 First-time integrator** | An empty project, a dependency line | Getting-started page, tutorial | A link from the README | What is the shortest path to something that works? | The first code block or command; stops when it runs or the first step fails | *Asserted* for the row; *studied* for frequency: Robillard and DeLine, *A field study of API learning obstacles*, Empirical Software Engineering 16(6), 2011, over 440 professional developers, name code examples and matching an API to a scenario among the key documentation factors |
| **D3 Task-doer** | A goal in the product's terms | Feature page, how-to guide | Site navigation, search on the feature name | How do I do X? What do I set, call, or run? | The heading matching the goal; stops at the code block that does it | *Asserted* for the row; *studied* for frequency: Xia et al., *What do developers search for on the web?*, Empirical Software Engineering 2017, queries from 60 developers and a survey of 235, name reusable code snippets and solutions to common bugs among the most frequent search tasks |
| **D4 Configurer** | A configuration file, a connection string, a deployment manifest, and a requirement (memory, latency, a limit) | The reference entry for one option | Search on the option name, a link from the feature page, the options table | What does it control? Default, syntax, scope, when read? What happens at the limit? How does it interact with Y? Since when? | The default and the type; stops when the value and its scope are known | *Asserted* for the row; supported by the convergence of option-entry conventions across PostgreSQL, `man-pages(7)`, OpenAPI, Spring Boot, and the Good Docs Project (section 3) |
| **D5 Troubleshooter** | An error message, an exception class, a log line, a wrong result | Whatever a web search on the literal text returns | Web search on the message, a URL or code inside the message, the issue tracker | What does this mean? What causes it? Is it my configuration? What do I change? | The block that matches the error text; leaves the instant the string is not on the page | *Studied* for frequency: Xia et al. 2017 name explanations of exceptions and error messages among the most frequent search tasks; that a debug query is often the message pasted verbatim is an interviewee's account in the same study, not a measured rate (*corrected*). The row the pass 2 rules served worst |
| **D6 Upgrader** | The version they run and the one they want | Migration guide, version markers on reference pages, the changelog | Release announcement, a link from the changelog | What changed that I can observe? Must I act? Which option replaces the one I had? | The breaking-changes list or the version marker; stops when they know whether action is required | *Asserted*; boundary with the upgrading user of `change-description-authoring`: the changelog entry belongs there, the migration guide, the deprecation notice, and the reference-page version marker (Sphinx `versionadded`, `versionchanged`, `deprecated`; Django's preferred marker) belong here |
| **D7 Contributor** | A clone and a build | Development and contributing pages | A link from the README or the pull request template | How do I build, test, and submit? Which conventions apply? | The build and test commands; stops when the build passes | *Asserted*; the Good Docs Project and Kubernetes both ship a contributing content type or a contributor role table |

A reader of a generated API reference who lands on one method or field page is a variant of D3 and D4, served by the
same field discipline, and is not a row of its own.

The test that follows from the table, applied to every sentence: **name the reader and the question it answers.** A
sentence that answers none of the questions above belongs on another page, in the pull request description, or
nowhere. Sources: derived from the table; the same device `change-description-authoring` uses.

## 2. The section and its slots

**Four slots, in order: Claim, Contract, Rationale, Use.** Claim is always present; Contract is skipped when the claim
is the whole contract; Rationale is present only when the way is surprising; Use is skipped when the contract implies
it. *Asserted*: no source prescribes these four (pass 2, baseline audit). The order has one piece of evidence: Meng,
Steinhardt, and Schubert, *How Developers Use API Documentation: An Observation Study*, Communication Design
Quarterly 2019, observed two strategies, opportunistic and systematic (the third, pragmatic, is cited from Clarke
2007, not observed; *corrected*); the opportunistic readers did not read larger sections but searched for one thing
and scanned, so a claim that comes first is the only one they see. The authors' 2020 guidelines recommend presenting
conceptual information at the point of use, because developers avoid a separate concepts document whatever their
strategy (*corrected*: not an opportunistic trait).

**The first paragraph carries the section.** Open with the claim, not the topic; name the subject in the first
sentence; put the qualification after the claim. Serves D3, D4, D5, who arrive at a heading rather than at the top of
the page. *Studied in spirit, overstated in letter* (pass 2): Meng et al. support mid-page entry for opportunistic
readers; systematic readers do start at the top, so "nobody enters at the top" is wrong and "many do not" is
what the evidence carries.

**An example is not a slot.** It belongs to whichever slot it serves. Derived.

## 3. The option entry

The most common section in a reference is the entry for one option: a configuration key, a connection property, a
command-line flag, an environment variable, a system property. Readers: D4 first, then D5 arriving from the error the
option triggers, then D6 reading the version marker.

**Fields every surveyed source carries** (*stated policy*, pass 3): name as the code spells it; type and valid values;
default; what it controls. Sources: PostgreSQL runtime configuration
(<https://www.postgresql.org/docs/current/runtime-config.html>), `man-pages(7)`
(<https://man7.org/linux/man-pages/man7/man-pages.7.html>), the Good Docs Project reference template
(<https://thegooddocsproject.dev/template/reference>), the OpenAPI parameter object
(<https://spec.openapis.org/oas/v3.1.0#parameter-object>), Spring Boot configuration metadata
(<https://docs.spring.io/spring-boot/specification/configuration-metadata/>).

**Fields a minority carries, and that D4 and D5 need**: scope (PostgreSQL per cluster or per session; OpenAPI `in`);
when the value is read (PostgreSQL's `context`, listed in order of decreasing difficulty of changing the setting;
*stated policy* with rationale); the behavior at the limit or on an invalid value, with the literal error (PostgreSQL
inline prose; `man-pages` ERRORS; a minority); since which version (`man-pages(7)`, whose description of the VERSIONS section gives the rationale that users
constrained to older kernel or library versions need it; Django's preferred marker); deprecation and replacement (OpenAPI `deprecated`,
Spring Boot `deprecation.replacement`); interactions (prose with a cross-reference in PostgreSQL, SEE ALSO in
`man-pages`, absent from OpenAPI and Spring Boot).

**A default is a value with its unit, not the constant that holds it.** A reader cannot set `DEFAULT_MAX_SIZE`; they
can set `64 MB`. Derived from the specification-versus-implementation rule (section 5) and observed in the trial
(section 14), where seven internal constant names had reached user-facing text.

**Order, as a house default.** Name, type and valid values, default with unit, scope, when read, what it controls, what
happens at the limit with the literal error, interactions, since version, deprecation. *Inferred* from convergence:
PostgreSQL leads with name, type, and default; OpenAPI recommends its own field order; the Good Docs template is
flexible. Sources differ, so the skill presents this as a default and not as a rule. The trial found one adjustment
worth keeping: the claim (what it controls) reads better immediately after the header line, because D4's first
question after "which option" is "what does it do", and the type and default fit on the header line.

**Interactions.** Sources do not converge (pass 3, Q5). PostgreSQL documents an interaction in prose inside one entry
with a cross-reference (`hash_mem_multiplier` against `work_mem`); `man-pages` pushes it to SEE ALSO; OpenAPI has no
field. Default (*inferred*, an application of the pass 2 canonical-source rule): the detail lives once, in the entry of
the option that gates or overrides the other; the subordinate entry carries one sentence and a link. D4 opens either
entry and does not know which, which is why the subordinate entry may not be silent.

**What generated reference text cannot supply.** Spring Boot generates name, type, default, and deprecation from
annotations and merges a hand-written file over them (*stated policy*). What the generator cannot see, and a
hand-written page must add, is the interaction, the behavior at the limit, and the literal error; the hand-written
copy must not restate a generated field (section 6).

## 4. Genres and their failure modes

**One primary purpose per section, and no section switches purpose silently.** The stronger rule, one page per genre,
does not survive a real repository (pass 2, Q1, settled): a README is introduction plus how-to plus reference, a
migration guide is how-to plus explanation. Diátaxis itself says to use it as a guide, not a plan, while also
prescribing a structure strongly; the sentence pass 2 attributed to it, that a page is one and only one of the four
types, is not on the site, and its page on complex hierarchies permits nested hierarchies rather than mixed pages
(*corrected*). The weakening rests on the observed mixtures. Drift inside a section is the defect; mixtures at page
level are normal.

| Genre | Serves | Its job | How it fails | Sources |
| --- | --- | --- | --- | --- |
| README | D1, then D2 | What this is, who it is for, the shortest thing that works | Becoming the manual; embedding a changelog | standard-readme, purposeful-readme (pass 2) |
| Tutorial | D2 | Teach by a path guaranteed to work | Completeness; every option offered is a chance to fail | Diátaxis; Carroll's minimalism (pass 2) |
| How-to, feature page | D3 | Carry a reader with a stated goal from start to done | Stopping mid-procedure to explain why; not linking the options it depends on | Diátaxis; Kubernetes task page rule; trial (section 14) |
| Reference | D4 | State the contract, exhaustively, in a searchable order | Drifting into the implementation; prose where a table answers faster | Uddin and Robillard (incompleteness as a blocker); Diátaxis |
| Troubleshooting | D5 | From a symptom to its cause to the action | Explaining the mechanism before the fix; paraphrasing the error | DITA 1.3 troubleshooting topic (condition, cause, remedy); Red Hat's solution articles (Environment, Issue, Resolution, Root Cause; the KCS standard itself orders them Issue, Environment, Cause, Resolution; *corrected*); Good Docs troubleshooting template (pass 3) |
| Explanation | D3, D1 | The model behind the design | Turning into reference | Diátaxis |
| Migration guide | D6 | Carry a reader across a break, old and new side by side | Assuming the reader knows what broke | Baseline (pass 2, asserted); D6 boundary (section 1) |
| Contributing | D7 | Build, test, submit | Describing the ideal process rather than the one CI enforces | Good Docs; Kubernetes (asserted) |

Completeness and brevity are settled by genre, not by taste (pass 2, Q8): a reference of record is judged by coverage,
and Uddin and Robillard rank incompleteness among the severest defects; a tutorial or how-to is judged by whether the
reader gets through, which is Carroll's minimalism, and it omits edge cases and links to the reference.

## 5. What a page may claim

These rules are pass 2's and survive unchanged; they are listed here with their basis so the skill can cite them.

- **The specification, not the implementation.** The test: could this sentence stop being true without any user
  noticing a behavior change? Serves D3 and D4. *Studied* for the harm: Uddin and Robillard, *How API Documentation
  Fails*, IEEE Software 32(4), 2015, two surveys of 323 IBM software professionals who supplied 179 examples covering
  131 documentation units (*corrected*: one company, and 179 is the example count), rank incorrectness and
  obsoleteness among the severest defects, with six of ten problems classed as blockers. The
  normative-versus-informative distinction of RFC 2119 and RFC 8174 transfers; the uppercase keywords do not, and the
  OASIS keyword guidelines tell non-standards documents to avoid them (pass 2, Q6).
- **The state that holds, not the route to it.** `now`, `no longer`, `used to`, `previously` are the tells. History
  has three homes: the changelog entry (owned by `change-description-authoring`), the migration guide, and a named
  version marker on a reference page (Sphinx directives; Django's preferred marker). Reference pages drop markers
  below the oldest supported version (pass 2, Q2: NumPy issue 27239 proposes dropping directives for versions long
  out of use; CPython's `versionadded:: next` tooling; the "bloat" remark pass 2 attributed to Sphinx maintainers has
  no source, *corrected*).
  *Asserted* plus tool convention.
- **Every name the page states exists, spelled as the code spells it.** *Studied* for the failure rate: Tan, Wagner, and Treude,
  *Detecting outdated code element references in software repository documentation*, Empirical Software Engineering
  29(1), 2024 (DOCER; *corrected* authors), found 28.9% of the top-1000 GitHub projects with at least one outdated
  reference, surviving 4.7 years on average. A name that resolves to a private symbol is a second finding: the page is
  describing the implementation.
- **Every number is read out of the code**, unit and digits both, and a suffix has a stated base. Derived, and
  observed in the trial: `64 MB` beside `64,000,000` is a decimal suffix, and the page said so.
- **Every quoted error is the one the code emits**, whole or up to a marked cut. Serves D5; the rationale is section
  8. Derived from the D5 entry point.
- **A fenced example is a claim.** Where a doctest harness covers the file (`cargo test --doc`,
  `pytest --doctest-modules`, the Sphinx doctest builder, `mdbook test`), a stale example fails the build; where none
  does, the example is prose that rots in silence. *Stated policy* of each tool (pass 2). A snippet is not edited in
  a wording pass, and a snippet that contradicts the code is reported as a bug.
- **A heading is a URL anchor.** Rewording one breaks inbound links silently; a rename is a separate change with the
  redirect. An explicit `{#id}` attribute pins a heading's anchor; Hugo `aliases` and Docusaurus `slug:` pin a page's
  URL, one level up, and do not protect heading anchors (*corrected*). Two exceptions: a heading the branch
  introduced, and a heading whose anchor is pinned explicitly. *Asserted from mechanics*; intra-documentation anchor rot is
  unstudied (pass 2, Q4), and the general link-rot figures (Pew Research Center, *When Online Content Disappears*,
  2024: 38% of pages that existed in 2013 are not available today) measure the web, not a documentation set.

## 6. Placement and ownership

**One copy is the record; the others summarize and link.** *Stated policy*: Kubernetes forbids dual-sourced content
because it doubles the effort and goes stale faster (pass 2); Spring Boot generates the metadata from code and lets a
hand-written file override only description, default, and deprecation (pass 3). The counter-example is PostgreSQL, which keeps the GUC list in three
hand-maintained places (the source, `postgresql.conf`, and the SGML reference) and whose own wiki page *GUCS Overhaul*
says they "are only synched with each other manually". Serves D4 (one answer) and D7
(one place to update).

**What a derived copy carries.** The claim, the default, and a link to the record, in one or two sentences. It may omit
what the record says; it may not contradict it. Interactions, modes, and error texts stay in the record. *Derived*;
the trial supplied the failure case in both directions: one run shortened README rows and dropped the mode
interaction the record carried, so the copy contradicted the record by omission; the other kept every fact and the
row became the manual (section 14).

**A new item goes where its siblings are.** Into every place a sibling occupies, in that place's shape and in that
list's order, and into no new place. Ordering conventions (*stated policy*): `man-pages` fixes the section order and
sorts SEE ALSO by section number then name; PostgreSQL groups options by topic; the default is by topic within a page
and alphabetical only within a flat table (pass 3, Q7).

**A new section with no sibling goes beside the entries that point at it**, not at the end of the page. *Derived*
from the trial: one run placed the new limits section some four hundred lines below the entries that linked to it.

**The README boundary.** The README links to the reference; the option table lives in the reference; a README must
not contain a changelog and may link to one (purposeful-readme, *stated policy*). A project decides otherwise only
when it ships no separate documentation site (pass 3, section 7).

**The readers' paths cross pages, so the pages link.** The feature page D3 reads names and links every option it
depends on; the option entry quotes the error D5 searches for; the migration guide D6 reads links to the replacement
entry. *Derived* from the reader table; the trial found the missing link in both feature pages (replication and
COPY) that a new limit affected.

## 7. What a change owes the documentation

The question is "did the promise change", not "did the code change" (pass 2, §7). The scan list below is what an agent
checks a diff for; each item names the reader and the page it serves and carries pass 3's basis label.

| # | Change in the diff | Reader | Owes | Basis |
| --- | --- | --- | --- | --- |
| 1 | A new or removed option, flag, property, environment variable | D4, D3 | An entry in the reference; a row in every derived table; a mention on each feature page it affects | **Named**: OpenStack `DocImpact` ("an added/altered/removed command line option"); pull request templates |
| 2 | A changed default or limit | D4, D6 | The entry's header and version marker; a migration note if a working configuration can start failing | *Inferred* (implied by "altered option") |
| 3 | A new or changed error message, exception, or log line a user can see | D5 | The literal text in the entry or the troubleshooting page, with the cause and the action | *Inferred*; load-bearing because of the D5 evidence |
| 4 | A new mode, or a switch that changes several options at once | D4 | An entry of its own, and one sentence in every entry it touches | *Inferred* (a subset of "new feature") |
| 5 | A deprecation or replacement | D6, D4 | A deprecation note with the replacement; the old entry marked, not deleted, until the removing version ships | **Named**: OpenStack ("a deprecated or new feature"); Django's `versionchanged` marker and deprecation policy |
| 6 | A changed behavior of an existing option | D4, D6 | The entry rewritten as the state that holds; the history goes to the changelog | **Named**: OpenStack ("altered option") |
| 7 | A breaking change requiring user action | D6 | The migration guide | **Named**: the Angular-style pull request template's breaking-change question |
| 8 | A new public type or method; a supported version or platform added or dropped | D3; D1, D6 | The feature page and the generated reference it links to; the compatibility table | *Inferred* |

**Mechanisms that enforce it** (*stated policy*): OpenStack's `DocImpact` flag, which files a documentation bug from a
commit message and is still documented in the contributor guide (*corrected*: pass 3 called it retired; no source
says so); documentation in the same commit or patch in PostgreSQL, Git, and Django, with Django preferring a
`versionadded` or `versionchanged` marker on every new or changed feature (*corrected*: preferred, not required);
pull request templates that ask whether the change is breaking and whether docs were updated (Angular's template
asks the question under a bare heading with a comment requesting the impact and migration path; the parenthetical
pass 3 quoted is not in it, *corrected*);
`needs-docs` review gates in Microsoft Learn and GitLab. The reference entry is the record; the changelog entry is
written from it and links to it, not the other way around (derived; boundary with `change-description-authoring`).

## 8. The troubleshooter's path

D5 holds an error string and pastes it into a search engine; the page is found or it is not. Three shapes make a page
findable, each demanding something of the code (*stated policy*, pass 3):

| Shape | Example | Requires of the code |
| --- | --- | --- |
| The error carries a stable code the docs index | `rustc --explain E0592`; explanations live in `compiler/rustc_error_codes`, and the rule is to give an error a code when the explanation would say more than the error itself | A stable code |
| The error carries a URL | Next.js prints `nextjs.org/docs/messages/<slug>` so the logged message stays short and the page carries the description and the fix | A stable slug emitted by the code |
| A page quotes the literal error | PostgreSQL's `HINT` and `DETAIL`; DITA's troubleshooting topic (condition, cause, remedy); Red Hat's solution articles (Environment, Issue, Resolution, Root Cause) | Only that the page quote the string verbatim |

No evidence measures which shape is found more often; that stays open. **Default when the code emits neither a code
nor a URL**: quote the literal error verbatim in the reference entry of the option that triggers it, and on a
troubleshooting page keyed by the string where the error recurs. This is the rule pass 2 lacked for D5 and the one
`change-description-authoring` already applies to changelog entries. The trial confirmed the cost of the alternative:
the pre-trial page quoted a message the code no longer emitted, so a search on the real text would not have found it.

## 9. Structure heuristics

- **Table versus list versus prose.** *Stated policy*, Google developer documentation style guide: a table for items
  with three or more related pieces of information per item (the sentence sits in the page's summary box, the body
  says two-dimensional data; *corrected*) which the reader compares, a list for single-field items or term and definition pairs,
  prose when items are not parallel or carry conditional logic. Redish's *Letting Go of the Words* corroborates at
  trade-book level. No measured reading study was found; the rule is design guidance. The agent-applicable tell: a
  paragraph in which the same three or four nouns recur with different values wants a table; a cell holding a
  paragraph wants prose.
- **A topic earns a heading when a reader would search for it.** Headings are anchors (section 5), search engines and
  tables of contents land on them, so an option, an error, a task, and a mode each get a heading or at least a row
  with the name in it. *Stated policy* for granularity: Kubernetes ("Writing a new topic", not the content guide; *corrected*) gives a
  task page one thing to do, short or long as long as it stays on one area; Diátaxis has reference structure mirror the structure of the product. No source sets a
  length limit; splitting is triggered by mixed purpose, not by word count.
- **The common case first, the escape hatch after.** *Stated policy* for the direction: Google's prescriptive
  guidance (procedures reflect the most likely use, commands serve the most common case), Diátaxis, the Good Docs
  reference template; Redish's "grab and go". No measurement of the cost of burying the common case was found; the
  ordering rests on design guidance and is labeled *asserted*.

## 10. The three parties that check a page

From pass 2, section 7. **The sweep oracle**, where a project runs one, byte-compares headings, fences, front matter,
link targets, code spans, and issue references; the agent reports on them and cannot edit them in a prose pass. **A
linter or CI job** owns what is mechanical: markdownlint, a link checker, a doctest runner, a coverage lint, the
DOCER script for outdated code references (a script on Zenodo; the GitHub Action pass 2 described is the paper's
future work, *corrected*), a tag-versus-changelog check. **The reviewer, or an agent standing in for one**, owns what
needs the page and the source read together: implementation stated as contract, a stale identifier in a sentence that
still reads well, an unsupported claim, a section that changed purpose. Research tools for that class mostly fail
outside narrow slices (pass 2, Q5), so the structured agent report is the practical answer.

## 11. Editing and comparing

**Two modes, declared before the pass starts.** A *prose pass* changes wording and nothing else, so that "prose only" is
checkable by the oracle; a *structural revision*, which is what "update the docs for this branch" usually means, may
add and move sections, introduce tables, split headings, and delete paragraphs, with new headings free and shipped
headings renamed only with their redirect and listed for the reviewer. *Derived* from the trial: the pass 2 rules were
written for the sweep and forbade the skeleton edits the task required.

**The growth budget.** Net delta zero; growth is paid for by a fact the old version did not carry, and on a branch the
facts the change introduced are what pays. *Asserted* (baseline, pass 2). **Prefer deleting**: lifted limitations,
removed options, workarounds for unsupported versions, version markers below the supported window. **A released
changelog entry is not reworded**; only a factual error is fixed. *Asserted by analogy* with release-artifact
immutability (GitHub immutable releases, PyPI) and localization string freeze (pass 2, Q9).

**Comparing two versions.** Read the old version first and reach the verdict last: list the old facts, mark each
present, restated, or absent, defend every absence, count the delta only then, check the new claims against the code
rather than the old page, name the reader of each new sentence, and name the finding. The taxonomy, extended by the
trial: lost fact, unpaid growth, unsupported claim, implementation stated as
contract, author's seat, history narration, stale identifier or number or error text, contradicted by the code, common
case buried, missing heading or row, interaction stated once, error not quoted, sibling place not updated, purpose
drift, duplicated canonical content, churn, reworded skeleton, edited released entry. *Asserted*.

## 12. Conflicts and how they were decided

| Conflict | Positions | Decision | Reader who won |
| --- | --- | --- | --- |
| One page, one genre | The pass 1 reading of Diátaxis against every real README and migration guide (Diátaxis's text prescribes a structure strongly and calls itself a guide, not a plan) | One primary purpose per section; failure modes kept as heuristics (pass 2, Q1) | D3 and D4, who arrive at a section, not a page; D1 is not harmed |
| Version markers against accumulation | Keep a Changelog's entry per version against NumPy maintainers proposing to drop `versionchanged` directives for versions long out of use (issue 27239) and CPython's `next` tooling | The changelog keeps history; the reference page drops markers below the supported window (pass 2, Q2) | D4; D6 keeps the changelog |
| Changelog in the README | purposeful-readme's prohibition against common practice | Link only (pass 2, Q3) | D1 |
| Uppercase MUST in ordinary docs | RFC 2119 boilerplate against OASIS's advice to non-standards documents | The distinction transfers; the vocabulary does not (pass 2, Q6) | D4 |
| Minimalism against completeness | Carroll against Uddin and Robillard | By genre: completeness for the reference of record, minimalism elsewhere (pass 2, Q8) | D4 and D2 each in their genre |
| Where an interaction is documented | PostgreSQL's prose in one entry against `man-pages` SEE ALSO | Detail in the gating entry; one sentence and a link in the other (pass 3, Q5) | D4; no reader harmed |
| Field order of an option entry | PostgreSQL, OpenAPI, Good Docs differ | A house default, labeled as such (pass 3) | none; the skill must not present one order as the rule |
| Option table in the README | purposeful-readme's minimal README against projects with no docs site | README links to the reference unless the project has no reference (pass 3) | D1; D4 is served by the link |
| Length of a derived copy | Consistency with the record against brevity | Claim, default, link; may omit, may not contradict (section 6) | D4 opens the record; D1 reads the copy |
| Generated against hand-written reference | Spring Boot and Kubernetes generate; PostgreSQL hand-writes | Generate the mechanical fields, hand-write what the generator cannot see, never restate a generated field (pass 3) | D4; D7 by fewer places to update |

## 13. Evidence map

**Measured** (the studies, named once):

- Uddin and Robillard, *How API Documentation Fails*, IEEE Software 32(4):68–75, 2015 (DOI 10.1109/MS.2014.80):
  two surveys of 323 IBM software professionals, who supplied 179 examples over 131 documentation units; ambiguity,
  incompleteness, and incorrectness severest; six of ten problems are blockers. Backs the specification rule and
  reference completeness.
- Aghajani et al., *Software Documentation Issues Unveiled*, ICSE 2019: 878 artifacts from mailing lists, Stack
  Overflow, issue trackers, and pull requests; 162 issue types. *Software Documentation: The Practitioners'
  Perspective*, ICSE 2020, finds that only a small subset of those types is rated important by practitioners, with
  clarity rated highest. Backs the defect taxonomy.
- Meng, Steinhardt, and Schubert, *How Developers Use API Documentation: An Observation Study*, Communication Design
  Quarterly, 2019: opportunistic and systematic strategies observed. Backs claim-first and concepts at the point of use.
- Robillard and DeLine, *A field study of API learning obstacles*, Empirical Software Engineering 16(6), 2011: over
  440 professional developers. Backs the frequency of D2 and D3.
- Xia et al., *What do developers search for on the web?*, Empirical Software Engineering, 2017: queries from 60
  developers and a survey of 235 engineers. Backs the frequency of D5 and D3 and the literal-error rule; reusable
  code snippets appear in both the most frequent and the most difficult lists.
- Tan, Wagner, and Treude, *Detecting outdated code element references in software repository documentation*,
  Empirical Software Engineering 29(1), 2024 (DOCER): 28.9% (265 of 918) of the top-1000 GitHub projects carry an
  outdated reference, 5.4% of 2,279 Google projects, surviving 4.7 years on average. Backs the identifier rule.
- Carroll, *The Nurnberg Funnel*, MIT Press, 1990: minimalism. Backs the tutorial and how-to genre rules.

**Stated policy** (a named project or standards body): RFC 2119 and 8174 with OASIS; Keep a Changelog and Common
Changelog; Kubernetes; the Google style guide; PostgreSQL; `man-pages(7)`; Django; Spring Boot; OpenStack's
`DocImpact`; Rust's error codes; Next.js's error URLs; DITA 1.3 and Red Hat; purposeful-readme and standard-readme;
Diátaxis; the doctest tools; Hugo and Docusaurus.

**Inferred from mechanics or from the trial**: the D-table entry points; the derived-copy rule; the placement of a new
section; the scan-list items marked inferred; the interaction default; the option-entry order; the two editing modes.

**Asserted**: the reader table as a partition; the four slots; the growth budget; released-entry immutability; the
comparison protocol; the common-case-first ordering; the anchor rule's scale.

**Corrections made during verification**, each marked *corrected* where it appears above:

- DOCER's authors are Tan, Wagner, and Treude (EMSE 29(1), 2024), not "Wan et al."; the tool is a script on Zenodo,
  and a GitHub Action is the paper's future work; the 28.9% figure is the top-1000 dataset, and a second dataset of
  Google projects shows 5.4%.
- Uddin and Robillard surveyed 323 IBM professionals, one company; 179 is the number of examples, over 131
  documentation units; the DOI year segment is 2014.
- Aghajani et al. 2020 rate clarity highest and find only a small subset of the 162 types important; pass 1's
  "completeness and up-to-dateness rated top" describes prior literature, not the result.
- Meng et al. observed two strategies; "pragmatic" is cited from Clarke 2007. Avoiding a concepts document is
  independent of strategy.
- Diátaxis does not say a page is "one and only one" type, and "compass, not a cage" is a third-party gloss; the site
  says "four and only four types" of the taxonomy, "use Diátaxis as a guide, not a plan", and "strongly prescribes a
  structure". Its complex-hierarchies page, now offline, permits hierarchies, not mixed pages. Tom Johnson's post
  raises the siloing objection and resolves it in the framework's favor.
- Xia et al.: the error-message-pasting behavior is an interviewee quote, not a measured rate.
- PostgreSQL: "It is never searched for function or operator names" is about the temporary schema, not `search_path`;
  the `context` list is in the `pg_settings` reference; the wiki page is *GUCS Overhaul* and names `postgresql.conf`
  and `settings.sgml`.
- `man-pages(7)`: the version-information rationale sits in the DESCRIPTION of the VERSIONS section.
- Django: the version marker is the "preferred way", not a requirement; the two-release removal is exact.
- Google: "state the location before the action" is the summary table's wording, the body says "goal before the
  action"; the three-or-more-pieces sentence is from the summary box.
- Kubernetes: the task-page quotes are from "Writing a new topic", not the content guide.
- Next.js: the guide never states the URL pattern; it is confirmed from the build source.
- Angular: the template's breaking-change question has no parenthetical; the checklist item is exact.
- OpenStack `DocImpact` is not retired; the trigger list is verbatim on the wiki, and the maintained guide drops "or
  if you're just not sure".
- PostgreSQL commit 9877374 (Tom Lane, 2021-01-06) edits `config.sgml` in the same commit, but the sentence pass 3
  quoted is from the commit message; the doc entry states the behavior in its own words.
- Prometheus PR 12019: the "a little bit vague" comment was left by a reader six months after the merge, not by a
  reviewer.
- The Sphinx maintainers' "bloat" remark has no source; the concern is NumPy issue 27239's.
- Red Hat's portal articles order the sections Environment, Issue, Resolution, Root Cause; KCS itself orders them
  Issue, Environment, Cause, Resolution, and the sections are a template, not mandatory.
- Docusaurus `id:` and `slug:` pin a page's URL, not a heading's anchor.
- Pew: "not available today", not "no longer accessible a decade later".

## 14. Test of the rule set

**The trial branch.** A JDBC driver branch (pgjdbc, pull request 4016) added two connection properties, a JVM system
property that switches a family of protocol limits, changed the failure behavior of an existing property, and
introduced a family of error messages. The pre-trial documentation, written without the skill, had: the limits table
and four paragraphs of protocol rationale inside a two-entry list of system properties; seven internal constant names
in user-facing text; a quoted error whose wording the code no longer emitted; one of two failure modes of the changed
property described as if it covered both; no mention of the new limit on the two feature pages (replication, COPY)
it affected; README rows longer than any neighbor.

The reader questions and the scan list demanded an option entry per property with the error at the limit and the
mode interaction (D4, items 1 and 4), the literal error where a search lands (D5, item 3), the changed property
rewritten as the state that holds (item 6), a mention on each affected feature page (item 1), and consistent README
rows (section 6). Two runs on the same prompt, judged blind against the code:

| | Pass 2 rules only | Rules with the reader table, option entry, scan list, placement |
| --- | --- | --- |
| Assertions passed (of 14) | 9 | 13 |
| Comparator score (of 10) | 7.0 | 9.7 |
| Quoted errors matching the code | 1 of 1, then generalized into a claim the code contradicts | 9 of 9 |
| Feature pages linked | replication only | replication and COPY |
| README rows against the record | dropped the mode interaction | consistent, but long |
| Claims contradicted by the code | 4 | 0 |

Both runs found the stale error text and removed the constants; both left the system property without a heading of its
own, following the page's list convention, which is the one assertion both failed and the skill should not force. The
second run's weaknesses became rules: the derived-copy length (section 6), the placement of a new section (section 6),
and quoting an error whole or up to a marked cut (section 5).

**Pass 3's tests**: a PostgreSQL reference page served D4 and not D5 (no literal error quoted); a Kubernetes task
page served D3 and sent D1 and D4 elsewhere by design; a README never serves D5, which confirms that D5 enters by
search. On two pull requests that added an option, the scan list matched what a PostgreSQL commit already did
(`idle_session_timeout`: entry, default, context, and the sibling interaction in the same commit) and would have
demanded what a Prometheus pull request omitted (`scrape_config_files`: no default or unset behavior, which a reader
called vague six months after the merge; *corrected*: not a reviewer).

**What the test established.** The questions and the scan list discriminate across four projects, and produced one
false positive worth a rule: a heading demanded for an item whose siblings are list entries, where the entry with the
name in it is the landing place.

## 15. Load-bearing versus refinement

**Load-bearing**, kept under any budget: the reader table and the name-the-reader test (section 1); the
specification-versus-implementation rule and the history rule (section 5); the option entry's universal fields plus
the error at the limit and the interaction (section 3); the literal-error rule (section 8); the scan list (section 7);
one copy is the record, with the derived-copy rule (section 6); identifiers and numbers read from the code (section
5); the anchor rule (section 5); the two editing modes and the comparison protocol (section 11).

**Refinements**, dropped first: the table-versus-prose tell; the common-case-first ordering; the heading-granularity
rule; the version-marker retention rule; the contributing genre row; the generated-versus-hand-written discussion; the
list of research inconsistency detectors; the doctest tool names beyond one example.

## 16. What the skill-writing session should be told

Do:

- Build the skill around the reader table; every rule names its reader first. Keep the slots of a section and add the
  option entry as a second slot table, with its order stated as the default the entry follows unless the page's
  siblings follow another.
- Carry the scan list of section 7 as the skill's answer to "what does this branch owe the docs", and the
  when-to-write-nothing list beside it.
- Make the literal-error rule explicit for D5, and the derived-copy and new-section placement rules explicit for the
  README and feature pages.
- Keep the two editing modes, and make the comparison protocol name the reader of every new sentence.
- Keep the worked example as an option entry written from the author's seat and then from the reader's.

Do not:

- Restate or re-derive wording rules; defer to `english-developer-style` in one sentence.
- Re-derive the changelog entry or the pull request description; defer to `change-description-authoring` and stop at
  the D6 boundary.
- Present the option-entry order, a page template, or a heading vocabulary as a rule; they are house defaults.
- Promote any reader row to studied as a situation, or present the common-case-first ordering as measured.
- Put research provenance, citations, or studied-and-asserted labels in the skill body; they live here.
- Force a heading on an item whose siblings are list entries; a row or an entry with the name in it is the landing
  place.
