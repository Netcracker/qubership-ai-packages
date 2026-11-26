# Final review of `08d388e..HEAD` (b6b79c5)

**Inputs.**
- The change touches two ADR pages and no code. I filled the form through the §2a analogues.
- The drift script was run and printed nothing, because it does not parse Markdown. It does not apply here.
- I loaded `english-developer-style`. `apm-authoring` is for skills and instruction files, so it does not apply. `docs-page-authoring` is not among the four skills I was given.
- There is no task statement. The claimed cases come from the commit message alone.
- The open PR text is in `gh/pr-view.json`. Its `baseRefOid` is `cd2f261`, which I used as the target.
- There is no previous report.
- `make mutation-diff` does not apply: no Go code changed.

## Item 1: comments consistent with the code and with each other

Analogue used: statements one page makes about its own rules, about the other ADRs, and about the RFC.

**Finding 1 (substantive).** ADR-0091 R79 (`:148-150`) says an entry with an `alg` verifies only a token with that `alg`.
- R79 does not say which code a token gets when it matches no entry. That covers a PS256 token whose only entry under its `kid` says RS256.
- R41 (`:199`) gives `TOKEN_ALG_NOT_ALLOWED` only for non-asymmetric algorithms, and R43 gives `TOKEN_SIGNATURE_INVALID` for a signature that does not verify.
- The new Negative bullet (`:400-402`) and the kept bullet (`:405-408`) both say the token gets `TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`, with no rule that picks between them.
- ADR-0095's table maps `TOKEN_ALG_NOT_ALLOWED` to R41 only.
- Request: add to R79 the code a token gets when no key under its `kid` accepts its `alg`, and make the two Negative bullets and the ADR-0095 row agree with it.

**Finding 2 (taste).**
- The new bullet (`:400-402`) and the rewritten last bullet (`:403-411`) both describe a key added under a held `kid`. Merge them. Expect this to be declined.
- "the server of the keys" (`:381`) is a new phrase beside the glossary's "Keycloak" and "source". "A 404 that something other than Keycloak or a provider sends" would use the glossary's words. Expect this to be declined.

**Other checks, none.**
- Every sentence about R23, R28, R38, R39, R81 and R61 was re-read against the new R39. They still hold.
- R20, R28, R61 and the new R39 agree about a 404 keeping the keys.
- No narration (`now`, `no longer`, `used to`) was added to the pages.
- No dense sentence was found that needs two parses.
- No coined term was found, apart from the taste item above.
- ADR-0095's new Justification sentence and its reworded A2 match R23.

## Item 2: claimed cases covered

The claims come from the commit message. The task statement was not handed over, so this item rests on the commit message alone.

| Claim | Section that makes it true |
| --- | --- |
| R23 drops `TOKEN_REALM_UNKNOWN`. | R23 table (`:141-146`) |
| ADR-0095 R16 drops the code. | `0095:98-101` |
| A 404 for any source keeps its keys and gives `TOKEN_KID_UNKNOWN`. | R39, R28 |
| ADR-0095 Justification says a 404 is not an outage. | `0095:119-121` |
| A14, A15 and A17 are rejected. | `0091:349-365` |
| R79 loads all usable entries under a `kid` as a list. | R79 |
| A16 rejects refusing such a JWKS, and A13 goes. | A16 added, A13 removed |
| R80 stays. | R80 unchanged |
| Negative: a deleted realm gets the code of an invented `kid`. | `:388-390` |
| Negative: a 404 for a provider or a realm with keys gives 401 rather than 503. | `:381-387` |
| Negative: no warning after a required source has keys. | `:394-399` |
| Negative: a key added under a held `kid` starts no load. | `:400-402` |

All are covered. The ADR-0092, ADR-0093 and ADR-0095 A2 citations of R23 still point to a code that exists. The page claims "an alg-mismatched token is refused" without a code, which is Finding 1.

No commands are told to run.

Hunks the commit does not claim:
- The ADR-0095 A2 rewording is needed for consistency, so I did not file it.
- The Negative wording "required sources" for "required realms" follows from the claimed 404 rule.

