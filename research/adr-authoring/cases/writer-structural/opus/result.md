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

- Architect, @example-architect: approves R1.

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. The packages `internal/token/parse` and
`internal/token/verify` parse and verify a token. The HTTP server, its middleware, and its handlers are in
`internal/http/`.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It has to build without the HTTP server.
The Go toolchain compiles every package that a binary imports into the binary, together with the packages those
packages import. A token package that imports the HTTP server would therefore bring the server into `tokencheck`.

The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the token packages. CI runs golangci-lint
with that file on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a directory under it. Its `_test.go` files
  count as part of it.
- **HTTP package**: `net/http`, every package whose import path starts with `net/http/`,
  `example/token-gate/internal/http`, and every package whose import path starts with
  `example/token-gate/internal/http/`.
- **imports**: a Go file imports a package when one of its import declarations names that package.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP package.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` fails on an import of `net/http` or of a package under
  `internal/http/` in a token package. golangci-lint runs it in `.github/workflows/ci.yml` on every pull request.

### Implementation notes

Adds no requirement. Where a token package needs to report why it refused a token, give it an error value or a reason
code of its own, and let `internal/http` map that value to a status code and a response. `tokencheck` can then live
under `cmd/tokencheck` and import `internal/token/parse` and `internal/token/verify` directly.

### Justification

`tokencheck` builds without the HTTP server only if no token package brings the server in (R1). `net/http` and its
subpackages hold the standard library's HTTP server, and an offline tool needs no part of them (R1). A lint rule reports
a forbidden import in the pull request that adds it. Without the lint rule, the import would only show up later, when
`tokencheck` fails to build without the server (R1).

### Alternatives considered

- **A1. Import `net/http` in a token package only for constants, such as `http.StatusUnauthorized`.** Rejected by R1:
  the import compiles `net/http` into `tokencheck` all the same.
- **A2. Build `tokencheck` from its own copy of the parse and verify code.** The two copies of the verification would
  drift apart, and a fix in one would miss the other.

## Consequences

Positive:

- A change under `internal/http/` leaves the cached test results of the token packages valid, so `go test ./...` does
  not rerun them.

Negative:

- A test of a token package cannot use `net/http/httptest` (R1, and O2).
- An error from a token package carries no HTTP status, so `internal/http` keeps a mapping from each error to a status
  code.

## Open points

- **O1.** Does R1 forbid only a direct import, or also an HTTP package that a token package reaches through another
  package of the module, such as a package under `internal/` that imports `internal/http`? The record assumes direct
  imports only, which is what `token-no-http` checks. Forbidding indirect imports would need a second check, such as a
  test that runs `go list -deps` on each token package. The architect decides. It affects the term **imports** and R1.
- **O2.** Do `_test.go` files count as part of a token package? The record assumes that they do. The alternative leaves
  them out, since `go build` does not compile them into `tokencheck`. The architect decides. It affects the term
  **token package**, R1, and the first negative consequence.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

This directory holds the architecture decision records of token-gate. A record with numbered rules applies to code under
the paths that **Layers** maps, and a change to that code is checked against those rules.

## Layers

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parses and verifies a token | `internal/token/` |
| `http` | HTTP server, its middleware, and its handlers | `internal/http/` |
| `cmd` | Entry points of the binaries | `cmd/` |

A test file beside its code belongs to the layer of that code.

These paths belong to no layer: `docs/`, `.github/`, `.golangci.yml`, `go.mod`, `go.sum`, and `AGENTS.md`. A path
leaves this list once a rule applies to it, and joins the layer of that rule. A change that adds a file that neither
the table nor this list covers adds the file to one of them.

## Which records bind a change

Records with the status `Accepted` bind a change. Records with the status `Proposed`, `Superseded`, or `Rejected` do
not.

Records `0001-` to `0011-` have no numbered rules, so a check of a change reports them as unchecked.

## Writing code under the records

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
record that binds the change. Anything that no rule states is your choice.

## Trailers

A change to code under a path in **Layers** ends its commit message and its pull request description with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0013 R2 to #<issue>
```

`Implements` names the rules the change brings in full. `Defers` names each rule the change leaves out or brings only in
part, with the existing issue or pull request that will bring the rest. A change that brings no rule and defers none,
such as a refactoring, carries neither trailer.

## Checking a change

To check a change against the records, follow
[Checking a change](<URL of the adr-authoring skill at the pinned version>#checking-a-change).
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` apply to the code under the paths that `docs/adr/README.md` maps to layers. Read that
  guide before you change such code, and end the commit message and the pull request description with the
  `Implements:` and `Defers:` trailers it describes.
````

### Message to the user

I wrote the decision as ADR-0012, with one rule, R1, and added the reading guide in `docs/adr/README.md`. `AGENTS.md` now has a paragraph that points agents at the guide and asks for the trailers.

**Why ADR-0012 is still `Proposed`.** It has two open points:

- **O1:** whether R1 forbids only direct imports, or also an HTTP package reached through another package of the module.
- **O2:** whether `_test.go` files count as part of a token package.

The record assumes direct imports only and counts test files. Once @example-architect settles both and signs off, the record needs three changes:
1. Empty **Open points**.
2. Set the status to `Accepted`.
3. Add a `#### Date` heading with the acceptance date, before `#### Owner`, inside the markdownlint comments.

**Questions:**

- **Skill link:** the guide links to the procedure for checking a change. The repository doesn't use APM, so that link has to go to the adr-authoring skill on GitHub at a pinned version. Which repository and version should it point to? The link in `docs/adr/README.md` is a visible placeholder until then.
- **depguard settings:** does the `files` setting of `token-no-http` include `_test.go` files, and does its deny list match subpackages of `net/http`? If the answer to O2 differs from what the rule checks, either the rule or the record has to change.

**Notes:**

- Records `0001-` to `0011-` have no numbered rules, so a check reports them as unchecked.
- This change only touches `docs/` and `AGENTS.md`, so it needs neither trailer.

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

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-without-http.md):
  the import rule R1, which applies to `internal/token/verify`.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. A JSON Web Token names its signature algorithm
