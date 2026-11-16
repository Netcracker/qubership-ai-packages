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

Architect, @example-architect: approves R1 and R2.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The packages `internal/token/parse` and
`internal/token/verify` parse and verify the token. `internal/http` holds the HTTP server, its middleware, and its
handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It imports the token packages and has
to build without the HTTP server. Go links every package that an imported package imports.

The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the token packages. CI runs golangci-lint
with that file on every pull request. Depguard checks the import declarations of the files it lints. It does not check
the packages that those imports pull in.

## Decision

We will keep every Go file under `internal/token/` free of imports of `internal/http` and of `net/http`.

### Terms

- **token file**: a Go file in `internal/token/` or in a directory under it, `_test.go` files included.
- **imports**: a Go file imports a package when an import declaration in that file names the package's import path,
  whether the import is named, blank, or dot.
- **HTTP server package**: a package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **net/http package**: the standard library package `net/http`, or a standard library package whose import path
  starts with `net/http/`, such as `net/http/httptest`.

### Rules

#### Imports of the token files

- **R1** (`token`). No token file imports an HTTP server package.
- **R2** (`token`). No token file imports a net/http package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports an import of an HTTP server package in a token
  file. golangci-lint runs it in `.github/workflows/ci.yml` on every pull request.
- **R2**: the same depguard rule reports an import of a net/http package in a token file.

### Implementation notes

Adds no requirement. A token package that has to report a result that the HTTP server turns into a status code returns
an error or a result type of its own. `internal/http` then maps that type to the status code. Code that reads the token
from an `http.Request` stays in `internal/http` and passes the token to the token packages.

### Justification

`tokencheck` imports the token packages, so every package that a token file imports is linked into `tokencheck`. An
import of an HTTP server package would put the HTTP server into `tokencheck` (R1). An import of a net/http package would
put the standard library's HTTP stack into it (R2). The depguard rule fails the pull request that adds such an import,
so the violation shows before anyone builds `tokencheck` (R1, R2).

### Alternatives considered

- **A1. Import `net/http` in a token package for its status constants, such as `http.StatusUnauthorized`.** Rejected
  by R2: the import links the HTTP stack into `tokencheck`. The token package can return its own result type, and
  `internal/http` can map that type to the constant.

## Consequences

Negative:

- A token package cannot take an `http.Request` or an `http.Header` as a parameter (R2). Code that needs the request
  stays in `internal/http`.

## Open points

- **O1.** R1 and R2 cover the imports that a token file declares, which the depguard rule `token-no-http` checks. A
  token file can still reach an HTTP server package or a net/http package through a package that it imports, such as a
  third-party library that imports `net/http`. `tokencheck` would then link that package. The answers are to keep R1
  and R2 to declared imports, or to extend them to every package that a token package depends on and add a CI step
  that checks the dependencies, such as one built on `go list -deps`. @example-architect decides. Affects R1 and R2.
- **O2.** R1 and R2 assume that `_test.go` files count as token files. Under that assumption, a test that imports
  `net/http/httptest` to serve keys breaks R2, although `tokencheck` never compiles that test. The answers are to keep
  `_test.go` files in the term **token file**, or to limit it to the files that `go build` compiles.
  @example-architect decides. Affects R1 and R2.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

The records in this directory govern the code under the paths that the layer table maps to a layer. Read this guide
before you change that code.

## Layers

A rule names its layer in parentheses, such as `(token)`. Look for the code that a rule constrains under the paths of
that layer.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies tokens | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | The entry points of the binaries | `cmd/` |

A test file beside its code belongs to the layer of that code.

These paths belong to no layer, because no rule constrains them:

- `docs/`, `docs/adr/` included
- the Markdown files at the repository root, such as `AGENTS.md`
- `.github/`
- `.golangci.yml`
- `go.mod` and `go.sum`

When a rule starts to constrain one of these paths, move the path to a layer in the same pull request as the record.
A change that adds a file that neither the table nor this list covers adds the file's path to one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## What to read in a record

