## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token whose `alg` is `none` before policy evaluation

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <Role, GitHub account: what they approve.>

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. R1 gives way to its `exp` check (R4) and its `kid` check (R5).

## Context

ADR-0007 decides that the service verifies the signature and the lifetime of every token before the request reaches
policy evaluation. Its rules cover the `exp` check (ADR-0007 R4) and the `kid` check (ADR-0007 R5). No rule of
ADR-0007 covers the `alg` value in the header of a token.

RFC 7518, section 3.6, defines `none` as the `alg` value of an Unsecured JWS. An Unsecured JWS has an empty signature.
A token with that `alg` value therefore has no signature that ties its subject to a key source.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Algorithm

- **R1** (`verify`). A token whose header has an `alg` value equal to `none`, compared case-insensitively, is refused
  with HTTP 401 and the reason code `TOKEN_ALG_NONE`, unless the `exp` check of ADR-0007 R4 or the `kid` check of
  ADR-0007 R5 refuses the token.

### Justification

A token whose `alg` is `none` has no signature, so nothing ties its subject to a key source the service trusts (R1).
Its own reason code lets an operator tell an attempt to forge a token apart from an expired token or one with no `kid`
(R1). R1 gives way to the `exp` check of ADR-0007 R4 and the `kid` check of ADR-0007 R5. As a result, a token that
either of those rules refuses keeps the reason code ADR-0007 gives it (R1).

### Alternatives considered

- **A1. Let the JWT library's signature check refuse a token whose `alg` is `none`, with the library's own error.**
  Rejected by R1: the caller does not get `TOKEN_ALG_NONE`, and a library configured to accept `none` passes the token
  on to policy evaluation.

## Consequences

Negative:

- A token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_KID_MISSING`, not `TOKEN_ALG_NONE` (R1).
  An expired token whose `alg` is `none` gets `TOKEN_EXPIRED` (R1).

## Open points

- **O1.** Which reason code goes to a token whose `alg` is `none` and that the `exp` check of ADR-0007 R4 or the `kid`
  check of ADR-0007 R5 also refuses. The options are the ADR-0007 code, which R1 gives now, or `TOKEN_ALG_NONE`. The
  second option needs this record to replace ADR-0007 R4 and R5 whole. The security architect decides. Affects R1.
- **O2.** Whether R1 compares `alg` with `none` case-insensitively, as it does now, so that `None` and `NONE` are
  refused too, or matches only the exact value `none`. RFC 7515 treats `alg` values as case-sensitive, and ADR-0007
  has no rule that refuses a token whose signature does not verify. The security architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement. I put the requirement in a new record, ADR-0008 (`docs/adr/0008-refuse-tokens-with-alg-none.md`), with the status `Proposed`. It is R1 in the `verify` layer.

Once ADR-0008 is accepted, add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and what it adds (R1, the `TOKEN_ALG_NONE` refusal). Also add the Date heading to ADR-0008 then.

Your request left some things open, and these block acceptance:

- **Owner and approvers**: who owns ADR-0008 and who approves R1? I left placeholders under **Owner** and **Participants and approvers**. Is it @security-architect, as for ADR-0007?
- **O1, which reason code wins**: a token with `alg: none` can also be expired or have no `kid`. ADR-0007 R4 and R5 already give such a token `TOKEN_EXPIRED` or `TOKEN_KID_MISSING`. As written, R1 lets those codes win, so ADR-0007 doesn't need to change. If `TOKEN_ALG_NONE` should win instead, ADR-0008 has to replace ADR-0007 R4 and R5 whole. Which do you want?
- **O2, letter case**: should `None` and `NONE` also be refused with `TOKEN_ALG_NONE`? I assumed yes and wrote R1 to compare case-insensitively. ADR-0007 has no rule that refuses a token whose signature fails to verify, so an exact-match rule would leave a token with `alg: NONE` uncovered by any rule. Do you want the case-insensitive match?

No check exists for R1 yet, so ADR-0008 has no **Confirmation** section. Add one when a test for R1 lands.

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

I fixed the link to ADR-0006 in ADR-0007. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. A broken link is an editorial fix that changes no rule, so ADR-0007 keeps its `Accepted` status. Nothing else in the file changed.

I couldn't see ADR-0006 itself, so I kept the link text "ADR-0006: Trust only listed key sources" as it was. Does that still match ADR-0006's title? If not, the link text should change to match.
