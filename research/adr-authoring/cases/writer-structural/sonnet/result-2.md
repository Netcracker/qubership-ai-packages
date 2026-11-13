## Request 1

### File: docs/adr/0012-token-packages-free-of-http.md

````markdown
# Keep the token packages free of imports of the HTTP server and of net/http

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The packages under `internal/token/` parse and verify a token. `internal/http/` holds the HTTP server, its middleware,
and its handlers. The team plans a command-line tool, `tokencheck`, that verifies tokens offline and has to build
without the HTTP server. A binary that imports a package also builds every package that package imports, so one import
of the HTTP server from a token package puts the server into `tokencheck`.

## Decision

We will keep every package under `internal/token/` free of imports of `internal/http` and of `net/http`.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`.
- **HTTP server package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **imports**: a package imports another package when a `.go` file in its directory, a `_test.go` file included, has an
  import declaration for it. A package that only a dependency imports is not imported (O1, O3).

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP server package or the package `net/http`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` fails the `golangci-lint` run on an import of either. CI
  runs it on every pull request.

### Justification

`tokencheck` has to build without the HTTP server, and a token package that imports `internal/http` makes it build the
server (R1). The meeting applied the same limit to `net/http`, so that the token packages depend on no HTTP stack (R1).

### Alternatives considered

- **A1. Let a token package import `internal/http`, for example to reuse a type of the server.** Rejected by R1: the
  package would pull the server into every binary that imports it, `tokencheck` included.
- **A2. Let a token package import `net/http`, for example for `http.Header`.** Rejected by R1: the package would link
  `net/http` into `tokencheck`.

## Consequences

Negative:

- A token package cannot use a type of `net/http`, such as `http.Header`. Code that needs one stays in `internal/http/`
  (R1).

## Open points

- **O1.** Do `_test.go` files of a token package count as imports? This record assumes that they do. @example-architect
  decides. Affects R1.
- **O2.** Does R1 reach the packages under `net/http/`, such as `net/http/httptest`? This record assumes that it names
  `net/http` only. The other answer is every package whose path starts with `net/http/`. @example-architect decides.
  Affects R1.
- **O3.** Does R1 reach a library that a token package imports and that imports `net/http` itself? This record assumes
  that it does not. The other answer is that no import path from a token package to `net/http` may exist.
  @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Each record in this directory states numbered rules. A change to code that a record governs is checked against those
rules.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/`, with the tests beside the code |
| `http` | HTTP server, middleware, and handlers | `internal/http/`, with the tests beside the code |
| `cmd` | Entry point of the service | `cmd/token-gate/` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `.github/workflows/`, `.golangci.yml`, `go.mod`, and
`go.sum`. A change that adds a file that neither the table nor this list covers extends one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not. Records 0001 to 0011 have no
numbered rules, so a trailer cannot name them.

## What to read before you change code

Read these parts of each record that governs the layer you change: **Terms**, **Rules**, **Confirmation**, and
**Implementation notes**. **Implementation notes** adds no requirement. Where no rule states a requirement, the choice
is yours.

## Trailers

A change to code under the paths in the layer table ends its commit message and its pull request description with two
trailers. `Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with the
issue or pull request that will bring it.

```text
Implements: ADR-<number> R<n>
Defers: ADR-<number> R<n> to #<issue or pull request number>
```

A `Defers` target is an issue or a pull request that exists. A change that brings no rule and leaves none out, such as
a refactoring, carries neither trailer. In a pull request with several commits, each commit carries the trailers of its
own part, and the description carries them for the whole change.

## Checking a change

[Checking a change](<URL of the adr-authoring skill at the pinned version>) describes how a reviewer or an agent checks
a change against the rules.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change that code. End the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that the guide describes.
````

### Message to the user

I wrote ADR-0012 with status `Proposed`, the reading guide `docs/adr/README.md`, and a bullet in `AGENTS.md` that points at the guide. I added the guide without asking first, because your request says the team agreed to keep it and to end every change with the trailers.

Questions:

