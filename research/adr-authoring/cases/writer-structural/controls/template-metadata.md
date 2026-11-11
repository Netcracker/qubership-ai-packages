## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of `internal/http` and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
### Owner

@example-architect

### Participants and approvers

- Architect, @example-architect: approves R1 and R2.

### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The packages under `internal/token/` parse and
verify a token. The packages under `internal/http/` hold the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. `tokencheck` has to build without the
HTTP server, so the packages it uses to parse and verify a token cannot bring the server into its build.

The depguard rule `token-no-http` in `.golangci.yml` reports a package under `internal/token/` that imports a package
under `internal/http/` or imports `net/http`. CI runs golangci-lint with that file on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`, so that `tokencheck` can verify tokens without the HTTP server.

### Terms

- **token package**: a Go package whose files sit in `internal/token/` or in a directory under it. Its `_test.go` files
  count, and so does a test package in the same directory, such as `verify_test`.
- **imports**: a Go file imports a package when an import declaration in the file names the import path of that
  package. A package that the file reaches only through another package is not imported.
- **HTTP standard package**: `net/http`, and every package whose import path starts with `net/http/`, such as
  `net/http/httptest`.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports a package whose files sit in `internal/http/` or in a directory under it.
- **R2** (`token`). No token package imports an HTTP standard package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports a package under `internal/token/` that imports a
  package under `internal/http/`. The `golangci-lint` step in `.github/workflows/ci.yml` runs this rule on every pull
  request.
- **R2**: the same depguard rule reports a package under `internal/token/` that imports `net/http`.

### Implementation notes

Adds no requirement. When a token package has to report why it refused a token, return an error value that the package
defines. A handler or a middleware in `internal/http/` then maps that error to an HTTP status. Put `tokencheck` in
`cmd/tokencheck`, and have it import the token packages and no package under `internal/http/`.

### Justification

`tokencheck` builds without the HTTP server only if the token packages it imports bring neither the code of
`internal/http/` nor `net/http` into its build (R1, R2). The depguard rule `token-no-http` already checks both imports
in CI, so the decision needs no new check (R1, R2).

## Consequences

Negative:

- A token package cannot use a type or a constant from `net/http`, such as `http.Header` or `http.StatusUnauthorized`.
  The mapping from a token error to an HTTP status lives in `internal/http/` (R2).
- A test of a token package cannot use `net/http/httptest` to serve keys or tokens (R2, O1).

## Open points

- **O1.** Whether R1 and R2 cover test files. The record assumes that they do, because **token package** includes the
  `_test.go` files and the test packages. The other answer leaves `_test.go` files and test packages out of R1 and R2,
  so that a test can use `net/http/httptest`. @example-architect decides. Affects R1 and R2.
- **O2.** Whether R1 and R2 cover indirect imports. The record assumes that they cover only direct imports, as
  **imports** states, and depguard checks only direct imports. The other answer also forbids a token package to import a
  package that brings in a package under `internal/http/` or an HTTP standard package, directly or through other
  packages. That answer needs a check that depguard cannot run, such as a test over the output of `go list -deps`.
  @example-architect decides. Affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code of token-gate. Before you change a file under a path that the layers in
this guide map, read the records that bind that change.

## Layers

A rule names its layer in parentheses, such as `(token)`. Each layer covers these paths:

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the binaries | `cmd/` |
| `build` | The module, the lint settings, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/` |

A test that sits beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/`, `AGENTS.md`.

A change that adds a file outside every path in this guide also adds the path to a layer or to the list of paths that
belong to no layer.

## Records that bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read in a record

Before you change code in a layer, read the **Terms**, **Rules**, **Confirmation**, and **Implementation notes** of each
binding record that has a rule in that layer. Anything that no rule states is your choice.

## Trailers

Every change to a file in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to #<issue>
```

- `Implements` names each rule that the change brings, in every case that the rule describes.
- `Defers` names each rule that the change leaves out, or brings only in part, with an existing issue or pull request
  that will bring the rest.

A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.

## Checking a change

A reviewer checks a change against the rules as
[Checking a change in the adr-authoring skill](<link to the adr-authoring skill on GitHub, at the pinned version>)
describes.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

## Architecture decision records

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
before you change code under those paths. End the commit message and the pull request description of such a change with
the `Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I've written ADR-0012 and a reading guide in `docs/adr/README.md`, and I've added a paragraph to `AGENTS.md` that points to the guide. Since the team agreed to it, every change to a file under `internal/`, `cmd/`, `go.mod`, `go.sum`, `.golangci.yml`, or `.github/` must now end its commit message and pull request description with the `Implements:` and `Defers:` trailers. This change only touches `docs/` and `AGENTS.md`, so it carries no trailers. A possible commit subject: `docs(adr): add ADR-0012 and a reading guide for the records`.

ADR-0012 has the status `Proposed`. To make it `Accepted`, @example-architect has to approve it and answer two open points. Then add a `#### Date` heading with the acceptance date after `## Status`, inside the markdownlint comments.

Questions:

