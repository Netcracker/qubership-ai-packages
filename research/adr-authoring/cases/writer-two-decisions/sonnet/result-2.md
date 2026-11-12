## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse a token whose signature does not verify

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `<account>`: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. The security architect decided that policy
evaluation must not run on a token whose signature was not checked, and that a failed check gets a fixed answer.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does
not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token in the `Authorization` header of a request. O1 asks whether this extent is right.
- **signature does not verify**: the signature check of a token ends in any result other than success, including a token
  that has no signature part. O2 asks whether this extent is right.
- **refuses**: the service sends the stated HTTP status and reason code as the response to the request, and policy
  evaluation does not start for that request.

### Rules

#### Signature verification

- **R1** (`verify`). The service verifies the signature of the token of every request before policy evaluation starts
  for that request.
- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP status 401 and the
  reason code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation then never reads claims from a token whose signature was not checked (R1). One fixed status and
reason code let a caller tell a bad signature from other refusals (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterwards.** Rejected by R1: policy evaluation would read claims
  of an unverified token.
- **A2. Read the claims of a token without checking its signature.** Rejected by R1 and R2.

## Consequences

Negative:

- Every request pays for a signature check before policy evaluation (R1).

## Open points

- **O1.** Which request field carries the token? Assumed: the `Authorization` header. The security architect decides.
  Affects R1, R2.
- **O2.** Does a token with no signature part, or a malformed token, count as a signature that does not verify?
  Assumed: yes. The security architect decides. Affects R2.
- **O3.** How does the response carry the reason code, for example in a body field or in a header? The security
  architect decides. Affects R2.
````

### Message to the user

I wrote ADR-0006 for the signature decision only, with the status `Proposed`.

I did not write the `GET /healthz` decision. The platform team settles it for a different reason than the security architect settles token verification. A liveness probe does not follow from a record about tokens, so it needs its own record, which would be 0007. Do you want me to write it?

Questions:

1. What is the GitHub account of the owner? The record has a placeholder.
2. What is the account of the security architect, who approves R1 and R2?
3. Is the token in the `Authorization` header (O1)?
4. Does a malformed token, or one with no signature, get `TOKEN_SIGNATURE_INVALID` (O2)?
5. How does the response carry the reason code (O3)?

The record stays `Proposed` until these open points are settled and the team signs off.

I tagged R2 with both `verify` and `server`, assuming the 401 response is produced in `internal/server`. Correct it if the code differs.

I also wrote the Justification and Alternatives from the decision itself, because the notes gave no reasons. Please confirm them.

I did not change `README.md`, so the guide is as it was.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-jwks-and-require-kid.md

````markdown
# Take signing keys from the JWKS of each trusted key source, hold them for 5 minutes, and refuse a token with no `kid`

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `<account>`: approves R1 to R3.

## Context

The service verifies the signature of each token against a signing key. The security architect decided three choices
about key handling: where the keys come from, how long a loaded key set is held, and what happens to a token whose header
names no key. These choices change together when the key handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source and hold a loaded key set for 5 minutes. We will
refuse a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **JWKS**: a JSON Web Key Set document, as RFC 7517 defines it.
- **trusted key source**: a key source that the service is configured to trust. O1 asks how the service lists these.
- **loaded key set**: the keys the service parsed from one JWKS document of one trusted key source.
- **header has no `kid`**: the header of the token has no `kid` member.
- **refuses**: the service sends the stated HTTP status and reason code as the response to the request, and policy
  evaluation does not start for that request.

### Rules

#### Key source

- **R1** (`keys`). The service takes the signing keys that it verifies a token with only from the JWKS of each trusted
  key source.

#### Key set lifetime

- **R2** (`keys`). The service uses a loaded key set to verify a token for at most 5 minutes (300 seconds) after the
  service loaded that key set.

#### Token header

- **R3** (`verify`, `server`). The service refuses a token whose header has no `kid` with HTTP status 401 and the reason
  code `TOKEN_KID_MISSING`.

### Justification

A JWKS lets a key source rotate its keys without a change to the service (R1). A bounded hold time limits how long a
retired key stays in use and how often the service fetches a JWKS (R2). A token with no `kid` names no key, so the
service has nothing to select and does not try every key of a set (R3).

### Alternatives considered

- **A1. Configure signing keys statically in the service.** Rejected by R1: a key rotation would need a change to the
  service.
- **A2. Fetch the JWKS again for every token.** Rejected by R2: the service would fetch on every request.
- **A3. Try every key of a loaded key set when the header has no `kid`.** Rejected by R3.

## Consequences

Negative:

- A key that a trusted key source retired stays usable for up to 5 minutes after the service loaded it (R2).
- A token from an issuer that does not set `kid` is refused (R3).

## Open points

- **O1.** How does the service list its trusted key sources, and what qualifies a key source? Assumed: the service takes
  keys from no source outside that list (R1). The security architect decides. Affects R1.
- **O2.** What does the service do when it cannot load a JWKS, or when a loaded key set is older than 5 minutes and the
  reload fails? The security architect decides. Affects R2.
- **O3.** What does the service do with a token whose header has a `kid` that no loaded key set contains? The security
  architect decides. Affects R1, R2.
- **O4.** Does a header with an empty `kid` count as a header with no `kid`? The security architect decides. Affects R3.
- **O5.** How does the response carry the reason code, for example in a body field or in a header? The security
  architect decides. Affects R3.
````

### Message to the user

I wrote one record, ADR-0006, with the status `Proposed`. The three choices come from one authority and change together, so they are one decision.

Questions:

1. What is the GitHub account of the owner? The record has a placeholder.
2. What is the account of the security architect, who approves R1 to R3?
3. How does the service list its trusted key sources (O1)? If the list will grow, I would keep it in one file and add a rule about it. I did not invent a file name.
4. What happens when a JWKS fails to load, or the reload fails after 5 minutes (O2)?
5. What happens to a token whose `kid` is in no loaded key set (O3)?
6. Does an empty `kid` count as a missing `kid` (O4)?
7. How does the response carry the reason code (O5)?

Assumptions I made:

- "Each trusted key source" means the service takes keys only from those sources, which is stated in R1 and in O1.
- The 5 minutes count from the time the service loaded the key set (R2).
- I tagged R3 with both `verify` and `server`, assuming `internal/server` produces the 401 response. Correct it if the code differs.
- I wrote the Justification and Alternatives from the decision itself, because the notes gave no reasons. Please confirm them.

The record stays `Proposed` until the open points are settled and the team signs off. I did not change `README.md`.
