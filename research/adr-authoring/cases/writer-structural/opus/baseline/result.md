## Request 1

### File: docs/adr/0012-token-packages-without-http.md

````markdown
# Keep token packages free of HTTP imports

## Status

Accepted

<!-- markdownlint-disable MD001 -->
#### Date

2026-11-11

#### Owner

@example-architect

#### Participants and approvers

Architecture meeting; approved by @example-architect

#### Related ADRs

None
<!-- markdownlint-enable MD001 -->

## Context

We plan a command-line tool, `tokencheck`, that verifies tokens offline. It needs the packages under `internal/token/`,
and it has to build without the HTTP server.

## Decision

We will keep every package under `internal/token/` free of imports from `internal/http/` and from `net/http`.

The depguard rule `token-no-http` in `.golangci.yml` checks both imports. CI runs it on every pull request.

### Justification

With neither import, the token packages build without the HTTP server, so `tokencheck` can use them as they are.

## Consequences

Code that turns a token result into an HTTP response, such as a status code, lives in `internal/http/`.

A pull request that adds either import to a package under `internal/token/` fails the lint job.

depguard checks the imports that each package lists. If a token package imports some other package that imports
`net/http`, the rule passes.
````

### File: docs/adr/README.md

````markdown
# Architecture decision records

Each record in this directory states one decision about token-gate, the reason for it, and what follows from it. The
number in the file name gives the order in which the records were accepted, so `0001-` is the oldest.

## Read a record

Every record uses the same sections:

| Section | What it holds |
| --- | --- |
| Status | Whether the decision applies. Every record here is `Accepted`. |
| Date | The day the decision was recorded. |
| Owner | The person to ask about the decision. |
| Participants and approvers | Who made the decision, and who approved it. |
| Related ADRs | Records this one depends on or changes, or `None`. |
| Context | The problem the decision solves. |
| Decision | What we decided, starting with "We will". |
| Justification | Why we chose this option. |
| Consequences | What follows from the decision, including its costs. |

A record governs the code its Decision names. For example, ADR-0012 governs the packages under `internal/token/`, and
ADR-0011 governs every place that writes a log record.

## Mark changes to governed code

End every commit that changes code a record governs with two trailers:

- `Implements:` lists the records whose decisions the change follows.
- `Defers:` lists the records whose decisions the change leaves unmet in that code, each with the reason in
  parentheses.

Name a record as `ADR-` followed by its four-digit number, and separate several records with commas. Write `none` where
a trailer has no record to list. Both trailers appear on every such commit, `none` included, so a missing trailer shows
that the author skipped the step.

```text
feat(verify): add the expiry check to token verification

Implements: ADR-0012
Defers: ADR-0011 (the check logs in plain text until the logger moves)
```

To list the changes made under a record, search the commit messages:

```bash
git log --grep='ADR-0012'
```

## Add a record

1. Copy the newest record and give the copy the next number.
2. Fill in every section. Write `None` under Related ADRs if the record depends on no other.
3. Get the approval of the people listed under Participants and approvers before you merge.
````

### File: AGENTS.md

````markdown
# Agent instructions

- Run `go test ./...` and `golangci-lint run` before you commit.
- Write commit messages in Conventional Commits.
- Before you change code that a record in `docs/adr/` governs, read the record. End the commit message with the
  `Implements:` and `Defers:` trailers that `docs/adr/README.md` describes.
````

### Message to the user

I added ADR-0012, which records that packages under `internal/token/` must not import `internal/http/` or `net/http`. It follows the same template as 0011, is dated 2026-11-11, and names @example-architect as the owner and approver.

I also added `docs/adr/README.md` as the reading guide. It covers the record sections, which code a record governs, the `Implements:` and `Defers:` trailers, and how to add a record. `AGENTS.md` now points to the guide for the trailers.

I have three questions:

1. **Who attended the meeting?** Under Participants and approvers I wrote only "Architecture meeting" and the approver. Should I list anyone else?
2. **Is this trailer format right?** I chose `ADR-0012` as the value and `none` when there is nothing to list, so `git log --grep` can find every change made under a record. The meeting didn't set a format, so please confirm it or tell me what you want instead.
3. **Do you want an index of records in the guide?** I left it out because I can't see the titles of 0001–0010, and I didn't want to make them up.

One limit of the rule is in the record's Consequences. depguard only checks the packages a token package imports directly. If a token package imports another package that imports `net/http`, the lint still passes. I haven't seen `.golangci.yml`, so the record describes `token-no-http` the way you described it.

If `tokencheck` has to be safe from indirect imports too, I can add a CI step that fails when `go list -deps ./internal/token/...` includes `net/http`. Do you want that?

## Request 2

### File: docs/adr/0013-refuse-alg-none.md

````markdown
# Refuse tokens that name the `none` algorithm

## Status

Accepted

<!-- markdownlint-disable MD001 -->
#### Date

2026-11-11

#### Owner

@example-security-architect

#### Participants and approvers

Security review; approved by @example-security-architect

#### Related ADRs

ADR-0012
<!-- markdownlint-enable MD001 -->

## Context

A token header names the algorithm that signed the token. The algorithm `none` marks a token with no signature, so
anyone can write a token that names it.

## Decision

We will refuse every token whose header names the algorithm `none`.

The check is in `internal/token/verify`. A request that carries such a token gets HTTP status 401 with the reason code
`TOKEN_ALG_NONE`.

### Justification

With the check in `internal/token/verify`, every caller of the package refuses these tokens, not only the HTTP server.
The separate reason code lets a client or an operator tell this refusal apart from other 401 responses.

## Consequences

Under ADR-0012, `internal/token/verify` cannot import `net/http`. The package reports the refusal, and code in
`internal/http/` maps it to the 401 response.

When this record was accepted, no test covered the check, so a change that removes it would still pass CI.
````

### Message to the user

I added ADR-0013, which records that a token naming the algorithm `none` is refused with HTTP 401 and `TOKEN_ALG_NONE`. The owner and approver is @example-security-architect. It links to ADR-0012 because the check is in `internal/token/verify`, and that package can't import `net/http`. Because of that, the record says the 401 mapping happens in `internal/http/`.

I have two questions:

1. **Is the 401 mapping in the right place?** I haven't seen the code. Is the mapping to 401 and `TOKEN_ALG_NONE` in `internal/http/`, or somewhere else?
2. **Does the check ignore case?** Forged tokens often use `None` or `NONE`. If `verify` refuses those too, the Decision should say so. If it only refuses the exact string `none`, that is a gap the security review should look at.

The record says that no test covers the check, which means CI would still pass if someone removed it. Do you want me to write that test? Its commit would end with `Implements: ADR-0013` and `Defers: none`.