**Finding 3 (substantive): the pull request title and description describe a different design from this diff.**
- PR diff means `git diff cd2f261..HEAD`, which I read from the `HEAD` of the repository.
- The title says "and add `TOKEN_REALM_UNKNOWN`". The diff adds no such code, and ADR-0095 does not list it.
- The description defines **Result** as "an answer, a missing realm, or a failure". The page now says "a 404".
- The description says R39 gives a "missing realm" only for a realm with no keys loaded. It says a 404 for a provider or for a realm with keys loaded is a failure.
- R39 now counts every 404 as a 404.
- The description says R79 loads entries as one key only when they share key material and `alg`, and that a differing pair fails the load. R79 now loads them all as a list.
- The same description line says A13 rejects loading the rest of such a JWKS. A13 is gone and A16 rejects refusing it.
- The description says a 404 for a required realm "counts like a 404 for any other realm with no keys loaded". Under R39 it does, but the description then says A14 rejects counting that 404 as a failure. A14's wording changed.
- Every item under the description's user-visible changes that names `TOKEN_REALM_UNKNOWN` or a refused JWKS is false.
- The user-visible bullets and the Negative-cost sentence on proxies are stale in the same way.
- Request: a new title (for example "define which responses ADR-0091 R39 counts as a 404 and load several keys under one `kid`") and a rewritten description to match the diff. It should say that a 404 keeps the keys and gives `TOKEN_KID_UNKNOWN`, that R79 loads a list, and that A16 and A17 are added.

The rest of the description (R38 for a canceled wait, R81, R80, the ADR-0104 scope note, `Closes #289`) still matches.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the partitions the change claims and the statement of what does not apply.

- **404 partitions:**
  - 404 for a realm with no keys, 404 for a realm with keys, and 404 for a provider are collapsed into one rule. Each has its Negative or Justification sentence.
  - A 404 on discovery versus on `jwks_uri` is A15.
  - A 404 after keys exist keeps the keys, and the Negative covers the lack of a warning.
- **R79 partitions:**
  - Several keys under one `kid` is covered.
  - A single key per `kid` keeps R28 and R61 unchanged.
  - An `alg` entry versus an entry with no `alg`: R79 gives no code, which is Finding 1.
  - A list with different `kty` is covered by the RFC sentence. Several usable entries of the same `kty` and key material are covered too.
- **Limit:** R80's 1 MiB bound ties to list length in the Justification. Good.
- **State from an earlier version:** none. These are design records.
- No mode or setting is added, so no control arm is owed.

None.

## Item 3a: level, placement, and the environment

Analogue used: file placement and registration entries.

- The edits stay in the two ADRs that already own the rules.
- The `Index` entry in ADR-0095 (`:22-24`) still names R23 and R38, which still exist.
- The repository's own gate for ADR pages was not found in `Makefile` (`git grep` for `adr` and `decisions` there found nothing), so none was run.

None.

## Item 4: names by content, not by position

New headings and cross-references use rule numbers and content words. "A16" and "A17" are labels in the page's established scheme. The gap after A13 is the page's own convention (the PR notes A12 as unused).

None.

## Item 5: the failure report

Analogue used: a rule's detection. ADR rules have none in these pages. R79 says what passes but not what the reader should expect on failure, which is Finding 1. R39's three outcomes are each stated with a condition.

None beyond Finding 1.

## Item 6: what the writer says it verified

Neither the commit message nor anything in the change names a check that the rules can fail: no exemplar that passes and no bad case that fails. The commit message says the architect decided it on 2026-11-25. That is a decision, not a verification. Say so.

## Item 7: siblings of the change

- I searched `docs/` for `TOKEN_REALM_UNKNOWN`, `missing realm`, `A13`, `R79`, and `ADR-0091 R23/R39`.
  - No leftover mention of the dropped code or of "missing realm" remains outside the PR description (Finding 3).
  - ADR-0092 R2 (`:65`), ADR-0093 R3 (`:66`), and ADR-0095 `:23`, `:100`, `:108`, `:130` are the only citations. All still match.
- A set count check: ADR-0091 still says "three codes" nowhere in the page. ADR-0095's table now has two 401 codes for a key (`TOKEN_KID_MISSING`, `TOKEN_KID_UNKNOWN`) and one 503 code, and the text does not count them.
- Repository references outside `docs/` (code, tests) were not searched for R79 or `TOKEN_REALM_UNKNOWN`. A `git grep -n REALM_UNKNOWN` over Go sources found nothing in the earlier search.

None.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| R79 and the two Negatives give no single code for a token whose `alg` no key under its `kid` accepts | Substantive | `docs/decisions/20261029-authz-agent-adr-0091-verify-tokens-before-policy-evaluation.md:148-150`, `:400-408` | 1 |
| Two Negative bullets describe a key added under a held `kid`; "the server of the keys" is a new phrase | Taste | same file, `:381`, `:400-411` | 1 |
| PR title and description describe `TOKEN_REALM_UNKNOWN`, a "missing realm" result, and the old R79 and A13 | Substantive | PR title and body | 2 |
| No check that the rules can fail is named | Substantive | commit message | 6 |

Checks I could not do: the offline gate for ADR pages was not found, and the repository's code and tests were not searched for uses of the dropped code beyond the one `git grep`.
