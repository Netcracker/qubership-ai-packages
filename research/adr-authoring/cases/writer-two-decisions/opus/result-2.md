## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every request token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account of the security architect>`: approves R1 to R3.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation decides from the claims of
the token whether the request may proceed. A claim is only as trustworthy as the signature over it: anyone can write a
token with any claims, and only the signature shows that a trusted issuer wrote them.

## Decision

We will verify the signature of every request token before policy evaluation, and refuse a request token whose
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **request token**: the bearer token in the `Authorization` header of a request to the service (O1).
- **verifies**: the signature of a request token verifies when the service checks it with a key that the service
  trusts for that token, under an algorithm that the service accepts, and the check succeeds. A request token with no
  signature, such as one whose header sets `alg` to `none`, does not verify. Which keys and algorithms count is open
  (O2).

### Rules

#### Verification

- **R1** (`verify`). The service runs policy evaluation for a request that carries a request token only after the
  signature of that request token verifies.

#### Refusal

- **R2** (`verify`, `server`). When the signature of a request token does not verify, the service answers the request
  with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.
- **R3** (`verify`). When the signature of a request token does not verify and another check of the same request token
  fails as well, the service answers with the reason code `TOKEN_SIGNATURE_INVALID` and not with the reason code of the
  other check.

### Justification

An unverified request token lets any caller write the claims that policy evaluation relies on, so policy evaluation
waits for the signature (R1). HTTP 401 reports failed authentication, which tells the client to get a new token. HTTP
403 would report an identity that is known and denied, and the service knows no identity from a token it cannot
verify (R2). The claims of a token whose signature does not verify come from nobody the service trusts, so the
service reports the signature failure and not a fact about those claims, such as an expiry the sender wrote (R3).

### Alternatives considered

- **A1. Evaluate policy on the decoded claims, and verify the signature afterward or in parallel.** Rejected by R1:
  policy evaluation would run on claims that nobody vouched for.
- **A2. Rely on a signature check that an upstream gateway or proxy has done.** Rejected by R1: the term "verifies"
  requires that the service itself checks the signature.
- **A3. Answer HTTP 403 for a request token whose signature does not verify.** Rejected by R2.

## Consequences

Positive:

- Logs and metrics can count forged and corrupted tokens apart from other refusals by the reason code
  `TOKEN_SIGNATURE_INVALID`.

Negative:

- The service spends a signature check on every request that carries a request token, including requests that policy
  evaluation would deny.

## Open points

- **O1.** Which input carries the request token. The record assumes the bearer token in the `Authorization` header.
  The security architect confirms it or names another header. Affects R1 to R3.
- **O2.** Which keys and which algorithms count when a signature verifies. Answers under consideration: the keys and
  algorithms that the `keys` layer provides today; a fixed list stated in this record; or a separate record about key
  handling. The security architect decides. Affects R1 and R2.
- **O3.** Where the response carries the reason code. The record assumes the same place as the reason codes of the
  service's other refusals. The security architect confirms it or names a field. Affects R2 and R3.
- **O4.** Whether the signature failure takes precedence over every other failed check of the same token. The record
  assumes it does (R3). The security architect confirms it or names the order. Affects R3.
- **O5.** What the service does with a request that carries no request token. R1 covers only requests that carry one.
  Answers under consideration: refuse it with HTTP 401 and a reason code of its own, or settle it in another record.
  The security architect decides. Affects R1.
````

### Message to the user

These notes hold two decisions, so I wrote only one of them as a record. ADR-0006 covers the signature check, which the security architect decided. `GET /healthz` is the platform team's decision and has a different reason: it serves Kubernetes restarts, not token security. That means it needs its own record. Should I write it as the next record, "Answer `GET /healthz` with HTTP 200 while the process runs"? It would be ADR-0007 if 0006 merges first.

Some questions for ADR-0006:

- **Owner and approver:** who owns the record, and what is the security architect's GitHub account? I left placeholders for both.
- **Status:** the record stays `Proposed` until the security architect settles O1 to O5:
  - **O1:** which header carries the token. The record assumes `Authorization`.
  - **O2:** which keys and algorithms count as a verified signature.
  - **O3:** where the response carries the reason code.
  - **O4:** whether `TOKEN_SIGNATURE_INVALID` takes precedence over other token failures.
  - **O5:** what happens to a request with no token.
- **Existing clients:** does any client today get past the check with a token whose signature does not verify? If so, they will start getting HTTP 401. If you name that case, I'll add it under **Negative**, along with the test that shows it.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md

