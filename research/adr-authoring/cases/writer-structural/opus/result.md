## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of `net/http` and `internal/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

- Architect, @example-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The packages under `internal/token/`,
`internal/token/parse` and `internal/token/verify`, parse and verify the token. The packages under `internal/http/` hold
the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It is built from the token packages, and
it has to build without the HTTP server. Go links every package that a package imports into the binary, so one import
of `net/http` or of `internal/http` in a token package puts the HTTP server into `tokencheck`.

The depguard rule `token-no-http` in `.golangci.yml` reports both kinds of import. CI runs golangci-lint with that file
on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of `net/http` and of the packages under
`internal/http/`, so that `tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or any directory under it, at any depth.
- **HTTP package**: `net/http`, any package whose import path starts with `net/http/`,
  `example/token-gate/internal/http`, and any package whose import path starts with `example/token-gate/internal/http/`.
- **imports**: a Go package imports another package when a `.go` file in its directory names that package in an
  `import` declaration. Files whose names end in `_test.go` count. A package that only a third package imports is not
  imported.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which the golangci-lint step of
  `.github/workflows/ci.yml` runs on every pull request, fails the step when a token package imports `net/http` or a
  package under `internal/http/`.

### Implementation notes

Adds no requirement. Where a token package needs to report why it refuses a token, return an error type of that package,
and let `internal/http` map the error to a status code. `tokencheck` can then map the same error to an exit status and a
message.

### Justification

`tokencheck` builds without the HTTP server only if no token package imports an HTTP package (R1). The term **HTTP
package** also covers the packages under `net/http/`, such as `net/http/httptest` and `net/http/httputil`, because they
import `net/http` themselves (R1). The check already runs in CI, so the rule needs no new tooling.

### Alternatives considered

- **A1. Let a token package import `net/http` for its types and constants only, such as `http.Header` or
  `http.StatusUnauthorized`.** Rejected by R1: the import links `net/http`, and the HTTP server with it, into
  `tokencheck`.

## Consequences

Negative:

- A token package cannot fetch verification keys over HTTP. Code that fetches keys lives outside the token packages
  and passes the keys in (R1).
- A test of a token package cannot use `net/http/httptest` (R1).

## Open points

- **O1.** Whether an import in a `_test.go` file counts under R1. One answer is that it counts, as **imports** assumes.
  The other is that it does not count, because Go does not link test files into `tokencheck`. @example-architect
  decides. Affects R1.
- **O2.** Whether R1 also covers an HTTP package that a token package reaches through a third package, such as a library
  that imports `net/http`. One answer is direct imports only, as **imports** assumes and as depguard checks. The other
  is every package in the build of a token package, checked in CI with `go list -deps ./internal/token/...`.
  @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. This guide maps the code to the layers that
rules name, and describes how a change declares the rules it brings.

## Layers

A rule names the layer it constrains in parentheses after its number, such as **R1** (`token`). A test beside its code
belongs to the layer of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies the token of a request | `internal/token/` |
| `http` | Serves HTTP: the server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Holds the entry points of the binaries | `cmd/` |
| `build` | Declares the module, the lint settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

These paths belong to no layer: `docs/` and `AGENTS.md`. A change that adds a file outside every path in this section
also adds the path to a layer or to this list.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Before you change code

Read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of every accepted record that has a rule
in a layer you change. Anything that no rule states is your choice. Where a rule cites a rule of another record, also
read the **Related ADRs** of that record: a line there names any later record that replaces the cited rule.

## Trailers

A change to a path in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-<NNNN> R<n>, R<n>; ADR-<NNNN> R<n>
Defers: ADR-<NNNN> R<n> to #<issue or pull request>
```

- `Implements` names each rule that the change brings in every case the rule describes.
- `Defers` names each rule that the change leaves out or brings only in part, with the existing issue or pull request
  that brings the rest. A rule with no such issue yet stays out of the trailers, and the pull request description names
  it.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.
- The trailers may name rules of `Proposed` records.

## Checking a change

