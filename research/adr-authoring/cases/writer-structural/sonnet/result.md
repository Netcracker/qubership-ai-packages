## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of `internal/http` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

- Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The packages under `internal/token/` parse and verify a token. The planned command-line tool `tokencheck` verifies
tokens offline, so it builds on those packages, and it has to build without the HTTP server. The HTTP server, its
middleware, and its handlers are under `internal/http/`. The depguard rule `token-no-http` in `.golangci.yml` already
checks the imports of the token packages, and CI already runs it.

## Decision

We will keep every package under `internal/token/` free of imports of `internal/http` and of `net/http`, and we will
check this with the depguard rule `token-no-http`.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`.
- **import**: an import declaration in a Go source file of the importing package, test files included. An import of a
  package that the imported package declares is not counted.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package has an import of `net/http`, or of a package whose import path is
  `example/token-gate/internal/http` or starts with `example/token-gate/internal/http/`.

#### Enforcement

- **R2** (`build`). The depguard rule `token-no-http` in `.golangci.yml` reports every import that R1 forbids, so that
  the golangci-lint step fails, and `.github/workflows/ci.yml` runs that step on every pull request.

### Confirmation

- **R1**: the depguard rule `token-no-http`, which `golangci-lint run` applies on every pull request.

### Implementation notes

Adds no requirement. Code that needs an HTTP type, such as the mapping of a verification failure to a status code,
belongs in `internal/http`, which can call the token packages.

### Justification

A token package that imports `internal/http` brings the HTTP server into every binary that links it, and `tokencheck`
has to build without that server (R1). The ban covers `net/http` too, so that `tokencheck` does not take on the standard
library's HTTP code (R1). A lint rule that runs on every pull request reports a forbidden import before the change
merges (R2).

### Alternatives considered

- **A1. Forbid only imports of `internal/http` and allow `net/http` in a token package.** Rejected by R1: the architecture
  meeting banned both.

## Consequences

Negative:

- A token package can still reach `net/http` through a library it imports, because only the imports of the token
  package itself count (R1).
- A token package cannot use `net/http` for any purpose, including its status code constants (R1).

## Open points

- **O1.** Do test files of a token package fall under R1? The record assumes they do, and the **import** term says so.
  The `files` settings of `token-no-http` in `.golangci.yml` decide whether R2 holds under that reading.
  @example-architect decides between "test files included" and "test files exempt". Affects R1 and R2.
- **O2.** Does R1 cover the subpackages of `net/http`, such as `net/http/httptest`? The record assumes it names only
  `net/http` itself, as the meeting wrote it. @example-architect decides between "`net/http` only" and "`net/http` and
  every package under it". Affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code under the paths mapped in **Layers**. Read the rules of each record that
applies before you change that code.

## Layers

Each rule of a record carries the layer of the code it constrains.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parse and verify a token | `internal/token/`, tests beside the code included |
| `http` | HTTP server, middleware, and handlers | `internal/http/`, tests beside the code included |
| `cmd` | Service entry point | `cmd/token-gate/` |
| `build` | Dependencies, lint settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/ci.yml` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`.

A change that adds a file covered by neither the layers nor that list extends one of them in the same change.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
binds nothing.

## What to read in a record

When you write code under a record, read its **Terms**, **Rules**, **Confirmation**, and **Implementation notes**.
Anything that no rule states is your choice.

Where a rule cites a rule of another record, read the **Related ADRs** of that record as well. A line there names any
later record that replaces the cited rule.

## Trailers

A change to code in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0092 R6, R8; ADR-0091 R54
Defers: ADR-0091 R38 to #208; ADR-0095 R2 to #215
```

- `Implements` lists the rules the change brings. It claims every case of each rule it names.
- `Defers` lists each rule the change leaves out, with the existing issue or pull request that will bring it. A change
  that brings only some cases of a rule names the rule under `Defers`, with the change that brings the rest.
- Where no issue exists yet for a deferred rule, open one first and name it. A guessed number stays in the merged
  commit.
- A change that brings no rule and leaves none out, such as a refactoring that keeps every rule met, carries neither
  trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

