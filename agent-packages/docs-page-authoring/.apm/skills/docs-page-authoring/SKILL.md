---
name: docs-page-authoring
description: >-
  Load before writing or editing a documentation page in a repository: a README, a reference or
  options page, a feature page, a how-to, a tutorial, a troubleshooting page, a migration guide.
  Inside a coding task, load it as soon as the change adds, renames, or removes an option, a
  property, a flag, an environment variable, an error a user can see, or a supported version, even
  where the task said nothing about docs: that change owes the documentation an entry, and this
  skill says which page and which slots. Also load for "update the docs", "document this", "does
  this need docs", or a review of a page or a section. Governs what a page says, for whom, in what
  order, and what it may not claim: the readers and their questions, the slots of a section and of
  an option entry, the promise rather than the code, headings as anchors, claims a machine checks.
  Wording is english-developer-style's and the changelog entry change-description-authoring's; load
  those too.
---

# Authoring a documentation page

This skill governs **what a page says, for whom, in what order, and what it may not claim**. Wording, tone, sentence
length, and dialect belong to `english-developer-style`; load it too, and let it own the sentences. The changelog entry
and the pull request description belong to `change-description-authoring`. Layout a linter settles, such as line
length, one H1, named links, and a language tag on every fence, belongs to the repository's markdownlint configuration.

A page is not read; a section is, by a reader who arrived with a question and leaves when it is answered. Every rule
below names that reader, because the same sentence is essential to one reader and noise to another, and the only way
to decide is to ask whose question it answers.

## 1. The correction that matters most

**Write from the reader's seat, not the author's.** The author has just finished understanding the code and wants to
explain it: how the mechanism works, why the design is right, what changed since last time. None of the readers below
asked that. Each holds one thing and brings one question, and a section earns its place by answering it.

| Reader | Holds | Opens | Asks |
| --- | --- | --- | --- |
| **D1 Evaluator** | A requirement, a comparison | README, landing page | What is this? Does it do X? What does trying it cost? |
| **D2 First-time integrator** | An empty project | Getting-started page, tutorial | What is the shortest path to something that works? |
| **D3 Task-doer** | A goal in the product's terms | Feature page, how-to guide | How do I do X? What do I set, call, or run? |
| **D4 Configurer** | A config file, a connection string, a requirement (memory, latency, a limit) | The reference entry for one option | What does it control? Default, syntax, scope? What happens at the limit? How does it interact with Y? |
| **D5 Troubleshooter** | An error message, an exception, a log line, a wrong result | Whatever a web search on the literal text returns | What does this mean? What causes it? What do I change? |
| **D6 Upgrader** | Two versions | Migration guide, version markers, changelog | What changed that I can observe? Must I act? |
| **D7 Contributor** | A clone and a build | Development and contributing pages | How do I build, test, and submit? |

The test, applied to every sentence: **name the reader and the question it answers.** A sentence that answers none of
them belongs on another page, in the pull request description, or nowhere. The tells of the author's seat are a
mechanism no reader must reason about, a rationale for a decision no reader questioned, the name of a constant or a
class the reader cannot type into their configuration, and history.

**State the promise, not the code.** D3 and D4 are deciding what they may rely on. A fact about today's code that a
safe refactoring is free to break makes the page wrong the day it breaks, and nobody edits the page. The test: *could
this sentence stop being true without any user noticing a behavior change?* If it could, it describes the
implementation.

- *Implementation:* "The driver builds a `PreparedStatement` after the fifth execution and caches it on the connection."
- *Promise:* "A statement is prepared on the server after `prepareThreshold` executions. Set `prepareThreshold=0` to
  disable that."

This is not a ban on mechanism. A page explains mechanism whenever the reader has to reason about it: a threshold they
configure, a resource they must close, an ordering they can observe. What it must not do is describe the current code
path as though it were the promise, or name the internals that hold a value. A default is a number with a unit, not the
constant that stores it; `64 MB` is a promise, `DEFAULT_MAX_SIZE` is a symbol the reader cannot set.

