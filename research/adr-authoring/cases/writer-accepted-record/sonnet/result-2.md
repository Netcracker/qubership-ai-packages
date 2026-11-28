## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose `alg` is `none`

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): adds R1 to its
  requirements, defines **token**, and has R4 and R5, the expiry and `kid` refusals that R1 takes precedence over.

## Context

ADR-0007 requires the service to verify the signature of every token before policy evaluation. A token whose header
declares the algorithm `none` declares that it carries no signature. ADR-0007 R4 and R5 refuse a token that is expired
or has no `kid`, and no rule of ADR-0007 names a token whose `alg` is `none`.

## Decision

We will refuse every token whose `alg` header parameter is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Refusal

- **R1** (`verify`). A token whose `alg` header parameter is the string `none` is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or R5 also refuses the same token, the response carries `TOKEN_ALG_NONE`.

### Justification

A token with no signature binds its subject to no key source, so the service refuses it on its `alg` alone, whether or
not it has a `kid` and an unexpired `exp` (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` when it has a `kid` and an `exp` in the future.** Rejected by R1: nothing
  checked the subject of such a token.

## Consequences

Negative:

- A caller that sends a token whose `alg` is `none` is refused with `TOKEN_ALG_NONE`, also where the token has a `kid`
  and an unexpired `exp` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names ADR-0008 and R1 as an added
  requirement.

## Open points

- **O1.** Which spellings of `none` R1 covers. R1 assumes that only the exact lowercase string `none` counts, as in the
  JWA algorithm registry. The alternative is to also refuse `None` and `NONE`. The security architect decides. This
  affects R1.
- **O2.** Which reason code a token gets where `alg` is `none` and ADR-0007 R4 or R5 also refuses it. R1 assumes
  `TOKEN_ALG_NONE`. The alternative is to leave the order to the implementation. The security architect decides. This
  affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, and I drafted `docs/adr/0008-refuse-alg-none-tokens.md` as `Proposed` with the rule as R1 (`verify`, which maps to `internal/verify`). ADR-0007 stays as it is for now. When ADR-0008 is accepted, ADR-0007 gains one line under **Related ADRs** that names ADR-0008 and R1. That is an edit an accepted record takes.

Questions:

1. Who owns ADR-0008? I left a placeholder in **Owner**, because I can't tell your GitHub account from the information I have.
2. Is @security-architect the approver of R1? I assumed so, because they approve the rules of ADR-0007.
3. Open points O1 and O2 block acceptance:
   - O1: does R1 cover only the exact string `none`, or also `None` and `NONE`?
   - O2: which reason code does a token get when it has `alg` set to `none` and is also expired or has no `kid`? I wrote that `TOKEN_ALG_NONE` wins.

The change to `internal/verify` can end its commit message and pull request description with `Implements: ADR-0008 R1`. Naming a `Proposed` rule is allowed. No check exists yet, so **Confirmation** has no entry. Add one when a test for R1 lands.

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

I changed one thing in ADR-0007: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`, where it was `0006-key-sources.md`. This is an editorial fix that an accepted record takes, and no rule, status, or date changed.

I could not open ADR-0006, so I did not check that the link text "ADR-0006: Trust only listed key sources" matches its title. Compare the two when you review.
