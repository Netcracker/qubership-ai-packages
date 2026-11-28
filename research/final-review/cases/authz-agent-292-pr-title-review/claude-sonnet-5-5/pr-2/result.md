# Final review of `08d388e..HEAD` (b6b79c5)

**Inputs.** The change has one commit and edits two ADR pages: ADR-0091 and ADR-0095. No code is involved, so I used the §2a analogues under every item. I did not run the drift script (`comment-drift.py`) because there are no members or doc comments to parse. I loaded `english-developer-style` and read `apm-authoring` only as far as its package rules, which do not apply to ADR pages. No task statement was handed over, so the claimed cases come from the commit message alone. The pull request title and description were handed over, with `cd2f261` as the start of the diff. There is no previous report.

**The commit message and the pull request text disagree.** The commit message and the diff remove `TOKEN_REALM_UNKNOWN` and refuse nothing in R79. The pull request text says the opposite. This is the first finding below.

## Item 1: Comments consistent with the code and with each other

Analogue used: every statement the changed pages make about another rule, another page, or a cited standard.

**1a. The pull request title and description claim a design the diff does not contain.** *Substantive.*
- The diff from `cd2f261..HEAD` adds no `TOKEN_REALM_UNKNOWN`, no "missing realm" result, and no refusal of a JWKS under R79. Each of these is stated as present in the title or the description:
  - The title says the change adds `TOKEN_REALM_UNKNOWN`.
  - The description says R39 yields a "missing realm" when the source is a realm with no keys loaded.
  - It says R23 has a 401 `TOKEN_REALM_UNKNOWN` row.
  - It says R79 "refuses the response for any other pair" of entries.
  - It says A13 rejects loading the rest of such a JWKS.
  - It says A14 rejects counting a required realm's 404 as a failure, "as on `main`", while R14, R17, and R19 keep the agent not ready.
  - It says ADR-0095 R16 lists three codes under R23.
  - It says the same for "ADR-0095 A2".
  - It says "Alternative A12 is not used."
  - Its user-visible bullets and costs describe 401 `TOKEN_REALM_UNKNOWN` and refused JWKS responses.
  - It says #208 "gives `TOKEN_REALM_UNKNOWN`".
  - It says ADR-0104 cites "these rules as this change leaves them".
- Actual state at HEAD:
  - R39 has three results: an answer, a 404, and a failure.
  - R23 maps a 404 to `TOKEN_KID_UNKNOWN`.
  - R79 loads every usable entry under one `kid` as a list. An entry with an `alg` verifies only a token with that `alg`.
  - `ADR-0091:363` has an alternative A17 that rejects a reason code of its own for a 404 (A16 rejects refusing a JWKS whose entries share a `kid`). A13 is gone.
  - A14 and A15 are reworded for the 404 result.
  - ADR-0095's table has no `TOKEN_REALM_UNKNOWN` row.
  - A2 of ADR-0095 is reworded.
  - ADR-0093 R3 is reworded.
- Request: rewrite the title and the description from the diff. The title should be along the lines of `docs(adr): define which responses ADR-0091 R39 counts as an answer, and give a 404 the code of an answer`.
- Request: the description must cover the 404 result, the list of keys under one `kid` (R79), A14 to A17, the new costs, and the ADR-0095 and ADR-0093 edits.
- Request: decide whether it still claims anything about #208 and ADR-0104. The description says #208 gives `TOKEN_REALM_UNKNOWN`. If so, #208 contradicts this ADR and needs a follow-up named. I cannot check ADR-0104 or #329 here.

**1b. R79 leaves the code of an `alg` mismatch undefined.** *Substantive.* `ADR-0091:148`, with R41 at `:199` and R43 at `:202`.
- R79 says a key from an entry with an `alg` verifies only a token with that `alg`. The Negatives (`:402`, `:405`) say such a token gets `TOKEN_ALG_NOT_ALLOWED` or `TOKEN_SIGNATURE_INVALID`.
- No rule says which. R41 refuses "any other `alg`", but that reads as the algorithms outside the allowed set, not a mismatch with the key's `alg`. R43 covers "a signature that does not verify".
- Cases left open:
  - every key under the `kid` is listed for another `alg`;
  - one key matches the `alg` and its signature fails, while another key is listed for another `alg`.
- Request: one sentence in R79 or R41 that names the code for each case, for example "`TOKEN_ALG_NOT_ALLOWED` when no key under the `kid` has the token's `alg` or no `alg`, otherwise `TOKEN_SIGNATURE_INVALID`". Then `:402` and `:405` can cite it.

**1c. The Justification sentence on R38 reads as two reasons spliced into one.** *Substantive.* `ADR-0091:287-289`.
- The sentence reads: "…because a 503 after an answer would report an outage that did not happen, and R23 gives a 404 the code of an answer".
- The clause after "and" is not part of the "because". The "because" clause also names only an answer, though the stored result can now be a 404 as well.
- Request: "…because a 503 after an answer or a 404 would report an outage that did not happen."

