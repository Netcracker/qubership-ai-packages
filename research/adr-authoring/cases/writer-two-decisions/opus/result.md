## Request 1

### File: docs/adr/0006-verify-token-signatures-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation decides on the claims that a
token carries. Anyone who sends a request can put any claims into a token. Only a signature that verifies shows that
the holder of a signing key issued those claims.

## Decision

We will verify the signature of every token before policy evaluation. We will refuse a token whose signature does not
verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that token-gate checks for a request before policy evaluation.
- **policy evaluation**: the step that decides from a token's claims whether token-gate admits the request.
- **signature does not verify**: covers three kinds of token. The first is a token whose signature fails the check
  against every key and algorithm that token-gate accepts for it (O2). The second is a token with no signature. The
  third is a token whose header names the algorithm `none`.

### Rules

#### Order of checks

- **R1** (`verify`, `server`). token-gate verifies the signature of the token of every request before policy evaluation
  receives the request.

#### Refusal

- **R2** (`verify`, `server`). When the signature of a token does not verify, token-gate responds to the request with
  HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID` in `<response field for the reason code>`, and policy
  evaluation does not receive the request.

### Implementation notes

Adds no requirement. Put the signature check in `internal/verify`. Have the handler chain in `internal/server` call
the check before it calls policy evaluation, so that one place maps a failed check to the HTTP 401 response.

### Justification

A token whose signature has not verified can carry claims that no key holder issued, so policy evaluation receives a
request only after the signature check (R1). HTTP 401 tells the client that token-gate did not accept its credentials,
and that a new token may succeed (R2). A reason code of its own lets a client or an operator tell a bad signature
apart from other refusals without reading the logs (R2).

### Alternatives considered

- **A1. Pass the token to policy evaluation with a flag that marks its signature as unverified, and let the policy
  refuse it.** Rejected by R2: policy evaluation receives the request.
- **A2. Refuse a token whose signature does not verify with HTTP 403.** Rejected by R2: HTTP 403 means that the client
  is known and lacks permission, and a token with a bad signature does not identify a client.

## Consequences

Negative:

- A client that sends a token whose signature does not verify gets the response of R2, even where policy evaluation
  would have allowed the request.
- Every request with a token costs a signature check, including a request that policy evaluation would refuse anyway.

Follow-ups:

- Write a record that decides which keys and algorithms make a signature verify (O2).

## Open points

- **O1.** Where the reason code goes in the response: a field of the JSON response body, such as `reason`, or a
  response header. The security architect decides. Affects R2.
- **O2.** Which keys and algorithms make a signature verify: a list in this record, or a separate record about key
  handling that this record points at. The security architect decides. Affects R1 and R2.
- **O3.** The definition of **signature does not verify** assumes that a token with no signature, or with the algorithm
  `none`, gets `TOKEN_SIGNATURE_INVALID`. The other answer is a separate reason code for an unsigned token. The
  security architect decides. Affects R2.
````

### Message to the user

I wrote ADR-0006 for the signature decision only. The `/healthz` decision comes from a different authority (the platform team) and changes for a different reason (Kubernetes liveness), so it belongs in its own record. A liveness rule in a record about tokens would also be hard for anyone to find later. I suggest ADR-0007, "Answer `GET /healthz` with HTTP 200 while the process runs". Do you want me to write it?

ADR-0006 stays `Proposed` until these questions are answered:

1. Who owns the record, and what is the security architect's GitHub account? There are placeholders for both.
2. O1: where does the response carry the reason code? Is it a JSON body field, such as `reason`, or a header? If one of the records 0001 to 0005 already sets this, tell me which one and I'll cite it.
3. O2: which keys and algorithms count as a valid signature? Should this record decide that, or a separate key-handling record?
4. O3: should a token with no signature, or with `alg: none`, get `TOKEN_SIGNATURE_INVALID`? Or should it get its own code?
5. Does token-gate verify signatures today? If it doesn't, some existing clients will get a different response. I'd add that case to **Negative**, along with the test that shows it.

The notes didn't give the justification or the two alternatives. I wrote them myself, so please confirm or correct them. I didn't change `docs/adr/README.md`, because both rules fall in layers it already maps.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks-and-require-kid.md

````markdown
# Verify tokens with keys from the JWKS of trusted key sources, and refuse a token without `kid`

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 to R5.

## Context

token-gate checks the token of each request before policy evaluation. Checking the signature of a token needs the
public key that signed it. A key source publishes its signing keys as a JWKS (RFC 7517), a JSON document that lists
keys and identifies each one by its `kid`. A token names the key that signed it in the `kid` parameter of its JOSE
header. Key sources rotate their keys, so a key that token-gate loaded can be removed or replaced later.

## Decision

We will take the signing keys that token-gate verifies tokens with from the JWKS of each trusted key source, and hold
a loaded key set for 5 minutes. We will refuse a token whose header has no `kid` with HTTP 401 and the reason code
`TOKEN_KID_MISSING`.

### Terms

- **token**: the token that token-gate checks for a request before policy evaluation.
- **policy evaluation**: the step that decides from a token's claims whether token-gate admits the request.
- **key source**: a party that publishes its signing keys as a JWKS at a URL.
- **trusted-key-sources**: the key sources listed in `<path of the trusted key source list>`. R2 states how a key
  source joins.
- **key set**: the keys that token-gate parsed from one load of the JWKS of one key source.
- **header without `kid`**: a JOSE header that has no `kid` parameter, or whose `kid` value is not a non-empty string.
- **stops the start**: the process exits before it serves a request. `internal/keys` meets this by returning an error
  when it loads trusted-key-sources.

### Rules

#### Key sources

- **R1** (`keys`). token-gate verifies the signature of a token only with a key from a key set of a key source in
  trusted-key-sources. It uses no other key, such as a key in its own configuration, a key in the `jwk` header
  parameter, or a key behind a URL in the `jku` or `x5u` header parameter.
- **R2** (`keys`). A key source joins trusted-key-sources only through a pull request that changes
  `<path of the trusted key source list>` and that the security architect approves.
- **R3** (`keys`, `server`). When trusted-key-sources lists no key source, token-gate stops the start.

#### Key set lifetime

- **R4** (`keys`). Once token-gate loads the JWKS of a key source in trusted-key-sources, it verifies tokens with the
  resulting key set for 5 minutes without loading that JWKS again. It verifies no token with that key set once
  5 minutes have passed since the load.

#### Tokens without `kid`

- **R5** (`verify`, `server`). When a token has a header without `kid`, token-gate responds to the request with
  HTTP 401 and the reason code `TOKEN_KID_MISSING` in `<response field for the reason code>`, and policy evaluation
  does not receive the request.

### Implementation notes

Adds no requirement. Load trusted-key-sources in `internal/keys` at start, and keep one key set per key source with
its load time. Have `internal/verify` read `kid` from the header before it asks `internal/keys` for a key, so that a
token without `kid` never causes a JWKS load.

### Justification

Keys from the JWKS that a key source publishes let the source rotate its keys without a change to token-gate. Taking
keys only from trusted key sources stops a token from naming its own key (R1). A list in a file lets a key source join
in one pull request. A list in this record would take a new record for each key source (R2). An empty list would leave
token-gate unable to verify any token, so it stops the start instead (R3). Holding a key set for 5 minutes limits how
many JWKS requests token-gate sends to each key source. It also limits how long a key that a source has removed stays
usable (R4). Without a `kid`, token-gate would have to try every key of every key source, so it refuses such a token
before any key lookup (R5). All three choices change together when the key handling changes, so they share one record.

### Alternatives considered

- **A1. Configure each public key in token-gate as a PEM file.** Rejected by R1: the key does not come from the JWKS
  of a trusted key source, and every key rotation would take a change to token-gate.
- **A2. Load the key from the `jwk`, `jku`, or `x5u` parameter of the token header.** Rejected by R1: the sender of the
  token would choose the key that verifies it.
- **A3. Load the JWKS again for every token.** Rejected by R4.
- **A4. Try each key of each trusted key source in turn when a token has no `kid`.** Rejected by R5.

## Consequences

Positive:

- A key source rotates its keys by publishing a new JWKS, and token-gate picks up the new key within 5 minutes without
  a deployment.

Negative:

- A client whose token has a header without `kid` gets the response of R5, even where a key of a trusted key source
  would verify its signature.
- A key that a key source removes from its JWKS stays usable for up to 5 minutes after the removal (R4).
- A key that a key source adds to its JWKS stays unusable until the next load, which can take up to 5 minutes (R4).
- An installation whose trusted-key-sources list is empty after the upgrade stops the start (R3).

Follow-ups:

- Map `<path of the trusted key source list>` to the `keys` layer in `docs/adr/README.md`.

## Open points

- **O1.** The path and format of the file that lists trusted-key-sources. It is needed in **Terms** and R2. The
  security architect decides.
- **O2.** Where the response carries the reason code: a field of the JSON response body, such as `reason`, or a
  response header. The security architect decides. Affects R5.
- **O3.** R4 assumes that a token whose `kid` matches no key in a held key set does not cause an early load of the
  JWKS. The other answer is an early load, limited to `<number of loads>` per `<interval>`. The security architect
  decides. Affects R4.
- **O4.** What token-gate does when a load of a JWKS fails after the 5 minutes have passed. One answer is to refuse
  every token from that key source, with a status and a reason code still to be named. The other is to keep using the
  old key set for a grace period of `<duration>`. The security architect decides. Affects R4.
- **O5.** R2 assumes that the security architect approves each new key source. The security architect confirms this
  or names another approver. Affects R2.
- **O6.** R3 assumes that an empty trusted-key-sources stops the start. The other answer is that token-gate starts and
  refuses every token. The security architect decides. Affects R3.
- **O7.** The definition of **header without `kid`** assumes that an empty or non-string `kid` counts as missing. The
  other answer is to treat such a `kid` as present and let the key lookup fail. The security architect decides.
  Affects R5.
- **O8.** Where token-gate looks up a `kid`. One answer is in the key sets of all trusted key sources. The other is
  only in the key set of the key source that matches the token's `iss` claim. The security architect decides. Affects
  R1.
````

### Message to the user

I wrote this as one record, ADR-0006. The three choices have one authority (the security architect), and your notes say they change together, so the skill keeps them as one decision.

ADR-0006 stays `Proposed` until these questions are answered:

1. Who owns the record, and what is the security architect's GitHub account? There are placeholders for both.
2. O1: where does the list of trusted key sources live, and in what format?
3. O2: where does the response carry the reason code? Is it a JSON body field, such as `reason`, or a header? If one of the records 0001 to 0005 already sets this, tell me which one and I'll cite it.
4. O3: when a `kid` matches no key in the held key set, should token-gate reload the JWKS before the 5 minutes are up? I assumed it doesn't.
5. O4: what happens when a reload fails after 5 minutes? Should token-gate refuse tokens from that key source (and with which status and code), or keep the old key set for a grace period?
6. O5 and O6: I assumed two things. First, the security architect approves each new key source. Second, an empty list of trusted key sources stops the service from starting. Are both right?
7. O7: should an empty or non-string `kid` count as missing?
8. O8: should token-gate look up a `kid` across all trusted key sources, or only in the key source that matches the token's `iss`?

The notes didn't give the justification, the alternatives, or the limit in R1 that rules out keys named in the token header. I wrote them myself, so please confirm or correct them. Once the path of the list is decided, it needs to be mapped to the `keys` layer in `docs/adr/README.md`. I don't have that file's content, so I listed this as a follow-up instead of editing the file.
