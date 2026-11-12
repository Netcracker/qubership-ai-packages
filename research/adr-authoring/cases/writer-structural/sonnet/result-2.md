## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep the token packages free of imports of the HTTP server and `net/http`

## Status

Proposed

<!-- markdownlint-disable MD001 -->
#### Owner

@example-architect

#### Participants and approvers

Architect, @example-architect: approves R1 and R2

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation. `internal/token/parse` and
`internal/token/verify` hold the code that parses and verifies a token, and `internal/http/` holds the HTTP server, its
middleware, and its handlers.

The team plans a command-line tool, `tokencheck`, that verifies tokens offline and has to build without the HTTP
server. The depguard rule `token-no-http` in `.golangci.yml` checks the imports of the token packages, and CI runs it
on every pull request.

## Decision

We will keep every package under `internal/token/` free of imports of the packages under `internal/http/` and of
`net/http`.

### Terms

- **token package**: a Go package whose import path is `example/token-gate/internal/token` or starts with
  `example/token-gate/internal/token/`. The test files in its directory belong to it.
- **HTTP server package**: a Go package whose import path is `example/token-gate/internal/http` or starts with
  `example/token-gate/internal/http/`.
- **import**: a direct import declaration in a Go file of the package. A package that an imported package imports in
  turn is not imported.

### Rules

#### Imports of the token packages

- **R1** (`token`). No token package imports an HTTP server package.
- **R2** (`token`). No token package imports the package `net/http`.

### Confirmation

- **R1**: the depguard rule `token-no-http` in `.golangci.yml` reports an import of an HTTP server package. CI runs it
  through golangci-lint on every pull request.
- **R2**: the same depguard rule reports an import of `net/http`.

### Implementation notes

Adds no requirement. A token package returns plain Go values and errors. The code under `internal/http/` translates
them into HTTP responses.

### Justification

The command-line tool `tokencheck` verifies tokens offline and has to build without the HTTP server. The packages that
parse and verify a token therefore must not import the server (R1) or `net/http` (R2).

## Consequences

Negative:

- A token package cannot use identifiers of `net/http`, such as status codes (R2). The code under `internal/http/` has
  to translate the result of a token package into an HTTP response.

## Open points

- **O1.** Whether the test files of a token package are bound by R1 and R2. The rules assume they are. The other answer
  is that only the non-test files are bound. @example-architect decides. The depguard rule `token-no-http` may need a
  change of its file scope to match the answer.
- **O2.** Whether R1 and R2 reach imports through another package. The rules assume they do not, so a token package may
  import a package that imports `net/http`. The other answer is that no package in the import graph of a token package
  may import them. That answer needs a check beyond depguard. @example-architect decides.
- **O3.** Whether R2 reaches the subpackages of `net/http`, such as `net/http/httptest`. The rule assumes it names only
  `net/http`. The other answer is that it names every package under `net/http/`. @example-architect decides.
````

### File: docs/adr/README.md

````markdown
# Reading guide for the architecture decision records

The records in this directory carry numbered rules. This guide maps the rules to the code they constrain. The team
commits to ending every change to that code with the two trailers described below.

## Layers

A rule names the layer of the code it constrains.

| Layer | Paths |
| --- | --- |
| `token` | `internal/token/`, with the tests beside the code |
| `http` | `internal/http/`, with the tests beside the code |
| `entry point` | `cmd/token-gate/` |

These paths belong to no layer: `docs/adr/`, `AGENTS.md`, `.github/`, `.golangci.yml`, `go.mod`, and `go.sum`. A change
that adds a file that neither the layers nor this list cover extends one of them.

## Which records bind a change

`Accepted` records bind a change. `Proposed`, `Superseded`, and `Rejected` records do not. Records 0001 to 0011 have no
numbered rules, so a check reports them as unchecked.

## Reading the records

Before you change code under a layer, read **Terms**, **Rules**, **Confirmation**, and **Implementation notes** in each
accepted record whose rules name that layer. Anything that no rule states is your choice.

## Trailers

End the commit message and the pull request description of every change to code under a layer with two trailers:

```text
Implements: ADR-0012 R1
Defers: ADR-0012 R2 to #<issue number>
```

`Implements` lists the rules the change brings. `Defers` lists each rule the change leaves out, with the issue or pull
request that will bring it. The target must exist. Where no issue exists yet, leave the rule out of the trailers and
say in the description which rules wait for a change that has no issue. In a pull request with several commits, each
commit carries the trailers of its own part, and the description carries them for the whole change. A change that
brings no rule and leaves none out carries neither trailer.

## Checking a change

Check a change against the rules by following **Checking a change** in the `adr-authoring` skill (TBD: link to the
skill at the version this repository pins).
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- The records in `docs/adr/` govern the code under the paths that `docs/adr/README.md` maps. Read that guide before you
  change such code.
- End the commit message and the pull request description of such a change with the `Implements:` and `Defers:`
  trailers that the guide describes.
````

### Message to the user

I wrote ADR-0012, the reading guide `docs/adr/README.md`, and two bullets in `AGENTS.md`. I took your agreement to the `Implements:` and `Defers:` trailers as the commitment the guide needs, so I did not ask for it again.

Questions:

1. **Approval and status.** The record is `Proposed`, with no Date heading, because I don't know that @example-architect has approved it. Once they approve and the open points below are settled, I set `Accepted` and add the date.
2. **O1: test files.** Are `_test.go` files of a token package bound by R1 and R2? I assumed yes. Check whether `token-no-http` in `.golangci.yml` covers test files, because the answer decides whether the rules match the check.
3. **O2: indirect imports.** Do the rules cover imports through another package? I assumed they don't, which matches what depguard checks. The tool would still not build without the server if a token package imported a package that imports `net/http`.
4. **O3: `net/http` subpackages.** Does R2 cover `net/http/httptest` and the other subpackages? I assumed it names only `net/http`. Check how `token-no-http` matches the path.
5. **Skill link.** The guide has a `TBD` where it links to **Checking a change** in the `adr-authoring` skill. What is the URL, and which version does the repository pin?
6. **Layer map.** Please confirm the layer map in the guide: `token`, `http`, `entry point`, and the paths that belong to no layer.

This change touches only `docs/adr/` and `AGENTS.md`, which belong to no layer, so its commit message and pull request description need no trailers. Records 0001 to 0011 have no numbered rules, so a check reports them as unchecked. Rewriting them would make eleven new records, and I didn't do it.

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

Security architect, @example-security-architect: approves R1 and R2

#### Related ADRs

- [ADR-0012: Keep the token packages free of imports of the HTTP server and `net/http`](0012-token-packages-without-http.md):
  the `net/http` import rule (R2), which the Justification cites.
<!-- markdownlint-enable MD001 -->

## Context

The service checks the token of each request before policy evaluation, and `internal/token/verify` holds the check. A
token whose header names the algorithm `none` declares that it carries no signature, so the signature check has nothing
to compare. The security review decided how the service answers such a token.

## Decision

We will refuse every token whose header names the algorithm `none`. `internal/token/verify` returns the reason code
`TOKEN_ALG_NONE`, and the HTTP server answers with status 401.

### Terms

- **none algorithm**: the algorithm `none` named in a token header, matched case-insensitively.

### Rules

#### Refusal of a token that names the none algorithm

- **R1** (`token`). `internal/token/verify` returns an error that carries the reason code `TOKEN_ALG_NONE` for every
  token whose header names the none algorithm, whatever the signature, the claims, and the other header fields of that
  token are.
- **R2** (`http`). A request whose token has a header that names the none algorithm gets the HTTP status 401, and its
  response carries the reason code `TOKEN_ALG_NONE` in `<where the response carries the reason code>`.

### Implementation notes

Adds no requirement. Add a table test in `internal/token/verify` that passes headers naming `none`, with and without a
signature and in different letter cases, and expects the error of R1. Add a test of the HTTP server that sends such a
token and expects the status and the reason code of R2. When the tests land, add them to **Confirmation**.

### Justification

A token that names the none algorithm carries no signature, so verification cannot show who issued it (R1, R2).
`internal/token/verify` is a token package and so is bound by the `net/http` import rule of ADR-0012 R2. It returns an
error that carries the reason code (R1), and the code under `internal/http/` sets the status (R2).

## Consequences

Negative:

- No test covers R1 or R2 yet, so a change can break either rule without a failing check.

## Open points

- **O1.** How the header is matched against `none`. The rules assume a case-insensitive match, so `None` and `NONE` are
  refused as well. The other answer is that only the exact lowercase value is refused. @example-security-architect
  decides. This affects R1 and R2.
- **O2.** Which reason code a response carries when a token names the none algorithm and also fails another check, such
  as a malformed header or an expired claim. R1 assumes that `TOKEN_ALG_NONE` always wins. The other answer is that the
  first failing check in the order of the code wins. @example-security-architect decides. This affects R1 and R2.
- **O3.** Where the response carries the reason code, such as a field of the response body or a header. R2 holds a
  placeholder until this is decided. @example-security-architect decides. This affects R2.
````

### Message to the user

I wrote ADR-0013 as a new record. Nothing in ADR-0012 or the guide needs to change. The `token` and `http` layers already cover the code it constrains.

Questions:

1. **O3: reason code in the response.** Where does the 401 response carry the reason code: a field of the body, a header, or both? R2 holds the placeholder `<where the response carries the reason code>` until you answer. I did not guess, because I can't see how the service reports other reason codes.
2. **O1: letter case.** Is `None` or `NONE` also refused? I assumed yes, so R1 and R2 match case-insensitively.
3. **O2: precedence.** If a token names `none` and also fails another check, does `TOKEN_ALG_NONE` always win? I assumed yes.
4. **Status.** The record is `Proposed`, with no Date heading, until @example-security-architect approves and the open points are settled. Then I set `Accepted` and add the date.

I split the rule in two. `internal/token/verify` returns the error (R1), and `internal/http/` answers with the 401 (R2). ADR-0012 R2 keeps `net/http` out of the token packages, and the two parts can land in separate changes.

The Justification gives one reason: a token that names `none` carries no signature, so verification cannot show who issued it. The security review notes you gave me did not state a reason, so please correct it if the review reasoned differently.

The record has no **Confirmation** section because no test covers the rules yet. The change that adds the tests also adds the entries. A test-only change brings no rule and leaves none out, so it carries no trailers.

I wrote R1 and R2 as decisions, not defects, because no accepted record or contract settles the 401 and the reason code for this system. If the code for either rule is not in place yet, the change that adds it ends with `Implements: ADR-0013 R1, R2`, and `Defers:` names any rule it leaves out, with an issue that exists.
