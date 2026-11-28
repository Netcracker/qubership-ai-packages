## Request 1

### File: `docs/adr/0012-token-packages-free-of-http.md`

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

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

`internal/token/` holds the packages that parse and verify a token. The planned command-line tool `tokencheck` verifies
tokens offline, so it has to build without the HTTP server. A token package that imports a package under
`internal/http/` or the package `net/http` puts that import into the build of every program that links the token
package, `tokencheck` included.

The depguard rule `token-no-http` in `.golangci.yml` checks both imports, and CI runs it on every pull request.

## Decision

We will not let any package under `internal/token/` import a package under `internal/http/` or the package `net/http`.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or begins with
  `example/token-gate/internal/token/`. The test files in its directory belong to it.
- **HTTP package**: a Go package whose import path is `example/token-gate/internal/http` or begins with
  `example/token-gate/internal/http/`, and the package `net/http`. Other packages under `net/http/`, such as
  `net/http/httptest`, are not HTTP packages (O2).
- **import**: an `import` declaration in a file of the importing package. A package that a token package imports
  and that itself imports an HTTP package is not an import of the token package (O1).

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports the import, and `golangci-lint run` fails on
  it. CI runs `golangci-lint run` on every pull request.

### Implementation notes

Adds no requirement. Where a token package has to report an outcome that the HTTP server turns into a status code,
return an error or a result type from the token package, and map it to the status code in `internal/http`.

### Justification

`tokencheck` has to build without the HTTP server, so no package that it links can import `internal/http/` or
`net/http` (R1).

## Consequences

Negative:

- A token package cannot use `net/http` types such as `http.Header` or `http.StatusUnauthorized`. The code in
  `internal/http` converts between those types and the types of the token packages (R1).

## Open points

- **O1.** Does R1 cover an HTTP package that a token package reaches through another package? The record assumes it
  does not, because the depguard rule checks direct imports only. The other answer, covering indirect imports, needs a
  different check, such as one built on `go list -deps`. @example-architect decides. This affects R1.
- **O2.** May a test file of a token package import `net/http/httptest`? The record assumes it may, because the term
  **HTTP package** names only `net/http`. The other answer forbids it. @example-architect decides. This affects R1.
````

### File: `docs/adr/README.md`

````markdown
# Reading guide for the decision records

The records in this directory hold numbered rules. This guide maps the rules to code and says what each change owes.

## Layers

Each rule carries the tag of the layer whose code it constrains.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parse and verify a token. | `internal/token/`, tests beside the code included |
| `http` | The HTTP server, its middleware, and its handlers. | `internal/http/`, tests beside the code included |
| `entrypoint` | The service's entry point. | `cmd/token-gate/` |
| `build` | Dependencies, lint settings, and CI. | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`. A change that adds a file that neither the layers nor this
list cover extends one of them.

## Which records bind a change

A record with the status `Accepted` binds a change. A record with the status `Proposed`, `Superseded`, or `Rejected`
binds none.

## What you read before you change code

Read these sections of each record that governs the code you change: **Terms**, **Rules**, **Confirmation**, and
**Implementation notes**. A rule is a requirement. A case that no rule states is your choice.

## Trailers

Every change to code under the paths in the table ends its commit message and its pull request description with two
trailers. In a pull request with several commits, each commit carries the trailers of its own part, and the description
carries them for the whole change.

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R1 to #<issue or pull request number>
```

- `Implements` lists the rules the change brings. It claims every case of each rule it names.
- `Defers` lists each rule the change leaves out, with the issue or pull request that will bring it. The target has to
  exist.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.

## Checking a change

<URL of "Checking a change" in the adr-authoring skill, at the version this repository pins>
````

### File: `AGENTS.md`

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to layers. Read that guide
  before you change such code, and end the commit message and the pull request description with the `Implements:` and
  `Defers:` trailers that it describes.
````

### Message to the user

I wrote ADR-0012 with status `Proposed`. You didn't say the team signed it off, and O1 and O2 are open. Once the team accepts it and both points are answered, set `Accepted` and add a `#### Date` heading with the acceptance date.

Questions for @example-architect:

