## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 to the verification rules of ADR-0007.

## Context

ADR-0007 decides that the service verifies every token before the request reaches policy evaluation. Its rules give a
response for the `exp` check (ADR-0007 R4) and for the `kid` check (ADR-0007 R5). No rule gives a response for a token
whose header sets `alg` to `none`.

RFC 7518, section 3.6, defines the `alg` value `none` for an Unsecured JWS, which carries no signature. Anyone can write
such a token, with any subject in it. RFC 7515, section 4.1.1, makes the `alg` value case-sensitive.

## Decision

We will refuse every token whose `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has `alg` set to `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`. Where the `exp` check of ADR-0007 R4 or the `kid` check of ADR-0007 R5 also refuses the token, the
  response carries `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` has no signature, so it binds its subject to no key source, and policy evaluation would
trust a subject that any caller chose (R1). A reason code of its own lets an operator tell a forged token from an
expired one in the logs (R1).

### Alternatives considered

- **A1. Refuse a `none` token with the reason code of another check, such as `TOKEN_KID_MISSING`.** Rejected by R1: the
  logs would show a forged token as a client that left out `kid`.

## Consequences

Negative:

- A dashboard or alert that counts `TOKEN_EXPIRED` or `TOKEN_KID_MISSING` stops counting a `none` token that is also
  expired or has no `kid`, because that token gets `TOKEN_ALG_NONE` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and says that it
  adds R1 to the verification rules.

## Open points

- **O1.** Which reason code a token gets when R1 and ADR-0007 R4 or R5 all refuse it. The answers are `TOKEN_ALG_NONE`,
  which R1 assumes, or the code of the ADR-0007 check. @security-architect decides. Affects R1.
- **O2.** Whether R1 also covers an `alg` that matches `none` only when case is ignored, such as `None` or `NONE`. The
  answers are an exact match only, which R1 assumes and which follows RFC 7515, or a case-insensitive match.
  @security-architect decides. Affects R1.
````

### Message to the user

I didn't edit ADR-0007. It's `Accepted`, and an accepted record takes no new requirement, so ADR-0007 stays as it is. The new requirement is R1 in a new record, `docs/adr/0008-refuse-tokens-with-alg-none.md`, with status `Proposed`. ADR-0008 links to ADR-0007 now. The link back from ADR-0007 gets added once ADR-0008 is accepted, and that step is listed under Follow-ups.

Two open points block acceptance. Could you or @security-architect answer them?

1. **O1:** If a `none` token is also expired or has no `kid`, which reason code should it get? I wrote R1 so that `TOKEN_ALG_NONE` wins. Is that right?
2. **O2:** Should `None` or `NONE` also count as `none`? R1 uses an exact match, as RFC 7515 does. Should it ignore case?

I made @security-architect the owner and the approver because they approve the rules of ADR-0007. Who should own and approve ADR-0008?

Separately, ADR-0007 has a broken link to ADR-0006 (`0006-key-sources.md`). Fixing it is an allowed edit to an accepted record if you want it done.

## Request 2

### File: docs/adr/0007-verify-every-token.md

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

- [ADR-0006: Trust only listed key sources](0006-trusted-key-sources.md): defines **key source**.

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

### Message to the user

I fixed the link in ADR-0007. It pointed to `0006-key-sources.md`, and it now points to `0006-trusted-key-sources.md`. Nothing else in the file changed. An accepted record can take a fix like this because it changes no rule, so ADR-0007 stays `Accepted` with its original date.

I left the link text, "ADR-0006: Trust only listed key sources", as it was. I couldn't open ADR-0006, so I couldn't check that this is still its title. Does it match the heading of `0006-trusted-key-sources.md`? If not, I'll change the text to match.
