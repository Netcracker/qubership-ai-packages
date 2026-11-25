## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner>

### Participants and approvers

- <role>, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**; this record adds one refusal to its verification.

## Context

ADR-0007 requires the service to verify every token before policy evaluation, and its rules state the result for an
expired token and for a token with no `kid`. They state no result for a token whose header `alg` is `none`. A JWT with
`alg` set to `none` is an unsecured JWT (RFC 7519, section 6): it carries no signature, so no key source can verify it.

## Decision

We will refuse every token whose `alg` is `none`, with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Refusal of unsigned tokens

- **R1** (`verify`). A token whose header `alg` is `none`, in any letter case, is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`. Where the token also meets the condition of the expiry check of ADR-0007 R4 or of the `kid`
  check of ADR-0007 R5, the reason code is `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` has no signature, so nothing binds its subject to a key source. Policy evaluation would
trust a subject that any caller can write (R1).

### Alternatives considered

- **A1. Refuse a token whose `alg` is `none` with the reason code of whichever check fails first.** Rejected by R1: the
  caller gets `TOKEN_ALG_NONE` whatever else is wrong with the token.

## Consequences

Negative:

- A token whose `alg` is `none` and that is also expired, or has no `kid`, gets `TOKEN_ALG_NONE` and not
  `TOKEN_EXPIRED` or `TOKEN_KID_MISSING` (R1).

## Open points

- **O1.** Does R1 cover `None` and `NONE`? R1 assumes it does. The other answer is the exact value `none` only. The
  owner of this record decides. It affects R1.
- **O2.** Which reason code wins for a token that meets R1 and the condition of ADR-0007 R4 or R5? R1 assumes
  `TOKEN_ALG_NONE`. The other answer is the code of the R4 or R5 check. The owner of this record decides. It affects R1.
````

### Message to the user

ADR-0007 is accepted, so I did not edit it. A new requirement goes into a new record. I drafted `docs/adr/0008-refuse-token-alg-none.md` with status `Proposed` and one rule, R1 in the `verify` layer.

When ADR-0008 is accepted, add its Date heading. Add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and says it adds the refusal of a token whose `alg` is `none`. Code that brings R1 can name `Implements: ADR-0008 R1` in its trailers.

Questions:

1. Who is the owner of ADR-0008, and who approves R1? The file has `<owner>` and `<role>, <account>` as placeholders until you answer.
2. Open point O1: does R1 also cover `None` and `NONE`? I assumed it does.
3. Open point O2: which reason code wins for a token that has `alg` `none` and is also expired or has no `kid`? I assumed `TOKEN_ALG_NONE`, because ADR-0007 R4 and R5 leave this open.

The record stays `Proposed` until O1 and O2 are settled.

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

I changed one line in ADR-0007. The link target under **Related ADRs** was `0006-key-sources.md` and is now `0006-trusted-key-sources.md`, which is `docs/adr/0006-trusted-key-sources.md` relative to the record. This is an editorial fix that changes no rule, so the accepted record can take it.

I could not open ADR-0006, so I left the link text `ADR-0006: Trust only listed key sources` as it was. Check that it matches the title of ADR-0006. The change touches no code under a layer, so the commit needs no `Implements` or `Defers` trailers.
