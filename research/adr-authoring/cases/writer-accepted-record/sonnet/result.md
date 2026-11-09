## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose alg is none before policy evaluation

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): adds a rule to the verification that ADR-0007 requires. ADR-0007 R4 and R5 stay as they are.

## Context

ADR-0007 requires verification of every token before policy evaluation. Its rules cover `exp` (R4) and `kid` (R5) and
say nothing about `alg`. A token whose `alg` is `none` declares that it carries no signature, and policy evaluation
trusts the subject of the token it receives.

## Decision

We will refuse every token whose `alg` is `none`, as part of the verification that ADR-0007 requires before policy
evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.

### Justification

A token that declares no signature binds its subject to no key source, so verification cannot accept it (R1).

## Consequences

Negative:

- A caller that sends an unsigned token, such as a test client, gets HTTP 401 with `TOKEN_ALG_NONE`.

## Open points

- **O1.** Does R1 also refuse a token whose `alg` is `None` or `NONE`? The answers are "only the exact value `none`" and
  "`none` in any letter case". The draft assumes the exact value `none`. The security architect decides. Affects R1.
- **O2.** Which reason code wins when one token meets R1 and also ADR-0007 R4 or R5, such as an expired token whose
  `alg` is `none`? The answers are "`TOKEN_ALG_NONE` always wins" and "the order of the checks in ADR-0007 comes first".
  The security architect decides. Affects R1, ADR-0007 R4, and ADR-0007 R5.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. The new rule is in a new record, ADR-0008, with status `Proposed`. ADR-0008 links ADR-0007 under **Related ADRs**. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that names ADR-0008 and the rule it adds.

Questions for you:

1. Who owns ADR-0008? I left `<owner account>` in **Owner** and did not copy `@security-architect` from ADR-0007. I put `@security-architect` under **Participants and approvers** as the approver, which is an assumption.
2. Open point O1: should R1 also refuse `None` and `NONE`, or only the exact value `none`? The draft assumes the exact value.
3. Open point O2: when one token breaks R1 and also ADR-0007 R4 or R5, which reason code wins?

The record stays `Proposed` until both open points are settled and the team signs off. A code change that brings R1 should carry `Implements: ADR-0008 R1`.

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

I fixed the link under **Related ADRs** in ADR-0007. The target changed from `0006-key-sources.md` to `0006-trusted-key-sources.md`. This is an editorial fix that changes no rule, so it is allowed on an accepted record, and nothing else in the file changed. I kept the link text as it was because I could not check the title of ADR-0006 against the file.
