## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse every token in Authorization whose `alg` is `none`

## Status

Proposed

### Owner

<owner>

### Participants and approvers

- <role>, <approver>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 to it, and R1 takes precedence over its reason codes for an expired token (R4) and for
  a token with no `kid` (R5).

## Context

ADR-0007 requires the service to verify every token before the request reaches policy evaluation. It gives a reason
code for an expired token (ADR-0007 R4) and for a token whose header has no `kid` (ADR-0007 R5). It gives none for a
token whose `alg` is `none`.

RFC 7518 defines the `alg` value `none` for an unsecured token, which has an empty signature. Such a token binds its
subject to no key, so a caller who sends one can name any subject.

## Decision

We will refuse every token whose `alg` is `none` with its own reason code, before the request reaches policy
evaluation.

### Terms

- **token**: as ADR-0007 defines it.
- **`alg`**: the value of the `alg` parameter in the JOSE header of a token.

### Rules

#### Unsecured tokens

- **R1** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where
  that token also meets the condition of ADR-0007 R4 or ADR-0007 R5, R1 takes precedence, and the reason code is
  `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` carries no signature that the service can check against a key source, so it has to be
refused (R1). Its own reason code tells the caller and the operator that the token was unsecured, rather than expired
or missing a `kid`, so R1 takes precedence over ADR-0007 R4 and R5.

### Alternatives considered

- **A1. Leave a token whose `alg` is `none` to the signature check, with whatever reason code the check reports.**
  Rejected by R1: the reason code would depend on the library and on which other check fails first.

## Consequences

Negative:

- A caller that sends a token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_ALG_NONE` instead of
  `TOKEN_KID_MISSING`, and one that sends an expired token whose `alg` is `none` gets `TOKEN_ALG_NONE` instead of
  `TOKEN_EXPIRED` (R1).

## Open points

- **O1.** R1 assumes that `TOKEN_ALG_NONE` takes precedence over the reason codes of ADR-0007 R4 and R5. The other
  answers are that ADR-0007 R5 wins, or that both ADR-0007 R4 and R5 win. The security architect decides. Affects R1.
- **O2.** R1 covers only the exact value `none`. The question is whether `alg` values that differ only in case, such
  as `None` and `NONE`, are also refused with `TOKEN_ALG_NONE`. The answers are "exact value only" and "any case". The
  security architect decides. Affects R1.
````

### Message to the user

I left ADR-0007 unchanged. It's `Accepted`, and an accepted record can't gain a requirement. I put the new rule in a new record instead: `docs/adr/0008-refuse-alg-none-tokens.md` (ADR-0008, status `Proposed`). It has one rule:

- **R1**: a token whose `alg` is `none` is refused with HTTP 401 and `TOKEN_ALG_NONE`.

Two open points have to be settled before ADR-0008 can be accepted:

- **O1. Which reason code wins.** A token can have `alg: none` and also be expired (ADR-0007 R4) or have no `kid` (ADR-0007 R5). I assumed `TOKEN_ALG_NONE` wins and wrote R1 that way. Is that right?
- **O2. Case variants.** Should `alg` values like `None` or `NONE` also get `TOKEN_ALG_NONE`, or only the exact value `none`?

Two more questions:

- Who owns ADR-0008, and who approves R1? I left `<owner>`, `<role>`, and `<approver>` as placeholders rather than guess. Is it @security-architect, as for ADR-0007?
- I couldn't find a test that shows which reason code a caller gets today for an `alg: none` token. Is there one I should name under **Negative**?

When ADR-0008 is accepted:

- Add the `### Date` heading after its status line.
- Add a line under **Related ADRs** in ADR-0007 that names ADR-0008 and says it adds R1, which takes precedence over ADR-0007 R4 and R5.

ADR-0007's link to ADR-0006 points at `0006-key-sources.md`, which doesn't exist. I can fix that separately if you want; a broken link is an allowed edit to an accepted record.

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

I fixed the link in ADR-0007. It pointed at `0006-key-sources.md` and now points at `0006-trusted-key-sources.md`. Nothing else in the file changed, and ADR-0007 stays `Accepted`, because fixing a broken link changes no rule.

I couldn't open ADR-0006, so I kept the link text "ADR-0006: Trust only listed key sources" as it was. If ADR-0006's title is different, should I change the link text to match it?

The change only touches `docs/adr/`, which isn't mapped to any layer in the reading guide. So the commit and the pull request don't need `Implements` or `Defers` trailers.
