# Task

The user sends two requests about the record below. Handle each request on its own, starting from the repository as it
is described here, as if the other request did not exist.

For each request, give a heading `## Request 1` or `## Request 2`. Under it, give every file you would create or change
as a heading `### File: <path>`, followed by the file's full content in a fence of four backticks, and then a heading
`### Message to the user` with what you would tell the user. Ask nothing and wait for nothing: where you would ask the
user something, write the question in that message.

Request 1: "Add one requirement to ADR-0007: a token whose `alg` is `none` is refused with HTTP 401 and the reason code
`TOKEN_ALG_NONE`."

Request 2: "Fix the broken link in ADR-0007. The record it links to is `docs/adr/0006-trusted-key-sources.md`."

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- `docs/adr/` holds `0006-trusted-key-sources.md` and `0007-verify-every-token.md`; the next free number is 0008. Its
  `README.md` is the reading guide, copied from `adr-authoring 2.0.0`, and maps the layer `verify` to
  `internal/verify`.
- `docs/adr/0007-verify-every-token.md` reads, in full:

````markdown
# Verify every token in Authorization before policy evaluation

## Status

Accepted

### Date

2026-10-02

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0006: Trust only listed key sources](0006-key-sources.md): defines **key source**.

## Context

The service passes every request to policy evaluation, and policy evaluation trusts the subject of the token it
receives. A token that no one has verified lets any caller name any subject.

## Decision

We will verify the signature and the lifetime of every token before the request reaches policy evaluation.

### Terms

- **token**: the value after `Bearer ` in the `Authorization` header of a request.
- **key source**: as ADR-0006 defines it.

### Rules

#### Verification

- **R4** (`verify`). A token whose `exp` is earlier than the time of the check is refused with HTTP 401 and the reason
  code `TOKEN_EXPIRED`.
- **R5** (`verify`). A token whose header has no `kid` is refused with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

A verified signature binds the subject to a key source the service trusts (R5), and a lifetime check stops a token that
leaked earlier from working forever (R4).

### Alternatives considered

- **A1. Leave verification to policy evaluation.** Rejected by R4 and R5: policy evaluation would trust a subject that
  nothing checked.

## Consequences

Negative:

- A caller whose clock runs ahead of the issuer's gets `TOKEN_EXPIRED` near the end of a token's lifetime.
````
