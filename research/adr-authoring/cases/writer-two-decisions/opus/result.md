## Request 1

### File: docs/adr/0006-verify-the-signature-of-every-token-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account of the security architect>`: approves R1 to R3.

## Context

The service checks the token of each request before policy evaluation. A token's signature shows that the token comes
from a holder of the signing key and that nobody changed its header or payload after signing. Policy evaluation decides
on the claims in the token. If the service does not check the signature, anyone who can send a request can write those
claims.

## Decision

We will verify the signature of every token before policy evaluation. We will refuse a request whose token's signature
does not verify.

### Terms

- **token**: the token that the service checks for a request before policy evaluation.
- **verifies**: a token's signature verifies when it is valid over the token's header and payload under a key and an
  algorithm that the service trusts for token signatures. O1 asks which keys and algorithms that covers. R3 names the
  tokens whose signature does not verify under any key.
- **reason code**: the code that names why the service refused a request, in `<field that carries the reason code>` of
  the response.

### Rules

#### Verification

- **R1** (`verify`). The service verifies the signature of a request's token before policy evaluation of that request.
  The service does not pass a request to policy evaluation if its token's signature does not verify.
- **R2** (`verify`, `server`). The service refuses a request whose token's signature does not verify with HTTP 401 and
  the reason code `TOKEN_SIGNATURE_INVALID`.
- **R3** (`verify`). The signature of a token does not verify if the token has no signature or if its header names the
  algorithm `none`.

### Implementation notes

Adds no requirement. `internal/verify` can return a distinct error for a signature that does not verify, and
`internal/server` can map that error to HTTP 401 with `TOKEN_SIGNATURE_INVALID`. A table test in `internal/verify` can
cover a valid signature, a changed payload, a token without a signature, and a header with `alg` set to `none`. A test
in `internal/server` can check the status code and the reason code.

### Justification

Policy evaluation trusts the claims it reads, so it reads claims only from a token whose signature verifies (R1). HTTP
401 tells the client that its credentials failed. The reason code lets the client and the logs tell this refusal apart
from other refusals (R2). Attackers often get a forged token past a verifier by leaving out the signature or by setting
`alg` to `none`, so neither one counts as a signature that verifies (R3).

### Alternatives considered

- **A1. Leave the signature check to policy evaluation.** Rejected by R1: a policy that leaves out the check would let a
  forged token through.
- **A2. Refuse a token whose signature does not verify with HTTP 403.** Rejected by R2: HTTP 403 tells the client that
  its credentials were valid and the request is forbidden.
- **A3. Accept unsigned tokens from callers inside the cluster.** Rejected by R3: the service cannot tell from a request
  where its caller runs.

## Consequences

Negative:

- Each request costs a signature verification before policy evaluation (R1).
- If the service passes tokens whose signature does not verify to policy evaluation today, the requests that policy
  evaluation allowed now get HTTP 401 (R2). The test in `internal/server` for R2 shows the case.

## Open points

- **O1.** Which keys and algorithms count when a signature verifies. One answer is the keys that `internal/keys`
  provides, with any algorithm that those keys support. The other is a fixed list of algorithms that this record would
  name. The security architect decides. This affects the term **verifies**, R1, R2, and R3. R3 assumes that an unsigned
  token and the algorithm `none` never verify, whatever the answer.
- **O2.** Where the response carries the reason code. One answer is the field that an earlier record fixes for reason
  codes, if one does. The other is a field of the JSON response body, such as `reason`. The security architect decides.
  This affects the term **reason code** and R2.
````

### Message to the user

The notes hold two decisions, so I wrote only the token one, as ADR-0006. The `GET /healthz` liveness probe was decided
by a different authority (the platform team) for a different reason (letting Kubernetes restart the service). It doesn't
follow from a record about token signatures. I suggest giving it its own record, "Respond to `GET /healthz` with HTTP 200
while the process runs", owned by the platform team, with a rule in the `server` layer. Should I write it as ADR-0007?

Questions about ADR-0006:

- Who owns the record, and what is the security architect's GitHub account? I put visible placeholders in **Owner**
  and **Participants and approvers**.
- O1 and O2 block acceptance:
  - O1: which keys and algorithms count when a signature verifies.
  - O2: which response field carries the reason code.

  If an earlier record already defines either one, tell me which record it is and I'll point to it.
- Your notes gave no reasons. I wrote the **Justification** from the usual security arguments. Does it match what the
  security architect said?

## Request 2

### File: docs/adr/0006-verify-tokens-with-keys-from-the-jwks-of-each-trusted-key-source.md

