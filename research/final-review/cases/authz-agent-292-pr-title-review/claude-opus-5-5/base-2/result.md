# Final review: `08d388e..b6b79c5` ("docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid")

The change has no code: it edits two ADRs, so I filled the form through the analogues in §2a. I loaded the `english-developer-style` skill. `docs-page-authoring` is not among the provided skills, and `apm-authoring` only covers skills and instruction files, so I did not load either. I ran the drift script; it printed nothing because the change has no members to parse. **There was no task statement, so the claimed cases in item 2 come from the commit message alone.** I also read the PR view saved under `gh/pr-view.json`.

No earlier report exists for this change.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement the changed files make about other rules, other ADRs, and the RFC. I checked the statements below and found them true:
- The Terms entry for Result, and the tables of R23 and ADR-0095 R16. No `TOKEN_REALM_UNKNOWN` or "missing realm" is left in the repository, and `internal/token/verify/verify.go` defines no such code.
- R28, which removes a key only on an answer, so keys survive a 404.
- The citations of R19, R20, and R81 in the Negative on required sources.
- ADR-0095 A2 ("only after an answer or a 404").
- RFC 7517 §4.5 (a shared `kid` for keys of different `kty`) and §4.4 (`alg` means the algorithm the key is intended for).

**Finding 1a (substantive): R79 gives no code for a token whose `alg` matches no entry, and the Negatives name a code R41 cannot give.**
- New R79 (`ADR-0091:148-150`) says an entry with an `alg` "verifies only a token with that `alg`". No rule says which code a token gets when every key under its `kid` carries a different `alg`.
- The new Negative at `:401-402` says such a token gets "`TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`", citing R41 and R43. The R80 Negative at `:406-407` says the same.
- R41 gives `TOKEN_ALG_NOT_ALLOWED` only for an algorithm that is not asymmetric. A token signed by a key the source added uses an asymmetric algorithm, so R41 never applies to it.
- One implementer will read the alg mismatch as "the signature does not verify" (R43). Another will read the Negatives as assigning `TOKEN_ALG_NOT_ALLOWED`. ADR-0095 R16 has no row citing R79 to settle it.
- **Request:** R79 names the code for a token whose `alg` matches no key of the list. For example: "…and a token whose `alg` no key of the list allows is refused with `TOKEN_SIGNATURE_INVALID` (R43)". ADR-0095 R16 then cites R79 in that code's row, and both Negatives name only that code.

**Finding 1b (substantive): the Justification claims every JWKS loads, which R80 contradicts.**
- `ADR-0091:305` says "every JWKS that a source publishes loads". R80 refuses a body over 1 MiB, and R39 then counts it as a failure.
- The quantifier has an exception the sentence does not name (`english-developer-style` §7, *Words that quantify need their boundary named*).
- **Request:** "so every JWKS within the limit of R80 loads".

**Finding 1c (substantive, wording): "a 404" names both the result and the HTTP status, so some sentences have to be read twice.**
- The change defines "a 404" as a result (Terms, `:69`). That is not a coinage, but it collides with the status of the same name in:
  - A15's title (`:357`): "Count only a 404 of the discovery document of R4 as a 404, and a 404 of the `jwks_uri` … as a failure". The status and the result meet in one clause.
  - R39 item 2 (`:186`): "a 404, when a request of the load got a 404".
  - A14 (`:353`): "a 404 for any source is a 404 rather than a failure".
- **Request:** where the result is meant, write "ends the load in a 404". For example, A15 becomes "Let only a 404 of the discovery document of R4 end the load in a 404, and a 404 of the `jwks_uri` … end it in a failure". A14 becomes "under which a 404 for any source ends the load in a 404 rather than a failure".

The change coins no term.

## Item 2: claimed cases covered

Analogue used: each case the commit message claims, matched to the section that handles it.

| Claimed case | Section |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms `:69`, R39 |
| A 404 for any source keeps the keys held | R28, Justification `:295-297` |
| A 404 plus an unknown `kid` gives `TOKEN_KID_UNKNOWN` | R23 table |
| R23 and ADR-0095 R16 drop `TOKEN_REALM_UNKNOWN` | Both tables; grep finds no other use |
| ADR-0095 Justification: a 404 is not an outage | ADR-0095 `:119-121` |
| A14, A15, A16, A17 present; A13 removed | `:353-369` |
| R79 loads a list and accepts any verifying key, with the `alg` restriction | R79; the code for an `alg` mismatch is missing (finding 1a) |
| R80 stays | R80, R39 |
| The four Negatives | `:388-402` |

The change adds no command.

