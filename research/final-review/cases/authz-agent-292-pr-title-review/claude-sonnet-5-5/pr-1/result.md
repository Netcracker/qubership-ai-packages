# Final review of `08d388e..HEAD`: `b6b79c5` (docs-only change)

I read the task statement from the commit message alone, because I could not ask for one. The pull request text is judged against `cd2f261..HEAD`, as the caller handed it over.

I loaded `english-developer-style` and `test-authoring` from the skills directory. I did not load `apm-authoring`, because the change has no skill or instruction file. This is the no-code form of §2a, and each item below uses the analogue the skill names. I ran the drift script, and it printed nothing for these Markdown files, so it gave me nothing to work from. I did not run the repository's gates, since §2a asks for one only on registration entries and this change adds none. There is no previous report.

I checked the following against the files:
- **Edited records:** the diffs of ADR-0091 and ADR-0095.
- **Other records:** a grep of the repository for every citation of R23, R38, R39, R79 and R80, and for `REALM_UNKNOWN` and "missing realm".
- **The PR diff:** the diff from `cd2f261` to `HEAD`, which also includes the ADR-0092 and ADR-0093 edits.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement one changed file makes about another file, a rule, or a cited standard.

- **PR text is stale.** See finding 1 under Item 2.
- **R23, R39 and R38 agree with each other.** The code of a 404, an answer and a failure is stated once, in the R23 table, and the Terms entry for Result matches R39. The ADR-0092 R2 and ADR-0093 R3 citations and the ADR-0095 R16 table and A2 agree with R23.
- **R79 leaves a code unstated.** Finding 2. R79 (lines 147–150) says an entry with an `alg` verifies only a token with that `alg`. It does not say what a token gets when no key of the list verifies it.
  - R43 gives `TOKEN_SIGNATURE_INVALID` for a signature that does not verify.
  - R41 gives `TOKEN_ALG_NOT_ALLOWED` only for algorithms outside the accepted set.
  - The Consequences bullets (lines ~400–406) say a token gets "`TOKEN_SIGNATURE_INVALID` or `TOKEN_ALG_NOT_ALLOWED`" under a held key. No rule says when each applies. That was already true on `main`, but R79 now creates the case. Request: one sentence in R79 or R41 saying which code a token gets when no key in its list verifies, for example when the only entry has a different `alg` and when entries of the right `alg` fail verification.
- **A claim about R19 that R19 does not state.** Finding 3, in the Consequences bullet at lines ~396–399. It says "R19 warns only while the agent is not ready". R19 says only that the agent retries a required source, logs a warning for each attempt, and stays not ready. Request: state in R19 that the warning stops once the agent is ready, or drop the claim.
- **Unbounded key list.** Finding 4. R79 loads "a list of keys, whatever their number", and the Justification (line ~309) says R80 bounds the length of the list. The 1 MiB limit bounds the response, but each token under that `kid` now costs up to one verification per entry. An entry with no `alg` is tried against any token, and a JWKS of a few hundred bytes per entry can hold thousands. That can exceed the 5 ms request budget. Anything that sets the list length, such as Keycloak or a provider, is outside the caller, so it needs a bound at any size. Request: a cap on the number of entries under one `kid`, with the failure R39 gives when the cap is hit, or a stated worst-case cost.
- **Scope claim from RFC 7517 §4.5 (taste).** The Justification (line 304) and A16 cite §4.5 as allowing keys of different `kty` under one `kid`. R79 accepts any entries, including the same `kty` with different material or `alg`, which §4.5 does not endorse. The sentence names the narrower case, so this is not false. Wording that says the rule goes beyond the RFC would be clearer.
- **New phrase without a source (taste).** "the server of the keys" (Consequences, line ~378) appears nowhere else. The Terms use "source". Taste only.
- **Spliced clause (taste).** The Justification sentence ending "and R23 gives a 404 the code of an answer (R23, R38, R39)" adds a new fact to a sentence about the 503 after an answer. It would read better as its own sentence.
- **No coined terms.** "Result", "Last result" and "404" are defined once in the Terms before use. There is no narration of the change in the ADR text such as "now" or "no longer".

## Item 2: claimed cases covered
Analogue used: each claimed case against the section that handles it.

The cases the commit message claims:
- A load ends in an answer, a 404 or a failure: R39 and the Terms.
- A 404 for any source keeps the keys the agent holds: R28 ("removed only when a load ends in an answer").
- A token whose `kid` matches no key after a 404 gets `TOKEN_KID_UNKNOWN`: R23 and R38.
- R23 and the ADR-0095 R16 table drop `TOKEN_REALM_UNKNOWN`: a grep finds none left.
- The ADR-0095 Justification says a 404 is not an outage: present.
- A14, A15 and A17 are present, and A13 is removed.
- R79 loads a list and an `alg` verifies only its token: stated, with the gap in finding 2.
- R80 is unchanged: yes.
- The four new Negatives: each has a bullet.

No command is told to run. Each rule's detection is its own text, with no test, and none is owed.

**Finding 1, substantive: the PR title and description describe a diff that is not there.** They are checked against `cd2f261..HEAD`. The title says "add TOKEN_REALM_UNKNOWN", and the description says the change:
- adds a Result "missing realm" and the code `TOKEN_REALM_UNKNOWN` (401);
- gives R39 an item "a missing realm";
- has R79 refuse the response for an `alg` mismatch and A13 reject loading the rest;
- has A14 reject counting a 404 as a failure "like on main", named as a realm only;
- has R14, R17 and R19 stay as before for a 404.

