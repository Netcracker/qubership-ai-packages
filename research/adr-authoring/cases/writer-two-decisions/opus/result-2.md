## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 to R3.

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation decides whether to allow a
request based on the claims in its token. Anyone who can send a request can put any claims they like into a token. Only
a valid signature shows that a key holder the service trusts issued those claims.

## Decision

We will verify the signature of every token before policy evaluation. We will refuse a token whose signature does not
verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the bearer token in the `Authorization` header of a request.
- **policy evaluation**: the step that uses the claims of a token to decide whether the service allows the request.
- **verifies**: a token's signature verifies when it is valid for the token's header and payload under a key that the
  service trusts for that token, and when its algorithm is one that R3 accepts.

### Rules

#### Order of checks

- **R1** (`server`, `verify`). A request that carries a token reaches policy evaluation only after the signature of
  that token verifies.

#### Refusal

- **R2** (`server`, `verify`). The service answers a request whose token's signature does not verify with HTTP 401 and
  the reason code `TOKEN_SIGNATURE_INVALID` in `<reason code field>`.

#### Accepted algorithms

- **R3** (`verify`). A token's signature verifies only where the algorithm in the token's `alg` header is one of
  `<accepted signature algorithms>`.

### Justification

Policy evaluation acts on the claims of a token. A claim counts as evidence only after the signature has verified, so
the service verifies the signature first (R1). HTTP 401 tells the client that its credentials failed. The reason code
lets clients and operators tell this refusal apart from other refusals without parsing a message (R2). A fixed list of
algorithms stops a token from choosing its own algorithm, including `none` (R3).

### Alternatives considered

- **A1. Let each policy check the token signature as part of policy evaluation.** Rejected by R1: the request would
  reach policy evaluation before its signature verifies, and every policy would have to repeat the check.
- **A2. Answer a token whose signature does not verify with HTTP 403.** Rejected by R2: HTTP 403 means that the client
  is known and lacks permission, but here the service cannot tell who the client is.
- **A3. Accept any algorithm that the token's `alg` header names.** Rejected by R3: a token with `alg` set to `none`
  would verify without any key.

## Consequences

Negative:

- The service refuses a token signed with an algorithm outside the R3 list, even when the key that signed it is
  trusted (R2, R3).
- Every request that carries a token costs one signature verification before policy evaluation (R1).

## Open points

- **O1.** Which algorithms R3 accepts. The security architect decides. One candidate is a list of asymmetric algorithms
  such as `RS256` and `ES256`. Affects R3 and the term **verifies**.
- **O2.** Which keys the service trusts for a token. The notes leave this open. If an existing record already settles
  it, this record cites that record under **Terms**. If not, the security architect settles it in a record of its own.
  Affects R1, R2, and the term **verifies**.
- **O3.** Where the response carries the reason code. Candidates are a field of a JSON response body, a response
  header, or the place that an existing record already sets for reason codes. Affects R2.
- **O4.** The term **token** assumes the bearer token in the `Authorization` header. The security architect confirms
  this or names the place the token comes from. Affects R1 and R2.
- **O5.** Which answer a token gets when its signature does not verify and another check fails too, for example
  because the token has expired. Candidates are: the signature check comes first, or a record that orders all the
  checks says which comes first. Affects R2.
````

### Message to the user

I wrote one record from these notes: ADR-0006 on token signature verification. The notes cover two decisions. Each has its own deciding authority and its own reason to change. The security architect owns signature verification. The platform team owns the `GET /healthz` liveness answer, which Kubernetes uses. A liveness probe in a record about tokens would be hard to find later.

I propose a separate record for the platform team's decision, ADR-0007, "Answer `GET /healthz` with HTTP 200 while the process runs". Should I write it?

The record stays `Proposed` until its open points are settled:

- **O1:** Which signature algorithms count as verified? Without a list, a token with `alg: none` is a gap.
- **O2:** Which keys does the service trust for a token? Is this already in one of ADR-0001 to ADR-0005, or does it need its own record?
- **O3:** Where does the response carry the reason code? Is that already fixed in an existing record?
- **O4:** Is the token the bearer token in `Authorization`?
- **O5:** Which reason code wins when the signature check and another check both fail?

I also need these for the metadata:

- Who owns this record? Please give the GitHub account.
- What is the security architect's account?

The reading guide already maps `verify` and `server`, so it needs no change.

## Request 2

### File: docs/adr/0006-select-token-signing-keys-by-kid-from-the-jwks-of-trusted-key-sources.md

````markdown
# Select token signing keys by `kid` from the JWKS of trusted key sources

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 to R4.

## Context

token-gate checks the token of each request before policy evaluation, and it needs the issuer's public key to verify
the token's signature. A token issuer publishes its signing keys as a JSON Web Key Set (JWKS). The issuer adds and
removes keys there when it rotates them. A token's `kid` header names the key in the JWKS that signed the token. The
three choices in this record change together when the key handling changes.

## Decision

We will take token signing keys only from the JWKS of each trusted key source, and hold each loaded key set for 5
minutes. We will refuse a token whose header has no `kid`.

### Terms

- **token**: the bearer token in the `Authorization` header of a request.
- **key source**: a token issuer that publishes its signing keys as a JWKS at a URL.
- **trusted-key-sources**: the JWKS URLs listed in `<path of the trusted-key-sources file>`. A key source joins this
  list only after the security architect approves it. R2 states who owns the file.
