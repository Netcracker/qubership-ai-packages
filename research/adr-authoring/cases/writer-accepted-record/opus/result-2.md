## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and sets the refusals for lifetime (R4) and for a missing `kid` (R5) that R1 of this record yields to. This
  record adds a requirement to ADR-0007.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before the request reaches policy
evaluation. Its rules cover the lifetime of a token (R4) and a header with no `kid` (R5). No rule covers the signing
algorithm.

The header of a token names its signing algorithm in the `alg` parameter. RFC 7518, section 3.6, defines the value
`none` for a token that carries no signature. RFC 7515, section 4.1.1, makes `alg` values case-sensitive. A library that
takes the algorithm from the token's header and supports `none` accepts such a token without checking a signature.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation, with a reason code of its
own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Signing algorithm

- **R1** (`verify`). A token whose header has the `alg` value `none`, in any letter case, is refused with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`, except where ADR-0007 R4 or ADR-0007 R5 refuses the token.

### Justification

A token whose `alg` is `none` carries no signature, so nothing binds its subject to a key the service trusts (R1). A
reason code of its own lets an operator tell an unsigned token apart from a token with no `kid` (R1). R1 yields to
ADR-0007 R4 and R5, so this record adds a requirement and leaves the reason codes that ADR-0007 sets unchanged (R1).

### Alternatives considered

- **A1. Rely on the `kid` check of ADR-0007 R5 to refuse unsigned tokens.** Rejected by R1: a token whose `alg` is
  `none` and whose header has a `kid` passes R5 and reaches signature verification.

## Consequences

Negative:

- A token whose `alg` is `none` and that has expired or has no `kid` gets the reason code of ADR-0007 R4 or R5, not
  `TOKEN_ALG_NONE`. A count of `TOKEN_ALG_NONE` refusals therefore misses those tokens (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the
  requirement it adds.

## Open points

- **O1.** R1 assumes that `alg` is compared with `none` in any letter case, so `None` and `NONE` are refused too. The
  other answer is an exact, case-sensitive match, as RFC 7515 defines `alg` values. With that answer, `None` falls under
  no rule. The security architect decides. Affects R1.
- **O2.** R1 assumes that a token refused under ADR-0007 R4 or R5 keeps that rule's reason code. The other answer is
  that `TOKEN_ALG_NONE` takes precedence. That answer contradicts ADR-0007 R4 and R5 for these tokens, so this record
  would also have to replace those two rules (superseding part of ADR-0007) rather than narrow them from here. The
  security architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so it can't take a new requirement and stays as it is. I added the requirement as a new record instead: `docs/adr/0008-refuse-tokens-with-alg-none.md`, with status `Proposed`. Its single rule is ADR-0008 R1, which refuses the token with HTTP 401 and `TOKEN_ALG_NONE`.

Two open points keep the record at `Proposed`. I wrote R1 under an assumption for each:

- **O1:** I assumed `none` is matched in any letter case, so `None` and `NONE` are refused too. Should the match be case-insensitive, or exact as RFC 7515 defines `alg` values?
- **O2:** I assumed that a token ADR-0007 R4 (expired) or R5 (no `kid`) already refuses keeps that rule's reason code. Should `TOKEN_ALG_NONE` win instead? If so, ADR-0008 also has to replace ADR-0007 R4 and R5, because an accepted rule can't be narrowed from another record.

I set the owner and approver to @security-architect, the same as ADR-0007. Is that right for this record?

Once the record is accepted, it needs a `### Date` heading, and ADR-0007 needs a line under **Related ADRs** that points to it. That is listed as a follow-up.

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

I fixed the link in ADR-0007. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. Nothing else in the file changed.

ADR-0007 is accepted, but fixing a broken link changes no rule, so it is one of the edits an accepted record can take. It doesn't need a new record.

I couldn't check the title of ADR-0006 because I only had the filename. The link text still says "Trust only listed key sources". If ADR-0006's heading reads differently, should I change the link text to match it?
