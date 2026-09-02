---
name: change-description-authoring
description: >-
  Structure and content rules for change descriptions: the commit subject and body, the pull
  request or merge request title and description, and the changelog or release-note entry. Use
  whenever the task involves one of them: writing a commit message, drafting or rewriting a pull
  request description, adding a changelog entry, reviewing any of these, comparing two versions, or
  deciding whether a change needs an entry at all. Covers the five readers a description serves and
  which artifact each one opens, the slots of a commit body and a pull request description and the
  question each slot answers, the changelog entry as the artifact an on-call engineer greps, the
  trailers and identifiers that make text searchable, what a squash merge copies into the permanent
  history and how to detect the merge model, which rules are house style gated on a workflow, and how
  far a rewrite may grow. Wording is governed by english-developer-style, which this skill defers to
  and does not replace.
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

Rules are marked *measured* where a study backs them, *asserted* where a project guide states them,
and *derived* where they follow from how a platform behaves. §9 lists what each rests on. Section
numbers follow `javadoc-authoring` and `docs-page-authoring` where the sections correspond; §4 and
§6 do not, because a change description has readers a comment does not and is copied by machinery a
page is not.

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

*Measured* for R1 and R2: reviewing others' changes is the most frequent reason engineers read a
change (67.2% of 180 respondents), and the rationale is the information they need most and "one of
the easiest to acquire if an informative change description ... is available"; about 44% of commit
messages in five active projects lacked the what or the why. *Asserted* for R3, R4, and R5: no study
observes an on-call engineer or a backporter reading, so what they open is inferred from what they
hold.

The test that follows from this, applied to every sentence: **name the reader and the question it
answers.** A sentence that answers none of the questions above belongs in another artifact, or
nowhere.

**The permanent record is the commit, not the pull request.** In a repository that merges with merge
commits, the description never reaches `git log`; in a repository that squashes with the default
setting, the body is the list of branch commit messages, not the description. Write the commit
message as if the pull request did not exist, and let the description repeat it. *Derived* from
platform mechanics; observed on Kubernetes, Prometheus, and Renovate changes where a full
description sat above a one-line commit.

## 2. The slots

### Commit subject

One slot: **the change, as what it does to behavior**, in a form that stands alone in a one-line
listing. Reader R2, then R1. Test: *R2, reading `git log --oneline`, asks what this commit did.* A
file name, a phase, a ticket number, or `Fix bug` fails it. *Asserted*: Google eng-practices, Git
`SubmittingPatches`, Zulip. The subject is change-first even though the body is problem-first; the
two lines serve different reading moments (§4, conflict 3). A type prefix and a length limit are
house style (§6).

### Commit body

Four slots, in this order. Verification is not one of them (§4).

| # | Slot | Reader | Answers | Skip when |
| --- | --- | --- | --- | --- |
| 1 | **Problem** | R2, R1, R3 | What was wrong or missing, before any word about the fix? | Never |
| 2 | **Impact and trigger** | R3, R5, R1 | What does a user or operator observe, under which condition? The diagnostic, quoted as a literal | The change is not a fix, or the defect has no observable symptom, and the body says so in one clause |
| 3 | **Change and approach** | R2, R1 | What was done; the constraint that forced it; the alternative a reader would propose and why not; the measured trade-off | The problem statement makes the approach obvious |
| 4 | **References** | R5, R2, R3, tools | Issue, report, discussion, introducing commit, backport range, as trailers (§5) | Nothing to reference |

Slot 1 is *measured*: the kernel's "Convince the reviewer that there is a problem worth fixing" and
Git's "explains the problem the change tries to solve, i.e. what is wrong with the current code
without the change" are the asserted forms, and the need behind them is the measured one. Zulip's
pattern is the cheapest way to fill it: "Previously, when X happened, this caused Y to happen, which
resulted in ...".

Slot 2 is *asserted*, from the kernel's "Describe user-visible impact ... provoking circumstances,
excerpts from dmesg, crash descriptions, performance regressions, latency spikes, lockups" and from
the CVE description template, which names the component, the version, the impact, and the vector.
Where the defect has no symptom (a leak on an error path with nothing logged), say so; an empty slot
looks like an omission, a stated absence does not.

