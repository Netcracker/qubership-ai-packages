## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# 0006. Verify the token signature before policy evaluation

- Status: Accepted
- Date: 2026-11-09
- Layer: verify (`internal/verify`)
- Decided by: security architect

## Context

token-gate checks the token of each request before policy evaluation. Policy evaluation reads claims from the token, so
a claim is only trustworthy once the signature over it has been verified.

## Decision

1. The service verifies the signature of every token before policy evaluation.
2. The service refuses a token whose signature does not verify with HTTP 401 and the reason code
   `TOKEN_SIGNATURE_INVALID`.

## Consequences

- Policy evaluation runs only on tokens whose signature verified.
- A client that receives `TOKEN_SIGNATURE_INVALID` knows the signature failed, and a retry with the same token fails
  again.
````

### File: docs/adr/0007-answer-healthz-while-the-process-runs.md

````markdown
# 0007. Answer `GET /healthz` while the process runs

- Status: Accepted
- Date: 2026-11-09
- Layer: server (`internal/server`)
- Decided by: platform team

## Context

Kubernetes restarts a container when its health probe stops getting an answer. The service needs an endpoint that
reports whether the process still responds.

## Decision

1. The service answers `GET /healthz` with HTTP 200 while its process runs.
2. When the process stops answering `GET /healthz`, Kubernetes restarts the service.

## Consequences

- A stopped or hung process fails the probe, so Kubernetes restarts it.
- `GET /healthz` reports process liveness only. It says nothing about token verification or any other function of the
  service.
````

### Message to the user

I split the notes into two ADRs, 0006 and 0007, because the two decisions have different owners and layers (`verify` and `server`) and can change independently.

- I couldn't read the `adr-authoring` template or the existing records 0001 to 0005. The structure above (status, date, layer, context, numbered decision rules, consequences) is my assumption, so please check it against the template.
- I didn't touch `docs/adr/README.md`, because I don't have its content. It likely needs one entry per new record under `verify` and `server`. Do you want me to add them if you send me the file?
- The Context and Consequences sections go slightly beyond the notes. Please confirm that the two consequence statements are right.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-jwks.md

````markdown
# 0006. Take signing keys from the JWKS of each trusted key source

- Status: Accepted
- Date: 2026-11-09
- Layer: keys (`internal/keys`)
- Decided by: security architect

## Context

Token verification needs the signing key that matches each token. These three choices (where keys come from, how long
a loaded key set is held, and what happens to a token with no `kid`) change together when the key handling changes, so
this record keeps them together.

## Decision

1. The service takes signing keys from the JWKS of each trusted key source.
2. The service holds a loaded key set for 5 minutes.
3. The service refuses a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

## Consequences

- A change to how keys are handled revisits rules 1 to 3 together, in a new record that supersedes this one.
- A client that receives `TOKEN_KID_MISSING` must send a token whose header carries a `kid`.
````

### Message to the user

I wrote one ADR, 0006, with three numbered rules, because you said all three choices change together.

- I couldn't read the `adr-authoring` template or the existing records 0001 to 0005. The structure above is my assumption, so please check it against the template.
- I placed the record in the `keys` layer (`internal/keys`), since key handling drives it. If the `kid` refusal belongs in `verify`, tell me and I'll change the layer.
- I didn't touch `docs/adr/README.md`, because I don't have its content. It likely needs an entry under `keys`. Do you want me to add one if you send me the file?
- The first consequence (a change supersedes this record as a whole) follows from your note that the choices change together. Please confirm that it matches how you handle supersession.