Before you change code in a layer, read the binding records whose rules carry that layer's tag. Read their **Terms**,
**Rules**, **Confirmation**, and **Implementation notes**. Anything that no rule states is your choice.

Outside its record, cite a rule with its record number, such as `ADR-0012 R1`.

## Trailers

A change to code under the paths of a layer ends its commit message and its pull request description with two
trailers:

```text
Implements: ADR-NNNN R1, R2
Defers: ADR-NNNN R3 to #<issue or pull request>
```

- `Implements` names each rule that the change brings, in every case that the rule describes.
- `Defers` names each rule that the change leaves out, or brings only in some of its cases. It names the issue or the
  pull request that will bring the rest. That issue or pull request has to exist. Where none exists yet, leave the rule
  out of the trailers, and name it in the pull request description as waiting for a change that has no issue yet.
- A change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.
- In a pull request with several commits, each commit carries the trailers for its own part, and the pull request
  description carries them for the whole change.

The trailers may name a rule of a `Proposed` record.

## Checking a change

A reviewer, or an agent, checks a change against the records with the procedure in
[Checking a change](<link to the adr-authoring skill on GitHub at the pinned version>#checking-a-change).
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.

## Architecture decision records

The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps to a layer. Read that guide
before you change such code. End the commit message and the pull request description of such a change with the
`Implements:` and `Defers:` trailers that the guide describes.
````

### Message to the user

I added ADR-0012, a reading guide in `docs/adr/README.md`, and a paragraph in `AGENTS.md` that points agents at the guide. The team agreed to the trailers, so from now on every change to code under `internal/` or `cmd/` has to end its commit message and its pull request description with `Implements:` and `Defers:`. A change that brings no rule and leaves none out carries neither trailer.

ADR-0012 is `Proposed`, and two open points keep it from being accepted:

- **O1:** Should R1 and R2 cover only the imports a token file declares, which is all depguard checks? Or should they also cover imports pulled in through other packages, such as a library that imports `net/http`? The second option needs an extra CI step.
- **O2:** Do `_test.go` files count? If they do, a test can't use `net/http/httptest`.

Once @example-architect settles both and approves, set the status to `Accepted` and add a `#### Date` heading with the acceptance date.

Things I need from you:

1. **Link to the checking procedure.** The guide needs a link to the "Checking a change" section of the `adr-authoring` skill. The repository doesn't use APM, so the link has to point at the skill on GitHub at a pinned version. I don't have that URL or version, so `docs/adr/README.md` has a visible placeholder. What URL and version should it use?
2. **Unlisted paths.** The guide puts `.github/`, `.golangci.yml`, `go.mod`, `go.sum`, `docs/`, and the root Markdown files in no layer, because no rule constrains them. Are there other top-level paths, such as `scripts/` or a `Makefile`, that I should list?
3. **Alternative A1.** The meeting notes list no alternatives. A1 (importing `net/http` for its status constants) is my addition. Was it discussed, or should I remove it?
4. **The depguard rule.** I couldn't read `.golangci.yml`. Can you confirm that `token-no-http` also blocks subpackages such as `net/http/httptest`? R2's Confirmation entry assumes it does.

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

Security architect, @example-security-architect: approves R1 and R2.

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  R2 of that record keeps `net/http` out of `internal/token/verify`, so R2 of this record sets the status code in
  `internal/http`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. `internal/token/verify` verifies the token, and
the HTTP server in `internal/http` turns the result into the response. The planned command-line tool `tokencheck` uses
`internal/token/verify` without the HTTP server.

RFC 7518 defines the algorithm `none` for a JWS that carries no signature. A verifier that accepts such a token
accepts a payload that anyone can write. RFC 8725 lists this as an attack on JWT libraries.

## Decision

We will refuse a token whose header names the algorithm `none`, in `internal/token/verify`, and answer the request with
status 401 and the reason code `TOKEN_ALG_NONE`.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses a token whose header parameter `alg` is the string `none` in any
  letter case, such as `none`, `None`, or `NONE`. It refuses the token whatever algorithms any setting of the service
  allows. To refuse the token, it returns an error that carries the reason code `TOKEN_ALG_NONE`, in place of any other
  error it would return for the same token.

#### Response

- **R2** (`http`). When `internal/token/verify` refuses the token of a request with the reason code `TOKEN_ALG_NONE`,
  the HTTP server answers that request with status 401 and the reason code `TOKEN_ALG_NONE` in
  `<response field for the reason code>`.

### Implementation notes

Adds no requirement. Check `alg` right after the header parses, before any key lookup or signature check. Then no later
check can return another error for the token. A table test in `internal/token/verify` with `none`, `None`, and `NONE`,
and a handler test in `internal/http` that expects status 401, would cover R1 and R2.

### Justification

A token signed with `none` carries no signature, so accepting it lets any client choose its own claims (R1). A
comparison that matches only the lowercase `none` lets `None` and `NONE` through, and earlier attacks on JWT libraries
used those spellings (R1). A setting that lists `none` among the allowed algorithms would reopen the attack, so R1
applies whatever the settings allow. `tokencheck` uses `internal/token/verify` without the HTTP server, so it refuses
the token too (R1). ADR-0012 R2 keeps `net/http` out of `internal/token/verify`, so the HTTP server maps the reason code
to status 401 (R2). A reason code of its own lets an operator find these refusals in the logs and the responses (R1,
R2).

### Alternatives considered

- **A1. Refuse `alg` `none` in the middleware of `internal/http` only.** Rejected by R1: `tokencheck` would accept the
  token.
- **A2. Compare `alg` with the lowercase string `none` only.** Rejected by R1: `None` and `NONE` would pass the check.

## Consequences

Negative:

- A client or a test setup that sends unsigned tokens with `alg` set to `none` gets status 401 (R1, R2). It needs a
  signing key that the service trusts.

## Open points

- **O1.** R2 needs the place in the response that carries the reason code. The answers are the place where the service
  already reports reason codes, if there is one, a field of the JSON body, or a response header.
  @example-security-architect decides. Affects R2.
- **O2.** R1 assumes that `alg` matches `none` in any letter case. The other answer is to refuse only the exact string
  `none` and to leave the other spellings to the rest of verification. @example-security-architect decides. Affects R1.
- **O3.** R1 assumes that `TOKEN_ALG_NONE` takes the place of any other error for the same token, such as one for an
  expired token. The other answer is that the first check that fails, in the order that `internal/token/verify` runs
  its checks, sets the reason code. @example-security-architect decides. Affects R1 and R2.
````

### Message to the user

I added ADR-0013. It has two rules: `internal/token/verify` refuses the token with `TOKEN_ALG_NONE` (R1), and the HTTP server answers with status 401 (R2). They're separate rules because ADR-0012 R2 keeps `net/http` out of `internal/token/verify`, so the status code has to be set in `internal/http`. The reading guide already covers both layers, so the guide and `AGENTS.md` stay as they are.

The record is `Proposed`, and three open points keep it from being accepted. @example-security-architect needs to answer them:

1. **O1:** Where does the response carry the reason code? R2 has a visible placeholder for it. If the service already reports reason codes in one place, that place is the answer.
2. **O2:** Is `none` matched in any letter case, as I assumed, or only as the exact lowercase string?
3. **O3:** Does `TOKEN_ALG_NONE` take the place of any other error for the same token, as I assumed? An expired token is one example. Or does the first check that fails set the reason code?

Once those are settled and approved, set the status to `Accepted` and add a `#### Date` heading with the acceptance date. ADR-0012 also needs a line under its Related ADRs then, saying that ADR-0013 R2 depends on its R2. An accepted record may take that kind of addition.

No test covers the check yet, so the record has no Confirmation section. Asking for a test is not a separate rule. Once tests for R1 and R2 land, add a Confirmation entry for each one, naming the test. That edit is allowed even after acceptance. The Implementation notes suggest what those tests would check.

The security review notes list no alternatives, so A1 and A2 are my additions. Should I keep them?