The procedure for checking a change against the rules is in the section "Checking a change" of the `adr-authoring`
skill: TBD, the URL of the skill at the version this repository pins.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
before you change such code. End the commit message and the pull request description with the `Implements:` and
`Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012, a reading guide at `docs/adr/README.md`, and a paragraph in `AGENTS.md`. Your request already agrees to the guide and the trailers, so I did not ask first.

- **Status:** ADR-0012 is `Proposed`, and it has no Date heading. Nothing you gave me says the team signed off. Set `Accepted` and add the Date on acceptance. Open points O1 and O2 must be settled first.
- **O1, test files:** I assumed R1 covers test files. I could not see the `files` settings of `token-no-http` in `.golangci.yml`. If that rule skips tests, R2 does not hold as written. Should test files be covered?
- **O2, `net/http` subpackages:** I assumed R1 names only `net/http` itself, as the meeting wrote it. Should it also cover `net/http/httptest` and the other packages under it?
- **Direct imports only:** R1 counts only direct imports, because depguard checks only those. A library can still bring `net/http` into a token package, and the record lists this as a cost.
- **Link in the guide:** I wrote `TBD` where the guide links to "Checking a change". Which URL and pinned version of the `adr-authoring` skill should it use?
- **Invented text:** The meeting notes gave no alternative or justification. A1 and the Justification paragraph are mine, so please confirm or correct them.
- **No trailers owed:** This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer, so its commit needs no `Implements:` or `Defers:` trailer.

## Request 2

### File: docs/adr/0013-refuse-unsigned-tokens.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1, R2, and O1.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of `internal/http` and `net/http`](0012-token-packages-without-http.md):
  the import rule of R1 that the Implementation notes cite.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation, and `internal/token/verify` verifies the token.
The header of a token names the algorithm of its signature. The value `none` declares the token unsigned, so its claims
prove nothing about who sent it.

## Decision

We will refuse every token whose header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, and the check will sit in `internal/token/verify`.

### Terms

- **none token**: a token whose header has the member `alg` with the string value `none`, compared exactly. O1 asks
  whether other letter cases count.

### Rules

#### Tokens that name the algorithm `none`

- **R1** (`token`). `internal/token/verify` refuses a none token with the reason code `TOKEN_ALG_NONE`, whatever the
  payload and the signature of the token contain.
- **R2** (`http`). The service answers a request with HTTP status 401 where `internal/token/verify` refused the token of
  that request with the reason code `TOKEN_ALG_NONE`.

### Implementation notes

Adds no requirement. The import rule of ADR-0012 R1 keeps `net/http` out of `internal/token/verify`, so the package
returns the reason code and `internal/http` maps it to status 401. A table test in `internal/token/verify` can cover R1,
and a handler test in `internal/http` can cover R2.

### Justification

A none token declares that it is unsigned, so accepting it would accept claims that nobody vouches for (R1). Status 401
tells the client that its credentials were refused (R2).

### Alternatives considered

- **A1. Refuse a none token with a generic invalid-token reason code.** Rejected by R1: the reason code
  `TOKEN_ALG_NONE` is fixed for this case.

## Consequences

Negative:

- A token whose `alg` value is `None` or `NONE` is outside R1 until O1 settles the letter case.

## Open points

- **O1.** Does a none token include a token whose `alg` value is `None`, `NONE`, or another letter case of `none`? The
  record assumes the exact string `none`, as the review wrote it. @example-security-architect decides between "exact
  string" and "any letter case". Affects R1 and R2.
````

### Message to the user

I added ADR-0013 as `Proposed`, with no Date heading. Nothing you gave me says the security review signed off. Set `Accepted` and add the Date once @example-security-architect approves and O1 is settled.

- **O1, letter case of `none`:** I assumed the exact string `none`, as the review wrote it. This is a security question, because some libraries accept `None` or `NONE`. Should those count as none tokens?
- **Layer tags:** I could not read the code, so I assumed `internal/token/verify` returns the reason code and the middleware in `internal/http` writes the 401. That is why R1 is tagged `token` and R2 is tagged `http`. Which component writes the status? If it is `verify`, merge R1 and R2 and tag the rule `token`.
- **Reason code:** The record does not say where the response carries `TOKEN_ALG_NONE`, such as a body field or a header. It relies on the service's existing convention for reason codes. If the review decided the location, tell me and I will add it to R2.
- **ADR-0012:** The Implementation notes cite ADR-0012 R1, so ADR-0013 links ADR-0012 under Related ADRs. ADR-0012 itself is unchanged.
- **Tests:** No test covers this yet, so the record has no Confirmation section. I suggest a table test in `internal/token/verify` for R1 and a handler test in `internal/http` for R2. When those land, add their names to Confirmation. The change that adds them should name R1 and R2 under `Implements:`.
- **Invented text:** A1 and the Justification are mine, not from the review. Please confirm or correct them.
