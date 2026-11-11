## Request 1

### File: docs/adr/0012-token-packages-free-of-http.md

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

`internal/token/` holds the packages that parse and verify a token: `internal/token/parse` and
`internal/token/verify`. `internal/http/` holds the HTTP server, its middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline. It has to build without the HTTP
server. The depguard rule `token-no-http` in `.golangci.yml` checks the imports of `internal/http/` and of `net/http`
in `internal/token/`, and CI runs it on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose directory is `internal/token/` or a subdirectory of it, such as
  `internal/token/parse`.
- **import**: an `import` declaration in a `.go` file of the importing package, a `_test.go` file included (O1).
  Packages that the imported package imports in turn are not imports of the importing package (O3).

### Rules

#### Imports of the token packages

- **R1** (`token`). No `.go` file of a token package imports `example/token-gate/internal/http` or a package beneath it.
- **R2** (`token`). No `.go` file of a token package imports `net/http` (O2).

### Confirmation

- **R1**, **R2**: the depguard rule `token-no-http` in `.golangci.yml`, which golangci-lint runs in
  `.github/workflows/ci.yml` on every pull request.

### Justification

`tokencheck` has to build without the HTTP server. A token package that imports a package under `internal/http/` puts
the server into that build (R1). A token package that imports `net/http` puts the HTTP server code of the standard
library into it (R2).

### Alternatives considered

- **A1. Let a token package import a package under `internal/http/` for shared types, such as a status code.** Rejected
  by R1: the import puts the server package into the build of `tokencheck`.
- **A2. Let a token package import `net/http` for its types, such as `http.Header`.** Rejected by R2: the import puts
  the HTTP server code of the standard library into the build of `tokencheck`.

## Consequences

Negative:

- A token package cannot use a type of `net/http` or of `internal/http/`, so the HTTP layer converts between those types
  and the types of the token packages (R1, R2).

## Open points

- **O1.** Do R1 and R2 cover `_test.go` files? The record assumes they do. The alternative is that they cover only the
  files that go into a build. @example-architect decides. Affects R1, R2.
- **O2.** Does R2 cover the packages beneath `net/http`, such as `net/http/httptest`? The record assumes it names only
  `net/http`. The alternative is `net/http` and every package beneath it. @example-architect decides. Affects R2.
- **O3.** Do R1 and R2 cover an indirect path, where a token package imports a package that imports `internal/http/` or
  `net/http`? The record assumes they cover direct imports only. The alternative is direct and indirect imports.
  @example-architect decides. Affects R1, R2.
````

### File: docs/adr/README.md

````markdown
# Reading the decision records

Records with numbered rules govern the code under the paths in **Layers**. A change to that code ends its commit
message and its pull request description with the trailers in **Trailers**.

## Layers

A rule names its layer in parentheses, such as (`token`). A test beside its code belongs to the layer of that code.

| Layer | Role | Paths |
| --- | --- | --- |
| `token` | Parsing and verifying a token | `internal/token/` |
| `http` | The HTTP server, its middleware, and its handlers | `internal/http/` |
| `entrypoint` | The service's entry point | `cmd/token-gate/` |
| `build` | Module files, lint configuration, and CI | `go.mod`, `go.sum`, `.golangci.yml`, `.github/workflows/` |

These paths belong to no layer: `docs/adr/` and `AGENTS.md`. A change that adds a file that neither the layers nor this
list cover extends one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not.

## Writing code under a record

Before you change code in a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
`Accepted` record that has a rule for that layer. Anything no rule states is your choice.

## Trailers

End the commit message and the pull request description of a change with these trailers:

```text
Implements: ADR-0012 R1, R2
Defers: ADR-0012 R2 to #<issue or pull request number>
```

`Implements` names the rules the change brings. `Defers` names each rule the change leaves out, with an existing issue
or pull request that will bring it. A change that brings only some cases of a rule names that rule under `Defers`. A
change that brings no rule and leaves none out, such as a refactoring, carries neither trailer.

## Checking a change

**Checking a change** in the [adr-authoring skill](<URL of adr-authoring SKILL.md at the pinned version>) describes how
a change is checked against the rules.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps. Read that guide before you
  change such code, and end the commit message and the pull request description with the `Implements:` and `Defers:`
  trailers it describes.
````

### Message to the user

I wrote ADR-0012 and, because the team agreed to it, a reading guide in `docs/adr/README.md` with a matching bullet in `AGENTS.md`. This change adds documents only. It brings no rule and defers none, so its commit message and pull request description carry no trailers.

- **Status:** the record is `Proposed`. There is no Date heading yet. Add it with the acceptance date once @example-architect signs off and the three open points below are answered.
- **Open points:** each has an assumption written into the record.
  - O1: do the rules cover `_test.go` files? I assumed yes.
  - O2: does R2 cover the packages beneath `net/http`, such as `net/http/httptest`? I assumed it names only `net/http`.
  - O3: do the rules cover indirect imports? I assumed direct imports only.
  - Please check these against the `token-no-http` configuration in `.golangci.yml`, which I could not see.
