# Final review: `08d388e..b6b79c5`, "docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid"

The commit is a good change to ADR-0091 and ADR-0095, but it has six substantive findings. The two that matter most:

- **Wrong pull request title and description.** The open pull request still says the change adds `TOKEN_REALM_UNKNOWN`, which this commit removes.
- **R79 removes the only cap on keys under one `kid`.** A forged token can then cost far more than the 5 ms request budget.

The change is documentation only, so I filled the form through the analogues in §2a.

- **No task statement.** I took the claimed cases from the commit message alone.
- **Drift script.** It ran and printed nothing, because it does not parse Markdown.
- **Skills.** I loaded `english-developer-style`. `docs-page-authoring` is not among the provided skills. `apm-authoring` does not apply, because the change is neither a skill nor an instruction file.
- **Pull request.** I read the saved `gh/pr-view.json`. The pull request is `OPEN`, and its `baseRefOid` `cd2f261` is in the clone, so the pull request diff is `git diff cd2f261 HEAD`.

## Item 1: comments consistent with the code and with each other

Analogue used: the statements the records make about their own rules, about each other, and about RFC 7517.

**1a. The code of a token whose `alg` matches no key in its list is not stated.**
- **Where:** ADR-0091 R79 (`:148`–`:150`), and the Negatives at `:401`–`:402` and `:406`–`:407`.
- **What conflicts:**
  - R79 says that a key from an entry with an `alg` "verifies only a token with that `alg`". It names no code.
  - The Negatives say that such a token gets "`TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`".
  - R41 gives `TOKEN_ALG_NOT_ALLOWED` only to algorithms outside RS, PS, ES and EdDSA, which do not depend on any key.
  - So a reader of R41 and R43 gets `TOKEN_SIGNATURE_INVALID`. The existing code gets `TOKEN_ALG_NOT_ALLOWED`: at `internal/token/verify/verify.go:58`, `CodeAlgNotAllowed` covers an `alg` "that the key its kid names does not accept".
- **Mixed case:** with a list, one key can reject the `alg` while another accepts it and still fails the signature. No rule says which code wins.
- **Request:** one sentence in R79 that names the code when no key of the list accepts the token's `alg`, and the code when some key accepts it but none verifies it. The Negatives then cite R79 for those codes.

**1b. A condition is given to R19 that R19 does not state.**
- **Where:** ADR-0091 `:396`–`:398`: "because R19 warns only while the agent is not ready and R81 only for a source that is not required".
- **Problem:** R19 says only that the agent "retries a required source … logs a warning for each attempt, and stays not ready". It does not say "only while not ready". A reader of R19 alone could expect a warning for a required source that is already ready, and an implementer could add one.
- **Request:** either state in R19 when it stops warning (for example, "until the agent becomes ready"), or drop the "because" clause and cite R20.

**1c. "Every JWKS that a source publishes loads" is false for a response that R80 refuses.**
- **Where:** ADR-0091 `:305`. R80 refuses a body over 1 MiB, and the same paragraph cites R80 two sentences later.
- **Rule:** `english-developer-style` §4, *Keep a truth condition in the sentence it limits*.
- **Request:** "so every JWKS that R80 does not refuse loads".

**Other checks: none.**
- No sentence narrates the change.
- ADR-0095 A2, its Justification and the R16 table agree with R23.
- ADR-0092 R2 and ADR-0093 R3 cite only `TOKEN_KEYS_UNAVAILABLE`, which is still true.
- Nothing in the repository mentions a missing realm, `TOKEN_REALM_UNKNOWN` or A13 any more.
- **Terms:** "a 404" as a result is defined in the Terms list (`:69`), so it is not a coinage.

## Item 2: claimed cases covered

Claims from the commit message, and where each is handled:

| Claim | Where |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms `:69`; R39 `:183`–`:188` |
| A 404 for any source keeps the held keys | R28 (a key goes only on an answer without it); Justification `:293`–`:295` |
| A 404 then gives `TOKEN_KID_UNKNOWN` | R23 table `:144` |
| R23 and the ADR-0095 R16 table drop `TOKEN_REALM_UNKNOWN` | `:144`; ADR-0095 `:100` |
| ADR-0095 Justification: a 404 is not an outage | ADR-0095 `:119`–`:121` |
| A14, A15, A17 | `:349`–`:366` |
| R79 loads a list; any key may verify; `alg` restricts | `:148`–`:150` |
| A16 added, A13 removed, R80 unchanged | `:360`–`:362`; no A13; `:151` |
| The four Negatives | `:390`–`:402` |

No command is documented. No hunk goes beyond the claims: the A2 rewording and the edits to the R80 Negative follow from the claimed change.

**2a. The pull request title and description are false for the diff the pull request will show** (Substantive). That diff is `cd2f261..HEAD`. These parts are false:

- **Title.** "…, and add TOKEN_REALM_UNKNOWN". The diff adds no such code. Request: `docs(adr): define the result of a key load in ADR-0091 R39, and give a 404 the code of an answer`.
- **Opening paragraph.** "answers the first question with a reason code of its own". That is false.
- **R39 bullet.** It still describes "a missing realm … a failure … such as a 404 for a provider or for a realm with keys loaded".
- **R23 bullet.** It still lists `TOKEN_REALM_UNKNOWN` (401).
- **R79 bullet.** It still says entries load "as one key only when they share key material and `alg`, and refuses the response", and that "A13 rejects…".
- **Paragraph after the bullets.**
  - "A 404 for a realm in `keycloak.requiredRealms` counts like … a realm with no keys loaded". Now every 404 counts the same.
  - "ADR-0095 R16 lists the three codes under ADR-0091 R23". There are now two.
