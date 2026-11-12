## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of the HTTP server and of `net/http`

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

token-gate checks the token of each request before policy evaluation. The packages under `internal/token/` parse and
verify a token. The packages under `internal/http/` hold the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. The tool uses the token packages, and it
has to build without the HTTP server.

The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the token packages. golangci-lint runs it in
`.github/workflows/ci.yml` on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token` or a directory under it, such as
  `internal/token/verify`. An external test package in such a directory, such as `verify_test`, is a token package too.
- **imports**: a package imports another package when one of its `.go` files, `_test.go` files included, names the other
  package in an import declaration. An import that reaches the other package only through a third package is outside
  this term.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports `example/token-gate/internal/http` or a package whose import path starts
  with `example/token-gate/internal/http/`.
- **R2** (`token`). No token package imports `net/http`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports a token package that imports a package under
  `internal/http/`. golangci-lint runs the rule in `.github/workflows/ci.yml` on every pull request.
- **R2**: the depguard rule `token-no-http` reports a token package that imports `net/http`.

### Implementation notes

Adds no requirement. A token package reports a refused token as a Go error value, and the handlers in `internal/http/`
map that error to an HTTP status. The code that reads a token from an HTTP request, such as from the `Authorization`
header, stays in `internal/http/` and passes the token to the token packages as a string or a byte slice.

### Justification

`tokencheck` can build the token packages without the HTTP server only if no token package imports the server's
packages (R1) or `net/http` (R2). The depguard rule turns an import that breaks either rule into a lint failure in CI,
so a reviewer does not have to find it (R1, R2).

### Alternatives considered

- **A1. Return HTTP status codes from `internal/token/verify`, such as `http.StatusUnauthorized`.** Rejected by R2: the
  constant needs an import of `net/http`.
- **A2. Give `tokencheck` its own copy of the parse and verify code.** The two copies would drift apart, and the tool
  could then accept a token that the service refuses.

## Consequences

Negative:

- A token package cannot use the types of `net/http`, such as `http.Header` or `http.Request`. Code that needs them
  stays in `internal/http/`.

## Open points

- **O1.** Do R1 and R2 also cover indirect imports? The record assumes that they do not, as **imports** defines, and as
  depguard checks. With that answer, a token package may import a library that imports `net/http`, and `tokencheck`
  then links `net/http`. The other answer also forbids such an import. It needs a check of its own, such as a test that
  runs `go list -deps` on each token package. @example-architect decides. Affects R1 and R2.
- **O2.** Do R1 and R2 cover `_test.go` files? The record assumes that they do, as **imports** defines. The other answer
  lets a test of a token package import `net/http`, for example to build a request, because test files are not part of
  the `tokencheck` build. @example-architect decides. Affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records (ADRs) of token-gate. From ADR-0012 on, a record states its
requirements as numbered rules, and every change to the code a record governs is checked against those rules.

## Layers

Each rule names the layer it constrains in its tag, such as `(token)`.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | Runs the HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Holds the entry points of the binaries | `cmd/` |

A test beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/`, `AGENTS.md`, `.github/`, `.golangci.yml`, `go.mod`, and `go.sum`. A path stays
on this list only while no rule constrains it. A change that adds a file that neither the table nor this list covers
also adds the file to one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records bind none. ADR-0001 to ADR-0011 have
no numbered rules, so a check of a change reports them as unchecked.

## Writing code under the records

Before you change a file in a layer, read the `Accepted` records with rules tagged with that layer. Read their
**Terms**, **Rules**, **Confirmation**, and **Implementation notes**. Anything that no rule states is your choice.

## Trailers

A change to a file in a layer ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to #<issue>
```

- `Implements` names each rule that the change brings, in every case the rule describes.
- `Defers` names each rule that the change leaves out or brings only in part, with the issue or pull request that will
  bring the rest. The target exists before you name it. Where no issue exists yet, leave the rule out of the trailers,
  and say in the pull request description which rules wait for a change that has no issue yet.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.

In a pull request with several commits, each commit carries the trailers of its own part, and the description carries
them for the whole change. A check reads the description.

## Checking a change

A change is checked as the section "Checking a change" of the `adr-authoring` skill describes:
`<URL of the adr-authoring SKILL.md at a pinned version>`.
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

I've added ADR-0012 as `Proposed`. Its two open points block acceptance, and @example-architect decides both:

- **O1:** whether R1 and R2 also cover indirect imports. The record assumes they don't, which matches what depguard checks. With that answer, a library that imports `net/http` could still end up in the `tokencheck` build.
- **O2:** whether test files count. The record assumes they do.

Once both are settled and the architect signs off, set the status to `Accepted` and add a `#### Date` heading after the status line. The heading goes inside the markdownlint comment, as in ADR-0011.

As the team agreed, I've also added the reading guide at `docs/adr/README.md` and a bullet in `AGENTS.md` that points agents to it. From now on, every change under `internal/token/`, `internal/http/`, or `cmd/` ends with the `Implements:` and `Defers:` trailers. This change only touches files outside any layer, so it needs no trailers.

Three questions:

