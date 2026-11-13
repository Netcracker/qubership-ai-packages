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
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The packages under `internal/token/`,
`internal/token/parse` and `internal/token/verify`, parse and verify a token. The packages under `internal/http/` hold
the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. `tokencheck` has to build without the
HTTP server. A Go binary includes every package that its packages import, directly or through other packages. A token
package that imports `internal/http` or `net/http` therefore brings the HTTP server into `tokencheck`.

The depguard rule `token-no-http` in `.golangci.yml` checks both imports. CI runs golangci-lint with `.golangci.yml` on
every pull request.

## Decision

We will keep every token package free of imports of the HTTP packages and of `net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it, test packages
  included.
- **HTTP package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`. A package such as `example/token-gate/internal/httputil` is not an HTTP package.
- **imports**: a package imports another package when an import declaration in one of the `.go` files in its directory
  names that package's import path. `_test.go` files count (O2). A package that is reached only through the imports of
  another package is not imported (O1).

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.
- **R2** (`token`). No token package imports `net/http` or a package whose import path starts with `net/http/`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in `.github/workflows/ci.yml`
  on every pull request, reports an import of an HTTP package in a token package.
- **R2**: the same depguard rule reports an import of `net/http` in a token package.

### Implementation notes

Adds no requirement. Where a token package needs to report a failure that the server turns into an HTTP status, return
an error from the token package, such as a typed error that carries a reason code, and map it to a status in
`internal/http`. Put the entry point of `tokencheck` in `cmd/tokencheck`, beside `cmd/token-gate`.

### Justification

`tokencheck` verifies tokens offline with the token packages and has to build without the HTTP server. Any import of an
HTTP package or of `net/http` in a token package adds the server code to that build (R1, R2). Most packages under
`net/http/`, such as `net/http/httptest` and `net/http/httputil`, import `net/http` themselves. One prefix also matches
how depguard checks a denied package (R2).

### Alternatives considered

- **A1. Return `net/http` status codes, such as `http.StatusUnauthorized`, from a token package.** Rejected by R2: the
  constant brings `net/http` into every binary that uses the package.
- **A2. Copy the verification code that `tokencheck` needs into `cmd/tokencheck`.** Two copies of the verification
  code would drift apart, and a fix to one would miss the other.

## Consequences

Negative:

- A test of a token package cannot use `net/http/httptest`, for example to serve keys from a test server (R2, O2).
- A new token error that the server reports with its own status needs a change in `internal/http` as well (R1, R2).

## Open points

- **O1.** Do R1 and R2 also forbid a package that a token package reaches only through another package, such as a
  third-party library that imports `net/http`? The answers are: direct imports only, which depguard checks and which
  this record assumes; or direct and indirect imports, which need a further check, such as one over `go list -deps`.
  @example-architect decides. Affects R1 and R2.
- **O2.** Do R1 and R2 cover `_test.go` files? The answers are: yes, which this record assumes; or no, so that a test of
  a token package may use `net/http/httptest`. @example-architect decides. Affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. A record with numbered rules governs the
code in the layers that its rules name.

## Layers

Each rule names its layer in parentheses, such as `(token)`. A test beside its code belongs to the layer of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | Serves HTTP: the server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Builds the binaries | `cmd/` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `.github/`, `.golangci.yml`, `go.mod`, and `go.sum`.

A change that adds a file outside the layers and outside this list adds the file's path to one of them.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read before you change code

Before you change code in a layer, read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of
every accepted record with a rule in that layer. Anything that no rule states is your choice.

## Trailers

Every change to code in a layer ends its commit message and its pull request description with two trailers.
`Implements` names the rules that the change brings. `Defers` names each rule that the change leaves out, with the
issue or pull request that will bring it:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0013 R3 to #42
```

`Implements` claims every case of a rule. A change that brings only some cases of a rule names it under `Defers`. A
`Defers` target is an issue or a pull request that exists. A change that brings no rule and leaves none out, such as a
refactoring, carries neither trailer. In a pull request with several commits, each commit carries the trailers of its
own part, and the description carries them for the whole change.

## Checking a change

A reviewer checks a change against the rules as
[Checking a change](`<URL of the "Checking a change" section of adr-authoring SKILL.md at a pinned version>`)
describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code. End the commit message and the pull request description of such a change with the
  `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I've added ADR-0012 with the status `Proposed`. It has two rules: R1 forbids a token package from importing anything under `internal/http/`, and R2 forbids `net/http`. Both name the depguard rule `token-no-http` under **Confirmation**. The team agreed to a reading guide and to the trailers, so I've also added the guide at `docs/adr/README.md` and a bullet in `AGENTS.md` that points to it.

Some questions before the record can be accepted:

1. **O1, for @example-architect:** should R1 and R2 also forbid a package that a token package only reaches through another package, such as a third-party library that imports `net/http`? The record assumes direct imports only, which is what depguard checks.
2. **O2, for @example-architect:** do the rules cover `_test.go` files? The record assumes they do, so a token package's tests can't use `net/http/httptest`.
3. **Subpackages:** R2 also forbids every package under `net/http/`, because `net/http/httptest` and `net/http/httputil` import `net/http` themselves. Is that what the meeting meant?
4. **Depguard settings:** does `token-no-http` check `_test.go` files, and does it match `net/http/...` as a prefix? If not, **Confirmation** covers fewer cases than the rules, and those cases need judging by hand.
5. **Guide link:** the repository doesn't use APM, so the guide should link to the adr-authoring skill on GitHub at a version the repository pins. Which URL and version should it use? Until you tell me, the link is a visible placeholder.

