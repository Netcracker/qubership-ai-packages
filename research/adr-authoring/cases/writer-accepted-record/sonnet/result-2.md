## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token whose alg is none

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- <role, account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record replaces the reason code that R4 and R5 give to a token whose `alg` is `none`.

## Context

A token whose header `alg` is `none` is an unsecured JWT: it carries no signature (RFC 7519, section 6). ADR-0007
verifies the signature and the lifetime of every token, and it states no rule for the `alg` header parameter.

## Decision

We will refuse every token whose `alg` is `none` with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is the string `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`. Where ADR-0007 R4 or R5 also applies to that token, the reason code is `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` has no signature, so nothing binds its subject to a key source (R1). Giving the refusal
one reason code regardless of the other checks lets a caller and a log reader recognize it (R1).

## Consequences

Negative:

- A token whose `alg` is `none` and whose `exp` is also in the past gets `TOKEN_ALG_NONE`, where ADR-0007 R4 alone
  would give it `TOKEN_EXPIRED` (R1).

## Open points

- **O1.** Does R1 cover a value that differs from `none` only in letter case, such as `None` or `NONE`? R1 is written
  as an exact, case-sensitive match. The answers under consideration are exact match only and a case-insensitive
  match. The owner decides. It affects R1.
- **O2.** Which reason code does a token get when `alg` is `none` and ADR-0007 R4 or R5 also applies? R1 is written
  with `TOKEN_ALG_NONE` winning. The other answer is that R4 or R5 wins, and then R1 loses its second sentence. The
  owner decides. It affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, `docs/adr/0008-refuse-tokens-with-alg-none.md`, with the status `Proposed` and rule R1 in the `verify` layer (`internal/verify`). ADR-0007 stays as it is. When ADR-0008 is accepted, two edits follow: add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and what it replaces, and add the Date heading to ADR-0008.

Questions:

1. Who owns ADR-0008, and who approves R1? I left `<owner GitHub account>` and `<role, account>` as placeholders.
2. O1: should R1 also match `None` and `NONE`? I wrote an exact, case-sensitive match.
3. O2: when `alg` is `none` and the token is also expired or has no `kid`, I assumed `TOKEN_ALG_NONE` wins, since a request needs one reason code. Is that right?

The record stays `Proposed` until O1 and O2 are settled. Code that implements R1 can end its commit message and pull request description with `Implements: ADR-0008 R1`.

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

I changed one thing in `docs/adr/0007-verify-every-token.md`: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`, where it was `0006-key-sources.md`. ADR-0007 is `Accepted`, and a broken-link fix is an editorial edit that changes no rule, so the record takes it directly. No new record is needed.

I did not touch the link text, because I cannot see ADR-0006's title. Check that "Trust only listed key sources" matches the heading of `0006-trusted-key-sources.md`. The change is in `docs/adr/`, which maps to no layer, so the commit owes no `Implements` or `Defers` trailers.
