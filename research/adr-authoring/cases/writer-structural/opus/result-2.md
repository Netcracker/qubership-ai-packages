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

token-gate checks the token of each request before policy evaluation. The packages `internal/token/parse` and
`internal/token/verify` parse and verify a token, and `internal/http` holds the HTTP server, its middleware, and its
handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline with the token packages. It has to build
without the HTTP server. Go compiles every package that a package imports into the binary's build, together with the
imports of those packages.

## Decision

We will keep every token package free of imports of `net/http` and of `example/token-gate/internal/http`, so that
`tokencheck` builds without the HTTP server.

### Terms

- **token package**: a Go package whose directory is `internal/token` or a directory under it, including the test
  packages built from its `_test.go` files.
- **imports**: a Go file of a package names another package in an import declaration. A package that the named package
  imports in turn does not count.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports `net/http`, a package whose path starts with `net/http/`,
  `example/token-gate/internal/http`, or a package whose path starts with `example/token-gate/internal/http/`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` fails when a token package imports one of these packages.
  golangci-lint runs it in `.github/workflows/ci.yml` on every pull request.

### Justification

`tokencheck` imports the token packages. An import of `net/http` or of `internal/http` in any of them would make the HTTP
stack a build dependency of `tokencheck` (R1). `internal/http` imports `net/http`, so `net/http` alone does not cover it,
and the rule names both (R1).

### Alternatives considered

- **A1. Let a token package import `net/http` for its types only, such as `http.Header` or `*http.Request`.** Rejected by
  R1: the import makes `net/http` a build dependency of `tokencheck`, whichever names the package uses.

## Consequences

Negative:

- A function in a token package cannot take an `*http.Request` or return an HTTP status code. `internal/http` reads the
  token from the request and maps each error from the token packages to a status code (R1).

## Open points

- **O1.** Do the test files of a token package fall under R1? The record assumes that they do, so a test in
  `internal/token/verify` cannot use `net/http/httptest`. The other answer exempts the `_test.go` files, since they are
  not part of the `tokencheck` build. @example-architect decides. Affects R1 and the term **token package**.
- **O2.** Does R1 also cover a package that a token package reaches through another package, such as a logging package
  that imports `net/http`? The record assumes direct imports only, which is what depguard checks. The other answer
  covers every package in the build of a token package, and needs a check other than depguard, such as one built on
  `go list -deps`. @example-architect decides. Affects R1 and the term **imports**.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records of token-gate. From ADR-0012 on, a record states its
requirements as numbered rules, and a change to the code a rule governs can be checked against it. ADR-0001 to ADR-0011
have no numbered rules.

## Layers

Each rule names the layer it constrains, such as `(token)`. A test beside its code belongs to the layer of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the service and of its tools | `cmd/` |

These paths belong to no layer, because no rule constrains them: `docs/`, `AGENTS.md`, `go.mod`, `go.sum`,
`.golangci.yml`, and `.github/`. A change that adds a file that neither the table nor this list covers extends one of
them. When a rule starts to constrain one of these paths, the path moves into a layer.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read before you change code

Before you change code under a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
binding record with a rule in that layer. Anything no rule states is your choice. Where a rule cites a rule of another
record, also read that record's **Related ADRs**: a line there names any later record that replaces the cited rule.

## Trailers

A change to code under a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-<NNNN> R<n> to #<issue>
```

`Implements` names the rules the change brings, each with every case it covers. `Defers` names each rule the change
leaves out, with the existing issue or pull request that will bring it. A change that brings no rule and leaves none
out, such as a refactoring, carries neither trailer. In a pull request with several commits, each commit carries the
trailers of its own part, and the description carries them for the whole change.

## Checking a change

