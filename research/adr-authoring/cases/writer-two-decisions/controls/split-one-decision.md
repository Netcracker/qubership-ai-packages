## Request 1

### File: docs/adr/0006-verify-token-signatures-before-policy-evaluation.md

````markdown
# Verify the signature of every request token before policy evaluation

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<account>`: approves the decision.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims in that token.
Until the service verifies the token's signature, anyone could have written those claims. The security architect
decided that the service verifies every signature, and that it refuses a token whose signature does not verify.

## Decision

We will verify the signature of every request token before policy evaluation. We will refuse a request token whose
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **request token**: the token that the service reads from a request and checks before policy evaluation. A request
  that carries no token has no request token.
- **verifies**: a signature verifies when it is valid for the token's header and payload under a signing key that the
  service trusts for that token. A token with no signature has a signature that does not verify. This includes a token
  whose header names the algorithm `none`.

### Rules

#### Signature verification

- **R1** (`verify`). The service verifies the signature of every request token before policy evaluation receives the
  request.
- **R2** (`verify`, `server`). When the signature of a request token does not verify, the service responds with HTTP
  401 and the reason code `TOKEN_SIGNATURE_INVALID`, and policy evaluation does not receive the request. This response
  applies even when the request token also fails another check of the service.

### Justification

The claims of a request token are only as trustworthy as its signature. Policy evaluation that reads claims from an
unverified token decides on input that an attacker controls (R1).

HTTP 401 means that the request lacks valid authentication credentials. A token with an invalid signature
authenticates no one. A reason code of its own lets clients and operators tell a forged or corrupted token apart from
other refusals (R2).

The other checks read claims that an invalid signature leaves unverified. A reason code from one of those checks would
describe content that may be forged, so the signature failure takes precedence (R2).

### Alternatives considered

- **A1. Verify the signature after policy evaluation, or only when policy evaluation asks for it.** Rejected by R1:
  policy evaluation would read the claims of a token that may be forged.
- **A2. Respond with HTTP 403 to a token whose signature does not verify.** Rejected by R2: HTTP 403 states that the
  client is authenticated and lacks permission.
- **A3. Report the reason code of whichever check runs first.** Rejected by R2: a token that fails an earlier check,
  such as expiry, would hide that its signature is invalid.

## Consequences

Negative:

- Every request token costs one signature verification, which adds CPU time to every request (R1).
- Some clients may now receive HTTP 401 with `TOKEN_SIGNATURE_INVALID` for a request token that the service accepted
  before this record. This applies to any request token whose signature does not verify. A test that sends a token
  signed with a key the service does not trust shows the change (R2).
- A request token that fails signature verification and another check gets only `TOKEN_SIGNATURE_INVALID`. The client
  sees the other failure only once it sends a correctly signed token (R2).

## Open points

- **O1.** Which signing keys the service trusts for a request token. The record assumes the keys that the `keys` layer
  provides. The security architect decides between confirming that assumption and naming the trusted key sources in
  this record or in another one. Affects the term **verifies**, and through it R1 and R2.
- **O2.** Where the response carries the reason code. The record assumes the response field in which the service
  already reports the reason code of a refused token. The security architect decides between confirming that field and
  naming another one. Affects R2.
- **O3.** Whether a signature that does not verify takes precedence over every other check of a request token. The
  record assumes that it does. The security architect decides between confirming this precedence and naming checks
  whose reason code wins over `TOKEN_SIGNATURE_INVALID`. Affects R2.
````

### Message to the user

Your notes cover two decisions, and I wrote a record for only one of them. The security architect decided the token signature check. The platform team decided the `GET /healthz` liveness answer. The two decisions have different owners and change for different reasons. A liveness probe also has nothing to do with a record about tokens, so a reader looking for it would not find it there.

I wrote `docs/adr/0006-verify-token-signatures-before-policy-evaluation.md` with status `Proposed`. Should I write the health check as its own record, `docs/adr/0007-answer-healthz-while-the-process-runs.md`, owned by the platform team?

For ADR-0006, I need:

- **Owner and approver:** the GitHub account of the owner, and the account of the security architect who approves it.
- **O1:** Does a signature have to verify against the keys that `internal/keys` provides, or against named key sources?
- **O2:** In which response field does the reason code go?
- **O3:** Should `TOKEN_SIGNATURE_INVALID` take precedence over every other refusal reason?

The record stays `Proposed` until all three open points are settled.

I didn't change `docs/adr/README.md`. The guide already maps both layers the record uses (`verify` and `server`).

## Request 2

### File: docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md

````markdown
# Take signing keys from the JWKS of each trusted key source

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<account>`: approves the decision.

## Context

The service verifies the signature of each request token with a signing key before policy evaluation. The security
architect decided three things for token verification:

- where the signing keys come from;
- how long the service uses a loaded key set;
- how the service treats a request token whose header names no key.

All three change together when the key handling changes, so this record holds them as one decision.

## Decision

We will take signing keys only from the JWKS of each trusted key source, and hold a loaded key set for 5 minutes. We
will refuse a request token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **request token**: the token that the service reads from a request and checks before policy evaluation.
- **trusted key source**: a key source that the service configuration lists as trusted. Every other key source is
  untrusted, including any key source that a request token names in its header or payload.
