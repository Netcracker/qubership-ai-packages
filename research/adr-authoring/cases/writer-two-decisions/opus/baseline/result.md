## Request 1

### File: docs/adr/0006-verify-token-signature.md

````markdown
# 6. Verify the token signature before policy evaluation

- Status: Accepted
- Date: November 9, 2026
- Deciders: security architect
- Layer: `verify` (`internal/verify`)

## Context

token-gate checks the token of each request before policy evaluation. This record sets what the service checks first
and how it refuses a token whose signature does not verify.

## Decision

1. The service verifies the signature of every token before policy evaluation.
2. The service refuses a token whose signature does not verify with HTTP 401 and the reason code
   `TOKEN_SIGNATURE_INVALID`.

## Consequences

- A request whose token signature does not verify gets HTTP 401 with `TOKEN_SIGNATURE_INVALID`. Policy evaluation
  never runs for that request.
- Every request with a token costs one signature verification before policy evaluation starts.
````

### File: docs/adr/0007-healthz-liveness-endpoint.md

````markdown
# 7. Respond to `GET /healthz` while the process runs

- Status: Accepted
- Date: November 9, 2026
- Deciders: platform team
- Layer: `server` (`internal/server`)

## Context

Kubernetes restarts a container when its liveness probe gets no successful response. token-gate needs an endpoint
for that probe.

## Decision

1. The service responds to `GET /healthz` with HTTP 200 while its process runs.

## Consequences

- The response depends only on the process running. When the process exits or stops responding, the probe fails and
  Kubernetes restarts the service.
- `GET /healthz` returns HTTP 200 even when the service cannot verify tokens. It reports only that the process
  runs.
````

### Message to the user

I split the notes into two ADRs. They record two separate decisions, made by different owners, that apply to different layers: signature verification in `verify`, and the health endpoint in `server`. Neither depends on the other, and either one could be replaced without touching the other. So they are 0006 and 0007. If you want a single record anyway, tell me and I'll merge them.

I didn't have the `adr-authoring` template or the text of 0001–0005. The headings and metadata lines above are a guess, so align them with the existing records. I also didn't change `docs/adr/README.md` because I don't have its content. If the guide lists records by layer, it needs entries for 0006 under `verify` and 0007 under `server`.

Questions:

1. The service checks the token of every request, but a Kubernetes liveness probe sends no token. Is `GET /healthz` exempt from the token check? If it is, that exemption should be a rule in 0007. Without it, the probe gets HTTP 401 and Kubernetes keeps restarting the service.
2. The notes give the two decisions but not the reasons for them. Should the Context sections state why, for example that policy evaluation reads claims that can only be trusted after the signature verifies?
3. Which date, and which names in place of "security architect" and "platform team", should the records carry?

## Request 2

### File: docs/adr/0006-signing-keys-from-jwks.md

````markdown
# 6. Take signing keys from the JWKS of each trusted key source

- Status: Accepted
- Date: November 9, 2026
- Deciders: security architect
- Layers: `keys` (`internal/keys`) for rules 1 and 2, `verify` (`internal/verify`) for rule 3

## Context

token-gate verifies the signature of each token with a signing key, before policy evaluation. This record sets where
the service gets those keys, how long it holds them, and how it refuses a token that names no key. The three rules
change together whenever key handling changes, so they share one record.

## Decision

1. The service takes signing keys from the JWKS of each trusted key source.
2. The service holds a loaded key set for 5 minutes.
3. The service refuses a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

## Consequences

- A key that is added to or removed from a JWKS takes effect in the service only after the key set it already loaded
  is 5 minutes old.
- A token without `kid` gets HTTP 401 with `TOKEN_KID_MISSING`. The service never tries the keys in the set one by
  one to find a match.
- A change to any of the three rules supersedes this record as a whole.
````

### Message to the user

All three choices are in one ADR, 0006, because they change together. Rules 1 and 2 belong to the `keys` layer and rule 3 belongs to `verify`, and the header says so.

I didn't have the `adr-authoring` template or the text of 0001–0005. The headings and metadata lines above are a guess, so align them with the existing records. I also didn't change `docs/adr/README.md` because I don't have its content. If the guide lists records by layer, 0006 belongs under both `keys` and `verify`.

The notes leave these cases open, and the record doesn't decide them:

1. When a token's `kid` matches no key in the loaded set, does the service reload the JWKS before the 5 minutes are up, or refuse the token right away? If it refuses, which reason code does it use?
2. When the key set is 5 minutes old and fetching the JWKS fails, does the service keep using the old set, or refuse tokens until a fetch succeeds?
3. Where is the list of trusted key sources configured, and should this record name that setting?
4. Should the Context state why the architect chose JWKS and 5 minutes? Two reasons that could apply are key rotation and how long a revoked key can still verify tokens.
5. Which date, and which name in place of "security architect", should the record carry?
