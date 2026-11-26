I'm partway through the review. I've read the skill and the diff, loaded the English style skill, and checked every reference to the changed rules across the docs. I'm now writing the report.

# Final review: `08d388e..HEAD` (b6b79c5, docs-only ADR change)

**Inputs.**
- No task statement was handed over, so the claimed cases come from the commit message only.
- The saved `gh/pr-view.json` is the body of the PR this commit sits on. It describes the earlier design, so it is evidence for item 7 only.
- The change is two Markdown ADRs, so §2a applies and each item below reads its analogue.
- The drift script was not run: it parses no members in Markdown.
- Loaded: `english-developer-style`.
- Not loaded: `apm-authoring`, because no skill or instruction file changed. `docs-page-authoring` is not among the four copies I was given, so the ADR wording is checked against `english-developer-style` only.
- No command was run that the change tells anyone to run. The `make mutation-diff` step does not apply, because no Go code changed.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another and about itself)

Every R-number cited by the changed text was checked. R23, R28, R35, R36, R38, R39, R79, R80 and R81 were read against each other, and ADR-0095 R16 and A2 were read against ADR-0091.

**Finding 1.1 (substantive).** ADR-0091 line 304 says "so every JWKS that a source publishes loads". That is false under R80 (a body over 1 MiB is refused) and R24 (an entry without `kid` is not loaded). The quantifier ranges over a set the rules narrow.
- Request: "so a JWKS that lists several usable keys under one `kid` loads them all".

**Finding 1.2 (substantive).** R79 (lines 148–150) and Negatives (lines 401–407) leave open which code a token gets when the list under its `kid` has no key that verifies it.
- R41 reserves `TOKEN_ALG_NOT_ALLOWED` for an `alg` outside the accepted set.
- R43 gives `TOKEN_SIGNATURE_INVALID` for a signature that does not verify.
- R79 now makes an `alg` mismatch with an entry a reason that key does not verify, but names no code. The Negatives name both codes without saying when each applies.
- A reader implementing R79 cannot tell whether a token of RS256 against a PS256-only entry is "algorithm not allowed" or "signature invalid".
- Request: one sentence in R79 giving the code when no entry's `alg` matches and the code when entries match and none verifies. That is the code, R77 notwithstanding. The two Negatives bullets (lines 401–402 and 406–407) can then cite it.

**Finding 1.3 (substantive, wording).** Line 289 splices a new fact into a sentence that already worked (style §4 table, last two rows).
- The sentence explains why a result stored during a wait counts, because "a 503 after an answer would report an outage".
- The appended clause "and R23 gives a 404 the code of an answer" does not follow from that reason.
- Request: a separate sentence, for example "R23 gives a 404 the code of an answer, so a 404 stored during the wait gives `TOKEN_KID_UNKNOWN` too."

**Finding 1.4 (substantive, coined term).** Line 381 says "something other than the server of the keys". Neither the Terms nor the code name that thing. The Terms say "The word Keycloak names the server", and the term for where keys are read from is Source.
- Request: "A 404 that a proxy or another server on the path sends", or "something other than the source".
- The wording also appears at lines 291–292 as "whether Keycloak does not hold the realm or a proxy has no route", which is fine.

**Finding 1.5 (taste).** The scope "RFC 7517, section 4.5, allows" (lines 304 and 360–362) is narrower than what R79 accepts.
- The RFC says different keys SHOULD use distinct `kid` values, with different `kty` as an example of an exception.
- R79 also accepts the same `kty` with different key material.
- I would write "as RFC 7517, section 4.5, allows for keys of different `kty`, though it recommends distinct values", or drop the citation from A16.
- Expect this to be declined.

**Finding 1.6 (taste).** The first Negatives bullet added at lines 399–402 and the later bullet at lines 406–407 both state that a key added under a held `kid` gets `TOKEN_ALG_NOT_ALLOWED` or `TOKEN_SIGNATURE_INVALID` without a load. Merging them would remove the duplicate. The R23 table's two rows with the same code (lines 143–144) could also be one row, but each row maps one result, so I leave it.

Not findings:
- No narration of the change (`now`, `no longer`) was added.
- R28's first sentence lists only a failed reload, but its second sentence ("removed only when a load ends in an answer") covers a 404.
- R36 and R20 stay true.
- R81's "result is not an answer" now includes a 404 for a non-required source. The Justification and the Negatives agree with it.
- ADR-0095 R16, A2, the Justification and the related-ADR line match ADR-0091 R23, R38 and R39.

## Item 2: claimed cases covered

The claims from the commit message are listed below, each with the section that covers it.

| Claim | Covered by |
| --- | --- |
| A 404 gets no reason code of its own | R23 table, R39, A17, Justification lines 291–296 |
| Applies to a provider or a realm, with or without keys loaded | R39 item 2 has no condition. R23 row. A14 (required) and A15 (discovery versus `jwks_uri`). Negatives lines 381 and 394. |
| A 404 keeps held keys | R28's second sentence, Justification line 293, Negatives line 390 |
| Token with `kid` matching no loaded key then gets `TOKEN_KID_UNKNOWN`, as after an answer | R23, R38 |
| R23 and the ADR-0095 R16 table drop `TOKEN_REALM_UNKNOWN`. ADR-0095 Justification says a 404 is not an outage. | The ADR-0095 diff. `git grep REALM_UNKNOWN` over the repository returns nothing outside history. |
| A14, A15, A17 | Present, each with a rejecting rule |
| R79 loads the usable entries under one `kid` as a list, and any key verifies | R79, Justification lines 304–309 |
| An entry with an `alg` verifies only a token with that `alg` | R79, line 306 |
| A16 added, A13 removed, R80 unchanged | Present |
| Four added costs | Lines 389–391 (deleted realm), 381 and 394 (401 rather than 503), 394–398 (no warning), 399–402 (added key under a held `kid`) |