**Describe the state that holds, not the route to it.** "This used to return `null`, but since the fix in 4.7.5 it
throws" is two versions in one sentence, and the reader has one. `now`, `no longer`, `used to`, `previously`, and
`instead of the old` are the tells. History has three homes, and only three: a changelog entry, whose whole subject is
the difference between two versions; a migration guide, which carries D6 across that difference; and a **named version
marker** on a reference page (`Since 4.8.0`, a deprecation notice, a compatibility table), where the version is named
rather than narrated, which is what makes it checkable.

## 2. The slots

### A section

At most four slots, in this order.

| # | Slot | Answers | Skip when |
| --- | --- | --- | --- |
| 1 | **Claim** | What is true, or what does this do? | Never; always present |
| 2 | **Contract** | What may the reader rely on? What do they owe in return? | The claim is the whole contract |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader type, set, or call next? | The contract already implies it |

Rationale comes after contract because a reader who accepts the contract can stop reading, and one who does not is
the only one who needs the reason. An example is not a slot: it belongs to whichever slot it serves, and one that
serves neither is decoration. A concept belongs at its point of use, not in a concept section at the top: D3 and D4
skip that section and arrive mid-page.

### An option entry

The most common section in a reference is the entry for one option: a configuration key, a connection property, a
command-line flag, an environment variable, a system property. It is read by D4, who holds a configuration and a
requirement, and by D5, who arrived from the error the option triggers. Its slots, in order:

| # | Slot | Owes |
| --- | --- | --- |
| 1 | **Header** | The name as the code spells it, the type, the default as a value with its unit, and what "unset" means when the default is unset |
| 2 | **Claim** | What it controls, in one sentence, before anything about why |
| 3 | **Values** | Syntax, valid range, units, and the forms accepted, including whether a suffix is decimal or binary |
| 4 | **Scope** | Per process, per connection, per call; when it is read (startup, reload, each use); whether a URL, a file, or a property object can set it |
| 5 | **At the limit** | What the reader observes when the value is exceeded or invalid: the literal error, and what to do about it |
| 6 | **Interactions** | Every other option or mode that changes this one's effect, in one sentence each, with a link to the entry that owns the detail |
| 7 | **When to change it** | The situation that calls for a value other than the default; the default first, the escape hatch after |
| 8 | **Version** | `Since X.Y`, where X.Y is the version the branch ships in, read from the build metadata; deprecation; replacement |

The order is a default: where the page's existing entries follow another order, follow theirs, and carry every slot
regardless. Rationale for the default is optional, last, and one sentence, present only where a reader would
otherwise mistrust the number. Slot 5 is what D5 searches for, so the error is quoted as the code emits it. Slot 6
is stated in **both** entries of an interacting pair, because D4 opens one of them and does not know which; the
detail lives in one, and the other says one sentence and links. An entry that opens with mechanism or rationale
before the claim was written from the author's seat (§1).

## 3. Where the reader enters, and what they see first

D3, D4, and D5 do not start at the top of the page. They arrive at a heading from a search engine, from another page,
from a table row, or from an error message, and they read one paragraph before deciding whether this is the section
they wanted. Some readers do start at the top; enough do not that the first paragraph of every section has to stand
alone.

- Open with the claim, not the topic. "This section describes connection failover" tells the reader only that they
  have not been told anything yet.
- Name the subject in the first sentence, so the paragraph survives being read on its own.
- Put the qualification after the claim. "Failover is per connection attempt, not per query" reads in one pass;
  "Note that, subject to the settings described below, …" does not.

**The common case first, the escape hatch after.** A reader who stops after the first paragraph should hold the answer
that fits most readers: the default, the one property to set, the one command to run. The rare case, the override, the
mode that switches checks off, goes under its own heading or its own row, where the reader who needs it can find it and
the reader who does not is not made to read it.

