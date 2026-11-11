## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation, and refuse a token whose signature does not verify

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 and R2.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation decides on the claims of the
token. A claim is only as trustworthy as the signature over it: anyone can write a token with any claims, and only the
signature shows that a trusted issuer wrote those claims.

## Decision

We will verify the signature of every token before policy evaluation, and refuse a token whose signature does not verify
with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that the service checks for a request before policy evaluation.
- **signature verifies**: the token carries a signature, and that signature checks against a signing key the service
  trusts, under the algorithm of that key. A token with no signature, such as one whose header names the algorithm
  `none`, has no signature that verifies. O1 asks which keys and algorithms the service trusts.

### Rules

#### Signature verification

- **R1** (`verify`). For every request that carries a token, the service verifies the signature of the token before
  policy evaluation runs for that request.
- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP status 401 and the
  reason code `TOKEN_SIGNATURE_INVALID`, and policy evaluation does not run for the request that carried that token.

### Justification

Policy evaluation decides on the claims of a token. If it ran on a token with an unverified signature, it would decide on
claims that anyone could have written (R1). A fixed status and reason code let a client and an operator tell a signature
failure apart from other refusals (R2).

### Alternatives considered

- **A1. Run policy evaluation first, and verify the signature only for a request that policy evaluation allows.**
  Rejected by R1: policy evaluation would then run on claims whose issuer is not established.
- **A2. Answer a token whose signature does not verify with HTTP 403.** Rejected by R2: the request failed
  authentication, and HTTP 401 is the status for that.

## Consequences

Negative:

- A client that sends a token without a signature, or with a signature under a key the service does not trust, now gets
  HTTP 401 with `TOKEN_SIGNATURE_INVALID` instead of a policy decision (R2).

## Open points

- **O1.** Which signing keys the service trusts, and which algorithms it accepts, fixes the extent of **signature
  verifies**. The answers under consideration: state the accepted algorithms and the key sources as rules in this
  record, or settle them in a separate record about key handling and point at it from the term. The security architect
  decides. Affects R1 and R2.
````

### Message to the user

I wrote ADR-0006 for the security architect's decision only. The notes hold two decisions, made by different authorities that change them for different reasons. A liveness probe also doesn't follow from a record about token signatures, so it belongs in its own record.

**Proposed split:** a second record, ADR-0007, "Answer `GET /healthz` with HTTP 200 while the process runs", owned by the platform team with a rule tagged `server`. Should I write it? If so, please tell me whether `GET /healthz` has to answer without a token. That would be an exception to ADR-0006 R1 and R2, and one of the two records has to state it.

**Questions on ADR-0006:**

1. Who owns the record, and what are the GitHub accounts of the owner and the security architect? I left placeholders for both.
2. O1 has to be settled before the record can be `Accepted`: which signing keys and algorithms count as a signature that verifies? Should they go in this record or in a separate record about key handling?
3. Should the HTTP 401 status be set in `internal/verify` or in `internal/server`? I tagged R2 with both layers because I couldn't read the code.

The record stays `Proposed`. No reading-guide change is needed, because the layers `verify` and `server` are already mapped.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md

````markdown
# Take signing keys from the JWKS of trusted key sources, hold a key set for 5 minutes, and refuse a token without `kid`

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation, and verifying its signature takes a signing key.
Each issuer that the service trusts publishes its signing keys as a JSON Web Key Set (JWKS, RFC 7517). An issuer rotates
its keys, so a key set the service loaded once goes stale. A token names the key that signed it in the `kid` parameter of
its JOSE header. The service can select a key from a key set only by that parameter.

The source of signing keys, the time a loaded key set stays in use, and the handling of a token without `kid` change
together whenever the key handling changes, so this record settles all three.

## Decision

We will take signing keys only from the JWKS of each trusted key source and use a loaded key set for 5 minutes at most.
A token whose header has no `kid` gets HTTP 401 with the reason code `TOKEN_KID_MISSING`.

### Terms

- **token**: the token that the service checks for a request before policy evaluation.
- **trusted-key-sources**: the key sources listed in `<trusted key sources file>`. O1 asks for that file and for what
  qualifies a source to join.
