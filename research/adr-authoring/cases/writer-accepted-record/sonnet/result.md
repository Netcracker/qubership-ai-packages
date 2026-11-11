## Request 1

### File: docs/adr/0008-refuse-token-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): adds R1 to the
  rules of ADR-0007 and replaces none of them. Defines **token**.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before policy evaluation. Its
rules R4 and R5 name the outcome for an expired token and for a token with no `kid`. They name no outcome for a token
whose `alg` is `none`, a value that declares the token unsigned.

## Decision

We will refuse every token whose `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.
- **alg**: the `alg` parameter in the header of a token.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Justification

A token that declares itself unsigned carries no signature that a key source could bind to its subject. Refusing it
with its own reason code (R1) lets a caller and an operator tell it apart from an expired token or a token with no
`kid`.

## Open points

- **O1.** Which spellings of `none` R1 covers. R1 is written for the exact value `none`. The answers are to cover only
  that value, or to cover every capitalization, such as `None` and `NONE`. @security-architect decides. It affects R1.
- **O2.** Which reason code a token gets when R1 and a rule of ADR-0007 both apply, such as a token whose `alg` is `none`
  and whose `exp` is earlier than the time of the check. The answers are `TOKEN_ALG_NONE`, or the reason code of the
  ADR-0007 rule. @security-architect decides. It affects R1 and ADR-0007 R4 and R5.
````

### Message to the user

ADR-0007 is `Accepted`, so it stays as it is. I put the requirement in a new record, ADR-0008, with status `Proposed`. R1 holds your rule, tagged `verify` as the reading guide maps it to `internal/verify`. ADR-0008 links ADR-0007 under **Related ADRs**. Once ADR-0008 is accepted, ADR-0007 gets a line under **Related ADRs** that names ADR-0008 and R1, and I can add that line then.

Questions before acceptance:

1. Who owns ADR-0008, and who approves R1? I assumed `@security-architect`, the owner of ADR-0007. Please confirm or give another account.
2. O1: does R1 cover only the exact value `none`, or also `None` and `NONE`? I wrote it for the exact value.
3. O2: which reason code does a token get when it has `alg` `none` and is also expired or has no `kid`? I left this open and did not choose.

The record has no **Date** heading until it is accepted. It has no **Confirmation** section because no check exists yet. Code in `internal/verify` that brings R1 should end its commit message and pull request description with `Implements: ADR-0008 R1`.

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

I changed one thing in ADR-0007: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`, where it was `0006-key-sources.md`. This is an editorial fix that changes no rule, so an accepted record takes it. The rest of the record is unchanged, including the status and the date.

I kept the link text "Trust only listed key sources" because I can't see the title of ADR-0006. Please check that it matches the title there.