In `HEAD`:
- no code `TOKEN_REALM_UNKNOWN` exists;
- R39 gives a 404, not a missing realm;
- R79 loads all entries as a list and refuses nothing;
- A13 is removed;
- A14 covers any required source;
- A16 and A17 are new.

The user-visible bullets are also wrong: the first would give `TOKEN_REALM_UNKNOWN`, and the fourth says a JWKS with two usable entries under one `kid` fails the load. The Negatives paragraph (a deleted realm's tokens get a distinct code) is the opposite of the final text. Request: a new title and description that match the final diff. Suggested title: `docs(adr): give a 404 of a key load the code of an answer in ADR-0091 R39, and load several keys under one kid`. The description should drop the missing-realm claims and describe R39, R23, R38, R79, R80, R81 and A14–A17 as they stand. The statements that the R33 refusal path has no result and that the hourly reload does not count remain true. Its mention of #208 giving `TOKEN_REALM_UNKNOWN` would need rewriting too.

**Finding 5, substantive: a claim about the keys code of #208.** The description says #208 "gives `TOKEN_REALM_UNKNOWN` for a missing realm". The final ADR no longer defines that code, so the sentence points the implementer at code the ADR now contradicts. I cannot see #208 offline. Request: replace it with what #208 must change, or remove it with the rest of the stale text.

Read the other way, every hunk is claimed by the commit message or the description: the ADR-0092 R2 and ADR-0093 R3 citation edits, the ADR-0095 reference-list entry, R16, the Justification and A2. The ADR-0091 hunks that remove `TOKEN_REALM_UNKNOWN` are claimed by the commit but are absent from the description's final state, which is finding 1.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the partitions the change claims, and what it says does not apply. For configuration-like text the questions of item 3 also apply.

- **Partitions covered by prose.** Provider and realm, with and without keys held, required and not required, discovery 404 and `jwks_uri` 404 (A15), wait ended, request canceled and deadline (R38), R33 refused (R38). The Negatives bullets cover the costs of each.
- **Negative control.** R39 lists a 5xx, a timeout and an over-limit body as failures, and R80 exempts a 404 from the body limit. A14 and A17 state the alternatives that do not apply.
- **Earlier state.** The change is a docs record with no persisted state. R12 says the trusted providers file is read at start, and nothing in the change reads an old file.
- **Limits.** R80 is the only limit. See finding 4 for the one downstream cost of it.
- Added instructions: not applicable, since there is no skill or instruction file.

## Item 3a: level, placement, and the environment
Analogue used: which file each rule lives in, and whether registration entries match the sibling layout.

- The rules live in the files that own them: R23, R38, R39, R79 and R80 in ADR-0091, citations in ADR-0092, ADR-0093 and ADR-0095.
- The layout matches the siblings, and the change adds no registration entry.
- The Alternatives numbering jumps from A11 to A14 in the final PR diff, so A12 and A13 are absent. The description says "A12 is not used", but the gap now looks like a missing record. Taste: renumber the new alternatives, or keep the numbers and say once that they are intentional. I deleted nothing here.

## Item 4: names by content, not by position
None. Rules and alternatives are cited by `R`/`A` identifier, which is the repository's own scheme, and no heading or case name refers to a position such as "see below".

## Item 5: the failure report
Analogue used: every rule's detection, and whether each detects the rule rather than a weaker property.

R23 and R39 are observable by the reason code on the refused request, and R38 by the code a canceled or timed-out token gets. R79 lacks a code for a key that verifies nothing (finding 2). R81's warning names the source, the result, the address and the status, which is what an operator needs.

## Item 6: what the writer says it verified
The commit message and the description state no check that a rule can fail, no red case and no mutation verdict. For a docs change this means a stated bad case per rule is missing. I did not run anything to supply it.

## Item 7: siblings of the change
- **Citations of the moved rule.** A grep of the repository for `ADR-0091 R23`, `R38`, `R39`, `R79` and `R80` shows each citation outside ADR-0091 now consistent with the rules.
- **Set of codes.** `TOKEN_REALM_UNKNOWN` appears nowhere after the change, and "missing realm" appears only in A17, where it names the rejected code.
- **README.** `docs/decisions/README.md:44` names R38 as a deferred rule in an example. It is an example of the format and needs no change.
- **Terms and counts.** No sentence still counts three outcomes by the old names. A grep for "two usable" and "R79 or R80" finds only the new text.
- **`policies/identity.rego:119`.** I did not review it (maintenance only).

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| 1. PR title and description describe `TOKEN_REALM_UNKNOWN`, a missing-realm result, an R79 refusal and A13, none of which the final diff has | Substantive | PR text (against `cd2f261..HEAD`) | 2 |
| 2. R79 does not say which code a token gets when no key of its list verifies it | Substantive | `…0091-verify-tokens-before-policy-evaluation.md:147–150`, `~400–406` | 1 |
| 3. The Consequences bullet says R19 warns only while the agent is not ready, which R19 does not state | Substantive | same file, `~396–399` | 1 |
| 4. R79 imposes no cap on the entries under one `kid`, and a token's cost grows with their number against the 5 ms budget | Substantive | same file, `147–150`, `~309` | 1 |
| 5. The description's sentence about #208 giving `TOKEN_REALM_UNKNOWN` contradicts the final ADR | Substantive | PR text | 2 |
| RFC 7517 §4.5 is cited for a narrower case than R79 accepts | Taste | same file, `304`, A16 | 1 |
| "the server of the keys" is a phrase with no source | Taste | same file, `~378` | 1 |
| Spliced clause about R23 giving a 404 the code of an answer | Taste | same file, `~288` | 1 |
| Alternatives numbering skips A12 and A13 | Taste | same file, `~349` | 3a |

Not checked: #208, #329 and the tracker, which are outside the repository and offline.
