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

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims of that token.

## Decision

We will verify the signature of every token before policy evaluation, and we will refuse a token whose signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **signature verifies**: verification of the token's signature against a signing key succeeds. Any other outcome of that verification means the signature does not verify.

### Rules

#### Signature verification

- **R1** (`verify`). For each request, the service verifies the signature of the token before it evaluates policy for that request.
- **R2** (`verify`, `server`). Where the signature of a token does not verify, the service responds with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`, and does not evaluate policy for that request.

### Justification

Policy evaluation only sees claims from a token whose signature verified (R1, R2).

## Consequences

Negative:

- Every request pays for one signature verification before policy evaluation (R1).
````

### Message to the user

I wrote ADR-0006 for the signature decision only. It is `Proposed`.

The notes hold two decisions. The security architect settled token signature verification. The platform team settled `GET /healthz`, which is a liveness probe and has nothing to do with tokens. Different authorities decide them, and they change for different reasons, so they need two records. I did not write the second one. Do you want ADR-0007 for `GET /healthz`, with the platform team as approver?

Questions and assumptions:

- Who is the owner, and which GitHub accounts belong to the approvers? I left placeholders in the record.
- I tagged R2 with `verify` and `server` because I could not see which code produces the 401 response. Correct the tag if only one layer produces it.
- The notes give no rejected alternatives, no checks and no cost beyond the verification itself. So I left out **Alternatives considered** and **Confirmation**, and the record lists only one cost.
- The Date heading is left out until the team accepts the record.

## Request 2

### File: docs/adr/0006-token-verification-key-handling.md

````markdown
# Take signing keys from the JWKS of trusted key sources, hold them for 5 minutes, and refuse a token without `kid`

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 to R3.

## Context

The service verifies the signature of each token with a signing key. The notes treat three choices about key handling as one decision, because all three change together when the key handling changes: where the keys come from, how long the service holds them, and what happens to a token that names no key.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **key source**: a service that publishes a JWKS.
- **trusted key source**: a key source that the service accepts signing keys from. O1 asks how the set of trusted key sources is defined.
- **loaded key set**: the keys of one JWKS, as the service read them from one trusted key source in one load.
- **load time**: the moment the service finishes reading a JWKS from a trusted key source.

### Rules

#### Key sources

- **R1** (`keys`). The service obtains signing keys for token verification from the JWKS of each trusted key source, and from no other place.

#### Key set lifetime

- **R2** (`keys`). The service uses a loaded key set for token verification for 5 minutes after its load time. After that, it reads the JWKS of that trusted key source again before it verifies a token with a key of that source.

#### Tokens without `kid`

- **R3** (`verify`, `server`). Where the header of a token has no `kid`, the service responds with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Justification

The three rules form one record because a change to key handling edits them together (R1, R2, R3).

## Consequences

Negative:

- A key that a trusted key source removes from its JWKS stays usable for up to 5 minutes, until the service reads that JWKS again (R2).
- A token without `kid` is refused, also where a loaded key set holds a key that could verify it (R3).

## Open points

- **O1.** How is the set of trusted key sources defined? The answers under consideration are a named set in one file in the repository, with `CODEOWNERS` covering that file, or a fixed list in this record. The security architect decides. This affects R1 and R2.
- **O2.** Assumption: R1 excludes every key location other than the JWKS of a trusted key source. The notes say only that the service takes keys from those JWKS. The security architect confirms or removes "and from no other place". This affects R1.
- **O3.** Assumption: "holds a loaded key set for 5 minutes" means 5 minutes counted from the load time, and that the service then reads the JWKS again. The other reading counts from the last use of the key set. The security architect decides. This affects R2.
````

### Message to the user

I wrote ADR-0006 as one record, `Proposed`. The three choices come from one authority and change together, so I kept them together.

Open points that block acceptance:

- **O1:** the notes do not say what makes a key source trusted. Do you want a named set in one repository file, or a fixed list in the record?
- **O2:** I assumed that R1 allows no key location other than a JWKS of a trusted key source.
- **O3:** I assumed the 5 minutes run from the load, and that the service then reads the JWKS again.

Other questions and assumptions:

- Who is the owner, and which GitHub accounts belong to the approvers? I left placeholders in the record.
- I tagged R3 with `verify` and `server` because I could not see which code produces the 401 response. Correct the tag if only one layer produces it.
- The notes give no rejected alternatives and no checks. So I left out **Alternatives considered** and **Confirmation**. If you name an alternative, I can add it.
- The Date heading is left out until the team accepts the record.