Once both open points are settled and @example-architect signs off, set the status to `Accepted` and add a `#### Date` heading with the date of acceptance.

Records 0001 to 0011 have no numbered rules, so a check of a change lists them as unchecked.

This change only touches `docs/adr/` and `AGENTS.md`, and the guide puts neither in a layer, so its commit doesn't need the trailers.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose header names the algorithm `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 to R3.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of `internal/http` and `net/http`](0012-token-packages-without-http.md):
  R2 keeps `net/http` out of `internal/token/verify`, so `internal/http` turns the reason code into the status 401.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The algorithm `none` marks a token that carries
no signature (RFC 7518, section 3.6), so any client can write such a token with any claims.

The security review settled how token-gate handles such a token. `internal/token/verify` holds the check, and no test
covers it.

## Decision

We will refuse every `none` token with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and `internal/token/verify` will
hold the check.

### Terms

- **`none` token**: a token whose header names the algorithm `none` in any letter case, such as `none`, `None`, or
  `NONE` (O2).
- **refuses**: `internal/token/verify` refuses a token when it returns an error that carries a reason code and returns
  no verified token.

### Rules

#### `internal/token/verify`

- **R1** (`token`). `internal/token/verify` refuses every `none` token with the reason code `TOKEN_ALG_NONE`.
- **R2** (`token`). Where a `none` token also fails another check of `internal/token/verify`, `internal/token/verify`
  refuses the token with `TOKEN_ALG_NONE` as its only reason code.

#### The HTTP server

- **R3** (`http`). The HTTP server responds to a request whose token `internal/token/verify` refuses with
  `TOKEN_ALG_NONE` with the status 401 and with `TOKEN_ALG_NONE` in
  `<location of the reason code in the response>`. The HTTP server does not pass the request to policy evaluation.

### Implementation notes

Adds no requirement. Add a table test to `internal/token/verify` with the header values `none`, `None`, and `NONE`, and
with a `none` token that has also expired. Each case expects `TOKEN_ALG_NONE`. Add a handler test to `internal/http`
that sends a `none` token and expects the status 401 and the reason code. Once the tests merge, list them under
**Confirmation**.

### Justification

A `none` token carries no signature, so its claims prove nothing about who wrote it (R1). The check sits in
`internal/token/verify`, so every caller of the package refuses the token, including the planned `tokencheck` (R1). A
client that receives `TOKEN_ALG_NONE` learns the cause it has to fix, and fixing another failure, such as an expiry,
would not make the token valid (R2). A 401 response means that the request lacks valid credentials (RFC 9110, section
15.5.2), and a `none` token is not a valid credential (R3).

### Alternatives considered

- **A1. Check the algorithm only in the HTTP middleware in `internal/http`.** Rejected by R1: `tokencheck` and any other
  caller of `internal/token/verify` would accept a `none` token.
- **A2. Accept a `none` token behind a setting, for tests or for local development.** Rejected by R1: R1 makes no
  exception for any setting.
- **A3. Respond to a `none` token with the status 403.** Rejected by R3.

## Consequences

Negative:

- A client that sends `none` tokens, such as a test harness that skips signing, receives the status 401 (R3).

## Open points

- **O1.** Where does the response carry the reason code? The answers under consideration are a field of the JSON body
  and a response header. @example-security-architect decides. Affects R3.
- **O2.** Does a header value that differs from `none` only in letter case, such as `NONE`, make a `none` token? This
  record assumes it does. The other answer limits the term to `none` exactly and leaves other casings to the handling
  of unknown algorithms in `internal/token/verify`. @example-security-architect decides. Affects R1, R2, and R3.
- **O3.** Should `TOKEN_ALG_NONE` be the only reason code for a `none` token that also fails other checks? This record
  assumes it should. The other answer is that the existing order of checks in `internal/token/verify` decides the
  reason code, and R2 is removed. @example-security-architect decides. Affects R2.
````

### Message to the user

I've added ADR-0013 with the status `Proposed`. ADR-0012 R2 keeps `net/http` out of `internal/token/verify`, so the decision is split into three rules:

- R1: `internal/token/verify` refuses a `none` token with `TOKEN_ALG_NONE`.
- R2: `TOKEN_ALG_NONE` wins over other failures.
- R3: `internal/http` turns that refusal into a 401.

Questions for @example-security-architect. Each one blocks acceptance:

1. **O1:** where does the 401 response carry the reason code: a field of the JSON body, or a response header? R3 has a placeholder until we know.
2. **O2:** should `None` and `NONE` count as `none`? The record assumes any letter case counts.
3. **O3:** should `TOKEN_ALG_NONE` be the only reason code when a `none` token also fails another check, such as an expiry? The record assumes it should (R2).

No test covers the check yet, so the record has no **Confirmation** section. Once tests merge, they can be listed there, even after acceptance. I couldn't confirm whether `internal/http` already responds with 401 and the reason code.

I'd suggest opening an issue for the tests and for any missing part of R3. A change that leaves those parts out can then name them under `Defers:` with that issue. Until the record is accepted it binds no change, but a change may still name its rules in the trailers.

ADR-0012 stays as it is, and the reading guide already maps both layers that the rules name, so ADR-0013 is the only file this request changes.
