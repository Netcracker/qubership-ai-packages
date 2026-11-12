## Request 1

### File: docs/adr/0006-verify-token-signatures-before-policy-evaluation.md

````markdown
# Verify the signature of every request token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation decides on the claims that a
token carries. Anyone can write a token with any claims. Only a signature that verifies shows that the claims come from
the party that signed the token.

## Decision

We will verify the signature of every request token before policy evaluation. We will refuse a request token whose
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **request token**: the token that a request to the service carries for the token check. A request that carries no
  token has no request token.
- **unverified signature**: the signature of a request token is unverified when the token carries no signature, or when
  its signature does not verify against the keys and algorithms that the service trusts for token verification. A token
  whose header names the algorithm `none` carries no signature. O1 asks which keys and algorithms the service trusts.

### Rules

#### Signature verification

- **R1** (`verify`). The service verifies the signature of every request token before policy evaluation runs for the
  request.
- **R2** (`verify`, `server`). When a request token has an unverified signature, the service answers the request with
  HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID` in `<where the response carries the reason code>`, and policy
  evaluation does not run for the request.

### Implementation notes

Adds no requirement. Verify the signature in `internal/verify`. Let the handler in `internal/server` call policy
evaluation only with a token that `internal/verify` returns as verified, and map the verification error to the 401
response in `internal/server`.

### Justification

Policy evaluation decides on the claims of a request token, and anyone can write the claims of a token whose signature
is unverified. Verifying the signature first keeps policy evaluation from deciding on forged claims (R1, R2). HTTP 401
is the status for a request whose credentials the server does not accept (RFC 9110, section 15.5.2). A reason code of
its own lets a client or an operator distinguish a bad signature from other refusals (R2).

### Alternatives considered

- **A1. Evaluate policy on the claims of a request token, and verify the signature only when policy allows the
  request.** Rejected by R1: policy evaluation would decide on claims that nobody has verified.

## Consequences

Negative:

- The service verifies a signature for every request that carries a request token, including a request that policy
  evaluation would deny. Each such request costs one signature verification (R1).

## Open points

- **O1.** Which keys and algorithms the service trusts for token verification. Either an existing record already
  decides it, and this record links that record under **Related ADRs**, or a new record on key handling decides it. The
  security architect decides. Affects R1 and R2 through the term **unverified signature**.
- **O2.** Where the 401 response carries the reason code: a field of a JSON body, a response header, or the place
  where an existing record already puts reason codes. The security architect decides. Affects R2.
- **O3.** Which reason code the service answers for a request token that it cannot parse as a signed token, and which
  reason code wins when a request token also fails another check of the service. The answers under consideration are
  `TOKEN_SIGNATURE_INVALID` or a reason code of their own. The security architect decides. Affects R2.
````

### Message to the user

I wrote ADR-0006 for the signature decision and left the `/healthz` decision out of it. The security architect made the
signature decision for security reasons. The platform team made the `/healthz` decision so that Kubernetes can restart
the service. Each of the two would change for its own reason, and in this record the liveness probe would be a rule
that doesn't follow from the title. I suggest a separate record, ADR-0007 "Answer `GET /healthz` with HTTP 200 while the
process runs", owned by the platform team, with its rule tagged `server`. Should I write it?

The record stays `Proposed`. These open points block acceptance:

- O1: which keys and algorithms the service trusts for verification. Does one of ADR-0001 to ADR-0005 already decide
  this?
- O2: where the 401 response carries the reason code. R2 has a placeholder for it.
- O3: which reason code an unparsable token gets, and which reason code wins when a token fails more than one check.

Who owns this record, and what are the GitHub accounts of the owner and the security architect? `Owner` and
`Participants and approvers` still have placeholders.

The reading guide already maps `verify` and `server`, so `docs/adr/README.md` doesn't change.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md

````markdown
# Take token signing keys from the JWKS of trusted key sources, and refuse a token without a `kid`

## Status

Proposed

### Owner

`<GitHub account>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation, and part of that check verifies the token's
signature. A key source publishes its signing keys as a JSON Web Key Set (JWKS, RFC 7517), and each key in the set
carries a key ID, `kid`. The `kid` member of a token's JOSE header (RFC 7515) names the key that signed the token. The
security architect settled where the keys come from, how long the service uses a loaded key set, and what happens to a
token without a `kid` as one decision. A change to key handling changes all three together.

## Decision

We will verify token signatures only with keys from the JWKS of trusted key sources, and use a loaded key set for at
most 5 minutes. We will refuse a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **token**: the token that a request to the service carries for the token check.
- **trusted-key-sources**: the key sources listed in `<path of the trusted key source list>`, each with the URL of its
  JWKS. O2 asks for the path and for what qualifies a key source to join the list.
