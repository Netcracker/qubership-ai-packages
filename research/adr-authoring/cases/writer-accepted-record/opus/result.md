## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

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
  **token**. This record adds R1 to the verification rules of ADR-0007 and replaces none of them.

## Context

ADR-0007 refuses a token that has expired (ADR-0007 R4) and a token whose header has no `kid` (ADR-0007 R5). A token
whose header sets `alg` to `none` carries no signature (RFC 7519, section 6). No rule of ADR-0007 refuses such a token
when it has a `kid` and has not expired, so a caller can write one with any subject.

## Decision

We will refuse every token whose header sets `alg` to `none` before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has the `alg` value `none`, in any letter case, is refused with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or ADR-0007 R5 also applies to the token, the reason code is
  still `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` binds its subject to no key source, so any caller could name any subject (R1). A
separate reason code lets an operator find such tokens in the logs, apart from expired tokens and tokens with no `kid`
(R1).

### Alternatives considered

- **A1. Let a token with `alg` set to `none` fail signature verification under a general reason code.** Rejected by
  R1: an operator could not tell an unsigned token from a token with a bad signature.

## Consequences

Negative:

- A client that sends unsigned tokens, such as a local test client, gets HTTP 401 with `TOKEN_ALG_NONE` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and its R1.

## Open points

- **O1.** R1 assumes that `alg` is compared in any letter case, so that `None` and `NONE` also get `TOKEN_ALG_NONE`.
  The other answer is an exact match on `none`, which leaves other spellings to the rest of verification. The security
  architect decides. Affects R1.
- **O2.** R1 assumes that `TOKEN_ALG_NONE` takes precedence over `TOKEN_EXPIRED` (ADR-0007 R4) and
  `TOKEN_KID_MISSING` (ADR-0007 R5) when a token meets more than one of these rules. The other answer gives the
  precedence to the ADR-0007 codes. The security architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement. I put the rule in a new record, `docs/adr/0008-refuse-alg-none-tokens.md`, as R1 with status `Proposed`. Once ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that points to it. That line is listed as a follow-up.

Your request didn't settle two things, so I picked an answer for each and recorded it as an open point. ADR-0008 stays `Proposed` until both are decided:

- **O1:** Should `None` and `NONE` also get `TOKEN_ALG_NONE`, or only `none` exactly? I chose any letter case.
- **O2:** When a token has `alg: none` and also no `kid` or an expired `exp`, which reason code wins? I chose `TOKEN_ALG_NONE`.

Questions for you:

- I made @security-architect the owner and approver, the same as for ADR-0007. Is that correct?
- ADR-0007 has no numbered rule that requires a valid signature. Only its Decision sentence says so. A token signed with the wrong key passes both R4 and R5. Do you want a separate record for that?
- The link to ADR-0006 in ADR-0007 points to `0006-key-sources.md`, which doesn't exist. The fix is an editorial change that an accepted record can take. Should I make it?

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

I changed the link to ADR-0006 in ADR-0007 from `0006-key-sources.md` to `0006-trusted-key-sources.md`. ADR-0007 is accepted, and a broken link is one of the editorial fixes an accepted record can take. No rule changed.

I kept the link text "ADR-0006: Trust only listed key sources" as it was. If the title in `0006-trusted-key-sources.md` is worded differently, should I change the link text to match it?