A reviewer or an agent checks a change against the rules as
[Checking a change](<URL of the adr-authoring SKILL.md at a pinned commit>#checking-a-change) describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
before you change such code. End the commit message and the pull request description of such a change with the
`Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I've written ADR-0012 and the reading guide in `docs/adr/README.md`, and added a paragraph to `AGENTS.md` that points agents at the guide. These are docs-only changes, so the commit carries no trailers. A suggested subject: `docs(adr): add ADR-0012 and the reading guide`.

The record is `Proposed`. Two open points block acceptance, and @example-architect needs to answer both:

- **O1:** Do imports in `_test.go` files count? I assumed they do, so tests can't use `net/http/httptest`.
- **O2:** Does R1 cover only direct imports, or every package in a token package's build? I assumed direct imports only, which is what depguard checks. But `tokencheck` building without the server really depends on the full build. A library that imports `net/http` would pass depguard and still pull the server in.

When the record is accepted, add `#### Date` after the status line.

Questions:

1. What URL should the guide link to for "Checking a change"? The repository doesn't use APM, so it needs a link to the adr-authoring skill at a pinned commit. The guide has a visible placeholder there until you give me the URL.
2. Does `token-no-http` match by prefix, so it also catches `net/http/httptest`? Does it check test files? The Confirmation entry describes the rule from the meeting notes, not from `.golangci.yml`.
3. Alternative A1 (importing `net/http` only for its types) is my own example, not from the meeting. Should I keep it or replace it?
4. Are there any top-level paths besides the ones in the guide, such as a `Dockerfile`, `Makefile`, or `README.md`? Each one needs a layer or a place in the no-layer list.

## Request 2

### File: docs/adr/0013-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. A token whose header names the algorithm `none`
carries no signature, so its claims hold whatever the sender wrote. The check that finds such a token sits in
`internal/token/verify`, and `internal/http` writes the HTTP response.

## Decision

We will refuse every request whose token names the algorithm `none` in its header, with HTTP status 401 and the reason
code `TOKEN_ALG_NONE`.

### Terms

- **alg-none token**: a token whose header has the `alg` parameter with the exact string value `none`. A value that
  differs only in case, such as `None` or `NONE`, does not make an alg-none token.
- **refuses**: token-gate refuses a request when it responds to the request without passing it to policy evaluation.

### Rules

#### Tokens that name the algorithm `none`

- **R1** (`token`, `http`). token-gate refuses a request whose token is an alg-none token, with HTTP status 401 and the
  value `TOKEN_ALG_NONE` in `<reason code field>` of the response. `TOKEN_ALG_NONE` takes precedence over the reason
  code of any other check that the alg-none token fails, such as an expired token.

### Implementation notes

Adds no requirement. The check in `internal/token/verify` can return an error of that package, such as
`verify.ErrAlgNone`, and the middleware in `internal/http` can map it with `errors.Is` to the response that R1 names.
Run the check before any check of the claims or the signature. Add a test in `internal/token/verify` for an alg-none
token, and a test in `internal/http` that sends one and checks the status and the reason code. Name both under
**Confirmation** when they land.

### Justification

An alg-none token carries no signature, so accepting it would let any client send a token with the claims it chooses
(R1). With the precedence in R1, an alg-none token gets the same reason code whatever its claims hold, and the order of
the checks doesn't change it (R1).

### Alternatives considered

- **A1. Report an alg-none token with the reason code of an invalid signature.** Rejected by R1: the security review
  gave an alg-none token a reason code of its own.

## Consequences

Negative:

- An alg-none token that also fails another check, such as an expired one, gets `TOKEN_ALG_NONE` and not the reason code
  of that check (R1).

## Open points

- **O1.** Which field of the response carries the reason code in R1. `<reason code field>` stands for it. The answer is a
  field name, such as the field where the other refusals of token-gate carry their reason codes.
  @example-security-architect decides. Affects R1.
- **O2.** Whether an `alg` value that matches `none` only when case is ignored, such as `NONE`, makes an alg-none token.
  One answer is an exact match, as **alg-none token** assumes. The other refuses those tokens with `TOKEN_ALG_NONE` as
  well. @example-security-architect decides. Affects R1.
- **O3.** Whether `TOKEN_ALG_NONE` takes precedence over the reason code of every other check that an alg-none token
  fails, as R1 assumes, or whether the record should set an order between them. @example-security-architect decides.
  Affects R1.
````

### Message to the user

I've written ADR-0013. It's `Proposed`, and three open points block acceptance. @example-security-architect needs to answer them:

- **O1:** Which response field carries the reason code? R1 has a visible placeholder, `<reason code field>`, until you name the field.
- **O2:** Should `None` or `NONE` also get `TOKEN_ALG_NONE`? I assumed an exact match on `none`.
- **O3:** Should `TOKEN_ALG_NONE` win over every other reason code the same token would get, such as an expired token? I assumed it does.

When the record is accepted, add `#### Date` after the status line.

R1 is tagged with both the `token` and `http` layers. That's because `internal/token/verify` can't produce the 401 itself: ADR-0012 R1 keeps `net/http` out of the token packages. So verify returns an error, and `internal/http` turns it into the response.

Since no test covers the check yet, the record has no **Confirmation** section. Adding the Confirmation entry later is one of the edits an accepted record allows. I suggest an issue to track the tests:

- Type: Task
- Title: `Test the refusal of alg-none tokens in verify and the HTTP middleware`

Once the tests land, add them under Confirmation. Also, alternative A1 is my own example, not from the review: should I keep it?
