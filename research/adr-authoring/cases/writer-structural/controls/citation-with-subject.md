## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the packages under `internal/token/` free of imports of HTTP packages

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

The packages under `internal/token/` parse and verify tokens. The packages under `internal/http/` hold the HTTP server,
its middleware, and its handlers. `cmd/token-gate` builds the service from both.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It builds from the packages under
`internal/token/`. A Go binary links every package that its packages import, so an import of `net/http` or of a package
under `internal/http/` in a token package also links that package into `tokencheck`.

The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the packages under `internal/token/`, and CI
runs golangci-lint on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of `net/http` and of the packages under
`internal/http/`, so that `tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory below it, with every Go file in
  that directory, `_test.go` files included.
- **HTTP package**: `net/http`, every standard-library package whose import path starts with `net/http/`, such as
  `net/http/httptest`, and every package whose directory is `internal/http/` or a directory below it.
- **imports**: a Go file of the package names the other package in an import declaration. A package that a token
  package reaches only through a third package is not imported.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in `.github/workflows/ci.yml`
  on every pull request, fails the lint step when a token package imports `net/http` or a package under
  `internal/http/`.

### Implementation notes

Adds no requirement. Where a token package has to report why a token failed, return an error value defined in the
token package, and let `internal/http` map it to a status code. Fetch keys or other remote data outside
`internal/token/`, and pass the result to the token packages. Put `tokencheck` under `cmd/tokencheck`.

### Justification

`tokencheck` can build without the HTTP server only while no token package imports an HTTP package (R1). An invariant
over imports is checked by a linter that CI already runs on every pull request, so the rule holds before `tokencheck`
exists (R1).

### Alternatives considered

- **A1. Let a token package import `net/http` for its types and constants alone, such as `http.Header` or
  `http.StatusUnauthorized`.** Rejected by R1: the import links `net/http` into `tokencheck` as fully as any other use.

## Consequences

Negative:

- A token package cannot fetch keys over HTTP itself. Code outside `internal/token/` fetches them and passes them in
  (R1).
- A test of a token package cannot use `net/http/httptest` to serve keys or tokens (R1).

## Open points

- **O1.** Do the `_test.go` files of a token package count? R1 assumes that they do, as the term token package states.
  The answers: every `_test.go` file counts; or no `_test.go` file counts, so that a test may use `net/http/httptest`,
  since tests are not linked into `tokencheck`. @example-architect decides. Affects R1.
- **O2.** Does R1 cover a package that a token package reaches only through a third package? R1 assumes that it does
  not, as the term imports states, which matches what depguard checks. The answers: direct imports only; or every
  package in the import graph of a token package, with a CI step such as `go list -deps` on each token package as its
  check. @example-architect decides. Affects R1.
- **O3.** Which standard-library packages under `net/http/` count as HTTP packages? The term HTTP package assumes all of
  them. The answers: every package whose import path starts with `net/http/`; or only those that import `net/http`
  themselves, which leaves out `net/http/httptrace`. @example-architect decides. Affects R1.
````

### File: docs/adr/README.md

````markdown
# Reading the decision records

The records in this directory govern the code under the paths that the layers below map. Read the records that govern
a path before you change code under it.

## Layers

A rule names its layer in parentheses after its number, such as `R1` (`token`).

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies tokens | `internal/token/` |
| `http` | Runs the HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Holds the entry points of the binaries | `cmd/` |

A test file beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/`, `.github/`, `.golangci.yml`, `go.mod`, `go.sum`, and `AGENTS.md`. A path
leaves this list and joins a layer once a rule constrains it. A change that adds a file that neither the table nor this
list covers extends one of them in the same change.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read in a record

When you write code under a record, read its **Terms**, **Rules**, **Confirmation**, and **Implementation notes**.
Anything that no rule states is your choice.

## Trailers

Every change to a file under a path that a layer maps ends its commit message and its pull request description with
two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R1 to #<issue>
```

- `Implements` names the rules that the change brings, each with every case it describes.
- `Defers` names each rule that the change leaves out, or brings only in part, with the existing issue or pull request
  that brings the rest. Where no issue exists yet, leave the rule out of the trailers, and say in the description which
  rules wait for a change that has no issue.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- The trailers may name a rule of a `Proposed` record.
- In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
  them for the whole change.

## Checking a change

A reviewer checks a change against the records as
[Checking a change](<URL of the adr-authoring skill on GitHub, at the version the repository pins>) describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

The decision records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that
guide before you change such code. End the commit message and the pull request description of such a change with the
`Implements:` and `Defers:` trailers, as the guide describes.
````

### Message to the user

I wrote ADR-0012 as `Proposed`, with one rule: no package under `internal/token/` imports `net/http` or a package under `internal/http/`. Since the team agreed to a reading guide and to the trailers, I also added `docs/adr/README.md` and a paragraph in `AGENTS.md` that points agents to the guide.

Three open points block acceptance. @example-architect needs to answer them:

- **O1:** Do `_test.go` files count? The draft assumes yes, which means no test can use `net/http/httptest`.
- **O2:** Does R1 cover packages imported indirectly? The draft assumes direct imports only, which is what depguard checks.
- **O3:** Do all packages under `net/http/` count? The draft assumes yes.

Once they're answered and approved, set the status to `Accepted` and add a `#### Date` heading with the acceptance date after the status line.

Questions:

