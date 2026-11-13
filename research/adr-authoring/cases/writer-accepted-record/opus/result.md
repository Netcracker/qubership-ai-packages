## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <Role>, <GitHub account>: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. R1 adds a rule to its verification rules and takes precedence over its R4 and R5.

## Context

ADR-0007 decides that the service verifies the signature and the lifetime of every token before the request reaches
policy evaluation. Its rules refuse a token whose `exp` has passed (ADR-0007 R4) and a token whose header has no `kid`
(ADR-0007 R5). None of its rules covers a token whose header has the `alg` value `none`. RFC 7518, section 3.6, defines
that value for a JWS that carries no signature.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation, and give the refusal a
reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has the `alg` value `none`, in any letter case, is refused with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or ADR-0007 R5 also applies to the token, R1 wins.

### Justification

A token with the `alg` value `none` carries no signature, so a service that accepted it would let any caller name any
subject (R1). A reason code of its own lets an operator tell an unsigned token from a token whose `kid` is missing
(R1). Most tokens with the `alg` value `none` also have no `kid`. Without the precedence in R1, ADR-0007 R5 would
refuse them with `TOKEN_KID_MISSING`, and `TOKEN_ALG_NONE` would rarely appear. A comparison in any letter case also
refuses `None` and `NONE`, so the refusal does not depend on how the JWT library compares algorithm names (R1).

### Alternatives considered

- **A1. Compare `alg` with `none` case-sensitively.** Rejected by R1: a token with the `alg` value `NONE` would reach
  whatever the JWT library does with an algorithm name it does not know.
- **A2. Refuse a token with the `alg` value `none` and no `kid` with `TOKEN_KID_MISSING`.** Rejected by R1: the
  operator could not tell an unsigned token from a signed token whose `kid` is missing.

## Consequences

Negative:

- A caller that sends a token with the `alg` value `none` and no `kid` gets `TOKEN_ALG_NONE` where ADR-0007 R5 gave it
  `TOKEN_KID_MISSING` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and R1.

## Open points

- **O1.** Does R1 cover `None`, `NONE`, and every other letter case of `none`, or only the exact value `none`? R1
  assumes every letter case. The approver of the rules decides. Affects R1.
- **O2.** Which reason code does a token get when it has the `alg` value `none` and ADR-0007 R4 or ADR-0007 R5 also
  applies to it: `TOKEN_ALG_NONE`, or the reason code of the ADR-0007 rule? R1 assumes `TOKEN_ALG_NONE`. The approver
  of the rules decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement. I put the requirement in a new record, `docs/adr/0008-refuse-tokens-with-alg-none.md`, as **R1** with the status `Proposed`. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that points to it. That step is listed under Follow-ups.

Before the record can be accepted, I need answers to these questions:

1. **Owner and approvers:** who owns ADR-0008, and who approves it? The metadata has placeholders for now. ADR-0007 has @security-architect as both owner and approver of the rules. Should ADR-0008 use the same?
2. **O1, letter case:** should R1 also refuse `None` and `NONE`, or only the exact value `none`? I wrote R1 to cover every letter case.
3. **O2, precedence:** a token with `alg` `none` can also be expired, or have no `kid`. Which reason code should it get? I wrote R1 so that `TOKEN_ALG_NONE` wins over ADR-0007 R4 and R5. Without that, most unsigned tokens would be refused with `TOKEN_KID_MISSING`. This changes the reason code for that case, and the record lists the change under Negative.

Separately, ADR-0007 links ADR-0006 as `0006-key-sources.md`. That file doesn't exist.

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

I fixed the link to ADR-0006 in ADR-0007. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. No other line changed. ADR-0007 is accepted, and its rules stay the same, so fixing a broken link is an edit it can take.

The link text still reads "ADR-0006: Trust only listed key sources". I don't have ADR-0006's title, so I couldn't check that this matches it. If the title is different, should I change the link text to match?
