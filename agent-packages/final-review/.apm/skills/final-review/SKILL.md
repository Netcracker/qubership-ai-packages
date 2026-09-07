---
name: final-review
description: >-
  Use at the end of a coding task, in a fresh subagent, when the code, tests, and comments are
  written and before the commit is final: "run the final review", "final-review this change",
  "check the change before I commit". Reviews one change against a fixed form: every doc comment
  added or changed, and every comment left above changed code, consistent with the code and with
  the other comments in the file; every case the task statement, the commit message, and the class
  comments claim, covered by a named test; boundaries, invalid partitions, and the negative control
  present; names and comments that refer by content rather than by position or ordinal; assertions
  that print the operands. Every item gets an answer, "none" included, with evidence. Findings are
  sorted substantive, taste, or churn, and only the first kind is a request. A change with no code,
  such as a skill or a docs page, fills the same form through the analogues the skill names. Not a
  general code review; for that use the code-review skills.
---

# Final review of a change

This skill is a form, not a reading. The agent that wrote a change re-reads its own text and finds nothing, because
a fact it left out leaves no trace in what it wrote; a second agent with a fresh context and a fixed list of
questions finds what the first could not. The list is short on purpose, and every item is answered in writing,
"none" included, so that an item cannot be skipped by not noticing it.

The rules the items check belong to other skills: `test-authoring` for what a test establishes and how its failure
reads, the doc-comment skill of the language (`javadoc-authoring` and its siblings) for what a comment says, the
developer-style skill for wording. Load the two that apply to the change's language before filling the form, and
cite their sections in the findings; do not restate them here. Wording enters this form only where it makes a
sentence read wrongly, which is a finding under the first item; a pass over the prose for style alone is not this
review, and the closing sentence of the report says it was not done.

## 1. Inputs

- The diff: the branch against its base, or the uncommitted change. Read it whole before the form.
- The task statement: the issue, the problem description, or the prompt the change answered. It is where the claimed
  cases come from. Ask for it if it was not handed over; a subagent that cannot ask answers item 2 from the commit
  message alone and says so in the report.
- The commit message and the class comments of the tests, which claim cases too.
- The previous report of this form over the same change, where one exists. A change reviewed more than once,
  as in a review loop, is re-read against that report first (§4).
- The output of `scripts/comment-drift.py <base> [<head>]`, run from anywhere in the repository. It lists, per changed
  file, every member whose code or doc comment moved, named with its parameter types so that overloads stay apart and
  followed by its line, tagged `code-changed, comment-unchanged`, `comment-added`, `comment-changed`, or
  `code-changed, no-comment`. The first tag is the list of comments to re-read that nobody edited; the parse is
  approximate, so a member it misses is still yours to find.

## 2. The form

Answer every item. An item with nothing to report says `none` and one line on what was checked; an item with a
finding gives the file and line, the sentence or the test it concerns, and what the reader would get wrong.

### Item 1: comments consistent with the code and with each other

For every member tagged `code-changed, comment-unchanged`: is every sentence of its comment still true of the new
body, the first sentence first? For every `comment-added` and `comment-changed`: does the first sentence stand alone
and state what the member now does, including a second form or outcome the change introduced; does a list the
comment carries (supported inputs, accepted values, thrown exceptions) include the case the change added; does any
other comment in the same file, or the comment of a sibling that delegates to this member with a fixed argument,
now say something different about the same fact? Does any comment narrate the change (`now`, `no longer`, `used to`)
outside the one place a regression test's comment may?

### Item 2: claimed cases covered

List every case the task statement, the commit message, and the test class comments claim: each input type, each
outcome, each setting or mode named, each error text quoted. Against each, the test method (or parameterized case)
that exercises it, by name. A claimed case with no test, or a test whose name promises a case its body does not
exercise, is a finding. Where the statement names a reason for the design (a warning avoided, a value preserved),
the test that would fail if the design were replaced by the alternative is the one to name.

### Item 3: boundaries, partitions, and the negative control

For every input the test set varies: the boundary values and the value just outside them; each invalid partition
tested alone; the empty value where the type admits one. For every setting or mode that triggers the defect: the
other value of that setting, or the other mode, present as the control that stays green on the base commit. A
suite that tests only the failing corner is a finding, named as such.

### Item 3a: level, placement, and the environment

Is there a test at the smallest level that can observe the changed behavior through the unit's interface? Where the
behavior is observable in one process, with no server, network, or file system, a change covered only by a test
that needs a server the CI matrix does not always provide is a finding, and the name of the in-process method to
test is the request. Where the behavior exists only across the boundary (transaction isolation, file permissions,
what a peer accepts), the in-process test is not owed; the finding is then a CI job that does not run the test
that exists. Does each new test sit beside the existing tests of the same unit, sharing their fixture, rather than
in a new class with the fixture copied? Where a test needs a setting, a version, or a service the repository's test
policy treats as optional, does it skip with a stated reason (`assumeTrue`, a version-range annotation) rather than
error? Where the prerequisite is one CI promises to provide, a skip hides a broken job: the test fails, and the job
that runs it is checked to run it.

### Item 4: names by content, not by position

Any name, comment, parameterized case id, or message that refers to a thing by its position or its ordinal (`a last
one`, `the fifth`, `case 3`, `see below`, `the test above`) where the thing has a content it could be named by
(`the bytea test`, `the trailing-backslash case`). Ordinals go stale on the next insertion and say nothing to a
reader of the report.

