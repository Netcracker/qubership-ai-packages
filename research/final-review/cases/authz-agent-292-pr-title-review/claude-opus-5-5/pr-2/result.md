# Final review: ADR-0091 and ADR-0095, `08d388e..HEAD` (b6b79c5)

I found nine substantive findings and two taste findings. The biggest problem is the pull request text: its title and much of its description still describe `TOKEN_REALM_UNKNOWN` and R79 refusing a response, and this commit removes both.

**Inputs.**
- **Task statement:** none was handed over. I took the claimed cases from the commit message of b6b79c5 alone, as the skill asks.
- **Pull request:** I read its title and description against `cd2f261..HEAD`, the start commit the caller named.
- **Kind of change:** two Markdown ADRs and no code, so the form uses the analogues of §2a.
- **Drift script:** `comment-drift.py 08d388e HEAD` printed nothing and exited 0, because the change has no members to parse.
- **Skills loaded:** `english-developer-style`. `apm-authoring` does not apply, because no skill or instruction file changed, so there is no table of added instructions. I was told to load no other copy, so I did not load `docs-page-authoring`.
- **Previous report:** none, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other

I used the analogue for a change with no code: every statement the changed text makes about another rule, another record, or an RFC, checked against what that text says.

1. **ADR-0091:302–306, "so every JWKS that a source publishes loads".** This is false for a JWKS whose body is over 1 MiB: R80 refuses it, and R39 item 3 makes that load a failure. A reader takes it as "no JWKS is ever refused". **Request:** "so every JWKS that R80 does not refuse loads".

2. **ADR-0091:289, "…would report an outage that did not happen, and R23 gives a 404 the code of an answer (R23, R38, R39)."** A new fact is spliced into a `because` clause that already worked (§4, "A new fact spliced into a sentence that already worked"). The reader has to work out whether the second clause is a second reason or a consequence. **Request:** end the sentence after "did not happen", then add: "The same holds for a 404, because R23 gives it the code of an answer."

3. **The word "answered" now clashes with the term "answer".**
   - The Terms define **answer** as a result, and that result is not a 404.
   - Despite that, A17 at ADR-0091:363 says "a token whose source answered a load with a 404". The first User-visible line of the commit message says "whose source answered its last load with a 404".
   - On `main`, R39 said "A 404 counts as an answer", so a reader who knows the old text will read A17 as bringing that rule back.
   - **Request:** in both places, write "whose last load ended in a 404" (A17: "whose source returned a 404 to a load").

4. **ADR-0091:397–400, the bullet on a required source.**
   - "After the source has keys, a 404 that starts later leaves the Pod ready" assumes the Pod was ready. That is false when another condition of R14 is unmet.
   - "because R19 warns only while the agent is not ready" states a limit that R19 does not state. R19 says that the agent retries a required source and logs a warning for each attempt; it gives no condition on readiness.
   - **Request:** "After the source has a usable key, a 404 that starts later does not make the Pod not ready (R20) and logs no warning, because R19 retries only a required source whose keys do not arrive, and R81 warns only for a source that is not required." If that is not what R19 means, R19 needs to state its condition.

5. **R79 (ADR-0091:148–150) gives no reason code.**
   - R79, now tagged `verify`, says that a key from an entry with an `alg` verifies only a token with that `alg`. It does not say which code a token gets when no key of the list has its `alg`.
   - Every other `verify` rule names its code. ADR-0095 R16, whose rows "state when the code applies", cites R79 in no row.
   - The Negatives (ADR-0091:401–402 and 407–408) say "`TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`", which leaves the choice open. R41 gives `TOKEN_ALG_NOT_ALLOWED` only for algorithms outside the allowed set.
   - **Request:** a sentence in R79 that gives this case `TOKEN_SIGNATURE_INVALID` (R43), and R79 added to the R43 row of ADR-0095 R16. Or else state that the choice belongs to the implementer.

6. **(Taste) ADR-0091:298, "The required sources show it at start".** The sentence is about a wrong `keycloak.url`, and only the required realms show that; providers have their own addresses. The base text said "required realms", which I prefer.

7. **(Taste) Duplicated fact in the Negatives.** ADR-0091:401–402, a key added under a `kid` the agent already holds, now says what the last sentences of the R80 bullet at 406–408 already say. I would cut those sentences from the R80 bullet.

**Terms.** The change defines "a 404" as a result in the Terms, so it has a source. The clash in finding 3 is the only coinage-type issue.

## Item 2: claimed cases covered

I used the analogue: each claim of the commit message, matched against the section that handles it. An ADR has no tests; its code is in the #208 stack.