- **trusted key source**: a member of trusted-key-sources.
- **JWKS**: the JSON Web Key Set that a key source publishes.
- **key set**: the signing keys that the service parsed from one load of the JWKS of one trusted key source.

### Rules

#### Key sources

- **R1** (`keys`). The service takes every signing key it uses for token verification from the JWKS of a trusted key
  source, and from no other source.

#### Key set lifetime

- **R2** (`keys`). The service loads the JWKS of one trusted key source at most once in 5 minutes. It verifies no token
  with a key set that it loaded more than 5 minutes earlier.

#### Tokens without `kid`

- **R3** (`verify`, `server`). The service refuses a token whose JOSE header has no `kid` parameter, or whose `kid` is
  an empty string, with HTTP status 401 and the reason code `TOKEN_KID_MISSING`. Policy evaluation does not run for the
  request that carried that token.

### Implementation notes

Adds no requirement. Keep one key set per trusted key source in `internal/keys`. Record the load time with each key set,
and load the JWKS again on the first verification after 5 minutes. Read `kid` in `internal/verify` before the key lookup.

### Justification

A key from any source other than a trusted key source would let whoever controls that source sign tokens the service
accepts (R1). A bound on the age of a key set limits how long the service keeps accepting a key that its source has
withdrawn. A bound on how often the service loads a JWKS keeps a stream of tokens from turning into a stream of requests
to the key source (R2). Without `kid`, the service cannot select a key from a key set by the token itself (R3).

### Alternatives considered

- **A1. Configure signing keys as static PEM files in the service configuration.** Rejected by R1: such a key comes
  from no trusted key source, and a key rotation would take a deployment.
- **A2. Load the JWKS again for every token, or whenever a token names a `kid` that the key set lacks.** Rejected by
  R2: either way, the service would load a JWKS more often than once in 5 minutes.
- **A3. Try every key in the key set when a token has no `kid`.** Rejected by R3.

## Consequences

Negative:

- A key that a trusted key source publishes is accepted only after the next load, up to 5 minutes later. Until then, a
  token signed with that key fails verification (R2).
- Once a key set is more than 5 minutes old and the JWKS cannot be loaded again, the service verifies no token from
  that key source (R2). O2 asks what the service answers then.
- A client whose tokens carry no `kid` gets HTTP 401 with `TOKEN_KID_MISSING` (R3).

## Open points

- **O1.** Which file holds trusted-key-sources, and what qualifies a key source to join. The answers under consideration:
  a criterion a checker can test from the repository, stated as a rule in this record; or a security review, stated in
  the term **trusted-key-sources**, together with a rule that requires an entry in `CODEOWNERS` for the file. The
  security architect decides. Affects R1.
- **O2.** What the service answers for a token whose key source has a key set older than 5 minutes and whose JWKS fails
  to load. The answers under consideration: HTTP 401 with the reason code of a signature that does not verify, or HTTP
  503 with a reason code of its own. The security architect decides. Affects R2.
- **O3.** R3 assumes that a `kid` given as an empty string counts as missing. The security architect confirms this or
  rejects it. Affects R3.
````

### Message to the user

I wrote ADR-0006 as one record, because one authority made all three choices and they change together.

Before the record can be `Accepted`, I need these answers:

1. Who owns the record, and what are the GitHub accounts of the owner and the security architect? I left placeholders.
2. **O1:** Which file lists the trusted key sources, and what qualifies a source to join the list? Should it be a criterion the repository can check, or a security review backed by a `CODEOWNERS` entry for that file?
3. **O2:** When a key set is older than 5 minutes and the JWKS can't be loaded, should the service answer HTTP 401 or HTTP 503, and with which reason code?
4. **O3:** Should an empty `kid` count as missing? I assumed it does.
5. I read "holds a loaded key set for 5 minutes" as a bound in two directions. The service doesn't use a key set older than 5 minutes, and it doesn't load a source's JWKS more than once in 5 minutes, so an unknown `kid` doesn't trigger an early reload. Is that what the security architect meant?
6. Should the HTTP 401 status be set in `internal/verify` or in `internal/server`? I tagged R3 with both layers because I couldn't read the code.

The record stays `Proposed`. No reading-guide change is needed, because the layers `keys`, `verify`, and `server` are already mapped.