**A topic earns a heading when a reader would search for it.** D4 searches on an option name and D5 on an error text,
and a search engine and a table of contents both land on headings, not on paragraphs. An option, an error, a task, a
mode: each gets a heading, or at least a table row or a list entry with the name in it, so that the search has
somewhere to land. Where a page documents its options as list entries, a new option is a list entry too (§4), not a
heading that breaks the pattern.
Conversely, a heading nobody would search for (`Overview`, `Details`, `Notes`) is a paragraph that lost its claim.

**A table beats prose when the reader compares.** Three or more items with the same fields, which the reader scans to
pick one, go in a table with one column per field. A sequence the reader performs goes in a numbered list. Everything
else is prose. The tell for a missing table is a paragraph in which the same three or four nouns recur with different
values; the tell for a table that should be prose is a cell holding a paragraph.

## 4. Purpose, genre, and where a fact lives

**One primary purpose per section, and no section switches purpose silently.** The stronger rule, one page per genre,
does not survive contact with a repository: a README is introduction plus how-to plus reference, a migration guide is
how-to plus explanation. Mixtures are normal at page level; drift inside a section is the defect.

| Genre | Serves | Its job | How it fails |
| --- | --- | --- | --- |
| **README** | D1, then D2 | What this is, who it is for, the shortest thing that works | Becoming the manual; embedding a changelog instead of linking to one |
| **Tutorial** | D2 | Teach by a path guaranteed to work | Completeness; every option offered is a chance to fail |
| **How-to, feature page** | D3 | Carry a reader with a stated goal from start to done | Stopping mid-procedure to explain why; not linking the options it depends on |
| **Reference** | D4 | State the contract, exhaustively, in a searchable order | Drifting into the current implementation (§1); prose where a table would answer faster |
| **Troubleshooting** | D5 | From a symptom to its cause to the action | Explaining the mechanism before naming the fix; paraphrasing the error instead of quoting it |
| **Explanation** | D3, D1 | Give the model behind the design | Turning into reference by listing every parameter it mentions |
| **Migration guide** | D6 | Carry a reader across a break, old and new side by side | Assuming the reader already knows what broke |
| **Contributing, development** | D7 | Build, test, submit | Describing the ideal process rather than the one CI enforces |

Completeness and brevity are settled by genre, not by taste. A reference is judged by coverage; a tutorial or how-to
is judged by whether the reader gets through, so it omits edge cases and links to the reference.

**A reference inherits the code's vocabulary.** Name a property, class, or flag exactly as the code names it. A page
that calls it "the prepare threshold" while the code calls it `prepareThreshold` costs every reader a search that
returns nothing.

**One copy is the record; the others summarize and link.** A mature docs set carries the same fact in several places:
a docstring that ships as generated reference, a README table, a reference page, a feature page. That is not a defect
to repair in passing. Find where the nearest sibling of the thing you are documenting already lives, and follow it:

- the copy with the most detail is the record, usually the reference page or the generated API reference;
- every other copy is short: the claim, the default, and a link to the record. It may omit what the record says; it
  may not contradict it. Interactions, modes, and error texts live in the record, or the copy becomes the manual;
- a new item goes into every place a sibling occupies, in that place's shape and in that list's order (alphabetical,
  by topic, or beside the option it interacts with), and into no new place;
- content that has a canonical source outside the repository is linked, not copied; the copy is the one nobody
  remembers to update;
- a new section with no sibling goes beside the entries that point at it, not at the end of the page, so that a
  reader who followed the link finds the answer within a scroll.

**The readers' paths cross pages, so the pages link.** The feature page D3 reads names every option it depends on and
links to each entry. The option entry quotes the error D5 will search for, and the troubleshooting page, where one
exists, names the option. The migration guide D6 reads links to the entry that replaced the one they had.

## 5. Links, and headings as anchors

**A heading is a URL anchor.** It is addressed as `#loading-the-driver` from other pages, from issues, from answers on
other sites, and from links nobody in this repository can see. Rewording one breaks every inbound link silently: no
build fails, and the page still renders. So a heading rename is a separate change, made deliberately and with the
aliases or redirects the site needs, never a side effect of a wording pass.

