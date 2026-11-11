## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse every token in Authorization whose `alg` is `none` before policy evaluation

## Status

Proposed

### Owner

<owner account>

### Participants and approvers

- <role>, <account>: approves R1.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token**. This record adds R1 to the verification rules of ADR-0007 and replaces none of them.

## Context

ADR-0007 requires the service to verify the signature and the lifetime of every token before the request reaches
policy evaluation. Its rules give a reason code to an expired token (ADR-0007 R4) and to a token with no `kid`
(ADR-0007 R5). They give no reason code to a token whose header sets `alg` to `none`. Such a token carries no signature,
so a verifier that accepts the header's `alg` value would accept it, and with it any subject the caller names.

## Decision

We will refuse every token whose header sets `alg` to `none`, and give that refusal a reason code of its own.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R1** (`verify`). A token whose header has `alg` set to the string `none`, compared case-sensitively, is refused
  with HTTP 401 and the reason code `TOKEN_ALG_NONE`. Where ADR-0007 R4 or ADR-0007 R5 also applies to the token, R1
  wins.

### Justification

A token with `alg` set to `none` has no signature to verify, so refusing it before any other check keeps the subject
of an unsigned token away from policy evaluation (R1). A reason code of its own lets an operator tell an attempt to send
an unsigned token apart from an expired token or a token with no `kid` (R1).

### Alternatives considered

- **A1. Let an `alg` of `none` fail the signature check and report the reason code of that failure.** Rejected by R1:
  an operator could not find unsigned tokens by their reason code.

## Consequences

Negative:

- A token whose `alg` is `none` and whose `exp` is earlier than the time of the check gets `TOKEN_ALG_NONE`, not
  `TOKEN_EXPIRED` (R1).
- A token whose `alg` is `none` and whose header has no `kid` gets `TOKEN_ALG_NONE`, not `TOKEN_KID_MISSING` (R1).

Follow-ups:

- When this record is accepted, add a line under **Related ADRs** in ADR-0007 that names this record and the rule it
  adds, R1.

## Open points

- **O1.** Which reason code a token gets when R1 and ADR-0007 R4 or R5 both apply to it. R1 assumes that
  `TOKEN_ALG_NONE` wins. The other answer is that the ADR-0007 rule wins. @security-architect, who approves the rules
  of ADR-0007, decides. Affects R1.
- **O2.** Whether `alg` values such as `None` and `NONE` also get `TOKEN_ALG_NONE`. R1 assumes a case-sensitive match,
  because RFC 7515 treats `alg` values as case-sensitive. The other answer is a case-insensitive match. @security-architect
  decides. Affects R1.
````

### Message to the user

ADR-0007 is `Accepted`, so I left it unchanged. An accepted record can't take a new requirement. I put the requirement in a new record instead: `docs/adr/0008-refuse-alg-none-tokens.md`, with status `Proposed` and one rule, R1 (`verify`). It says that a token whose `alg` is `none` is refused with HTTP 401 and `TOKEN_ALG_NONE`. Once ADR-0008 is accepted, ADR-0007 gets one line under **Related ADRs** pointing to it. I listed that as a follow-up.

Your request left two things open. I assumed an answer for each and recorded both as open points. They keep ADR-0008 at `Proposed` until they're settled:

- **O1:** A token with `alg: none` can also be expired or have no `kid`. Which reason code should it get? I assumed `TOKEN_ALG_NONE` wins over ADR-0007 R4 and R5.
- **O2:** Should `None` and `NONE` also get `TOKEN_ALG_NONE`? I assumed a case-sensitive match on `none`.

Questions for you:

1. Who owns ADR-0008, and who approves R1? I left visible placeholders under **Owner** and **Participants and approvers**.
2. Do you agree with the assumptions for O1 and O2, or do you want the other answers?

The link from ADR-0007 to ADR-0006 is still broken. I didn't change it as part of this request.

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

I fixed the link under **Related ADRs** in ADR-0007. It now points to `0006-trusted-key-sources.md` instead of `0006-key-sources.md`. A broken link is an editorial fix that changes no rule, so an accepted record can take it. Nothing else in the file changed.

The link text still reads "ADR-0006: Trust only listed key sources". I couldn't check that against the actual title of `0006-trusted-key-sources.md`. If the title is different, tell me and I'll update the link text to match.

The change only touches `docs/adr/`, which the reading guide maps to no layer. So the commit and the pull request need no `Implements` or `Defers` trailers.
