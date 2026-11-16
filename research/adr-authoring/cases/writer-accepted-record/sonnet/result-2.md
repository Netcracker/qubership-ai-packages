## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose signing algorithm is none

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**; R1 takes precedence over R4 and R5 of ADR-0007.

## Context

RFC 7519 section 6 defines an unsecured token as one whose header `alg` is `none`. Such a token carries no signature, so
nothing binds its subject to a key. Policy evaluation trusts the subject of the token it receives, and ADR-0007 requires
every token to be verified before the request reaches it.

## Decision

We will refuse every token whose `alg` is `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose header `alg` is `none`, in any letter case, is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`, also where the token is expired or has no `kid`. R1 takes precedence over ADR-0007 R4 and
  ADR-0007 R5.

### Justification

A token with `alg` set to `none` has no signature to verify, so only a refusal keeps an unchecked subject away from
policy evaluation (R1). A single reason code for this case lets a caller tell it apart from an expired token or a token
without `kid` (R1).

### Alternatives considered

- **A1. Leave a token with `alg` set to `none` to the signature check.** Rejected by R1: a token with no signature gives
  that check nothing to compare, and the outcome would depend on how the check treats a missing signature.

## Consequences

Negative:

- A caller that sends an unsecured token, such as a test client, gets `TOKEN_ALG_NONE` and no other reason code (R1).
- A token with `alg` set to `none` that is also expired gets `TOKEN_ALG_NONE`, not `TOKEN_EXPIRED` (R1).

## Open points

- **O1.** Does R1 cover `none` in any letter case, such as `None` or `NONE`? R1 assumes it does. RFC 7519 compares
  `alg` values case-sensitively, so the alternative is to refuse only the exact value `none`. @security-architect
  decides. Affects R1.
- **O2.** Which reason code does a token get when R1 and ADR-0007 R4 or R5 both apply? R1 assumes that
  `TOKEN_ALG_NONE` wins. The alternative is to keep the order of ADR-0007 and let `TOKEN_EXPIRED` or
  `TOKEN_KID_MISSING` win. @security-architect decides. Affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, `docs/adr/0008-refuse-alg-none-tokens.md`, with the status `Proposed`. It links ADR-0007 under **Related ADRs**. Once ADR-0008 is accepted, ADR-0007 gains a line under **Related ADRs** that names ADR-0008 and what it adds.

Questions for you:

- Is `@security-architect` the owner and approver of ADR-0008? I copied it from ADR-0007, and I did not invent a different account.
- O1: should R1 refuse `None` and `NONE` as well as `none`? I assumed yes.
- O2: should `TOKEN_ALG_NONE` win over `TOKEN_EXPIRED` and `TOKEN_KID_MISSING` when both apply? I assumed yes, and R1 says so. Both open points keep the record `Proposed` until they are settled, and the Date heading is added on acceptance.

The change to `internal/verify` that implements this ends its commit message and pull request description with `Implements: ADR-0008 R1`.

Separately, ADR-0007 links `0006-key-sources.md`, but the file is `0006-trusted-key-sources.md`. I left that link alone here.

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

I changed the link target under **Related ADRs** from `0006-key-sources.md` to `0006-trusted-key-sources.md`. ADR-0007 is `Accepted`, and a broken link is an editorial fix that changes no rule, so the status, the Date, and every rule stay as they were.

I did not check the link text, "ADR-0006: Trust only listed key sources", against the heading of ADR-0006, because I can't see that file. If its title differs, tell me and I'll update the text.
