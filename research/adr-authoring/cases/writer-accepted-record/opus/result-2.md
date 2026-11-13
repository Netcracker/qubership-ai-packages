## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token whose `alg` is `none` before policy evaluation

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. R1 adds a rule to its verification rules, and replaces its R4 and R5 for a token that R1 refuses.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before policy evaluation. Its
rules cover the `exp` of a token (R4) and the `kid` in its header (R5), and no rule covers the `alg` in its header. RFC
7518, section 3.6, defines the `alg` value `none` for an unsecured JWS, which carries no signature. A token with `alg`
set to `none`, a `kid`, and an `exp` later than the time of the check meets ADR-0007 R4 and R5.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has an `alg` value equal to `none`, compared without regard to case, is
  refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or R5 also applies to the token, R1
  takes precedence, and the token gets `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` carries no signature, so the subject it names is bound to no key source, and any caller
could name any subject (R1). The case-insensitive comparison also covers `None` and `NONE`, which some JWT libraries
have treated as unsecured (R1). The `exp` and the `kid` of such a token are unsigned, so a refusal on either of them
would report a value that no one has verified. `TOKEN_ALG_NONE` takes precedence for that reason (R1).

### Alternatives considered

- **A1. Leave tokens with `alg` set to `none` to the `exp` and `kid` checks of ADR-0007.** Rejected by R1: a token with
  `alg` set to `none`, a `kid`, and a future `exp` passes both checks.

## Consequences

Negative:

- A token with `alg` set to `none` that ADR-0007 R4 or R5 refused with `TOKEN_EXPIRED` or `TOKEN_KID_MISSING` gets
  `TOKEN_ALG_NONE` instead (R1). A client or a dashboard that matches the old reason codes sees the new one for these
  tokens.

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record, R1, and the
  replacement of R4 and R5 for a token that R1 refuses.

## Open points

- **O1.** Does R1 match `alg` without regard to case, so that `None` and `NONE` are refused too, or only the exact
  value `none`? R1 assumes the comparison ignores case. @security-architect decides. Affects R1.
- **O2.** When a token with `alg` set to `none` also meets the condition of ADR-0007 R4 or R5, which reason code does
  it get: `TOKEN_ALG_NONE`, or the reason code of ADR-0007 R4 or R5? R1 assumes `TOKEN_ALG_NONE`. If ADR-0007 takes
  precedence, R1 no longer replaces R4 and R5, and the line under **Related ADRs** and the **Negative** consequence
  go. @security-architect decides. Affects R1.
````

### Message to the user

I left ADR-0007 unchanged because it is `Accepted`, and a requirement added to an accepted record has to go into a new record. I wrote the new requirement as ADR-0008 R1 in `docs/adr/0008-refuse-tokens-with-alg-none.md`, with the status `Proposed`. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** pointing back to it. That's listed as a follow-up.

Before ADR-0008 can be accepted, please answer these:

1. **Owner and approver:** I used @security-architect for both, as in ADR-0007. Is that right?
2. **O1:** Should `None` and `NONE` be refused the same way as `none`? R1 assumes yes, because some JWT libraries have treated those spellings as unsecured.
3. **O2:** A token with `alg` set to `none` often has no `kid`, and it might also be expired. Should it get `TOKEN_ALG_NONE` or the reason code from ADR-0007 R4 or R5? R1 assumes `TOKEN_ALG_NONE`. That choice partly replaces ADR-0007 R4 and R5 for these tokens, and the record says so.

Separately, the ADR-0006 link in ADR-0007 points to `0006-key-sources.md`, but that file doesn't exist. Fixing the link is an editorial change that the accepted record can take directly.

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

I fixed the link in ADR-0007. Under **Related ADRs**, it now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`, which doesn't exist. No rule changed, so this is an editorial fix that an accepted record can take directly, and no new record is needed.

I kept the link text "ADR-0006: Trust only listed key sources" as it was, but I couldn't see the heading of `0006-trusted-key-sources.md`. If that heading reads differently, should the link text be changed to match it?
