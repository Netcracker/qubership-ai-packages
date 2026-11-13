## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads claims from the token, so
a token with a forged or altered payload would reach policy evaluation unless its signature is checked first.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does
not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token a request carries in its `Authorization` header. O1 asks whether any other place carries one.
- **signature verifies**: the signature of a token matches the token content under the algorithms and keys that O2
  names.

### Rules

#### Signature check

- **R1** (`verify`). For every token, the service verifies the signature before it starts policy evaluation for the
  request that carries the token.
- **R2** (`verify`, `server`). For a request whose token signature does not verify, the service responds with HTTP 401
  and the reason code `TOKEN_SIGNATURE_INVALID`, and does not start policy evaluation for that request. O3 asks how the
  response carries the reason code.

### Justification

Policy evaluation decides on claims, and a claim can be trusted only after the signature over it has been verified (R1).
A distinct reason code lets a client tell a bad signature from other 401 causes (R2).

### Alternatives considered

- **A1. Evaluate policy first and verify the signature afterwards.** Rejected by R1: policy evaluation would act on
  claims that nobody has verified.

## Consequences

Negative:

- Every request pays the cost of a signature verification, including a request that policy evaluation would deny anyway
  (R1).
- A client sees HTTP 401 for a bad signature, and can no longer reach a policy decision for that token (R2).

## Open points

- **O1.** Does a token arrive anywhere other than the `Authorization` header, such as a cookie or a query parameter? The
  record assumes the `Authorization` header only. The security architect decides. This affects R1, R2.
- **O2.** Which signature algorithms and which keys make a signature verify, and how an unsigned token is treated? The
  security architect decides. This affects R1, R2.
- **O3.** Where does the response carry the reason code: a body field, a header, or both? The security architect
  decides. This affects R2.
````

### Message to the user

I wrote one record from these notes, not two. The notes hold two decisions with different authorities and different reasons to change: the security architect's signature check and the platform team's `GET /healthz` liveness answer. A liveness probe does not follow from a record about tokens, so it belongs in its own record. I left it out rather than write it unasked.

Question: should I write that second record as ADR-0007, `GET /healthz` answers HTTP 200 while the process runs, with the platform team as approver?

Details of the draft:

- The status is `Proposed`. The owner and the approver account are placeholders, because the notes give none. Which GitHub accounts should I use?
- O1 to O3 hold what the notes leave open: where a token can arrive, which algorithms and keys count as a verified signature, and how the response carries `TOKEN_SIGNATURE_INVALID`. The record needs answers to these before it can become `Accepted`.
- I tagged R2 with both `verify` and `server`, assuming `internal/verify` decides the outcome and `internal/server` writes the 401. Please correct this if the code splits differently.
- I wrote no Confirmation section, because I know of no test for these rules yet.
- Code under `internal/verify` and `internal/server` that lands for this record should end its commit message and pull request description with `Implements: ADR-0006 R1, R2`, once the record binds.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks.md

````markdown
# Take signing keys from the JWKS of each trusted key source

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 to R3.

## Context

The service verifies the signature of each token against a signing key. Which keys it uses, how long it keeps them, and
what it does with a token that does not say which key signed it are one set of choices about key handling, and they
change together when the key handling changes.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **trusted key source**: an entry of `trusted-key-sources`. O1 asks where the set lives and what an entry must meet.
- **key set**: the keys that one fetch of the JWKS of one trusted key source returns.
- **loaded key set**: a key set that the service has fetched and holds in memory.

### Rules

#### Key sources and key lifetime

- **R1** (`keys`). The service takes signing keys from the JWKS of each trusted key source, and from no other source.
- **R2** (`keys`). The service uses a loaded key set for verification for at most 5 minutes after it fetched that key
  set, and fetches the JWKS of its trusted key source again before it uses the key set after that time. O2 asks what
  happens when the fetch fails.

#### Tokens without a key identifier

- **R3** (`verify`). For a token whose header has no `kid`, the service responds with HTTP 401 and the reason code
  `TOKEN_KID_MISSING`.

### Justification

A fixed set of trusted key sources keeps a token from choosing its own key source (R1). The 5-minute limit bounds how
long the service keeps using a key that its source has removed, and bounds how often it fetches the JWKS (R2). A token
that names no `kid` cannot be matched to one key of a key set (R3). The three rules form one decision about key
handling, so they share one record.

### Alternatives considered

- **A1. Try every key of the key set when a token has no `kid`.** Rejected by R3: the token is refused without a key
  lookup, so a token never selects a key by trial.

## Consequences

Negative:

- A key that its source has removed stays usable for up to 5 minutes, until the service fetches the key set again (R2).
- A token without `kid` is refused even where the key set holds a single key (R3).

## Open points

- **O1.** Where is the set `trusted-key-sources` kept, and what does a key source need to join it: a file in the
  repository with a `CODEOWNERS` entry, or another form? The security architect decides. This affects R1, R2.
- **O2.** What does the service do when the fetch after the 5 minutes fails: refuse the tokens that need that key set,
  or keep using the expired key set for a further period? The security architect decides. This affects R2.
````

### Message to the user

I wrote one record, because the three choices change together and one authority settles them. The status is `Proposed`.

Questions:

- Which GitHub accounts are the owner and the approver? Both are placeholders now.
- Where is the set of trusted key sources kept, and what must a source meet to join? O1 holds this question, and R1 and R2 depend on the answer.
- What should the service do when the fetch after the 5 minutes fails? O2 holds this question.

Assumptions:

- I added "and from no other source" to R1, because "takes signing keys from the JWKS of each trusted key source" would otherwise pass code that also reads keys elsewhere. Please remove it if you do not mean it.
- I read "holds a loaded key set for 5 minutes" as a limit on how long the service uses a fetched key set.
- I tagged R1 and R2 with `keys` and R3 with `verify`, following the layer map in the guide.
- The record says nothing about a token whose `kid` matches no key in the key set, because the notes do not cover it. A new record can decide that case.
- I wrote no Confirmation section, because I know of no test for these rules yet.
- Code under `internal/keys` and `internal/verify` that lands for this record should end its commit message and pull request description with `Implements: ADR-0006 R1, R2, R3`, or with `Defers` for any rule the change leaves out and an existing issue that will bring it.
