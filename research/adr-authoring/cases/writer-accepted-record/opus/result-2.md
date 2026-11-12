## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse every token whose `alg` is `none` with a reason code of its own

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <role>, <GitHub account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and holds the `exp` check (R4) and the `kid` check (R5) that take precedence over R1.

## Context

The `alg` header parameter of a JSON Web Token names the algorithm that secures the token. The value `none` marks an
unsecured token, which carries no signature (RFC 7519, section 6).

ADR-0007 decides that the service verifies the signature and the lifetime of every token before policy evaluation. It
has rules for the `exp` check (R4) and the `kid` check (R5). None of its rules names the HTTP status or the reason code
for a token whose `alg` is `none`.

## Decision

We will refuse a token whose `alg` is `none` with HTTP 401 and a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.
- **`alg`**: the `alg` parameter in the JOSE header of a token. Its value is case-sensitive (RFC 7515, section 4.1.1),
  so `None` and `NONE` are not `none`.

### Rules

#### Verification

- **R1** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where
  the `exp` check of ADR-0007 R4 or the `kid` check of ADR-0007 R5 also refuses the token, the reason code of that
  rule wins.

### Justification

A token whose `alg` is `none` carries no signature, so the subject it names can be any subject. A reason code of its
own lets an operator find these tokens in the logs and tell a forgery attempt or a misconfigured issuer apart from an
expired token (R1). The precedence in R1 keeps every reason code that ADR-0007 already gives, so ADR-0007 stays as it is
(R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` as a token without a signature.** Rejected by R1: policy evaluation would
  trust a subject that nothing signed.
- **A2. Refuse a token whose `alg` is `none` with a reason code that other signature failures share.** Rejected by R1:
  the logs would not show which callers send unsigned tokens.

## Consequences

Negative:

- A token whose `alg` is `none` and that the `exp` check of ADR-0007 R4 or the `kid` check of ADR-0007 R5 refuses gets
  the reason code of that rule, so a count of `TOKEN_ALG_NONE` misses those tokens (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the rule it
  adds, R1.

## Open points

- **O1.** Which reason code a token gets when its `alg` is `none` and the `exp` check of ADR-0007 R4 or the `kid` check
  of ADR-0007 R5 also refuses it. R1 assumes that the reason code of ADR-0007 wins, so that ADR-0007 stays as it is.
  The other answer is `TOKEN_ALG_NONE`. That answer would narrow ADR-0007 R4 and R5, so this record would then replace
  both rules in part and state them again in full. The approver of this record decides. The answer affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement. I put the requirement in a new record instead, `docs/adr/0008-refuse-alg-none-tokens.md`, with the status `Proposed`. Its R1 refuses a token whose `alg` is `none` with HTTP 401 and `TOKEN_ALG_NONE`.

I need two things from you before the record can be accepted:

1. **Owner and approvers:** who owns ADR-0008, and who approves R1? I left placeholders under **Owner** and **Participants and approvers**. Is it @security-architect again, as on ADR-0007?
2. **Precedence (O1):** a token can have `alg` set to `none` and also fail the `exp` check (ADR-0007 R4) or the `kid` check (ADR-0007 R5). Which reason code should it get?
   - **Keep ADR-0007's code:** this is what R1 assumes now. ADR-0007 stays as it is.
   - **Use `TOKEN_ALG_NONE`:** ADR-0008 would then have to replace ADR-0007 R4 and R5 in part.

   O1 keeps the status at `Proposed` until you answer.

Once ADR-0008 is accepted, ADR-0007 gets a line under **Related ADRs** that points to ADR-0008 R1. The repository has a reading guide, so the change that adds the check should end its commit message and pull request description with `Implements: ADR-0008 R1`.

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

I fixed the link in ADR-0007. Under **Related ADRs**, it pointed to `0006-key-sources.md`, which doesn't exist; it now points to `0006-trusted-key-sources.md`. ADR-0007 is accepted, but a broken link is an editorial fix that changes no rule, so it can be made in place. Nothing else in the file changed.

The link text still reads "ADR-0006: Trust only listed key sources". I couldn't open ADR-0006 to check that this matches its title. Could you confirm that it does?