A change is checked against the records as
[Checking a change](<link to the adr-authoring skill on GitHub at a pinned version>#checking-a-change) describes.
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

I added ADR-0012 with status `Proposed`. It also adds the reading guide in `docs/adr/README.md` and a bullet in `AGENTS.md` that points agents at the guide and the trailers. From now on, every change to code under `internal/token/`, `internal/http/`, or `cmd/` owes the `Implements:` and `Defers:` trailers. This change only touches `docs/` and `AGENTS.md`, so it carries neither trailer.

Two open points keep ADR-0012 at `Proposed`. @example-architect needs to settle them before it can be accepted. Once they're settled, set the status to `Accepted` and add a `#### Date` heading:

- **O1:** Should the depguard rule's ban on `net/http` also apply to the token packages' `_test.go` files? The `files` setting of `token-no-http` in `.golangci.yml` shows what the lint checks today.
- **O2:** Should R1 cover only direct imports, or every package in a token package's build? Only the second answer guarantees that `tokencheck` builds without `net/http`.

ADR-0012 binds no change until it's accepted.

The guide has a placeholder where it links to the "Checking a change" section of the adr-authoring skill. The repository doesn't use APM, so it needs a GitHub URL pinned to a version. Which URL and version should it use? Please fill it in before merging.

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

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation, and `internal/token/verify` verifies the token.
The planned command-line tool `tokencheck` verifies tokens offline with the same package.

A token's header names the algorithm of its signature in the `alg` member. The value `none` declares that the token
carries no signature (RFC 7518, section 3.6). A verifier that accepts such a token accepts claims that any client wrote.

## Decision

We will refuse every token whose header names the algorithm `none`, in `internal/token/verify`, and the HTTP server
will answer the request with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **token of a request**: the token that token-gate checks for a request before policy evaluation.
- **names the algorithm `none`**: the `alg` member of the token's header is the string `none`, compared
  case-sensitively.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` returns an error for every token whose header names the algorithm `none`,
  whatever the token's signature part holds, and reports no such token as verified.

#### Response

- **R2** (`http`, `token`). The HTTP server responds with HTTP 401 and the reason code `TOKEN_ALG_NONE` to every
  request whose token of a request names the algorithm `none`, and does not pass that request to policy evaluation.
  For such a request, `TOKEN_ALG_NONE` takes precedence over every other reason code that the token would get.

### Implementation notes

Adds no requirement. In `internal/token/verify`, read `alg` before any signature or claim check, and return an error
that `internal/http` maps to `TOKEN_ALG_NONE`. Add a test in `internal/token/verify` for a token with `alg` set to
`none`, with an empty signature part and with a non-empty one. Add a handler test in `internal/http` that sends such a
token and expects HTTP 401 with `TOKEN_ALG_NONE`. Add both tests under **Confirmation** when they land.

### Justification

A token that names the algorithm `none` carries no signature, so accepting it would let any client choose its own
claims (R1). The check sits in `internal/token/verify`, so `tokencheck` refuses such a token as the HTTP server does
(R1). A reason code of its own lets an operator tell an unsigned token from an expired or wrongly signed one (R2). An
unsigned token is a forgery whatever else is wrong with it, so its reason code wins over the others (R2).

### Alternatives considered

- **A1. Refuse `none` in the HTTP middleware in `internal/http` and leave `internal/token/verify` unchanged.** Rejected
  by R1: `tokencheck` would then accept such a token.
- **A2. Report a token with `alg` set to `none` under the reason code for an invalid signature.** Rejected by R2: the
  response has to carry `TOKEN_ALG_NONE`.

## Consequences

Positive:

- An operator can find attempts with unsigned tokens by the reason code `TOKEN_ALG_NONE` alone.

Negative:

- A token that names the algorithm `none` and also fails another check, such as an expired one, gets `TOKEN_ALG_NONE`
  instead of the reason code of that check (R2).

## Open points

- **O1.** Does an `alg` value that matches `none` only when case is ignored, such as `None` or `NONE`, name the
  algorithm `none`? The record assumes that it does not, because RFC 7515 compares `alg` values case-sensitively. A
  token with such a value then gets whatever `internal/token/verify` does for an unknown algorithm. The other answer
  ignores case, and such a token gets `TOKEN_ALG_NONE`. @example-security-architect decides. Affects R1, R2, and the
  term **names the algorithm `none`**.
- **O2.** Which reason code does a token get when it names the algorithm `none` and also fails another check? The
  record assumes `TOKEN_ALG_NONE` in every case. The other answer gives the reason code of the first check that fails,
  in the order the service runs its checks. @example-security-architect decides. Affects R2.
````

### Message to the user

I added ADR-0013 with status `Proposed`. Two open points keep it from acceptance, and @example-security-architect needs to settle them:

- **O1:** Should `None` or `NONE` count as `none`?
- **O2:** Should `TOKEN_ALG_NONE` win over every other reason code?

Once they're settled, set the status to `Accepted` and add a `#### Date` heading. Until then, the record binds no change.

Since no test covers the check yet, the record has no **Confirmation** section. **Implementation notes** suggests a test in `internal/token/verify` and a handler test in `internal/http`. When they land, add them under **Confirmation**, which an accepted record allows.

The change that adds those tests or the check counts as a change to code under the guide's layers, so it owes the trailers. Could you open an issue for the tests, and for any part of R1 or R2 the code doesn't meet yet? A change that leaves a rule out can then name that issue under `Defers:`.

Also, does `internal/token/verify` already check `alg` before the signature check? If it doesn't, a token with `alg` set to `none` might get the reason code for an invalid signature today, and O2 decides whether that answer changes.

This change only touches `docs/adr/`, so it carries no trailers.