Slot 3 is *asserted*: Git's "justifies the way the change solves the problem" and "alternate
solutions considered but discarded, if any"; Google's "why this is the best approach. If there are
any shortcomings to the approach, they should be mentioned"; the kernel's "include numbers that back
them up. But also describe non-obvious costs". A rejected alternative earns its sentence only where
a
reader would propose it; a mechanism or a measurement makes it checkable, a preference does not.

**The one-line why is not replaced by the issue link.** *Measured*: of 611 commit messages that
linked an issue instead of stating a reason, 15% linked to something that did not contain the reason
either, against 89.77% of surveyed developers who expected it to. Git says the same without the
number: "Instead of giving a URL to a mailing list archive, summarize the relevant points of the
discussion." Minimum inline content when an issue exists: one sentence of problem, the identifier,
and the symptom string.

### Pull request title

One slot: **a searchable, accurate summary**, which a squash merge turns into the commit subject and
a merge commit carries as its second line. Reader R1, then R2. Test: *R1, reading a list of thirty
open pull requests, asks which one this is.* Accuracy beats brevity here, because the title is read
in a list and searched; the commit subject's limit belongs to the subject. *Derived* from GitHub and
GitLab squash mechanics; Google's first-line rule applies because the title becomes that line.

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
serves the reviewer and no one else: *measured*, "does this change break any code elsewhere?" is the
second hardest information need to acquire, and naming what the tests establish is how the
description answers it without the reviewer rerunning them. Say which tests are new; do not
transcribe assertions. Slot 4 is *asserted* (Google's shortcomings; the Kubernetes cherry-pick guide
for dependency order) and answers the hardest measured need of all, "are there other places that
need similar changes". A sentence in slot 4 is falsifiable when it names a number or a path; "a
follow-up will handle that" is not. Slot 5 is *documented mechanics*, project-specific: Kubernetes
reads a fenced `release-note` block from its template, Prometheus a `release-notes` block.

Reviewer-only content is not a slot. Checklists, screenshots, the template's own comments, and
round-by-round history live in comments or in a collapsed block, and never in a description that a
squash setting will copy into the commit body (§4).

### Changelog entry

Five parts in order, under a category heading. §3 argues the order.

| # | Part | Reader | Answers |
| --- | --- | --- | --- |
| 1 | **Category**: Added, Changed, Deprecated, Removed, Fixed, Security | R4 | Which kind of change is this? |
| 2 | **The observable change**, self-describing without the heading | R4 | What can I now do, or what now happens differently? |
| 3 | **The symptom and the trigger**, diagnostic quoted as a literal, setting or condition named | R3 | Can I grep this with my log line? Does the condition match my deployment? |
| 4 | **References**: pull request or commit, issue, CVE | R3, R2, R5 | Where is the detail? |
| 5 | **Compatibility and action**: breaking or not, what the reader must do, and for a regression the version that introduced it | R4, R5, R3 | Will my upgrade break? Am I on an affected version? |

