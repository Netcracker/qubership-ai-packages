# House rules for the merge model

A line in `AGENTS.md` or `CLAUDE.md` is already in the agent's context, so it spares the skill the
reading of `git log` that SKILL.md §4 otherwise prescribes. The line has to carry two things: the
method the maintainers use, and what that method expects of the branch. A line that names the method
alone (`we use rebase and merge`) leaves the branch rules open, and the skill still has to work them
out.

The blocks below are written to be pasted as they are, under a `## Merging` heading or beside the
repository's other commit rules. Pick the one that matches the repository, and edit the details the
repository does differently.

## Every pull request is squashed, default setting

The commonest GitHub setup: squash is the only allowed method, and the repository keeps GitHub's
default squash message, so the body of the squash commit is the branch commit messages.

```markdown
Every pull request is squashed into one commit. The squash keeps the pull request title as the
subject and the branch commit messages as the body; the description itself is not copied. Write the
title as the commit subject, write the first commit with a full body (problem, symptom, approach,
issue number), and keep later commits short: each one lands as a bullet in the body.
```

## Every pull request is squashed, title and description

Squash is the only method, and the repository set the squash message to the pull request title and
description, so the description is the commit body.

```markdown
Every pull request is squashed into one commit whose subject is the pull request title and whose
body is the pull request description. Write the title as a commit subject and the description as a
commit body: problem, symptom, approach, issue number. Keep checklists, screenshots, and test
transcripts in comments, because everything in the description lands in git log.
```

## Every pull request is rebased

Rebase is the only method, so each branch commit lands on the default branch as it is.

```markdown
Every pull request is rebased onto the default branch: each commit lands as it is, with no merge
commit and no pull request number appended. Write every commit to stand alone in git log, with a
full body and the issue number, and squash fix-up commits (`Fix lint`, `Apply suggestion`) into the
commit they correct before the merge. The description stays on the platform and is never copied.
```

## Every pull request gets a merge commit

Merge commits are the only method. GitHub composes the merge commit from the repository setting;
name what it copies.

```markdown
Every pull request is merged with a merge commit that carries the pull request title and
description; the branch commits land behind it unchanged. Write every commit to stand alone in git
log, with a full body and the issue number, and write the description as a commit body, because
`git log --first-parent` shows it as the commit for the whole change.
```

Where the merge commit carries only the title, drop the clause about the description being a commit
body and say that the description is never copied.

## Squash for one commit, rebase for a tidy branch

Both methods are allowed and the maintainer picks one per pull request. This is the setup the
GitHub defaults produce when a repository turns merge commits off.

```markdown
Maintainers squash a single-commit pull request and rebase a multi-commit one, so every commit on
the branch may land on the default branch as it is. Write every commit to stand alone in git log,
with a full body and the issue number; squash fix-up commits before the merge; write the pull
request title as a commit subject. The description is never copied into git log under either
method.
```

## What the skill reads from the line

- The method, or the pair of methods, decides the model row in SKILL.md §4.
- `the description is not copied` or `the description is the commit body` decides whether the
  description is shaped as a commit body with verification compressed to one line.
- `every commit stands alone` and `squash fix-up commits` decide whether the branch is tidied before
  review.
- `the issue number` in a commit body is the reference the skill puts in every commit under rebase
  and merge, where the platform appends nothing.