| Claim in the commit message | Section |
| --- | --- |
| A load ends in an answer, a 404, or a failure | Terms "Result"; R39 |
| A 404 for any source keeps the keys the agent holds | R28, second sentence; Justification at :292–296 |
| A token whose `kid` matches no loaded key gets `TOKEN_KID_UNKNOWN` after a 404 | R23 table |
| R23 and ADR-0095 R16 drop `TOKEN_REALM_UNKNOWN` | R23; ADR-0095:98–101 |
| The Justification of ADR-0095 says a 404 is not an outage | ADR-0095:119–121 |
| A14, A15, A16, and A17; A13 goes; R80 stays | ADR-0091:349–366; R80 is unchanged |
| R79 loads a list, and an entry's `alg` limits what it verifies | R79 |
| The four new Negatives | ADR-0091:385–402 |

No hunk changes anything beyond these claims. The new wording of ADR-0095 A2 follows from the change to R23.

**The pull request (`cd2f261..HEAD`).** That diff contains no `TOKEN_REALM_UNKNOWN`, no missing-realm result, and no R79 refusal. These parts of the title and description are now false:

- **Title**, "…and add TOKEN_REALM_UNKNOWN". **Request:** "docs(adr): give a 404 of a key load the code of an answer in ADR-0091, and load every key under one kid".

- **First paragraph**, "answers the first question with a reason code of its own". **Request:** "answers the first question: a 404 of any source is a result of its own that gives the code of an answer, `TOKEN_KID_UNKNOWN`, as the architect decided on 2026-11-25."

- **Second paragraph**, "…report a deleted tenant as a token with an invented `kid`". It is presented as a defect this change fixes, but the change keeps it as a Negative (ADR-0091:385–387). **Request:** cut that clause, or move it to the costs.

- **"Result (an answer, a missing realm, or a failure)"**. **Request:** "(an answer, a 404, or a failure)".

- **R39 bullet.** **Request:** "R39 decides which result a load ends with: an answer for a JWKS that R80 does not refuse; a 404 when a request of the load got a 404, for any source; a failure in every other case. The agent does not read the body of a 404."

- **R23 bullet.** **Request:** "R23 maps a result to a code in one table: an answer or a 404 gives `TOKEN_KID_UNKNOWN`, and a failure or no result gives `TOKEN_KEYS_UNAVAILABLE` (503)."

- **R79 bullet and "A13 rejects…"**. **Request:** "R79 loads the usable entries of a JWKS under one `kid` as a list, and a token passes when any key of the list verifies it. An entry with an `alg` verifies only a token with that `alg`. A16 rejects refusing such a JWKS."

- **"counts like a 404 for any other realm with no keys loaded"**. **Request:** "counts like a 404 for any other source".

- **"ADR-0095 R16 lists the three codes under ADR-0091 R23"**. It now lists two. **Request:** "lists `TOKEN_KID_UNKNOWN` and `TOKEN_KEYS_UNAVAILABLE` under ADR-0091 R23".

- **User-visible, first bullet** (401 with `TOKEN_REALM_UNKNOWN`). **Request:** "A token whose source got a 404 for its last load, and whose `kid` matches no loaded key, gets 401 with `TOKEN_KID_UNKNOWN` for every source. On `main`, a 404 for a provider or for a realm with keys loaded gave 503 with `TOKEN_KEYS_UNAVAILABLE`."
  - The second half of that bullet is a user-visible change against `main`, as `main`'s R39 shows ("A 404 for a provider is no answer"), and the description does not mention it at all.

- **User-visible, fourth bullet**, "A JWKS that lists two usable entries under one `kid` … fails the load". **Request:** "A JWKS that lists several usable keys under one `kid` loads all of them, and a token passes when any of them verifies it. A response other than a 404 whose body is longer than 1 MiB fails the load."

- **Paragraph on the Negative consequences.** It names `TOKEN_REALM_UNKNOWN`-era costs and leaves out the new ones. **Request:** list the six Negatives the record now states:
  - a 404 from a proxy gives 401 rather than 503;
  - a token of a deleted realm gets the code of a token with an invented `kid`;
  - Pods that loaded a realm's keys accept its tokens after the realm is deleted;
  - a required source on a 404 gives 401, and logs no warning once it has keys;
  - a key added under a `kid` the agent already holds starts no load;
  - a refused response keeps a withdrawn key.

- **#208 paragraph**, "#208 (e759672a) gives `TOKEN_REALM_UNKNOWN` for a missing realm". The stack now contradicts R23 and R79. **Request:** a sentence saying that #208 must drop `TOKEN_REALM_UNKNOWN`, count a 404 of any source as a 404, and load a list under one `kid`, or that these rules are deferred to a named change.
  - e759672a is not in the local repository, so I could not read it.

- **Scope paragraph**, "ADR-0104 in #329 cites these rules as this change leaves them (d1607e02)". d1607e02 is not in the local repository, and R23, R39, and R79 changed after it. **Request:** check #329 against b6b79c5 and update the hash, or drop the claim.

- **"Alternative A12 is not used"**. A13 is now unused too. **Request:** "Alternatives A12 and A13 are not used."

