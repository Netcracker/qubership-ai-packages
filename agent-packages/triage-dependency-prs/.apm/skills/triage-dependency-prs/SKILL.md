---
name: triage-dependency-prs
description: "Triage failing checks on dependency-update PRs (Renovate or Dependabot) and drive them back to green: classify each failure, fix the clear ones, ask about the rest. Use only when the user asks to triage, fix, or sweep failing checks on dependency-update PRs — pass a PR number for one PR, or none to process every open dependency-update PR with a failing check."
---

# Triage dependency-update PRs

Work out why checks are failing on dependency-update PRs and get them
back to green. When the user names a PR number, triage that PR; with no
number, process every open dependency-update PR that has a failing
check.

This covers Renovate (hosted and self-hosted, including fork mode) and
Dependabot. The bot determines how you push a fix and how you request a
rebase; step 3 covers the differences.

## Policy (read first)

- Cause is clear: fix it and push to the PR branch.
- Cause is unclear or ambiguous: ask, don't guess.
- Test is flaky: open an issue linking the CI failure, or fix it in a
  separate PR when the change is a line or two.
- Reproduce and confirm the fix locally before any push, under the same
  toolchain and command as CI. Don't push what you haven't verified.

## Step 1. Find the failing checks

Identify the dependency-update PRs:

- Hosted bots filter directly: `gh pr list --state open --app renovate`
  and `gh pr list --state open --app dependabot`.
- Self-hosted Renovate runs under its own app or account, so the
  `--app` slug differs. Fall back to the branch prefix or the shared
  label:

  ```sh
  gh pr list --state open \
    --json number,author,headRefName,labels,isCrossRepository
  ```

  A dependency-update PR has an author of `renovate[bot]` or
  `dependabot[bot]` (or your self-hosted bot account), a `renovate/` or
  `dependabot/` branch prefix, or a `dependencies` label.

For each PR:

- `gh pr checks <PR>` shows which checks are red and links to their runs.
- Read the real error in the failing run, not the stacktrace around it:

  ```sh
  gh run view <run-id> --log-failed
  ```

  Strip ANSI codes and look for the `What went wrong` / `FAILED` block,
  or the first non-zero exit.

## Step 2. Classify each failure

- **Infrastructure or runner flake**: `502`/`504`, `context deadline
  exceeded`, Docker Hub / ghcr.io / Actions-cache timeouts, network
  blips. Re-run the failed jobs with `gh run rerun <run-id> --failed`. A
  one-off network error is not worth an issue; a recurring one is
  probably an ongoing incident, so note it and come back later.
- **Real regression from the update**: the bump itself breaks the build
  or the compile (API incompatibility, stricter lint defaults, a major
  version). Fix it, verify locally, and push to the PR branch.
- **Pre-existing tech debt the PR surfaces**: the failure also exists on
  the default branch and shows up only because the PR touches these
  files (super-linter, for instance, lints the diff alone). It is not
  the bump's fault. Fix it in a separate PR against the default branch,
  not the bot branch.
- **Flaky test in the code**: the test is unstable, the default branch
  is reliably green, and the update touches neither the test nor its
  code path. Re-run, then open an issue (or fix it in a separate PR when
  it is a line or two).
- **Not a test**: PR-title lint, `renovate/artifacts`,
  `renovate/stability-days`, a Dependabot compatibility score. Usually
  out of scope or resolved by the bot. Note it.

The anchor for every class: does the same check pass on a fresh default
branch? If it passes there and fails here, find what the PR introduces
or drags into view.

## Step 3. Fix, verify, and push

Reproduce in an isolated `git worktree` so you don't disturb the current
branch, then confirm the fix removes the failure under the same JDK,
toolchain, and command as CI.

When the fix is directly tied to the update (adjusting call sites for a
changed API, removing deprecations, regenerating a lockfile), commit it
to the PR's own branch, where it belongs alongside the bump. `gh pr
checkout <PR>` checks the branch out and tracks the fork for a fork-mode
PR, so the same push works whether the branch lives in this repo or a
fork, for Renovate or Dependabot.

Two bot-specific points once you have pushed:

- **Renovate** keeps your commits unless a rebase is triggered, so don't
  tick the rebase checkbox or apply the rebase label afterwards; either
  one overwrites your work. Use the checkbox or label only when you want
  Renovate to redo the branch; it takes no comment commands.
- **Dependabot** stops updating the PR once you push your own commits and
  leaves a note saying so. When a rebase is all you need, comment
  `@dependabot rebase` or `@dependabot recreate` instead of pushing.

Commit with Conventional Commits; the body explains *why*. Check project
memory and `CLAUDE.md` for project-specific pitfalls before you push.

## Step 4. Report

A table: PR | update | what failed | class | action | status.

Below it, list the issues you opened and the PRs you created, each with
a link.
