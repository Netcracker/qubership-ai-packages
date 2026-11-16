## Request 1

### File: docs/adr/0008-refuse-token-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <Role>, <GitHub account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): adds R1 to the
  rules of its **Verification** topic. R4 and R5 of ADR-0007 stay as they are.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before policy evaluation. The
`alg` field in the header of a token names the algorithm that signed it. The value `none` names no algorithm, so such a
token carries no signature to verify.

## Decision

We will refuse every token whose `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` has no signature that could bind its subject to a key source, so refusing it keeps a
caller from naming any subject (R1).

## Open points

- **O1.** Does R1 also cover `alg` values that differ from `none` only in letter case, such as `None` or `NONE`? The
  answers are "exactly `none`" and "`none` in any letter case". The owner decides. R1 is affected.
- **O2.** Which reason code does a token receive when it breaks R1 and also ADR-0007 R4 or R5, such as a token with
  `alg` set to `none` and no `kid`? The answers are `TOKEN_ALG_NONE` first, or the code of the ADR-0007 rule first. The
  owner decides. R1, ADR-0007 R4, and ADR-0007 R5 are affected.
````

### Message to the user

ADR-0007 is `Accepted` and carries a Date, so it is final. A new requirement goes into a new record, so I wrote ADR-0008 as `Proposed` and left ADR-0007 unchanged. When ADR-0008 is accepted, ADR-0007 gains one line under **Related ADRs** that names ADR-0008 and the rule it adds.

Questions:

- Who is the owner of ADR-0008, and who approves R1? I left placeholders instead of guessing.
- O1: should R1 also refuse `None` and `NONE`, or only exactly `none`?
- O2: which reason code wins when a token also breaks ADR-0007 R4 or R5? An example is a token with `alg` set to `none` and no `kid`.

The record stays `Proposed` until both open points are settled and the team signs off. A change that implements R1 can name `ADR-0008 R1` under `Implements` in its trailers.

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

I changed the link target under **Related ADRs** from `0006-key-sources.md` to `0006-trusted-key-sources.md`. A broken link is an editorial fix that changes no rule, so an accepted record takes it. I touched nothing else, and the status and Date stay as they were.

I left the link text, "ADR-0006: Trust only listed key sources", as it was. I can't see the title of ADR-0006, so please check that it matches the heading of that record.
