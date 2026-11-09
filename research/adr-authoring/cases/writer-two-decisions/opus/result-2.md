## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves the decision and R1–R2.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation decides on the claims of that
token, such as its subject and its scopes. Anyone can write the claims of an unsigned token or change the claims of a
signed one. The service can rely on the claims only after the token's signature verifies.

The security architect decided that the service verifies the signature of every token before policy evaluation. The
decision also fixes how the service refuses a token whose signature does not verify.

## Decision

We will verify the signature of the token in every request before policy evaluation. We will refuse a request whose
token signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the bearer token in the `Authorization` header of a request.
- **signature does not verify**: verification of a token's signature ends in any result other than success. This
  includes a token with no signature, a token with a malformed signature, a token whose `alg` is `none`, a token whose
  signature does not match the signing key, and a token whose signing key the service cannot find.

### Rules

#### Order

- **R1** (`verify`). For a request that carries a token, the service runs policy evaluation only after the signature of
  that token has verified.

#### Refusal

- **R2** (`verify`, `server`). When the signature of the token in a request does not verify, the service refuses the
  request with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID` in `<response field that carries the reason
  code>`.

### Justification

Policy evaluation decides on the claims of a token. If the signature has not verified, any caller can write those
claims and steer the policy decision. Verifying first means that policy evaluation reads only claims that the issuer
signed (R1).

A fixed status and a fixed reason code let a caller and an operator tell a signature failure apart from a policy denial,
and let a test assert the outcome (R2).

### Alternatives considered

- **A1. Run policy evaluation first, and verify the signature only for a request that the policy allows.** Rejected by
  R1: policy evaluation would read claims from an unverified token, so a caller could control both its result and the
  time it takes.
- **A2. Decode the token claims without verifying the signature, and leave signature verification to a gateway in front
  of the service.** Rejected by R1: the service would then trust every component on the path to it.
- **A3. Refuse a token whose signature does not verify with HTTP 403.** Rejected by R2: HTTP 401 reports a missing or
  invalid credential, and HTTP 403 reports a valid credential that lacks permission.

## Consequences

Negative:

- Every request that carries a token costs one signature verification before policy evaluation, including a request
  that policy evaluation would deny (R1).
- A caller whose token signature does not verify gets HTTP 401 with `TOKEN_SIGNATURE_INVALID`, even for a request that
  policy evaluation would allow (R2). To show it, change one byte in the signature of a valid token, send the request,
  and expect HTTP 401 and `TOKEN_SIGNATURE_INVALID`.

## Open points

- **O1.** Where the token sits in a request. The rules assume the bearer token in the `Authorization` header. The other
  answer is a definition that one of ADR-0001 to ADR-0005 already gives, if one does. The security architect decides.
  Affects R1 and R2.
- **O2.** Which part of the 401 response carries the reason code. The answers under consideration are a field of a JSON
  body, such as `reason`, a response header, or the field that an existing record already defines for refusals. The
  security architect decides. Affects R2.
- **O3.** The extent of **signature does not verify**. The record assumes that it includes a token whose `alg` is `none`
  and a token whose signing key the service cannot find. The other answer gives those cases their own reason codes in a
  separate record. The security architect decides. Affects R2.
````

### Message to the user

I wrote ADR-0006 for the security architect's decision only. The notes contain two decisions. The security architect
settled token signature verification for security reasons. The platform team settled `GET /healthz` so that Kubernetes
can restart the service. Each one has its own authority and its own reason to change, so a liveness rule doesn't belong
in a record about tokens.

I'd write the second one as ADR-0007, "Answer `GET /healthz` with HTTP 200 while the process runs", with its rule in the
`server` layer and the platform team as approver. **Do you want me to write it?**

ADR-0006 stays `Proposed` until these are settled:

- **Owner and approver:** which GitHub accounts should go in **Owner** and **Participants and approvers**? Right now
  they're placeholders.
- **O1:** where does the token sit in a request? I assumed the bearer token in `Authorization`.
- **O2:** which response field carries `TOKEN_SIGNATURE_INVALID`? R2 has a placeholder for it.
- **O3:** should a token with `alg: none`, or a token whose signing key can't be found, also count as "signature does
  not verify"? I assumed yes.
- **Related records:** does any of ADR-0001 to ADR-0005 already define the token or the format of a refusal response?
  If one does, I'll link it under **Related ADRs** and use its definition.

The reading guide already maps `verify` and `server`, so `docs/adr/README.md` doesn't need to change.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md

````markdown
# Take token signing keys from the JWKS of each trusted key source

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves the decision and R1–R4.

## Context

token-gate checks the token of each request before policy evaluation. To verify a token's signature, the service needs
the key that signed it. Issuers publish their public keys as a JWKS (JSON Web Key Set, RFC 7517) and rotate them over
time.

The security architect decided three things for token verification: where the service takes signing keys from, how
long it holds a loaded key set, and how it refuses a token whose header has no `kid`. All three change together when key
handling changes, so this record holds all three.

## Decision

We will take the keys that verify token signatures from the JWKS of each trusted key source and hold each loaded key set
for 5 minutes. We will refuse a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **token**: the bearer token in the `Authorization` header of a request.
- **trusted key source**: a key source whose JWKS URL is listed in `<setting that lists the trusted key sources>`. A URL
  that is not in that setting is not a trusted key source, including a `jku` or `x5u` URL in a token header.
- **key set**: the keys returned by one load of the JWKS of one trusted key source.
- **header without `kid`**: a JOSE header of a token that has no `kid` member, or whose `kid` value is not a non-empty
  string.

### Rules

#### Key sources

- **R1** (`keys`). The service takes the keys it verifies token signatures with from the JWKS of each trusted key
  source, and from no other source.
- **R2** (`keys`). When `<setting that lists the trusted key sources>` lists no trusted key source, the service
  `<outcome for an installation with no trusted key source>`.

#### Key set lifetime

- **R3** (`keys`). The service holds a key set for 5 minutes (300 seconds) after it loads that key set. Within those 5
  minutes, the service verifies tokens with the held key set and does not load the JWKS of that trusted key source
  again. Once the 5 minutes have passed, the service verifies no token with the held key set.

#### Tokens without `kid`

- **R4** (`verify`, `server`). When the token in a request has a header without `kid`, the service refuses the request
  before policy evaluation, with HTTP 401 and the reason code `TOKEN_KID_MISSING` in `<response field that carries the
  reason code>`.

### Justification

A JWKS lets an issuer add and rotate keys without a redeployment of the service. Limiting the service to the JWKS of
trusted key sources means that a token can't name the key it is verified with (R1).

An installation with no trusted key source has no key to verify any token with. A rule fixes what such an installation
gets on upgrade, so that its outcome doesn't depend on the code path that runs first (R2).

Holding a key set for 5 minutes limits each trusted key source to one load per 5 minutes. It also limits how long the
service keeps using a key that the source has removed from its JWKS (R3).

The `kid` selects one key from the key sets of all trusted key sources. Without it, the service would have to try every
key, and the cost of verification would grow with the number of keys (R4).

### Alternatives considered

- **A1. Load the key from the `jku` or `x5u` URL in the token header.** Rejected by R1: the token would name its own
  key source.
- **A2. Configure the signing keys as static PEM files in the service configuration.** Rejected by R1: every key
  rotation would need a configuration change and a restart.
- **A3. Load the JWKS on every request, with no cache.** Rejected by R3: every request would load each trusted key
  source.
- **A4. Try every key of every key set against a token whose header has no `kid`.** Rejected by R4: the cost of
  verification grows with the number of keys.

## Consequences

Negative:

- After a trusted key source removes a key from its JWKS, the service keeps verifying tokens with that key for up to 5
  minutes (R3).
- After a trusted key source adds a key to its JWKS, the service can't verify tokens signed with that key for up to 5
  minutes (R3).
- A caller whose token header has no `kid` gets HTTP 401 with `TOKEN_KID_MISSING` (R4). To show it, send a token whose
  header is `{"alg":"RS256","typ":"JWT"}` and expect HTTP 401 and `TOKEN_KID_MISSING`.
- An existing installation with no trusted key source configured gets the outcome of R2 on upgrade.

## Open points

- **O1.** Where the token sits in a request. The rules assume the bearer token in the `Authorization` header. The other
  answer is a definition that one of ADR-0001 to ADR-0005 already gives, if one does. The security architect decides.
  Affects R4.
- **O2.** The name and format of the setting that lists the trusted key sources. R1 and R2 hold a placeholder for it.
  The security architect and the maintainers decide. Affects R1 and R2.
- **O3.** What an installation with no trusted key source gets. The answers under consideration are that the service
  exits before it serves a request, or that it starts and refuses every token with HTTP 401. The security architect
  decides. Affects R2.
- **O4.** Which part of the 401 response carries the reason code. The answers under consideration are a field of a JSON
  body, such as `reason`, a response header, or the field that an existing record already defines for refusals. The
  security architect decides. Affects R4.
- **O5.** What the service does when the 5 minutes of R3 have passed and the reload of a JWKS fails. The answers under
  consideration are refusing every token that needs a key from that source, or keeping the expired key set until a load
  succeeds. The second answer changes R3. The security architect decides. Affects R3.
- **O6.** Whether a token whose `kid` matches no held key triggers an early load. The record assumes it does not, so
  R3 forbids a load within the 5 minutes. The other answer allows one early load per source, with a minimum interval
  between loads. The security architect decides. Affects R3.
- **O7.** The extent of **header without `kid`**. The record assumes that an empty or non-string `kid` counts as
  missing. The other answer refuses those tokens under another reason code. The security architect decides. Affects R4.
````

### Message to the user

I wrote this as one record, ADR-0006. The security architect settled all three choices for one reason, and they change
together when key handling changes, so splitting them would separate rules that get edited together.

ADR-0006 stays `Proposed` until these are settled:

- **Owner and approver:** which GitHub accounts should go in **Owner** and **Participants and approvers**? Right now
  they're placeholders.
- **O1:** where does the token sit in a request? I assumed the bearer token in `Authorization`.
- **O2:** which setting lists the trusted key sources, and in what format?
- **O3:** what should an installation with no trusted key source get on upgrade? It can exit before it serves a request,
  or it can start and refuse every token.
- **O4:** which response field carries `TOKEN_KID_MISSING`?
- **O5:** if a JWKS reload fails after the 5 minutes, should the service refuse tokens from that source or keep the
  expired key set?
- **O6:** may an unknown `kid` trigger an early reload? I assumed no.
- **O7:** should an empty or non-string `kid` count as missing? I assumed yes.
- **Related records:** does any of ADR-0001 to ADR-0005 already define the token, the key sources, or the format of a
  refusal response? If one does, I'll link it under **Related ADRs** and use its definitions.

The reading guide already maps `keys`, `verify`, and `server`, so `docs/adr/README.md` doesn't need to change.
