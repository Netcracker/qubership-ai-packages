## Request 1

### File: docs/adr/0008-refuse-token-alg-none.md

````markdown
# Refuse a token whose alg is none

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): this record adds
  R1 to its rules, and takes precedence over R4 and R5 of ADR-0007.

## Context

ADR-0007 requires that every token is verified before policy evaluation, and policy evaluation trusts the subject of the
token it receives. A JWT header can name the algorithm `none`, which marks a token that has no signature.

## Decision

We will refuse every token whose `alg` is `none`, with a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Unsigned tokens

- **R1** (`verify`). A token whose header field `alg` is the string `none` is refused with HTTP 401 and the reason code
  `TOKEN_ALG_NONE`. Where such a token also meets ADR-0007 R4 or ADR-0007 R5, this rule takes precedence, and the reason
  code is `TOKEN_ALG_NONE`.

### Justification

A token with no signature binds its subject to nothing, so policy evaluation would trust a subject that no key source
vouches for (R1). Refusing it before the expiry and `kid` checks gives the caller the cause that matters (R1).

## Open points

- **O1.** Whether R1 also covers `alg` values that differ from `none` only in letter case, such as `None` and `NONE`.
  R1 is written for the exact string `none`. The security architect decides.
- **O2.** Whether `TOKEN_ALG_NONE` wins over `TOKEN_EXPIRED` and `TOKEN_KID_MISSING` for a token that meets more than
  one rule. R1 is written as if it wins. The security architect decides.
````

### Message to the user

ADR-0007 is `Accepted`, so I did not edit it. A new requirement goes into a new record, and I drafted `docs/adr/0008-refuse-token-alg-none.md` with the status `Proposed`. It links ADR-0007 under **Related ADRs**. When ADR-0008 is accepted, ADR-0007 gains one line under its own **Related ADRs** that names ADR-0008 and R1.

Questions:

1. Who owns ADR-0008, and who approves R1? I left `<owner account>` and a placeholder approver line. I would expect @security-architect, but I did not assume it.
2. O1: should R1 also refuse `None` and `NONE`, or only the exact string `none`? I wrote the exact string.
3. O2: should `TOKEN_ALG_NONE` win over `TOKEN_EXPIRED` and `TOKEN_KID_MISSING` when a token meets more than one rule? I wrote that it wins, because a token with no signature has no lifetime or key worth reporting.

The record stays `Proposed` until O1 and O2 are settled. The `Date` heading is added on acceptance.

The code change in `internal/verify` should end its commit message and pull request description with `Implements: ADR-0008 R1`. No test or build check for R1 exists yet, so I wrote no **Confirmation** section.

ADR-0007 links `0006-key-sources.md`, which does not match the file `0006-trusted-key-sources.md`. I left it alone here. Request 2 fixes it.

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

I changed one thing: the link target under **Related ADRs** is now `0006-trusted-key-sources.md`. A broken link is an editorial fix that changes no rule, so the accepted record takes it in place, with no new record.

I kept the link text `ADR-0006: Trust only listed key sources`. I could not read ADR-0006, so please check that it matches the title of that record.

The change touches only `docs/adr/`, which maps to no layer, so it needs no `Implements` or `Defers` trailers.
