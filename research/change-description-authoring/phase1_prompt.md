# Research title

Find what each reader of a change description needs, and which published guidance supplies it

## Goal

Run a broad discovery pass to find candidate sources for an LLM skill that writes and reviews **change descriptions**:
the commit subject and body, the pull request (or merge request) title and description, and the changelog or
release-note entry that a change produces.

The question is not "which style guide is popular" and not "which style guide is best". The question is **what each
reader needs**, and which parts of which sources could be borrowed to build a guide that serves those readers. A source
earns a place by supplying a rule that a named reader needs; a source that only ranks high on adoption does not.

The eventual skill is repository-independent. It has to produce descriptions that are useful on average, across projects
with different merge strategies, issue trackers, and release cadences. A house style (a prefix vocabulary, a template, a
trailer set) is a later, per-repository overlay. So do not sample any single repository's authors as exemplars of good
practice, and do not treat one project's house rule as a general rule without saying which reader it serves outside that
project.

This is Pass 1 only. The goal is discovery and classification, not final ranking.

## The readers

Fix these five readers first and carry them through every part of the report. Every rule a source states should be
attributed to at least one of them, or marked as serving none.

| Reader | Situation | What they need to find |
| --- | --- | --- |
| **R1. Reviewing maintainer** | Reading the change now, deciding whether to approve it | What was wrong; why this behavior is the right one; what changed; how it was verified; what is new test coverage; what is deliberately left out; what else touches the same files |
| **R2. Archaeologist** | Running `git blame` or `git log` years later, holding a line of code | Why the change was needed; why this approach rather than the obvious one; which constraint forced it; the issue; the identifiers and error text they will grep for |
| **R3. On-call or support engineer** | During an incident, holding a stack trace or a log line | The symptom as it appears (exception class, message text, error code); the trigger condition; the versions that introduced and fixed it; the workaround or the setting |
| **R4. Upgrading user** | Reading release notes before upgrading | What changed, in terms of what they can observe; whether it is compatible; what they have to do |
| **R5. Release manager or backporter** | Deciding what to cherry-pick into a maintenance branch | Severity; affected versions; dependencies between changes; whether the change is a fix, a feature, or a refactor |

For each reader, the report must record **which artifact they actually open** (subject line, commit body, PR
description, changelog entry, issue) and **what they read first** in it. Where a source states or measures this, cite
it; where it is your inference, say so.

## Important framing

Do not search for sources that merely agree with the baseline at the end of this prompt. The baseline is the structural
guidance currently embedded in a companion prose-style skill, written from one team's practice. It is a starting point,
not the target. Prefer sources that improve on it, contradict it usefully, or take a different approach.

It is acceptable, and expected, to conclude that no single source covers all five readers. In that case identify the
strongest reusable rule sources per reader and explain how they could be combined.

Two distinctions matter more here than in a general writing guide:

- **Structure versus wording.** Structural rules say what goes where, in what order, with what identifiers: the slots of
  a body, the trailer lines, the position of the issue reference, the shape of a changelog entry. Wording rules say how
  a sentence is phrased: tense, mood, length, voice. Wording is already governed by the companion skill and is out of
  scope (see below). Classify every rule you meet as structural or wording, and keep only the structural ones.
- **Home project versus transfer.** Most sources were written for one project's workflow. A kernel rule about patch
  series does not transfer to a repository that squash-merges every pull request; a Conventional Commits type prefix
  helps a release tool and does nothing for the on-call reader. For each source, note the workflow it assumes (email
  patches, Gerrit, GitHub squash-merge, merge commits, rebase-and-merge, monorepo) so that Pass 2 can assess the
  false-positive risk of adopting its rules elsewhere.

## Out of scope

The following is owned by the companion skill `english-developer-style` and must not be restated or re-derived:

- voice, tone, person; sentence length; paragraph craft
- imperative mood in the subject, present tense, capitalization, trailing period
- em-dash, hyphen, and punctuation policy; LLM writing tells
- hedging; `currently`; bare `will`
- British and US dialect policy; inclusive language
- error-message and log-message wording

