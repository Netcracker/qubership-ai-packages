# Final review of `08d388e..HEAD` (b6b79c5, "docs(adr): drop TOKEN_REALM_UNKNOWN and keep every key under one kid")

**Verdict: five substantive findings and one taste finding; nothing blocks on the drift script or on tests.** The two that matter most are below.

- **R79 has no limit on per-token cost.** It now loads "whatever their number" of keys under one `kid`. A forged token can make the agent try every key in the list, and a 1 MiB JWKS holds thousands of keys, so one request can cost tens to hundreds of milliseconds against the 5 ms budget.
- **The PR title and description are stale.** PR #289 still says it adds `TOKEN_REALM_UNKNOWN` and describes the old R79, R39, Result, and A13.

**Inputs.** No task statement was handed over, so the claimed cases in item 2 come from the commit message alone. The PR title and description came from the saved `gh pr view` output: state `OPEN`, base `main` at `cd2f261`, which is in the clone. No previous report exists.

The change has no code: it edits two ADR pages (ADR-0091 and ADR-0095). So §2a applies, and each item says which analogue it uses. The drift script ran and printed nothing, because there is no source code to parse. I loaded `english-developer-style`. `docs-page-authoring`, the authoring skill for a docs page, is not among the four skills provided, so I did not load it. `apm-authoring` does not apply: the change touches no skill or instruction file.

## Item 1: comments consistent with the code and with each other

Analogue: the statements each page makes about its own rules, the other ADRs, and RFC 7517. I checked them against the rule text. The RFC 7517 §4.4 and §4.5 citations are checked from memory, because there is no network.

1. **Justification states something false.** At ADR-0091:305, "so every JWKS that a source publishes loads" contradicts R80. Two sentences later, R80 still refuses a JWKS body over 1 MiB.
   - Request: "so a JWKS loads whatever number of keys it lists under one `kid`".
2. **A Negative gives R19 a condition R19 does not have.** At :397–398, it says "because R19 warns only while the agent is not ready". R19 (:128–130) says the agent retries a required source whose keys do not arrive, logs a warning for each attempt, and stays not ready. It never says the warning stops once the agent is ready. Someone implementing R19 from its own text can log a warning on every 404 reload of a required source after readiness, so the Negative's "logs no warning" would be wrong.
   - Request: either add the condition to R19 ("while the agent is not ready"), or give the reason R19 does state: "R19 warns only for a required source whose keys do not arrive, and this source holds keys".
3. **Dense wording: a fact spliced into a "because" sentence** (`english-developer-style` §4, the row *A new fact spliced into a sentence that already worked*). At :288–289, "…because a 503 after an answer would report an outage that did not happen, and R23 gives a 404 the code of an answer". This reads as a second reason why a result stored during the wait decides, which it is not.
   - Request: put it in its own sentence: "R23 gives a 404 the same code as an answer."
4. **Dense wording: the result name "a 404" collides with the HTTP status, and "answered" with the result "an answer".** One finding, three places:
   - A14, :350: "a 404 for any source is a 404 rather than a failure" reads as a tautology.
   - A17, :363: "whose source answered a load with a 404" uses the verb of the result "answer" for the other result.
   - The commit message's first User-visible line has the same phrase.
   - Request: at :350, "under which a load that gets a 404 ends in the result *a 404*, not a failure". At :363 and in the commit message, "whose last load ended in a 404".

No new term is a coinage. The term "a 404" as a result is defined in Terms at :69, and "server of the keys" is ordinary wording.

## Item 2: claimed cases covered

Analogue: the section that handles each claimed case. There are no commands to run in the change.

| Claim (commit message) | Section |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms :69; R39 :183–190 |
| A 404 for any source keeps the held keys | R28 :159; Justification :293–295 |
| 404 then no matching `kid` gives `TOKEN_KID_UNKNOWN` | R23 table :141–145 |
| R23 and ADR-0095 R16 drop `TOKEN_REALM_UNKNOWN` | ADR-0091 :144; ADR-0095 table. `git grep` finds no other occurrence. |
| ADR-0095 Justification: a 404 is not an outage | ADR-0095 :119–121 |
| A14, A15, A17 | :349–365 |
| R79 loads the list; any key may verify; an entry with `alg` verifies only that `alg` | :148–150 |
| A16 added, A13 removed, R80 unchanged | :360–362; A13 absent; :152 |
| Four new Negatives | :388–390, :394–399, :400–402, plus the reworked :382–387 |

Every claimed case has a section. Every hunk is claimed.

**The pull request (substantive).** I read the PR diff as `git diff cd2f261 HEAD`: four ADR files and no untracked files.
- **The title is false.** "…and add TOKEN_REALM_UNKNOWN": the PR diff no longer adds that code.
- **These description sentences are false:**
  - Result is "an answer, a missing realm, or a failure".
  - The R39 bullet: missing realm; a 404 for a provider or a realm with keys counts as a failure.
  - The R23 bullet: `TOKEN_REALM_UNKNOWN` (401).
  - The R79 bullet, and "A13 rejects loading the rest of such a JWKS". A13 does not exist in the PR diff.
  - "A 404 for a realm in `keycloak.requiredRealms` counts like a 404 for any other realm with no keys loaded". It is now any source, with or without keys.
  - User-visible bullets 1 and 4.
  - The Negatives sentence about a "realm with no keys" and a "required realm".
  - "#208 … gives `TOKEN_REALM_UNKNOWN` for a missing realm", presented as matching these rules.
