---
name: change-description-authoring
description: >-
  Load before writing the commit message, the pull request title and description, or the changelog
  or release-note entry for a change, including at the end of a coding task ("fix the bug",
  "implement the feature", "prepare the PR"): load it when the code is done and before git commit.
  Also load to rewrite, review, or compare any of them, or to decide whether a change needs a
  changelog entry at all. Governs what each artifact says and for whom: the reviewer, the future
  git blame reader, the on-call engineer holding a stack trace, the upgrading user, the backporter;
  the slots of a commit body and a description; the merge model and what survives it; trailers;
  house style gated on the workflow; identifiers that are never invented. Wording is
  english-developer-style's; load both.
---

# Authoring a change description

This skill governs **what a change description says, in what order, and for whom**. Wording, tense,
mood, sentence length, punctuation, and dialect belong to `english-developer-style`; load it too,
and let it own the sentences. Subject length limits, prefix grammar, and trailer syntax belong to
commitlint or the platform, not to a prompt.

A change description is three artifacts written at once: the commit message, the pull request
description, and the changelog entry. They are read by five readers, at five different moments,
holding five different things. The rules below name the reader every time, because the same
sentence is essential to one reader and noise to another, and the only way to decide is to ask
whose question it answers.

## 1. The correction that matters most

**Write for the readers who are not in the room.** The reviewer can ask; the other four cannot. The
archaeologist holds a line of code years later, the on-call engineer holds a stack trace at 3 a.m.,
the upgrading user holds release notes, and the backporter holds a list of subjects. Each of them
has
one artifact and one search string, and a description that answers the reviewer's questions in the
pull request while leaving `git log` with a title has served the one reader who needed it least.

| Reader | Holds | Opens | Asks |
| --- | --- | --- | --- |
| **R1 Reviewing maintainer** | The diff | The pull request description | Was something wrong? Is this behavior right? How was it checked? What is left out? |
| **R2 Archaeologist** | A line of code, via `git blame` | The commit message | Why does this exist? Why this approach? Which constraint forced it? |
| **R3 On-call engineer** | A stack trace or a log line, and a version | The changelog, then the commit a bisect reaches | Is this my incident? What triggers it? Am I on an affected version? Is there a workaround? |
| **R4 Upgrading user** | The version they run and the one they want | The release notes | What changed that I can observe? Is it compatible? What must I do? |
| **R5 Backporter** | A maintenance branch | Labels, trailers, and the subject list | Is this a fix? How severe? Which versions? Does it need another change first? |

The test that follows from this, applied to every sentence: **name the reader and the question it
answers.** A sentence that answers none of the questions above belongs in another artifact, or
nowhere.

**The permanent record is the commit, not the pull request.** In a repository that merges with merge
commits or rebases, the description never reaches `git log`; in a repository that squashes with the
default setting, the body is the list of branch commit messages, not the description. Write the
commit message as if the pull request did not exist, and let the description repeat it.

## 2. The slots

### Commit subject

One slot: **the change, as what it does to behavior**, in a form that stands alone in a one-line
listing. Reader R2, then R1. Test: *R2, reading `git log --oneline`, asks what this commit did.* A
file name, a phase, a ticket number, or `Fix bug` fails it. The subject is change-first even though
the body is problem-first; the two lines serve different reading moments (§4). A type prefix and a
length limit are house style (§6).

- *Fails:* `Fix bug`, `Phase 1`, `Update JobController.go`, `JIRA-1234`.
- *Passes:* `Retry finalizer removal when the orphan pod sync fails`.

### Commit body

Four slots, in this order. Verification is not one of them (§4).

| # | Slot | Reader | Answers | Skip when |
| --- | --- | --- | --- | --- |
| 1 | **Problem** | R2, R1, R3 | What was wrong or missing, before any word about the fix? | Never |
| 2 | **Impact and trigger** | R3, R5, R1 | What does a user or operator observe, under which condition? The diagnostic, quoted as a literal | The change is not a fix, or the defect has no observable symptom, and the body says so in one clause |
| 3 | **Change and approach** | R2, R1 | What was done; the constraint that forced it; the alternative a reader would propose and why not; the measured trade-off | The problem statement makes the approach obvious |
| 4 | **References** | R5, R2, R3, tools | Issue, report, discussion, introducing commit, backport range, as trailers (§5) | Nothing to reference |

