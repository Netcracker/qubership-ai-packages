# Pass 3: A candidate rule set for change descriptions, by reader

This is a synthesis document, not a skill. It carries the evidence a later session needs to write a
repository-independent skill for commit messages, pull request descriptions, and changelog entries. Every rule names the
reader whose need it exists for and the source it rests on. A house style (prefix vocabulary, template, trailer set) is
a per-repository overlay and is kept out of the core.

Sources are `phase1_result.md` and `phase2_result.md`. During synthesis, the Pass 2 claims about primary sources were
checked against those sources; the corrections are marked *corrected* where they appear and collected in section 10.

Wording is out of scope throughout. Tense, mood, length, capitalization, trailing period, punctuation, hedging, and
dialect belong to `english-developer-style`. Where a source's contribution is wording (Beams rules 1 to 6, Pope's 50/72
widths, Kubernetes' past tense for release notes, Git's and Google's imperative mood), it is left out here and not
counted.

## 1. Reader table

| Reader | Artifact opened | Reads first | Question they bring | Sources | Basis |
| --- | --- | --- | --- | --- | --- |
| **R1 Reviewing maintainer** | The PR description and the diff, in the review UI | The title, then the description body | Should I approve this? What was wrong, why is this behavior right, what changed, how was it checked, what is left out, what else touches these files? | Tao et al. FSE 2012; Google eng-practices; Bosu et al. MSR 2015 | **Measured** that reviewing others' changes is the most frequent change-understanding scenario (121 of 180 respondents, 67.2%) and that rationale is the most important information need, "one of the easiest to acquire if an informative change description ... is available" (Tao et al., Microsoft). Read-first order within the artifact: asserted by the guides; two small eye-tracking studies (n=35, n=13, as reported by Pass 2 and not re-verified here) corroborate title-then-description. |
| **R2 Archaeologist** | `git log` and `git blame` output | The subject, then the body; greps for identifiers | Why does this line exist? Why this approach? Which constraint forced it? Which issue? | Tian et al. ICSE 2022; Tao et al.; Li and Ahmed ICSE 2023; Git SubmittingPatches; Google | **Measured**: about 44% of commit messages lack What or Why (Tian et al., 1,597 messages, five Java projects); 15% of issue links fail to supply Why (Li and Ahmed, 611 linked messages, 32 Apache projects). |
| **R3 On-call or support engineer** | The changelog or release notes; sometimes the commit that a blame or a bisect reached | The symptom string they hold: exception class, error text, error code | Is this my incident? What triggers it? Am I on an affected version? Is there a workaround? | CVE Key Details Phrasing; kernel "Describe user-visible impact"; Common Changelog | **Asserted.** No study observes on-call engineers reading release notes. The artifact and the reading order are inferred from what the reader holds at the moment of need: a log line and a version, not a diff. |
| **R4 Upgrading user** | Release notes or changelog for the target version | The version heading, breaking or action-required entries, then the category that affects them | What changed that I can observe? Is it compatible? What must I do? | Keep a Changelog; Common Changelog; Bi et al. TSE 2022; Abebe et al. EMSE 2016 | **Partly measured.** Bi et al. (32,425 release notes, 1,000 GitHub projects, 314 survey respondents) measured content and found users want more detail on new features than producers write. The breaking-first reading order is asserted by Keep a Changelog and Common Changelog. |
| **R5 Release manager or backporter** | Labels, trailers, and the issue's version fields; the commit subject list of a release branch | Kind and severity, then the affected range (`Fixes:`, `Backpatch-through:`), then dependencies | Does this belong on the maintenance branch? Which versions? Does it need another commit first? | kernel stable-kernel-rules and `Fixes:`; PostgreSQL Commit Message Guidance and Committing checklist; Kubernetes cherry-picks | **Asserted, and operationalized in tooling.** No study observes backporters. The signals are documented process and consumed by scripts, which is strong non-empirical evidence that they are read. |

## 2. Artifacts and slots

Each slot states what it owes, the reader it serves (first listed is the one it exists for), the test for whether a
sentence belongs, and the sources. The test is always phrased as a reader and the question a sentence answers; a
sentence that answers none of the questions in its slot belongs in another artifact or nowhere.

### 2.1 Commit subject

