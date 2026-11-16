## Request 1

### File: docs/adr/0012-token-packages-free-of-http.md

````markdown
# Keep the token packages free of imports from the HTTP server and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

`internal/token/` holds the packages that parse and verify a token, and `internal/http/` holds the HTTP server. The team
plans a command-line tool, `tokencheck`, that verifies tokens offline and has to build without the HTTP server.

## Decision

We will keep every package under `internal/token/` from importing a package under `internal/http/` and from importing
`net/http`.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`.
- **http package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **imports**: a Go package imports another when any of its `.go` files, test files included, lists the other in an
  import declaration. O1 asks about the test files.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an http package.
- **R2** (`token`). No token package imports `net/http`.

### Confirmation

- **R1**: the `token-no-http` rule of depguard in `.golangci.yml` fails the golangci-lint step of
  `.github/workflows/ci.yml`, which runs on every pull request, when a token package imports an http package.
- **R2**: the same rule fails the same step when a token package imports `net/http`.

### Justification

`tokencheck` has to build without the HTTP server, and a token package that imports an http package (R1) or `net/http`
(R2) brings that code into the build.

### Alternatives considered

- **A1. Let a token package take its input as a `net/http` type, such as `http.Header`.** Rejected by R2: `tokencheck`
  would then build with `net/http`.

## Consequences

Negative:

- Code that reads a token from an HTTP request must live outside `internal/token/` (R1, R2).

## Open points

- **O1.** Do R1 and R2 cover the `_test.go` files of a token package? The text assumes they do. @example-architect
  decides. Affects R1 and R2.
- **O2.** Do R1 and R2 cover the subpackages of `net/http`, such as `net/http/httptest`, and imports that reach
  `net/http` through a third-party library? The text assumes they do not. @example-architect decides. Affects R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory are numbered, and each one holds numbered rules. A change to code under the paths in
**Layers** is checked against the rules of the records that bind it.

## Layers

Each rule of a record names the layer of the code it constrains.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |
| `http` | HTTP server, middleware, and handlers | `internal/http/` |
| `cmd` | Entry points of the service and its tools | `cmd/` |
| `build` | Module, lint, and CI configuration | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/` |

A test beside its code belongs to the layer of that code. `docs/adr/` and `AGENTS.md` belong to no layer. A change that
adds a file covered by neither the layers nor this paragraph extends one of them.

## Which records bind

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not.

## What to read before you change code

Read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each binding record that governs the
code you change. Where a rule cites a rule of another record, read the **Related ADRs** of that record too, because a
line there names any later record that replaces the cited rule. Where no rule states a requirement, the choice is yours.

## Trailers

The commit message and the pull request description of every change to code under the paths above end with two
trailers. `Implements` lists the rules the change brings. `Defers` lists each rule the change leaves out, with the issue
or pull request that will bring it.

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R2 to #<issue or pull request number>
```

`Implements` claims every case of a rule. A change that brings only some cases of a rule lists it under `Defers`. A
`Defers` target is an issue or a pull request that exists. A change that brings no rule and leaves none out, such as a
refactoring, carries neither trailer. In a pull request with several commits, each commit carries the trailers of its
own part, and the description carries them for the whole change.

## Checking a change

[Checking a change](<URL of the adr-authoring SKILL.md at the pinned version>) in the `adr-authoring` skill describes how
a reviewer reaches a verdict on each rule.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers it describes.
````

### Message to the user

I wrote ADR-0012 as `Proposed`, with no Date heading. You didn't say the team signed off, and the record has two open points. Before it can be `Accepted`:

- **O1:** Do the rules cover `_test.go` files of the token packages? I assumed yes.
- **O2:** Do they cover subpackages of `net/http`, such as `net/http/httptest`, and imports that reach `net/http` through a third-party library? I assumed no.

Question: have @example-architect and the team signed off, and what are the answers to O1 and O2? If so, I'll set the status to `Accepted` and add the Date heading with the acceptance date.

The reading guide is `docs/adr/README.md`. You agreed to the trailer commitment, so I added it without asking. I also added a paragraph to `AGENTS.md`, because an agent that writes code never loads the skill and reads only that file.

- **Guide link:** Question: what is the URL of the `adr-authoring` skill, and which version does the repository pin? The guide has a visible placeholder for that link, because the repository doesn't commit deployed skill files. I did not guess a URL.
- **Layers:** I mapped the layers from the paths you gave. `build` covers `go.mod`, `go.sum`, `.golangci.yml`, and `.github/workflows/`. Tell me if you want them split differently.
- **Existing records:** ADR-0001 to ADR-0011 have no numbered rules. A checker reports them as unchecked, and I left them unchanged.
- **Trailers:** This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer. It carries neither trailer.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-alg-none.md

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

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The header of a token names the algorithm that
signed it, and the name `none` stands for no signature. The security review found that no record says what the service
does with such a token.

## Decision

We will refuse a token whose header names the algorithm `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and
`internal/token/verify` will make the check.