A source whose only contribution is wording is a reject; say so in one line. A source may still count when its
structural rules are strong even though its wording rules duplicate the above; say which parts matter.

Also out of scope: commit-message *generation* research (models that write messages from diffs) except where it measured
what a good message contains; code-review process guidance that does not touch the description; branching and
release-process guidance that does not touch what a description says.

## Questions the pass should answer

Use these to steer the search. Pass 1 does not have to answer them fully; it has to find the sources that can.

1. **Slots.** Which sources prescribe an order of content for a commit body or a PR description (problem, cause, change,
   verification, scope left out), and do any of them say which reader each part serves? Which sources prescribe only a
   subject line?
2. **Greppability.** Which sources say that the message must carry the identifiers a later reader will search for: the
   exception class, the error text quoted verbatim, the method or option name, the issue key, the version? Which say the
   opposite, that the message should stay abstract and let the diff carry the identifiers?
3. **Trailers and references.** What conventions exist for machine-readable lines: `Fixes:`, `Closes #`, `Link:`, `Cc:
   stable`, `Backpatch-through:`, `Reported-by:`, `Co-authored-by:`, `Change-Id`, `BREAKING CHANGE:`, `Discussion:`?
   Which tool consumes each one, and which of the five readers benefits? What does `git interpret-trailers` standardize?
4. **Versions.** Where does the version that introduced a defect and the version that fixed it get recorded: the commit,
   the changelog, the issue, a trailer? Which projects record the introducing commit (kernel `Fixes:`), and what do they
   say it is for?
5. **Squash-merge repositories.** What guidance exists for a repository where the PR title becomes the commit subject
   and the PR body becomes, or seeds, the commit body? What do GitHub and GitLab do by default when squashing, and which
   projects instruct authors accordingly? Where does the reviewer-facing content (test plan, screenshots, checklist) go,
   so that it does not end up in `git log` forever?
6. **Changelog as the on-call artifact.** Which changelog and release-note conventions name the symptom rather than the
   fix, name the trigger condition, and name the affected versions? Which keep the changelog for humans and refuse a
   commit-log dump? Which projects generate release notes from commits or PR labels, and what do they lose? How do
   security advisories describe a defect for an operator, and is that a model for a `Fixed` entry?
7. **Backport signals.** What do projects that maintain several release branches require in a description so that the
   backporter can decide: severity labels, affected-version fields, `Cc: stable` rules, cherry-pick templates,
   "backpatch through" lines?
8. **Anti-patterns.** Which anti-patterns does each source name (paraphrasing the diff, `fix bug`, `address review
   comments`, a subject that names the file rather than the behavior, a body that narrates the investigation, an issue
   link with no summary), and which reader does each one fail?
9. **Evidence.** What has been measured about what a description contains and what its readers use? Tian et al., "What
   makes a good commit message?" (ICSE 2022) is the anchor; find its successors and any study that observed maintainers,
   reviewers, or support engineers reading descriptions. Find studies of release-note content and use. Find studies of
   what makes a code review useful to the author, where they touch the description.
10. **Agent-authored descriptions.** Is there any existing skill, rule file, or system prompt that governs the
    *structure* of a commit or PR description for an LLM agent, as opposed to its wording or its prefix? If the category
    is thin, say so.

## Seed sources

Start from these. Add whatever the search turns up. Record every source with a URL.

Project guidance:

- Linux kernel, `Documentation/process/submitting-patches`, section "Describe your changes", and its rules for the
  `Fixes:` and `Link:` trailers: <https://www.kernel.org/doc/html/latest/process/submitting-patches.html>. The tip-tree
  handbook restates the commit-message rules with examples:
  <https://www.kernel.org/doc/html/latest/process/maintainer-tip.html>. The stable-kernel rules define what a
  backportable fix must say: <https://www.kernel.org/doc/html/latest/process/stable-kernel-rules.html>.
- Git, `Documentation/SubmittingPatches`: <https://git-scm.com/docs/SubmittingPatches>. Also `git interpret-trailers`:
  <https://git-scm.com/docs/git-interpret-trailers>.