1. What is the URL of the `adr-authoring` skill at the version you pin? The guide's "Checking a change" link holds a visible placeholder. Fill it in before the merge.
2. Is the list of paths with no layer right? I put `.golangci.yml`, `.github/workflows/`, `go.mod`, and `go.sum` there, because no rule constrains them. A later rule that constrains one of them moves it into a layer.
3. Does `token-no-human-readable-name`... correction: does the depguard rule `token-no-http` cover `_test.go` files and `net/http`? I could not read `.golangci.yml`. Confirmation says it fails on both imports.

The record stays `Proposed` until @example-architect settles three open points. O1 asks whether `_test.go` files count. O2 asks whether `net/http/...` packages such as `httptest` count. O3 asks whether a third-party library that imports `net/http` counts. Add the Date heading when the record is accepted.

The meeting gave one reason, that `tokencheck` has to build without the HTTP server. I attached it to both imports in the Justification. The two alternatives come from the text of R1, not from the meeting.

This change touches only `docs/adr/` and `AGENTS.md`, so it carries no `Implements` or `Defers` trailer. I did not check whether existing code already meets R1.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

````markdown
# Refuse a token that names the algorithm none with 401 and TOKEN_ALG_NONE

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of net/http](0012-token-packages-free-of-http.md):
  R1 keeps `internal/token/verify` free of imports of `internal/http` and `net/http`.
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` declares that it carries no signature. ADR-0012 R1 keeps the packages
under `internal/token/` free of imports of `net/http`, so `internal/token/verify` cannot write an HTTP response, and
the code in `internal/http/` writes it.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, and we will make that check in `internal/token/verify`.

### Terms

- **none-algorithm token**: a token whose header names the algorithm `none`. The name is compared exactly, so `None`
  and `NONE` are outside the term (O1).

### Rules

#### Refusing a none-algorithm token

- **R1** (`token`, `http`). The service answers a request whose token is a none-algorithm token with HTTP status 401
  and the reason code `TOKEN_ALG_NONE` in <location of the reason code in the response> (O2).

#### Where the check is made

- **R2** (`token`). The package `example/token-gate/internal/token/verify` decides that a token is a none-algorithm
  token, and no other package does.

### Implementation notes

Adds no requirement. Because of ADR-0012 R1, `internal/token/verify` can return an error that carries
`TOKEN_ALG_NONE`, and the code in `internal/http/` can map that error to status 401.

### Justification

A none-algorithm token carries no signature, so nothing in it can be verified (R1). Token verification lives in
`internal/token/verify`, so the check belongs there (R2).

## Consequences

Negative:

- No test covers R1 yet, so a change can break it without a failing check.

## Open points

- **O1.** Does R1 reach a token whose header names `None` or `NONE`? This record assumes that it does not, because the
  term compares the name exactly. The other answer is that the comparison ignores case. @example-security-architect
  decides. Affects R1 and R2.
- **O2.** Where does the response carry the reason code: in the response body, in a header, or elsewhere? The answer
  could follow the way the service reports other token refusals. @example-security-architect decides. Affects R1.
````

### Message to the user

I wrote ADR-0013 with status `Proposed`. It names @example-security-architect as owner and approver. The Date heading is added when the record is accepted. The guide and `AGENTS.md` from Request 1 need no change.

Two open points block acceptance:

1. O1: Does the algorithm name `none` also match `None` and `NONE`? I wrote the exact match you stated. This is a security question, so @example-security-architect should answer it.
2. O2: Where does the response carry the reason code `TOKEN_ALG_NONE`? R1 holds a visible placeholder. I did not invent a location.

R2 is my reading of "the check sits in `internal/token/verify`": that package decides, and no other package does. Because of ADR-0012 R1, R1 carries both the `token` and `http` layer tags: `verify` cannot write the 401, so code in `internal/http/` has to. Please confirm that reading.

No test covers R1 or R2, so **Confirmation** has no entries and the record's Negative consequences say so. I suggest an issue, type Task, titled "Test the refusal of a token that names the algorithm none". It would state that a token whose header names `none` must get status 401 and the reason code `TOKEN_ALG_NONE`, with a test in `internal/token/verify` and one in `internal/http`. Please open it and tell me the number. The change that adds the tests can then name it in its trailers. After the tests land, add their names to **Confirmation**.

The review gave no rejected alternatives, so I left out **Alternatives considered** instead of inventing them. The reason in the Justification, that a none-algorithm token carries no signature, is my wording, so please confirm it.

I did not check whether `verify` already refuses these tokens.
