# Final review: `08d388e..HEAD` (b6b79c5, docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid)

**Inputs.**
- There is no separate task statement, so the claimed cases come from the commit message alone. The PR body in `gh/pr-view.json` describes the previous design and is addressed under item 2.
- Skills loaded: `final-review`. I did not load `english-developer-style` or `apm-authoring` in full; the wording checks below are from my own reading and cite no section numbers.
- This is a change with no code, two ADR pages, so I used the §2a analogues under every item.
- The drift script was not run: it gave no output on `.md` files and there are no members to parse.
- This is not a skill or an instruction file, so there is no table of added instructions. `Added instructions: n/a`.

## Item 1: comments consistent with the code and with each other
Analogue: every statement the pages make about one another or about their own rules (rule numbers, counts, cited RFC sections).

I checked each cross-reference against the page it points to, and the page-level claims against the text:
- R23's table, R38, and R39 agree with the Terms entries *Result* and *Last result*.
- R28 and the new Justification paragraph agree that a 404 keeps the held keys.
- ADR-0095's R16 row and the new Justification sentence match ADR-0091 R23.
- A14 to A17 cite R23, R39, and R79 correctly.
- Nothing in the repository still names `TOKEN_REALM_UNKNOWN` or "missing realm".
- RFC 7517 §4.5 (different `kty` under one `kid`) and §4.4 (`alg`) are read as the RFC states them.

One finding, taste:
- **F1 (taste).** `…0091…md:181` (R28) and the R20 and R36 wording say a reload "fails" keeps the keys. After this change R39 makes a 404 a result that is not a failure. R28's second sentence ("A key is removed only when a load ends in an answer without it") settles the case, so a reader cannot go wrong. I would still write "a reload that ends in a 404 or a failure keeps the keys".

There are no narrating words ("now", "no longer") in the added text. I found no coinages: *Result*, *Last result*, *Required source*, and *Source* are defined in Terms. The "server of the keys" in the Negatives uses ordinary words.

## Item 2: claimed cases covered
Analogue: each claimed case against the section that handles it.

| Claimed case | Section |
| --- | --- |
| A 404 for any source, provider or realm, keeps held keys, and a token with an unmatched `kid` gets `TOKEN_KID_UNKNOWN` | R23, R39, Justification para. 2 |
| R23 and the ADR-0095 R16 table drop `TOKEN_REALM_UNKNOWN` | R23, ADR-0095 R16 |
| ADR-0095's Justification says a 404 is not an outage | ADR-0095 Justification |
| A14, A15, A17 | A14, A15, A17 |
| R79 loads all usable entries as a list, a token passes when any key verifies it, and an entry with an `alg` verifies only that `alg` | R79, Justification para. 4, A16 |
| A13 removed, R80 stays | A13 absent, R80 unchanged |
| Negative: the code of a deleted realm equals the code of an invented `kid` | Consequences bullet 3 |
| Negative: a 404 for a provider or a realm with keys gives 401, not 503 | Consequences bullet 2 |
| Negative: no warning when a required source's 404 starts after it has keys | Consequences bullet 4 |
| Negative: a key added under a held `kid` starts no load | Consequences bullet 5 |

There are no commands to run. The change claims nothing beyond what the commit message lists.

One finding, substantive:
- **F2 (substantive).** The PR title and body (`gh/pr-view.json`) still describe the previous design, which this commit reverses. They name `TOKEN_REALM_UNKNOWN` and the "missing realm" result. They say R79 refuses entries that differ in key material or `alg`, and that A13 is kept. They also list user-visible changes that no longer hold. A reader of the PR sees claims the diff contradicts. Rewrite the title and body to match the commit message.

## Item 3: boundaries, partitions, negative control
Analogue: the partitions are provider / realm with keys / realm without keys / required / not required, and key lists with and without `alg`. For a page, the negative control is the statement of what does not apply.

- The Negatives and A14 cover each source partition.
- The negative control is stated: a 404 on a body over 1 MiB is exempt in R80, and an entry without `alg` is accepted in R79.
- The change reads no earlier persisted state, so there is no state-from-earlier-version question.
- The change replaces no mechanism and moves no limit.

One finding, taste:
- **F3 (taste).** The Justification says the 1 MiB limit of R80 bounds "the length of a list" under one `kid`, and R79 says "whatever their number". Each token that fails verification is not cached (R60), so it tries every key of the list. A source that publishes thousands of small keys under one `kid` could therefore exceed the 5 ms request budget in `AGENTS.md`. The bound exists but is stated nowhere in the rules. I prefer a stated cap on the keys tried per token, sized to the budget. This is a taste finding because the source of keys is operator-configured.

## Item 3a: level, placement, environment
Analogue: file placement and the repository's own gate.
- Both files sit beside their sibling ADRs, and the Rule/Negative layout matches.
- `markdownlint-cli2` is not installed, so I could not run the gate. I checked line length by hand: no added line is over 121 characters.

## Item 4: names by content, not by position
None. The cross-references use rule numbers (R23, R39), which are stable identifiers rather than positions. The alternative numbers A14 to A17 skip A12 and A13. That keeps numbers stable and matches the PR's note that A12 is unused.

## Item 5: the failure report
Analogue: a rule's failure report and its detection. None. R23's table gives each result its code, and R79 and R39 state outcomes a reader can check. The ambiguity in F4 below belongs to item 1's wording, not to a detection gap.

## Item 6: what the writer says it verified
The commit message states no verification. I found no evidence that either page was checked against code, and no gate output. This is docs-only; I did not run anything to supply the evidence.

## Item 7: siblings
Analogue: the places that enumerate or route to these rules.
- ADR-0092 (line 65), ADR-0093 (line 66), ADR-0095 R2, ADR-0095 Related ADRs, and `docs/decisions/README.md` cite R23, R38, or `TOKEN_KEYS_UNAVAILABLE`. None names `TOKEN_REALM_UNKNOWN`, the three-code table, or R79, so none is stale.
- No sentence still counts the result kinds or the reason codes as before.
- I found no other page that mentions same-`kid` handling.

One more finding, taste:
- **F4 (taste).** The R80 Negative (…0091…md:~405) and the new bullet before it say a token against a held `kid` gets `TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`. R79 says an entry with an `alg` "verifies only a token with that `alg`". It does not say which code a token whose `alg` differs from every held entry gets. R41 covers only algorithms outside RS, PS, ES, and EdDSA. R77 leaves the order of checks to the implementer, so the text is defensible. I prefer a sentence in R79 naming the code for an `alg` mismatch.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| R28, R20, and R36 say "fails" where R39 now has a 404 that is not a failure | Taste | `docs/decisions/…0091….md:181` | 1 |
| PR title and body still describe `TOKEN_REALM_UNKNOWN` and the old R79 | Substantive | `gh/pr-view.json` (title, body) | 2 |
| List length under one `kid` has no per-token cap sized to the 5 ms budget | Taste | `docs/decisions/…0091….md:148` | 3 |
| R79 does not say which code an `alg` mismatch gets | Taste | `docs/decisions/…0091….md:148` | 7 |

Checks not done: I could not run markdownlint, and I did not read the Go code under `internal/` against the new rules (out of scope for a docs-only change).