- PostgreSQL, commit message guidance: <https://wiki.postgresql.org/wiki/Commit_Message_Guidance>, and the committing
  checklist: <https://wiki.postgresql.org/wiki/Committing_checklist>. Find Bruce Momjian's description of how the
  release notes are written from the commit log (the pgsql-hackers discussions, his blog, and the
  `src/tools/RELEASE_CHANGES` file) and the released notes themselves: <https://www.postgresql.org/docs/release/>.
- OpenStack, GitCommitMessages: <https://wiki.openstack.org/wiki/GitCommitMessages>.
- Google eng-practices, "How to write good CL descriptions":
  <https://google.github.io/eng-practices/review/developer/cl-descriptions.html>, and "Small CLs":
  <https://google.github.io/eng-practices/review/developer/small-cls.html>.
- Kubernetes, pull request guide: <https://www.kubernetes.dev/docs/guide/pull-requests/>; release-note block in the PR
  template: <https://www.kubernetes.dev/docs/guide/release-notes/> and
  <https://github.com/kubernetes/community/blob/master/contributors/guide/release-notes.md>; cherry-pick process:
  <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md>.
- Rust, contribution procedures and PR conventions: <https://rustc-dev-guide.rust-lang.org/contributing.html>;
  release-notes process: <https://forge.rust-lang.org/release/release-notes.html>.
- Go, contribution guide, commit messages section: <https://go.dev/doc/contribute>.
- Mozilla, how to submit a patch (commit message and bug reference):
  <https://firefox-source-docs.mozilla.org/contributing/how_to_submit_a_patch.html>; code review:
  <https://firefox-source-docs.mozilla.org/contributing/reviews.html>.
- LLVM developer policy, commit messages: <https://llvm.org/docs/DeveloperPolicy.html>.
- Chromium contributing guide: <https://chromium.googlesource.com/chromium/src/+/main/docs/contributing.md>.
- GitLab merge request workflow, commit message guidelines:
  <https://docs.gitlab.com/development/contributing/merge_request_workflow/>.
- Zulip commit discipline: <https://zulip.readthedocs.io/en/latest/contributing/commit-discipline.html>.
- Erlang/OTP, writing good commit messages: <https://github.com/erlang/otp/wiki/Writing-good-commit-messages>.
- Python developer guide, committing, and the NEWS entry rules:
  <https://devguide.python.org/core-developers/committing/>.
- Microsoft engineering fundamentals playbook, pull requests:
  <https://microsoft.github.io/code-with-engineering-playbook/code-reviews/pull-requests/>, and author guidance:
  <https://microsoft.github.io/code-with-engineering-playbook/code-reviews/process-guidance/author-guidance/>.

Essays:

- Chris Beams, "How to Write a Git Commit Message": <https://cbea.ms/git-commit/>.
- Peter Hutterer, "On commit messages": <https://who-t.blogspot.com/2009/12/on-commit-messages.html>.
- Tim Pope, "A Note About Git Commit Messages": <https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>.

Specifications and formats:

- Conventional Commits 1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>, and the Angular commit guidelines it
  descends from: <https://github.com/angular/angular/blob/main/CONTRIBUTING.md>.
- Keep a Changelog 1.1.0: <https://keepachangelog.com/en/1.1.0/>, and Common Changelog: <https://common-changelog.org/>.
- GNU Coding Standards, Change Logs chapter (gnu.org, `prep/standards`), and Debian policy on `debian/changelog`:
  <https://www.debian.org/doc/debian-policy/ch-source.html>.
- Gerrit `Change-Id`: <https://gerrit-review.googlesource.com/Documentation/user-changeid.html>.
- Semantic Versioning, for what "compatible" means to reader R4: <https://semver.org/>.
- CVE "Key Details Phrasing", as the operator-facing description of a defect:
  <https://cveproject.github.io/docs/content/key-details-phrasing.pdf>.

Platform behavior:

- GitHub pull request templates:
  <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository>;
  what squash and merge does to the commit message:
  <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges>;
  closing keywords:
  <https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue>.
