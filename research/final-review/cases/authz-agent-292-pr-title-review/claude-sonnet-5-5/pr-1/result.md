# Final review: `08d388e..HEAD`, commit b6b79c5 "drop TOKEN_REALM_UNKNOWN and keep every key under one kid"

**Inputs.**
- There is no separate task statement, so the claimed cases come from the commit message alone.
- The open pull request is in `gh/pr-view.json`: state OPEN, base `main` at `cd2f261`.
- No previous report exists.
- This change is docs only (two ADRs), so §2a applies and the drift script was not run, because it has nothing to parse.
- I loaded `english-developer-style`. `apm-authoring` covers skills and instruction files, not ADR pages, and `docs-page-authoring` is not among the four skills, so I loaded neither. Wording was judged against `english-developer-style` §4 and §5.
- The "added instructions" table is for skills and instruction files only, so it does not apply here.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another, counts, citations)

Substantive: none. I checked these against the text:
- R23's table and R39's three results agree with each other.
- The Terms entry for `Result` agrees with R38 and R81.
- ADR-0095 R16 and A2 agree with R23.
- A14, A15, A16 and A17 each cite a rule that says what they claim.
- No `TOKEN_REALM_UNKNOWN` or "missing realm" remains outside A17, where "names a missing realm" describes the rejected code.
- The rule numbers cited in the new Negatives exist and say what the citations rely on.
- The RFC 7517 claims are correct for §4.4 (`alg` is the algorithm intended for the key) and §4.5 (different `kty` under one `kid`).
- The claim that R19 and R81 leave a later 404 of a required source without a warning holds. R19 covers a required source only while the agent is not ready, and R81 covers only a source that is not required.

Taste:
- `…091…md:171,175` (R28 and R36). The first sentence of R28 and R36 name only "a reload that fails". The 404 result is now separate from a failure. The Negatives and the Justification cite R28 and R36 for keys kept after a 404.
  - R28's second sentence still covers the case, so it reads correctly.
  - I would write "a reload that ends in a 404 or a failure" in R28 and R36.
- `…091…md:381`. "the server of the keys" is a phrase used nowhere else. The ADR says "source" and "Keycloak". Prefer "something other than the source".
- `…091…md:294-297`. The Justification cites RFC 7517 §4.5, which allows keys of different `kty` under one `kid`. R79 loads any number of usable entries, including entries of one `kty`. Naming that R79 goes wider than the RFC would stop a reader from taking the whole rule as RFC-backed.
- `…091…md:402,406`. The new Negative about a key added under a `kid` the agent already holds repeats the last sentences of the next Negative. The two could be merged.

## Item 2: claimed cases covered (analogue: the section that handles each claim)

| Claim in the commit message | Where it is handled |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms `Result`, R39 |
| A 404 for any source keeps the keys the agent holds | R28 second sentence, Justification |
| A kid with no loaded key gets `TOKEN_KID_UNKNOWN` | R23 table |
| R23 and ADR-0095 R16 drop `TOKEN_REALM_UNKNOWN` | R23; 0095 table, `…0095…md:101` |
| The ADR-0095 Justification says a 404 is not an outage | `…0095…md:119-122`, and A2 |
| A14 rejects counting a required source's 404 as a failure | A14 |
| A15 still rejects counting only the discovery 404 | A15 |
| A17 rejects a code of its own for a 404 | A17 |
| R79 loads the usable entries under one `kid` as a list; any key of the list may verify; an entry with an `alg` verifies only that `alg` | R79, Justification |
| A16 rejects refusing such a JWKS | A16 |
| A13 goes | gone |
| R80 stays | R80 unchanged |
| Four new Negatives (deleted-realm code, 401 not 503, no warning after keys, added key under a held `kid`) | Consequences, lines 388-402 |

No command is claimed, so there is no command table.

Hunks beyond the claim: none. The edit of ADR-0095 A2, from "Report missing keys" to "Report keys that could not be loaded", is needed for the new R23.

