## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token whose `alg` is `none`

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and holds the expiry rule (R4) and the `kid` rule (R5) whose reason codes R1 ranks against.

## Context

ADR-0007 requires the service to verify every token before the request reaches policy evaluation. No rule of ADR-0007
names an outcome for a token whose header sets `alg` to `none`. RFC 7518, section 3.6, defines `none` as the algorithm
of an unsecured JWS, which carries an empty signature. A token with that header is not bound to any key.

## Decision

We will refuse every token whose header sets `alg` to `none` before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose header has an `alg` value equal to `none`, compared case-insensitively, is refused
  with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or ADR-0007 R5 also refuses the token, the
  service returns the reason code of that rule instead of `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` has no signature, so any caller can write one that names any subject (R1). Because the
reason code is specific to this case, a caller or an operator can tell an unsigned token apart from an expired one or
one without a `kid` (R1).

### Alternatives considered

- **A1. Let the signature check refuse a token with `alg` `none` the same way it refuses any token whose signature
  fails.** Rejected by R1: the response would carry no reason code that names the unsigned header.

## Consequences

Negative:

- A client that sends tokens with `alg` set to `none`, such as a local test client, gets HTTP 401 with
  `TOKEN_ALG_NONE` (R1) and has to send a signed token instead.

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names this record and the rule it
  adds, R1.

## Open points

- **O1.** R1 assumes that when ADR-0007 R4 or R5 also applies, the reason code of the ADR-0007 rule is returned. The
  other option is that `TOKEN_ALG_NONE` is returned. In that case this record replaces part of ADR-0007 R4 and R5 and
  has to name them under **Related ADRs**. The security architect, @security-architect, decides. Affects R1.
- **O2.** R1 assumes that `alg` is compared case-insensitively, so `None` and `NONE` are refused too. The other option
  is an exact match on `none`. With an exact match, no rule covers `None`. The security architect, @security-architect,
  decides. Affects R1.
````

### Message to the user

I didn't change ADR-0007. It's accepted, and an accepted record can't take a new requirement, so I put the rule in a new record: `docs/adr/0008-refuse-tokens-with-alg-none.md`, as R1. Its status is `Proposed`. Once it's accepted, ADR-0007 gets a link back to it under **Related ADRs**. That step is listed under Follow-ups.

I need a few answers before this record can be accepted:

- **Owner and approver:** Who owns ADR-0008, and who approves R1? I left placeholders for both. Should they be @security-architect, like ADR-0007?
- **O1, which reason code wins:** If a token with `alg: none` is also expired or has no `kid`, should the response carry `TOKEN_ALG_NONE` or the ADR-0007 code? I assumed the ADR-0007 code wins, because then this record doesn't override any accepted rule. If you want `TOKEN_ALG_NONE` to win, the record will replace part of ADR-0007 R4 and R5.
- **O2, case of `none`:** Should `None` and `NONE` also be refused? I assumed yes, so the comparison is case-insensitive. With an exact match, no rule covers those values.

Separately, the link in ADR-0007 to ADR-0006 points to `0006-key-sources.md`, which doesn't exist. Fixing it is an editorial change that an accepted record is allowed to take.

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

I fixed the link in ADR-0007: the link to ADR-0006 now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. Nothing else in the file changed. A broken link is an editorial fix, so the accepted record can take it without a new ADR.

I kept the link text, "ADR-0006: Trust only listed key sources," as it was. Does that still match the title of `0006-trusted-key-sources.md`? If it doesn't, I'll update the link text to match.
