## Request 1

### File: docs/adr/0012-keep-http-out-of-token-packages.md

````markdown
# Keep HTTP out of the token packages

## Status

Accepted

<!-- markdownlint-disable MD001 -->
#### Date

2026-11-11

#### Owner

@example-architect

#### Participants and approvers

Architecture meeting. Approver: @example-architect

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

We plan a command-line tool, `tokencheck`, that verifies tokens offline. It has to build without the HTTP server, so the packages it links must not depend on the server.

## Decision

We will not import anything under `internal/http/`, or `net/http`, from any package under `internal/token/`.

### Justification

A package under `internal/token/` that imported either one would pull the HTTP server or `net/http` into every binary that links it. Without those imports, `internal/token/parse` and `internal/token/verify` build on their own, which `tokencheck` needs.

## Consequences

The depguard rule `token-no-http` in `.golangci.yml` checks both imports. CI runs it on every pull request, so a violation fails the build.

Code under `internal/token/` cannot write an HTTP response or choose a status code. That work stays in `internal/http/`.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Each file in this directory records one decision, numbered in the order it was accepted. The file name is the number followed by a short slug, for example `0012-keep-http-out-of-token-packages.md`.

## How to read a record

1. Read the title and the `Status` section. Only an accepted record is in force.
2. Read `Decision`. It states the rule in one or two sentences.
3. Read `Context` for the problem the decision answers, and `Justification` for the reasons.
4. Read `Consequences` for what the decision changes, including the lint rule or test that enforces it, where there is one.
5. Check `Related ADRs` for records that this one depends on or changes.

A newer record does not rewrite an older one. Where a decision changes, a new record says so and names the old one under `Related ADRs`.

## Writing a record

Copy the section layout of the latest record. Keep `Decision` to what the team agreed, and put the enforcement mechanism in `Consequences`.

## Linking code changes to records

End every change to code that a record governs with `Implements:` and `Defers:` trailers. The format is in `AGENTS.md`.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- End every commit that changes code governed by a record in `docs/adr/` with `Implements:` and `Defers:` trailers.
````

### Message to the user

I added `docs/adr/0012-keep-http-out-of-token-packages.md`, a reading guide at `docs/adr/README.md`, and a trailer rule in `AGENTS.md`.

The record is marked Accepted and dated 2026-11-11. @example-architect's approval of the pull request is what merges it. If you want it to sit as Proposed until then, say so.

I need two answers before the trailer rule is complete:

1. What does each trailer hold? I assumed `Implements:` names a record and `Defers:` names what the change leaves for later, but you didn't say. Should the value be `ADR-0012`, a file name, or free text? What goes in `Defers:` when nothing is deferred: `none`, or the trailer omitted?
2. Which code counts as "governed by the records"? I wrote "code governed by a record in `docs/adr/`", which is broad. Should it be narrowed to named paths, such as `internal/token/` for this record?

The reading guide has no index of records. I don't know the titles of `0001-` to `0010-`, and a partial index would go stale. If you want an index, send the titles or tell me to build it from the files.

## Request 2

### File: docs/adr/0013-refuse-tokens-with-algorithm-none.md

````markdown
# Refuse tokens that name the algorithm none

## Status

Accepted

<!-- markdownlint-disable MD001 -->
#### Date

2026-11-11

#### Owner

@example-security-architect

#### Participants and approvers

Security review. Approver: @example-security-architect

#### Related ADRs

0012
<!-- markdownlint-enable MD001 -->

## Context

A token whose header names the algorithm `none` declares that it carries no signature. A verifier that follows the header would accept such a token without checking anything.

## Decision

We will refuse a token whose header names the algorithm `none`. The service responds with HTTP 401 and the reason code `TOKEN_ALG_NONE`. The check sits in `internal/token/verify`.

### Justification

The header is supplied by the sender, so it cannot decide whether the token needs a signature. Refusing `none` in `internal/token/verify` applies the check to every caller of the verifier, including `tokencheck` once it exists.

## Consequences

ADR 0012 keeps `net/http` out of `internal/token/`, so `internal/token/verify` reports the reason code `TOKEN_ALG_NONE`, and `internal/http/` turns it into the 401 response.

No test covers the check yet.
````

### Message to the user

I added `docs/adr/0013-refuse-tokens-with-algorithm-none.md`. It is marked Accepted, dated 2026-11-11, and lists ADR 0012 as related, because the rule puts the check in a package that 0012 keeps free of HTTP.

Two statements in the record are inferences from 0012, not facts I checked in the code. One is that `internal/token/verify` returns the reason code and does not write the 401. The other is that `internal/http/` maps the code to the response. Please confirm both against the code, or tell me how the 401 is produced and I will correct the record.

The record says that no test covers the check. A test in `internal/token/verify` for an `alg: none` header would close that gap, but I have not seen the package's API or its existing tests, so I did not write one. Do you want it as a follow-up change? If so, its commit would carry the `Implements:` trailer for this record. The open questions about the trailer format from Request 1 still apply.
