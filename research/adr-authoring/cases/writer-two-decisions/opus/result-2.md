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

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims of that
token. Anyone who can send a request can write any claim into a token. Only a verified signature shows that the issuer
made those claims.

## Decision

We will verify the signature of every token before policy evaluation. A request whose token signature does not verify
gets HTTP 401 with the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token the service checks for a request before policy evaluation.

### Rules

#### Order of the checks

- **R1** (`verify`, `server`). For each request that carries a token, the service verifies the signature of that token
  before policy evaluation starts for the request.

#### Refusal

- **R2** (`verify`, `server`). When the signature of a token does not verify, the service answers the request with
  HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`, and policy evaluation does not run for that request.

### Implementation notes

Adds no requirement. Let `internal/verify` return an error that carries the reason code `TOKEN_SIGNATURE_INVALID`, and
let `internal/server` map that error to HTTP 401 before it calls policy evaluation. A test in `internal/server` can send
a token with one changed signature byte, then assert the status and the reason code, and assert that the policy
evaluation stub received no call.

### Justification

Policy evaluation decides on the claims of a token. Without a verified signature, any caller can write those claims,
and policy evaluation would allow requests based on claims the issuer never made (R1, R2). A fixed status and reason
code let a client and an operator tell a signature failure apart from other refusals (R2).

### Alternatives considered

- **A1. Run policy evaluation first, and verify the signature only for requests that it allows.** Rejected by R1:
  policy evaluation would read claims that nobody has verified.
- **A2. Answer a token with an invalid signature with HTTP 403.** Rejected by R2: HTTP 403 means that the caller is
  known and lacks permission, and a token with an invalid signature does not identify the caller.

## Consequences

Negative:

- Every request that carries a token costs one signature verification. This includes requests that policy evaluation
  would refuse anyway (R1).

## Open points

- **O1.** Which signature algorithms and which keys make a signature verify. This record does not settle it. Until it
  is settled, a checker cannot tell whether R2 covers a token whose `alg` is `none`, or a token signed with a key that
  the service does not trust. Answers under consideration: list the algorithms in a new rule here and take the keys
  from a record on key handling, or settle both in a record on key handling and cite it here. The security architect
  decides. Affects R1 and R2.
- **O2.** Where the response carries the reason code `TOKEN_SIGNATURE_INVALID`. Answers under consideration: the field
  that the service's other error responses use, or a response header. The security architect decides. Affects R2.
- **O3.** Whether a token that the service cannot parse has a signature that does not verify. Answers under
  consideration: yes, so R2 applies, or no, and a new rule gives that token a reason code of its own. The security
  architect decides. Affects R2.
- **O4.** What the service does with a request that carries no token. R1 and R2 cover only requests that carry one.
  Answers under consideration: a new rule that refuses the request with HTTP 401 and a reason code of its own, or no
  rule, which leaves the case outside this record. The security architect decides. Affects R1.
````

### Message to the user

I wrote ADR-0006 for the signature check only. The `/healthz` decision is a second decision: the platform team made it, and it changes for a different reason (how Kubernetes detects a stopped process). It doesn't follow from a record about tokens. A checker looking for the liveness probe also wouldn't find it under this title.

Shall I write it as its own record, ADR-0007 "Answer `GET /healthz` with HTTP 200 while the process runs"? The platform team would own it.

Before ADR-0006 can be accepted, I need:

- **Owner and approver accounts.** Who owns this record, and what is the security architect's GitHub account? I used placeholders for both.
- **Open points O1 to O4.** The status stays `Proposed` until they're settled. These are: which algorithms and keys count as verifying, where the reason code appears in the response, whether an unparseable token falls under R2, and what happens to a request without a token.
- **Layer tags.** I tagged R1 and R2 with `verify` and `server` from the reading guide's map. I couldn't read the code to confirm that `internal/server` calls policy evaluation and builds the 401 response.
- **Error response format.** Do any of ADR-0001 to ADR-0005 define the error response format or the term "token"? If so, I'll cite them under **Related ADRs** and **Terms**.
- **Justification and alternatives.** Your notes gave no reasons and no rejected options. I drafted the **Justification** and the two **Alternatives considered**, and the security architect should confirm them.

`docs/adr/README.md` needs no change, because the record uses only layers the guide already maps.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks.md

````markdown
# Take signing keys from the JWKS of trusted key sources, use a key set for at most 5 minutes, and refuse tokens without `kid`

## Status

Proposed

### Owner

`<owner account>`

### Participants and approvers

- Security architect, `<security architect account>`: approves R1 to R3.

## Context

The service checks the token of each request before policy evaluation, and it verifies the token's signature with a
signing key. An issuer publishes its public keys as a JSON Web Key Set (JWKS, RFC 7517) and rotates them over time. A
token names the key that signed it in the `kid` parameter of its header (RFC 7515).

## Decision

We will take signing keys only from the JWKS of each trusted key source, and use a loaded key set for at most 5
minutes. A token whose header has no `kid` gets HTTP 401 with the reason code `TOKEN_KID_MISSING`.

### Terms

- **token**: the token the service checks for a request before policy evaluation.
- **trusted key source**: a key source that has an entry in `internal/keys/trusted-key-sources.yaml`, the set
  `trusted-key-sources`. Each entry names the URL of one JWKS. O1 asks what qualifies a key source to join.
- **signing key**: a key that the service verifies a token signature with.
- **key set**: the keys that the service parsed from one response to its request for the JWKS of one trusted key
  source.
- **no `kid`**: the token header has no `kid` parameter, or its `kid` parameter is the empty string.

### Rules

#### Key sources

- **R1** (`keys`, `verify`). The service takes signing keys only from the JWKS of trusted key sources. A key from any
  other place, such as a file, an environment variable, the `jwk` parameter of a token header, or a URL in the `jku` or
  `x5u` parameter of a token header, is never a signing key.

#### Lifetime of a key set

- **R2** (`keys`). The service verifies a token signature with a key from a key set only within 5 minutes (300 seconds)
  after it loaded that key set.

#### Tokens without `kid`

- **R3** (`verify`, `server`). When a token has no `kid`, the service answers the request with HTTP 401 and the reason
  code `TOKEN_KID_MISSING`, and policy evaluation does not run for that request.

### Implementation notes

Adds no requirement. Keep `trusted-key-sources` in `internal/keys/trusted-key-sources.yaml`, and let `internal/keys`
load each JWKS and record the load time with each key set. The key lookup can then skip a key set that is older than
300 seconds. Let `internal/verify` check `kid` before it looks up a key, and let `internal/server` map that error to
HTTP 401. A test with a fake clock can assert that a key set loaded 301 seconds earlier verifies no token.

### Justification

A JWKS lets an issuer rotate its keys without a change to the service. A fixed list of key sources keeps the sender of
a token from choosing the key that verifies it (R1). A lifetime of 5 minutes limits how long a key that an issuer has
removed from its JWKS still verifies tokens. It also keeps the service from loading a JWKS for every request (R2). With
`kid`, the service looks up one key for each token. Without it, the service would have to try keys until one verifies
(R3). The three choices change together when key handling changes, so they share one record.

### Alternatives considered

- **A1. Configure signing keys as PEM files or environment variables.** Rejected by R1: each key rotation would take a
  deployment.
- **A2. Load the key from the URL in the `jku` or `x5u` parameter of a token header.** Rejected by R1: the sender of the
  token would choose the key that verifies it.
- **A3. Keep a key set until the process restarts.** Rejected by R2: a key that the issuer removed would verify tokens
  until the next restart.
- **A4. Try every loaded key for a token with no `kid`.** Rejected by R3: the cost of a verification would grow with
  the number of keys.

## Consequences

Negative:

- A key that an issuer removes from its JWKS still verifies tokens for up to 5 minutes (R2).
- Every token from an issuer that signs tokens without `kid` gets HTTP 401 (R3).

## Open points

- **O1.** What qualifies a key source to join `trusted-key-sources`. Answers under consideration: a security review by
  the security architect, which a new rule enforces by requiring a `CODEOWNERS` entry for
  `internal/keys/trusted-key-sources.yaml`, or a criterion that a checker can read from the entry, such as a JWKS URL
  that uses `https`. The security architect decides. Affects R1, and either answer adds a rule.
- **O2.** Where `trusted-key-sources` lives. This record assumes `internal/keys/trusted-key-sources.yaml`. The security
  architect decides. Affects R1.
- **O3.** What an existing installation gets on upgrade, since this record changes which keys the service trusts.
  Answers under consideration: the release fills `trusted-key-sources` with the key sources that installations use
  today, or the service stops the start while `trusted-key-sources` is empty. The security architect decides. Affects
  R1, and either answer adds a rule.
- **O4.** Whether the service may load the JWKS of a key source again before 5 minutes have passed, for example for a
  token whose `kid` no loaded key set holds. R2 sets only an upper limit, but "holds a key set for 5 minutes" could also
  mean that the service does not reload earlier. Answers under consideration: a reload for an unknown `kid`, at most
  once per `<minimum reload interval>` for each key source, or no reload before the 5 minutes have passed. The security
  architect decides. Affects R2.
- **O5.** What the service does when a key set is older than 5 minutes and the JWKS of its key source cannot be loaded.
  Answers under consideration: a new rule that refuses tokens of that key source with HTTP 401 and a reason code of its
  own, or a grace period during which the old key set still verifies tokens, which would change R2. The security
  architect decides. Affects R2.
- **O6.** Whether a `kid` parameter set to the empty string counts as no `kid`. This record assumes that it does. The
  security architect decides. Affects R3.
- **O7.** Where the response carries the reason code `TOKEN_KID_MISSING`. Answers under consideration: the field that
  the service's other error responses use, or a response header. The security architect decides. Affects R3.
````

### Message to the user

I wrote this as one record, ADR-0006. All three choices come from the security architect and change together when key handling changes, so they're one decision.

Before it can be accepted, I need:

- **Owner and approver accounts.** Who owns this record, and what is the security architect's GitHub account? I used placeholders for both.
- **Open points O1 to O7.** The status stays `Proposed` until they're settled. O1 and O3 each add a rule once answered, because a list of trusted key sources needs a membership criterion and an upgrade path. O4 and O5 decide what "holds for 5 minutes" means at its edges. O2 and O6 are assumptions I made so the rules could be written: the file path and treating an empty `kid` as missing.
- **Behavior I left unspecified.** The notes don't say what happens to a token whose `kid` matches no loaded key, or which reason code wins when a token has no `kid` and also fails another check. Right now the code can do either however it likes. Should either become a rule?
- **Error response format.** Do any of ADR-0001 to ADR-0005 define the error response format or the term "token"? If so, I'll cite them under **Related ADRs** and **Terms**.
- **Justification and alternatives.** Your notes gave no reasons and no rejected options. I drafted the **Justification** and the four **Alternatives considered**, and the security architect should confirm them.
- **Layer tags.** I tagged the rules from the reading guide's map (`keys`, `verify`, `server`), but I couldn't read the code to confirm them.

`docs/adr/README.md` needs no change. The assumed list file sits under `internal/keys`, which the guide already maps to the `keys` layer.
