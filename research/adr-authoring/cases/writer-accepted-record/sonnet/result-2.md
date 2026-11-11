## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1 and R2.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and R4 and R5 refuse a token with other reason codes, so R2 here says which code wins.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before policy evaluation. Its
rules cover an expired token (R4) and a token with no `kid` (R5). It has no rule for a token whose `alg` is `none`, and
such a token declares that it carries no signature.

## Decision

We will refuse every token whose header `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none`, in any letter case, is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`.
- **R2** (`verify`). A token to which R1 and either ADR-0007 R4 or ADR-0007 R5 apply is refused with the reason code
  `TOKEN_ALG_NONE`.

### Justification

A token with `alg` `none` has no signature, so nothing binds its subject to a key source the service trusts (R1). A
caller that receives `TOKEN_ALG_NONE` learns the cause, and a caller that sent such a token would otherwise be told to
fix its `exp` or `kid` (R2).

### Alternatives considered

- **A1. Refuse a token whose `alg` is `none` with a reason code other than `TOKEN_ALG_NONE`.** Rejected by R1: the
  caller could not tell this refusal from the other refusals of ADR-0007.

## Consequences

Negative:

- A token whose `alg` is `none` and whose `exp` is earlier than the time of the check gets `TOKEN_ALG_NONE`, where
  ADR-0007 R4 alone would give `TOKEN_EXPIRED` (R2). The same holds for a token that has no `kid` (ADR-0007 R5).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the rule it
  adds.

## Open points

- **O1.** Letter case of `none`. R1 assumes that `None` and `NONE` count as `none`, because some JWT libraries accept
  them. The alternative is to match only the lowercase value `none`. The owner of this record decides; R1 is affected.
- **O2.** Precedence. R2 assumes that `TOKEN_ALG_NONE` wins over `TOKEN_EXPIRED` and `TOKEN_KID_MISSING`. The
  alternative is that ADR-0007 R4 and R5 win. The owner of this record decides; R2 is affected.
````

### Message to the user

ADR-0007 is `Accepted`, so it is final and I did not edit it. I put the requirement in a new `Proposed` record, ADR-0008 (`docs/adr/0008-refuse-tokens-with-alg-none.md`). When ADR-0008 is accepted, ADR-0007 gains one line under **Related ADRs** that names it.

Two things need your answer:

1. **Owner and approvers.** Who owns ADR-0008, and who approves R1 and R2? ADR-0007 lists `@security-architect`. If that person also approves this record, I will fill in both fields. Both are placeholders for now.
2. **Two assumptions I made.**
   - R1 treats `None` and `NONE` like `none` (O1).
   - I added R2, because a token with `alg` `none` can also be expired or lack a `kid`, and two rules would then give different codes. R2 makes `TOKEN_ALG_NONE` win (O2).

   Tell me if you want the other answer to either. The record stays `Proposed` until O1 and O2 are settled.

Separately, the link to ADR-0006 in ADR-0007 points to `0006-key-sources.md`, which does not exist. The file is `0006-trusted-key-sources.md`. A link fix is an allowed edit to an accepted record, and I can make it if you want.

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

I changed one thing in ADR-0007: the link under **Related ADRs** now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. A link fix changes no rule, so an accepted record takes it. I left the link text, the status, and every rule as they were.

`docs/adr/` maps to no layer in the reading guide, so this change owes no `Implements` or `Defers` trailers.
