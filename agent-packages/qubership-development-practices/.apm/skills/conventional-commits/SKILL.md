---
name: conventional-commits
description: Write focused Conventional Commit messages. Use when creating commits, preparing a branch for review, or proposing commit messages.
---

# Conventional commits

Use Conventional Commits for every commit the agent creates.

## Message format

Use this shape:

```text
type(scope): imperative summary

body explaining why, when useful
```

Rules:

- Pick the narrowest accurate type: `fix`, `feat`, `docs`, `test`,
  `refactor`, `perf`, `build`, `ci`, `chore`, `revert`.
- Add a scope when it helps reviewers locate the change:
  `fix(apm)`, `docs(readme)`, `ci(super-linter)`.
- Keep the subject imperative and lower-case after the colon unless a
  proper noun requires capitalization.
- Keep each commit focused on one reviewable purpose.
- Stage files explicitly by path. Do not use `git add .` unless the user
  explicitly asks for it.

## Before committing

1. Inspect `git status --short`.
2. Review the unstaged and staged diffs.
3. Split unrelated edits into separate commits.
4. Run the relevant validation from the `repo-quality-gate` skill.
5. Commit only when the staged diff matches the message.

## Breaking changes

For breaking changes, add `!` after the type or scope and explain the
migration in the body:

```text
feat(api)!: remove legacy request header

BREAKING CHANGE: clients must send X-Request-Id instead of X-Correlation-Id.
```
