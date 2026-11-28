## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

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
  **token**. R1 adds a requirement to its Verification rules, R4 and R5.

## Context

ADR-0007 requires the service to verify every token before the request reaches policy evaluation. ADR-0007 R4 refuses
a token whose `exp` has passed, and ADR-0007 R5 refuses a token whose header has no `kid`. No rule of ADR-0007 refuses a
token whose header sets `alg` to `none`.

RFC 7518, section 3.6, defines `none` as the `alg` value of an unsecured JWS, whose signature is empty. RFC 7515,
section 4.1.1, makes the `alg` value a case-sensitive string.

## Decision

We will refuse every token whose header sets `alg` to `none`, and give the refusal a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has `alg` set to `none`, in any letter case, is refused with HTTP 401 and the
  reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or ADR-0007 R5 also refuses the token, the reason code that rule sets
  wins.

### Justification

A token whose `alg` is `none` has no signature. Nothing binds its subject to a key source, and policy evaluation would
trust a subject that no one checked (R1). With its own reason code, a caller or an operator can tell this refusal apart
from an expired token or a token without `kid` (R1). Existing callers keep the same answer for an expired token or a
token without `kid`, because the reason codes of ADR-0007 R4 and R5 win (R1).

### Alternatives considered

- **A1. Refuse a token whose `alg` is `none` as a failed signature check, with no reason code of its own.** Rejected by
  R1: the reason code would not name the cause of the refusal.

## Consequences

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and the requirement
  that ADR-0008 R1 adds.

## Open points

- **O1.** R1 assumes that `alg` matches `none` in any letter case, so `None` and `NONE` are refused as well. The other
  answer is an exact, case-sensitive match on `none`, which is how RFC 7515 compares `alg` values. @security-architect
  decides. Affects R1.
- **O2.** R1 assumes that when ADR-0007 R4 or ADR-0007 R5 also refuses a token, the reason code from ADR-0007 wins over
  `TOKEN_ALG_NONE`. The other answer is that `TOKEN_ALG_NONE` wins. This record would then replace part of ADR-0007 R4
  and R5, and would have to name that replacement under **Related ADRs**. @security-architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement. I wrote the requirement as R1 of a new record, `docs/adr/0008-refuse-alg-none-tokens.md`, with the status `Proposed`. It links to ADR-0007 under **Related ADRs** and uses ADR-0007's definition of **token**.

Two open points keep ADR-0008 at `Proposed`. Please answer them:

- **O1:** Should `None` and `NONE` also be refused with `TOKEN_ALG_NONE`, or only the exact value `none`? R1 assumes any letter case.
- **O2:** A token can have `alg: none` and also be expired or have no `kid`. Which reason code should it get in that case? R1 assumes the ADR-0007 code wins (`TOKEN_EXPIRED` or `TOKEN_KID_MISSING`). If `TOKEN_ALG_NONE` should win instead, ADR-0008 would replace part of ADR-0007 R4 and R5, and I'd record that.

I made @security-architect the owner and approver, the same as ADR-0007. Is that right?

When ADR-0008 is accepted, it gets a Date heading. ADR-0007 then gets a line under **Related ADRs** that points to ADR-0008, as the Follow-ups section says.

One gap in ADR-0007: its Decision says the service verifies every token's signature, but none of its rules requires that. Only R4 (`exp`) and R5 (`kid`) are rules. Do you want a separate record that requires a valid signature?

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

I fixed the ADR-0006 link in ADR-0007 under **Related ADRs**. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. An accepted record can take an editorial fix that changes no rule, so ADR-0007 stays `Accepted` and nothing else in it changed. I left the link text, "ADR-0006: Trust only listed key sources", as it was, so check that it matches the title in `0006-trusted-key-sources.md`.
