## Request 1

### File: docs/adr/0006-verify-the-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse a token that fails

## Status

Proposed

### Owner

TBD

### Participants and approvers

- Security architect, `<account>`: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims of the token,
so a token whose signature is not checked lets a caller choose those claims.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does
not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that a request carries in its `Authorization` header. O1 asks whether any other place counts.
- **refuse**: the service answers the request with the stated HTTP status and reason code, and the request never
  reaches policy evaluation.

### Rules

#### Signature verification

- **R1** (`verify`). The service verifies the signature of the token of each request before it starts policy evaluation
  for that request.
- **R2** (`verify`, `server`). The service refuses a request whose token has a signature that does not verify, with HTTP
  401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation can trust the claims of a token only if the signature has been verified first (R1). A fixed status
and reason code let a client tell a bad signature from other refusals (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterward.** Rejected by R1: policy would read claims that no
  one has authenticated.

## Consequences

Negative:

- A request with a token whose signature does not verify never reaches policy evaluation, so no policy can allow it
  (R1, R2).

Follow-ups:

- Write a separate record for the `GET /healthz` liveness probe that the platform team decided.

## Open points

- **O1.** The notes say "every token" and do not name where a request carries it. We assume the `Authorization` header.
  The security architect decides. It affects R1 and R2.
- **O2.** The notes do not say how the reason code reaches the client, such as a field of the response body or a
  header. The security architect decides. It affects R2.
````

### Message to the user

I wrote only the signature decision, as ADR 0006. The notes hold two decisions with different deciding authorities and different reasons to change. The liveness probe (`GET /healthz` returns 200 while the process runs) belongs in its own record, so I didn't write it. Do you want me to draft it as ADR 0007, with the platform team as approver?

Questions before the record can be accepted:

- Who is the owner (a GitHub account)? Which account is the security architect's? I left `TBD` and `<account>`.
- O1: do tokens arrive only in the `Authorization` header?
- O2: how does the client receive `TOKEN_SIGNATURE_INVALID`?

The status is `Proposed` while these are open. I tagged R2 with both `verify` and `server`, because I assumed `verify` produces the refusal and `server` maps it to HTTP 401. I had no code to check this, so correct the tags if the mapping lives elsewhere. No **Confirmation** section exists yet because no check is known. Add one when a test lands.

## Request 2

### File: docs/adr/0006-verify-tokens-with-jwks-keys-cached-for-5-minutes-and-require-kid.md

````markdown
# Verify tokens with keys from the JWKS of each trusted key source, hold them for 5 minutes, and require a kid

## Status

Proposed

### Owner

TBD

### Participants and approvers

- Security architect, `<account>`: approves R1 to R3.

## Context

The service verifies the signature of each token against a signing key. The service has to know which key sources it
trusts, where it gets their keys, how long it reuses them, and what it does with a token that does not say which key
signed it.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **trusted key source**: a key source that the service accepts keys from. O1 asks how the set of trusted key sources is
  kept.
- **key set**: the keys that the service has loaded from one JWKS of one trusted key source.
- **refuse**: the service answers the request with the stated HTTP status and reason code, and the request never
  reaches policy evaluation.

### Rules

#### Keys

- **R1** (`keys`). The service takes the signing keys for token verification only from the JWKS of each trusted key
  source.
- **R2** (`keys`). The service holds a key set for 5 minutes (300 seconds) after it loads it, and loads the JWKS of that
  key source again before it uses the key set after that time. O2 asks what happens when the load fails.

#### Tokens without a `kid`

- **R3** (`verify`, `server`). The service refuses a request whose token header has no `kid` parameter, with HTTP 401
  and the reason code `TOKEN_KID_MISSING`.

### Justification

Keys from the JWKS of a trusted key source let a key source rotate its keys without a change to the service (R1). A
fixed holding time bounds how long a key that a source has removed stays usable, and spares the key source a JWKS
request for each token (R2). A token with a `kid` selects one key of the key set. A token without one would force a
choice among keys, so the service refuses it (R3). The three choices change together when the key handling changes, so
they form one record (R1, R2, R3).

### Alternatives considered

- **A1. Load the JWKS again for every token.** Rejected by R2: each token would cost a request to the key source, and
  the 5 minutes would have no effect.
- **A2. Try every key of the key set when the token header has no `kid`.** Rejected by R3: a token without `kid` is
  refused and no key is tried.

## Consequences

Negative:

- A key that a key source removes stays usable for the service for up to 5 minutes (R2).
- A token that a client issues without a `kid` is refused, even where its signature would verify against some key (R3).

## Open points

- **O1.** The notes do not say how the set of trusted key sources is defined. The answers under consideration are a
  list in one file of the repository, with a `CODEOWNERS` entry for that file, or a runtime setting. The security
  architect decides. It affects R1.
- **O2.** The notes do not say what the service does when a reload after 5 minutes fails. The answers under
  consideration are to keep using the old key set, or to refuse the request. The security architect decides. It
  affects R2.
````

### Message to the user

The three choices are one decision from one authority, and they change together, so I wrote one record, ADR 0006. This is independent of the Request 1 record.

Questions before the record can be accepted:

- Who is the owner (a GitHub account)? Which account is the security architect's? I left `TBD` and `<account>`.
- O1: how is the set of trusted key sources kept? I suggest a file in the repository with a `CODEOWNERS` entry, because then a new source is one reviewed pull request. A runtime setting is the other answer.
- O2: what happens when the reload after 5 minutes fails? Does the service keep the old key set, or refuse the request?

The status is `Proposed` while these are open. I read "holds a loaded key set for 5 minutes" as a time to live that starts at the load. Tell me if you meant something else. I tagged R3 with `verify` and `server` on the assumption that `verify` finds the missing `kid` and `server` sets the HTTP 401. I had no code to check this, so correct the tags if the mapping lives elsewhere. The notes don't cover a token whose `kid` is absent from the key set, so that case is the implementer's choice. No **Confirmation** section exists yet because no check is known. Add one when a test lands.