````markdown
# Verify tokens with keys from the JWKS of each trusted key source

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account of the security architect>`: approves R1 to R4.

## Context

The service checks the token of each request before policy evaluation, and it verifies the token's signature with a
signing key. A key source publishes its public keys as a JSON Web Key Set (JWKS, RFC 7517), and each key in the set
carries a key ID, `kid`. A token names the key that signed it in the `kid` parameter of its header (RFC 7515, section
4.1.4). A key source that rotates its keys publishes the new key in its JWKS.

Three choices go together: where the keys come from, how long the service uses a loaded key set, and whether a token
must name its key. All three change together when the key handling changes, so this record holds them as one decision.

## Decision

We will take the signing keys for token verification from the JWKS of each trusted key source. We will use a loaded key
set for 5 minutes. We will refuse a token whose header has no `kid`.

### Terms

- **trusted-key-sources**: the key sources listed in `<path of the trusted key sources file>`, each with the URL of its
  JWKS. A key source joins the list only after the security architect approves it. R2 takes the place of that
  criterion in the repository.
- **trusted key source**: a key source in trusted-key-sources.
- **key set**: the keys that the service loaded from the JWKS of one trusted key source in one load.
- **has no `kid`**: the token's header has no `kid` parameter, or its `kid` is not a non-empty string.
- **reason code**: the code that names why the service refused a request, in `<field that carries the reason code>` of
  the response.

### Rules

#### Key sources

- **R1** (`keys`). The service takes the signing keys that it verifies tokens with from the JWKS of each trusted key
  source and from no other source.
- **R2** (`keys`). `CODEOWNERS` names `<GitHub account of the security architect>` as an owner of
  `<path of the trusted key sources file>`.

#### Key sets

- **R3** (`keys`). The service verifies tokens with a key set for 5 minutes after it loads that key set, and for no
  longer.

#### Tokens without `kid`

- **R4** (`verify`, `server`). The service refuses a request whose token has no `kid` with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`, and it verifies that token with no key.

### Implementation notes

Adds no requirement. `internal/keys` can hold one key set per trusted key source together with its load time, and can
take the current time from an injected clock so that a test can move past the 5 minutes. `internal/verify` can check the
`kid` before it looks up a key, and can return a distinct error that `internal/server` maps to HTTP 401 with
`TOKEN_KID_MISSING`. Tests in `internal/keys` against a local JWKS server can show which key sets the service loads and
when it stops using them.

### Justification

A JWKS lets a key source rotate its keys without a change to the service (R1). A list in a file lets one pull request
add a key source, and the `CODEOWNERS` entry keeps each addition under the security architect's review (R2). Five
minutes limits both how often the service loads each JWKS and how long the service keeps using a key that a key source
has removed (R3). With a `kid`, the service verifies the token with the one key that the token names. Without one, the
service would have to try keys from every trusted key source (R4).

### Alternatives considered

- **A1. Configure signing keys as static key files in the deployment.** Rejected by R1: a key rotation would need a
  deployment of the service.
- **A2. Load the JWKS again for every token.** This adds a request to the key source for each token and makes every
  token check depend on the key source being reachable.
- **A3. Try every key of every key set when a token has no `kid`.** Rejected by R4.
- **A4. List the trusted key sources in this record.** Each new key source would need a new record.

## Consequences

Negative:

- After a key source removes a key from its JWKS, the service accepts that key for up to 5 minutes (R3).
- If the service accepts tokens without a `kid` today, clients that send them now get HTTP 401 with
  `TOKEN_KID_MISSING` (R4). The test in `internal/server` for R4 shows the case.

Follow-ups:

- Map `<path of the trusted key sources file>` and `CODEOWNERS` to the `keys` layer in `docs/adr/README.md`.

## Open points

- **O1.** Where trusted-key-sources lives and what qualifies a key source to join it. One answer is approval by the
  security architect through `CODEOWNERS`. The other is a written security review linked from each entry. The security
  architect decides. This affects the term **trusted-key-sources**, R1, and R2. R2 assumes the first answer.
- **O2.** How the service handles two cases while a key set is younger than 5 minutes:
  - A token whose `kid` is in no loaded key set. One answer is to refuse the token until the 5 minutes pass. The other
    is to load the JWKS again at once, with a limit of `<loads per minute>`.
  - A load that fails after the 5 minutes. R3 assumes that the service then stops using the old key set. The other
    answer is to keep using it for `<grace period>`.

  The security architect decides. This affects R3.
- **O3.** Whether a `kid` that is an empty string or not a string counts as no `kid`. The term **has no `kid`**
  assumes that it does. The security architect decides. This affects R4.
- **O4.** Where the response carries the reason code. One answer is the field that an earlier record fixes for reason
  codes, if one does. The other is a field of the JSON response body, such as `reason`. The security architect decides.
  This affects the term **reason code** and R4.
````

### Message to the user

I wrote one record, ADR-0006. One authority settled the three choices, and they change together, so they belong in one
record.

Questions:

- Who owns the record, and what is the security architect's GitHub account? R2 needs the account too.
- Where should the trusted key sources file live? I left a placeholder for its path in the term, in R2, and in the
  follow-up.
- How does the service get its signing keys today? If it reads them from somewhere else, such as static key files, this
  record changes what the service trusts. It then needs a rule for what an existing installation gets on upgrade.
- O1 to O4 block acceptance. Each one names the assumption that the rules use for now.
- Your notes gave no reasons. I wrote the **Justification** from the usual arguments for JWKS, key-set caching, and
  `kid`. Does it match what the security architect said?
- The guide in `docs/adr/README.md` has to map the trusted key sources file and `CODEOWNERS` to the `keys` layer. I
  listed that as a follow-up rather than editing a guide whose text I don't have.
