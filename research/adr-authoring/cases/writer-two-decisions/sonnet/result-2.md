## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse a token that fails

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `<account>`: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. The security architect decided that the check
includes the token signature, and decided how the service answers a token whose signature does not verify.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does
not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that a request presents to the service for checking.
- **signature verifies**: the signature of a token is valid for the header and payload of that token under a signing key
  and an algorithm that the service accepts. A token with no signature does not verify. O1 asks which algorithms the
  service accepts.
- **policy evaluation**: the component that decides, from the claims of a token and the request, whether the request is
  allowed.

### Rules

#### Verification

- **R1** (`verify`). The service starts policy evaluation for a request only after the signature of the token of that
  request verifies.

#### Refusal

- **R2** (`verify`, `server`). The service refuses a token whose signature does not verify with HTTP 401 and the reason
  code `TOKEN_SIGNATURE_INVALID`.

### Justification

Policy evaluation then never reads claims that no signature backs (R1). A fixed status and reason code let a caller tell
a bad signature from other refusals (R2).

### Alternatives considered

- **A1. Evaluate policy on the decoded claims and verify the signature afterward.** Rejected by R1: policy evaluation
  would read claims that no signature backs.

## Consequences

Negative:

- Every request pays for a signature verification before policy evaluation starts (R1).

Follow-ups:

- The `GET /healthz` decision from the same meeting is a separate record (see the message to the user).

## Open points

- **O1.** Which signing algorithms does the service accept? The security architect decides. It affects R1 and R2, because
  it fixes which tokens verify.
- **O2.** Where does a response carry the reason code `TOKEN_SIGNATURE_INVALID`: a field of the response body, a header,
  or both? The security architect decides. It affects R2.
````

### Message to the user

I wrote one record, ADR-0006, for the signature decision. The notes hold two decisions with different deciding authorities and different reasons to change. The `GET /healthz` liveness answer belongs to the platform team and is not about tokens, so I did not write it. I propose a separate record, ADR-0007, owned by the platform team. Say so and I will draft it.

Questions:

1. What is the GitHub account of the owner, and of the security architect? The record has `<owner GitHub account>` and `<account>` as placeholders.
2. O1: which signing algorithms does the service accept?
3. O2: where does the response carry `TOKEN_SIGNATURE_INVALID`?
4. R2 carries the tags `verify` and `server`, on the assumption that `internal/verify` decides the refusal and `internal/server` writes the 401. Is that right?

The status stays `Proposed` until O1 and O2 are settled. I did not change `docs/adr/README.md`, because the layers `verify` and `server` already exist there.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-jwks-and-require-kid.md

````markdown
# Take signing keys from the JWKS of each trusted key source, hold them for 5 minutes, and refuse a token with no `kid`

## Status

Proposed

### Owner

`<owner GitHub account>`

### Participants and approvers

- Security architect, `<account>`: approves R1 to R3.

## Context

The service verifies tokens with signing keys. The security architect decided where the keys come from, how long the
service holds them, and how it answers a token that names no key. The three choices change together when the key
handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **JWKS**: a JSON Web Key Set, as RFC 7517 defines it.
- **trusted-key-sources**: the key sources listed in `<file that lists the trusted key sources>`. O1 asks what a key
  source needs to join and who approves it.
- **loaded key set**: the keys that the service read from the JWKS of one key source in one load.

### Rules

#### Key sources

- **R1** (`keys`). The service takes a signing key for token verification only from the JWKS of a key source in
  trusted-key-sources.

#### Key lifetime

- **R2** (`keys`). The service takes a signing key from a loaded key set only within 5 minutes (300 seconds) of the load
  of that key set, and loads the JWKS of that key source again before it takes a key after that time.

#### Key identifier

- **R3** (`verify`, `server`). The service refuses a token whose header has no `kid` with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

A fixed list of key sources limits which issuers the service trusts (R1). A 5-minute hold limits how often the service
loads a JWKS, and limits how long a key that a source changed stays in use (R2). A token with a `kid` names the key to
use, so the service does not have to guess among the keys of a source (R3).

### Alternatives considered

- **A1. Try every key of a key source when the header has no `kid`.** Rejected by R3: the token names no key, so the
  service would test it against each key until one verifies.

## Consequences

Negative:

- A key that a source adds or removes reaches the service after up to 5 minutes (R2).
- A token that carries no `kid` is refused, even where its signature would verify under one of the keys (R3).

## Open points

- **O1.** What does a key source need to join trusted-key-sources, who approves a new one, and which file lists them?
  The security architect decides. It affects R1, and the answer becomes rules of this record.
- **O2.** What does the service do when a reload under R2 fails: refuse the token, or keep using the expired key set for
  some time? The security architect decides. It affects R2.
- **O3.** Where does a response carry the reason code `TOKEN_KID_MISSING`: a field of the response body, a header, or
  both? The security architect decides. It affects R3.
````

### Message to the user

I wrote one record, because one authority decided the three choices and they change together.

Questions:

1. What is the GitHub account of the owner, and of the security architect? The record has placeholders for both.
2. O1: which file lists the trusted key sources, what must a source meet to join, and who approves a new one? The record cannot name the members, because the set will change.
3. O2: what happens when a reload of a JWKS fails after the 5 minutes pass?
4. O3: where does the response carry `TOKEN_KID_MISSING`?
5. R3 carries the tags `verify` and `server`, on the assumption that `internal/verify` decides the refusal and `internal/server` writes the 401. Is that right?

I read "holds a loaded key set for 5 minutes" as a limit counted from the load of each key source. If the notes meant something else, tell me and I will change R2.

The status stays `Proposed` until the open points are settled. I did not change `docs/adr/README.md`, because the layers `keys` and `verify` already exist there.
