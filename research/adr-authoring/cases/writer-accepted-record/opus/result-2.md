## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose alg is none with its own reason code

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 to its verification rules. Under answer (a) of O1, R1 also replaces ADR-0007 R4 and R5
  for a token whose `alg` is `none`.

## Context

ADR-0007 has the service verify the signature and the lifetime of every token before the request reaches policy
evaluation. Its rules R4 and R5 give the reason codes for an expired token and for a token without `kid`.

A token whose `alg` is `none` carries no signature (RFC 7518, section 3.6), so nothing binds its subject to a key that
the service trusts. A verifier that takes the algorithm from the token header can accept such a token without checking
any signature. No rule of ADR-0007 names the response to such a token.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation, with a reason code that
no other refusal uses.

### Terms

- **token**: as ADR-0007 defines it.
- **`alg`**: the `alg` parameter of the JOSE header of a token (RFC 7515, section 4.1.1). A claim named `alg` in the
  payload is not the `alg` of the token.

### Rules

#### Verification

- **R1** (`verify`). A token whose `alg` is exactly `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`. Where ADR-0007 R4 or R5 also applies to the token, R1 wins, and the response carries
  `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` carries no signature. A check that trusts the algorithm in the header would skip signature
verification and pass any subject to policy evaluation (R1).

A reason code of its own lets an operator tell a token sent without a signature, a known way to forge a token, apart from
an expired token in the logs (R1).

R1 wins over ADR-0007 R4 and R5 because an unsigned token gives the service no reason to trust its `exp`. Most unsigned
tokens also carry no `kid`, so without that precedence they would get `TOKEN_KID_MISSING` and `TOKEN_ALG_NONE` would
rarely appear (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` when a setting allows it, such as in development or in tests.** Rejected by
  R1: R1 refuses every such token, whatever the configuration.

## Consequences

Negative:

- A client or a test that sends a token whose `alg` is `none` is refused with `TOKEN_ALG_NONE` (R1).
- A token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_ALG_NONE`, where ADR-0007 R5 gives
  `TOKEN_KID_MISSING`. An expired token whose `alg` is `none` gets `TOKEN_ALG_NONE`, where ADR-0007 R4 gives
  `TOKEN_EXPIRED`. A test that sends either token and reads the reason code shows the change (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names this record, the rule it adds,
  and the cases of ADR-0007 R4 and R5 that it replaces.

## Open points

- **O1.** Which reason code a token gets when R1 and ADR-0007 R4 or R5 both apply to it. The answers are: (a) R1 wins,
  and this record replaces ADR-0007 R4 and R5 for a token whose `alg` is `none`; (b) ADR-0007 R4 and R5 win, and R1
  applies only to a token that neither of them refuses. R1 is written for answer (a). The security architect,
  @security-architect, decides. It affects R1.
- **O2.** Whether R1 also covers an `alg` that differs from `none` only in case, such as `None` or `NONE`. The answers
  are: (a) yes, and the check compares `alg` without regard to case; (b) no, and the check compares `alg` exactly, since
  RFC 7515 makes `alg` values case-sensitive. R1 is written for answer (b). The security architect, @security-architect,
  decides. It affects R1.
````

### Message to the user

ADR-0007 is already accepted, so I left it unchanged. The new requirement is rule R1 in a new record, `docs/adr/0008-refuse-alg-none-tokens.md`. Its status is `Proposed`, and it links to ADR-0007. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that points back to it. ADR-0008 lists that edit as a follow-up.

Two open points block acceptance. Both are questions for you or the security architect:

- **O1, which rule wins.** A token with `alg` `none` usually has no `kid`, so ADR-0007 R5 would also refuse it, with `TOKEN_KID_MISSING`. I wrote R1 so that `TOKEN_ALG_NONE` wins. That means ADR-0008 overrides ADR-0007 R4 and R5 for these tokens. Should R1 win, or should R4 and R5 win and R1 apply only to the tokens they don't refuse?
- **O2, letter case.** Should R1 also refuse `None` and `NONE`? I wrote R1 to match `none` exactly, as RFC 7515 does.

I made @security-architect the owner and approver, the same as for ADR-0007. Is that right for this record?

A code change that adds the check should end its commit message and pull request description with `Implements: ADR-0008 R1`.

ADR-0007 also has no rule for which of R4 and R5 wins when a token is both expired and missing `kid`. Fixing that would need another new record, and I didn't change anything for it.

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

I fixed the ADR-0006 link in ADR-0007 so that it points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. Nothing else in the file changed. An accepted record can take an editorial fix like this because no rule changes. The commit doesn't need an `Implements` or `Defers` trailer.

I couldn't open ADR-0006, so I kept the link text "ADR-0006: Trust only listed key sources" as it was. Is that still the heading of `0006-trusted-key-sources.md`? If it isn't, I'll update the link text to match.