## Item 3: boundaries, partitions, and the negative control

The partitions are:
- **Kind of source:** provider or realm.
- **Keys already loaded:** none, or some.
- **Configuration:** required or not.
- **Where the 404 comes from:** the server of the keys or a proxy.

The phrase "for every source" covers all of them, and each has a Negative or a rule. The negative control is stated: R80 still refuses, the body of a 404 is not read, and R38 keeps its exceptions.

One substantive finding:

8. **R79 (ADR-0091:148) removes the one-key-per-`kid` limit without bounding verification cost.**
   - After this change, the only bound on the list under one `kid` is R80's 1 MiB, which Justification :308 names as the bound.
   - A token with a held `kid` and a bad signature is tried against every key of the list, and R60 does not cache it, so a caller can repeat it at will.
   - Rough count: an RSA-2048 JWK is about 450 bytes, so 1 MiB holds about 2300 keys. At about 30–50 µs per verification, that is about 70–115 ms for one token. The request budget is 5 ms, and a check request carries two tokens.
   - **Request:** a cap on the usable keys under one `kid` in R79, with what happens past it, or a Negative that accepts the cost against the 5 ms budget.

**Pre-existing state.** The record is Proposed, and the state it meets is the code of the #208 stack. That is filed under item 2.

## Item 3a: level, placement, and the environment

`none`. I used the analogue: which file each rule lives in, and the repository's gate.
- R79's new `verify` tag fits its new clause on verification. The three-code index stays in ADR-0095 R16, and the alternatives keep their numbering.
- `markdownlint-cli2` is not installed, and `npx` needs a network, so I could not run the Markdown gate.
- I checked by hand against `.github/linters/.markdown-lint.yml` (MD013 at 400): no changed line comes near it.

## Item 4: names by content, not by position

`none`. The headings and cross-references of the change name rules by number (R23, A16), which is how this repository identifies them. No text says "above", "below", or uses an ordinal.

## Item 5: the failure report

`none`. I used the analogue for a rule: what a reader looks at to tell whether a text obeys it. ADR rules carry no detections of their own. Each new or changed rule names an outcome a test of the #208 stack can assert, except R79's code, which is finding 5.

## Item 6: what the writer says it verified

The commit states no evidence: no check of the rules against the #208 stack, and no worked case that the new R39 or R79 decides differently from the base text. The User-visible lines give the outcomes, but they are not runs.

## Item 7: siblings of the change

These references are consistent with the change:
- `TOKEN_REALM_UNKNOWN`, "missing realm", and A13 have no remaining occurrence anywhere in `HEAD`, the Rego in `policies/` excepted.
- ADR-0092 R2, ADR-0093 R3, and ADR-0095 (the Related ADRs entry, the R16 rows, and A2) cite R23 consistently.
- `docs/decisions/README.md:44` cites R38 only as an example.

9. **R21 (ADR-0091:122), "A key is found by source and then by `kid`", still describes one key per `kid`.** It is a sibling of R79, which now finds a list. R29 ("finds no key") and R61 ("the key that verified it") read correctly only if "find" means a match on `kid`. Only the new Negative at :400 says so. **Request:** "Keys are found by source and then by `kid`, and R79 gives the list under one `kid`." Also state in R29 that a token whose `kid` matches a list finds a key, whatever the `alg` of the entries.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "every JWKS that a source publishes loads" is false under R80 | Substantive | ADR-0091:303 | 1 |
| "and R23 gives a 404 the code of an answer" is spliced into a `because` clause | Substantive | ADR-0091:289 | 1 |
| "answered … with a 404" clashes with the defined term "answer" | Substantive | ADR-0091:363; commit message | 1 |
| "leaves the Pod ready", and a condition R19 does not state | Substantive | ADR-0091:398–399 | 1 |
| R79 `alg` mismatch has no reason code, and no ADR-0095 R16 row cites R79 | Substantive | ADR-0091:148–150 | 1 |
| "required sources show it" for a wrong `keycloak.url` | Taste | ADR-0091:298 | 1 |
| Same fact on a key added under a held `kid` in two Negatives | Taste | ADR-0091:401, 406–408 | 1 |
| PR title and description still describe `TOKEN_REALM_UNKNOWN`, the R79 refusal, A13, three codes, stale costs, #208, d1607e02, and A12 only; they omit the provider and keyed-realm change from 503 to 401 | Substantive | PR title and description | 2 |
| No bound tighter than 1 MiB on keys per `kid`, so about 2300 verifications per bad token | Substantive | ADR-0091:148, 308 | 3 |
| R21 and R29 still describe one key per `kid` | Substantive | ADR-0091:122, 162 | 7 |

The Markdown gate could not run, because `markdownlint-cli2` is not installed and there is no network, and commits e759672a and d1607e02 are not in the local repository.