### Item 5: the failure report

Any boolean assertion wrapped around a comparison, where an equality assertion would print the operands; any
boolean assertion on a method's result with no message, where the report would say only `expected true but was
false`; any assertion whose message repeats the test's name or the values the assertion prints, or says only that it
failed; any parameterized case whose id is an index.

### Item 6: what the writer says it verified

Does the change carry, or the report state, the evidence that the tests can fail: the red run on the base commit, or
the mutation verdict? If neither is stated, say so. The evidence is the writer's to state, so do not run the suite
to supply it; a gate the repository runs on every change is a consistency check, not that evidence, and item 3a may
run it.

### Item 7: siblings of the change

A fix to one site usually has siblings: other callers of the helper it wrapped, other places that build the same
literal, other readers of the same setting. For each helper the change touched or now relies on, list its other call
sites, with `git grep -n '<name>('`, or with `sb callers <name>` where the `sb` code-search command (a semantic index
over the repository, installed separately) is on the path; where it is, one `sb search "<the task statement's first
sentence>"` finds sites the name does not reach. For each site: the same defect applies, or it does not, and why. A
site where it applies is a finding; the request is to fix it in the same change or to name it as follow-up in the
description, never to leave it unsaid. Where a helper has more call sites than you can read, say how many there are
and read the ones the change's own condition can reach: the callers that pass the value, the state, or the argument
shape the defect needed. Report the count and the criterion, so that the reader knows what was not read.

## 2a. A change with no code

A skill, a documentation page, a configuration, or a research directory has no members, no tests, and nothing for
the drift script to parse. The form still applies; each item reads the analogue below, and the report says under
every item which analogue was used. Say that the drift script was not run and why, and do not skip an item because
its literal wording does not fit. The skills to load are the developer-style skill and the authoring skill of the
artifact (`docs-page-authoring` for a page, `apm-authoring` for a skill package) in place of the doc-comment skill.

- **Comments consistent with the code and with each other.** The comments are every statement one changed file makes
  about another, about the repository, or about a document it cites: a section reference, a count ("six questions",
  "five slots"), a file list, a description repeated across an index and a manifest, a claim about what a named issue
  or standard says. Check each against the file or the document it describes. A cited exemplar is fetched and read,
  not remembered: in one review the artifact's own rule was refuted by the issue it cited as the model to follow.
- **Claimed cases covered.** The claimed cases are the cases the task statement names and the artifacts or situations
  the change says it covers. Against each, the section that handles it. The test that covers a rule is its detection:
  a rule the artifact states with no way for a reader to tell whether a text obeys it is a claimed case with no test.
  A README's claim about the repository is covered by the file that makes it true.
- **Boundaries, partitions, and the negative control.** The partitions are the genres, modes, and situations the
  change claims; the negative control is the statement of what does not apply, and the control arm of any trial the
  change carries. A trial that exercised one of three claimed genres leaves two partitions with no evidence, and the
  finding names them.
- **Level, placement, and the environment.** Which file each rule lives in, whether the layout matches the siblings in
  the repository, and whether the registration entries are the ones the repository's own gate checks. Run that gate
  where it runs offline.
- **Names by content, not by position.** Unchanged, and applied to the change's own headings, cross-references, and
  case names.
- **The failure report.** A rule's failure report is what it tells the reader to look at and what a failure looks
  like. Two checks: every rule with a detection is reached by the artifact's own checklist, where it has one, and
  every detection detects the rule it is attached to rather than a weaker property.
- **What the writer says it verified.** The evidence that the rules can fail: an exemplar they pass and a bad case
  they fail, both named in the change. Where a rule was rewritten, apply it again to both; a rewrite that now fails
  the change's own worked example is a finding.
- **Siblings of the change.** The siblings are the places that enumerate or route to the artifact: an index, a
  marketplace entry, a sibling package's cross-reference, an umbrella that pins it. A scope widened in the artifact's
  body and not on the surface that decides whether it loads is the classic miss.

## 3. Sorting the findings

Every finding carries one of three labels, and the label is the reader's cue for what to do with it.

- **Substantive**: a reader could read the sentence wrongly, the sentence states something false, a claimed case has
  no test, a boundary or the control is missing. These are requests.
- **Taste**: two readings and both are right; the finding names the one the reviewer prefers. Say so, and expect it
  to be declined without discussion.
- **Churn**: the suggested version has the property it objects to, or changes wording with no fact behind it. Do not
  report it; if it slipped in, delete it before the report goes out.

A finding whose label you cannot decide is taste.

## 4. The report

Where a previous report exists, open with a table over its substantive findings: holds, partly, reshaped, or
declined, with the line that shows it or the writer's reason for declining. A fix that moves the defect to a new
sentence, or replaces one contradiction with another, is reshaped, not resolved, and is refiled as a substantive
finding of this round; one loop refiled the same rule three times before it was stated from the exemplar rather
than from the previous fix.

One section per item, in the order above, each headed by the item's name and answered even when the answer is
`none`. Then a table: finding, label, file and line, the change requested. Then one sentence on what the review did
not check (the suite was not run, a language the drift script does not parse), so that the reader does not assume
it.
