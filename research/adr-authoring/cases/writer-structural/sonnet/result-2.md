## Request 1

### File: docs/adr/0012-token-packages-free-of-http.md

````markdown
# Keep the token packages free of imports of `internal/http/` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1 and R2 and the check under **Confirmation**.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

`internal/token/` holds the packages that parse and verify a token, `internal/token/parse` and `internal/token/verify`.
`internal/http/` holds the HTTP server, its middleware, and its handlers. The planned command-line tool `tokencheck`
will verify tokens offline, and it has to build without the HTTP server. The depguard rule `token-no-http` in
`.golangci.yml` already reports both imports, and CI runs it through golangci-lint on every pull request.

## Decision

We will not let any package under `internal/token/` import a package under `internal/http/` or the standard package
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a subdirectory of it, with its `_test.go`
  files.
- **imports**: a package imports another package when a Go file of the first names the second in an import
  declaration. A package that a third package imports on its behalf is not imported by the first.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports `example/token-gate/internal/http` or a package whose import path starts
  with `example/token-gate/internal/http/`.
- **R2** (`token`). No token package imports `net/http` or a package whose import path starts with `net/http/`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports the import. golangci-lint runs it in
  `.github/workflows/ci.yml` on every pull request.
- **R2**: the same depguard rule reports the import.

### Justification

`tokencheck` has to build without the HTTP server, and verifying a token offline needs no HTTP code. A token package
that imports `internal/http/` would pull the server into that build (R1). A token package that imports `net/http` or one
of its subpackages would tie the token packages to the HTTP stack (R2).

### Alternatives considered

- **A1. Let a token package import `internal/http/` and build `tokencheck` with the HTTP server.** Rejected by R1:
  `tokencheck` has to build without the server.
- **A2. Import `net/http` in a token package only for its constants, such as status codes.** Rejected by R2: the rule
  covers every import of `net/http`, whatever the importing file takes from it.

## Consequences

Negative:

- A token package cannot use the constants of `net/http`, such as status codes. Code that maps a verification result to
  an HTTP response belongs outside `internal/token/` (R2).
- A token package can still reach the HTTP server or `net/http` through a package that it imports and that is not
  itself a token package, because **imports** counts only the import declarations of the token package. R1 and R2 do
  not report that path.

## Open points

- **O1.** Does R2 cover the packages under `net/http/`, such as `net/http/httptest`? R2 assumes it does. Decided by
  @example-architect. Affects R2. The depguard rule `token-no-http` has to match the answer.
- **O2.** Do R1 and R2 cover the `_test.go` files of the token packages? The term **token package** assumes they do.
  Decided by @example-architect. Affects R1 and R2. The depguard rule `token-no-http` has to match the answer.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code under the paths in the layer table. Read this guide before you change
that code.

## Layers

A rule in a record carries the tag of the layer whose code it constrains. A test beside its code belongs to the layer of
that code.

| Layer | Paths |
| --- | --- |
| `token` | `internal/token/` |
| `http` | `internal/http/` |
| `entrypoint` | `cmd/token-gate/` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `.github/`, `.golangci.yml`, `go.mod`, and `go.sum`. A change
that adds a file that neither the table nor this list covers extends one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not. Records `0001` to `0011` have
no numbered rules, so a check lists them as unchecked.

## What to read when you write code

In each binding record that governs the code you change, read **Terms**, **Rules**, **Confirmation**, and
**Implementation notes**. Anything that no rule states is your choice.

## Trailers

Every change to code under the paths of the layer table ends its commit message and its pull request description with
two trailers. `Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with the
issue or pull request that will bring it. A `Defers` target must exist.

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to #123
```

Cite a rule with its record, as `ADR-0012 R2`. A change that brings no rule and leaves none out carries neither
trailer. Where a rule waits for a change that has no issue yet, open the issue first.

## Checking a change