1. Which URL should the guide use for "Checking a change"? The repository doesn't use APM, so the link should go to the `adr-authoring` skill on GitHub at a pinned version. I left a visible placeholder in `docs/adr/README.md` because I don't know the URL or the version.
2. I couldn't see `.golangci.yml`. Do the `deny` list and the `files` setting of `token-no-http` match the terms in the record? Specifically: does it match `net/http/` subpackages by prefix, and does it include test files? If not, I'll narrow the entry under **Confirmation** to what the rule actually checks.
3. The guide's list of paths outside any layer only has the root files I know about. Are there other files at the root, such as a `README.md`, `Makefile`, or `Dockerfile`? They need a place in the guide.

The records 0001 to 0011 have no numbered rules, so a check against them reports them as unchecked. This change only touches `docs/adr/` and `AGENTS.md`, so its commit doesn't need the trailers.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose `alg` header is `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the packages under `internal/token/` free of imports of HTTP packages](0012-token-packages-without-http.md)
<!-- markdownlint-enable MD001 -->

## Context

The `alg` parameter in the JOSE header of a token names the algorithm that secures it. RFC 7518, section 3.6,
registers the value `none` for a token that carries no signature, so anyone can create a token with that value. RFC
7515, section 4.1.1, defines the `alg` value as a case-sensitive string.

Token verification sits in `internal/token/verify`. The HTTP server calls it for the token of each request before
policy evaluation, and the planned offline tool `tokencheck` will call it without the HTTP server. The security review
asked how the service handles a token whose `alg` value is `none`.

## Decision

We will refuse a token whose `alg` header is `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`, and token
verification will make the check.

### Terms

- **`alg` value**: the value of the `alg` parameter in the JOSE header of a token.
- **token verification**: the package `internal/token/verify`.

### Rules

#### Token verification

- **R1** (`token`). For a token whose `alg` value equals `none` in a case-insensitive comparison, token verification
  returns an error that carries the reason code `TOKEN_ALG_NONE`, also where the token fails another check of token
  verification.

#### The response

- **R2** (`http`). When token verification returns the reason code `TOKEN_ALG_NONE` for the token of a request, the
  HTTP server answers that request with HTTP status 401 and the reason code `TOKEN_ALG_NONE` in `<the response field
  that carries the reason code>`, and policy evaluation does not run for that request.

### Implementation notes

Adds no requirement. Read the `alg` value before any signature check, and return the error at once. Add tests in
`internal/token/verify` for the `alg` values `none` and `NONE`, and for an expired token whose `alg` value is `none`.
Add a test in `internal/http` that expects status 401 and `TOKEN_ALG_NONE`. Once the tests land, name them under
**Confirmation**.

### Justification

The check sits in token verification, so every caller of it refuses the token, `tokencheck` included, and not only the
HTTP server (R1). `TOKEN_ALG_NONE` takes the place of the reason code of any other failed check. A client or an operator
who reads the code then learns that the token carried no signature, whatever else is wrong with it (R1). A
case-insensitive comparison also refuses `None` and `NONE`, values that attacks on JWT libraries try (R1). Status 401
tells the client that the request carries no valid credential (R2).
R2 is a rule of its own, with the tag `http`, because the import rule of ADR-0012 R1 applies to token verification.

### Alternatives considered

- **A1. Refuse a token whose `alg` value is `none` in the HTTP middleware of `internal/http`.** Rejected by R1:
  `tokencheck`, which calls token verification without the HTTP server, would accept the token.

## Consequences

Negative:

- A token whose `alg` value is `none` and that fails another check, such as an expired one, gets the reason code
  `TOKEN_ALG_NONE` and not the reason code of the other check (R1).

## Open points

- **O1.** Does R1 compare the `alg` value case-insensitively? R1 assumes that it does. The answers: case-insensitively,
  so that `None` and `NONE` get `TOKEN_ALG_NONE`; or only the exact value `none`, as RFC 7515 compares it, so that other
  spellings get the reason code of an unsupported algorithm. @example-security-architect decides. Affects R1.
- **O2.** Which part of the response carries the reason code? The answers under consideration: a field of a JSON
  response body, a response header, or the `error_description` of a `WWW-Authenticate` header.
  @example-security-architect decides. Affects R2.
````

### Message to the user

I wrote ADR-0013 as `Proposed`, with two rules:

- **R1 (`token` layer):** `internal/token/verify` returns `TOKEN_ALG_NONE` for a token whose `alg` is `none`, even when the token also fails another check.
- **R2 (`http` layer):** the HTTP server answers that request with 401 and the reason code, and policy evaluation doesn't run.

Two open points block acceptance. @example-security-architect needs to answer them:

- **O1:** Should the `alg` comparison ignore case? R1 assumes it does.
- **O2:** Where does the response carry the reason code? I didn't invent a field. R2 has a visible placeholder until this is answered.

Once they're answered and approved, set the status to `Accepted` and add a `#### Date` heading with the acceptance date.

No test covers the check yet, so the record has no **Confirmation** section. When the tests land, add a **Confirmation** section that names them. That edit is allowed even after the record is accepted. The implementation notes list the cases worth testing. A change that only adds tests doesn't touch a rule, so it doesn't need trailers.

Questions:

1. Does the service already put reason codes in a set place in its responses? If so, that answers O2.
2. Does the check in `internal/token/verify` compare `alg` case-sensitively today? And does it return `TOKEN_ALG_NONE` for a token that is also expired? If the code differs from what you decide on O1 or R1, the change that fixes it should carry `Implements: ADR-0013 R1`.

The reading guide doesn't need changes, since it already maps both layers.