Slot 1 opens the body. Convince the reader that there is a problem worth fixing before saying what
you did about it. The cheapest shape is "Previously, when X happened, this caused Y, which resulted
in Z."

Slot 2 carries what a person outside the code observes: the exception, the log line, the wrong
result, the hang, the regression in latency, and the circumstances that provoke it. Where the defect
has no symptom (a leak on an error path with nothing logged), say so; an empty slot looks like an
omission, a stated absence does not.

Slot 3 justifies the way the change solves the problem: why the result with the change is better,
and which alternative was considered and discarded. A rejected alternative earns its sentence only
where a reader would propose it, and a mechanism or a measurement makes it checkable where a
preference does not. A performance claim carries its number and its cost.

**The one-line why is not replaced by the issue link.** Links rot, trackers move, and a good share
of
linked issues do not contain the reason either. Summarize the relevant point instead of pointing at
the archive. Minimum inline content when an issue exists: one sentence of problem, the identifier,
and the symptom string.

*Before:*

```text
Fix checkpointer assertion

See #4711.
```

*After:*

```text
Fix checkpointer restartpoint assertion failure

When recovery starts from a backup without a signal file, pg_subtrans is
not started and stays unstarted throughout recovery. A restartpoint run
by the checkpointer during recovery nevertheless tried to truncate it,
which failed the assertion:

    TRAP: failed Assert("TransactionIdIsValid(initial)")

Track whether pg_subtrans was started during recovery and have the
checkpointer check the flag before truncating. Skipping the truncation
unconditionally was rejected: it leaves stale pages in the common case
where pg_subtrans is running.

Reported-by: ...
Backpatch-through: 14
```

Slot 1 is the first paragraph, slot 2 the literal `TRAP:` line and the condition "from a backup
without a signal file", slot 3 the fix and the rejected shortcut, slot 4 the trailers. R3 greps the
`TRAP:` line; R5 reads `Backpatch-through:`; R2 gets the why without opening a tracker.

### Pull request title

One slot: **a searchable, accurate summary**, which a squash merge turns into the commit subject, a
merge commit carries as its second line, and a rebase and merge leaves on the platform. Reader R1,
then R2. Test: *R1, reading a list of thirty
open pull requests, asks which one this is.* Accuracy beats brevity here, because the title is read
in a list and searched; the commit subject's limit belongs to the subject.

The imperative form, the prefix, and the absent trailing period carry over from the commit subject;
the length limit does not. A pull request title has about 100 characters, and below that ceiling
accuracy wins: an 82-character line that names the component and the observable change beats a
60-character one that makes the reader open the diff. The 72-character rule belongs to the subject,
which `git log --oneline` shows and whatever quotes it truncates. Where a project squash-merges, the
title seeds that subject rather than becoming it: the merging maintainer edits the line and the
platform may append or strip the number (§4).

### Pull request description

Five slots, in order; the last two are conditional.

| # | Slot | Reader | Answers | Test |
| --- | --- | --- | --- | --- |
| 1 | **Why** | R1; R2 and R3 where the description becomes the commit body | The problem, the symptom, the condition that reaches it | *R1 asks: is there a problem worth fixing?* |
| 2 | **What** | R1, R2 | The behavioral change, not the changed files; why this approach; the rejected alternative a reviewer would raise | *R1 asks: is this the right behavior, and would I have done it differently?* |
| 3 | **Verification** | R1 only | What the tests establish; which tests are new; a manual check and what it showed | *R1 asks: what would fail if this were wrong?* |
| 4 | **Scope** | R1, R5 | What is deliberately left out; the follow-up by number; related or stacked pull requests, where they overlap, which depends on which | *R1 asks: is this gap intentional?* *R5 asks: does this need another change first?* |
| 5 | **Release note** | R4, R3 | The user-facing sentence, or `NONE`, where the repository's tooling reads a block for it | *R4 asks: what changed for me?* |