### Terms

- **none token**: a token whose header has the field `alg` with the value `none` in any letter case. O2 asks about the
  letter case.

### Rules

#### Refusal of a none token

- **R1** (`token`). `internal/token/verify` refuses a none token with the reason code `TOKEN_ALG_NONE`, also where it
  would refuse that token for another reason. O3 asks about the other reasons.
- **R2** (`http`). Where `internal/token/verify` refuses the token of a request with `TOKEN_ALG_NONE`, the HTTP server
  answers that request with status 401 and the code `TOKEN_ALG_NONE` in <response field that carries the reason code>.
  O1 asks for the field.

### Justification

A none token carries no signature, so accepting one would let any caller present a token it wrote itself (R1). Status
401 is the status for a request that fails authentication (R2).

### Alternatives considered

- **A1. Accept a none token where a setting allows it.** Rejected by R1: R1 has no exception, so no setting turns the
  refusal off.

## Consequences

Negative:

- A caller that sends a none token, such as a test client that skips signing, receives status 401 (R2).

## Open points

- **O1.** Which field of the response carries the reason code: a body field, a header, or both? @example-security-architect
  decides. Affects R2.
- **O2.** Does the match on `none` ignore letter case, so that `None` and `NONE` are refused too? The text assumes it
  does. @example-security-architect decides. Affects R1 and R2.
- **O3.** Does `TOKEN_ALG_NONE` win over the reason codes of other failures, such as an expired token or a malformed
  token? The text assumes it does. @example-security-architect decides. Affects R1 and R2.
````

### Message to the user

I wrote ADR-0013 as `Proposed`, with no Date heading. You didn't say the team signed off, and the record has three open points. Before it can be `Accepted`:

- **O1:** Which response field carries the reason code `TOKEN_ALG_NONE`: a body field, a header, or both? R2 holds a visible placeholder for it, because you didn't give a value and I did not invent one.
- **O2:** Does the match on `none` ignore letter case? I assumed it does, so `None` and `NONE` are refused too.
- **O3:** Does `TOKEN_ALG_NONE` win over the reason codes of other failures, such as an expired token? I assumed it does.

Question: have @example-security-architect and the team signed off, and what are the answers to O1 to O3? If so, I'll fill in the placeholder, set the status to `Accepted`, and add the Date heading with the acceptance date.

- **Rule split:** I split the behavior into R1 (the check in `internal/token/verify`, layer `token`) and R2 (the HTTP 401 answer, layer `http`). I couldn't read the code, so I assumed the HTTP server produces the 401. Tell me if the verify package does.
- **Confirmation:** No test covers the rules, so the record has no **Confirmation** section. Propose a test in `internal/token/verify` for R1 and a handler test in `internal/http` for R2. Once they land, the record gains the entries, and the accepted record takes that edit.
- **Trailers:** The test change would carry `Implements: ADR-0013 R1, R2`, or list a rule under `Defers` with an existing issue if it covers only part of one. This record's own change touches only `docs/adr/`, so it carries neither trailer.
- **Binding:** Under the guide in `docs/adr/README.md`, the record binds no change until its status is `Accepted`.