- **O1:** Should R1 also cover imports that reach `internal/http/` or `net/http` through another package? I assumed it doesn't, because depguard checks direct imports only. `tokencheck` would still pull in the HTTP stack through an indirect import, so you may want a stricter check.
- **O2:** May a token package's test files import `net/http/httptest`? I assumed they may.

Other points:

- **Reading guide:** you agreed to keep one and to use the trailers, so I added `docs/adr/README.md` and a paragraph in `AGENTS.md`. The guide's last section has a placeholder for the link to "Checking a change" in the `adr-authoring` skill. Replace it with the URL of the version you pin, or with the path of a committed copy.
- **Layers:** I guessed the `build` layer and the layer names. Please check them.
- **Trailers:** this change touches no code under the mapped paths, so it needs no trailers.
- **Confirmation:** I couldn't see `.golangci.yml`, so the Confirmation entry for R1 rests on your description of `token-no-http`.

## Request 2

### File: `docs/adr/0013-refuse-tokens-with-algorithm-none.md`

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

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-free-of-http.md):
  R1 keeps `net/http` out of `internal/token/verify`, so R1 of this record states the refusal as an error with a reason
  code, and R2 states the HTTP response.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. A token whose header names the algorithm
`none` declares that it has no signature, so signature verification cannot confirm its claims. The security review
decided how the service treats such a token.

The check sits in `internal/token/verify`. ADR-0012 R1 forbids that package to import `net/http`, so the HTTP status
code is set in `internal/http`.

## Decision

We will refuse every token whose header names the algorithm `none`: `internal/token/verify` returns an error with the
reason code `TOKEN_ALG_NONE`, and the HTTP server answers with status 401 and the same reason code.

### Terms

- **none-algorithm token**: a token whose header names the algorithm `none`. The name is compared with `none` without
  regard to case (O1).

### Rules

#### Refusal of a none-algorithm token

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE` for a
  none-algorithm token, whatever the signature part of the token holds.
- **R2** (`http`). For a request whose token `internal/token/verify` refused with the reason code `TOKEN_ALG_NONE`,
  the HTTP server responds with status 401 and carries the reason code `TOKEN_ALG_NONE` in
  `<location of the reason code in the response>` (O2).

### Implementation notes

Adds no requirement. Let the error of `internal/token/verify` expose the reason code as a value of a type that package
defines, and let the middleware in `internal/http` map that value to the status code and the response field.

### Justification

A none-algorithm token declares itself unsigned, and the security review chose to refuse it instead of accepting it
(R1). The status 401 tells the caller that the token is refused, and the reason code tells it why (R2).

## Consequences

Negative:

- No setting turns the refusal off, so a client that sends a none-algorithm token is refused in every environment (R1,
  R2).

## Open points

- **O1.** Is the name compared without regard to case, so that `None` and `NONE` also make a none-algorithm token? The
  record assumes they do. The other answer compares the exact string `none`. @example-security-architect decides. This
  affects R1 and R2.
- **O2.** Where does the response carry the reason code: a field of the response body, a response header, or both? The
  record has a placeholder in R2 until it is answered. @example-security-architect decides. This affects R2.
````

### Message to the user

I wrote ADR-0013 with status `Proposed`, because O1 and O2 are open. Once both are answered and the team signs off, set `Accepted` and add the `#### Date` heading.

Questions for @example-security-architect:

- **O1:** Is `None` or `NONE` also refused? I assumed so, because an exact-case comparison lets those spellings through.
- **O2:** Where does the response carry `TOKEN_ALG_NONE`: the body, a header, or both? R2 holds a visible placeholder until this is answered.

Other points:

- **Two rules:** you described one refusal, but I split it into R1 (`internal/token/verify` returns an error with the reason code) and R2 (`internal/http` sets the 401). ADR-0012 R1 forbids `net/http` in `internal/token/`, so `verify` can't set an HTTP status. If the 401 is meant to come from `verify` itself, this record and ADR-0012 conflict, and one of them has to change.
- **No Confirmation section:** no test covers R1 or R2 yet, so I left it out. Add entries when the tests land. An accepted record takes that edit. I suggest opening an issue for a test of each rule. A change that adds the tests can then name the issue under `Defers:`, and I haven't guessed an issue number.
- **No other source:** I didn't write any rule beyond what the review stated.