Slots 1 and 2 are the commit body's slots 1 to 3 written for a reader who has the diff open; where
the merge model copies the description into the commit, they *are* the commit body (§4). Slot 3
serves the reviewer and no one else: name what the tests establish and which are new, and do not
transcribe assertions. Slot 4 answers the two questions a reviewer finds hardest to settle from the
diff alone, whether this breaks something elsewhere and whether other places need the same change;
a sentence in it is falsifiable when it names a number or a path, and "a follow-up will handle that"
is not. Slot 5 is project-specific: Kubernetes reads a fenced `release-note` block from its
template, Prometheus a `release-notes` block.

*Before:*

```text
## Summary
Updated the job controller.

## Testing
Ran the unit tests, all green.
```

*After:*

```text
## Why
When the pod GC force-deletes a completed job pod and the job is deleted
before the pod's finalizer is removed, the orphan sync fails with
`"syncing orphan pod failed" err="Timeout: request did not complete within
requested timeout"` and is never retried. The pod keeps its finalizer and
cannot be removed.

## What
The orphan sync is requeued with backoff on failure instead of being
dropped. Removing the finalizer synchronously in the GC path was rejected:
the GC has no client for the job namespace.

## Verification
`TestSyncOrphanPodRetriesOnError` (new) fails without the change; the
existing finalizer tests are unchanged.