**The pull request.** The open title and body describe the design this commit reverses.
- The title says "and add `TOKEN_REALM_UNKNOWN`".
- The body says R39 ends in "a missing realm".
- The body says R23 maps it to `TOKEN_REALM_UNKNOWN` (401).
- The body says R79 loads entries only when they share key material and `alg`, and refuses the rest, and that A13 rejects loading the rest.
- The body lists these as user-visible changes: "refused with 401 and `TOKEN_REALM_UNKNOWN`" and "fails the load" for two entries under one `kid`.
- The body says ADR-0095 R16 lists three codes.
- The body says the stack's #208 gives `TOKEN_REALM_UNKNOWN`.
- The negatives it lists no longer match the ADR.

Finding F1 below is substantive. The request is a new title and description taken from the commit message: a 404 gets no code of its own, and R79 loads every usable entry under one `kid`. The description also needs the new `Result` wording, the new A14 to A17, and a check of the #208 sentence against the ADR.

## Item 3: boundaries, partitions, and the negative control (analogue: sources and situations the change claims, and what does not apply)

Partitions the change names:
- A provider, a realm with keys loaded, a realm without keys, and a required source versus one that is not required: R39, A14, and the first, second, and fourth new Negatives cover them.
- A 404 at discovery versus at `jwks_uri`: A15.
- The control, an answer to the load: R23 table row 1.
- Several keys under one `kid`: R79 and A16. R79 does not state the code when no key of the list verifies the token. The Negatives accept either `TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`, and R77 leaves the order to the implementer, so the gap is stated and not a finding.

Pre-existing state: the "deleted realm, Pods that hold keys" Negative covers the state older Pods carry.

Replaced mechanism and limits: none changed, since R80 and the 1 MiB limit are unchanged.

None.

## Item 3a: level, placement, and the environment

The layout matches the sibling ADRs, and no registration entry changed. `docs/decisions/README.md` mentions only R38 and ADR-0095 R2, both still valid. I ran the repository's docs gate nowhere, since none runs offline. Added lines are at most 120 characters.

None.

## Item 4: names by content, not by position

None. The new text refers to rules by number and by content, in the form the file already uses.

## Item 5: the failure report

None. The "detection" analogue is that each rule carries a way to tell whether a text obeys it. The new R39 results and the R79 rule are checkable from R23's table, so the check is not missing.

## Item 6: what the writer says it verified

The commit message states no verification. It names no consistency check of the rule numbers, no gate that ran, and no red case. For a rewrite of rules, the evidence is a pass over the previous worked cases (the old R39 case list and A13) against the new rules. I made that pass here and found no contradiction. The writer should state it.

## Item 7: siblings of the change

- `TOKEN_REALM_UNKNOWN` and "missing realm": every place is clean (searched across the repository; the only remaining hit is A17).
- R79: `git grep` over `docs` finds it only in ADR-0091.
- R23 and R39: the citing ADRs 0092 (line 65), 0093 (line 66), and 0095 (lines 23, 100, 130) match the new text.
- Counts: nothing in the prose still says "three codes" or counts the results as before.

None.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| F1. The open PR title and body still say the change adds `TOKEN_REALM_UNKNOWN`, a missing-realm result, and an R79 that refuses unequal entries | Substantive | PR title and body | 2 |
| R28 and R36 name only "a reload that fails" where a 404 reload is meant too | Taste | `…091…md:171,175` | 1 |
| "the server of the keys" is a new phrase | Taste | `…091…md:381` | 1 |
| R79 goes wider than the RFC case the Justification cites | Taste | `…091…md:294-297` | 1 |
| Two Negatives repeat each other | Taste | `…091…md:402,406` | 1 |

Check not done: GitHub was unreachable, so I read the pull request from the saved `pr-view.json` and could not fetch `baseRefOid`. The merge-base diff of the PR is therefore not read; F1 rests on the commit message against the saved body.
