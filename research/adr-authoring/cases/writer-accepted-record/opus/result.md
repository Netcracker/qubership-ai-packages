## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <role>, <GitHub account>: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. R1 adds a requirement to that record and gives way to its expiry rule (R4) and its `kid` rule (R5).

## Context

ADR-0007 has the service verify the signature of every token before the request reaches policy evaluation. ADR-0007
has no reason code for a token whose header sets `alg` to `none`. RFC 7518, section 3.6, defines `alg` `none` as a JWS
with no signature, and RFC 7515 compares `alg` values case-sensitively.

## Decision

We will refuse every token whose header sets `alg` to `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose header sets `alg` to `none`, compared case-sensitively, is refused with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`. R1 gives way to the expiry rule of ADR-0007 R4 and the `kid` rule of ADR-0007 R5: a
  token that either of them refuses gets the reason code of that rule.

### Justification

A token whose `alg` is `none` has no signature. A verifier that accepts it lets any caller name any subject, and R1
refuses such a token whatever the JWT library does by default. A reason code of its own lets operators count these
tokens apart from other refusals (R1). R1 gives way to ADR-0007 R4 and R5 so that this record adds a requirement and
changes no outcome that ADR-0007 requires (R1).

### Alternatives considered

- **A1. Leave `alg` `none` to the algorithm allowlist of the JWT library.** Rejected by R1: the response would carry
  whatever the library's error maps to, not `TOKEN_ALG_NONE`.

## Consequences

Negative:

- A token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_KID_MISSING`, not `TOKEN_ALG_NONE` (R1), so
  a count of `TOKEN_ALG_NONE` leaves such tokens out.

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the
  requirement it adds.

## Open points

- **O1.** Which reason code a token whose `alg` is `none` gets when the expiry rule of ADR-0007 R4 or the `kid` rule
  of ADR-0007 R5 also refuses it. R1 assumes that the ADR-0007 code applies. The other answer is `TOKEN_ALG_NONE`. That
  answer changes what ADR-0007 R4 and R5 require for such a token, so this record would then replace that part of them
  and name it under **Related ADRs**. The security architect decides. Affects R1.
````

### Message to the user

I added your requirement as a new record, ADR-0008, with the status `Proposed`. ADR-0007 is accepted, and an accepted record doesn't take new requirements, so I left it unchanged. Once ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that points to it. That step is listed as a follow-up.

The requirement is ADR-0008 R1, tagged `verify` (`internal/verify`). It refuses a token whose `alg` is exactly `none` with HTTP 401 and `TOKEN_ALG_NONE`.

ADR-0008 stays `Proposed` because of one open point:

- **O1:** A token with `alg` `none` often has no `kid`, and it may also be expired. In that case ADR-0007 R5 or R4 also refuses it, but with a different reason code. I assumed the ADR-0007 code applies, so the new record changes nothing ADR-0007 requires. Should `TOKEN_ALG_NONE` apply instead? Then ADR-0008 would replace that part of ADR-0007 R4 and R5 and would have to say so.

I also need two answers to fill in the metadata:

- Who owns ADR-0008?
- Who approves its rules? Is it @security-architect, as for ADR-0007?

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

I fixed the link in ADR-0007. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. An accepted record can take a fix like this because it changes no rule, so ADR-0007 stays `Accepted` and nothing else in it changed.

I couldn't open ADR-0006, so I kept the link text "Trust only listed key sources" as it was. If ADR-0006 has a different title, the link text should be updated to match.