One slot. **The change, as what it does to behavior.** Reader R2, then R1. Test: *R2, reading `git log --oneline`, asks:
what did this commit do?* If the line names a file, a phase, or a ticket instead of a behavior, it fails. Sources:
Google, "a short summary of specifically what is being done by the CL" and the bad-description list ("Fix bug", "Fix
build", "Add patch", "Moving code from A to B", "Phase 1", "Add convenience functions", "kill weird URLs")
(<https://google.github.io/eng-practices/review/developer/cl-descriptions.html>); Git SubmittingPatches
(<https://git-scm.com/docs/SubmittingPatches>); Zulip, "a one or two word description of the part of the codebase
changed" plus "a short sentence summarizing your changes"
(<https://zulip.readthedocs.io/en/latest/contributing/commit-discipline.html>). The subject is change-first even though
the body is problem-first; see section 8, conflict 3. Length limits and a type prefix are house style; see section 7.

### 2.2 Commit body

Four slots in order. The verification narrative is not one of them; see conflict 4.

1. **The problem.** What was wrong or what was needed, before any mention of the fix. Reader R2, then R1, R3. Test: *R2
   asks: why did this code have to change?* Sources: kernel, "Describe your problem ... Convince the reviewer that there
   is a problem worth fixing and that it makes sense for them to read past the first paragraph"
   (<https://www.kernel.org/doc/html/latest/process/submitting-patches.html>); Git SubmittingPatches, the body "explains
   the problem the change tries to solve, i.e. what is wrong with the current code without the change"; Zulip's pattern
   "Previously, when X happened, this caused Y to happen, which resulted in ..."; measured need: Tao et al. (rationale
   ranked first) and Tian et al. (Why present in good messages, with "Describe error scenario" the largest Why category
   at 19.8% of 252 good messages; *corrected* category name).
2. **The observable impact and the trigger.** What a user or operator sees, under which circumstances, with the
   diagnostic quoted as a literal. Reader R3, then R5, R1. Test: *R3 asks: is this my stack trace, and what provokes
   it?* Sources: kernel, "Describe user-visible impact ... include anything that could help route your change
   downstream: provoking circumstances, excerpts from dmesg, crash descriptions, performance regressions, latency
   spikes, lockups, etc." (*corrected*: the source does not say "oops" in this sentence); CVE Key Details Phrasing, the
   `[VULNTYPE] in [COMPONENT] in [VENDOR] [PRODUCT] [VERSION] allows [ATTACKER] to [IMPACT] via [VECTOR]` template
   (<https://www.cve.org/Resources/General/Key-Details-Phrasing.pdf>). Basis: asserted. Where a defect has no observable
   symptom (a leak with no diagnostic), the slot says so in one clause rather than staying silent; whether an absent
   symptom is a defect of the message is a human judgment (section 11, kernel sample).
3. **The change and why this approach.** What was done, the constraint that forced it, the alternative a reader would
   propose and why it was rejected, and any measured trade-off. Reader R2, then R1. Test: *R2 asks: why not the obvious
   fix?* and *R1 asks: what would I have proposed, and has it been answered?* Sources: Git SubmittingPatches, the body
   "justifies the way the change solves the problem, i.e. why the result with the change is better" and lists "alternate
   solutions considered but discarded, if any"; Google, "why this is the best approach. If there are any shortcomings to
   the approach, they should be mentioned"; kernel, "Once the problem is established, describe what you are actually
   doing about it in technical detail" and "If you claim improvements in performance, memory consumption, stack
   footprint, or binary size, include numbers that back them up. But also describe non-obvious costs." Basis: asserted;
   the "alternatives" slot has no measured support (Pass 2, Q10).
4. **The references.** Issue, report, discussion, introducing commit, backport range, as trailers. Reader R5, R2, R3,
   and the tools that parse them. Section 3 has the list. The one-line why in slot 1 is not replaced by the link: Git
   SubmittingPatches, "Instead of giving a URL to a mailing list archive, summarize the relevant points of the
   discussion"; Li and Ahmed, 15% of links did not provide Why
   (<https://stairs.ics.uci.edu/papers/2023/Commit_Messages.pdf>).

Not in the body: the test plan, the review-round history, screenshots, and checklists. In an email workflow they go
below the `---` separator, which "serves the essential purpose of marking for patch handling tools where the changelog
message ends" (kernel). In a pull request workflow they go in the description's verification section or in comments; see
2.5 and section 4.

### 2.3 Trailers

A block of `Key: value` lines at the end of the message, preceded by a blank line, with no blank lines inside. Keys are
ASCII alphanumerics and hyphens (`git interpret-trailers`, <https://git-scm.com/docs/git-interpret-trailers>;
*corrected*: the blank line before the block is required, and the source does not speak of spaces replaced by dashes). A
`---` line ends the message for the parser. Which trailers, and for whom, is in section 3.

### 2.4 Pull request title

One slot. **A searchable, accurate summary of the change**, which in a squash-merge repository seeds the commit subject
and in a merge-commit repository becomes the second line of the merge commit. Reader R1, then R2. Test: *R1, reading a
list of thirty open pull requests, asks: which one is this?* Sources: platform mechanics (GitHub,
<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests>;
GitLab, `%{title}` is the default squash template,
<https://docs.gitlab.com/user/project/merge_requests/commit_templates/>); Google's first-line rule applies because the
title becomes that line. Basis: derived from mechanics.

### 2.5 Pull request description

Five slots in order; the last two are conditional.

1. **Why.** The problem, the observable symptom, and the condition that makes it reachable; the same content as commit
   body slots 1 and 2. Reader R1, then R2 and R3 where the description becomes the commit body. Test: *R1 asks: is there
   a problem worth fixing?* Sources: kernel; Google; Tao et al.
2. **What.** The behavioral change, not the changed files, and why this approach. Reader R1, then R2. Test: *R1 asks: is
   this the right behavior, and would I have done it differently?* Sources: Google; Git SubmittingPatches. The rejected
   alternative a reviewer would propose belongs here, collapsed where the platform allows; the baseline's rule for it is
   one team's practice (asserted).
3. **Verification.** What the tests establish, which tests are new, and any manual check with what it showed. Reader R1
   only. Test: *R1 asks: what would fail if this were wrong?* Sources: Google eng-practices on reviewing tests; Tao et
   al. measured that "does this change break any code elsewhere?" (I-9) is the second hardest information need to
   acquire. Basis: the slot is asserted; the need it serves is measured. This slot does not belong in `git log`
   (conflict 4).
4. **Scope.** What is deliberately left out, which follow-up exists by number, and which related or stacked pull
   requests overlap and in what order they depend. Reader R1, then R5. Test: *R1 asks: is this gap intentional?* and *R5
   asks: does this need another change first?* Sources: Google, shortcomings; Tao et al., I-10 "are there other places
   that need similar changes" is the hardest information need to acquire; Kubernetes cherry-picks for dependency order
   (<https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md>). Basis:
   asserted.
5. **Release-note block**, where the repository's tooling reads one. The user-facing sentence, or `NONE`. Reader R4,
   then R3. Kubernetes puts it in a fenced `release-note` block in the PR template (*corrected*: the fence is in the
   template, not in the guide; the guide says to add the note "beneath the question *Does this PR introduce a
   user-facing change?*", <https://github.com/kubernetes/community/blob/master/contributors/guide/release-notes.md>);
   Prometheus uses a `release-notes` fence in its template (section 11). Basis: documented mechanics, project-specific.

Reviewer-only content (checklists, screenshots, the template's own comments, round-by-round history) is not a slot. It
lives in comments, or in a collapsed block, and never in a description that a squash setting will copy into the commit
body (section 4).

### 2.6 Changelog entry

Five parts in order, under a category heading. Section 5 argues the order.

1. **Category**: Added, Changed, Deprecated, Removed, Fixed, Security (Keep a Changelog 1.1.0,
   <https://keepachangelog.com/en/1.1.0/>). Reader R4. Test: *R4 asks: which kind of change is this?*
2. **The observable change**, first, self-describing without the heading. Reader R4. Test: *R4 asks: what can I now do,
   or what now happens differently?* Sources: Common Changelog 2.4.1, "Each change must be self-describing, as if no
   category heading exists" (<https://common-changelog.org/>); Bi et al., users want impact and detail, and a tester's
   complaint that "'Bug fixes and performance improvements' is completely meaningless. What was fixed? How will
   performance improve?" (measured).
3. **The symptom and the trigger**, with the diagnostic quoted as a literal and the setting or condition named. Reader
   R3. Test: *R3 asks: can I grep this entry with my log line, and does the condition match my deployment?* Sources:
   Common Changelog's antipattern "json-parser 8.0.2 is fixed (#295)", which "doesn't explain or reference what was
   fixed" (*corrected*: the word "symptom" is a paraphrase); CVE phrasing; kernel impact rule. Basis: asserted.
4. **References**: the commit or pull request, the issue, the CVE. Reader R3, R2, R5. Sources: Common Changelog 2.4.2,
   "changes must reference relevant commits, and should reference tickets or pull requests when available"; Keep a
   Changelog 2.0.0, "When a Security entry has a CVE identifier, lead with it so readers and security tools can match
   the entry to the advisory" (<https://keepachangelog.com/en/2.0.0/>; *corrected*: 1.1.0 says nothing about CVEs).
5. **Compatibility and action**: whether the change is breaking, what the reader must do, and for a regression the
   version that introduced it. Reader R4, then R5, R3. Test: *R4 asks: will my upgrade break, and what do I do?*
   Sources: Keep a Changelog 1.1.0, "list deprecations, removals, and any breaking changes"; Common Changelog 2.4.4,
   `**Breaking:**` prefix, sorted first per category; Kubernetes "action required". The introducing version is a
   recommendation with no observed practice (section 5).

## 3. Greppability

The message is the only artifact indexed by the strings a later reader holds. Two kinds of string matter: trailers,
which tools parse, and identifiers, which people grep.

**Trailers.** Each row names the consumer and the reader who benefits.

| Trailer | Form | Consumer | Reader | Source |
| --- | --- | --- | --- | --- |
| `Fixes:` | `Fixes: <12+ hex sha> ("<subject>")`, one line | Kernel stable team scripts; "assists the stable kernel team in determining which stable kernel versions should receive your fix" | R5, then R3 (introducing version) | kernel submitting-patches |
| `Fixes #n` / `Closes #n` / `Resolves #n` | GitHub or GitLab issue reference | The platform: closes the issue when the change merges into the default branch; "If the pull request targets any other branch, then these keywords are ignored" | R2, R5 | GitHub (<https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue>); GitLab default closing pattern, `%{issues}` template variable |
| `Closes:` (kernel) | URL of the bug report; "Private bug trackers and invalid URLs are forbidden" | Humans; regzbot | R2, R3 | kernel submitting-patches |
| `Link:` | URL of the discussion or patch archive | Humans | R2 | kernel submitting-patches |
| `Discussion:` | a `postgr.es/m/` URL carrying the message id | Humans; PostgreSQL process | R2 | PostgreSQL Commit Message Guidance (<https://wiki.postgresql.org/wiki/Commit_Message_Guidance>) |
| `Backpatch-through:` | Oldest major version, e.g. `15`; a range `13-15`; or `15 only` | `src/tools/git_changelog`, which groups identical messages across branches for release notes | R5 | PostgreSQL Commit Message Guidance; Committing checklist (<https://wiki.postgresql.org/wiki/Committing_checklist>) |
| `Cc: stable@vger.kernel.org # <ver>: <sha>: <subject>` | Optional prerequisite list in an inline comment | Kernel stable team; "The tag sequence has the meaning of: `git cherry-pick a1f84a3 ... git cherry-pick <this commit>`" | R5 | kernel stable-kernel-rules (<https://www.kernel.org/doc/html/latest/process/stable-kernel-rules.html>) |
| `Reported-by:` | Name and address | Credit | R2 (who saw it first) | kernel; PostgreSQL |
| `Co-authored-by:` | Name and address | GitHub and GitLab attribution | none of the five; provenance | GitHub docs; GitLab `%{co_authored_by}` |
| `BREAKING CHANGE:` | Footer, or `!` after the type | release-please and semantic-release: major bump and changelog section | R4, through the tool | Conventional Commits 1.0.0 (<https://www.conventionalcommits.org/en/v1.0.0/>); release-please (<https://github.com/googleapis/release-please>) |
| `Change-Id:` | Gerrit hash | Gerrit patch-set tracking | none of the five | Gerrit |
| `Signed-off-by:` | DCO sign-off | Legal provenance | none of the five | kernel; Git |

**Identifiers.** These rules are structural because they decide what a search finds, not how a sentence reads.

- **Quote the diagnostic as a literal**: exception class, error text, error code, log line, exactly as emitted,
  including its punctuation. Reader R3. Sources: CVE phrasing (under-reporting "you may not be able to make the
  appropriate match later on"; over-reporting "can obscure the distinguishing details"); kernel dmesg excerpts; Common
  Changelog. Basis: asserted. Observed in the PostgreSQL and Kubernetes samples of section 11.
- **Name the public identifier the reader will grep**: the option, flag, class, method, or configuration key that the
  change touches, spelled as the code spells it. Reader R2, R3. Source: Google, "Future developers will search for your
  CL based on its description." Basis: asserted. A private helper is named only where its name is what the reader will
  search for; that boundary is a wording rule in `english-developer-style` and is not restated.
- **Name both versions**: the one that introduced a defect and the one that fixes it, where the project versions its
  releases. Reader R3, then R5. Sources: kernel `Fixes:` (the introducing commit, from which the stable team derives the
  version); GitHub Security Advisories, affected and patched version fields; CVE phrasing `[VERSION]`. Basis: asserted;
  the changelog placement is a recommendation (section 5).
- **Reference the issue by identifier and still write the why.** Reader R2, R3. Sources: Li and Ahmed, 15% of links do
  not provide Why, against 89.77% of surveyed developers expecting them to; Git SubmittingPatches, summarize rather than
  link. Basis: measured. Minimum inline content when an issue exists: one sentence of problem, the issue identifier, and
  the symptom string.
- **Keep the message identical across branches when back-patching**, so that tooling groups the copies as one change.
  Reader R5. Source: PostgreSQL Committing checklist, "Commit messages for multiple branches should be identical when
  back-patching, in order to have tooling recognize the redundancy for purposes of compiling release notes." Basis:
  asserted; workflow-bound (section 6).

## 4. Squash-merge repositories

**Mechanics, cited.** On GitHub the squash commit's default message "uses the commit title and message if the pull
request contains only 1 commit, or the pull request title and list of commits if the pull request contains 2 or more
commits", and the repository can be set to "just the pull request title, the pull request title and commit details, or
the pull request title and description"
(<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests>;
*corrected*: the about-pull-request-merges page no longer carries the table). The pull request number is appended to the
subject. The merging maintainer can edit the message before merging. On GitLab the default squash template is
`%{title}`; a project can compose `%{title}`, `%{description}`, `%{issues}`, `%{reference}`, `%{first_commit}`,
`%{all_commits}`, and `%{co_authored_by}` (<https://docs.gitlab.com/user/project/merge_requests/commit_templates/>).
Closing keywords in the description or a commit close the issue on merge to the default branch (GitHub; GitLab
`managing_issues`). Whether `Co-authored-by:` trailers survive a squash is not stated in the GitHub pages checked; treat
it as observed behavior, not documented.

**Rules, each marked.**

1. *Cited.* Write the pull request title as the commit subject it will become: the change, not a placeholder. (GitHub
   and GitLab squash defaults; Google's first-line rule.)
2. *Cited.* Where the repository uses "pull request title and description", the description is the commit body. Shape it
   as section 2.2: problem, impact, approach, references. (GitHub settings page.)
3. *Derived.* Where the repository uses the default or "commit details", the body is the list of branch commit messages,
   so the durable why must be in the branch's commits, or the maintainer must edit at merge. A pull request whose branch
   commits read "Fix lint" and "Apply suggestion" leaves `git log` with those lines and nothing else (section 11,
   Renovate sample). The agent therefore writes the first branch commit's message as a full commit body regardless of
   how rich the description is.
4. *Derived.* Reviewer-only content, checklists, screenshots, template comments, and the verification transcript stay
   out of a description that will become the body. Compress verification to one line naming what the tests establish;
   move the rest to comments or a collapsed block that the maintainer strips.
5. *Cited.* `Fixes #n` and `Closes #n` in the description or a commit close the issue on merge to the default branch and
   are ignored on any other target branch. A backport pull request therefore carries the reference for humans, not for
   the platform.
6. *Derived.* Where a release tool reads the squash subject (release-please, semantic-release), the title's prefix is
   what the tool parses; get the prefix right in the title, because the branch commits are discarded from the tool's
   view.

**Detection, derived.** The agent reads the last twenty or so subjects from `git log --format=%s%n%b`:

- subjects ending in `(#123)` and no `Merge pull request` lines: squash merge;
- `Merge pull request #123 from` lines: merge commits, and the pull request body never reaches `git log` unless a branch
  commit carries it;
- `Change-Id:` or `Reviewed-on:` trailers: Gerrit, one commit per change, the commit message is the review description;
- `Signed-off-by:` chains with `Link: https://patch.msgid.link` or `Link: https://lore.kernel.org`: email patches;
- a `CHANGELOG.md` with an `Unreleased` heading, or a `changes/` or `newsfragments/` directory: entries are written in
  the pull request; a changelog whose entries all carry `(#123)` references and no `Unreleased` section: entries are
  curated at release.

**Default when detection fails.** Treat the repository as squash-merging with "title and description": write the
description so it can stand as a commit body, and write the first branch commit's message the same way. This is the
conservative case: it keeps the durable content in both places the platform might copy from, and it costs one paragraph
of duplication in the case that turns out to be merge commits.

## 5. The changelog entry as the on-call reader's artifact

The upgrading user (R4) and the on-call engineer (R3) open the same file with different questions. R4 asks what changed
and whether it is compatible; R3 holds a stack trace and asks whether this entry is their incident. Keep a Changelog and
Bi et al. write for R4; CVE phrasing, the kernel's impact rule, and Common Changelog's antipattern lean toward R3. Pass
2 settled that one entry serves both if its parts are ordered so that each reader stops where their question is
answered:

1. the observable change (R4 stops here for a feature);
2. the symptom and trigger, quoted literally (R3 greps this; R4 skips it);
3. the references (both follow them);
4. compatibility, action required, and the introducing version (R4 and R5 read this; R3 reads the version).

The order is a decision, not a finding. Its justification is cost: putting the symptom second costs R4 one clause to
skip, while putting it last or omitting it costs R3 the whole entry, because the entry then contains nothing their
search matches. Prometheus' hand-written changelog was found to use this order without any rule requiring it: "Set a
request timeout for `docker_sd` and `dockerswarm_sd` on `unix`, `npipe`, and `tcp` hosts. Previously an unresponsive
daemon could freeze discovery indefinitely, silently pinning targets to a stale snapshot. #19237" (section 11).

**What no project was found doing.** None of the shortlisted projects records the version that introduced a defect
inside the changelog entry. The kernel keeps it in `Fixes:`, GitHub Security Advisories keep it in structured
affected-version fields, and PostgreSQL's release notes state the back-patch range per release rather than per entry.
The recommendation to write "regression since 3.12.0" into a `Fixed` entry therefore rests on R3's question alone ("am I
on an affected version?") and is labeled *derived*. It is cheap where the introducing version is known from a `Fixes:`
trailer or a bisect, and it is not to be guessed.

**Breaking changes.** *Corrected.* Keep a Changelog 1.1.0 asks only that deprecations, removals, and breaking changes be
listed. Keep a Changelog 2.0.0 says to "Keep the **Breaking:** marker on the entry itself, within its type, rather than
collecting breaks into a separate section, so anyone scanning Changed or Removed sees them in place." Common Changelog
2.4.4 prefixes `**Breaking:**` and sorts such entries "before other changes (per category)". The baseline's "own block
at the top of the version" matches neither current source; Kubernetes' "Urgent Upgrade Notes" section is the one
large-project example of a separate block, and it exists because Kubernetes release notes run to hundreds of entries.
Decision for R4: mark in place and sort first per category by default; a separate top block is a house option for
release notes long enough that R4 cannot scan every category. See conflict 5.

## 6. Workflow gating

| Rule | Home workflow | Precondition to apply elsewhere | False-positive risk outside | Principle that transfers |
| --- | --- | --- | --- | --- |
| Content below `---` is stripped | Email patches (`git am`) | Never outside email; in a pull request the separator is inert text | High: the test plan lands in `git log` | Keep verification out of the permanent body (conflict 4) |
| `Cc: stable # <ver>` and prerequisite lists | Kernel stable trees | Only where a stable team reads the trailer | High | Name backport dependencies somewhere R5 reads (PR scope section, label) |
| `Fixes: <sha> ("subject")` | Kernel | Where a project adopts it; elsewhere it is prose that only R5 reads | Medium: no consumer, but harmless | Name the introducing commit or version |
| `Backpatch-through:` and identical messages across branches | PostgreSQL | Where a project maintains release branches and tooling groups by message | Medium: identical messages can misdescribe a diverging branch | Record the back-patch range where R5 looks |
| `Change-Id:` | Gerrit | Where `git log` already shows it | High | None; it is tooling |
| `/kind`, `/release-note-none`, fenced `release-note` block | Kubernetes (Prow) | Where the PR template has the block | High | Separate the user-facing sentence from the reviewer-facing description |
| `type(scope):` prefix | Repositories with release-please, semantic-release, or commitlint | Where the history already carries prefixes or a config file names the tool | Medium to high: Common Changelog, "it gives commit authors the false impression that their messages are descriptive" | Mark fix versus feature where R5 reads it (label, category, or prefix) |
| 50-character subject | Email and terminal habit (Git SubmittingPatches soft limit; Pope) | Where the project states it | Low, but it is a linter's job | Subject stands alone in a one-line listing |
| News fragment per change (towncrier) | Twisted and Python projects with `newsfragments/` | Where the directory exists | High | The author, not a tool, writes the user-facing sentence |
| Past tense in release notes | Kubernetes | Wording; out of scope | n/a | n/a |

## 7. Rules no reader needs

| Prescription | Source | Whom it serves | Decision |
| --- | --- | --- | --- |
| `Signed-off-by:` | Kernel, Git | DCO and legal provenance | House option where DCO is enforced; not reader-serving |
| `Change-Id:` | Gerrit | Gerrit's patch-set tracking | Drop unless the history shows it |
| 50-character subject | Git SubmittingPatches (soft), Pope | Terminal and email display | Drop from the core; a linter check at the project's limit |
| `type(scope):` prefix | Conventional Commits | release-please, semantic-release, commitlint | House option, applied only where a tool parses it; it serves the tool, not a reader (Common Changelog critique) |
| `Discussion:` URL required | PostgreSQL | The pgsql-hackers archive workflow | Drop outside PostgreSQL; the principle (link the design discussion) is in section 3 |
| `/kind`, `/release-note-none` | Kubernetes | Prow | Drop unless Prow is present |
| One news fragment file per change | towncrier | Merge-conflict avoidance in the changelog file | House option where the directory exists |
| Imperative mood, tense, 72-column wrap | Beams, Pope, Kubernetes | Readers, but as wording | Out of scope here; owned by `english-developer-style` |

## 8. Conflicts and how they were decided

1. **Issue link versus inline why.** Tian et al. "treated links of issue reports and pull requests in commit messages as
   a way to provide Why information" and called the approach controversial. Li and Ahmed measured that "15% of issue
   reports/pull requests do not provide Why", against "89.77%" of surveyed developers who expected them to. Git
   SubmittingPatches independently says to summarize the discussion rather than link it. **R2 and R3 win**: the message
   carries one sentence of problem, the identifier, and the symptom string; the link is supplementary. The author loses
   one sentence of brevity and is not harmed. *Corrected*: Li and Ahmed's `add @SPI annotation (#6436)` example
   illustrates their "Additional Information on What" category (21 commits), not "Content Repetition" (59 commits).
2. **Who owns the `Fixed` entry.** Keep a Changelog and Bi et al. write for R4; CVE phrasing and Common Changelog's
   antipattern for R3. **Both, in the order of section 5**; R3's part goes second because omitting it costs R3 the entry
   and including it costs R4 a clause.
3. **Problem first or change first.** The kernel orders problem, impact, solution; Google puts "specifically what is
   being done" on the first line with the problem in the body; release tools read only the subject and footers.
   **Resolved by artifact**: the subject is change-first, because R2 reads it in a one-line listing where a problem
   statement does not identify the commit; the body is problem-first, because R2 and R1 read it to learn why. Neither
   reader is harmed, because the two lines serve different reading moments; Google and the kernel agree once the
   artifacts are separated.
4. **Verification in the permanent record.** The kernel strips it below `---`; Google and most PR templates ask for it;
   a squash setting copies the description into the body. **R1's need is met in the pull request; R2's noise is kept out
   of `git log`**: verification lives in the description's third slot, compressed to one line where the description will
   become the body. Default when the merge model is unknown: assume squash and compress.
5. **Breaking changes: a separate block or an in-place marker.** The baseline and Kubernetes' "Urgent Upgrade Notes" use
   a block; Keep a Changelog 2.0.0 and Common Changelog mark in place and sort first per category. **R4 wins under
   either**, so the deciding factor is length: in-place marking by default, a top block where the notes are long enough
   that R4 cannot scan every category. The losing side loses nothing, since both keep breaking changes ahead of
   everything else in their category.
6. **Unreleased section.** Keep a Changelog keeps it; Common Changelog drops it because "it cannot add the necessary
   (self) references. These can only be added after the fact." **Workflow-dependent**: where entries are written in the
   pull request, keep it; where entries are curated from history at release, drop it. Default when undetected: keep it.
7. **Where the durable why lives in a merge-commit repository.** *New, from the test in section 11.* Google's CL
   description is the commit message, so their guidance has no gap. On GitHub with merge commits, the pull request
   description never reaches `git log`; Kubernetes, Prometheus, and GitHub CLI all showed a rich description above a
   one-line commit. Zulip, Git, and the kernel place the why in each commit. **R2 wins**: the commit message carries
   problem, impact, and approach whether or not the description repeats them, because the description is reachable only
   while the platform is. The pull request author loses nothing but the duplication. Basis: derived from mechanics and
   observed in three samples.

## 9. Anti-patterns

| Anti-pattern | Source | Reader it fails |
| --- | --- | --- |
| `Fix bug`, `Fix build`, `Add patch`, `Moving code from A to B`, `Phase 1`, `Add convenience functions`, `kill weird URLs` | Google eng-practices | R2, R1 |
| A message with no Why or no What (about 44% of the sample) | Tian et al. | R2 |
| An issue link standing in for the why, where the link repeats the subject or lacks rationale | Li and Ahmed; Git SubmittingPatches | R2, R3 |
| A body that paraphrases the diff | Google; Common Changelog | R2, R1 |
| Commit log diffs used as a changelog: "they're full of noise" | Keep a Changelog | R4, R3 |
| Ignoring deprecations; confusing dates; inconsistent changes ("only mentions some of the changes") | Keep a Changelog | R4 |
| `json-parser 8.0.2 is fixed (#295)`: the ticket number where the change should be | Common Changelog | R3, R4 |
| "Bug fixes and performance improvements" | Bi et al., survey respondent | R4, R3 |
| A prefix mistaken for descriptiveness | Common Changelog | R2 |
| A tangled change that addresses several concerns at once | Tao et al. (composite changes hardest to understand); Google "Small CLs" | R1, R5 |
| Divergent messages for the same fix on different branches | PostgreSQL Committing checklist | R5 |
| A backport with an undeclared prerequisite | kernel stable-kernel-rules | R5 |
| Maintenance noise in the changelog: dotfiles, dev dependencies, formatting | Common Changelog 3.2 | R4 |
| A rich pull request description above a one-line commit in a merge-commit repository | Derived (section 11) | R2 |
| A squash body made of `Fix lint` and `Apply suggestion` lines | Derived (section 11) | R2 |
| A fix that names the mechanism and never the symptom | kernel impact rule; CVE phrasing | R3 |
| Unquoted or retyped error text | CVE phrasing; Common Changelog | R3 |

## 10. Evidence map

**Measured.** These rest on a study with a stated sample.

| Claim | Study | Sample |
| --- | --- | --- |
| Reviewing others' changes is the most frequent change-understanding scenario (67.2%); rationale is the most important information need and "one of the easiest to acquire if an informative change description ... is available"; consistency (I-10) is the hardest to acquire and risk (I-9) the second | Tao, Dang, Xie, Zhang, Kim, FSE 2012, <https://taoxie.cs.illinois.edu/publications/fse12-study.pdf> | 180 survey respondents at Microsoft (99 developers, 56 test engineers, 25 program managers), plus interviews |
| About 44% of commit messages could be improved because they lack What or Why; "Describe error scenario" is the largest Why category (19.8%) and "Object of change" the largest What category (56.8%) among good messages | Tian, Zhang, Stol, Jiang, Liu, ICSE 2022, <https://arxiv.org/abs/2202.02974> | 1,597 classified messages from five active Java projects; taxonomy percentages over 252 good messages |
| 15% of issue and pull request links fail to provide Why; 89.77% of surveyed developers expected them to | Li and Ahmed, ICSE 2023, <https://stairs.ics.uci.edu/papers/2023/Commit_Messages.pdf> | 611 linked messages from 32 Apache Java projects; 93 surveyed developers |
| Issues fixed appear in 79.3% and new features in 55.1% of release notes; users want more new-feature detail than producers write | Bi, Xia, Lo, Grundy, Zimmermann, IEEE TSE 48(6):1834–1852, 2022, DOI 10.1109/TSE.2020.3038881 | 32,425 release notes from 1,000 GitHub projects; 15 interviews; 314 survey respondents |
| Six information types in release notes: title, system overview, resource requirements, installation, addressed issues, caveats | Abebe, Ali, Hassan, EMSE 21(3), 2016, DOI 10.1007/s10664-015-9377-5 (*corrected* from a wrong DOI in Pass 1) | 85 release notes across 15 systems, as reported by Bi et al. |
| Smaller changes receive a higher proportion of useful review comments | Bosu, Greiler, Bird, MSR 2015 | Microsoft code reviews |
| Title and description are read before the diff | Begel and Vrzakova (n=35); an ETRA 2025 GitHub study (n=13), both as reported by Pass 2 and not re-verified here | Small single-site eye-tracking samples; corroborating only |

**Asserted.** Everything else: the kernel's body order and impact rule, Google's first line and shortcomings, Git's
three-part body, the whole of R3 (symptom, trigger, versions, workaround), the whole of R5 (trailers, severity,
prerequisites, identical messages), the changelog part order, the breaking-change placement, the scope slot, and the
rejected-alternatives slot. **Derived** from platform mechanics: the squash-merge rules, the detection heuristics, the
introducing version in the changelog entry, and conflict 7. The skill must not present any of these as measured.

**Unmeasured entirely.** What on-call engineers and backporters read, and in what order; whether the changelog order of
section 5 helps them; whether `Co-authored-by:` survives a squash on GitHub (not documented on the pages checked).

## 11. Test of the rule set

Six real public changes from five workflows, fetched on 2026-09-02. The purpose is to check that the slot tests
discriminate, not to grade the authors; each project's house rules were followed by its authors and the observations
below are about what the tests reveal, not about anyone's diligence.

| Sample | Workflow | Present | Absent | What the tests told the reader that the raw text did not |
| --- | --- | --- | --- | --- |
| Linux `3220b62fbb8a`, "net: fix a resource leak in copy_net_ns() error handling path" | Email patches | Problem (slot 1, "resources allocated by net_alloc() are leaking"); approach and rejected alternative (slot 3, "We cannot simply jump to the put_userns: label ... But we can reorder"); `Fixes:` with the introducing commit; `Closes:` report URL; `Link:`; `Reported-by:` | Slot 2: no observable symptom or trigger | The R3 test flagged the absence and also showed why it is legitimate: a leak on an error path has no diagnostic to quote. The slot should be allowed to say so in one clause; whether an absent symptom is a defect is the human judgment Pass 2 assigned it. |
| PostgreSQL `c2c696c1a482`, "Fix checkpointer restartpoint assertion failure" | Rebase and back-patch | Problem with trigger ("When recovery starts from a backup without a signal file"); verbatim diagnostic `TRAP: failed Assert("TransactionIdIsValid(initial)")`; approach; `Backpatch-through: 14`; `Discussion:`; `Reported-by:` | Introducing version | Every R3 and R5 question was answered from the message alone. "Backpatch to all supported versions" in prose duplicates the trailer and answers R5's affected-range question in words, which the trailer alone would not. |
| Go `cmd/compile: fix large riscv64 move/zero` | Gerrit | Subject with component; two sentences of mechanism ("We were packing the size into an int32"); `Fixes #81240`, `Fixes #81242`; `Change-Id:`; `Reviewed-on:` | Slot 2 symptom; the why beyond the mechanism | The R3 test sent the reader to the issue, where Go keeps the symptom; Li and Ahmed's 15% is the risk the test names. The R5 test found no backport signal in the message; Go carries it in issue labels, outside anything the author writes here. |
| Kubernetes PR 141329, "fix job pod could not be removed while removing finalizer failed" | Merge commits via Prow; PR template | In the description: trigger conditions as four steps; verbatim log line `"syncing orphan pod failed" err="Timeout: request did not complete within requested timeout"`; `Fixes #141346`; `/kind bug`; release note "Ensure job controller retries removing tracking finalizer, unblocking pod removal." | In the commit: everything but the title. In the release note: the symptom | The R2 test on `git log` returned the title and nothing else; the description that satisfies R1 and R3 is reachable only on GitHub. This is conflict 7. The R3 test on the release note found the fix but not the log line the operator holds. |
| Prometheus PR 19557, "promql: fix info() with mixed identifying-label presence" | Merge commits; hand-written `CHANGELOG.md`; `release-notes` fence in the template | Description in problem, change, verification order; regression test named; release note `[BUGFIX] PromQL: Fix info() enrichment when input series use different subsets of identifying labels` | Commit body (title and `Signed-off-by:` only); introducing version | The slot tests matched the description one to one, which shows the three-slot shape occurs without a rule imposing it. The release note names the function and the trigger, which is the R3 content for a silent wrong result. The R2 test failed on the commit, as in the Kubernetes sample. |
| Renovate PR 44987, "fix(cache): re-add cacache.verify() to garbage collect orphaned content from put() overwrites" | Squash with "title and commit details"; semantic-release changelog from prefixes | Description: problem and mechanism; measured impact ("~5 GB", "~565k unreferenced content blobs"); quantified trade-off answering an earlier objection (#29795); related pull requests with dependency direction (#28275, #29860, #42543); honest verification ("No unit tests, but ran on a real repository") | Squash commit body: `* fix(cache): ...`, `* Fix lint`, `* Apply suggestion from @bbodenmiller` (twice); release notes: subject line only | The squash setting, not the author, decided what R2 gets; the body is section 4, rule 3's failure case. The `fix(cache)` prefix reached the release notes through semantic-release, so R4 gets the what and R3 gets no symptom (cache growth, upload failures). |

**Changelog test.** Prometheus `CHANGELOG.md` 3.14.0
(<https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md>), 36 entries, checked against section 5's order.
Entries with a symptom put it after the change, as the order predicts ("Fix 100% CPU usage on shutdown that could delay
graceful shutdown and trigger timeout-based kills. #17859"). Configuration keys are quoted as literals
(`stale_series_compaction_threshold`). Compatibility statements appear on `[CHANGE]` entries ("will be rejected in the
next major release"). The slot found empty in every entry was the introducing version, which matches section 5's finding
that no project records it there.

**What the test established.** The slot tests discriminate: they separated messages that answer a reader's question from
messages that do not, across five workflows, and they exposed two failures no source names, both about where the text
ends up rather than what it says (conflict 7 and squash rule 3). They also produced one false positive worth a rule: an
absent symptom on a defect that has none, which the skill should let the author state rather than flag.

## 12. Load-bearing versus refinement

**Load-bearing**, kept under any budget: the commit body's problem slot (2.2.1); the one-line why beside the issue link
(section 3); the verbatim diagnostic (section 3); the observable impact and trigger for a fix (2.2.2); the PR
verification slot naming new tests (2.5.3); the changelog order of section 5; `Fixes:` or an equivalent introducing
reference where the project back-patches; the compatibility statement (2.6.5); the squash rules 1 to 4; the merge-model
detection with its default; conflict 7's rule that the commit carries the why in a merge-commit repository.

**Refinements**, dropped first: the rejected-alternatives block; identical messages across branches; `Cc: stable`
prerequisites; the in-place breaking marker versus a block; the Unreleased decision; maintenance-noise exclusion;
one-line changelog entries; the accuracy-over-brevity title rule; the introducing version in the changelog entry.

## 13. What the skill-writing session should be told

Do:

- Build the skill around the reader table; every rule names its reader first and its source second. Keep the "asserted",
  "measured", and "derived" labels from section 10 in the skill's own text or its companion notes, so an asserted rule
  is never presented as measured.
- Detect the merge model and the changelog model before applying any workflow-bound rule (section 4, detection), and
  apply the default when detection fails.
- Fix the changelog entry order of section 5 and the commit body order of 2.2; make the subject change-first and the
  body problem-first (conflict 3).
- Make the commit message carry the why in every workflow, including merge-commit repositories where the description
  would otherwise be the only copy (conflict 7).
- Give the agent the slot tests as questions with a named reader; a sentence that answers none is cut or moved, and the
  skill says where it moves to.
- Allow the impact slot to state that a defect has no observable symptom (section 11, kernel sample).

Do not:

- Restate or re-derive wording: mood, tense, length, punctuation, dialect, hedging, capitalization, the trailing period.
  Those belong to `english-developer-style`; the skill defers to it in one sentence.
- Reopen conflicts 1 to 6; the decisions and the reader who won are recorded here.
- Treat Conventional Commits prefixes, the 50-character subject, `Change-Id:`, `Signed-off-by:`, `Discussion:`, or Prow
  commands as reader-serving; they are house options gated on detection (sections 6 and 7).
- Put a house style in the core: no prefix vocabulary, no template headings as requirements, no fixed trailer set beyond
  what the detected workflow consumes.
- Sample one repository's authors as exemplars; the section 11 samples check the tests and are not models to copy.
- Cite the baseline's artifact-level table as a source; it was one team's practice, and section 2 replaces it with
  sourced slots. The one row it got right with support is "the commit message carries why the change was needed, for
  whoever runs `git blame` years later" (Tao et al.; Tian et al.).