A reviewer, human or agent, checks a change against the rules by the procedure in
[Checking a change in the adr-authoring skill](<URL of the adr-authoring skill at the version this repository pins>).
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change that code. End the commit message and the pull request description of such a change with the
  `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I wrote ADR-0012 and added the reading guide. Your request already commits the team to the guide and the trailers, so I didn't ask first.

ADR-0012 has status `Proposed`. Two open points block `Accepted`, and both need an answer from @example-architect:

1. Does R2 cover subpackages of `net/http`, such as `net/http/httptest`? I assumed yes.
2. Do R1 and R2 cover the `_test.go` files of the token packages? I assumed yes.

Does the `token-no-http` rule in `.golangci.yml` match both answers? I couldn't see the file. Once the record is accepted, add the Date heading with the acceptance date.

The guide has one placeholder to fill before merge: the link under "Checking a change". Which GitHub URL and pinned version of the `adr-authoring` skill should it point to? I didn't guess one.

This change touches only `docs/adr/` and `AGENTS.md`, so it carries neither trailer. The guide lists records 0001 to 0011 as unchecked because they have no numbered rules.

## Request 2

### File: docs/adr/0013-refuse-token-algorithm-none.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of `internal/http/` and `net/http`](0012-token-packages-free-of-http.md):
  the import rules of R1 and R2 apply to `internal/token/verify`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation, and the check sits in `internal/token/verify`. A
token whose header names the algorithm `none` carries no signature to verify. The security review decided that the
service refuses such a token. `internal/token/verify` is a token package under the import rules of ADR-0012 R1 and R2,
and the HTTP server of `internal/http/` writes the response.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and
the check will sit in `internal/token/verify`.

### Rules

#### Refusal of the algorithm `none`

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE` for a token
  whose header names the algorithm `none`, in any letter case, also where the token fails another check.
- **R2** (`http`). The HTTP server answers a request with status 401 and the reason code `TOKEN_ALG_NONE` in
  `<location of the reason code in the response>`, where verification of the token of that request returns the error of
  R1.

### Implementation notes

Adds no requirement. A table-driven test in `internal/token/verify` can cover R1 with the header values `none`, `None`,
and `NONE`, and a handler test in `internal/http/` can cover R2.

### Justification

A verifier that follows the algorithm in the header would accept a token with the algorithm `none`, and anyone can forge
such a token (R1, R2). R1 and R2 are separate rules because the import rules of ADR-0012 apply to
`internal/token/verify`: it returns the error, and `internal/http/` sets the status.

### Alternatives considered

- **A1. Let `internal/token/verify` set the HTTP status itself.** The import rules of ADR-0012 R1 and R2 apply to that
  package, so R1 returns an error and R2 has the HTTP server set the status.

## Consequences

Negative:

- No test covers R1 or R2 yet, so a change that breaks either shows in no check until a test lands.

## Open points

- **O1.** Where does the response carry the reason code, for example in the body or in a header, and under which field
  name? Decided by @example-security-architect. Affects R2.
- **O2.** Does the rule match the algorithm name in any letter case? R1 assumes it does. Decided by
  @example-security-architect. Affects R1.
- **O3.** Does `TOKEN_ALG_NONE` win where the token also fails another check, such as expiry? R1 assumes it does.
  Decided by @example-security-architect. Affects R1.
````

### Message to the user

I wrote ADR-0013 with status `Proposed`. Three open points block `Accepted`, and all three need an answer from @example-security-architect:

1. Where does the response carry the reason code, and under which field name? R2 has a visible placeholder until this is answered.
2. Is `none` matched in any letter case? I assumed yes.
3. Does `TOKEN_ALG_NONE` win when the token also fails another check, such as expiry? I assumed yes.

I split the decision into two rules because of ADR-0012. `internal/token/verify` can't import `net/http`, so it can't set HTTP 401. R1 makes it return an error with the reason code, and R2 has `internal/http/` answer with 401. If you want one rule instead, ADR-0012 R2 has to change first.

No test covers the check yet, so the record has no **Confirmation** section and lists the missing test as a cost under Negative. Please open an issue for the test, say in `internal/token/verify`, and send me its number. The change that adds the test can then name ADR-0013 R1 and R2 under `Implements`, or under `Defers` with that issue as the target. I did not guess a number. I couldn't see the code, so I don't know whether the check and the 401 mapping already exist.

ADR-0012 stays as it is, because ADR-0013 neither replaces nor extends it. This change touches only `docs/adr/`, so it carries no trailers.