**1d. A source for the "list of keys" claim is mismatched with its cited standard.** *Substantive.* `ADR-0091:303-310`, and A16 at `:360`.
- The page cites RFC 7517 §4.5 as allowing several keys under one `kid`. That section says keys in one set SHOULD use distinct `kid` values, and gives different `kty` as an example of an exception.
- R79 loads any number of entries under one `kid`, whatever their `kty`. The cited section covers only the different-`kty` case.
- Request: say the decision goes beyond the RFC for the same `kty`, and give the reason that applies: the source lists the key, and refusing the response keeps withdrawn keys and drops added ones. A16 already carries that reason. As it stands, "as RFC 7517, section 4.5, allows" is read as the RFC covering R79.
- I checked RFC 7517 §4.4 (`alg`) from memory. It matches the page's use.

**1e. Terms the change introduces.** *Substantive.* One coinage: "the server of the keys" at `ADR-0091:383`.
- Other terms:
  - **Result, Last result, Source, Required source** are defined in the page's term list.
  - **404** as a result name: the field names the response by that status. Item 4 covers that point separately.
  - **List of keys** has no definition. It is an ordinary-sense use for R79, and the page uses "list" for the realms (R34) as well.
  - **Key material** and **usable entry**: "usable" is used at the base (R28, R42), and "key material" is the field's term.
- "The server of the keys" has no source. The page defines **Keycloak** and **Provider** and says "source" elsewhere. The sentence means "something other than the source", so the request is "A 404 that something other than Keycloak or the provider sends".

No sentence narrates the change ("now", "no longer") outside a place that allows it. The wording shapes from `english-developer-style` §4 occur only in the one sentence in 1c.

## Item 2: Claimed cases covered

Analogue used: each claim of the commit message, covered by the section that carries it.

| Claimed case | Section that handles it |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Term list, R39 |
| A 404 for any source, with or without keys loaded, keeps the keys held | R28 and the Justification (`:293-295`) |
| A token whose `kid` matches no key then gets `TOKEN_KID_UNKNOWN` | R23 table |
| R23 and the ADR-0095 table drop `TOKEN_REALM_UNKNOWN` | R23; ADR-0095 table at `:100`. ADR-0095 A2 and its Justification are also edited for the 404 case. |
| ADR-0095 Justification says a 404 is not an outage | ADR-0095 `:119-121` |
| A14: a 404 for a required source is not a failure | A14 |
| A15: still rejects counting only a 404 of the discovery document | A15 |
| A17: no code of its own for a 404 | A17 |
| R79: the usable entries of a JWKS under one `kid` load as a list, and an entry with an `alg` verifies only a token with that `alg` | R79 |
| A16: rejects refusing such a JWKS; A13 goes | A16; A13 absent |
| R80 stays | R80 unchanged |
| Negatives: deleted realm's tokens get the invented-`kid` code | Negatives (`:388-390`) |
| Negatives: a 404 for a provider or for a realm with keys gives 401 rather than 503 | Negatives (`:381-387`) |
| Negatives: a 404 that starts after a required source has keys logs no warning | Negatives (`:394-399`) |
| Negatives: a key added under a `kid` the agent holds starts no load | Negatives (`:400-402`) |
| User-visible: a source's 404 gives 401 `TOKEN_KID_UNKNOWN` | R23, R39 |
| User-visible: all keys under one `kid` load and any key that verifies passes | R79; gap in 1b |

- No command or runnable form is added, so there are no `none` rows to list.
- No test could fail the claims, because the change is a doc change. The detection is that each rule is stated so a reader can tell whether code obeys it. R79 fails that for the `alg` code (1b).
- **Claims read the other way.** Two hunks are not claimed by the commit message and are not covered by the pull request description (which claims something else).
  - ADR-0092 R2 and ADR-0093 R3 move their citation from R38 to R23. The ADR-0095 table and A2 are also edited. All three belong to the same code move, but the description lists only A2 and R16.
  - A new Negative on the key a source adds under a `kid` the agent already holds is stated in the commit message ("The Negatives add four costs") but not in the pull request text.
- The pull request-level findings are in 1a.

## Item 3: Boundaries, partitions, and the negative control

Analogue used: the partitions and the negative control are the cases of R38, R39, and R79 and what the page says does not apply. No instruction-file table applies: this is not a skill or an instruction file.

