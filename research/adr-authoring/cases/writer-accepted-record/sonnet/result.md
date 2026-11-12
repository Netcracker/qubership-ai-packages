## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose `alg` is `none`

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and refuses a token by `exp` (R4) and by `kid` (R5).

## Context

ADR-0007 has the service verify every token before policy evaluation, and policy evaluation trusts the subject of the
token it receives. ADR-0007 R4 and R5 cover `exp` and `kid`, and no rule there covers `alg`. RFC 7515 defines the `alg`
value `none` for an unsecured JWS, which carries no signature. A token with that value binds its subject to no key.

## Decision

We will refuse every token whose header `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`, also where the token meets the condition of the `TOKEN_EXPIRED` check of ADR-0007 R4 or of the
  `TOKEN_KID_MISSING` check of ADR-0007 R5.

### Justification

An unsigned token lets any caller name any subject, and policy evaluation would trust that subject (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` and leave the check to policy evaluation.** Rejected by R1: policy
  evaluation trusts the subject of the token it receives.

## Consequences

Negative:

- A caller that sends an unsigned token gets `TOKEN_ALG_NONE`, including where the token is also expired or has no
  `kid` (R1).

## Open points

- **O1.** Which `alg` values count as `none`: the exact string `none` only, or also `None` and `NONE`. The security
  architect decides. It affects R1.
- **O2.** Which reason code a token gets when it has `alg` `none` and also meets ADR-0007 R4 or R5. R1 assumes
  `TOKEN_ALG_NONE`. The alternative is the code of ADR-0007 R4 or R5. The security architect decides. It affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so it stays as it is. I wrote the requirement as a new `Proposed` record, ADR-0008, with R1 in the `verify` layer (`internal/verify`). The record links ADR-0007 under **Related ADRs**. Once ADR-0008 is accepted, add a line under ADR-0007's **Related ADRs** that names ADR-0008 and what it adds. That edit is allowed on an accepted record.

Questions:

1. Who is the owner (a GitHub account), and who approves R1? I left placeholders in **Owner** and **Participants and approvers**.
2. O1: does `alg` `none` also cover `None` and `NONE`? R1 now covers the exact string `none` only.
3. O2: a token with `alg` `none` that is also expired, or has no `kid`, could get either reason code. I assumed `TOKEN_ALG_NONE` wins and wrote that into R1. Say so if you want the ADR-0007 codes to win.

The record stays `Proposed` until O1 and O2 are settled, and I left the Date heading out until acceptance. The code change in `internal/verify` should end its commit message and pull request description with `Implements: ADR-0008 R1`. ADR-0007 also has a broken link, `0006-key-sources.md`. I did not fix it here.

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

I changed one thing in ADR-0007: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`, where it was `0006-key-sources.md`. A link fix changes no rule, so it is allowed on an accepted record. I did not open ADR-0006, so I kept the link text "Trust only listed key sources". Check that it matches the title of ADR-0006.
