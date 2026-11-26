# Final review: `08d388e..b6b79c5`, "docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid"

The change touches only two ADRs, so I filled the form through the §2a analogues for a docs page:

- **Task statement:** none was handed over, so the claimed cases come from the commit message alone. I also read the saved PR view (`gh/pr-view.json`).
- **Skills loaded:** `english-developer-style`. `docs-page-authoring` is not in the provided skills, so I didn't load it. `apm-authoring` and `test-authoring` don't apply, because the change has no skill, instruction file or test.
- **Drift script:** it ran and printed nothing, because it doesn't parse Markdown.
- **Files:** ADR-0091 is `docs/decisions/20261029-authz-agent-adr-0091-verify-tokens-before-policy-evaluation.md` and ADR-0095 is `docs/decisions/20261029-authz-agent-adr-0095-refuse-before-policy-evaluation.md`.

## Item 1: comments consistent with the code and with each other
*Analogue: the statements the ADRs make about each other and about the documents they cite.*

I checked:
- the new Result term (`:69`) against R23, R28, R38, R39 and R81;
- the ADR-0095 R16 table and Justification, and A2, against ADR-0091 R23;
- the RFC 7517 §4.4 and §4.5 claims, which match the RFC;
- the other places that cite ADR-0091 R23: ADR-0092 `:65` and ADR-0093 R3. Neither still names `TOKEN_REALM_UNKNOWN` or a missing realm.

I found no coined term. "a 404" is the HTTP status.

**1a. Substantive. `ADR-0091.md:148` (R79) never says which code a token gets when no key of the list accepts its `alg`.**
- The Negatives at `:401` and `:407` say such a token gets `TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`, and cite R41.
- R41 (`:199`) gives `TOKEN_ALG_NOT_ALLOWED` only for an algorithm outside the accepted set. So nothing gives it for a PS256 token whose `kid` lists only RS256 keys.
- The current code makes the opposite choice: `internal/token/verify/verify.go:285` returns `CodeAlgNotAllowed` when the key does not accept the `alg`.
- With a list, a token can also meet both cases at once: one key accepts its `alg` but fails the signature, and another key doesn't accept the `alg`.
- **Request:** one sentence in R79 that gives the code for "no key of the list accepts the `alg`", and the code for the mixed case, or a citation of R77 if the order is left to the implementer. Then cite R79 instead of R41 at `:401` and `:407`.

**1b. Substantive (wording). `ADR-0091.md:288–289` splices a new fact into a sentence that already worked.**
- The sentence reads "…because a 503 after an answer would report an outage that did not happen, and R23 gives a 404 the code of an answer".
- A reader can't tell whether the last clause is a second reason or a separate fact. This is the "new fact spliced into a sentence" shape in `english-developer-style` §4.
- **Request:** end the sentence at "did not happen" and add: "R23 gives a 404 the code of an answer, so a 503 after a 404 would report an outage too."

**1c. Taste. `:305` says "so every JWKS that a source publishes loads".**
- This isn't true of a body over 1 MiB, which R80 refuses.
- **Suggestion:** "so a JWKS loads whatever `kid` its entries share".

**1d. Taste. Two Negatives state the same fact.**
- The new bullet at `:400–402` and the kept sentence at `:405–407` both say a key added under a `kid` the agent already holds starts no load and gets `TOKEN_ALG_NOT_ALLOWED` or `TOKEN_SIGNATURE_INVALID`.
- **Suggestion:** drop the sentence from the R80 bullet.

**1e. Taste. `:381` "the server of the keys"** could be "the source", the defined term.

## Item 2: claimed cases covered
*Analogue: for each claim in the commit message, the section that handles it.*

| Claim in the commit message | Where it is handled |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms `:69`; R39 `:183–190` |
| A 404 for any source, with or without keys loaded, keeps the keys | R28 `:159` (keys are removed only on an answer); Justification `:295–297` |
| A token whose `kid` matches no key after a 404 gets `TOKEN_KID_UNKNOWN` | R23 table `:144` |
| `TOKEN_REALM_UNKNOWN` dropped from R23 and ADR-0095 R16 | `:141–145`; ADR-0095 `:98–108` |
| ADR-0095 Justification says a 404 is not an outage | ADR-0095 `:119–121` |
| A14, A15 and A17 as described | `:351–366` |
| R79 loads a list of keys, any key may verify, an `alg` limits its key | `:148–150`, but see 1a for the gap |
| A16 added and A13 removed; R80 unchanged | `:360`; R80 `:151` unchanged |
| Four new costs in the Negatives | deleted realm `:389`; 401 rather than 503 `:381`, `:392`; no warning `:396–399`; key added under a held `kid` `:400` |

The change adds no command for anyone to run.

Reading the other way, the A2 rewrite in ADR-0095 `:130` and the `verify` tag on R79 are part of the claimed change.

