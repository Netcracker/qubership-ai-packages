## Request 1

### File: docs/adr/0008-refuse-token-with-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- `<role>`, `<GitHub account>`: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and sets the refusals of R4 and R5 that R1 here takes precedence over.

## Context

The `alg` parameter in the header of a token names the algorithm that signed it, and the value `none` names no
algorithm: the token carries no signature. ADR-0007 requires the service to verify every token before policy evaluation,
and a token with `alg` set to `none` has nothing to verify.

## Decision

We will refuse every token whose `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header `alg` is `none`, compared without regard to letter case, is refused with HTTP
  401 and the reason code `TOKEN_ALG_NONE`, also where ADR-0007 R4 or R5 would refuse the same token.

### Justification

A caller can send any subject in a token with no signature, so the service refuses it before any other check (R1). A
reason code of its own lets an operator tell an unsigned token from an expired one (R1).

### Alternatives considered

- **A1. Let the signature check refuse a token whose `alg` is `none`.** Rejected by R1: the refusal would carry the
  reason code of a failed signature, and an operator could not tell an unsigned token from a forged one.

## Consequences

Negative:

- A caller that sends a token with `alg` set to `none`, such as a local test client, gets `TOKEN_ALG_NONE` (R1).

## Open points

- **O1.** Does R1 apply to `None` and `NONE` as it does to `none`? The rule assumes that it does. The owner decides, and
  the answer affects R1.
- **O2.** Which reason code does a token get when `alg` is `none` and `exp` is in the past, or `kid` is missing? The
  rule assumes `TOKEN_ALG_NONE`. The owner decides, and the answer affects R1 and ADR-0007 R4 and R5.
````

### Message to the user

ADR-0007 is `Accepted`, so it is final and I left it unchanged. The new requirement is in a new record, `docs/adr/0008-refuse-token-with-alg-none.md`, with the status `Proposed`. It links ADR-0007 under **Related ADRs**. When ADR-0008 is accepted, ADR-0007 gains a line under **Related ADRs** that names it and R1, and I can add that line then.

Questions:

1. Who owns ADR-0008, and who approves R1? The owner and the approver are placeholders in the record.
2. Does R1 also cover `None` and `NONE`? I assumed it does (O1).
3. Which reason code wins when a token with `alg` set to `none` is also expired or has no `kid`? I assumed `TOKEN_ALG_NONE` (O2).

The status stays `Proposed` until O1 and O2 are settled and the team signs off.

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

I changed the link target under **Related ADRs** from `0006-key-sources.md` to `0006-trusted-key-sources.md`. The link text, the rules, and the status are unchanged. ADR-0007 is `Accepted`, and a broken-link fix is an editorial edit that an accepted record takes.