Two exceptions. A heading this branch introduced has no inbound links yet, so its wording is still yours. And a
heading whose anchor is pinned explicitly, with an `{#explicit-id}` attribute or a site that generates ids
independently of the words, has already separated the words from the address. A page move is the same problem one
level up: a Hugo `aliases` entry or a Docusaurus `slug:` keeps the old URL answering, and protects nothing below it.

For links themselves: link text names the destination; a relative link survives a domain move; a link to a source file
names the symbol rather than a line number, because line numbers rot on the next commit.

## 6. Claims a machine could check

A page carries text that is not prose, and rewording any of it is a behavior change: **front matter** (`aliases` are
live URLs), **fenced code blocks** including the info string, **shortcodes and directive comments**, **inline code
spans and issue references**. `binaryTransfer` and `#3837` are facts with exact spellings, not phrasings.

**A fenced example is a claim.** Where a doctest harness covers the file (`cargo test --doc`,
`pytest --doctest-modules`, the Sphinx doctest builder, `mdbook test`), the fence is a test and a stale example fails
the build. Where no harness covers it, the fence is prose that looks authoritative and rots in silence. Know which
case you are in, and prefer moving an important example into a harness over polishing it. Either way, do not edit a
snippet as part of a wording pass, and when a snippet contradicts the code, report it as a bug rather than rewording
around it.

**Every name the page states must exist**, spelled as the code spells it: an identifier, a configuration key, a flag,
an environment variable. Grep each one. A name that resolves to a private symbol is a second finding: the page is
describing the implementation (§1).

**Every number the page states is read out of the code**, not out of the sentence around it: a limit, a default, a
timeout. A size or duration carries a unit and digits, and both halves need checking; `64 MB` beside a constant of
`67108864` is the harder mismatch to see. A suffix has a base: say whether `1M` is 1,000,000 or 1,048,576 where the
reader could get it wrong.

**Every error the page quotes is the one the code emits.** D5 searches the literal text; a paraphrase matches nothing.
Quote the message as emitted, whole or up to a marked cut, with its placeholders shown as placeholders, and check it
against the source string or the message bundle.

Three parties enforce this, and confusing them wastes attention. A **sweep oracle**, where the project runs one,
byte-compares headings, fences, front matter, link targets, and code spans, so a prose pass never has to check them
and also cannot change them. A **linter or CI job** owns what is mechanical: markdownlint for heading structure and
fence languages, a link checker for dead links and broken fragments, a doctest runner for examples. **You** own what
is left, and it is the valuable half: everything that needs the page and the source read together.

## 7. What a change owes the documentation

The question is not "did the code change" but "did the promise change." Most branches change no promise and owe no
page. Scan the diff for the changes that do, and for each one name the reader and the page:

| Change in the diff | Reader | Owes |
| --- | --- | --- |
| A new option, flag, property, or environment variable | D4, D3 | An entry in the reference (§2), a row in every derived table (§4), a mention on each feature page it affects |
| A removed or renamed option | D6, D4 | A deprecation or migration note with the replacement; the old entry marked, not deleted, until the version that removes it ships |
| A changed default or limit | D4, D6 | The header and the version marker of the entry; a migration note if a working configuration can start failing |
| A new mode, or a switch that changes several options at once | D4 | An entry of its own, and one sentence in every entry it touches (§2, slot 6) |
| A new or changed error, exception, or log line a user can see | D5 | The literal text in the entry or the troubleshooting page that names the cause and the action |
| A changed behavior of an existing option | D4, D6 | The entry, rewritten as the state that holds (§1); the history goes to the changelog |
| A new public type or method | D3 | The feature page that shows the task, and the generated reference it links to |
| A supported version or platform added or dropped | D1, D6 | The compatibility table |
| A change that makes a working configuration or program fail | D6 | The migration guide, with the old and the new side by side |

The entry in the reference is the record; the changelog entry, which `change-description-authoring` governs, is
written from it and links to it, not the other way around.

