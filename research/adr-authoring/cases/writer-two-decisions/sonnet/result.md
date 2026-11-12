## Request 1

### File: docs/adr/0006-verify-the-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse a token whose signature does not verify

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Security architect, <GitHub account>: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims of the token.
A token whose signature has not been verified carries claims that anyone could have written.

## Decision

We will verify the signature of the token of every request before policy evaluation, and we will refuse a token whose
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that a request carries in its `Authorization` header (O1).
- **signature verifies**: the signature check of the token succeeds. Which algorithms and keys the check accepts is not
  decided here (O3).

### Rules

#### Signature verification

- **R1** (`verify`). The service starts policy evaluation of a request only after the signature of the token of that
  request verifies.
- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP 401 and the reason
  code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation reads claims, and claims of a token with an unverified signature cannot be trusted (R1, R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterward.** Rejected by R1: policy evaluation would read claims
  that no check has authenticated.

## Consequences

Negative:

- The service verifies a signature on every request, so each request pays the cost of that check (R1).
- A request whose token has an invalid signature gets HTTP 401, including where policy would have allowed it (R2).

## Open points

- **O1.** Where does a request carry its token? This record assumes the `Authorization` header. The security architect
  decides. It affects the term **token**, R1, and R2.
- **O2.** How does the response carry the reason code `TOKEN_SIGNATURE_INVALID`, for example in the body or in a header?
  The security architect decides. It affects R2.
- **O3.** Which signature algorithms and which keys count as a verified signature? The security architect decides. It
  affects R1 and R2.
````

### Message to the user

I wrote one record, ADR-0006, for the signature decision. The two notes come from different deciding authorities and change for different reasons, so the `GET /healthz` liveness decision (platform team) needs its own record. I did not write it. Do you want me to draft it as ADR-0007?

Questions:

- Who owns this record? Which GitHub accounts should go under Owner and Participants and approvers? I left visible placeholders. The security architect approves R1 and R2.
- Where does a request carry its token (O1), how does the response carry the reason code (O2), and which algorithms and keys count as a verified signature (O3)? The record stays `Proposed` until these are settled.

Assumptions of mine:

- The token is in the `Authorization` header.
- The `server` layer produces the HTTP result, so R2 carries both `verify` and `server`.
- Alternative A1 and the one-line Justification are mine. The notes gave no reasons, so please correct them.

`docs/adr/README.md` needs no change. Code under `internal/verify` and `internal/server` that implements R1 or R2 should end its commit message and pull request description with `Implements: ADR-0006 R1, R2`. The rules only bind once the record is `Accepted`, but the trailers may already name them.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks-and-require-a-kid.md

````markdown
# Take signing keys from the JWKS of each trusted key source, hold a key set for 5 minutes, and require a `kid`

## Status

Proposed

### Owner

<GitHub account of the owner>

### Participants and approvers

- Security architect, <GitHub account>: approves R1 to R3.

## Context

The service verifies the signature of each token with a signing key. The notes record three choices for this: where the
keys come from, how long a loaded key set is held, and what happens to a token whose header has no `kid`. All three
change together when the key handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **trusted key source**: an entry of the named set `trusted-key-sources`. Which sources belong to the set, and the file
  that lists them, are not decided yet (O1).
- **key set**: the set of keys that one load of the JWKS of one trusted key source returns.
- **token header**: the JOSE header of a token.

### Rules

#### Key sources

- **R1** (`keys`). The service takes the signing keys it verifies tokens with from the JWKS of each trusted key source,
  and from no other source.

#### Key set lifetime

- **R2** (`keys`). The service holds a loaded key set for 5 minutes, counted from the load of that key set.

#### Key identifier

- **R3** (`verify`, `server`). The service refuses a token whose token header has no `kid` with HTTP 401 and the reason
  code `TOKEN_KID_MISSING`.

### Justification

The notes record no reasons for R1 to R3. The security architect supplies them (O3).

### Alternatives considered

- **A1. Try every key of the key set when the token header has no `kid`.** Rejected by R3: a token without a `kid` is
  refused, so no key is tried.

## Consequences

Negative:

- A key that a trusted key source adds or removes can take up to 5 minutes to reach the service, because the service
  holds the loaded key set (R2).
- A token without a `kid` is refused even where its signature would verify with one of the keys (R3).

## Open points

- **O1.** Which sources are trusted key sources, where is the set `trusted-key-sources` kept, and what qualifies a
  source to join it? The security architect decides. It affects R1.
- **O2.** What does the service do after the 5 minutes pass, and what does it do when loading the JWKS fails? The
  security architect decides. It affects R2.
- **O3.** What are the reasons for the three choices? The security architect supplies them for the Justification.
````

### Message to the user

I wrote one record, ADR-0006. The three choices have one deciding authority and change together, so they stay in one record.

Questions:

- Who owns this record? Which GitHub accounts should go under Owner and Participants and approvers? I left visible placeholders. The security architect approves R1 to R3.
- Which sources are trusted key sources, and where is the set kept (O1)? What happens after the 5 minutes pass, and when a JWKS load fails (O2)? The notes do not say, so I left both as open points instead of inventing rules. The record stays `Proposed` until they are settled.
- What are the reasons behind the three choices (O3)? The notes gave none.

Assumptions of mine:

- "From no other source" in R1 and alternative A1 are my additions.
- The `server` layer produces the HTTP result, so R3 carries both `verify` and `server`.
- I could not see records 0001 to 0005. If one of them already covers key handling, tell me and I will add the Related ADRs entry, or turn this into a superseding record.

`docs/adr/README.md` needs no change. Code under `internal/keys`, `internal/verify`, and `internal/server` that implements these rules should end its commit message and pull request description with `Implements: ADR-0006 R1, R2, R3`. A change that brings only some of them names the rest under `Defers`, with an existing issue or pull request.
