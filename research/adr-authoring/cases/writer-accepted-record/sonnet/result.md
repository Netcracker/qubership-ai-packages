## Request 1

### File: docs/adr/0008-refuse-token-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- <role>, <GitHub account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines **token**, and gives the refusals whose HTTP status and reason-code form R1 follows (R4, R5).

## Context

The header of a token carries an `alg` field that names the signature algorithm. The value `none` marks a token that has no signature. ADR-0007 gives no outcome for such a token, so the code decides it today.

## Decision

We will refuse every token whose `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none`, in any letter case, is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where the same token also meets R4 or R5 of ADR-0007, the reason code is `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` has no signature, so no key source vouches for its subject. Refusing it by name gives the caller a reason code that points at the cause (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` and check only its lifetime.** Rejected by R1: the subject of such a token is a claim that nothing signed, and policy evaluation would trust it.

## Consequences

Negative:

- A caller that sends unsigned tokens, such as a test client, gets HTTP 401 and `TOKEN_ALG_NONE` (R1).
- A token that is both unsigned and expired gets `TOKEN_ALG_NONE`, not `TOKEN_EXPIRED` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** of ADR-0007 that names this record and what it adds.

## Open points

- **O1.** Does R1 cover `alg` values such as `None` and `NONE`? R1 assumes it does. The alternative is to match the exact value `none`. The owner decides. This affects R1.
- **O2.** Which reason code does a token get that meets R1 and also R4 or R5 of ADR-0007? R1 assumes `TOKEN_ALG_NONE`. The alternative is to leave the order to the implementer. The owner decides. This affects R1.
````

### Message to the user

ADR-0007 is accepted, so I did not edit it. A requirement for an accepted record goes into a new record. I wrote ADR-0008 as `Proposed`, and it links to ADR-0007. When ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** that names it. That line is the only change to ADR-0007.

Questions:

1. Who owns ADR-0008, and who approves R1? I left placeholders in **Owner** and **Participants and approvers**.
2. Open point O1: should `None` and `NONE` count as `none`? I assumed yes.
3. Open point O2: when a token is unsigned and also expired or has no `kid`, which reason code wins? I assumed `TOKEN_ALG_NONE`.

The status stays `Proposed` until O1 and O2 are settled. The code change for R1 belongs under `internal/verify`. Its commit message and pull request description should end with `Implements: ADR-0008 R1`.

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

I changed one link target under **Related ADRs**, from `0006-key-sources.md` to `0006-trusted-key-sources.md`. The change is editorial and touches no rule, so the accepted record takes it. I left every other line as it was.

While reading the record, I saw that the Decision promises signature verification, but no rule covers it. The Justification also cites R5 for a verified signature, and R5 is about `kid`. I did not touch either, because a rule change to an accepted record needs a new record. Tell me if you want me to draft one.