Every claimed case has a covering section.

**The claim read the other way.**
- Hunk "A2 rewritten" in ADR-0095 is covered by the commit message's reference to ADR-0095 R16 and the Justification. It is claimed implicitly. I count it as covered.
- The bullet about a Pod holding no keys of a deleted realm is reworded only by the removal of "missing realm". It is covered.
- The Negatives bullet rewrite for R80-only refusal (`R79 or R80` to `R80`) is claimed through "R79 loads ... whatever their number".

Not findings: no command is added or edited.

## Item 3: boundaries, partitions, negative control (analogue: genres and the statement of what does not apply)

Partitions of R39: answer (including an empty `keys` array), 404, and every other outcome. Partitions of R23: result is an answer, a 404, a failure, or no result. All four are in the table. Partitions of R79: one key, several under a `kid`, and an entry with an `alg` or without one. The control is unchanged behavior for a single key under a `kid`, which is covered by "whatever their number".

**Finding 3.1 (substantive).** R79 says "whatever their number", and the only bound is 1 MiB of body (R80). With about 100-byte entries the list can reach thousands of keys under one `kid`.
- A token with a held `kid` and a wrong signature tries every key whose `alg` fits. It is not cached (R60), so the cost is paid per request.
- The repository's cost rule requires a bound on a count controlled by a PIP at any size. The 5 ms budget per request is stated, and thousands of signature checks per request exceed it by orders of magnitude.
- Line 308 says the 1 MiB limit "bounds the length of a list", which is true but not the bound the budget needs.
- Request: a cap on the entries kept under one `kid`, with an explicit result when it is exceeded, as a new rule or in R79. Alternatively, say that only entries whose `kty` and `alg` fit the token's algorithm are tried, and cap those. The cap should be small, in line with how many keys one `kid` has in practice.

**Pre-existing state.** The change reads nothing an earlier version left behind.

**Limits.** The change sets no limit. It relies on R80, which it leaves as it was.

**Added instructions.** This is an ADR, not a skill or an instruction file, so there is no table.

## Item 3a: level, placement, and the environment

Both changed files sit beside their siblings in `docs/decisions/`. No registration entry changes: `docs/decisions/README.md` line 44 does not mention the changed rules. The repository's markdown gate was not run. None.

## Item 4: names by content, not by position

None. The new text refers to rules by number, which is the ADR's own scheme. Alternatives are cited as A14 to A17. A13 is removed and A12 stays unused, so the sequence has a gap that the PR description already states. No "see below" appears.

## Item 5: the failure report (analogue: what a rule tells the reader to look at)

Detection of the new rules is by the R-number each alternative cites. A16 cites R79 and A17 cites R23, and each does reach the rule it rejects. One check: A14's rejecting rule (R39) supports "the same code for every source", and the R14, R17 and R19 clause covers the wrong-address detection. None.

## Item 6: what the writer says it verified

Neither the commit message nor the change states a check that a rule can fail, such as an exemplar that passes and a bad case that fails. The commit message says the architect decided it on 2026-11-25, which is provenance, not evidence. I did not run the markdown gate. The writer's report should state which of the changed rules a worked case exercises. At minimum: a JWKS with two usable keys under one `kid` and different `alg` values, and a 404 for a required provider.

## Item 7: siblings of the change

- `git grep` for `REALM_UNKNOWN`, `missing realm`, `A13`, `R79`, `R38` and `R39` shows no other file in the repository that names the changed rules in a way the change leaves stale. The only other hit is ADR-0095, which the change updates.
- The Terms entry for Result, the R39 list, A15, and the Negatives all use "a 404" with no leftover "missing realm". The set of results is "answer, 404, failure" everywhere. No sentence counts the results as before.
- Siblings that cite `TOKEN_KID_UNKNOWN`: ADR-0092 R2 and ADR-0093 R3 cite R23 for the code and name no realm code. No change is needed.
- **Finding 7.1 (substantive).** The title and body of the PR this commit sits on (`gh/pr-view.json`) are now false.
  - The title says "add TOKEN_REALM_UNKNOWN".
  - The body describes the three results with "a missing realm" and says R79 "refuses the response for any other pair".
  - Its user-visible list claims a JWKS with two usable entries under one `kid` "fails the load", and that a token gets `TOKEN_REALM_UNKNOWN`.
  - Request: rewrite the title and body to the design this commit leaves, or name this commit as the one that supersedes those lines.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "every JWKS that a source publishes loads" contradicts R80 and R24 | Substantive | `20261029-authz-agent-adr-0091-…md:304` | 1 |
| R79 gives no code when no entry of the list verifies the token, or when `alg` mismatches | Substantive | `…adr-0091-…md:148, 401–407` | 1 |
| New clause on 404 spliced into the sentence about waits | Substantive | `…adr-0091-…md:289` | 1 |
| "the server of the keys" is a coined term | Substantive | `…adr-0091-…md:381` | 1 |
| RFC 7517 section 4.5 "allows" is broader than the RFC says | Taste | `…adr-0091-…md:304, 360` | 1 |
| Two bullets state the same added-key outcome | Taste | `…adr-0091-…md:399–407` | 1 |
| R79's list has no bound short of 1 MiB, and an invalid token pays per entry on every request | Substantive | `…adr-0091-…md:148, 308` | 3 |
| PR title and body still describe `TOKEN_REALM_UNKNOWN` and the refused JWKS | Substantive | PR title and body | 7 |

Not done: the drift script (Markdown, not parsed), `docs-page-authoring` (not among the four skill copies), and the repository's markdown lint gate (not run).