**When to write nothing.** Every page is a claim somebody has to keep true. Do not write a page that restates a
generated API reference; a section explaining what the reader can see from the signature or the CLI help; a rationale
for a decision nobody would question; a note about a change that a changelog entry already carries; a changelog inside
a README. A change that alters no contract needs no documentation change, and adding one anyway creates a second place
to keep in sync.

## 7a. Editing an existing page

Most of the time you are not writing a page; you are rewriting part of one, and the work runs in one of two modes.
Say which before you start, because the rules differ.

**A prose pass** changes wording and nothing else. Headings, fences, front matter, code spans, and link targets stay
byte-identical, so that "prose only" is checkable and a sweep oracle can prove it. Anything wrong in the skeleton is
reported, not fixed.

**A structural revision**, which is what "update the docs for this branch" usually means, may add sections, move
content between pages, introduce a table, split a heading, or delete a paragraph. Headings the branch introduces are
free; a heading that already shipped is renamed only with its redirect (§5), and the revision lists every heading it
renamed or removed so a reviewer can check the redirects. Code blocks still change only when the code they show
changed.

In either mode:

- **Budget the net delta at zero.** Restructuring is free. Growth is paid for by a fact the old version did not carry:
  a bound, a default, a failure mode, a version, an interaction. Name the fact to yourself; if you cannot, you are
  rephrasing, and the old wording stays. On a branch, the facts the change introduced are what pays. One more payment
  holds: unpacking an over-compressed sentence, one of the shapes `english-developer-style` §4 tabulates, adds words
  and no fact and is not churn; name the construction you unpacked instead of a fact.
- **Check every name the section mentions.** A page written before a refactor cites properties, classes, and methods
  that no longer exist, and nothing in a Markdown toolchain notices. Grep each one, and check the sentence around it.
- **Prefer deleting.** A limitation that was lifted, an option that was removed, a workaround for a version out of
  support, version markers below the oldest version the project still supports: cutting these is usually the
  highest-value edit in the diff, even though the result looks like less work.
- **A released entry is not yours to reword.** A changelog entry under a version that shipped has been read, quoted in
  issues, and linked. Fix a factual error and leave the wording alone.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions: reviewing
someone else's edit, checking your own before you commit, or judging a generated one. It is the rubric a sweep's
sweeper and judge both work from.

The new version will read better; it was written second, by someone who had just finished understanding the subject.
Reading forward confirms that impression and finds nothing, because a fact that vanished leaves no trace in the text
that replaced it. So the work runs backwards: read the **old** version first, and reach the verdict last.

1. **List the old version's facts before you read the new one.** One fact is one bound, one default, one required
   call, one ordering constraint, one version, one failure mode, one identifier, one link target, one stated
   guarantee, one interaction. A topic sentence is not a fact. Compare facts, not sentences.
2. **Mark each fact present, restated, or absent.** Absent needs a defense in words, and three hold: the fact was
   wrong; it moved, and you can point at the sentence that now carries it; it belongs to a purpose this section does
   not serve and moved to the page that owns it. Three do not: *the code implies it*, *the new wording covers it*,
   *it was obvious anyway*.
3. **Only now count the delta**, under §7a's budget.
4. **Check what the new version asserts without support.** Every claim traces to the code, to the old page, or to a
   contract it links to. The commit message and the pull request description are not sources: they record what
   someone meant to do.
5. **Check the claims against the code, not against the old page.** For each identifier, number, and quoted error the
   section names, find it, then ask whether the sentence around it is still true. A section that survives every
   other step and fails this one is the most valuable finding in the pass, and it is a bug report.
6. **Name the reader of each new sentence** (§1). A sentence with no reader is churn or the author's seat.
7. **A new section runs on a different rubric.** With no earlier version, steps 1 to 3 have nothing to work on. Check
   instead for implementation stated as contract, history, purpose drift, the author's seat, and a sibling place
   (§4) that did not get its copy.
8. **Prove the skeleton did not move** where the pass claimed prose only; where it was a structural revision, check
   the list of renamed and removed headings against the redirects.
9. **Say which finding it is**, not whether the page got better.

