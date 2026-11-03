---
name: final-review
description: >-
  Use at the end of a coding task, in a fresh subagent, when the code, tests, and comments are
  written and before the commit is final: "run the final review" or "check the change before I
  commit". Reviews one change against a fixed form: every doc comment added or changed, and every
  comment left above changed code, consistent with the code and with the other comments in the
  file; every case the task statement, the commit message, and the class comments claim, covered
  by a named test; boundaries, invalid partitions, and the negative control present; names and
  comments that refer by content rather than by position or ordinal; assertions that print the
  operands. Every item gets an answer, "none" included, with evidence. Findings are sorted
  substantive, taste, or churn, and only the first kind is a request. A change with no code, such
  as a skill, AGENTS.md, a docs page, or a configuration, fills the same form through the
  analogues the skill names. Not a general code review; for that use the code-review skills.
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
review.

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

Answer every item. An item with nothing to report says `none` and one sentence on what was checked, not an answer to
each of its questions; an item with a finding gives the file and line, the sentence or the test it concerns, what the
reader would get wrong, and the change requested. The finding is stated there once; the index of §4 points to it.

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

A command the change tells someone to run is a claimed case too: a command line in a page, a comment, a help text, or a
recipe that the change adds or edits, or whose outcome depends on a configuration the change creates, with the outcome
it promises. List each such command line with its outcome. Beside each, put the script, build target, or CI job that
runs the same command with the same flags on that configuration, or `none`. A documented form that differs from every
form that runs, by a flag, a tool, or a version, is `none`. For each `none`, name the property of this configuration the
outcome depends on (the kind of object the command acts on, a flag combination, the platform) and say what the tool does
with it in each version the change says it supports. That a flag exists does not settle its outcome: compare what its
help text, reference, or source says it acts on with what this configuration has. Unless that shows this configuration
getting the promised outcome in every version the change supports, the finding is substantive, and the request is a run
of that form on that configuration and those versions, or the documented form replaced by the one that runs.

Then read the claims the other way. A hunk that changes behavior, a version, or a dependency beyond what the claimed
change needs is a finding, however small, where no sentence of the commit message or the description claims it: a
version bump carried over from another branch, a dependency moved in a file the change otherwise does not touch. The
tests of a claimed change, and the generated or lock output it produces, are claimed with it. The request is a sentence
that claims the hunk, with the run that checks it, or the hunk moved to a change of its own. A hunk outside that scope,
such as a typo fixed in a comment or a page, needs no claim, and the report does not mention it.

### Item 3: boundaries, partitions, and the negative control

For every input the test set varies: the boundary values and the value just outside them; each invalid partition
tested alone; the empty value where the type admits one. For every setting or mode that triggers the defect: the
other value of that setting, or the other mode, present as the control that stays green on the base commit. A
suite that tests only the failing corner is a finding, named as such. Where the change reads or replaces something an
earlier version left behind (a configuration file, keys, a persisted format, a cache, deployed objects), ask which
pre-existing state the change will meet. A change whose every test and run starts from a fresh install is a finding;
the request is a test or a run that starts from that state, or the documented remedy, run on that state.

The values users already pass are such state too. Where an existing setting (a pass-through variable, a flag, an
environment variable) now reaches a consumer it did not reach before, check the values users pass through it, not only
the documented example: list the names the new consumer reads that the old consumers also read, such as a values key
both charts define or a variable both programs read, and for each say what a value meant for the old consumers does to
the new one. A value that means something else there, or makes it ask for something nothing builds or provides, is a
finding. The request is a setting of the new consumer's own, or a run with that value.

Where the change replaces a mechanism (a build target, a wait, a client, a deployment step), say from the old code and
the new how long each takes to fail and what each prints, on two faults: the one the old mechanism met most often, which
its error handling or the CI history shows, and, where the new mechanism waits in a loop, the fault on which one attempt
waits longest. On that fault, count each attempt at its call's own timeout, the default where nothing sets one, and a
call with no timeout as never returning. Count a deadline checked before each attempt as overrun by up to one attempt
and one sleep. A replacement that fails later or prints less, with no sentence in the change that accepts it, is a
finding. The request is a run of that fault on the new mechanism, with its duration and its output. For a later failure,
the request adds a deadline that bounds the whole wait, last attempt included, at the old mechanism's time to fail; for
a quieter one, the old output.