- **trusted key source**: a key source whose JWKS URL is in trusted-key-sources.
- **key set**: the keys that one load of a trusted key source's JWKS returns.

### Rules

#### Key sources

- **R1** (`keys`). The service takes the keys it uses to verify token signatures from the JWKS of trusted key sources,
  and from no other source.
- **R2** (`keys`). `CODEOWNERS` names `<security architect account>` as an owner of
  `<path of the trusted-key-sources file>`.

#### Key set lifetime

- **R3** (`keys`). The service keeps each key set for 5 minutes after loading it, and uses that key set to verify
  token signatures during that time. After 5 minutes, the service verifies token signatures with keys from that
  trusted key source only after it loads a new key set.

#### Tokens without `kid`

- **R4** (`verify`, `server`). The service answers a request whose token's header has no `kid` with HTTP 401 and the
  reason code `TOKEN_KID_MISSING` in `<reason code field>`.

### Implementation notes

Adds no requirement. Load the list in trusted-key-sources when the service starts, and keep one key set per trusted
key source, keyed by the JWKS URL. Look a key up by the token's `kid` in the key set of its trusted key source.

### Justification

A JWKS lets a key source rotate its keys without any change to the service (R1). A list kept in a file lets a new key
source join in one pull request. The `CODEOWNERS` entry means each such pull request needs the security architect's
approval (R1, R2). Holding a key set for 5 minutes limits how long the service keeps using a key after its source
removes it. It also spares the key source one load per token (R3). A `kid` selects one key from the key set. Without
it, the service would have to try every key (R4).

### Alternatives considered

- **A1. Configure signing keys as PEM files in the service's deployment.** Rejected by R1: every key rotation would need
  a change to the deployment.
- **A2. Load the JWKS for every token.** Rejected by R3: every request would wait for the key source, and the key source
  would get one load per token.
- **A3. Try every key in the key set when the token has no `kid`.** Rejected by R4: the cost of a check would grow with
  the size of the key set, and one token could match keys from different sources.

## Consequences

Negative:

- After a key source removes a key from its JWKS, that key still verifies tokens for up to 5 minutes (R3).
- The service refuses tokens from a key source that does not set `kid`, even when the key source is trusted (R4).
- Every 5 minutes, verification depends on the service reaching the JWKS of each trusted key source (R3).

Follow-ups:

- Map `<path of the trusted-key-sources file>` and `CODEOWNERS` to the `keys` layer in the reading guide.

## Open points

- **O1.** The term **token** assumes the bearer token in the `Authorization` header. The security architect confirms
  this or names the place the token comes from. Affects R4.
- **O2.** The term **trusted-key-sources** assumes two things: the list lives in a file in the repository, and the
  security architect approves each new member. The alternative is a deployment setting. In that case, R2 goes and the
  term names the setting. The security architect decides. Affects R1 and R2.
- **O3.** What the service does when a token's `kid` is not in a key set younger than 5 minutes. Candidates are to load
  the JWKS again at once, perhaps no more than once in a set interval, or to refuse the token until the 5 minutes pass.
  The security architect decides. Affects R3.
- **O4.** What the service does when a load after 5 minutes fails. Candidates are to refuse tokens from that key source,
  with a reason code still to be chosen, or to keep the old key set for a grace period. The security architect
  decides. Affects R3.
- **O5.** Where the response carries the reason code. Candidates are a field of a JSON response body, a response
  header, or the place that an existing record already sets for reason codes. Affects R4.
- **O6.** Whether a `kid` that is an empty string, or that is not a string, counts as no `kid`. The security architect
  decides. Affects R4.
- **O7.** Which answer a token gets when its header has no `kid` and another check fails too. Candidates are: the
  `kid` check comes first, or a record that orders all the checks says which comes first. Affects R4.
- **O8.** How the service gets its keys today. If it uses another source, R1 changes what the service trusts. A rule
  then has to state what an existing installation gets on upgrade, for example that the service stops at startup when
  trusted-key-sources is empty. Affects R1.
````

### Message to the user

I wrote one record: ADR-0006. The JWKS key source, the 5-minute key set lifetime, and the `kid` requirement come from one authority and change together, so they belong in one record.

I need answers to these questions:

- Who owns the record? Please give the GitHub account.
- What is the security architect's account? R2 needs it for the `CODEOWNERS` entry.
- Where does the list of trusted key sources live? I assumed a file in the repository that the security architect approves (O2). If that's right, what path should the file have? If it is a deployment setting instead, R2 goes away.
- When a token's `kid` is not in the loaded key set, should the service load the JWKS early (O3)?
- When a reload after 5 minutes fails, should the service refuse the tokens or keep the old key set (O4)?
- Where does the response carry the reason code (O5)?
- Does an empty `kid` count as missing (O6)?
- Which reason code wins when the `kid` check and another check both fail (O7)?
- How does the service get its keys today (O8)? If the answer is a different source, the record needs a rule for what an existing installation gets on upgrade.
- Is the token the bearer token in `Authorization` (O1)?

The record stays `Proposed` until O1 to O8 are settled.

The record also brings `CODEOWNERS` and the trusted-key-sources file under a rule. The reading guide doesn't map either one yet, so I listed that change as a follow-up. I can update `docs/adr/README.md` once you send me its current text.