Parts 1, 2, and 4 are *asserted* by Keep a Changelog and Common Changelog ("Each change must be
self-describing, as if no category heading exists"; "changes must reference relevant commits, and
should reference tickets or pull requests when available"). Part 2 has *measured* backing: users of
release notes want impact and detail, and a surveyed tester called "Bug fixes and performance
improvements" "completely meaningless. What was fixed? How will performance improve?" Part 3 is
*asserted* from the CVE template, the kernel's impact rule, and Common Changelog's antipattern
`json-parser 8.0.2 is fixed (#295)`, which "doesn't explain or reference what was fixed". The
introducing version in part 5 is *derived*: no project was found writing it into the entry, so it
is written only where a `Fixes:` trailer or a bisect established it, never guessed.

## 3. The changelog entry is the on-call reader's artifact too

The upgrading user and the on-call engineer open the same file with different questions, and most
changelog guidance writes for the first. One entry serves both if its parts are ordered so that each
reader stops where their question is answered: the observable change first, because R4 stops there
for a feature; the symptom and trigger second, because R3 greps for it and R4 skips one clause; the
references third; compatibility last, because R4 and R5 read it and R3 reads the version.

The order is a decision, not a finding, and its argument is cost: the symptom in second place costs
R4 one clause, while the symptom omitted costs R3 the whole entry, because nothing in it matches
their search. A hand-written changelog was found using this order with no rule requiring it: "Set a
request timeout for `docker_sd` and `dockerswarm_sd` on `unix`, `npipe`, and `tcp` hosts.
Previously an unresponsive daemon could freeze discovery indefinitely, silently pinning targets to a
stale snapshot. #19237".

**Breaking changes are marked in place and sorted first within their category**, with a
`**Breaking:**` prefix (Common Changelog; Keep a Changelog 2.0.0 argues against a separate
section so that "anyone scanning Changed or Removed sees them in place"). A separate top block is a
house option for release notes long enough that R4 cannot scan every category, which is what
Kubernetes' "Urgent Upgrade Notes" is for. **A Security entry leads with its CVE identifier** where
one exists (Keep a Changelog 2.0.0), because R3 and security tooling match on it.

**Quote the diagnostic as a literal**, everywhere it appears: exception class, error text, error
code, log line, exactly as emitted, punctuation included. Under-reporting the detail means the
reader "may not be able to make the appropriate match later on"; over-reporting "can obscure the
distinguishing details" (CVE phrasing). The entry names the public identifier the reader will grep,
spelled as the code spells it, and both versions where the project versions its releases: the one
that introduced the defect and the one that fixes it.

## 4. The merge model decides where the text ends up

Detect it before applying anything in §5 or §6. Read the last twenty or so subjects and bodies from
`git log --format='%s%n%b'`:

| Signal in history | Model | Consequence |
| --- | --- | --- |
| Subjects end in `(#123)`, no `Merge pull request` lines | Squash merge | The title becomes the subject; the body is whatever the setting copies (below) |
| `Merge pull request #123 from` lines | Merge commits | The description never reaches `git log`; only the branch commits do |
| `Change-Id:` or `Reviewed-on:` trailers | Gerrit | One commit per change; the commit message is the review description |
| `Signed-off-by:` chains with `Link: https://patch.msgid.link` or `lore.kernel.org` | Email patches | Text below `---` is stripped on apply; trailers are the routing layer |

For a squash repository, the setting decides what the body is. *Cited*: GitHub's default "uses the
commit title and message if the pull request contains only 1 commit, or the pull request title and
list of commits if the pull request contains 2 or more commits"; a repository can choose "just the
pull request title, the pull request title and commit details, or the pull request title and
description". GitLab's default squash template is `%{title}`, and a project can compose
`%{description}`, `%{first_commit}`, `%{all_commits}`, and `%{issues}`. The merging maintainer can
edit the message before merging on both.

Rules, each marked:

1. *Cited.* Write the title as the commit subject it will become.
2. *Cited.* Under "title and description", the description is the body: shape it as §2's commit
   body, and keep reviewer-only content out of it.
3. *Derived.* Under the default or "commit details", the body is the list of branch commit messages,
   so the durable why must be in the first branch commit, or the maintainer must edit at merge. A
   rich description above branch commits reading `Fix lint` and `Apply suggestion` leaves `git log`
   with those lines and nothing else. Write the first branch commit as a full commit body regardless
   of how good the description is.
4. *Derived.* Compress verification to one line naming what the tests establish where the
   description will become the body; move transcripts and checklists to comments.
5. *Cited.* `Fixes #n` and `Closes #n` close the issue only when the change merges into the default
   branch; on any other target the keywords are ignored, so a backport carries the reference for
   humans.
6. *Derived.* Where a release tool parses the squash subject (release-please, semantic-release), the
   title's prefix is what it reads; the branch commits are invisible to it.

In a merge-commit repository, rule 3 applies with more force: the commit message carries problem,
impact, and approach whether or not the description repeats them, because the description is
reachable only while the platform is.

**Default when detection fails**: treat the repository as squashing with "title and description".
Write the description so it can stand as a commit body and write the first branch commit the same
way. This costs one paragraph of duplication when the repository turns out to merge, and loses
nothing in every other case.

**Verification does not belong in `git log`.** The kernel strips it below `---`; Google and most
templates ask for it in the description; a squash setting can copy it into the body. R1's need is
met in the pull request; R2's noise is kept out of the history. Where the description will become
the body, rule 4 applies.

## 5. Trailers and the identifiers a reader greps

Trailers are a block of `Key: value` lines at the end of the message, after a blank line, with no
blank lines inside; keys are ASCII alphanumerics and hyphens (`git interpret-trailers`). Each one
has a consumer, and the consumer decides whether it is worth writing.

| Trailer | Consumer | Reader | Write it when |
| --- | --- | --- | --- |
| `Fixes: <12+ hex sha> ("<subject>")` | Kernel stable scripts, to pick the branches that need the fix | R5, R3 | The project uses it; elsewhere it is prose only R5 reads, and still worth a line for a regression |
| `Fixes #n`, `Closes #n`, `Resolves #n` | GitHub and GitLab: link, and close on merge to the default branch | R2, R5 | An issue exists |
| `Closes: <url>` (kernel) | Humans and regzbot; "Private bug trackers and invalid URLs are forbidden" | R2, R3 | The project uses it |
| `Link:` | Humans | R2 | A discussion or archive exists |
| `Backpatch-through: <major>` | PostgreSQL's `git_changelog`, which groups identical messages across branches | R5 | The project back-patches and uses it |
| `Cc: stable@vger.kernel.org # <ver>: <sha>: <subject>` | Kernel stable team; the sequence means `git cherry-pick <sha>` then this commit | R5 | Kernel only |
| `Reported-by:` | Credit | R2 | Someone reported it |
| `BREAKING CHANGE:`, or `!` after the type | release-please and semantic-release: major bump | R4, through the tool | The tool is present |
| `Co-authored-by:` | Platform attribution | none of the five | Provenance requires it |
| `Change-Id:`, `Signed-off-by:` | Gerrit; the DCO | none of the five | The workflow requires it |

**Identifiers.** These decide what a search finds.

- The diagnostic, quoted as a literal (§3), in the commit body and the changelog entry both.
- The public identifier the change touches: option, flag, class, method, configuration key, spelled
  as the code spells it. *Asserted*: "Future developers will search for your CL based on its
  description." A private helper is named only where its name is what the reader will grep for.
- Both versions, introduced and fixed, where the project versions its releases (§3).
- The issue identifier, beside the one-line why, never instead of it (§2).
- Identical messages across branches when back-patching, where tooling groups them; where the
  branches diverge in behavior, one branch-specific line beats a misdescription.

## 6. House style, gated on the workflow

These prescriptions serve a tool or a process, not one of the five readers. Apply each only where
the detected workflow consumes it; a repository's `CONTRIBUTING.md`, commitlint configuration, or
existing history shows which.

| Prescription | Serves | Apply when |
| --- | --- | --- |
| `type(scope):` prefix | release-please, semantic-release, commitlint | The history already carries prefixes or a config names the tool. It "gives commit authors the false impression that their messages are descriptive" (Common Changelog); the body still owes the why |
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
- No verification narrative in the commit body (§4), and no narration of an obvious command in the
  description: the sentence beside a command earns its place by naming a prerequisite, a skip, an
  intended failure, or a property the test names do not reveal.
- No paraphrase of the diff. A body whose sentences map one to one onto hunks adds no rationale;
  R2 has the diff.
- No sentence about neighboring work that predicts rather than reports. Name the paths two changes
  share and leave the difficulty to whoever resolves it.

## 7a. Editing an existing description

A rewrite of a description drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** A description under roughly 300 words is presumed not to grow;
  each added clause must support a review decision or restore a truth condition. Reordering,
  transitions, and a mechanism another slot already gave do not qualify.
- **Ask of every paragraph which review decision becomes harder if it disappears.** Delete a
  paragraph with no concrete decision. This is sharper than "does the reader need the fact", because
  almost any true fact can be argued to be needed.
- **State each causal link once.** Why carries the symptom, the condition, and the wrong decision;
  What carries the new boundary; Verification names the property the tests establish.
- **Keep a specific value where the decision depends on it.** A threshold, a version, an
  identifier, or a magnitude stays when changing it would change the behavioral conclusion, the
  compatibility boundary, or what a test discriminates; being searchable alone does not keep it.
- **A quoted diagnostic is a literal.** Reproduce its capitalization, spacing, and final
  punctuation; moving a period outside the quotation marks makes it a string nobody will find.
- **A released changelog entry is not yours to reword.** It has been read, quoted, and linked. Fix a
  wrong version or a wrong CVE and leave the wording.

## 7b. Comparing two versions

The new version will read better; it was written second. So read the old one first and reach the
verdict last, on the protocol `docs-page-authoring` §7b and `pr-description-sweep` share:

1. List the old version's facts: one fact is one symptom, one condition, one identifier, one
   version, one measured value, one named test, one dependency between changes, one stated
   non-goal.
2. Mark each present, restated, or absent. Absent needs a defense: wrong, moved to a named place, or
   belonging to another artifact. "The diff implies it" is not one.
3. Only now count the delta, against §7a's budget.
4. Check what the new version asserts without support, against the diff and the tests, not against
   the old text.
5. Name the changes that bought nothing.
6. Say which finding it is: lost fact, unpaid growth, unsupported claim, diff paraphrased, symptom
   dropped, diagnostic retyped, verification in the permanent body, reviewer content in a body the
   squash will copy, issue link standing in for the why, edited released entry.

## 8. Review checklist

- Reader: for every sentence, which of R1 to R5 asks the question it answers (§1)?
- Subject: does it name the change, and would it identify the commit in `git log --oneline` (§2)?
- Problem: does the body open with what was wrong, before the fix (§2)?
- Symptom: is the diagnostic quoted as a literal, with the trigger condition, or is its absence
  stated (§2, §3)?
- Why: is there a sentence of reason beside the issue link, not only the link (§2)?
- Approach: is the alternative a reviewer would propose answered with a mechanism or a number (§2)?
- Verification: does the description say what the tests establish and which are new, and is none of
  it in the commit body (§2, §4)?
- Scope: is every gap named as intentional, every follow-up by number, every stacked change by its
  overlap and order (§2)?
- Changelog: category, observable change, symptom, reference, compatibility, in that order; breaking
  marked in place and first; CVE leading a Security entry (§2, §3)?
- Merge model: detected, and the first branch commit written as a full body where the squash setting
  or a merge commit would otherwise leave `git log` with a title (§4)?
- Trailers: each one has a consumer in this repository, and the closing keyword targets the default
  branch (§5)?
- House style: prefix, limit, sign-off applied only where the workflow consumes them (§6)?
- Nothing: no entry for noise, no empty section, no diff paraphrase, no predicted merge difficulty
  (§7)?
- Rewrite: net delta defended, causal links stated once, released entries untouched (§7a)?

## 9. What these rules rest on

*Measured*, and weighted accordingly when two rules collide:

- **What readers need and how often they read**: 180 Microsoft engineers surveyed (Tao, Dang, Xie,
  Zhang, Kim, FSE 2012); reviewing others' changes ranked first, rationale the most important need
  and the easiest to meet with a description, consistency across the codebase the hardest and risk
  the second hardest.
- **How often messages lack it**: 1,597 messages from five active Java projects, about 44% lacking
  What or Why (Tian, Zhang, Stol, Jiang, Liu, ICSE 2022).
- **The issue link as a substitute for the why**: 611 linked messages from 32 Apache projects, 15%
  failing to supply it (Li and Ahmed, ICSE 2023).
- **What release notes contain and what users want**: 32,425 release notes from 1,000 GitHub
  projects and 314 survey respondents (Bi, Xia, Lo, Grundy, Zimmermann, IEEE TSE 48(6), 2022).

*Asserted*, by the projects and specifications named inline: the Linux kernel's `submitting-patches`
and `stable-kernel-rules`, Git's `SubmittingPatches`, Google's eng-practices, PostgreSQL's commit
message guidance and committing checklist, Zulip's commit discipline, Kubernetes' release-note and
cherry-pick guides, Keep a Changelog 1.1.0 and 2.0.0, Common Changelog, and MITRE's CVE Key Details
Phrasing. Everything about the on-call reader and the backporter is asserted; no study observes
them.

*Derived* from platform mechanics documented by GitHub, GitLab, and `git interpret-trailers`: the
squash rules, the detection table, the default when detection fails, the introducing version in a
changelog entry, and the rule that the commit carries the why in a merge-commit repository. The
evidence, the sources with URLs, the conflicts between them and which reader decided each, and a
test
of these rules on real changes from five workflows are in the research directory
`research/change-description-authoring/` of the `qubership-ai-packages` repository.