````markdown
# Take token-signing keys only from the JWKS of trusted key sources, and refuse a token without `kid`

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account of the security architect>`: approves R1 to R4.

## Context

The service checks the token of each request before policy evaluation, and it checks the signature of the token with
a signing key. An issuer of tokens publishes its signing keys as a JSON Web Key Set (JWKS, RFC 7517), and rotates them
by publishing a new set. A token names the key that signed it with the `kid` member of its header. Where the keys come
from, how long a loaded set is used, and how a token selects its key all change together when key handling changes, so
this record holds all three.

## Decision

We will take the keys that verify request tokens only from the JWKS of each trusted key source, use a loaded key set
for at most 5 minutes, and refuse a request token whose header has no `kid` with HTTP 401 and the reason code
`TOKEN_KID_MISSING`.

### Terms

- **request token**: the bearer token in the `Authorization` header of a request to the service (O1).
- **key source**: an issuer of request tokens that publishes its signing keys as a JWKS at a URL.
- **trusted-key-sources**: the key sources listed in `<file that lists the trusted key sources>`. R2 states how a key
  source joins.
- **key set**: the keys that the service parsed from one load of the JWKS of one key source.
- **`kid` missing**: the JOSE header of a request token has no `kid` member (O5).

### Rules

#### Key sources

- **R1** (`keys`, `verify`). The service verifies the signature of a request token only with a key from a key set of a
  key source in trusted-key-sources. A key from any other place, such as a key in the token header (`jwk`, `x5c`) or a
  key at a URL that the token names (`jku`, `x5u`), never verifies a request token.
- **R2** (`keys`). A key source joins trusted-key-sources only through a pull request that
  `<approver of trusted key sources>` approves.

#### Loaded key sets

- **R3** (`keys`). The service uses a key set to verify request tokens for at most 5 minutes (300 seconds) after it
  loaded that key set.

#### Tokens without `kid`

- **R4** (`verify`, `server`). When `kid` is missing from a request token, the service answers the request with HTTP
  401 and the reason code `TOKEN_KID_MISSING`, and does not run policy evaluation for that request.

### Justification

A JWKS lets an issuer rotate its keys without a change to the service (R1, R3). A key that the token carries or points
at would let the sender choose the key that verifies its own token (R1). A list in a file lets a key source join in one
pull request, where a list in this record would take a new record for each source (R2). The 5-minute limit bounds how
long a key that an issuer withdrew still verifies tokens (R3). Without `kid` the service would have to try every key
it trusts, and a token's own header would no longer name the key that signed it (R4).

### Alternatives considered

- **A1. Accept a key from the token header (`jwk`, `x5c`) or fetch one from a URL that the token names (`jku`,
  `x5u`).** Rejected by R1.
- **A2. Configure signing keys as static key files in the service configuration.** Rejected by R1: such a key comes
  from no key set.
- **A3. Load each JWKS once at start and keep it until the process restarts.** Rejected by R3.
- **A4. Try every key of every trusted key source when `kid` is missing.** Rejected by R4.

## Consequences

Negative:

- An issuer that signs tokens without `kid` cannot be a key source until it adds `kid` to its tokens (R4).
- A key that an issuer withdrew keeps verifying tokens for up to 5 minutes after the withdrawal (R3).
- Each instance of the service loads the JWKS of each key source at least once every 5 minutes while it verifies
  tokens from that source, which puts a steady load on every issuer's JWKS endpoint (R3).

## Open points

- **O1.** Which input carries the request token. The record assumes the bearer token in the `Authorization` header.
  The security architect confirms it or names another header. Affects R1 and R4.
- **O2.** Which file lists trusted-key-sources, what qualifies a key source to join, and who approves a new one.
  The security architect decides. Affects R1 and R2.
- **O3.** How the service selects the key source for a request token. Answers under consideration: by the token's
  `iss` claim, then by `kid` within that source's key set; or by `kid` alone across every trusted key source. The
  security architect decides. Affects R1.
- **O4.** What the service does when a reload is due or fails. Answers under consideration: a request token with an
  unknown `kid` triggers a reload before 5 minutes have passed, or it does not; after a failed reload, the service
  refuses request tokens from that key source, or a later record adds a grace period to R3. The security architect
  decides. Affects R3.
- **O5.** Whether a `kid` member whose value is an empty string counts as missing. The security architect decides.
  Affects R4.
- **O6.** Where the response carries the reason code. The record assumes the same place as the reason codes of the
  service's other refusals. The security architect confirms it or names a field. Affects R4.
````

### Message to the user

I wrote ADR-0006 as one record. The security architect decided all three choices, and they change together, so they're one decision.

Some questions:

- **Owner and approvers:** who owns the record, and what is the security architect's GitHub account? I left placeholders for both.
- **R2 placeholders:** where should the list of trusted key sources live, and who approves a new source? R2 carries placeholders for both, and O2 tracks them.
- **Status:** the record stays `Proposed` until the security architect settles O1 to O6:
  - **O1:** which header carries the token. The record assumes `Authorization`.
  - **O2:** where the list of trusted key sources lives, what qualifies a source, and who approves one.
  - **O3:** how the service picks a token's key source, by `iss` or by `kid` alone.
  - **O4:** whether an unknown `kid` may trigger an early reload, and what happens when a reload fails.
  - **O5:** whether an empty `kid` counts as missing.
  - **O6:** where the response carries the reason code.
- **Upgrade behavior:** where do the signing keys come from today? If an existing installation uses keys from another place, R1 changes what it trusts. The record then needs a rule for what that installation gets on upgrade, and a **Negative** entry that cites it.
- **Tokens without `kid`:** does any issuer in use today sign tokens without `kid`? If so, its tokens will start getting HTTP 401, and I'll name that case and its test under **Negative**.
