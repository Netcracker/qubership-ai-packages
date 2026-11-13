## Request 1

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

- [ADR-0006: Trust only listed key sources](0006-key-sources.md): defines **key source**.

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
- **R6** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Justification

A verified signature binds the subject to a key source the service trusts (R5), and a lifetime check stops a token that
leaked earlier from working forever (R4). A token whose `alg` is `none` has no signature to verify, so R6 keeps it from
reaching policy evaluation.

### Alternatives considered

- **A1. Leave verification to policy evaluation.** Rejected by R4 and R5: policy evaluation would trust a subject that
  nothing checked.

## Consequences

Negative:

- A caller whose clock runs ahead of the issuer's gets `TOKEN_EXPIRED` near the end of a token's lifetime.
````

### Message to the user

I added R6 to the Verification rules in `docs/adr/0007-verify-every-token.md`. I numbered it R6 because R4 and R5 are the highest numbers in use. It carries the `verify` layer, which maps to `internal/verify`. I also added one sentence to the Justification so the new rule has a stated reason. I left the Status, Date, and Alternatives sections unchanged.

Two questions:

1. ADR-0007 is already Accepted, and its approver is @security-architect. Should this change go in as an edit to ADR-0007 with their re-approval, or as a new ADR-0008 that amends it? I made the edit you asked for.
2. The `Related ADRs` link still points to `0006-key-sources.md`, which does not match the file name `0006-trusted-key-sources.md`. I did not touch it here. Do you want it fixed in the same change?

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

I fixed the link in `Related ADRs` in `docs/adr/0007-verify-every-token.md`. The target was `0006-key-sources.md` and is now `0006-trusted-key-sources.md`. I changed nothing else in the file. I could not check the link by building the docs, because there is no checkout. I compared it against the file name you gave me.
