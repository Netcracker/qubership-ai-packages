## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines **token**, and gives the rules R4 and R5 that this record's R2 refers to.

## Context

ADR-0007 requires every token to be verified before policy evaluation, and policy evaluation trusts the subject of the
token it receives. A token whose header `alg` is `none` declares that it carries no signature, so there is nothing to
verify, and any caller can name any subject in it.

## Decision

We will refuse every token whose header `alg` is `none`, before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Unsigned tokens

- **R1** (`verify`). A token whose header `alg` is `none`, in any letter case, is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`.
- **R2** (`verify`). A token that meets R1 and also meets ADR-0007 R4 or ADR-0007 R5 is refused with the reason code
  `TOKEN_ALG_NONE`.

### Justification

A token with no signature binds its subject to nothing, so the service refuses it outright (R1). One reason code per
refusal keeps the response predictable for a token that fails several rules (R2).

## Open points

- **O1.** Does R1 cover `alg` values such as `None` and `NONE`? R1 assumes it does. The security architect decides; the
  answer affects R1.
- **O2.** Which reason code does a token get when it is `alg: none` and also expired or without `kid`? R2 assumes
  `TOKEN_ALG_NONE`. The security architect decides; the answer affects R2.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, so I drafted ADR-0008 as `Proposed`. It links ADR-0007 under Related ADRs. When ADR-0008 is accepted, ADR-0007 gets a line under Related ADRs that names it. That is the only edit ADR-0007 takes, and it does not change a rule.

- **Owner:** I left a placeholder, `<GitHub account of the owner>`. Who owns ADR-0008?
- **Approver:** I assumed @security-architect approves, as in ADR-0007. Is that right?
- **O1:** I assumed `alg` is matched in any letter case, so `None` and `NONE` are refused too. Should R1 match only the exact value `none`?
- **O2:** I assumed a token that is `alg: none` and also expired, or without `kid`, gets `TOKEN_ALG_NONE` (R2). Should it get the reason code of ADR-0007 R4 or R5 instead?

The status stays `Proposed` until O1 and O2 are settled. There is no Date heading until acceptance.

ADR-0007's link to ADR-0006 looks broken, because it points at `0006-key-sources.md`. I left it alone here.

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

I changed the link target under Related ADRs from `0006-key-sources.md` to `0006-trusted-key-sources.md`. Nothing else changed. ADR-0007 is `Accepted`, and a broken-link fix is an editorial edit that changes no rule, so it can go in directly. I could not read ADR-0006, so I did not check that the link text, "Trust only listed key sources", matches its title. Please check that.
