# change-description-authoring

An APM package that governs **what a change description says, in what order, and for whom**: the
commit subject and body, the pull request or merge request title and description, and the changelog
or release-note entry.

The rules are organized by reader rather than by style guide. A change description is read by five
people at five moments, each holding one thing and one search string: the reviewing maintainer with
the diff, the archaeologist with a `git blame` line years later, the on-call engineer with a stack
trace, the upgrading user with the release notes, and the backporter with a maintenance branch. Every
rule names the reader whose question it answers, and the test for any sentence is which reader asks
the question it answers.

## What it covers

- The five readers, what each one holds, which artifact each one opens, and what each one asks.
- The slots of a commit body (problem, impact and trigger, change and approach, references) and of a
  pull request description (why, what, verification, scope, release note), with the question each
  slot answers and when it is skipped.
- What each paragraph of a pull request description must earn: the review decision that gets harder
  without it, the shortest chain that justifies that decision, the level of detail each artifact
  owns, and the verification section that names what the tests establish rather than transcribing
  them.
- Why the commit subject is change-first while the body is problem-first, and why the two do not
  conflict.
- The changelog entry as the artifact the on-call engineer greps as well as the one the upgrading
  user reads, and the order of its parts that serves both.
- The trailers and identifiers that make text searchable, each with the tool that consumes it and the
  reader it serves: `Fixes:`, closing keywords, `Backpatch-through:`, the diagnostic quoted as a
  literal, both versions of a regression.
- What a squash merge, a merge commit, and a rebase and merge each leave in the permanent history,
  how to read the merge model from `git log`, what to write where the maintainers may pick either,
  and the default when detection fails.
- Which prescriptions are house style gated on a workflow (a type prefix, a subject limit,
  `Signed-off-by:`, `Change-Id:`, Prow commands, news fragments) rather than reader-serving rules.
- When to write nothing, how far a rewrite may grow, and how to compare two versions of a description
  without being sold by the newer one.

## Contents

- `.apm/instructions/change-description-authoring.instructions.md`: the trigger merged into
  `AGENTS.md` / `CLAUDE.md` by `apm compile`.
- `.apm/skills/change-description-authoring/SKILL.md`: the on-demand rules, before/after examples for
  each artifact, and a review checklist. It carries no citations; the evidence stays in the research
  directory below.
- `.apm/skills/change-description-authoring/references/merge-model.md`: a paste-ready `AGENTS.md`
  block for each common merge setup. The skill does not read it; it is for whoever configures a
  repository.

## Telling the skill how the repository merges

Left to itself, the skill reads the merge model from `git log`. A line in `AGENTS.md` or `CLAUDE.md`
is already in the agent's context, so it saves the detection when it names both the method and what
the method expects of the branch. Three lines cover most open-source repositories; the reference file above has the rest,
including squash with "title and description" and the merge-commit setup.

Squash only, GitHub's default squash message:

```markdown
Every pull request is squashed into one commit. The squash keeps the pull request title as the
subject and the branch commit messages as the body; the description itself is not copied. Write the
title as the commit subject, write the first commit with a full body (problem, symptom, approach,
issue number), and keep later commits short: each one lands as a bullet in the body.
```

Rebase only:

```markdown
Every pull request is rebased onto the default branch: each commit lands as it is, with no merge
commit and no pull request number appended. Write every commit to stand alone in git log, with a
full body and the issue number, and squash fix-up commits (`Fix lint`, `Apply suggestion`) into the
commit they correct before the merge. The description stays on the platform and is never copied.
```

Squash for one commit, rebase for a tidy branch, the setup GitHub's defaults produce once merge
commits are turned off:

```markdown
Maintainers squash a single-commit pull request and rebase a multi-commit one, so every commit on
the branch may land on the default branch as it is. Write every commit to stand alone in git log,
with a full body and the issue number; squash fix-up commits before the merge; write the pull
request title as a commit subject. The description is never copied into git log under either
method.
```

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tense, mood, sentence
  length, and dialect, and keeps its own per-surface modules for commits, pull requests, and
  changelogs. This package decides what goes in which slot and for whom; that one writes the
  sentences. Install both.
- [`javadoc-authoring`](../javadoc-authoring/) and its siblings govern the doc comment, the artifact
  that carries the durable API contract; this package governs the artifacts that carry the reason
  the code changed.

## Research

The rules were synthesized from project guides (Linux kernel, Git, Google eng-practices, PostgreSQL,
Kubernetes, Zulip), specifications (Keep a Changelog, Common Changelog, Conventional Commits, CVE Key
Details Phrasing), platform documentation (GitHub, GitLab, `git interpret-trailers`), and four
empirical studies, then tested against real changes from five workflows. The evidence, the sources
with URLs, and the conflicts between them are in
[`research/change-description-authoring/`](../../research/change-description-authoring/README.md).

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/change-description-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/change-description-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.
