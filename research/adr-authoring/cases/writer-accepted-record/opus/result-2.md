## Request 1

### File: docs/adr/0008-refuse-tokens-with-alg-none.md

````markdown
# Refuse every token in Authorization whose header sets `alg` to `none`

## Status

Proposed

### Owner

@security-architect

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. R1 adds a rule to its Rules, and R1 yields to its R4 and R5.

## Context

ADR-0007 has the service verify the signature and the lifetime of every token before the request reaches policy
evaluation. One of its rules refuses a token whose `exp` has passed (ADR-0007 R4). Another refuses a token whose header
has no `kid` (ADR-0007 R5). No rule of ADR-0007 covers a token whose header sets `alg` to `none`. RFC 7518, section 3.6,
defines `none` as the `alg` value of an unsecured JWS, which carries no signature. RFC 7515, section 4.1.1, defines the
`alg` value as a case-sensitive string.

## Decision

We will refuse every token whose header sets `alg` to `none`, and give the refusal a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Unsigned tokens

- **R1** (`verify`). A token whose header sets `alg` to the exact string `none` is refused with HTTP 401 and the reason
  code `TOKEN_ALG_NONE`, except where ADR-0007 R4 or ADR-0007 R5 refuses the token. In that case, the response that
  ADR-0007 R4 or R5 defines applies.

### Justification

A token whose `alg` is `none` carries no signature, so nothing binds its subject to a key source the service trusts
(R1). A reason code of its own lets an operator count unsigned tokens apart from expired tokens and tokens without
`kid` (R1). R1 yields to ADR-0007 R4 and R5, so this record changes no response that an accepted rule defines.

### Alternatives considered

- **A1. Check `alg` before `exp` and `kid`, so that a token whose `alg` is `none` always gets `TOKEN_ALG_NONE`.**
  Rejected by R1: an expired token or a token without `kid` would then get a reason code other than the one that
  ADR-0007 R4 or R5 defines. Only a record that replaces those rules can change that. O1 asks whether to write that
  record.

## Consequences

Negative:

- A token whose `alg` is `none` and that is also expired, or has no `kid`, gets the reason code of ADR-0007 R4 or R5.
  The count of `TOKEN_ALG_NONE` refusals therefore leaves out some unsigned tokens that the service refuses (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the rule R1 it
  adds.

## Open points

- **O1.** Which reason code a token gets when its `alg` is `none` and ADR-0007 R4 or R5 also refuses it. R1 assumes
  that the reason code of ADR-0007 R4 or R5 wins, so that this record changes no accepted rule. The other answer is
  that `TOKEN_ALG_NONE` wins, which requires a record that replaces ADR-0007 R4 and R5. The security architect,
  @security-architect, decides. Affects R1.
- **O2.** Whether R1 covers an `alg` value that differs from `none` only in letter case, such as `None` or `NONE`. R1
  assumes that it does not, because RFC 7515 defines `alg` as case-sensitive. The other answer is that R1 covers every
  letter case of `none`. The security architect, @security-architect, decides. Affects R1.
````

### Message to the user

I didn't change ADR-0007. It's `Accepted`, and an accepted record can't take a new requirement, so the rule is R1 in a new record, `docs/adr/0008-refuse-tokens-with-alg-none.md`, with the status `Proposed`. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that points to it. ADR-0008 lists that as a follow-up.

I have three questions before ADR-0008 can be accepted:

1. **Owner and approver:** I made @security-architect the owner and approver because they own ADR-0007. Is that right, or should someone else own or approve this record?
2. **O1, which reason code wins:** A token can have `alg: none` and also be expired or have no `kid`. Which reason code should it get?
   - **As written:** ADR-0007's code wins (`TOKEN_EXPIRED` or `TOKEN_KID_MISSING`). That way no accepted rule changes.
   - **The alternative:** `TOKEN_ALG_NONE` always wins. That needs a further record that replaces ADR-0007 R4 and R5.
3. **O2, letter case:** Should R1 also refuse `None`, `NONE`, and other letter-case variants with `TOKEN_ALG_NONE`? As written, it covers only the exact string `none`, because RFC 7515 defines `alg` as case-sensitive.

ADR-0008 stays `Proposed` until O1 and O2 are settled.

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

I fixed the link in ADR-0007. It pointed to `0006-key-sources.md` and now points to `0006-trusted-key-sources.md`. Nothing else changed.

ADR-0007 is accepted, and a broken link is one of the few edits an accepted record can take. The fix changes no rule, so the status and date stay as they are.

I couldn't open ADR-0006, so I kept the link text "ADR-0006: Trust only listed key sources" as it was. Does that still match ADR-0006's title? If not, I'll update the link text to match.
