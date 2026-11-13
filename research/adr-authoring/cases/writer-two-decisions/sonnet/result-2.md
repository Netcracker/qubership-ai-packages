## Request 1

### File: docs/adr/0006-verify-token-signature-before-policy-evaluation.md

````markdown
# Verify the signature of every token before policy evaluation and refuse an invalid one

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 and R2.

## Context

The service checks the token of each request before policy evaluation. Policy evaluation reads the claims of the
token, so it depends on the token being genuine.

## Decision

We will verify the signature of the token of every request before policy evaluation, and refuse a request whose token
signature does not verify with HTTP 401 and the reason code `TOKEN_SIGNATURE_INVALID`.

### Terms

- **token**: the token that the service checks in a request before policy evaluation.
- **policy evaluation**: the step that decides whether the service allows a request.
- **refuse a request**: the service answers the request with the stated HTTP status and reason code, and does not run
  policy evaluation for it.

### Rules

#### Signature verification

- **R1** (`verify`). For every request that carries a token, the service verifies the signature of the token before it
  runs policy evaluation for that request.
- **R2** (`verify`, `server`). The service refuses a request whose token signature does not verify, with HTTP 401 and
  the reason code `TOKEN_SIGNATURE_INVALID` in `<reason code field>`.

### Justification

Policy evaluation reads the claims of the token, and an unverified token can carry any claims. Verifying first keeps
such a request out of policy evaluation (R1, R2).

### Alternatives considered

- **A1. Run policy evaluation first and verify the signature afterward.** Rejected by R1: policy evaluation would act
  on the claims of a token that is not yet known to be genuine.

## Consequences

Negative:

- Every request that carries a token pays the cost of one signature verification (R1).
- A request whose token has an invalid signature is refused, also where its claims would pass policy evaluation (R2).

## Open points

- **O1.** The notes do not name the field that carries the reason code in the response. The security architect decides.
  It affects R2.
- **O2.** The notes do not say which algorithms and which keys count as a verified signature. The security architect
  decides. It affects R1 and R2.
- **O3.** The notes do not say what the service does with a request that carries no token. The security architect
  decides. It affects R1.
````

### Message to the user

I wrote one record, ADR-0006, from the security architect's decision. I did not write the second decision, and I propose a separate record for it.

- **Why the split:** the `GET /healthz` liveness probe is the platform team's decision and changes for a different reason. A liveness probe has no place in a record about tokens. Say if you want me to draft it as ADR-0007, owned by the platform team.
- **Status:** the record is `Proposed`. It stays that way until the team signs off and O1 to O3 are closed.
- **Owner and approver:** I did not have a GitHub account for either, so both are placeholders. Who owns ADR-0006, and what is the security architect's account?
- **Open points:**
  - O1: which field of the 401 response carries `TOKEN_SIGNATURE_INVALID`.
  - O2: which algorithms and keys count as a verified signature.
  - O3: what happens to a request with no token.
- **Layers:** I tagged R2 with `verify` and `server`, because I could not see which package builds the 401 response. Correct the tag if only one of them is right.
- **Not checked:** I could not read ADRs 0001 to 0005, so there is no **Related ADRs** section. Tell me if one of them overlaps. I copied the metadata block from the template, so compare it with the existing records.
- **Not added:** I added no **Confirmation** entries, because I know of no test for these rules.
- **Reading guide:** `docs/adr/README.md` needs no change, because `verify` and `server` are already mapped.

## Request 2

### File: docs/adr/0006-take-signing-keys-from-trusted-jwks-and-require-kid.md

````markdown
# Take signing keys from the JWKS of trusted key sources, hold them for 5 minutes, and require a `kid`

## Status

Proposed

### Owner

`<GitHub account of the owner>`

### Participants and approvers

- Security architect, `<GitHub account>`: approves R1 to R3.

## Context