1. **O1:** Should R1 and R2 also cover test files? The record assumes yes, which means no `net/http/httptest` in the tests of `internal/token/`.
2. **O2:** Should the rules cover only direct imports, which is what depguard checks? Or should they also cover imports that pass through other packages? Covering those would need a separate check.
3. In `.golangci.yml`, does `token-no-http` deny `net/http` as a prefix (no trailing `$`), so that it also catches `net/http/httptest`? Does it lint `_test.go` files? Until I know, the Confirmation section claims only that it reports `net/http` and `internal/http/`.
4. The guide's "Checking a change" link has a placeholder. Which GitHub URL and version of the adr-authoring skill should it point to?
5. Are there other top-level files, such as `README.md` or `Makefile`, that the guide should map to a layer or list under "no layer"?

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

- Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of `internal/http` and `net/http`](0012-token-packages-without-http.md):
  ADR-0012 R2 keeps `net/http` out of `internal/token/verify`, so the HTTP status that R2 of this record requires is
  set in `internal/http/`.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. The header of a signed token names the signing
algorithm in its `alg` member. The value `none` marks a token that carries no signature (RFC 7518, section 3.6). Any
client can write such a token with claims of its choice.

The security review places the check for this algorithm in `internal/token/verify`. No test covers the check.

## Decision

We will refuse every token whose header names the algorithm `none`, in `internal/token/verify`, and token-gate will
answer such a request with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **alg-none token**: a token whose header has an `alg` member with the value `none` in any mix of upper and lower case,
  such as `none`, `None`, or `NONE`.

### Rules

#### Verification

- **R1** (`token`). The `internal/token/verify` package refuses every alg-none token, whatever the signature and the
  claims of the token, and reports the reason code `TOKEN_ALG_NONE` for it. When another check of the same token fails
  too, the package reports `TOKEN_ALG_NONE` and no other reason code.

#### HTTP response

- **R2** (`http`). When `internal/token/verify` refuses the token of a request under R1, token-gate responds with HTTP
  status 401 and the reason code `TOKEN_ALG_NONE` in `<place of the reason code in the response>`, and the request does
  not reach policy evaluation.

### Implementation notes

Adds no requirement. Compare `alg` before `internal/token/verify` looks up a key or checks the signature, so that no
other check fails first. Return an error type that carries the reason code, and map it to the status 401 in the
middleware in `internal/http/`.

Add a table test in `internal/token/verify` with an `alg` of `none`, `None`, and `NONE`, plus an alg-none token whose
`exp` has passed. Add a middleware test in `internal/http/` that sends an alg-none token and checks the status, the
reason code, and that policy evaluation is never called. When the tests land, name them under a new **Confirmation**
section.

### Justification

An alg-none token carries no signature, so a verifier that accepts it accepts claims that any client wrote (R1). The
check sits in `internal/token/verify`, so every program that verifies tokens through that package refuses the token,
`tokencheck` included (R1). Clients send `None` and `NONE` to get past a comparison with the exact value `none` (R1).
A reason code that names this algorithm lets an operator tell an alg-none token apart from a token with a bad
signature, even when another check of the token fails too (R1, R2).

## Consequences

Negative:

- A client that sends unsigned tokens, such as a local development setup, gets HTTP 401 (R2).

## Open points

- **O1.** Where the 401 response carries the reason code: in a field of the error body, under a name to be chosen, or
  in a response header. The security review named the code but not its place. @example-security-architect decides.
  Affects R2.
- **O2.** Whether the comparison of `alg` with `none` ignores case. The record assumes that it does, as
  **alg-none token** states. The other answer covers only the exact value `none`, since RFC 7515 defines the `alg` value
  as case-sensitive. Under that answer, R1 and R2 do not cover `None` and `NONE`. @example-security-architect decides.
  Affects R1 and R2.
- **O3.** Which reason code `internal/token/verify` reports when an alg-none token also fails another check, such as an
  `exp` that has passed. The record assumes `TOKEN_ALG_NONE`, as R1 states. The other answer reports the reason code of
  whichever check runs first. @example-security-architect decides. Affects R1 and R2.
````

### Message to the user

I've written ADR-0013. The change only touches `docs/adr/`, which belongs to no layer in the guide, so its commit carries no trailers. A possible commit subject: `docs(adr): add ADR-0013 to refuse tokens with alg none`. ADR-0012 stays unchanged, because ADR-0013 builds on it and doesn't replace any part of it.

The record has the status `Proposed`. To make it `Accepted`, @example-security-architect has to approve it and answer three open points. Then add a `#### Date` heading with the acceptance date.

Questions for @example-security-architect:

1. **O1:** Where should the 401 response put `TOKEN_ALG_NONE`? In a field of the error body (which name?) or in a response header? R2 has a placeholder until this is answered.
2. **O2:** Should `None` and `NONE` be refused as alg-none tokens too? The record assumes yes.
3. **O3:** If an alg-none token fails another check as well (for example, it has expired), should the reason code still be `TOKEN_ALG_NONE`? The record assumes yes.

No test covers the check yet, so the record has no **Confirmation** section. Once the tests land, that section can be added to the record even after it's accepted. Could you open an issue for the tests? A later change to `internal/token/verify` or `internal/http/` that doesn't bring R1 or R2 in full can then name that issue in its `Defers:` trailer.
