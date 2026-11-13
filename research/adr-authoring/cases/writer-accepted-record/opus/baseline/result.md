## Request 1

### File: docs/adr/0008-refuse-alg-none-tokens.md

````markdown
# Refuse every token whose alg is none

## Status

Proposed

### Date

2026-11-09

### Owner

TBD

### Participants and approvers

- Security architect, @security-architect: approves the rules.

### Related ADRs

- [ADR-0007: Verify every token in Authorization before policy evaluation](0007-verify-every-token.md): defines
  **token** and the rules R4 and R5. This record adds R6 to them.

## Context

ADR-0007 requires the service to verify the signature of every token before policy evaluation. Its rules refuse an
expired token (R4) and a token whose header has no `kid` (R5). No rule refuses a token whose `alg` is `none`. Such a
token carries no signature, and it can still carry a `kid` and a future `exp`.

## Decision

We will refuse every token whose `alg` is `none`.

### Terms

- **token**: as ADR-0007 defines it.

### Rules

#### Verification

- **R6** (`verify`). A token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`.

### Justification

A token whose `alg` is `none` has no signature, so its subject is whatever the caller wrote (R6).

### Alternatives considered

- **A1. Rely on R5 to refuse unsigned tokens.** Rejected by R6: R5 refuses only a token whose header has no `kid`, and
  an unsigned token can carry a `kid`.

## Consequences

Negative:

- An issuer that sends unsigned tokens, such as one in a test environment, gets `TOKEN_ALG_NONE` on every request.
````

### Message to the user

I put the requirement in a new record, ADR-0008, and left ADR-0007 unchanged. ADR-0007 is Accepted, and it lists @security-architect as the person who approves its rules. If I added a rule to it directly, the record would show the security architect approving a rule they never saw. ADR-0008 has the status Proposed and adds the rule as R6, so you can take it to them for approval.

The rule uses your wording: a token whose `alg` is `none` is refused with HTTP 401 and the reason code `TOKEN_ALG_NONE`. It is filed under the `verify` layer, which the README maps to `internal/verify`.

I need you to answer or confirm a few things:

- **Separate record:** do you want the separate record? If the README from `adr-authoring 2.0.0` allows amending an Accepted record, I can move R6 into ADR-0007 instead.
- **Rule number:** is R6 the right number? I picked it because ADR-0007 ends at R5. If ADR-0006 or another record already uses R6, tell me the next free number.
- **Owner:** who owns ADR-0008? I left the field as `TBD`.
- **Case:** should `None`, `NONE`, and other casings of `none` also be refused? Attackers use those variants. As written, R6 covers only the lowercase value.
- **Order of checks:** which reason code wins when a token breaks more than one rule? For example, a token with `alg` set to `none` and no `kid` could get `TOKEN_ALG_NONE` or `TOKEN_KID_MISSING`.
- **Back-link:** should I add a line to the Related ADRs section of ADR-0007 that points to ADR-0008? Right now, someone reading ADR-0007 won't find R6.

Separately, the ADR-0006 link in ADR-0007 is broken: it points to `0006-key-sources.md`. I didn't change it as part of this request.

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

I fixed the link in the Related ADRs section of ADR-0007. It pointed to `0006-key-sources.md`, which doesn't exist, and now points to `0006-trusted-key-sources.md`. Nothing else in the file changed.

The link text still reads "ADR-0006: Trust only listed key sources." I couldn't open ADR-0006 to check its actual title. Does that match the heading of ADR-0006? If it doesn't, I'll update the link text to match.
