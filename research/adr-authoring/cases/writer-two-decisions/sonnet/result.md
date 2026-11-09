## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# We will verify the signature of every token before policy evaluation and refuse a token whose signature does not verify

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect (`<GitHub account>`): approves the decision.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads claims from that token.
A claim is only as trustworthy as the signature that covers it.

## Decision

We will verify the signature of the token of every request before policy evaluation, and refuse a token whose signature
does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that a request presents to the service for checking.
- **signature does not verify**: the token has no signature, or its signature does not match its content under the
  signature check.
- **refuses a token**: the service sends the response that the rule names for the request, and does not start policy
  evaluation for it.

### Rules

#### Signature verification

- **R1** (`verify`). The service verifies the signature of the token of each request before policy evaluation starts for
  that request.
- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify, with HTTP 401 and the reason
  code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation then never sees a claim from a token whose signature failed (R1). A caller can tell a failed signature
from other 401 causes by its reason code (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterward.** Rejected by R1: policy evaluation would read claims
  that nothing has authenticated.

## Consequences

Negative:

- Every request pays for one signature verification before policy evaluation (R1).
- A token with a failed signature gets HTTP 401 even where policy would have allowed the request (R2).

## Open points

- **O1.** Where the response carries the reason code (a body field, a header, or both), and under which name. The
  security architect decides. Affects R2.
- **O2.** Assumption: the signature check runs in `internal/verify` and the HTTP response is written in
  `internal/server`, so R2 carries both layer tags. The owner confirms against the code. Affects R2.
````

### Message to the user

I wrote one record, from the security architect's decision. The notes hold two decisions, and I left out the second.

- **Split:** the `GET /healthz` liveness probe is the platform team's decision and changes for a different reason, so it needs its own record, for example `0007-answer-healthz-while-the-process-runs.md`. Do you want me to write it?
- **Questions for you:**
  - What are the GitHub accounts of the owner and of the security architect? The record has placeholders for them.
  - Where does the response carry `TOKEN_SIGNATURE_INVALID`: a body field, a header, or both (O1)?
  - Does the signature check run in `internal/verify` and the response get written in `internal/server` (O2)?
- **Status:** the record is `Proposed` because O1 and O2 are open. Once the team signs off and they are closed, set it to `Accepted` and add `### Date`.
- **Reading guide:** `docs/adr/README.md` already exists with the layer map, so I did not change it.
- **Existing records:** I could not read ADRs 0001 to 0005, so I added no **Related ADRs** entry. Tell me if one of them touches token checks.
- **Justification and A1:** the notes gave no reasons, so I inferred these. Please confirm them.
- **Trailers:** the change that implements this carries `Implements: ADR-0006 R1, R2`.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-each-trusted-key-source.md

````markdown
# We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a token without a kid

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect (`<GitHub account>`): approves the decision.

## Context

The service verifies the signature of each token, and verification needs the signing key that matches the token. Key
issuers publish their keys as a JWKS (JSON Web Key Set), and they change those keys over time. The token header carries
the `kid` that names the key to use.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`. The three choices are one
decision because they change together when the key handling changes.

### Terms

- **trusted key source**: an issuer whose JWKS the service is configured to load. No other issuer is a trusted key
  source.
- **loaded key set**: the set of keys that the service has loaded from the JWKS of one trusted key source.
- **token**: the token that a request presents to the service for checking.
- **refuses a token**: the service sends the response that the rule names for the request, and does not start policy
  evaluation for it.

### Rules

#### Key sources

- **R1** (`keys`). The service loads signing keys from the JWKS of each trusted key source, and from no other source.

#### Key set lifetime

- **R2** (`keys`). The service uses a loaded key set to verify tokens for 5 minutes after it loaded that key set, and
  loads the JWKS of that trusted key source again before it verifies a later token with it.

#### Key identifier

- **R3** (`verify`, `server`). The service refuses a token whose header has no `kid`, with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

A JWKS lets an issuer change its keys without a change to the service, and a closed list of sources limits whose keys
the service trusts (R1). The 5 minute limit bounds how long a key that an issuer has withdrawn stays usable, and how
often the service fetches a JWKS (R2). The `kid` is what selects one key from a key set, so a token without it cannot
be matched to a key (R3).

### Alternatives considered

- **A1. Try every key of the key set when the header has no `kid`.** Rejected by R3: the service would verify a token
  against keys that the token never named.

## Consequences

Negative:

- A key that an issuer withdraws stays usable for up to 5 minutes after the service loaded its key set (R2).
- Verification depends on a trusted key source being reachable at each reload (R2).
- A token without a `kid` gets HTTP 401 even where its issuer publishes one key (R3).

## Open points

- **O1.** Where the list of trusted key sources is configured and how a source is named. The security architect decides.
  Affects R1.
- **O2.** What the service does when a reload of a JWKS fails: refuse tokens at once, or keep using the expired key set
  for a limit. The security architect decides. Affects R2.
- **O3.** Where the response carries the reason code (a body field, a header, or both), and under which name. The
  security architect decides. Affects R3.
- **O4.** Assumption: the key loading and holding run in `internal/keys`, the `kid` check runs in `internal/verify`, and
  the HTTP response is written in `internal/server`, so R3 carries two layer tags. The owner confirms against the code.
  Affects R1, R2, R3.
````

### Message to the user

I wrote one record. The three choices come from one deciding authority and change together, so they stay together as R1, R2, and R3.

- **Questions for you:**
  - What are the GitHub accounts of the owner and of the security architect? The record has placeholders for them.
  - Where is the list of trusted key sources configured (O1)?
  - What happens when a JWKS reload fails (O2)? R2 needs this to be testable, and the notes did not say.
  - Where does the response carry `TOKEN_KID_MISSING` (O3)?
  - Do `internal/keys`, `internal/verify`, and `internal/server` hold the code as I assumed (O4)?
- **Status:** the record is `Proposed` because O1 to O4 are open. Once the team signs off and they are closed, set it to `Accepted` and add `### Date`.
- **Reading guide:** `docs/adr/README.md` already exists with the layer map, so I did not change it.
- **Existing records:** I could not read ADRs 0001 to 0005, so I added no **Related ADRs** entry. If one of them decides part of this, I would add it, and I would supersede that part rather than edit the old record.
- **Justification and A1:** the notes gave no reasons, so I inferred these. Please confirm them.
- **Trailers:** the change that implements this carries `Implements: ADR-0006 R1, R2, R3`. If a change leaves one out, it goes under `Defers` with an existing issue or pull request.