## Scope
Fixes #141346. The stale-finalizer metric proposed in #140900 is not part
of this change.
```

Reviewer-only content is not a slot. Checklists, screenshots, the template's own comments, and
round-by-round history live in comments or in a collapsed block, and never in a description that a
squash setting will copy into the commit body (§4).

The heading names are house style. `Why`, `What`, `How to verify`, and `Scope` is one set that
matches the slots; a template's `Summary` and `Testing` are another. Where the repository has a
template, use its headings and fill them with the slots' content.

#### What each paragraph must earn

**A reviewer decides, and does not re-investigate.** Carry what changes that decision: what was
wrong, why this behavior is the right one, what changed, how it was checked, and what scope or risk
is left. The reader should be able to tell whether to engage and where to look.

**Take the shortest chain that justifies the decision.** Once the problem and the chosen behavior
stand, add another link only where a reviewer would otherwise need it. Prefer the conclusion the
reviewer needs (severity, affected users, supported reachability, compatibility, remaining scope)
over the route that established it. `Inside the driver the defect is latent, and the class is
public API` is the conclusion; the property name, the header arithmetic, and the `assert` that
guards them are the route.

**Ask of every paragraph: which review decision becomes harder if this disappears?** Delete a
paragraph with no concrete decision. This is sharper than whether the reader needs the fact,
because almost any true fact can be argued to be needed. *Whether `n <= 0` is the right condition*
is a decision; *whether `Long.MIN_VALUE` needs handling of its own* is one; *that a sibling pull
request touches the same class* usually is. Six assertion messages and a parameter matrix are not.

**State each causal link once.** The Why slot carries the symptom, the condition that makes it
reachable, and the decision that was wrong. The What slot carries the new behavioral boundary. The
verification slot names the property the tests establish.

**Each artifact has a primary level of detail.** Repeat a lower-level fact only where the reviewer
needs it to understand or challenge the decision.

| Artifact | Its level |
| --- | --- |
| the diff | implementation detail |
| the tests | individual cases, fixtures, parameter matrices, failure output |
| the doc comment | the durable API contract |
| the commit message | why the change was needed, for whoever runs `git blame` years later |
| the changelog | the released, user-visible symptom |
| the pull request | the problem, the decision, the scope, and a verification summary |

**In the What slot, name the behavioral change, not the artifacts that carry it.** `Javadoc records
the rule` and `changelog entry added` are changed files the diff already shows. A doc comment earns
a line only where the contract it states is itself under review, and even then do not quote its
wording, which is the part most likely to change before merge.

**Keep a specific value where the decision depends on that value.** A threshold, a version, an
identifier, or a magnitude stays when changing it would change the behavioral conclusion, the
compatibility boundary, or what a test discriminates. Being searchable does not make a value
necessary: where the property is that a trigger is internal rather than dependent on the operating
system, the internal source is the claim and its particular threshold is test construction, so `the
driver's 64 KB receive-buffer estimate` may become `the driver's own receive-buffer estimate`
without loss. The detail and the claim resting on it leave together, or neither does.

**An approach you tried and rejected earns a collapsed block, when a reviewer would propose it.**
The What slot names the alternative a reviewer would raise in one sentence, with the mechanism that
rules it out. An approach you actually tried, with a measurement, goes in a `<details>` block with a
one-line `<summary>`, after the What slot and before verification. Each entry states a mechanism or
a measurement, in one short paragraph: *the watcher's consumer thread needs the same lock, so the
event cannot arrive while the build waits; measured, 6 timeouts in 6 runs*. An entry that reports
the alternative as considered and this one preferred is unfalsifiable and belongs nowhere; neither
do the investigation route, every idea anyone had, or the internal identifiers of the review
process. This does not contradict `javadoc-authoring` §7a, where cutting a rejected alternative is
usually the highest-value edit in a diff: a doc comment's reader is using or fixing the thing, while
a pull request's reader is deciding whether the approach is right.

#### Verification

**Name what the tests establish; do not transcribe them.** `SkipTest covers negative counts, the
read position after a refused skip, the minimum signed value, and zero as the boundary` replaces
three paragraphs of parameter sets and assertion output. A measured result earns a sentence where it
shows test discrimination, the intended boundary, or another property the test names do not: `revert
the guard and six of the seven fail, while zero still passes because it pins the boundary` does; `17
of 23 tests fail without the change` does not.

**Say which tests are new where that changes the coverage question.** Mark it once, as *two new
tests* or a `New tests:` label above them, and say nothing further about the ones that did not
change. The marking stays while the change is under review and may go on a settled diff.

**What a test establishes is a property, not the construction that reaches it.** Fixture shape,
parameter sets, and the harness belong to the tests unless one of them is itself under review: an
integration path chosen to prove that the real caller sees a checked exception is a property; the
buffer state that makes a branch reachable is construction, and its reason has usually been given in
the Why slot already. Name the test or the class either way, so a reviewer who wants the
construction has somewhere to go.

**Follow-the-link test.** Where a paragraph only demonstrates a fact that a named test, a diff hunk,
or a documented contract already carries, delete the demonstration and name the artifact instead.
Keep the demonstration where the reviewer needs it *before* judging that artifact: four lines of the
old code that make the bug obvious earn their space; six lines of output proving the new tests fail
without the fix do not.

**Do not narrate an obvious command.** Give the command and one sentence on what success, or an
intentional failure, establishes. Where the command names `RetryPolicyTest` and `RetryFailureTest`,
`the command also runs the existing retry coverage` adds nothing. A sentence beside a command earns
its place by naming a prerequisite, a skip, an intended failure, or a property the test names do not
reveal. Paste output only where the exact output is part of the behavior under review.

#### Scope

**A claim about neighboring work is a claim about the world now.** A description that calls a merge
trivial, simple, or mechanical without having looked has predicted rather than reported; two changes
that create the same path conflict over the whole file. Describe the overlap and leave the
difficulty to whoever resolves it. Where both are still open, or one is stacked on the other, name
the paths they share, because that decides merge order. Once both have landed, the overlap is
history and the sentence is not required.

For related or stacked pull requests, describe the relationship as scope: one sentence on where they
overlap and whether any of them is a dependency. Do not summarize what each one changes, and do not
describe a neighbor's implementation or tests unless that changes how this one is reviewed. Where a
follow-up exists, name its number; where it does not, state what this change leaves out (`GSS
handling is outside this change`). `A separate pull request follows for that` is unfalsifiable when
written and stale once the number exists.

### Changelog entry

Five parts in order, under a category heading. §3 argues the order.

| # | Part | Reader | Answers |
| --- | --- | --- | --- |
| 1 | **Category**: Added, Changed, Deprecated, Removed, Fixed, Security | R4 | Which kind of change is this? |
| 2 | **The observable change**, self-describing without the heading | R4 | What can I now do, or what now happens differently? |
| 3 | **The symptom and the trigger**, diagnostic quoted as a literal, setting or condition named | R3 | Can I grep this with my log line? Does the condition match my deployment? |
| 4 | **References**: pull request or commit, issue, CVE | R3, R2, R5 | Where is the detail? |
| 5 | **Compatibility and action**: breaking or not, what the reader must do, and for a regression the version that introduced it | R4, R5, R3 | Will my upgrade break? Am I on an affected version? |

Each entry must be self-describing as if no category heading existed, because dependency bots
quote entries out of context. `json-parser 8.0.2 is fixed (#295)` is the antipattern: it names a
ticket and explains nothing. The introducing version in part 5 is written only where a `Fixes:`
trailer or a bisect established it, never guessed.

*Before:*

```text
### Fixed
- Bug fixes and performance improvements.
- Fixed #19016.
```

*After:*

```text
### Fixed
- Set a request timeout for `docker_sd` and `dockerswarm_sd`. Previously an
  unresponsive daemon could freeze discovery indefinitely, silently pinning
  targets to a stale snapshot. #19237
- Fix silent data loss and a crash loop when `stale_series_compaction_threshold`
  is set in the config file. Regression since 3.12.0. #19016
```

## 3. The changelog entry is the on-call reader's artifact too

The upgrading user and the on-call engineer open the same file with different questions, and most
changelog guidance writes for the first. One entry serves both if its parts are ordered so that each
reader stops where their question is answered: the observable change first, because R4 stops there
for a feature; the symptom and trigger second, because R3 greps for it and R4 skips one clause; the
references third; compatibility last, because R4 and R5 read it and R3 reads the version.

The order is a decision, and its argument is cost: the symptom in second place costs R4 one clause,
while the symptom omitted costs R3 the whole entry, because nothing in it matches their search.

**Breaking changes are marked in place and sorted first within their category**, with a
`**Breaking:**` prefix, so that anyone scanning Changed or Removed sees them where they are. A
separate top block is a house option for release notes long enough that R4 cannot scan every
category. **A Security entry leads with its CVE identifier** where one exists, because R3 and
security tooling match on it.

**Quote the diagnostic as a literal**, everywhere it appears: exception class, error text, error
code, log line, exactly as emitted, punctuation included. Under-reporting the detail means the
reader cannot make the match later; over-reporting buries the distinguishing detail. The entry names
the public identifier the reader will grep, spelled as the code spells it, and both versions where
the project versions its releases: the one that introduced the defect and the one that fixes it.

## 4. The merge model decides where the text ends up

The merge model changes three things: which line becomes the subject of the permanent commit, what
becomes its body, and which of the branch commits survive as commits of their own. Detect it before
applying anything in §5 or §6.

Count the last forty subjects by shape:

```bash
git log -n 40 --format='%s' | awk '/^Merge pull request #/ {m++; next} / \(#[0-9]+\)$/ {s++; next} {p++} END {printf "merge %d squash %d plain %d\n", m, s, p}'
```

| Count | Model |
| --- | --- |
| `squash` dominates | Squash merge; a body of `* subject` bullets under one of them means the default setting, a body shaped like a description means "title and description" |
| `merge` present | Merge commits |
| `plain` dominates | Rebase and merge, or a repository pushed to directly; the shape is the same and the consequences are too |
| `squash` and `plain` both present | Squash and rebase both allowed, chosen per pull request (below) |

| Model | Subject of the permanent commit | Body of the permanent commit | Branch commits that survive |
| --- | --- | --- | --- |
| Squash, "title and description" | The pull request title, number appended | The description | None |
| Squash, default or "commit details" | For a single-commit pull request, that commit's subject; otherwise the title, number appended | That commit's body; otherwise the branch commit messages as a bulleted list | None, and every message lands as a bullet, `Fix lint` included |
| Merge commit | Each branch commit keeps its own; the merge commit carries the title | Each branch commit keeps its own; the description is never copied | Every one, behind a merge commit that a `--first-parent` reader sees instead |
| Rebase and merge | Each branch commit keeps its own; nothing is appended | Each branch commit keeps its own; the description is never copied | Every one, verbatim, as a separate commit that `git bisect` can stop on |

GitHub's default squash setting is the second row, and GitHub lets a repository allow several
methods at once, with the merging maintainer choosing one per pull request. GitLab's default squash
template is the title alone, and a project can compose the description, the first commit, all
commits, and the closing issues. The merging maintainer can edit the message before merging on both.

1. Every commit that will survive is a full commit message (§2). Under rebase and merge that is
   every commit on the branch; under the default squash it is the first, since the later ones
   become bullets; under "title and description" it is none, and the description takes the role.
2. Under rebase and merge, tidy the branch before review. A `Fix lint` or `Apply suggestion` commit
   lands on the default branch as a commit of its own, so squash it into the commit it corrects
   before the merge. Under the default squash the same commit lands as a bullet in the body.
3. Under rebase and merge, the platform appends nothing. Put the issue number in the commit body, as
   `Fixes #n` or in prose, or `git log` will never link the commit to its discussion. The issue
   number is known before the pull request exists; the pull request number reaches a commit only
   by amending after the pull request is opened, so the issue is the reference to rely on.
4. Write the title as the commit subject it may become: under a squash of a multi-commit pull
   request it is the subject, and under every other model it is the line the reviewer picks from a
   list.
5. Under "title and description", the description is the body: shape it as §2's commit body, keep
   reviewer-only content out of it, and compress verification to one line naming what the tests
   establish, with transcripts and checklists moved to comments. Under every other model the
   description stays on the platform, and a template's checklist may stay in it.
6. `Fixes #n` and `Closes #n` close the issue only when the change merges into the default branch;
   on any other target the keywords are ignored, so a backport carries the reference for humans.
7. A release tool reads either the commits on the default branch (release-please, semantic-release:
   the squash subject, or under rebase and merge every commit) or the pull request titles and labels
   (release-drafter, GitHub's generated release notes). Find out which tool the repository runs, and
   put the prefix or the label where that tool reads it.

**Where squash and rebase are both allowed**, the maintainer usually rebases a tidy branch and
squashes a messy one, and the author cannot tell in advance. Write for both: every commit
self-standing with its number (rule 1 to 3) and the title as a subject (rule 4). Under the default
squash setting the description is copied in neither case, so rule 5 does not apply.

What rule 1 prevents, from a squash under "title and commit details" of a pull request whose
description ran to five paragraphs of mechanism and measurements:

```text
fix(cache): re-add cacache.verify() to garbage collect orphaned content (#44987)

* fix(cache): re-add cacache.verify() to garbage collect orphaned content

* Fix lint

* Apply suggestion from @reviewer

* Apply suggestion from @reviewer
```

That is all `git blame` will ever show. Under rebase and merge the same pull request lands as four
commits, three of them `Fix lint` and `Apply suggestion from @reviewer`, and under merge commits
the four sit behind a merge commit; in each case the description is never copied, so the commit
messages carry problem, impact, and approach whether or not the description repeats them, because
the description is reachable only while the platform is.

**Default when detection fails**: write every branch commit as a full commit message, with the
issue number in its body, and write the description so it can stand as a commit body. This is what
the strictest rows above demand at once; it costs one paragraph of duplication when the repository
turns out to merge or rebase, and loses nothing in every other case.

**Verification does not belong in `git log`.** Email workflows strip it below `---`; pull request
templates ask for it in the description; a squash setting can copy it into the body. R1's need is
met in the pull request; R2's noise is kept out of the history. Where the description will become
the body, rule 5 applies.

## 5. Trailers and the identifiers a reader greps

Trailers are a block of `Key: value` lines at the end of the message, after a blank line, with no
blank lines inside; keys are ASCII alphanumerics and hyphens. Each one has a consumer, and the
consumer decides whether it is worth writing.

| Trailer | Consumer | Reader | Write it when |
| --- | --- | --- | --- |
| `Fixes: <12+ hex sha> ("<subject>")` | Kernel stable scripts, to pick the branches that need the fix | R5, R3 | The project uses it; elsewhere it is prose only R5 reads, and still worth a line for a regression |
| `Fixes #n`, `Closes #n`, `Resolves #n` | GitHub and GitLab: link, and close on merge to the default branch | R2, R5 | An issue exists |
| `Closes: <url>` (kernel) | Humans and regression trackers; a public URL is required | R2, R3 | The project uses it |
| `Link:` | Humans | R2 | A discussion or archive exists |
| `Backpatch-through: <major>` | PostgreSQL's release-note tooling, which groups identical messages across branches | R5 | The project back-patches and uses it |
| `Cc: stable@vger.kernel.org # <ver>: <sha>: <subject>` | Kernel stable team; the sequence means `git cherry-pick <sha>` then this commit | R5 | Kernel only |
| `Reported-by:` | Credit | R2 | Someone reported it |
| `BREAKING CHANGE:`, or `!` after the type | release-please and semantic-release: major bump | R4, through the tool | The tool is present |
| `Co-authored-by:` | Platform attribution | none of the five | Provenance requires it |
| `Change-Id:`, `Signed-off-by:` | Gerrit; the DCO | none of the five | The workflow requires it |

**Identifiers.** Beyond the diagnostic and the versions of §3, these decide what a search finds.

- The public identifier the change touches: option, flag, class, method, configuration key, spelled
  as the code spells it. Future readers search the history by these strings. A private helper is
  named only where its name is what the reader will grep for.
- The issue identifier, beside the one-line why, never instead of it (§2).
- Identical messages across branches when back-patching, where tooling groups them; where the
  branches diverge in behavior, one branch-specific line beats a misdescription.

## 6. House style, gated on the workflow

These prescriptions serve a tool or a process, not one of the five readers. Apply each only where
the detected workflow consumes it; a repository's `CONTRIBUTING.md`, commitlint configuration, or
existing history shows which.

| Prescription | Serves | Apply when |
| --- | --- | --- |
| `type(scope):` prefix | release-please, semantic-release, commitlint | The history already carries prefixes or a config names the tool. Where it does, the prefix is mandatory and the imperative is the first word after it. The prefix gives authors the impression that the message is descriptive; the body still owes the why |
| 50- or 72-character subject | Terminal and email display | The project states a limit; it is a linter's check |
| `Signed-off-by:` | The DCO | The project enforces it |
| `Change-Id:` | Gerrit | The history shows it |
| `Discussion:` URL | PostgreSQL's mailing-list archive | PostgreSQL |
| `/kind`, `/release-note-none`, fenced `release-note` block | Prow | The pull request template has them |
| One news-fragment file per change | towncrier's merge-conflict avoidance | A `newsfragments/` or `changes/` directory exists |
| An `Unreleased` section | Entries written in the pull request | Keep it where entries are written in the pull request; drop it where they are curated at release. Default: keep |
| Content below `---` in the message | `git am` | Email patches only; in a pull request the separator is inert text and everything below it lands in the body |

The principle behind each transfers when the mechanism does not: mark fix versus feature where R5
reads it (a label, a category, or a prefix); name backport prerequisites where R5 looks (the scope
slot, a label); keep the user-facing sentence separate from the reviewer-facing description.

## 7. When to write nothing

- No changelog entry for maintenance noise: dotfiles, development-only dependencies, formatting,
  CI. Where the tooling demands a line, `NONE` is the line.
- No section for an absent concern. A description with no breaking change, no follow-up, and no
  rejected alternative has no such sections; an empty heading is not a gap to fill.
- No verification narrative in the commit body (§4).
- No paraphrase of the diff. A body whose sentences map one to one onto hunks adds no rationale;
  R2 has the diff.

## 7a. Editing an existing description

The "which review decision becomes harder" test, the rule that each causal link is stated once, and
the literal treatment of a quoted diagnostic are `english-developer-style` §7's and apply here
unchanged. The growth budget is the authoring skills' shared rule: **restructuring is free, and growth
is paid for by a fact the old version did not carry** (a symptom, a condition, a version, a measured
value, a named test, a dependency between changes); name the fact, or keep the old wording. A
description under roughly 300 words is presumed not to grow. Two rules are this skill's own:

- **A released changelog entry is not yours to reword.** It has been read, quoted, and linked. Fix a
  wrong version or a wrong CVE and leave the wording.
- **A rewrite that moves a fact between artifacts says where it went.** A symptom cut from the
  description because the changelog entry now carries it is a move; the same cut with no entry is a
  loss.

## 7b. Comparing two versions

Read the old version first and reach the verdict last; the new version was written second and reads
better for it, and a fact that vanished leaves no trace in the text that replaced it.

1. List the old version's facts before you read the new one: a symptom, a condition, an identifier,
   a version, a measured value, a named test, a dependency between changes, a stated non-goal. A
   topic sentence is not a fact.
2. Mark each fact present, restated, or absent, and defend every absence in words. *The diff implies
   it* and *the new wording covers it* are not defenses.
3. Only now count the delta, under §7a's budget.
4. Check what the new version asserts against the diff and the tests, not against the old text; the
   old text is provenance, not evidence.
5. Name the finding: lost fact, unpaid growth, unsupported claim, diff paraphrased, symptom dropped,
   diagnostic retyped, verification in the permanent body, reviewer content in a body the squash will
   copy, issue link standing in for the why, edited released entry, invented identifier.

## 8. Review checklist

- Reader: for every sentence, which of R1 to R5 asks the question it answers (§1)?
- Subject: does it name the change, and would it identify the commit in `git log --oneline` (§2)?
- Problem: does the body open with what was wrong, before the fix (§2)?
- Symptom: is the diagnostic quoted as a literal, with the trigger condition, or is its absence
  stated (§2, §3)?
- Why: is there a sentence of reason beside the issue link, not only the link (§2)?
- Approach: is the alternative a reviewer would propose answered with a mechanism or a number (§2)?
- Verification: does the description say what the tests establish and which are new, and is none of
  it in the commit body (§2, §4)? Does any sentence narrate an obvious command or transcribe
  assertions?
- Decision: for every paragraph, which review decision becomes harder without it (§2)?
- Alternatives: is an approach a reviewer would propose answered in one sentence, and a tried one in
  a collapsed block with a mechanism or a measurement (§2)?
- Title: does it name the component and the observable change, within about 100 characters (§2)?
- Scope: is every gap named as intentional, every follow-up by number, every stacked change by its
  overlap and order (§2)?
- Changelog: category, observable change, symptom, reference, compatibility, in that order; breaking
  marked in place and first; CVE leading a Security entry (§2, §3)?
- Merge model: read from the history; every commit that survives the merge
  written as a full body with its issue number; no `Fix lint` commit left to land on its own under
  rebase and merge (§4)?
- Trailers: each one has a consumer in this repository, and the closing keyword targets the default
  branch (§5)?
- Identifiers: does every issue, pull request, commit, and version number exist, or stand as a visible
  placeholder (`english-developer-style` §7)?
- House style: prefix, limit, sign-off applied only where the workflow consumes them (§6)?
- Nothing: no entry for noise, no empty section, no diff paraphrase, no predicted merge difficulty
  (§7)?
- Rewrite: net delta defended, causal links stated once, released entries untouched (§7a)?
