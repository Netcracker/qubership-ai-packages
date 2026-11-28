## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- Security architect, @security-architect: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 and replaces no rule of ADR-0007.

## Context

A token whose header names the algorithm `none` carries no signature. Policy evaluation trusts the subject of the token
it receives, so an unsigned token lets any caller name any subject.

## Decision

We will refuse every token whose header names the algorithm `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has `alg` set to `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`.

### Justification

An unsigned token binds its subject to no key, so only a refusal keeps the subject from being chosen by the caller (R1).

## Open points

- **O1.** Which spellings of `alg` count as `none`? This record assumes the exact value `none`, because the values of
  `alg` are case-sensitive. The alternative is to treat `None` and `NONE` the same way. The security architect decides.
  It affects R1.
- **O2.** Which reason code does a token get when R1 and a rule of ADR-0007 both apply, such as an expired token with
  `alg` set to `none`? The answers under consideration are `TOKEN_ALG_NONE` first, or the code of the rule that the
  verification reaches first. The security architect decides. It affects R1, and ADR-0007 R4 and R5.
````

### Message to the user

ADR-0007 is `Accepted`, so it is final and I did not edit it. The new requirement goes into a new record, `docs/adr/0008-refuse-token-alg-none.md`, with status `Proposed`. It links ADR-0007 under **Related ADRs** and defines **token** by pointing at ADR-0007. When 0008 is accepted, ADR-0007 gains one line under **Related ADRs** that names 0008 and the rule it adds.

Questions for you:

1. Who owns 0008? The Owner field holds the placeholder `<owner account>`. Is it `@security-architect`, as in ADR-0007?
2. Does the security architect approve R1? I listed them as approver, as in ADR-0007.
3. Open point O1: should `None` and `NONE` count as `none`? I assumed only the exact value `none`.
4. Open point O2: which reason code wins when R1 and ADR-0007 R4 or R5 both apply to one token?

The record stays `Proposed` until O1 and O2 are answered. There is no Date heading yet, because that heading is added on acceptance. I listed no check under **Confirmation**, because I know of no test for R1.

R1 carries the layer tag `verify`, which the reading guide maps to `internal/verify`. A change to that code must end its commit message and pull request description with `Implements: ADR-0008 R1`.

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

I changed one thing in ADR-0007: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`. The old target was `0006-key-sources.md`. A broken link is an editorial fix that changes no rule, so an accepted record may take it. The status, the Date, and every rule are unchanged.

I kept the link text `ADR-0006: Trust only listed key sources`. I could not open ADR-0006, so please check that its title matches this text.