**2a. Substantive. The PR description contradicts the change.**
- In `gh/pr-view.json`, the title is "…and add TOKEN_REALM_UNKNOWN".
- The body still describes the missing-realm result, the new code `TOKEN_REALM_UNKNOWN`, an R79 that refuses mismatched entries, and A13. It also lists user-visible changes that this commit reverses.
- **Request:** rewrite the title and body from this commit's message.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the situations the change claims, and the statement of what does not apply.*

Each claimed 404 situation has a stated outcome, and the failure row of R23 is the negative control:
- provider, or realm;
- with or without keys loaded;
- required source before keys (R14, R17), or after keys (`:396`);
- discovery document versus `jwks_uri` (A15).

The key-list partitions are one entry, several entries, an entry with an `alg`, and an entry without one. All are covered except the `alg` mismatch code (1a).

**3a. Substantive. The 1 MiB limit does not bound the per-request cost of R79 within the 5 ms budget.**
- The Justification at `:308–309` says the 1 MiB limit bounds "the length of a list".
- In 1 MiB, a source can list about 2,700 RSA-2048 entries (about 380 bytes each) or about 14,000 Ed25519 entries (about 75 bytes each) under one `kid`.
- I measured a failing verify on this machine at 29 µs for RSA-2048 and 42 µs for Ed25519. A token with a bad signature therefore costs about 80 ms or about 590 ms against that list.
- R60 doesn't cache refused tokens, so a caller that repeats such a token pays this on every request. Two tokens per request double it.
- The key response is untrusted bytes from an external server, so under `AGENTS.md` its count needs a bound at any size. The byte limit fires only long after the 5 ms budget is spent.
- **Request:** a limit on the keys loaded under one `kid`, derived from the budget. At about 42 µs per key and two tokens per request, that is about 60. State what a JWKS over that limit gets, and replace the sentence at `:308` with that derivation.

There is no earlier state to meet, because the ADR's status is Proposed.

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, and the repository's own gate.*

none. The rules stay in the record and section they belong to, and the code index in ADR-0095 R16 is updated with them. The repository's Markdown gate (`Makefile:30`, `npx markdownlint-cli2`) needs the network, so I didn't run it. The only lines over 120 characters are the existing link lines.

## Item 4: names by content, not by position
none. The references are by rule number (R23, A16), which is how the ADRs name rules, and "the two" at `:296` refers to the Keycloak and the proxy in the sentence before it.

## Item 5: the failure report
*Analogue: what each rule tells the reader to look at.*

none beyond 1a. That is the one rule whose outcome a reader can't tell from the text.

## Item 6: what the writer says it verified
Neither the commit message nor the PR description states any evidence: no case the rules pass, no case they fail, and no reviewed trial.

## Item 7: siblings of the change
I searched `ADR-0091`, `R23`, `R39`, `R79`, `KID_UNKNOWN`, `404`, `TOKEN_REALM_UNKNOWN` and `missing realm` across `docs/` and the code. No document still names the dropped code.

**7a. Substantive. The code that implements these rules follows the old design, and the change names no follow-up for it.**
- `internal/token/keys/fetch.go:255` refuses a JWKS with the error "kid %q names two different keys".
- `internal/token/verify/verify.go:280` looks up one key per `kid`.
- The saved PR body says #208 (e759672a) gives `TOKEN_REALM_UNKNOWN` for a missing realm.
- **Request:** name #208, and the single-key lookup in `keys`/`verify`, as follow-ups in the PR description.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| R79 does not give the code for an `alg` that no key of the list accepts; the Negatives cite R41, which doesn't cover it | Substantive | `ADR-0091.md:148`, `:401`, `:407` | 1 |
| A new fact is spliced into a sentence that gives a reason | Substantive | `ADR-0091.md:289` | 1 |
| "every JWKS that a source publishes loads" isn't true above 1 MiB | Taste | `ADR-0091.md:305` | 1 |
| Two Negatives state the same fact about a key added under a held `kid` | Taste | `ADR-0091.md:400`, `:405` | 1 |
| "the server of the keys" instead of "source" | Taste | `ADR-0091.md:381` | 1 |
| PR title and body describe the design this commit drops | Substantive | `gh/pr-view.json` | 2 |
| The 1 MiB limit allows thousands of keys per `kid`, about 80 to 590 ms per token against a 5 ms budget | Substantive | `ADR-0091.md:148`, `:308` | 3 |
| Code and #208 implement the old R79 and `TOKEN_REALM_UNKNOWN`, with no follow-up named | Substantive | `internal/token/keys/fetch.go:255`, `internal/token/verify/verify.go:280` | 7 |

Two checks couldn't be done: the drift script doesn't parse Markdown, and the Markdown lint gate needs network access to fetch `markdownlint-cli2`.
