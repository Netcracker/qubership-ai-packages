## Request 1

### File: docs/adr/0008-refuse-unsecured-tokens.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1, and its R2 replaces ADR-0007 R4 and R5 for an unsecured token.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before the request reaches policy
evaluation. ADR-0007 R4 refuses a token that has expired, and ADR-0007 R5 refuses a token whose header has no `kid`. A
JWS whose header sets `alg` to `none` carries no signature (RFC 7518, section 3.6). No rule of ADR-0007 names the status
or the reason code that the service returns for such a token.

## Decision

We will refuse every token whose header sets `alg` to `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.
- **unsecured token**: a token whose JOSE header has an `alg` parameter with the value `none`, compared
  case-sensitively as RFC 7515, section 4.1.1, requires.

### Rules

#### Unsecured tokens

- **R1** (`verify`). An unsecured token is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`.
- **R2** (`verify`). Where an unsecured token also meets the condition of ADR-0007 R4 or ADR-0007 R5, the refusal
  carries the reason code `TOKEN_ALG_NONE`, not the reason code of that rule.

### Justification

An unsecured token has no signature, so a service that accepts it lets any caller name any subject, which is the problem
ADR-0007 addresses (R1). A reason code of its own lets an operator tell an attempt to skip the signature check apart
from a malformed or stale token (R1). An unsecured token is the more serious defect of a token that also has expired or
lacks a `kid`, so its reason code is the one the refusal carries (R2).

### Alternatives considered

- **A1. Refuse an unsecured token as a failed signature check, with a reason code that every invalid signature
  shares.** Rejected by R1: an operator could not tell an unsecured token apart from a token signed with the wrong key.
- **A2. Report `TOKEN_EXPIRED` or `TOKEN_KID_MISSING` where ADR-0007 R4 or R5 also applies.** Rejected by R2: the
  reason code would hide that the token carried no signature.

## Consequences

Negative:

- An unsecured token that has no `kid` gets `TOKEN_ALG_NONE` instead of `TOKEN_KID_MISSING`, and an unsecured token
  that has expired gets `TOKEN_ALG_NONE` instead of `TOKEN_EXPIRED` (R2). A caller that matches on either of those
  codes sees a different code for these tokens.

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names this record, R1 as an added
  rule, and R2 as the replacement of ADR-0007 R4 and R5 for an unsecured token.

## Open points

- **O1.** Which reason code an unsecured token gets when ADR-0007 R4 or R5 also applies. The possible answers are
  `TOKEN_ALG_NONE`, which R2 assumes, or the reason code of ADR-0007 R4 or R5. The security architect decides. This
  affects R2.
````

### Message to the user

ADR-0007 is `Accepted`, so I can't add a requirement to it, and its text stays as it is. The new rule is in a new record, `docs/adr/0008-refuse-unsecured-tokens.md`, with the status `Proposed`. It links back to ADR-0007 under **Related ADRs**. ADR-0007 gets a line pointing to ADR-0008 only once ADR-0008 is accepted. That step is listed under **Follow-ups**.

R1 is the rule you asked for. I also added R2, because a token whose `alg` is `none` can also have no `kid` or be expired, and then ADR-0007 R5 or R4 applies too. Without a precedence rule, a checker can't tell which reason code is correct.

Two questions:

1. **Which reason code wins?** Should such a token get `TOKEN_ALG_NONE` (my assumption in R2) or the code from ADR-0007 R4 or R5? This is open point O1. ADR-0008 stays `Proposed` until you answer it.
2. **Owner and approver:** I copied @security-architect from ADR-0007. Is that right for ADR-0008?

Separately, ADR-0007 links ADR-0006 as `0006-key-sources.md`, but the file is `0006-trusted-key-sources.md`. An accepted record can take that fix, since it changes no rule.

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

I fixed the link in ADR-0007. Under **Related ADRs**, it now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. ADR-0007 is `Accepted`, but a broken-link fix changes no rule, so it can be edited in place. Nothing else in the file changed.

I didn't change the link text, "ADR-0006: Trust only listed key sources". I couldn't open ADR-0006 to check its title. Does that text match the title of `0006-trusted-key-sources.md`? If it doesn't, I'll update the link text to match.
