# Task

You are the agent that wrote the two changes below, in the repository below. For each change, write its commit message
and its pull request description, under a heading `## Change 1` or `## Change 2`, as if the other change did not
exist. Under each, give the commit message under `### Commit message` and the description under `### Pull request
description`, each in a fence of four backticks.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- Pull requests merge with rebase and merge.
- Issue #12 is open and tracks the rest of ADR-0007 R5.
- `AGENTS.md` at the repository root holds your instructions for this repository. Its content is below.

### `AGENTS.md`

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
````

## The changes

Change 1 adds a branch to `internal/verify`: a token whose header has no `kid` is now refused with HTTP 401 and
`TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before. A token whose `kid` names no loaded key still
gets HTTP 401 and `TOKEN_INVALID`. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`. One new test,
`TestVerifyRefusesMissingKid`, covers the new branch, and `go test ./...` passes.

Change 2 changes `.github/workflows/ci.yml` to cache Go modules between runs. Nothing else changes.
