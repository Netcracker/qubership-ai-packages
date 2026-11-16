## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse a token in Authorization whose alg is none, with its own reason code

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and gives the responses of R4 and R5, which take precedence over R1.

## Context

A token names its signing algorithm in the `alg` field of its JOSE header. RFC 7518 registers the value `none` for a
token that carries no signature. A verifier that takes the algorithm from the token accepts such a token without a key,
and the caller can then name any subject. ADR-0007 gives a reason code to a refusal by the lifetime check (R4) and by the
`kid` check (R5), and gives none to a token whose `alg` is `none`.

## Decision

We will refuse every token whose `alg` is `none` before the request reaches policy evaluation, with a reason code of its
own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose JOSE header has `alg` set to `none`, in any letter case, is refused with HTTP 401 and
  the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or R5 also applies to the token, the reason code of that rule
  takes precedence over `TOKEN_ALG_NONE`.

### Justification

A reason code of its own lets an operator tell an unsigned token apart from an expired token or a token without `kid`
(R1). Letting the reason codes of ADR-0007 R4 and R5 win leaves those accepted rules as they are (R1). A match in any
letter case also refuses the values `None` and `NONE`, which an exact match passes on to the next check (R1).

### Alternatives considered

- **A1. Let a token whose `alg` is `none` fail signature verification with the reason code of any other bad
  signature.** Rejected by R1: the logs would not separate an unsigned token from a token signed with an unknown key.

## Consequences

Negative:

- A token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_KID_MISSING`, not `TOKEN_ALG_NONE`, so a
  count of `TOKEN_ALG_NONE` misses the unsigned tokens that ADR-0007 R5 refuses first (R1).
- Clients and alerts that match on reason codes have to handle `TOKEN_ALG_NONE` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and the refusal it
  adds.

## Open points

- **O1.** Which reason code wins when ADR-0007 R4 or R5 also applies to a token whose `alg` is `none`. R1 assumes that
  the ADR-0007 code wins. The other answer is that `TOKEN_ALG_NONE` wins, and then this record has to replace ADR-0007
  R4 and R5 whole, because an accepted rule cannot be narrowed from another record. @security-architect decides.
  Affects R1.
- **O2.** Whether R1 matches `alg` in any letter case. R1 assumes it does. The other answer is an exact match of
  `none`, since RFC 7518 treats `alg` values as case-sensitive. @security-architect decides. Affects R1.
````

### Message to the user

ADR-0007 is accepted, so I left it unchanged. An accepted record can't take a new requirement, so I put the rule in a new record, ADR-0008 (`docs/adr/0008-refuse-tokens-with-alg-none.md`). It has the status `Proposed`, and its R1 is the refusal you asked for.

Two open points block acceptance. Please answer them:

1. **O1:** If a token has `alg: none` and also has no `kid` or is expired, which reason code should it get? I assumed ADR-0007's `TOKEN_KID_MISSING` or `TOKEN_EXPIRED` wins, because that keeps ADR-0007 as it is. If you want `TOKEN_ALG_NONE` to win, ADR-0008 must also replace ADR-0007 R4 and R5 whole.
2. **O2:** Should `None` and `NONE` count as `none`? I assumed they do.

I named @security-architect as owner and approver, the same as ADR-0007. Tell me if someone else owns this record.

When ADR-0008 is accepted, it gets its Date heading, and ADR-0007 gets a line under **Related ADRs** that points to it.

Separately, ADR-0007 links ADR-0006 as `0006-key-sources.md`, but the file is `0006-trusted-key-sources.md`. An accepted record may take that fix. Do you want me to make it?

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

I pointed the ADR-0006 link in ADR-0007 to `0006-trusted-key-sources.md`. No rule changed, and an accepted record may take an editorial fix like this, so ADR-0007 stays `Accepted` with its date.

I didn't have the contents of ADR-0006, so I couldn't check two things there. First, that its title is still "Trust only listed key sources". Second, that it defines **key source**. If either is different, tell me and I'll correct the link text or the description.

The change only touches `docs/adr/`, so the commit needs no `Implements` or `Defers` trailers.
