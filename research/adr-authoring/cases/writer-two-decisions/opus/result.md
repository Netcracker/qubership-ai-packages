## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation decides whether the request may proceed. Policy
evaluation reads the claims in the token. Anyone who can send a request can write any claims into a token. Only a valid
signature shows that the claims come from the issuer that signed them.

## Decision

We will verify the signature of every token before policy evaluation. The service will refuse a request whose token
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the bearer token in the `Authorization` header of a request to the service.
- **unverified token**: a token whose signature does not verify. It includes a token that carries no signature and a
  token whose header names the algorithm `none`. O2 asks which algorithms and keys make a signature verify.

### Rules

#### Signature verification

- **R1** (`verify`, `server`). For every request that carries a token, the service verifies the signature of that token
  before policy evaluation runs for that request.
- **R2** (`verify`, `server`). For a request that carries an unverified token, the service responds with HTTP 401 and
  the reason code `TOKEN_SIGNATURE_INVALID`, and policy evaluation does not run for that request.

### Implementation notes

Adds no requirement. Put the signature check in `internal/verify`, and let `internal/server` call it in the request path
ahead of policy evaluation for every route, so that no route reaches policy evaluation without it. A test that sends a
token signed with an unknown key and a token with `alg: none`, and asserts the status, the reason code, and that policy
evaluation was not called, covers R1 and R2.

### Justification

Policy evaluation decides on the claims in a token, and only a verified signature shows that an issuer wrote those
claims (R1). Verification on every request leaves no route where forged claims reach policy evaluation (R1). HTTP 401
tells the client that its credentials failed, which a policy denial does not. A reason code of its own lets clients and
operators tell a bad signature apart from other refusals without parsing a message (R2).

### Alternatives considered

- **A1. Verify the signature only on routes that policy evaluation marks as sensitive.** Rejected by R1: a forged token
  on any other route reaches policy evaluation.
- **A2. Pass an unverified token to policy evaluation and deny it there with HTTP 403.** Rejected by R2: policy
  evaluation runs on forged claims, and 403 reports accepted credentials with denied access.

## Consequences

Negative:

- Every request that carries a token pays for a signature verification before policy evaluation, including requests
  that policy evaluation would deny.
- A client that sends an unverified token gets HTTP 401 on every route (R2), including routes where policy evaluation
  would allow the request.

## Open points

- **O1.** Which token R1 and R2 cover. The rules assume the bearer token in the `Authorization` header. Another answer
  also covers a token in a cookie or in another header. The security architect decides. Affects **token**, R1, and R2.
- **O2.** Which algorithms and which keys make a signature verify. The notes name neither. One answer is a fixed list of
  algorithms, such as `RS256` and `ES256`, with keys from configured key sources. Another answer is to leave keys to a
  separate record about key handling. The security architect decides. Affects **unverified token**, R1, and R2.
- **O3.** Where the response carries the reason code. R2 assumes the field that the service's existing error responses
  use for reason codes. The other answers are a new body field or a response header. The security architect decides.
  Affects R2.
````

### Message to the user

I've written ADR-0006 for the security architect's decision only. The notes hold two decisions, and they need separate records. Each has its own authority (the security architect and the platform team) and its own reason to change (token security and Kubernetes restarts). A liveness probe in a record about tokens would also be hard to find later.

**I suggest a second record for the health check.** It would be ADR-0007, "Answer `GET /healthz` with HTTP 200 while the process runs". It would have one rule tagged `server`, and the platform team would approve it. Do you want me to write it?

**Questions:**

1. Which GitHub accounts should go in as the owner and as the security architect for ADR-0006? I used placeholders.
2. Do ADR-0001 to 0005 refuse tokens for other reasons, such as expiry? If so, which reason code should a token get when it fails more than one check?
3. I couldn't see ADR-0001 to 0005, so I took the metadata block from the template. If their metadata looks different, I'll copy theirs.

**Before acceptance:** the record stays `Proposed` until O1 (which token), O2 (which algorithms and keys make a signature verify) and O3 (where the reason code goes in the response) are answered.

I tagged the rules with layer names from the reading guide, not from reading the code. Once someone checks where the 401 response is built, the tags may need changing.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks.md

````markdown
# Take token signing keys from the JWKS of trusted key sources, and require a `kid`

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 to R3.

## Context

The service verifies the signature of each token before policy evaluation, so it needs the public keys of the issuers
it trusts. An issuer publishes its signing keys as a JSON Web Key Set (JWKS, RFC 7517). It rotates a key by publishing a
new key set. A token names the key that signed it in the `kid` header parameter (RFC 7515). A token header can also
carry a key or a key location in the `jwk`, `jku`, `x5c`, and `x5u` parameters. Loading a JWKS for every token would
add an HTTP request to a key source to every request the service handles.

The three choices in this record change together when the key handling changes.

## Decision

We will verify token signatures only with keys from the JWKS of trusted key sources. The service will use each loaded
key set for 5 minutes, and it will refuse a token whose header has no `kid` with HTTP 401 and the reason code
`TOKEN_KID_MISSING`.

### Terms

