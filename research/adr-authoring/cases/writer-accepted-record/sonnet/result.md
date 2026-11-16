## Request 1

### File: docs/adr/0008-refuse-token-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- <role>, <GitHub account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and sets the refusals of R4 and R5 that R1 takes precedence over.

## Context

The service passes every request to policy evaluation, and policy evaluation trusts the subject of the token it
receives. The header of a token names its signing algorithm in `alg`. RFC 7518 section 3.6 registers the value `none`
for a token with no signature. A verifier that takes the algorithm from the token header treats such a token as
correctly signed.

## Decision

We will refuse every token whose `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.
- **alg**: the value of the `alg` parameter in the header of a token.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`, also
  where the token is expired or has no `kid`. Where a token's `alg` is `none` and ADR-0007 R4 or ADR-0007 R5 also
  applies to it, this rule decides the reason code.

### Justification

A token with `alg` set to `none` carries no signature, so nothing binds its subject to a key source. The refusal stops
a caller from naming any subject by choosing that value (R1).

### Alternatives considered

- **A1. Leave an unsigned token to the signature check.** Rejected by R1: a verifier that reads the algorithm from the
  token header accepts `none` as a valid choice, so the signature check passes the token.

## Consequences

Negative:

- A caller that sends unsigned tokens, such as a test client, gets HTTP 401 with `TOKEN_ALG_NONE`.
- A token with `alg` set to `none` that is also expired or has no `kid` gets `TOKEN_ALG_NONE`, not `TOKEN_EXPIRED` or
  `TOKEN_KID_MISSING` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names ADR-0008 and the refusal it
  adds.

## Open points

- **O1.** Does a case variant of `none`, such as `None` or `NONE`, count as `none`? The record assumes only the exact
  value `none` counts. The security architect decides. Affects R1.
- **O2.** Which reason code does a token get that has `alg` set to `none` and is also expired or has no `kid`? The
  record assumes `TOKEN_ALG_NONE`. The security architect decides. Affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so it stays as it is. I put the requirement in a new `Proposed` record, ADR-0008, as rule R1 in the `verify` layer.

Questions for you:
- Who is the owner and who approves ADR-0008? I left `<owner GitHub account>` and `<role>, <GitHub account>` as placeholders in the file. ADR-0007 names `@security-architect`. Is that the owner here too?
- Does a case variant such as `None` or `NONE` count as `none`? I assumed only the exact value counts (open point O1).
- Which reason code should a token get when its `alg` is `none` and it is also expired or has no `kid`? I assumed `TOKEN_ALG_NONE` wins, which R1 states (open point O2).

The record stays `Proposed` until both open points are settled and the team signs off. After that, ADR-0007 gets one line under **Related ADRs** that names ADR-0008. I did not add that line now.

Code that implements R1 ends its commit message and pull request description with `Implements: ADR-0008 R1`.

Separately, the link to ADR-0006 in ADR-0007 points at `0006-key-sources.md`, and the file is named `0006-trusted-key-sources.md`. I did not touch it in this request.

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

I changed one thing: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`. ADR-0007 is `Accepted`, and a broken link is an editorial fix that changes no rule, so editing it in place is allowed. No rule, status, or date changed.

I could not read ADR-0006, so I kept the link text `ADR-0006: Trust only listed key sources` as it was. Compare it with the title of that record. The fix touches no code, so the commit needs no `Implements` or `Defers` trailer.