in the `alg` parameter of its header. The value `none` marks an unsecured token, which carries no signature (RFC 7518,
section 3.6). A verifier that accepts such a token accepts a token that anyone can write.

`internal/token/verify` holds the check of `alg`. No test covers it.

## Decision

We will refuse every token whose header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`.

### Terms

- **`alg`**: the value of the `alg` parameter in the header of a token.
- **names the algorithm `none`**: `alg` is a string equal to `none` when compared case-insensitively, so `None` and
  `NONE` are included.

### Rules

#### Verification

- **R1** (`token`). `internal/token/verify` refuses a token whose `alg` names the algorithm `none`, with an error that
  carries the reason code `TOKEN_ALG_NONE`. Where another check of `internal/token/verify` would also refuse that token,
  the error still carries `TOKEN_ALG_NONE`.

#### Response

- **R2** (`http`). A request whose token `internal/token/verify` refuses with the reason code `TOKEN_ALG_NONE` gets a
  response with HTTP status 401. The response carries `TOKEN_ALG_NONE` in `<part of the response that carries the
  reason code>`. Policy evaluation does not run for the request.

### Implementation notes

Adds no requirement. Check `alg` before any other check of the token, so that the reason code of R1 does not depend on
the order of later checks. A table test in `internal/token/verify` with the `alg` values `none`, `None`, and `NONE`
covers R1. A handler test in `internal/http` that sends such a token and asserts the status, the reason code, and that
policy evaluation never ran covers R2.

### Justification

A token whose `alg` is `none` has no signature to verify, so accepting it would let any client write its own token
(R1). Some libraries have accepted `none` written in other cases, so the comparison ignores case (R1). A reason code of
its own lets a client and an operator tell this refusal apart from the others (R1, R2). Status 401 says that the request
carries no valid credentials (R2). Under the import rule of ADR-0012 R1, `internal/token/verify` cannot set an HTTP
status, so `internal/http` sets it (R2).

### Alternatives considered

- **A1. Treat `alg: none` as an unsupported algorithm, and refuse it with the reason code of that case.** Rejected by R1:
  the error carries `TOKEN_ALG_NONE`.
- **A2. Accept `alg: none` from internal callers, such as health checks or local development.** Rejected by R1: R1 has
  no exception.
- **A3. Answer with HTTP status 403.** Rejected by R2: the status is 401.

## Consequences

Negative:

- A test client or development tool that sends unsigned tokens to the service gets 401 (R2), so it needs a signed
  token.

## Open points

- **O1.** Which part of the 401 response carries the reason code: a field of a JSON body, the `error_description` of a
  `WWW-Authenticate` header, or a header of its own. The security architect decides. It affects R2.
- **O2.** The record assumes that `alg` is compared case-insensitively. The alternative is an exact comparison, as RFC
  7515 prescribes for `alg`. With an exact comparison, `None` gets whatever outcome `internal/token/verify` gives an
  unknown algorithm. The security architect decides. It affects the term **names the algorithm `none`** and R1.
- **O3.** The record assumes that `TOKEN_ALG_NONE` wins over the reason code of any other check that would also refuse
  the token. The alternative lets the order of the checks in `internal/token/verify` decide. The security architect
  decides. It affects R1.
````

### Message to the user

I wrote the decision as ADR-0013 with two rules:

- **R1** (`token`): `internal/token/verify` refuses the token with `TOKEN_ALG_NONE`.
- **R2** (`http`): the request gets a 401 that carries the code.

Under ADR-0012 R1, `internal/token/verify` can't import `net/http`, so `internal/http` has to set the 401. That's why it's two rules.

**Why the record stays `Proposed`.** Three open points need an answer from @example-security-architect:

- **O1:** Which part of the 401 response carries `TOKEN_ALG_NONE`? R2 has a visible placeholder until then.
- **O2:** Should `alg` be compared case-insensitively? The record assumes yes, so `None` and `NONE` are refused too.
- **O3:** Should `TOKEN_ALG_NONE` win when another check would also refuse the token? The record assumes yes.

Once they answer and sign off, the record needs four changes:
1. Fill in the placeholder in R2.
2. Empty **Open points**.
3. Set the status to `Accepted`.
4. Add `#### Date` with the acceptance date.

**Tests.** No test covers R1 or R2 yet, so the record has no **Confirmation** section. I suggest you open this issue:

- **Type:** Task
- **Title:** "Test the refusal of tokens with `alg: none` (ADR-0013 R1, R2)"

When the tests land, add them under **Confirmation**; an accepted record allows that edit.

**Trailers.** This change only touches `docs/adr/`, so it needs neither trailer. A later change that makes the code meet R1 or R2 should name those rules under `Implements`.