- **Request:** a new title, such as "docs(adr): define the results of a key load in ADR-0091, and keep every key under one kid". The bullets need rewriting from the commit message's paragraphs, plus a sentence that #208 still implements the dropped code and the refusal of R79 (see item 7).

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are source kind (provider, required realm, other realm) × keys held or not × result. Each combination is assigned by R39 and R23, and the Negatives name the costs.

**Substantive: R79 removes a limit without bounding per-token cost.** R79 (:148) loads the entries under one `kid` "whatever their number", and a token is checked against every key of the list. The Justification (:308–309) cites R80's 1 MiB as the bound on "the length of a list". That bounds memory, not the work for one token. The other limit on the same work is the 5 ms per-request budget in AGENTS.md.

- **Key count:** an RS256 entry is about 380 bytes and an ES256 or Ed25519 entry about 110–130 bytes. That gives roughly 2,700 to 9,000 keys under one `kid` within 1 MiB.
- **Cost per token:** at tens of µs per signature check, a token with a forged signature costs about 0.1–0.5 s.
- **It repeats freely:**
  - It starts no load (R29, R32), so R31 and R33 never apply.
  - It is not cached (R60).
  - Any caller can aim at that list through `iss` and `kid`.
- **Who controls the count:** whoever manages a realm's keys in Keycloak. AGENTS.md requires a bound at any size for a count an outside service controls.
- **Regression:** base R79 kept one key per `kid`.
- **Request:** a stated cap on the keys under one `kid`, with what happens past it (refuse the response, or load only the first n). Alternatively, a rule that checks only keys whose `kty` and `alg` fit the token's `alg`, with a cap. Add the cost to the Negatives.

There is pre-existing state outside this repository: Pods built from #208 emit `TOKEN_REALM_UNKNOWN`. That is filed under item 7.

## Item 3a: level, placement, and the environment

Analogue: rules sit in the ADR that owns them (ADR-0091), and the reason-code index sits in ADR-0095 R16. That matches the sibling records. The repository's lint gate (`make lint`, markdownlint-cli2 with `.github/linters/.markdown-lint.yml`) could not run as configured, because that config file is not in this checkout. Run with default rules it flags only line length at 80, which the repository's own pages exceed on base too. None.

## Item 4: names by content, not by position

Analogue: headings, cross-references, and alternative ids. Rules and alternatives are cited by id, and "the two" at :293 points to the proxy and Keycloak named in the sentence just before it. None.

## Item 5: the failure report

Analogue: the detection of each rule. The decisions README's "Check a change" walks every rule of the layers a change touches, so R39, R23, and R79 are reached. Each rule states an observable outcome: a code, a load result, or which keys verify a token. None.

## Item 6: what the writer says it verified

Analogue: an exemplar and a bad case named in the change. The commit cites the architect's decision of 2026-11-25. It names no worked case run through the rewritten R39, R23, or R79, such as a deleted realm, a proxy 404, or a JWKS with two keys under one `kid`. Nothing is stated.

## Item 7: siblings of the change

Analogue: places that enumerate or cite these rules.
- **In the repository:** `git grep` finds no `TOKEN_REALM_UNKNOWN`, "missing realm", or old-R79 wording left anywhere. ADR-0092 R2, ADR-0093 R3, and the ADR-0095 rows cite R23 and remain true. Go's `verify.go` has no `TOKEN_REALM_UNKNOWN`. The README's `Defers` example is illustrative only.
- **Substantive: siblings outside the branch.** By the PR description, #208 (e759672a) implements `TOKEN_REALM_UNKNOWN` and the refusal of R79. ADR-0104 in #329 cites these rules as of d1607e02. Both now disagree with ADR-0091. **Request:** name both as follow-up in the PR description. I could not check either one, because there is no network.

**Taste.** The R80 Negative at :405–407 still carries "When the source added the key under a `kid` the agent already holds … `TOKEN_ALG_NOT_ALLOWED` or `TOKEN_SIGNATURE_INVALID`". The new bullet at :400–402 now states that for every response. The sentence could go from the R80 bullet.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| R79 loads unlimited keys per `kid`; a forged token costs about 0.1–0.5 s against a 5 ms budget | Substantive | ADR-0091 :148, :308 | 3 |
| PR title and description still claim `TOKEN_REALM_UNKNOWN`, the old R79, Result, R39, and A13 | Substantive | PR #289 | 2 |
| "every JWKS that a source publishes loads" contradicts R80 | Substantive | ADR-0091 :305 | 1 |
| Negative says R19 warns only while not ready; R19 states no such condition | Substantive | ADR-0091 :397 | 1 |
| A fact about the 404 spliced into a "because" sentence | Substantive | ADR-0091 :289 | 1 |
| "a 404 … is a 404" and "answered … with a 404" collide with the result names | Substantive | ADR-0091 :350, :363; commit message | 1 |
| #208 and ADR-0104 (#329) now disagree with these rules; not named as follow-up | Substantive | PR #289 | 7 |
| Kid-reuse sentence repeated in the R80 Negative | Taste | ADR-0091 :405 | 7 |

Checks I could not do:
- The repository markdownlint config is missing from this checkout.
- #208, #329, and RFC 7517 could not be fetched, because there is no network.