- Release-note tooling that consumes descriptions: release-please <https://github.com/googleapis/release-please>,
  towncrier <https://towncrier.readthedocs.io/>, and the Kubernetes release-notes tool. Record what each reads and what
  it therefore forces the author to write.

Empirical literature:

- Tian et al., "What Makes a Good Commit Message?" (ICSE 2022): <https://arxiv.org/abs/2202.02974>.
- Later work that cites it and measured content or readers: Li and Ahmed, "Commit Message Matters" (ICSE 2023); studies
  of release-note production and use (Bi et al., TSE 2020; Abebe et al., EMSE 2016; Moreno et al. on ARENA); Bosu et
  al., "Characteristics of Useful Code Reviews" (MSR 2015); any observational study of developers reading commit
  histories or release notes. Find the URLs.

## Search scope

## 1. Project contribution guides

Beyond the seeds: Apache projects, Node.js, Django, Ruby on Rails, Swift, .NET runtime, Android (AOSP), Mesa, QEMU,
systemd, Debian and Fedora packaging guides, Homebrew. Prefer guides that say *why* a rule exists and which reader it
serves.

## 2. Release-note and changelog practice

Project release-note style guides (Kubernetes, Rust, Python "What's New", Django, PostgreSQL, Node.js), security
advisory conventions (GitHub Security Advisories, CVE, distribution security teams), and tools that generate notes from
descriptions.

## 3. Backport and maintenance-branch process

Kernel stable rules, PostgreSQL back-branch policy, Kubernetes cherry-pick guide, Python backport labels, Debian
stable-update rules, and any project that requires an affected-versions statement.

## 4. Platform and tool documentation

GitHub, GitLab, Gerrit, Phabricator (historical), Azure DevOps: what each does with the title and body on merge, which
fields it parses, and which templates it ships.

## 5. Research

Empirical software engineering on commit messages, PR descriptions, release notes, code-review usefulness, and software
archaeology (how developers use history). Include work on what reviewers read first if any exists.

## 6. Agent skills and rule files

Claude Code skills, Cursor and Continue rules, commitlint and gitlint presets, PR-description bots. Report honestly if
the category holds only prefix enforcement and wording tips.

## Freshness

Prefer sources updated in 2023 or later where the subject is platform behavior, tooling, or agent-authored text. Older
sources are expected for project guidance and essays; a 2008 essay that projects still link to is a strong source. Say
when a source's advice predates the workflow it is now applied to (for example, patch-series advice applied to squash
merges).

## What counts as evidence

Treat these as scoring signals, not hard filters:

- adopted by a large open-source project or a known engineering organization, and still linked from its contribution
  guide
- states a rationale and names the reader it serves, not only the rule
- ships with before-and-after examples of real messages
- measured rather than asserted: an observed reader, a coded corpus, a survey with a stated sample
- public discussion showing the rule being applied or disputed in review
- consumed by a tool, so the rule has a mechanical check

Prefer a studied claim over a widely repeated one, and say which is which.

## Exclusions

Exclude:

- wording-only guidance (see *Out of scope*)
- commit-message generation models, unless the paper measured what good messages contain
- listicles restating Chris Beams without a source or an example
- prefix-vocabulary debates (which types Conventional Commits should have) with no reader in view
- marketing pages for changelog SaaS products
- anonymous prompt lists with no evidence of use

## Required output for Pass 1

Produce a discovery report under 3000 words. Do not analyze every candidate deeply; the purpose is to build a strong
candidate pool for Pass 2.

## 1. Executive summary

Answer briefly:

- Does any single source cover all five readers, or is synthesis required?
- Which reader is best served by the existing literature, and which is worst served?
- Is there an existing agent skill for description *structure*, as opposed to prefix and wording?
- Which of the ten questions look answerable from existing sources, and which look under-served?
- Should Pass 2 concentrate on project guides, tooling behavior, research, or a combination?

## 2. Reader table

One row per reader (R1 to R5): the artifact they open, what they read first, which sources say so, and whether the claim
is measured or asserted. Where the sources are silent, say so and give your inference with the reasoning.