Where the change sets, exposes, or moves a limit, list the other limits on the same work: in whatever starts or wraps
this code, in what this code starts, and in the environment, each with the place that sets it (a documented setting, a
value fixed in a script or a wrapper, a default, another program's code). A limit counts where the work it bounds
contains this work or lies inside it as a whole; one on a single operation inside the work, after which the work goes
on, or on work that only overlaps it, does not. An enclosing limit that starts earlier still counts, with the time spent
before this work starts taken from its budget. Then raise each documented setting just past each of the other limits,
not only at its default: where a limit fixed elsewhere fires first, so that the raised value has no effect, that is a
finding. So is an inner limit that does not fire first at the defaults. The request is to derive one limit from the
other. Where the other limit is in a program the repository does not contain, the request is the line that sets it or a
run that reaches it.

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

A change that adds a member to a set (a Makefile variable, an environment variable, a flag, a values key, a component, a
build target) has a sibling in every place that lists the other members: a page's table of overrides, a help text, a CI
matrix, a schema. Search for two existing members by name (the one, where the set had one), and read every file that
names both; a list that names the others and not the new member is a finding. Then search the prose for the set's old
size, in digits and in words (`both`, `two`, `the three`): a sentence that still counts the members as before is a
finding too.

Where the change fixes a symptom, its sites include the other paths that show the same symptom, which `git grep` on a
helper does not find: a twin target, the other major version of a tool, the other operating system. Then read every
remedy, troubleshooting row, and step the change writes: list the paths its symptom or its cause names, and check that
its action names a step for each. A row whose symptom names two targets and whose action names one is a finding. A fix
made in answer to a review comment is where this is missed: the comment names one path, and the fix covers that one.

## 2a. A change with no code

A skill, an instruction file an agent reads (`AGENTS.md`, `CLAUDE.md`, a rule file), a documentation page, a
configuration, or a research directory has no members, no tests, and nothing for the drift script to parse. The form
still applies; each item reads the analogue below, and the report says under every item which analogue was used. Say
that the drift script was not run and why, and do not skip an item because its literal wording does not fit. An analogue
that names a skill or an instruction file applies to those files only; a docs page or a configuration in the same change
gets the others. The skills to load are the developer-style skill and the authoring skill of the artifact
(`docs-page-authoring` for a page, `apm-authoring` for a skill package or an instruction file) in place of the
doc-comment skill.

- **Comments consistent with the code and with each other.** The comments are every statement one changed file makes
  about another, about the repository, or about a document it cites: a section reference, a count ("six questions",
  "five slots"), a file list, a description repeated across an index and a manifest, a claim about what a named issue or
  standard says. Check each against the file or the document it describes. A cited exemplar is fetched and read, not
  remembered: in one review the artifact's own rule was refuted by the issue it cited as the model to follow. In a skill
  or an instruction file, a worked example is a statement too: an example followed by a sentence on what not to copy
  from it contradicts its rule (`apm-authoring` rule *One canonical example per concern*).
- **Claimed cases covered.** The claimed cases are the cases the task statement names and the artifacts or situations
  the change says it covers. Against each, the section that handles it. The test that covers a rule is its detection: a
  rule the artifact states with no way for a reader to tell whether a text obeys it is a claimed case with no test. A
  README's claim about the repository is covered by the file that makes it true. A command the artifact tells a reader
  to run is a claimed case, listed and covered as in *Item 2: claimed cases covered*. A hunk that changes a rule, a
  version, or a dependency is claimed as in the same item.
- **Boundaries, partitions, and the negative control.** The partitions are the genres, modes, and situations the change
  claims; the negative control is the statement of what does not apply, and the control arm of any trial the change
  carries. A trial that exercised one of three claimed genres leaves two partitions with no evidence, and the finding
  names them. For a configuration, a script, a deployment definition, or a package installed over an earlier version,
  each question of item 3 applies as written, and its answer often lies in another file or in the program the change
  starts. For a skill or an instruction file, the negative control is the table of added instructions below.
- **Level, placement, and the environment.** Which file each rule lives in, whether the layout matches the siblings in
  the repository, and whether the registration entries are the ones the repository's own gate checks. Run that gate
  where it runs offline. A sentence in a skill or an instruction file that could appear unchanged in any tutorial on the
  topic has no level, and the finding asks for its removal (`apm-authoring` rule *Encode platform-specific knowledge,
  nothing else*).
- **Names by content, not by position.** Unchanged, and applied to the change's own headings, cross-references, and
  case names.
- **The failure report.** A rule's failure report is what it tells the reader to look at and what a failure looks
  like. Two checks: every rule with a detection is reached by the artifact's own checklist, where it has one, and
  every detection detects the rule it is attached to rather than a weaker property.
- **What the writer says it verified.** The evidence that the rules can fail: an exemplar they pass and a bad case they
  fail, both named in the change. Where a rule was rewritten, apply it again to both; a rewrite that now fails the
  change's own worked example is a finding. For an instruction added after a bad output, the bad case includes an input
  where the added item is noise, and a check that the output there did not grow, beside the check that the item now
  appears.
- **Siblings of the change.** The siblings are the places that enumerate or route to the artifact: an index, a
  marketplace entry, a sibling package's cross-reference, an umbrella that pins it. A scope widened in the artifact's
  body and not on the surface that decides whether it loads is the classic miss. A member added to a set (a package to
  the umbrella, a skill to the index, an option to a table) is listed wherever the other members are, and no sentence
  still counts the set as before.

For a skill or an instruction file, the report carries one more table, of the instructions the change adds or widens.
Count them before filling a row: an instruction is one thing the change tells the agent to do. A rule that takes several
sentences is one row, because the sentences that define its terms, state its exceptions, or say where it stops belong
to it, and a checklist line that restates it is the same instruction. Take each instruction through three steps:

1. **Choose the input.** Take an input that meets every condition the instruction states, so that it fires, and where
   its item helps no reader or drops something a reader needs. Take it from what the artifact names: its own text, its
   examples, its cases. An input brought from outside them, such as a versioning scheme, a template, or a deployment
   model the artifact never mentions, is taste whatever it costs: a taste finding of this item, with no row. An input
   that fails one of those conditions tests nothing.
2. **Label it before writing a row.** The input gets no row in three cases. Where the artifact already ends the
   instruction for that input, by its own condition or by a definition it relies on, it is not a finding: add the line
   number that ends it to the `Not findings:` line. Only a condition ends it: a clause on where the output stops, such
   as `end the sentence there`, says what the agent writes once the instruction fires, and does not keep it from firing.
   Where another rule asks for the opposite on the same input, or the instruction's text reads two ways and one of the
   readings serves the input, the conflict or the ambiguity is the finding, and it goes under item 1, not into the
   table. Where another item already files that input, that finding carries the clause. Any other input is substantive
   and gets a row, including one that every reading of the text fails.
3. **Fill the row from the text.** Write what an agent that follows the instruction produces for that input, and the
   condition that would end the instruction there (`only where …`, `absent when …`). A run on the input is
   evidence for the row, not a substitute for it. Name the instruction by its line and a few of its words, and keep
   every other cell to a phrase of at most about fifteen words, as in the example row. The request is the clause, not a
   further instruction or a further run (`apm-authoring` rule *Fix a bad output where the rule stops*), and the
   index of §4 points to the row rather than restating it.

Where no instruction gets a row, write no table: write `Added instructions: <n>, no rows.` and the `Not findings:` line.
Both lines carry numbers alone, as in the example below: no list of the instructions, and no word on why each one ends.

One such input per instruction is the negative control the item asks for. The other branches of the instruction's
condition are partitions, owed evidence only where the change claims them.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:42` "List every file the change touches" | a one-line fix | a list of one file the diff already shows | "only where the change spans more than one package" |

Not findings: `:57`, `:63`.

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

One section per item, in the order above, each headed by the item's name and answered even when the answer is `none`.
For a skill or an instruction file, the section of *Boundaries, partitions, and the negative control* carries the table
of added instructions from §2a, or the line that replaces it, and its `Not findings:` line. Then an index of the
findings, one row each, in these four columns; the request stays in the item's section:

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The `@throws` sentence names the exception the change removed | Substantive | `Parser.java:88` | 1 |

Where no item has a finding, the index is the line `Findings: none.` Where a check the form asks for could not be done
(the drift script does not parse the language, a file could not be read), end with one sentence that names it.
