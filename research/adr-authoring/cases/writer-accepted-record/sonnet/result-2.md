## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves the rule.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines **token**, and R4 and R5 can apply to the same token as R1 here.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before policy evaluation. Its rules cover an expired token (R4) and a token with no `kid` (R5). No rule covers a token whose header `alg` is `none`, which declares that the token carries no signature.

## Decision

We will refuse every token whose header `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`, including a token to which ADR-0007 R4 or R5 also applies.

### Justification

A token whose `alg` is `none` has no signature for the service to verify, so only a refusal keeps an unverified subject
away from policy evaluation (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` and leave it to policy evaluation.** Rejected by R1: policy evaluation would
  trust a subject that nothing checked.

## Consequences

Negative:

- A caller that sends a token with `alg` set to `none` gets `TOKEN_ALG_NONE`, even where that token is also expired or
  has no `kid`.

## Open points

- **O1.** Which reason code wins for a token that is `alg` `none` and also expired or without `kid`? R1 assumes
  `TOKEN_ALG_NONE`. The security architect decides. Affects R1.
- **O2.** Does R1 cover case variants of the value, such as `None` or `NONE`? R1 assumes only the exact value `none`.
  The security architect decides. Affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. The new requirement is a new record, `docs/adr/0008-refuse-token-alg-none.md`, with status `Proposed`. It links ADR-0007 under Related ADRs. When ADR-0008 is accepted, ADR-0007 gains a line under Related ADRs that names ADR-0008 R1.

Questions for you:
- Who is the owner, and who approves the rule? I left `<owner account>` and `<role>, <account>` as placeholders.
- O1: which reason code wins for a token that is `alg` `none` and also expired or without `kid`? I assumed `TOKEN_ALG_NONE`.
- O2: should `None` and `NONE` count as `none`? I assumed only the exact value `none`.

The status stays `Proposed` until both open points are settled. Add `### Date` on acceptance. The code change that implements the rule should carry `Implements: ADR-0008 R1`.

ADR-0007 also has a broken link to ADR-0006. I did not fix it here.

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

I changed one link target in the Related ADRs line, from `0006-key-sources.md` to `0006-trusted-key-sources.md`. No rule, status, or date changed, and an editorial fix like this is allowed on an accepted record. No `Implements` or `Defers` trailers are needed. I did not check the link text "Trust only listed key sources" against the title of ADR-0006, because I can't see that file.
