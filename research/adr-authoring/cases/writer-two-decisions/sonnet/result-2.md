## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# We verify the signature of every token before policy evaluation and refuse a token that fails

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `<account>`: approves the decision.

## Context

The service checks the token of each request before policy evaluation. A token whose signature is not verified can
carry claims that anyone wrote, and policy evaluation reads those claims.

## Decision

We will verify the signature of each token before policy evaluation, and we will refuse a token whose signature does not
verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **signature does not verify**: the signature check of a token fails, or the service cannot complete it for any reason.

### Rules

#### Signature check

- **R1** (`verify`). For each request on which the service checks a token, the service verifies the signature of that
  token before policy evaluation starts for that request.
- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP 401 and the reason
  code `TOKEN_SIGNATURE_INVALID`, and policy evaluation does not start for the request that carries it.

### Justification

Policy evaluation reads token claims, so the claims are trustworthy only if the signature has verified first (R1). A
token that fails the check must not reach policy evaluation, and the caller needs a stable code to tell this refusal
from others (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterwards.** Rejected by R1: policy evaluation would read
  claims that no one has authenticated.
- **A2. Let a token whose signature cannot be checked continue to policy evaluation.** Rejected by R2: the term
  **signature does not verify** includes a check that cannot be completed.

## Consequences

Negative:

- A token whose signature check cannot be completed is refused, so a failure to complete the check, for example in key
  handling, turns valid tokens away with HTTP 401 (R2).

## Open points

- **O1.** The notes do not say whether a token whose signature check cannot be completed (no key found, unsupported
  algorithm) is refused with `TOKEN_SIGNATURE_INVALID` or with another code. The record assumes the former. The
  security architect decides. Affects R2.
````

### Message to the user

The notes hold two decisions: signature verification (the security architect) and `GET /healthz` liveness (the platform team). They have different deciding authorities and different reasons to change, so they need two records. I wrote only the signature record, as ADR-0006. I did not write the `/healthz` record. If you want it, it becomes ADR-0007 with the platform team as approver, and I can draft it next.

Before this can leave `Proposed`:

- Who is the owner (GitHub account)? Which account is the security architect's? Both are placeholders in the file.
- Open point O1: should a token whose signature check cannot be completed also get `TOKEN_SIGNATURE_INVALID`? I assumed yes.

I tagged R2 with both `verify` and `server`, because I assumed `verify` decides the refusal and `server` sends the 401. Please confirm. I did not see records 0001 to 0005, so I linked none. If one of them overlaps, tell me and I'll add it under Related ADRs. The reading guide needs no change.

## Request 2

### File: docs/adr/0006-token-verification-key-handling.md

````markdown
# We take signing keys from the JWKS of trusted key sources, hold them for 5 minutes, and refuse a token without `kid`

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `<account>`: approves the decision.

## Context

The service verifies the signature of a token with a signing key. The service has to decide where those keys come from,
how long it keeps a loaded key set, and what it does with a token whose header does not name a key. These three choices
change together when the key handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **trusted key source**: a source of signing keys that the service configuration lists as trusted.
- **loaded key set**: the keys that the service obtained from the JWKS of one trusted key source in one load.

### Rules

#### Key source

- **R1** (`keys`). The service obtains every signing key that it uses to verify a token from the JWKS of a trusted key
  source.

#### Key set lifetime

- **R2** (`keys`). The service uses a loaded key set for at most 5 minutes (300 seconds) after its load completes. After
  that, the service loads the JWKS of that trusted key source again before it uses a key from that source.

#### Token header

- **R3** (`verify`, `server`). The service refuses a token whose header has no `kid` with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

The JWKS of a trusted key source publishes the keys that the source signs with, so the service needs no key material of
its own (R1). A bounded lifetime limits how long a key that a source has rotated out stays in use, and it keeps the
number of JWKS requests low (R2). A token that names no key cannot be matched to one key of a set (R3). The three choices
belong to one decision because a change to key handling edits them together (R1, R2, R3).

### Alternatives considered

- **A1. Try every key of a loaded key set when the token header has no `kid`.** Rejected by R3: the service refuses the
  token instead.

## Consequences

Negative:

- A key that a trusted key source removes stays usable for up to 5 minutes, until the loaded key set expires (R2).
- A token without `kid` is refused, even where the loaded key set holds a single key (R3).

## Open points

- **O1.** The notes do not say where the list of trusted key sources comes from. The record assumes the service
  configuration. The security architect decides. Affects R1 and R2.
- **O2.** The notes do not say what the service does when the reload after 5 minutes fails: refuse tokens from that
  source, or keep using the expired key set. The security architect decides. Affects R2.
- **O3.** The notes do not say whether a token with an empty `kid` counts as having no `kid`. The record assumes that it
  does not, so R3 covers only a missing member. The security architect decides. Affects R3.
````

### Message to the user

This is one decision. One authority settles all three choices, and they change together, so I wrote one record, ADR-0006. The status is `Proposed` until the open points are settled.

Questions for you:

- Who is the owner (GitHub account)? Which account is the security architect's? Both are placeholders in the file.
- O1: does the service configuration list the trusted key sources?
- O2: when a reload fails after 5 minutes, does the service refuse tokens from that source or keep using the expired key set? I wrote no rule for this, because the notes do not say.
- O3: does a token with an empty `kid` count as having no `kid`?
- I tagged R3 with `verify` and `server`, assuming `verify` decides the refusal and `server` sends the 401. Please confirm.

The notes give no reasons. The Justification and alternative A1 are my inference from the rules, so please check them against what the security architect decided. I did not see records 0001 to 0005, so I linked none. If one of them overlaps, I'll add it under Related ADRs. The reading guide needs no change.