- **Link in the guide:** the guide links to **Checking a change** in the `adr-authoring` skill, but the repository does not use APM and I don't know the URL. The link holds the placeholder `<URL of adr-authoring SKILL.md at the pinned version>`. What URL and version should it point to?
- **Layers:** I mapped only the directories you described. If the repository has other code, such as the policy evaluation, a change to it is a guide error until one of the layers is extended. Which paths should that code map to?
- **Existing records:** ADR-0001 to 0011 have no numbered rules. A check of a change lists them as unchecked.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

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

- [ADR-0012: Keep the token packages free of imports of the HTTP server and of `net/http`](0012-token-packages-free-of-http.md):
  R2 keeps `net/http` out of `internal/token/verify`, so R1 of this record returns an error and R2 sets the status.
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` carries no signature, so anyone can create one. The security review
decided that the service refuses such a token. `internal/token/verify` verifies tokens, and `internal/http/` answers
requests. No test covers the refusal yet.

## Decision

We will refuse every token whose header names the algorithm `none`, with HTTP status 401 and the reason code
`TOKEN_ALG_NONE`, and we will make the check in `internal/token/verify`.

### Terms

- **none-algorithm token**: a token whose header names the algorithm `none`, written exactly so (O2).
- **refuse**: `internal/token/verify` ends the verification of a token with an error, not with a verified token.

### Rules

#### Refusal of a none-algorithm token

- **R1** (`token`). `internal/token/verify` refuses a none-algorithm token, whatever else the token contains, and the
  error it returns carries the reason code `TOKEN_ALG_NONE` (O3).
- **R2** (`http`). The HTTP server answers a request whose token `internal/token/verify` refuses under R1 with status
  401 and the reason code `TOKEN_ALG_NONE` in `<place of the reason code in the response>` (O1).

### Justification

A token with algorithm `none` proves nothing about who sent it. The check sits in `internal/token/verify`, so every
caller of that package refuses such a token, whichever way the caller treats the error (R1). The status 401 tells the
client that its credentials failed, and the reason code tells it and the logs why (R2).

### Alternatives considered

- **A1. Check for the algorithm `none` in the HTTP middleware instead of in `internal/token/verify`.** Rejected by R1:
  code that calls `internal/token/verify` without the middleware would accept the token.

## Consequences

Negative:

- No environment accepts an unsigned token, a test setup included (R1).

## Open points

- **O1.** Where does the reason code appear in the response of R2: a field of the response body, or a response header?
  The rule holds a placeholder until it is settled. @example-security-architect decides. Affects R2.
- **O2.** Does a header that names the algorithm in another case, such as `None` or `NONE`, make a none-algorithm token?
  The record assumes only the exact name `none` does. The alternative is a case-insensitive match. The answer also
  decides which reason code a token with `None` gets. @example-security-architect decides. Affects R1, R2.
- **O3.** Does `TOKEN_ALG_NONE` win where a none-algorithm token also fails another check, such as an expired
  timestamp? The record assumes it wins, because R1 holds whatever else the token contains. The alternative is that the
  other failure's reason code wins. @example-security-architect decides. Affects R1, R2.
````

### Message to the user

I wrote ADR-0013 as `Proposed`. The three open points block acceptance. There is no Date heading until it is accepted.

- **Two rules, two layers:** ADR-0012 R2 forbids `internal/token/verify` from importing `net/http`, so R1 (`token`) has `verify` return an error with the reason code, and R2 (`http`) has the HTTP server answer with 401. This reads "refused with HTTP 401" as an HTTP-layer outcome. If the 401 is meant to come from somewhere else, tell me and I'll change R2.
- **O1:** where does the reason code appear in the response, in the body or in a header? R2 holds a visible placeholder until you answer.
- **O2:** does `None` or `NONE` count as the algorithm `none`? I assumed only the exact name does.
- **O3:** does `TOKEN_ALG_NONE` win where the token also fails another check? I assumed it wins.
- **No Confirmation section:** no check exists, so the record leaves it out. I suggest two tests: one in `internal/token/verify` for R1, and one in `internal/http` for R2. Once they land, add their entries to **Confirmation**. An accepted record takes that edit.
- **Trailers:** this change adds a document only, so it carries no trailers. The change that adds the tests will need `Implements:` or `Defers:` trailers for R1 and R2. A `Defers` target must be an existing issue, and I don't have one. If you want to defer either rule, open an issue for the missing test and give me its number.
- **Dependency on ADR-0012:** the record cites ADR-0012 R2. If ADR-0012 changes before it is accepted, I'll update the link and the sentence that cites it.