- **token**: a token whose signature the service verifies before policy evaluation.
- **trusted key source**: a token issuer listed in `<path of the trusted key source list>`, with the location of its
  JWKS. O1 asks what qualifies a source.
- **key set**: the keys that the service took from the JWKS of one trusted key source in one load.
- **token without `kid`**: a token whose header has no `kid` parameter, or has a `kid` parameter whose value is not a
  non-empty string.

### Rules

#### Key sources

- **R1** (`keys`, `verify`). The service verifies the signature of a token only with a key from a key set. It uses no
  other key. This includes a key in a configuration file, and a key or key location that the token carries in its
  `jwk`, `jku`, `x5c`, or `x5u` header parameter.

#### Key set lifetime

- **R2** (`keys`). After the service loads the key set of a trusted key source, it does not load the key set of that
  source again within 5 minutes of the load. It does not use that key set to verify a token more than 5 minutes after
  the load.

#### Tokens without `kid`

- **R3** (`verify`, `server`). For a request that carries a token without `kid`, the service responds with HTTP 401 and
  the reason code `TOKEN_KID_MISSING`. It does so before it looks up a key for that token and before policy evaluation
  runs for that request.

### Implementation notes

Adds no requirement. Keep one key set per trusted key source in `internal/keys`, together with the time of its load. Give
that code a clock that tests can replace, so that a test for R2 can move time forward without waiting 5 minutes. Read
the `kid` in `internal/verify` before asking `internal/keys` for a key.

### Justification

A JWKS lets an issuer rotate its keys without a change to the service (R1). A key that a token carries, or a key that
the token points at, lets anyone who can make a key sign a token that verifies, so the service takes no key from the
token (R1). A 5-minute lifetime limits the load on each key source to one load in 5 minutes. It also limits how long a
key that an issuer removed stays usable to 5 minutes (R2). With a `kid`, the lookup finds one key. Without one, the
service would try every key of every key set. The reason code lets an operator tell an issuer that leaves out `kid`
apart from other refusals (R3).

### Alternatives considered

- **A1. Verify with the key in the token's `jwk` header, or load the JWKS from the token's `jku` URL.** Rejected by R1:
  the sender of the token chooses the key.
- **A2. Configure issuer public keys as PEM files in the service configuration.** Rejected by R1: every key rotation
  needs a configuration change and a deployment.
- **A3. Load the JWKS of the key source for every token.** Rejected by R2: every request waits for the key source, and
  the key source carries the request rate of the service.
- **A4. Try every key of every key set when a token has no `kid`.** Rejected by R3: verification cost grows with the
  number of keys, and an issuer that leaves out `kid` goes unnoticed.

## Consequences

Negative:

- After an issuer removes a key from its JWKS, the service accepts tokens signed with that key for up to 5 minutes
  (R2).
- After an issuer adds a key to its JWKS, a token signed with the new key fails verification for up to 5 minutes, until
  the next load (R2).
- The service cannot use a token issuer whose tokens carry no `kid` until that issuer adds one (R3).
- Verification depends on the JWKS endpoint of each trusted key source answering at least once every 5 minutes (R2).

## Open points

- **O1.** Where the list of trusted key sources lives, and what qualifies a source. One answer is a file in the
  repository with a `CODEOWNERS` entry for the security architect, and a rule that requires that entry. The other is a
  deployment setting outside the repository. The security architect decides. Affects **trusted key source** and R1.
- **O2.** What the service does when it loads a key set again and the load fails. R2 as written stops the use of the
  old key set after 5 minutes, so tokens from that source fail verification. The other answer keeps the old key set for
  a longer, stated time. The security architect decides. Affects R2.
- **O3.** Whether a token whose `kid` names no key in a held key set makes the service load that key set again before 5
  minutes pass. R2 as written does not allow it. The other answer allows one early load, with a minimum interval
  between such loads. The security architect decides. Affects R2.
- **O4.** Whether an empty `kid` counts as missing. **token without `kid`** assumes it does. The other answer refuses an
  empty `kid` with another reason code. The security architect decides. Affects R3.
- **O5.** Where the response carries the reason code. R3 assumes the field that the service's existing error responses
  use for reason codes. The other answers are a new body field or a response header. The security architect decides.
  Affects R3.
````

### Message to the user

I've written ADR-0006 as a single record. The three choices have one authority (the security architect) and one reason to change (key handling), and the notes say they change together.

**Questions:**

1. Which GitHub accounts should go in as the owner and as the security architect? I used placeholders.
2. Where should the list of trusted key sources live? I used a placeholder path, and O1 asks what qualifies a source. If it's a file in the repository, I suggest a `CODEOWNERS` entry for the security architect and a rule that requires that entry.
3. I couldn't see ADR-0001 to 0005, so I took the metadata block from the template. If their metadata looks different, I'll copy theirs.

**Before acceptance:** the record stays `Proposed` until O1 to O5 are answered. They cover:

- the list of trusted key sources
- what happens when a reload fails
- whether an unknown `kid` triggers an early reload
- whether an empty `kid` counts as missing
- where the reason code goes in the response

I tagged the rules with layer names from the reading guide, not from reading the code. Once someone confirms where the key lookup and the 401 response are built, the tags may need changing.
