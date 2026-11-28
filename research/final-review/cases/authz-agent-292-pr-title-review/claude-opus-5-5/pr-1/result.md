I found five substantive findings and one taste finding. The biggest is that the pull request title and description no longer match the diff: this commit undid most of what they claim.

# Final review: `08d388e..HEAD` (b6b79c5, "docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid")

**Inputs.**
- **Task statement:** none was handed over, so the claimed cases come from the commit message alone.
- **Pull request text:** read against the diff `cd2f261..HEAD`.
- **Previous report:** none.
- **Kind of change:** Markdown only (ADR-0091 and ADR-0095), so the form follows the no-code analogues in §2a.
- **Skills:** I loaded `english-developer-style`. `apm-authoring` covers skills and instruction files, not ADR pages, so I did not use it. The `docs-page-authoring` skill is not among the four supplied.
- **Drift script:** `comment-drift.py 08d388e HEAD` ran and printed nothing, because nothing in the change is code.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement the changed files make about another rule, ADR, or RFC.

What I checked and found consistent:
- `TOKEN_REALM_UNKNOWN`, "missing realm" (except inside A17's title, where it is meant), and A13 appear nowhere in `docs/`.
- ADR-0095 R16 cites ADR-0091 R23 and R39 for `TOKEN_KID_UNKNOWN`, and R23, R37 and R38 for `TOKEN_KEYS_UNAVAILABLE`. Both are correct.
- The ADR-0095 Justification sentence at `:119` and A2 at `:130` agree with R23's table.
- R28's second sentence ("removed only when a load ends in an answer") keeps keys on a 404, which `:293` relies on.

**1a (substantive). "A 404" names both the HTTP response and the result, and two sentences become hard to parse.**
- Terms `:69` defines a Result as "an answer, a 404, or a failure".
- R39 item 2 `:186` then reads "a 404, when a request of the load got a 404".
- A14 `:350` reads "a 404 for any source is a 404 rather than a failure". A reader takes this as a tautology until they work out which "404" is the result.
- `:288–289` has a fact spliced onto a reason that already worked (`english-developer-style` §4, row "A new fact spliced into a sentence that already worked"): "…because a 503 after an answer would report an outage that did not happen, and R23 gives a 404 the code of an answer". The reader has to work out whether the 404 clause is part of the reason.
- **Request:**
  - Name the result with a word distinct from the status code, such as "a not-found", in Terms `:69`, R23's table `:144`, R39 `:186`, A14 `:350`, A15 `:354`, and the Negatives that say "its result under R38 is a 404" (`:383`, `:389`, `:394`).
  - Split `:288` into two sentences: "…would report an outage that did not happen. R23 gives a not-found the same code as an answer."

**1b (substantive). `:304–305` "so every JWKS that a source publishes loads" is false as written.**
- R80 (`:151`) refuses a body over 1 MiB, and that condition sits in a later sentence (§4, "Keep a truth condition in the sentence it limits").
- **Request:** "so a JWKS loads whatever keys it lists under one `kid`, and the order of its entries decides nothing (R79)."

**1c (substantive). `:397` "because R19 warns only while the agent is not ready" gives R19 a condition R19 does not state.**
- R19 (`:128–130`) says the agent retries a required source, logs a warning per attempt, and stays not ready. It sets no readiness condition on the warning.
- This matters once the agent is ready: an answer with an empty `keys` array (R28) leaves a required source with no keys, and R20 keeps the agent ready. A reader of `:397` concludes R19 is silent there; a reader of R19 does not.
- The sentence also chains "because … and …, so …" across 45 words.
- **Request:** state the reason from the source's state, such as "R19 retries only a required source that has no usable key". Put the conclusion "so only the refusals with `TOKEN_KID_UNKNOWN` show it" in a sentence of its own.

**1d (taste).**
- `:400–402` and the last sentences of `:405–407` both describe a key added under a `kid` the agent already holds. One of them could go.
- "the server of the keys" (`:381`) is a new phrase where "source" is the ADR's term.

Coinages: apart from the "404" overload filed in 1a, none.

## Item 2: claimed cases covered

Analogue used: the section that handles each claimed case. There are no commands in the change.

The claimed cases are all present:

| Claimed case (commit message) | Section |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms `:69`, R39 `:183–190` |
| A 404 for any source keeps the held keys | R28 `:159`, Justification `:293` |
| A 404 then gives `TOKEN_KID_UNKNOWN` | R23 table `:144` |
| R23 and ADR-0095 R16 drop `TOKEN_REALM_UNKNOWN` | `:141–145`; ADR-0095 `:97–108` |
| The ADR-0095 Justification says a 404 is not an outage | ADR-0095 `:119–120` |
| A14, A15 and A17 present; A13 removed | `:349–365` |
| R79 loads a list, any key verifies, `alg` restricts | `:148–150`, `:304–308` |
| A16 present | `:360` |
| R80 unchanged | `:151` |
| Deleted realm gets the invented-`kid` code | Negative `:388` |
| 404 for a provider or a realm with keys gives 401 rather than 503 | `:381`, `:394` |
| No warning for a required source's later 404 | `:397` (but see 1c) |
| A key added under a held `kid` starts no load | `:400` |
| Both user-visible changes | R23, R79 |

Read the other way, no hunk of this commit goes beyond the commit message.

**2a (substantive). The pull request title and description describe the design this commit removed.** Checked against `cd2f261..HEAD`:

- **Title.** "…and add TOKEN_REALM_UNKNOWN" is false. Request: `docs(adr): define which responses ADR-0091 R39 counts as an answer or a 404, and load every key under one kid`.
- **First paragraph.** It says the redesign approved on 2026-11-23 answers with "a reason code of its own". Now A17 rejects such a code, and the commit cites a decision of 2026-11-25. Request: name the 2026-11-25 decision and say that a 404 gets `TOKEN_KID_UNKNOWN`.
- **Problem paragraph.** It says the deleted-tenant audit problem is a defect on `main`. The change now keeps that outcome and lists it as a cost (`:388`). Reframe it, or drop it from the problem statement.
- **Terms bullet.** "an answer, a missing realm, or a failure" becomes "an answer, a 404, or a failure".
- **R39 bullet.** Replace "missing realm… failure… such as a 404 for a provider or for a realm with keys loaded" with "a 404 when any request of the load got a 404", and say that R79 no longer refuses.
- **R23 bullet.** Drop `TOKEN_REALM_UNKNOWN` and say that an answer and a 404 both give `TOKEN_KID_UNKNOWN`.
- **R79 bullet.** Replace it with the list rule. Change "A13 rejects…" to A16, and add A17.
- **ADR-0095 bullet.** "ADR-0095 R16 lists the three codes" becomes "the two codes".
- **User-visible changes:**
  - Replace the first bullet (401 `TOKEN_REALM_UNKNOWN`) with the commit's line: `TOKEN_KID_UNKNOWN` for every source.
  - The fourth bullet says a JWKS with two entries under one `kid` fails the load. That is false now; keep only the 1 MiB part.
  - Add the behavior change against `main`, where R39 counted a 404 for a provider, or for a realm with keys, as a failure (503). It now gives 401 `TOKEN_KID_UNKNOWN`.
  - Add the new list behavior.
- **Negative consequences.** Update "tokens of a realm with no keys" to "of any source". Replace "a required realm that never loaded a key" with the new `:394` bullet. Add the deleted-realm cost and the cost of a key added under a held `kid`.
- **Code paragraph.** It says #208 gives `TOKEN_REALM_UNKNOWN`. The ADR now asks #208 to drop that code and to load lists. Say so as a follow-up on #208.
- **Scope paragraph.** "ADR-0104 in #329 cites these rules as this change leaves them (d1607e02)" cannot hold for rules this commit changes, and d1607e02 is not in the local repository. Re-check it. "Alternative A12 is not used" should now read "A12 and A13".

## Item 3: boundaries, partitions, and the negative control

Analogue used: the source kinds and the token-wait situations the change claims.

**Partitions present:**
- A provider, a realm with keys, and a realm without keys (R39, `:381`, `:388`).
- A required and a non-required source (`:394`, R81).
- A 404 on discovery versus on the `jwks_uri` (A15).
- Waited, joined, timed out, canceled, and R33-refused tokens (R38).
- An entry with and without `alg` (R79).
- **Negative control:** R39 item 3 lists the failures (a 200 with another body, a timeout, a 5xx, an R80 refusal).

**3a (substantive). R79 drops the one-key-per-`kid` limit, and the 1 MiB of R80 that `:308` names as the bound on a list's length does not fit the request budget.**
- **How long a list can get.** A minimal Ed25519 JWK is about 75 bytes, so 1 MiB holds roughly 14,000 entries under one `kid`. An RSA-2048 JWK is about 400 bytes, so roughly 2,600.
- **What each request costs.**
  - Under R79 a token is checked against every key under its `kid` whose `alg` matches or is absent.
  - R60 does not cache a refused token.
  - So every request with a forged signature under that `kid` costs the whole list: about 2,600 × ~30 µs ≈ 80 ms for RSA, and 14,000 × ~50 µs ≈ 0.7 s for Ed25519.
  - The repository's instructions give a request 5 ms.
- **Why it needs a bound.** The key source controls this count, and R80 already treats its responses as untrusted in size. No Negative states this cost.
- **Request:** a limit on the entries loaded under one `kid`, derived from the 5 ms budget (a handful, not thousands), with the refusal or truncation rule it implies. Alternatively, a Negative that accepts the cost with its numbers.

## Item 3a: level, placement, and the environment

None. Each rule sits in ADR-0091 under its section. R79 gained the `verify` tag, which fits its new verification clause. ADR-0095 changed only its index and Justification. I could not run the Markdown lint gate offline (no `markdownlint` installed). A manual check found no prose line over 120 columns in either file.

## Item 4: names by content, not by position

None. Rules and alternatives use stable IDs (R79, A16, A17). The gap from A11 to A14 follows the record's practice of not reusing numbers. The only issue is the pull request's "A12 is not used" sentence, filed under 2a.

## Item 5: the failure report

None. This change has no checklist or detection of its own. Each R-rule names the reason code a reader can observe for its outcome.

## Item 6: what the writer says it verified

Neither the commit message nor the pull request text names a case the new rules pass or fail, such as a JWKS sample or a walk-through of a 404. Nothing is stated.

## Item 7: siblings of the change

Searches for `TOKEN_KID_UNKNOWN` and `TOKEN_KEYS_UNAVAILABLE` across the repository (outside `policies/`) found:
- ADR-0091, ADR-0092, ADR-0093 and ADR-0095: all consistent at HEAD. ADR-0092 R2 and ADR-0093 R3 cite R23 for `TOKEN_KEYS_UNAVAILABLE`, which still holds.
- `internal/token/verify/verify.go` and its test: code from before the ADR, never using `TOKEN_REALM_UNKNOWN`.

`internal/token/keys/keys.go:168` still fails a load when two providers publish one `kid`. That is code from before the ADR, which R21 replaces, and it belongs to the #208 stack (see 2a). No sentence in the change still counts three codes.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "A 404" names both the response and the result; the A14 tautology and the spliced clause at `:288` | Substantive | ADR-0091 `:69`, `:186`, `:288`, `:350` | 1 |
| "every JWKS that a source publishes loads" leaves out R80 | Substantive | ADR-0091 `:305` | 1 |
| "R19 warns only while the agent is not ready" is not in R19; 45-word because/so chain | Substantive | ADR-0091 `:397` | 1 |
| Repeated held-`kid` sentences; "the server of the keys" | Taste | ADR-0091 `:381`, `:400`, `:405` | 1 |
| PR title and description claim `TOKEN_REALM_UNKNOWN`, R79 refusal, A13, three codes, a stale #208/ADR-0104 status, and miss the 404→401 change for providers and realms with keys | Substantive | PR text | 2 |
| R79 list length is bounded only by 1 MiB; a forged token costs ~80 ms–0.7 s against a 5 ms budget | Substantive | ADR-0091 `:148`, `:308` | 3 |

I could not verify #208 (e759672a), #329 or d1607e02, because those commits are not in the local repository and there is no network. I also could not run the Markdown lint gate offline.
