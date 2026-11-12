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
- You may consult the other files below; they are in the repository as shown.

### `AGENTS.md`

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

## Decision records

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to a layer. Read that guide
before you change such code. A change to that code ends its commit message and its pull request description with the
`Implements:` and `Defers:` trailers the guide describes.
````

### `docs/adr/README.md`

````markdown
# Decision records

Each record in this directory states one decision, with numbered rules that code is checked against.

## Layers

| Layer | Paths |
| --- | --- |
| `verify` | `internal/verify/` |
| `http` | `internal/http/` |

`docs/adr/`, `.github/`, and `.golangci.yml` belong to no layer.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Writing code under a record

Before you change code under a layer, read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of
the records that bind it. Anything no rule states is the implementer's choice.

## Trailers

A change to code under a layer ends its commit message and its pull request description with two trailers, and leaves
out the one with nothing to list:

```text
Implements: ADR-0007 R4
Defers: ADR-0007 R5 to #12
```

`Implements` lists the rules the change brings in full. `Defers` lists each rule the change leaves, wholly or in part,
to a later change, with an issue or a pull request that exists.

## Checking a change

The procedure is the section "Checking a change" of the `adr-authoring` skill, in
`.agents/skills/adr-authoring/SKILL.md`.
````

### `docs/adr/0007-verify-tokens.md`

````markdown
# Verify every token in `Authorization` before policy evaluation

## Status

Accepted

### Date

2026-10-02

## Decision

We will verify the token of every request in `internal/verify` before policy evaluation.

### Terms

- **token**: the value after `Bearer ` in the `Authorization` header of a request.

### Rules

- **R4** (`verify`). A token whose `exp` is earlier than the time of the check is refused with HTTP 401 and the reason
  code `TOKEN_EXPIRED`.
- **R5** (`verify`). A token whose `exp` has not passed is refused with HTTP 401 and the reason code
  `TOKEN_KID_MISSING` when its header has no `kid`, and with HTTP 401 and the reason code `TOKEN_KID_UNKNOWN` when its
  `kid` names no loaded key.
````

## The changes

Change 1 adds a branch to `internal/verify`: a token whose header has no `kid` is now refused with HTTP 401 and
`TOKEN_KID_MISSING`, where it got HTTP 401 and `TOKEN_INVALID` before. A token whose `kid` names no loaded key still
gets HTTP 401 and `TOKEN_INVALID`. A token whose `exp` has passed still gets HTTP 401 and `TOKEN_EXPIRED`. One new test,
`TestVerifyRefusesMissingKid`, covers the new branch, and `go test ./...` passes.

Change 2 changes `.github/workflows/ci.yml` to cache Go modules between runs. Nothing else changes.