**Finding 2a (substantive): the PR title and description still describe the design this commit removes.**
- `gh/pr-view.json` has the title "…and add TOKEN_REALM_UNKNOWN".
- Its body describes "a missing realm" as a result, `TOKEN_REALM_UNKNOWN` (401), R79 refusing mismatched pairs, and A13.
- **Request:** rewrite the title, the bullets, and the User-visible list of the PR description to match this commit.

Every other hunk is claimed, including the R79 tag gaining `verify` and the ADR-0095 A2 rewording.

## Item 3: boundaries, partitions, and the negative control

The partitions are provider or realm, required or not, and keys held or not, each meeting a 404. The text covers all of them through the uniform rule in R39, A14, and the Negatives at `:384` and `:396`.

**Finding 3a (substantive): the change removes the bound of one key per `kid`, and R80 does not bound per-token work within the 5 ms budget.**
- New R79 loads the entries under one `kid` "whatever their number". The Justification (`:308`) says R80's 1 MiB limit bounds the length of the list.
- Other limits on the same work: R80 (1 MiB per response), the request budget of 5 ms from AGENTS, and R60 (a refused token is not cached).
- Size at R80's limit: an RSA-2048 JWK is about 430 bytes, so 1 MiB holds about 2400 keys under one `kid`. EC keys are smaller, so the list holds more of them.
- Cost: a token with that `kid` and a bad signature tries every key whose `alg` admits it. At roughly 30–50 µs per RSA verification, that is about 100 ms per request, 20 times the budget.
- R60 does not cache a refused token, so each request with such a token pays this again. The work is limited only by bytes the key source controls, and AGENTS requires a bound at any size for a count an outside party controls.
- **Request:** a limit on the number of usable keys loaded under one `kid`, with a value derived from the 5 ms budget, and the source's response refused (or the excess entries dropped) beyond it. Alternatively, a sentence in R79 that states the worst-case number of verifications per token and accepts it.

Pre-existing state: the agent holds no persisted state across restarts (R12, R34). A held key that now gains siblings under its `kid` is covered by the Negative at `:399`.

## Item 3a: level, placement, and the environment

The rules stay in ADR-0091 and the code index stays in ADR-0095 R16, as before the change. I found no Makefile target for Markdown and no `markdownlint` binary installed, so I ran no gate. The only lines longer than 120 characters are the pre-existing link lines. None.

## Item 4: names by content, not by position

The cross-references use rule and alternative numbers, which are stable identifiers here. Removing A13 leaves no dangling reference. None.

## Item 5: the failure report

Analogue used: each rule's detection. R23's table, R79, and R81 each state an observable code or log line, except the `alg` mismatch filed under 1a. None beyond 1a.

## Item 6: what the writer says it verified

The commit states no evidence, such as a lint run or a check of the sibling ADRs for the dropped code. I did that grep myself and found no use left.

## Item 7: siblings of the change

- ADR-0092 R2 and ADR-0093 R3 cite R23 only for `TOKEN_KEYS_UNAVAILABLE`, so they are unaffected.
- ADR-0095 R16 has dropped its `TOKEN_REALM_UNKNOWN` row.
- `internal/token/verify` has no `TOKEN_REALM_UNKNOWN`.
- R21, R29, R32, and R61 are stated per key. With a list per `kid`, they still read consistently, because the Negative at `:399` reads "finds a key under its `kid`" as the list being non-empty.
- The PR description is filed under 2a.
- Taste: the Negative at `:399-402` and the second half of the R80 Negative (`:404-407`) now state the same fact about a key added under a held `kid`. One of the two could point to the other.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| R79 gives no code for an `alg` mismatch; the Negatives name `TOKEN_ALG_NOT_ALLOWED`, which R41 cannot give here | Substantive | `docs/decisions/…adr-0091….md:148`, `:401`, `:406` | 1 |
| "every JWKS that a source publishes loads" ignores the refusal under R80 | Substantive | `docs/decisions/…adr-0091….md:305` | 1 |
| "a 404" as both result and status forces a re-read in A15, A14, and R39 | Substantive | `docs/decisions/…adr-0091….md:357`, `:353`, `:186` | 1 |
| The PR title and body still describe `TOKEN_REALM_UNKNOWN`, the "missing realm" result, and A13 | Substantive | `gh/pr-view.json` | 2 |
| The list per `kid` is bounded only by 1 MiB, about 2400 verifications per refused token against a 5 ms budget | Substantive | `docs/decisions/…adr-0091….md:148`, `:308` | 3 |
| Two Negatives state the same fact about a key added under a held `kid` | Taste | `docs/decisions/…adr-0091….md:399`, `:404` | 7 |

I could not run a Markdown lint gate, because the repository defines none and no linter is installed.
