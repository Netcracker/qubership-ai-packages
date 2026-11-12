## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 to the rules of ADR-0007, and R1 sets which reason code wins over the `exp` check of
  ADR-0007 R4 and the `kid` check of ADR-0007 R5.

## Context

ADR-0007 decides that the service verifies the signature and the lifetime of every token before the request reaches
policy evaluation. Its rules cover the `exp` check (ADR-0007 R4) and the `kid` check (ADR-0007 R5). No rule names the
`alg` value `none`.

RFC 7518, section 3.6, defines the `alg` value `none` for an unsecured JWS, which carries an empty signature. A
verifier that accepts such a token accepts a subject that no key signed.

## Decision

We will refuse every token whose header gives `alg` as `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose JOSE header has an `alg` value equal to `none`, compared without regard to letter
  case, is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where such a token also fails the `exp` check of
  ADR-0007 R4 or the `kid` check of ADR-0007 R5, the response carries `TOKEN_ALG_NONE`.

### Implementation notes

Adds no requirement. Read `alg` in `internal/verify` before the `kid` and `exp` checks. A token with `alg` set to
`none` then gets its reason code before any other check runs.

### Justification

A token with `alg` set to `none` carries no signature, so accepting it lets any caller name any subject (R1). A reason
code of its own lets an operator tell a forged token from an expired one in the logs (R1). A token with `alg` set to
`none` is the clearest sign of forgery that a token can carry, so its reason code wins over the reason codes of
ADR-0007 R4 and R5 (R1).

### Alternatives considered

- **A1. Refuse a token with `alg` set to `none` through the `kid` check, with `TOKEN_KID_MISSING`.** Rejected by R1:
  a forged token that names a `kid` passes that check, and the reason code hides the forgery.
- **A2. Match `alg` against the lowercase `none` only.** A header with `None` or `NONE` would then fall to no rule.

## Consequences

Negative:

- A token with `alg` set to `none` and no `kid` gets `TOKEN_ALG_NONE` where the `kid` check of ADR-0007 R5 gives
  `TOKEN_KID_MISSING`. A caller that matches on `TOKEN_KID_MISSING` or `TOKEN_EXPIRED` sees the new code for that
  token.

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the rule it
  adds.

## Open points

- **O1.** R1 assumes that `alg` is compared without regard to letter case, so `None` and `NONE` are refused too. The
  other answer is an exact match on `none`, as RFC 7515 compares `alg` values. The security architect decides. Affects
  R1.
- **O2.** R1 assumes that `TOKEN_ALG_NONE` wins where a token also fails the `exp` check of ADR-0007 R4 or the `kid`
  check of ADR-0007 R5. The other answers are that the reason code of ADR-0007 R4 or of ADR-0007 R5 wins. The security
  architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so it stays as it is. An accepted record can't take a new rule. I put the requirement in a new record instead, `docs/adr/0008-refuse-tokens-with-alg-none.md`, as **R1**. Its status is `Proposed`.

Two open points block acceptance:

- **O1:** Should `None` and `NONE` be refused as well? R1 assumes yes.
- **O2:** Which reason code wins when a token with `alg: none` also has no `kid` or has expired? R1 assumes `TOKEN_ALG_NONE` wins over ADR-0007 R4 and R5.

Questions for you:

1. Should @security-architect own and approve ADR-0008? I used the owner and approver of ADR-0007. Please confirm or give the right accounts.
2. ADR-0007's Decision says the service verifies the signature, but none of its rules says which `alg` values are accepted. R1 only covers `none`. Should I draft a separate record for the list of allowed algorithms?

Once ADR-0008 is accepted, ADR-0007 gets one new line under **Related ADRs** that points to it. I listed that under Follow-ups.

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

I fixed the link in ADR-0007 under **Related ADRs**. It pointed to `0006-key-sources.md` and now points to `0006-trusted-key-sources.md`. Fixing a broken link changes no rule, so the accepted record can take it directly and needs no new record. Nothing else in the file changed.

I couldn't open ADR-0006 to check its title. The link text still reads "ADR-0006: Trust only listed key sources." Is that the exact title of `0006-trusted-key-sources.md`? If it isn't, I'll update the link text to match in the same edit.