## 3. Candidate inventory

Produce a table with 20 to 30 candidates. For each:

- name
- URL
- category: project guide / essay / specification / platform doc / tool / research / agent skill
- author or organization
- workflow assumed: email patches / Gerrit / GitHub merge commits / GitHub squash / monorepo / unclear
- readers served: list of R1 to R5
- structural rules it contributes: one line
- evidence strength: strong / medium / weak, and whether its central claim is studied or asserted
- maintenance status: active / stale / unclear
- one line on why it is worth considering

## 4. Promising shortlist for Pass 2

Select 8 to 12 candidates. For each, in two to four sentences: why it is promising, which structural rules it may
contribute, which readers it serves, which workflow it assumes, and whether its rules are likely to transfer outside the
home project.

## 5. Obvious rejects

List 5 to 10 sources or categories that looked relevant but should be excluded, with a one-line reason each.

## 6. Gaps and questions for Pass 2

List the main uncertainties. Include at least these, and add your own:

- where sources contradict each other, and which reader's need would decide the contradiction
- which rules are specific to a workflow and would produce false positives elsewhere
- whether any source treats the changelog entry as the on-call reader's artifact, rather than the upgrading user's
- what evidence exists on what readers actually read first
- whether the squash-merge case (PR title seeds the subject) has any published guidance at all
- what is left that only a human can judge

## Baseline

Use the following only as context, and as a snapshot of what one team's practice has already produced. Do not treat it
as the target, and do not limit the search to sources that agree with it. Where a source contradicts it, that
contradiction is a finding worth reporting.

The baseline is the structural part of the *Commit messages*, *PR titles*, *PR descriptions*, and *Changelog and release
notes* modules of the companion skill `english-developer-style`, with the wording rules removed. Its weakest parts, and
the ones most in need of external evidence, are: the claim that the PR body has exactly three sections in the order why,
what, how to verify; the absence of any rule for the on-call reader (R3) beyond "name the symptom"; the absence of any
rule for the backporter (R5); and the claim that a commit body carries the *why* for `git blame`, which the baseline
asserts without a source.

---

**Commit messages.** Subject in the form `type(scope): summary`, at most 72 characters. The body, after a blank line,
explains why the change was needed and notes anything non-obvious: migration risk, performance trade-off, related
incident. Reference issues by ID. Do not paraphrase the diff.

**PR titles.** About 100 characters; below that ceiling accuracy wins over brevity, because the title is read in a list
and searched. Where a project squash-merges, the title seeds the commit subject rather than becoming it: the merging
maintainer edits the line and the platform may append or strip the number.

**PR descriptions.** Three short sections, in order: **Why** (the problem or constraint that forced the change),
**What** (the behavioral change, not the changed files), **How to verify** (commands, and what each one establishes).
Call out breaking changes, migrations, and follow-up work where there are any; an absent section is not a gap to fill. A
reviewer decides and does not re-investigate: carry what changes that decision (what was wrong, why this behavior is
right, what changed, how it was checked, what scope or risk is left). Ask of every paragraph which review decision
becomes harder if it disappears. Name what the tests establish rather than transcribing them; say which tests are new. A
rejected alternative a reviewer would propose goes in a collapsed block with a mechanism or a measurement. Related or
stacked pull requests are described as scope: where they overlap and whether one is a dependency. Quoted diagnostics are
literals, reproduced exactly.

Each artifact has a primary level of detail:

| Artifact | Its level |
| --- | --- |
| the diff | implementation detail |
| the tests | individual cases, fixtures, parameter matrices, failure output |
| the doc comment | the durable API contract |
| the commit message | why the change was needed, for whoever runs `git blame` years later |
| the changelog | the released, user-visible symptom |
| the PR | the problem, the decision, the scope, and a verification summary |

**Changelog and release notes.** Group under `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`, `Security` (Keep a
Changelog). One sentence per entry by default. Name the symptom a reader will search for, such as the exception class or
the error text, even at the cost of a second sentence. Link to the PR or commit. Breaking changes get their own block at
the top of the version.