- **JWKS**: a JSON Web Key Set, as RFC 7517 section 5 defines it, that a trusted key source publishes.
- **key set**: the signing keys that the service loaded in one load from the JWKS of one trusted key source.

### Rules

#### Key sources

- **R1** (`keys`). The service verifies the signature of a request token only with a signing key from the key set of a
  trusted key source. A signing key from any other place goes unused, including a key that the request token carries
  in its header.
- **R4** (`keys`). When the service configuration lists no trusted key source, the service `<outcome with no trusted
  key source>`.

#### Key set lifetime

- **R2** (`keys`). After the service loads the key set of a trusted key source, it uses that key set for 5 minutes (300
  seconds). The service doesn't load that source's JWKS again within those 5 minutes. After those 5 minutes, it loads
  that source's JWKS again before it uses a key of that source to verify a request token.

#### Tokens without a key ID

- **R3** (`verify`, `server`). When the header of a request token has no `kid` parameter, or has a `kid` whose value is
  an empty string, the service responds with HTTP 401 and the reason code `TOKEN_KID_MISSING`. Policy evaluation does
  not receive the request. This response applies even when the request token also fails another check of the
  service.

### Justification

A trusted key source publishes its JWKS, so it can add and remove keys without a change to the service (R1). Some
request tokens carry their own key or point at one. If the service used such a key, anyone could sign a token that it
accepts (R1).

Holding a key set for 5 minutes limits how often the service loads each JWKS. It also limits how long a removed key
stays usable (R2).

A `kid` names the one key in the key set that verifies the token. Without a `kid`, the service would have to try every
key. A reason code of its own shows the client what to fix (R3).

### Alternatives considered

- **A1. Use a key that the request token carries or points at, through the `jwk`, `x5c`, or `jku` header
  parameter.** Rejected by R1: anyone could then sign a token that the service accepts.
- **A2. Load the JWKS for every request token.** Rejected by R2: the load on each trusted key source would grow with
  the request rate.
- **A3. Try every key in the key set for a request token without a `kid`.** Rejected by R3.

## Consequences

Negative:

- A key that a trusted key source removes from its JWKS stays usable for up to 5 minutes (R2).
- A key that a trusted key source adds to its JWKS stays unusable for up to 5 minutes (R2).
- Some clients may now receive HTTP 401 with `TOKEN_KID_MISSING` for a request token that the service accepted before
  this record. This applies to any request token whose header has no `kid`. A test that sends a token without a `kid`
  shows the change (R3).
- An existing installation that configures signing keys in another way gets the outcome that R4 states on upgrade.

## Open points

- **O1.** What the service does when it cannot load the JWKS of a trusted key source after the 5 minutes of R2 have
  passed. The answers under consideration:
  - The service keeps using the old key set until a load succeeds.
  - The service refuses with HTTP 401 every request token whose `kid` belongs to that source, with a reason code still
    to be named.

  The security architect decides. Affects R2.
- **O2.** Whether a `kid` whose value is an empty string counts as no `kid`. The record assumes that it does. The
  security architect decides. Affects R3.
- **O3.** Which setting lists the trusted key sources, and what its name is. The record assumes a list in the service
  configuration. The security architect decides. Affects the term **trusted key source**, R1, and R4.
- **O4.** What the service does when its configuration lists no trusted key source. This includes an existing
  installation after the upgrade. The answers under consideration:
  - The service exits before it serves a request.
  - The service starts and refuses every request token with HTTP 401.

  The security architect decides. Affects R4.
- **O5.** Whether `TOKEN_KID_MISSING` takes precedence over every other check of a request token. The record assumes
  that it does. The security architect decides between confirming this precedence and naming checks whose reason code
  wins. Affects R3.
````

### File: docs/adr/0007-hold-keys-five-minutes.md

````markdown
# Hold a loaded key set for 5 minutes
````

### Message to the user
I suggest a separate record for the key cache.

I wrote `docs/adr/0006-take-signing-keys-from-the-jwks-of-trusted-key-sources.md` as one record with status `Proposed`. The three choices come from one authority, the security architect, and change together, so they belong in one record.

Rule R4 has a visible placeholder. Your notes don't say what an installation gets on upgrade when it lists no trusted key source. Open point O4 asks for that outcome.

To finish the record, I need:

- **Owner and approver:** the GitHub account of the owner, and the account of the security architect who approves it.
- **O1:** When the JWKS reload fails after 5 minutes, should the service keep the old key set or refuse the tokens?
- **O2:** Does an empty `kid` count as a missing `kid`?
- **O3:** Which setting lists the trusted key sources, and what is its name?
- **O4:** With no trusted key source configured, should the service exit before it serves a request, or start and refuse every request token?
- **O5:** Should `TOKEN_KID_MISSING` take precedence over every other refusal reason?

The record stays `Proposed` until all five open points are settled.

Does any of ADR-0001 to ADR-0005 decide where signing keys come from? If one does, this record replaces those rules. In that case, I'll name them by number under **Related ADRs**.

I didn't change `docs/adr/README.md`. The guide already maps the layers the record uses (`keys`, `verify`, and `server`).
