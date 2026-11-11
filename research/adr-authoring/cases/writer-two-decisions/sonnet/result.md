## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse a token with an invalid signature

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `<account>`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation reads its input from the token.
A token whose signature has not been verified gives no assurance about who issued it or whether its content changed.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does
not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token a request carries. O1 asks where a request carries it.
- **refuse**: the service answers the request with the stated HTTP status and reason code, and policy evaluation does
  not run for the request.

### Rules

#### Verification

- **R1** (`verify`). For every request that carries a token, the service verifies the signature of the token before
  policy evaluation of that request starts.

#### Refusal

- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP 401 and the
  reason code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation reads the content of the token, and that content can be trusted only after the signature verifies
(R1). A refusal with a fixed status and reason code lets a client tell a bad signature from other failures (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterwards.** Rejected by R1: a decision could be made from
  content that is not yet verified.

## Consequences

Negative:

- Every request that carries a token pays for a signature verification before policy evaluation (R1).

## Open points

- **O1.** Where does a request carry the token (for example the `Authorization` header), and which requests carry none?
  The security architect decides. Affects R1 and R2.
- **O2.** Which response field carries the reason code `TOKEN_SIGNATURE_INVALID`? The security architect decides.
  Affects R2.
- **O3.** The record assumes that the `verify` layer decides the refusal and the `server` layer writes the response. The
  security architect or the maintainers of `internal/verify` and `internal/server` confirm. Affects the layer tags of
  R2.
- **O4.** Does a token that has no signature, or that names an algorithm the service does not support, count as a token
  whose signature does not verify? The security architect decides. Affects R2.
````

### Message to the user

The notes hold two decisions, and I wrote only the first as ADR-0006. The signature rule comes from the security architect. The `GET /healthz` liveness probe comes from the platform team and changes for a different reason, so it needs its own record. I left it out and did not write ADR-0007. Do you want me to write it?

The ADR is `Proposed`. Please give me:

- the owner's GitHub account and the security architect's account, which I left as placeholders;
- answers to O1 to O4, which cover where the token is carried, which field holds the reason code, which layer writes the response, and how unsigned tokens are treated.

I read no existing records, so the metadata block follows the template and may need adjusting to match records 0001 to 0005. No check exists for either rule, so there is no Confirmation section. The reading guide is unchanged.

## Request 2

### File: docs/adr/0006-token-signing-keys-from-jwks-with-kid.md

````markdown
# Take token signing keys from the JWKS of each trusted key source, hold them for 5 minutes, and require a `kid`

## Status

Proposed

### Owner

<owner GitHub account>

### Participants and approvers

- Security architect, `<account>`: approves R1 to R3.

## Context

token-gate verifies the signature of each token before policy evaluation. Verification needs the signing key that
matches the token. The way the service obtains, holds, and selects its signing keys changes as one piece whenever key
handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **trusted key source**: a key source that the service is set up to trust. O1 asks how this set is defined and who
  approves a new member.
- **key set**: the keys in the JWKS that the service loaded from one trusted key source.
- **refuse**: the service answers the request with the stated HTTP status and reason code, and policy evaluation does
  not run for the request.

### Rules

#### Key sources

- **R1** (`keys`). The service takes every signing key it uses for token verification from the JWKS of a trusted key
  source, and from no other source.

#### Holding keys

- **R2** (`keys`). The service holds a key set for 5 minutes, counted from the moment it loaded the key set.

#### Tokens without a `kid`

- **R3** (`verify`, `server`). The service refuses a token whose header has no `kid` with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

The JWKS is the standard format in which a key source publishes its keys, so the service needs no other key format
(R1). A held key set spares the service a JWKS load for each token (R2). A token with no `kid` cannot be matched to a key
in the key set (R3).

### Alternatives considered

- **A1. Take signing keys from a static key configured in the service.** Rejected by R1: key rotation at a key source
  would need a change to the service.
- **A2. Load the JWKS again for every token.** Rejected by R2: each token would cost a request to the key source.
- **A3. Try every key of the key set on a token with no `kid`.** Rejected by R3.

## Consequences

Positive:

- A change to key handling edits one record, because the key source, the holding time, and the `kid` requirement
  belong to one decision.

Negative:

- A key that a key source withdraws can still verify tokens until the service's key set expires, which is at most 5
  minutes (R2).
- A token that carries no `kid` is refused even where the key set holds a single key (R3).

## Open points

- **O1.** How is the set of trusted key sources defined, and who approves a new member? The security architect decides.
  Affects R1.
- **O2.** What does the service do when it fails to load a key set after the 5 minutes pass: refuse the tokens, or keep
  using the expired key set? The security architect decides. Affects R2.
- **O3.** Does a token whose `kid` is not in the key set cause an early reload of that key set, or is it refused at
  once? The security architect decides. Affects R2.
- **O4.** Which response field carries the reason code `TOKEN_KID_MISSING`? The security architect decides. Affects R3.
- **O5.** The record assumes that the `verify` layer decides the refusal and the `server` layer writes the response. The
  security architect or the maintainers of `internal/verify` and `internal/server` confirm. Affects the layer tags of
  R3.
````

### Message to the user

I wrote one record, ADR-0006. The key source, the 5-minute holding time, and the `kid` requirement come from one authority and change together, so they stay in one record. The status is `Proposed`.

Please give me:

- the owner's GitHub account and the security architect's account, which I left as placeholders;
- answers to O1 to O5, which cover how trusted key sources are defined, what happens when a reload fails or a `kid` is unknown, which field holds the reason code, and which layer writes the response.

I read no existing records, so the metadata block follows the template and may need adjusting to match records 0001 to 0005. No check exists for any rule, so there is no Confirmation section. The reading guide is unchanged.