- **key set**: the JWKS that the service loaded from the JWKS URL of one key source in trusted-key-sources, in one
  load.
- **header without `kid`**: the JOSE header of a token that has no `kid` member, or whose `kid` member is `null` or an
  empty string.

### Rules

#### Key sources

- **R1** (`keys`). The service verifies the signature of a token only with a key from a key set, and with no other key.

#### Key set lifetime

- **R2** (`keys`). The service uses a key set for at most 5 minutes (300 seconds) after it loads the key set, and after
  that loads the key set of that key source again.

#### Tokens without a `kid`

- **R3** (`verify`, `server`). When a token has a header without `kid`, the service answers the request with HTTP 401
  and the reason code `TOKEN_KID_MISSING` in `<where the response carries the reason code>`. It does not verify the
  signature of that token, and policy evaluation does not run for the request. This refusal takes precedence over any
  refusal that signature verification would produce.

### Implementation notes

Adds no requirement. Keep each key set in `internal/keys` with the time of its load, and look up a key by its `kid`.
Let `internal/verify` check the header for a `kid` before it asks `internal/keys` for a key. A key set can be loaded
again when a request needs it, or by a timer in the background.

### Justification

The three choices settle one question: how the service finds the key that verifies a token. A change to key handling
changes all three together, so they share one record (R1, R2, R3). A JWKS lets a key source rotate its keys without a
change to the service (R1). The 5-minute limit bounds how long a key that a key source removed from its JWKS still
verifies tokens (R2). The `kid` selects one key from the key sets. Without a `kid`, the service would have to try every
key of every key set (R3).

### Alternatives considered

- **A1. Configure the signing keys in the service's own configuration.** Rejected by R1: each key rotation would then
  need a change to the service's configuration.
- **A2. Try every key of every key set when a token has a header without `kid`.** Rejected by R3: the cost of
  verification would grow with the number of keys, and the service could not report which key it expected.

## Consequences

Negative:

- An issuer that signs tokens without a `kid` cannot be used with the service (R3).
- A key that a key source removes from its JWKS still verifies tokens for up to 5 minutes, and a key that a key source
  adds verifies tokens only after the next load of its key set (R2).
- When a key source cannot be reached after its key set is 5 minutes old, the service has no key set for that source.
  Tokens signed by that source then fail verification until a load succeeds (R2, O3).

Follow-ups:

- Map `<path of the trusted key source list>` to the `keys` layer in the reading guide.

## Open points

- **O1.** Where the 401 response carries the reason code: a field of a JSON body, a response header, or the place
  where an existing record already puts reason codes. The security architect decides. Affects R3.
- **O2.** The path of the list of trusted key sources, what qualifies a key source to join it, and whether an entry in
  `CODEOWNERS` should require the security architect's approval for a change to the list. With that entry, a rule would
  state it in place of the criterion. The security architect decides. Affects R1.
- **O3.** What the service does when a key set is 5 minutes old and the new load fails. One answer is to refuse tokens
  of that key source, as R2 reads now, with a reason code still to be named. The other is to keep using the old key set
  until a load succeeds, which needs an exception in R2 with a limit. The security architect decides. Affects R2.
- **O4.** R3 assumes that a `kid` member whose value is `null` or an empty string counts as missing, as the term
  **header without `kid`** defines. The security architect confirms or narrows that term. Affects R3.
- **O5.** Where the service takes its verification keys today. If it takes them from another place, such as a key in
  its configuration, R1 removes that place. A rule then has to state what an existing installation gets on upgrade:
  the service stops the start while the list of trusted key sources is empty, or it starts and refuses every token. The
  security architect decides. Affects R1.
````

### Message to the user

I wrote all three choices as one record, ADR-0006, because one authority made them and they change together. The rules
are R1 (keys only from the JWKS of trusted key sources), R2 (a loaded key set is used for at most 5 minutes), and R3
(`TOKEN_KID_MISSING` for a token without a `kid`).

The record stays `Proposed`. These open points block acceptance:

- O1: where the 401 response carries the reason code. R3 has a placeholder for it.
- O2: the path of the list of trusted key sources, what qualifies a source to join it, and whether `CODEOWNERS` should
  gate changes to the list.
- O3: what happens when reloading a key set fails after its 5 minutes are up.
- O4: whether a `kid` that is `null` or an empty string counts as missing. I assumed it does.
- O5: where the service takes its keys today, and what an existing installation gets on upgrade.

Who owns this record, and what are the GitHub accounts of the owner and the security architect? `Owner` and
`Participants and approvers` still have placeholders.

The reading guide already maps `keys`, `verify`, and `server`. Once O2 settles the path of the list, the guide needs
that file mapped to the `keys` layer. I listed this as a follow-up and left `docs/adr/README.md` unchanged for now.