1. **Link to "Checking a change":** which URL should the guide use? The repository doesn't use APM, so the guide should link to the `adr-authoring` skill on GitHub at a pinned version. I left a visible placeholder in `docs/adr/README.md`.
2. **Other root files:** what else sits at the repository root besides `go.mod`, `go.sum`, `.golangci.yml`, `.github/`, `AGENTS.md`, and `docs/`? For example, a `README.md`, a `Makefile`, or a `Dockerfile`. The guide lists only the paths I know of, and each other path needs to go into a layer or into the list of paths that belong to no layer.
3. **depguard settings:** does `token-no-http` check `_test.go` files? It depends on the rule's `files` setting and on `run.tests` in `.golangci.yml`. If it skips them, O2's assumed answer has no machine check, and the R1 and R2 entries under **Confirmation** cover only non-test files.

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse a token whose `alg` is `none`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-security-architect

#### Participants and approvers

- Security architect, @example-security-architect: approves R1.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of
  `net/http`](0012-token-packages-without-http.md): the `net/http` import rule of ADR-0012 R2 applies to the code in the
  `token` layer that meets R1.
<!-- markdownlint-enable MD001 -->

## Context

token-gate checks the token of each request before policy evaluation. A token carries a JOSE header, and the header's
`alg` member names the algorithm that secures the token (RFC 7515, section 4.1.1). RFC 7518, section 3.6, defines the
value `none` for an unsecured token, which carries no signature. RFC 7515 makes the `alg` value case-sensitive, so
`None` and `NONE` name no algorithm that RFC 7518 defines.

The check that refuses a token whose `alg` is `none` sits in `internal/token/verify`.

## Decision

We will refuse every token whose `alg` is `none`, with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **`alg` of a token**: the value of the `alg` member in the JOSE header of a token that the service checks for a
  request.

### Rules

#### Unsecured tokens

- **R1** (`token`, `http`). When the service checks a token whose `alg` is `none` in any mix of upper and lower case,
  such as `none`, `None`, or `NONE`, the service responds to the request with HTTP status 401 and with the reason code
  `TOKEN_ALG_NONE` in `<the response field that carries the reason code>`. R1 also holds where another check would
  refuse the token for another reason.

### Implementation notes

Adds no requirement. `internal/token/verify` returns an error of its own for an `alg` of `none` before it runs any other
check of the token, and `internal/http/` maps that error to HTTP 401 and `TOKEN_ALG_NONE`. A test can build such a token
from the header `{"alg":"none"}`, any payload, and an empty signature part.

### Justification

A token whose `alg` is `none` has no signature, so anyone can write its claims, and the service would pass forged
claims to policy evaluation (R1). R1 matches `none` in any case, so a variant such as `NONE` gets the same response
however a token library treats it (R1).

### Alternatives considered

- **A1. Refuse a token whose `alg` is `none` with the same reason code as any other unsupported algorithm.** Rejected by
  R1: the response would not carry `TOKEN_ALG_NONE`.

## Consequences

Negative:

- A client that sends unsecured tokens, such as a local test setup that skips signing, gets HTTP 401 and has to sign its
  tokens (R1).
- An expired token whose `alg` is `none` gets `TOKEN_ALG_NONE`, not the reason code of an expired token (R1).

## Open points

- **O1.** Where does the response carry the reason code? R1 holds the placeholder
  `<the response field that carries the reason code>`. The answers under consideration are the field where the service
  already puts the reason code of a refused token, or a new field or header. @example-security-architect decides.
  Affects R1.
- **O2.** Does R1 match `none` in any case? The record assumes that it does. The other answer matches only the exact
  value `none`, as RFC 7515 compares `alg` values. `None` and `NONE` then get the response of an unsupported algorithm.
  @example-security-architect decides. Affects R1.
- **O3.** Does `TOKEN_ALG_NONE` take precedence over the reason code of another check that refuses the same token? The
  record assumes that it does. The other answer limits R1 to a token that no other check refuses.
  @example-security-architect decides. Affects R1.
````

### Message to the user

I've added ADR-0013 as `Proposed`. Its three open points block acceptance, and @example-security-architect decides all three:

- **O1:** where the response carries the reason code. R1 has a visible placeholder for it. If the service already returns reason codes in a fixed field, tell me its name and I'll close O1.
- **O2:** whether `None` and `NONE` count as `none`. The record assumes they do.
- **O3:** whether `TOKEN_ALG_NONE` wins when another check would also refuse the same token. The record assumes it does.

Once the open points are settled, check the existing code in `internal/token/verify` and its mapping in `internal/http/` against the answers. Then set the status to `Accepted` and add the `#### Date` heading.

No test covers the check yet, so the record has no **Confirmation** section. I suggest this issue:

- **Type:** Task
- **Title:** "Test the refusal of a token whose `alg` is `none`"
- **Scope:** a test in `internal/token/verify` that the check returns its error, and a test in `internal/http/` that the response has status 401 and carries `TOKEN_ALG_NONE`. It should include the cases that O2 and O3 settle.

When the tests land, add them under **Confirmation** in ADR-0013. An accepted record takes that addition.

Should I open that issue?