| Finding | Repair |
| --- | --- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Implementation stated as contract | Rewrite as what the reader may rely on (§1) |
| Author's seat | Name the reader and their question, or cut (§1) |
| History narration | Convert to a named version marker, or move it to the changelog (§1) |
| Stale identifier, stale number, stale error text | Read the value out of the code and fix it (§6) |
| Contradicted by the code | Report it; do not reword it into vagueness |
| Common case buried | Move the default and the one-line answer to the first paragraph (§3) |
| Missing heading or row | Give the option, error, or task a place a search can land on (§3) |
| Interaction stated once | State it in both entries; detail in one, a sentence and a link in the other (§2) |
| Error not quoted | Quote the emitted text (§6) |
| Sibling place not updated | Add the derived copy in that place's shape (§4) |
| Purpose drift | Move the content to the section or page that owns it, and link (§4) |
| Duplicated canonical content | Cut the copy and link to the source (§4) |
| Churn | Restore the old wording |
| Reworded skeleton | Restore its exact text, or list the rename with its redirect (§5, §7a) |
| Edited released entry | Restore it unless the change was factual (§7a) |

## 8. Review checklist

Run this over a section before you commit it.

- Reader: which of D1 to D7 asks the question each paragraph answers (§1)?
- Promise: would any sentence stop being true after a refactoring no user could observe (§1)?
- History: any `now`, `no longer`, `used to`, `previously` outside a changelog, migration guide, or version marker
  (§1)?
- Entry: does each option entry carry name, type, default with unit, claim, values, scope, the error at the limit,
  interactions in both entries, and when to change it (§2)?
- First paragraph: does it open with the claim, and does the common case come before the escape hatch (§3)?
- Findability: does every option, error, and task the branch introduced have a heading or a row (§3)?
- Table: any paragraph in which the same nouns recur with different values (§3)?
- Names and numbers: does every identifier, value, unit, and quoted error match the code (§6)?
- Copies: is the new item in every place a sibling occupies, in that place's shape, and in no new place (§4)?
- Links: does the feature page link the options it depends on, and the entry the error it triggers (§4)?
- Headings: did a shipped heading change, and if so is the redirect in the same change (§5)?
- Owed: did the diff change a promise the table in §7 lists, and did each get its page?
- Nothing: is there a section here that should not exist, or that duplicates a canonical source (§7)?

## 9. Worked example

An option entry written from the author's seat, and the same entry from the reader's:

*Before:*

```markdown
* **`maxCopyDataSize`** *Default `null`*
  The limit exists because the protocol gives `CopyData` no maximum. The driver sizes the receiving
  array from the length the message declares, so without a bound one corrupt length becomes an
  out-of-memory error. When unset, the driver applies a built-in limit of 64 MB
  (`DEFAULT_MAX_COPY_DATA_SIZE`, 64,000,000 bytes), which `protocolHardeningMode=disable` skips.
```

*After:*

```markdown
* **`maxCopyDataSize`** (size, default: unset, which applies a built-in limit of 64 MB)
  The largest single `CopyData` message the driver accepts. `CopyData` carries `COPY ... TO STDOUT`
  output and replication data, so the limit bounds `PGReplicationStream` too.
  Accepts the forms `maxResultBuffer` accepts: `100`, `150M`, `10p`; suffixes are decimal, so `64M`
  is 64,000,000 bytes.
  Over the limit, the `COPY` fails with `Protocol error. CopyData message has length N, which
  exceeds the pgjdbc limit of M bytes.` and the connection closes.
  Raise it when a `COPY` or a replication slot legitimately sends larger messages. A value you set
  applies in every `protocolHardeningMode`; the built-in limit is the one `disable` skips.
  Since 42.7.14.
```

The first version opens with rationale and mechanism, names a constant the reader cannot set, and never says what the
reader sees at the limit. The second opens with the claim, quotes the error D5 will search for, states the interaction
with the mode in one sentence, and leaves the rationale out, because a reader who wants a 64 MB default explained is
rarer than one who wants to know what happens at 65.