- **Partitions covered.** R39 covers a 404 for a provider, a realm with keys loaded, a realm without keys, and a required source (A14). A15 covers the discovery document's 404 against the `jwks_uri` 404. R79 covers entries with and without an `alg` and with different key material.
- **Negative control.** R38 states what counts as a result for a token that waited and for one whose load R33 refused.
- **Partition without evidence: the cost per token of a list (substantive).** `ADR-0091:307-310` and R80.
  - R79 loads any number of entries under one `kid`, and the page states R80 bounds the memory "and with it the length of a list". R80 allows up to 1 MiB for a response, so a list can hold well over a thousand RSA entries.
  - A token's check tries every key in the list when any key may verify it. Cost per request therefore grows with the length of the list, against a budget of 5 ms a request.
  - The Justification and the Negatives claim only a memory bound. This is a count that a source controls, so it needs a bound at any size.
  - Request: either a limit on the number of keys under one `kid` (a response that exceeds it is refused under R80, as for the size), or a statement that the check cost is bounded and why. This is not a cost beyond the stated production numbers.
- **State left by an earlier version.** The change replaces a design that R79 had refused. After a deploy no persisted data differs, because the agent holds keys in memory only. None.
- **Limits on the same work.** R80's 1 MiB is a limit on a response. The only other limit on the same work is R71's 3-second wait, which bounds a single request. None conflicts.

## Item 3a: Level, placement, and the environment

Analogue used: file placement and registration.

None. The edits sit in the ADRs that own the rules. `docs/decisions/README.md` needs no change (its only mention of these ADRs is "Defers: ADR-0091 R38 to #208"). I did not run a docs gate because the repository's own gate was not named, and I found no script for it in the diff.

## Item 4: Names by content, not by position

Analogue used: headings, cross-references, and case names.

None. A14 to A17 are ordinals by the page's convention. The alternatives skip A12 and A13 (A12 was never used, and A13 is removed here), so a reader may think they are missing. The description's "Alternative A12 is not used" does not explain A13. Taste: add one line to the page that the numbers A12 and A13 are unused, or renumber. I do not request it.

"A 404" as a result name is ordinary here: the code takes it from the status line, and the page says the agent does not read the body.

## Item 5: The failure report

Analogue used: whether each rule can be checked by a reader of a failing text.

- Each changed rule tells the reader what to look at: R23's table maps result to code, R39 names the three outcomes, and R81 names what the warning must carry.
- R23's table has two rows with the same code (`An answer` and `A 404`). The table reads fine. Taste only: merge them into "An answer or a 404", which would also remove the need to say in 1c that the two are treated alike. I do not request it.
- R79 does not detect the rule it is attached to: the code of an `alg` mismatch is not stated (1b).

## Item 6: What the writer says it verified

Analogue used: a passing exemplar and a failing case, named.

The commit message states no check, no exemplar, and no counter-example. For a doc change the evidence would be a read of each rule against the cases in the Negatives. For example, a deleted realm's token with and without keys held, a 404 for a provider, and a JWKS with two keys under one `kid` and an `alg` on one of them. R79's case with an `alg` on one entry gives no code in the rules (1b), and that case is not carried through.

## Item 7: Siblings of the change

Analogue used: places that enumerate or route to the artifact.

- Searched for `TOKEN_REALM_UNKNOWN`, "missing realm", `R38`, `R39`, `R79`, `R80`, and `R81` across `docs`. The only remaining mention of `TOKEN_REALM_UNKNOWN` is the new A17. No page still counts three codes under R23.
- The ADR-0095 table cites R23 and R39 for `TOKEN_KID_UNKNOWN`, and R23, R37, R38 for `TOKEN_KEYS_UNAVAILABLE`. Both match.
- The ADR-0095 introduction cites R23 and R38. Both are still true.
- ADR-0092 R2 and ADR-0093 R3 cite R23 for the 503 code, which matches the table.
- **Outside the repository (not checked).** #208 and ADR-0104 in #329 are named in the description as citing these rules. I could not read them. If #208 gives `TOKEN_REALM_UNKNOWN`, it now disagrees with R23 (1a).

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Pull request title and description describe the removed `TOKEN_REALM_UNKNOWN` design, not the diff | Substantive | PR text; diff `ADR-0091` R23, R39, R79, A13 to A17 | 1a |
| R79 does not state the code for a token whose `alg` matches no key, or fails on one that matches | Substantive | `ADR-0091:148`, `:199`, `:202`, `:402`, `:405` | 1b |
| The R38 Justification splices a second reason into a "because" clause and names only an answer | Substantive | `ADR-0091:287-289` | 1c |
| RFC 7517 §4.5 cited for a list under one `kid`, but R79 goes beyond different `kty` | Substantive | `ADR-0091:303`, `:360` | 1d |
| "The server of the keys" is a coinage | Substantive | `ADR-0091:383` | 1e |
| Per-token cost of the list of keys is not bounded under the 5 ms budget; R80 bounds memory only | Substantive | `ADR-0091:148`, `:307-310` | 3 |
| Alternatives skip A12 and A13 | Taste | `ADR-0091:345-349` | 4 |
| R23 table has two rows with one code | Taste | `ADR-0091:141-146` | 5 |

The checks I could not do: #208, ADR-0104, and the #329 text are outside this repository, so 1a and Item 7 rest on the description's own account of them.
