## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse a token whose `alg` is `none` with HTTP 401 and `TOKEN_ALG_NONE`

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**, and holds the expiry check (R4) and the `kid` check (R5) whose reason codes R1 takes precedence over.

## Context

ADR-0007 requires the service to verify every token before the request reaches policy evaluation, and policy
evaluation trusts the subject of the token it receives. A token whose header `alg` is `none` declares that it has no
signature, so no key source can bind its subject to a signer.

## Decision

We will refuse a token whose header `alg` is `none` before the request reaches policy evaluation.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Unsigned tokens

- **R1** (`verify`). A token whose header `alg` field is the string `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`. Where the same token also fails the expiry check of ADR-0007 R4 or the `kid` check of ADR-0007 R5,
  the refusal carries `TOKEN_ALG_NONE`.

### Justification

A token with `alg` set to `none` has no signature to verify, so only a refusal keeps a caller from naming any subject
(R1). A single reason code for such a token tells the caller the real cause, instead of an expiry or a missing `kid`
that fixing would not help (R1).

### Alternatives considered

- **A1. Accept a token whose `alg` is `none` and leave the decision to policy evaluation.** Rejected by R1: policy
  evaluation would trust a subject that nothing checked.

## Consequences

Negative:

- A caller that sends unsigned tokens, such as a test client, gets `TOKEN_ALG_NONE` on every request (R1).

## Open points

- **O1.** Which `alg` values count as `none`. R1 assumes the exact string `none`. The alternative is to also refuse
  `None` and `NONE`. The security architect decides. R1 is affected.
- **O2.** Which reason code wins for a token that fails R1 and also ADR-0007 R4 or R5. R1 assumes `TOKEN_ALG_NONE`,
  because a token with no signature is not worth a finer diagnosis. The alternative is to keep the reason code of
  ADR-0007 R4 or R5. The security architect decides. R1 is affected.
````

### Message to the user

ADR-0007 is `Accepted`, so it stays as it is. I put the requirement in a new record, `docs/adr/0008-refuse-alg-none-tokens.md`, with status `Proposed`. It links ADR-0007. When ADR-0008 is accepted, ADR-0007 gains a line under **Related ADRs** that names ADR-0008 and what it adds.

Questions:

1. Who owns ADR-0008, and who approves R1? The owner and approver fields hold placeholders until you answer.
2. O1: should `None` and `NONE` also count as `none`? I assumed only the exact string `none`.
3. O2: should `TOKEN_ALG_NONE` win when a token also fails ADR-0007 R4 or R5? I assumed it does, so R1 says so. Otherwise two rules would give one token two reason codes.

The status stays `Proposed` until O1 and O2 are settled. The code change that adds the check in `internal/verify` can already end its commit message and pull request description with `Implements: ADR-0008 R1`.

I did not touch ADR-0007. Its link to ADR-0006 points at `0006-key-sources.md`, but the file is `0006-trusted-key-sources.md`, so the link is broken. That is a separate fix.

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

I changed one thing in ADR-0007: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`, where it was `0006-key-sources.md`. An accepted record allows this edit because it changes no rule. I left the link text, `ADR-0006: Trust only listed key sources`, as it was, because I can't see the title of ADR-0006 and so can't confirm it matches.