The service verifies the signature of each token with a signing key. Where the service gets those keys, how long it
keeps them, and what it does with a token that names no key are three choices about key handling. When the key
handling changes, all three change together.

## Decision

We will take signing keys from the JWKS of each trusted key source, hold a loaded key set for 5 minutes, and refuse a
token whose header has no `kid` with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

### Terms

- **JWKS**: a JSON Web Key Set, as RFC 7517 defines it.
- **key set**: the set of keys that one load of a JWKS returns.
- **trusted key source**: a key source listed in `<file that lists the trusted key sources>`. O1 asks what qualifies a
  source for that list.
- **refuse a request**: the service answers the request with the stated HTTP status and reason code, and does not run
  policy evaluation for it.

### Rules

#### Key sources

- **R1** (`keys`). The service takes the signing keys that it verifies tokens with only from the JWKS of a trusted key
  source.
- **R2** (`keys`). The service holds a key set for 5 minutes (300 seconds) after it loads it, and does not use that key
  set for token verification after that time.

#### Token header

- **R3** (`verify`, `server`). The service refuses a request whose token header has no `kid`, with HTTP 401 and the
  reason code `TOKEN_KID_MISSING` in `<reason code field>`.

### Justification

R1 to R3 come from one decision about key handling and change together, so they sit in one record. A token whose header
names no `kid` cannot be matched to a key in a key set (R3). Holding a key set for a fixed time bounds how long the
service uses a key that its source has since changed (R2).

## Consequences

Negative:

- A key that a trusted key source adds, rotates, or removes reaches the service only after the held key set expires, so
  for up to 5 minutes the service may verify with the old key set (R2).
- A token whose header has no `kid` is refused, also where the key set holds one key that could verify it (R3).

## Open points

- **O1.** The notes do not say what qualifies a key source as trusted or where the list is kept. The security architect
  decides. It affects R1. The skill's usual answer is a named set in one repository file, with a rule that requires a
  `CODEOWNERS` entry for it.
- **O2.** The notes do not say what the service does when the held key set has expired. This record assumes that it
  loads the JWKS again before it next verifies a token (R2). The security architect confirms or corrects this.
- **O3.** The notes do not say what the service does when loading a JWKS fails. The security architect decides. It
  affects R1 and R2.
- **O4.** The notes do not say whether a `kid` that is present and empty counts as having no `kid`. The security
  architect decides. It affects R3.
- **O5.** The notes do not name the field that carries the reason code in the response. The security architect decides.
  It affects R3.
````

### Message to the user

I wrote one record, ADR-0006. The three choices (JWKS key sources, the 5-minute hold, and the `kid` refusal) have one deciding authority and change together, so they stay in one record.

- **Status:** the record is `Proposed`. It stays that way until the team signs off and O1 to O5 are closed.
- **Owner and approver:** I did not have a GitHub account for either, so both are placeholders. Who owns ADR-0006, and what is the security architect's account?
- **Assumption (O2):** the notes say the service "holds a loaded key set for 5 minutes" but not what happens afterward. I assumed that it loads the JWKS again. R2 is written as "does not use that key set after that time", which does not depend on that assumption.
- **Open points:**
  - O1: what qualifies a key source as trusted, and where the list is kept. I left `<file that lists the trusted key sources>` as a placeholder.
  - O3: what happens when a JWKS load fails.
  - O4: whether an empty `kid` counts as missing.
  - O5: which field carries the reason code.
- **Layers:** R3 is tagged `verify` and `server`, because I could not see which package builds the 401 response. Correct the tag if only one of them is right.
- **Not checked:** I could not read ADRs 0001 to 0005, so there is no **Related ADRs** section. Tell me if one of them overlaps. I copied the metadata block from the template, so compare it with the existing records.
- **Not added:** I added no **Confirmation** entries, because I know of no test for these rules.
- **Reading guide:** `docs/adr/README.md` needs no change, because `keys`, `verify`, and `server` are already mapped.
