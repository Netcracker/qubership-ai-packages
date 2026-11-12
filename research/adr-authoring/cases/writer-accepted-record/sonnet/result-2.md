## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose `alg` is `none`

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- Security architect, <approver account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and gives the `TOKEN_EXPIRED` check (R4) and the `TOKEN_KID_MISSING` check (R5) that R1 takes precedence
  over. This record adds R1 and replaces no statement of ADR-0007.

## Context

A token whose header `alg` is `none` carries no signature, so a caller can write any subject into it without holding a
key. ADR-0007 makes the service verify every token before policy evaluation, but its rules name only the `exp` check and
the `kid` check. A token with `alg` set to `none` can carry a `kid` and a future `exp`, and then it passes both checks.

## Decision

We will refuse every token whose header `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`, also where the token fails the `TOKEN_EXPIRED` check of ADR-0007 R4 or the `TOKEN_KID_MISSING` check
  of ADR-0007 R5.

### Justification

A token with `alg` set to `none` has no signature to verify, so refusing it by its header closes the way around the
checks of ADR-0007 (R1). The reason code names the cause even for a token that also fails another check, so a caller
learns that retrying with a fresh token or a `kid` does not help (R1).

### Alternatives considered

- **A1. Refuse a token with `alg` set to `none` only through the `kid` check of ADR-0007 R5.** Rejected by R1: such a
  token can carry a `kid`, and then the `kid` check passes it.

## Consequences

Negative:

- A token that is expired, or has no `kid`, and whose `alg` is `none` gets `TOKEN_ALG_NONE`, not `TOKEN_EXPIRED` or
  `TOKEN_KID_MISSING` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names ADR-0008 and the rule it adds.

## Open points

- **O1.** Which reason code a token gets when it fails R1 and also the check of ADR-0007 R4 or R5. This record assumes
  `TOKEN_ALG_NONE`. The other answer is the code of ADR-0007 R4 or R5. The owner of this record decides. It affects R1.
- **O2.** Whether R1 covers a header `alg` that differs from `none` only in letter case, such as `None` or `NONE`. The
  answers are the exact value `none` only, as R1 reads now, and every letter case. The owner of this record decides. It
  affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, `docs/adr/0008-refuse-token-alg-none.md`, with the status `Proposed` and no Date heading. When ADR-0008 is accepted, ADR-0007 gains one line under **Related ADRs** that names it. The record lists that line as a follow-up.

Questions for you:

- Who is the owner of ADR-0008, and who approves R1? I left `<owner account>` and `<approver account>` as visible placeholders. Should it be `@security-architect`, as in ADR-0007?
- O1: for a token with `alg` set to `none` that is also expired or has no `kid`, I assumed `TOKEN_ALG_NONE` wins. Do you want that, or the code of R4 or R5?
- O2: should R1 also cover `None` and `NONE`? As written, it covers the exact value `none` only.

The record stays `Proposed` until O1 and O2 are answered. R1 is tagged `verify`, which the README maps to `internal/verify`. A change that implements it ends its commit message and pull request description with `Implements: ADR-0008 R1`.

ADR-0007 also has a broken link to `0006-key-sources.md`. I did not touch it here. Request 2 fixes it.

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

I changed the link target under **Related ADRs** in ADR-0007 from `0006-key-sources.md` to `0006-trusted-key-sources.md`. ADR-0007 is `Accepted`, and a broken link is an editorial fix that changes no rule, so the record takes it. Nothing else in the file changed, and no trailers are needed.

I could not open ADR-0006, so I kept the link text `ADR-0006: Trust only listed key sources`. Check that it matches the title of that record.