- **User-visible changes.**
  - The first bullet (`TOKEN_REALM_UNKNOWN`) and the fourth (a JWKS with two entries under one `kid` fails) are false.
  - Two user-visible changes against `main` are missing:
    - A 404 for a provider, or for a realm with keys loaded, now gives 401 `TOKEN_KID_UNKNOWN` instead of 503 `TOKEN_KEYS_UNAVAILABLE`.
    - Several keys under one `kid` now load, and any of them can verify a token.
- **Negative consequences.**
  - "gives the tokens of a realm with no keys 401" now applies to every source.
  - "a key it added does not load" leaves out the new cost: a key added under a `kid` the agent already holds starts no load.
- **#208 paragraph.** "#208 … gives `TOKEN_REALM_UNKNOWN` for a missing realm". This is now a gap between the record and that stack (see 7a). The paragraph should name that gap as a follow-up.
- **Scope.** "ADR-0104 in #329 cites these rules as this change leaves them (d1607e02)". I could not check #329 offline. The sentence names a commit from before this change, so it needs re-checking.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the sources, results and situations the change claims, and the limits it sets or removes.

**Partitions checked:** provider, realm, required, not required, with keys loaded, without keys loaded. Each gets a 404 and a code through R23, R28, R14 and the Negatives. The negative control, that a failure or no result still gives `TOKEN_KEYS_UNAVAILABLE`, is kept at `:145`. The R79 partitions with no code are filed under 1a.

**3a. R79 drops the only limit on keys under one `kid`, and 1 MiB is not enough to replace it** (Substantive).
- **The change:** R79 loads the usable entries under one `kid` "whatever their number". The Justification (`:308`–`:309`) names R80's 1 MiB as the bound on "the length of a list".
- **Size of a list under 1 MiB:** about 2,600 RSA-2048 entries at about 400 bytes each, or about 7,000 P-256 entries at about 150 bytes each.
- **Cost per token:** a token that names that `kid` with a bad signature is checked against every key whose `alg` admits it. That is roughly 80 ms for RSA and more for ECDSA, against the 5 ms request budget that `AGENTS.md` sets.
- **Repeat cost:** R60 does not cache a failed token, so every resend costs the same again.
- **Who controls the count:** the key source does. In a shared Keycloak that can be a tenant's realm administrator. `AGENTS.md` asks for a bound at any size on a count that a PIP controls.
- **Request:** a limit on the keys loaded under one `kid`, sized for what Keycloak publishes (a few keys per `kid`), with the result for a response over it (for example, R39 "a failure"). Then name that limit in the Justification instead of R80.

**3b. A 404 for a provider has no Negative of its own** (Taste). The Negative at `:384`–`:387` covers it through "any source", so this is wording only.

## Item 3a: level, placement, and the environment

Analogue used: where each rule lives, and the repository's own gate. None.
- The rules stay in the R23, R39 and R79 sections, and the alternatives are numbered on from A15.
- I ran `markdownlint-cli2` with the repository config over both files offline. It reported 0 issues.

## Item 4: names by content, not by position

None. The cross-references are rule and alternative numbers, which are stable identifiers in these records, plus RFC section numbers. Nothing refers to "above" or "below".

## Item 5: the failure report

Analogue used: whether each rule can be checked. None. R23 gives a code for each result, and R39's list ends with "every other case". The missing code for a mismatched `alg` is filed under 1a.

## Item 6: what the writer says it verified

The commit carries no evidence and none was handed over. The only basis it cites is the architect's decision of 2026-11-25. There is no worked case run against the new R23 or R79, for example a JWKS with two entries under one `kid` and the code of a PS256 token.

## Item 7: siblings of the change

**7a. Code that still implements the replaced design** (Substantive).
- **On `main`:** `internal/token/keys/fetch.go:256` refuses a JWKS with "kid %q names two different keys", and `keys.go:241`–`:247` holds a single `Key` per `kid`. Both now contradict R79 and A16.
- **In the #208 stack:** the pull request description says it gives `TOKEN_REALM_UNKNOWN` for a missing realm. I could not read #208 offline.
- **Request:** name both as follow-up in the pull request description, under `Defers` as `docs/decisions/README.md:43`–`:44` shows. Neither should be left unsaid.

**Set members checked, none outstanding.**
- The reason-code set lost a member. ADR-0095 R16 is the only table that lists the codes, and it is updated.
- The decisions README index (`:22`–`:23`) describes R23 without naming codes.
- No sentence still counts three codes.

## Findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| No code for a token whose `alg` no key of its list accepts; the Negatives and R41 disagree | Substantive | ADR-0091 `:148`–`:150`, `:401`, `:406` | 1 |
| The Negative gives R19 an "only while not ready" condition that R19 does not state | Substantive | ADR-0091 `:396`–`:398` | 1 |
| "Every JWKS that a source publishes loads" is false for a response that R80 refuses | Substantive | ADR-0091 `:305` | 1 |
| Pull request title and description still describe `TOKEN_REALM_UNKNOWN`, the missing realm, refusing entries under one `kid`, A13 and three codes | Substantive | pull request title and body | 2 |
| R79 removes the per-`kid` limit; 1 MiB allows thousands of verifications per forged token | Substantive | ADR-0091 `:148`, `:308` | 3 |
| A 404 for a provider has no Negative of its own | Taste | ADR-0091 `:384` | 3 |
| `fetch.go:256` and #208 implement the replaced design and are not named as follow-up | Substantive | `internal/token/keys/fetch.go:256` | 7 |

I could not do two checks offline: read #208 and #329, and confirm the Scope sentence of the pull request description.
