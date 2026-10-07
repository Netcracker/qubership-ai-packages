# tax-engine port: last parity round (round 10) and remaining blind spots

Scope: what our current evidence cannot see, the work we can do for free before the round, and the round of at most
50 requests to the legacy stand, with a drop order in case the budget is cut. The goal is **parity** (reproduce the legacy service, quirks included). Where we decide to fix a quirk instead of copying it,
record it as a deliberate difference in `decisions.md`.

## 1. Why green does not mean safe

Every measure we report is built from the port itself. So each one can only catch errors in rules the port already
has. None of them can catch a rule the port is missing.

| Measure | Where it gets its cases | What it cannot see |
| --- | --- | --- |
| Parity suite, 1,812 pairs | Rounds 1 to 9, read through `comparator.yaml` | Anything the comparator erases (below), and any input shape no earlier round sent |
| Mutation score 94% | Changes go-mutesting makes to the port's code | A legacy rule that differs in shape from every mutant, e.g. a rounding mode keyed on something other than category |
| `rapid` properties | Our generators, our invariants | "Total equals the sum of line taxes" and "tax is never negative" are **our beliefs**, and no golden is known to pin them. If the legacy service rounds the total from unrounded line taxes, or returns negative tax on refund lines, these properties pass and production differs |
| Pairwise, 100% | `jurisdiction × category × exemption kind × priority class`, all port concepts | Rule upload order, equal priorities, groups, line position, duplicate SKUs or rule names, the spelling of values, and request sequences |

### What the comparator erases

| Normalization | What we can no longer see |
| --- | --- |
| `arrays: sort` | Order of lines in the response. If response lines don't carry their `sku`, we also can't see a tax moved to the wrong line. The same goes for the order of rules or errors in any list |
| `nulls: drop` | `null` versus a missing field, in both directions |
| `numbers: decimal-value` | `1.5` versus `1.50` versus `1.5E+1`, and possibly `"1.50"` (string) versus `1.50` (number). Jackson writes `BigDecimal` with its scale, and may use scientific notation. Clients that parse text or compare strings would break |
| `ignore $.error.message` | Our best side channel. The legacy error message usually says which rule or field failed, and we throw it away |

### The ten decisions, rated by evidence

| Id | Evidence | Rating | Main alternative we haven't ruled out |
| --- | --- | --- | --- |
| D3 | Design doc only | **Guess** | Upload order or group order wins over `priority`. Priorities may be per group, not global. Whether matching rules stack, compound, or the first one wins |
| D7 | 3 goldens | **Exception list** | A list of categories that round differently is usually the trace of a single underlying cause. Candidates: half-even everywhere, with other-category goldens never hitting a tie that tells the two modes apart; or `double` arithmetic (`new BigDecimal(double)`) that looks like half-even on some amounts; or a mode set by jurisdiction or rate, not category |
| D9 | 1 golden | **Weak** | Every outcome looks alike: "did not apply", "evaluated to false", and "error swallowed". These need a negated rule and a fallback to tell apart. It's also open whether a known but absent optional field (`exemptionCode`) counts as "unknown" |
| D12 | Design doc only | **Guess** | JVM `trim()` strips characters ≤ U+0020 (tab included) but not NBSP. Go `strings.TrimSpace` strips NBSP too. A PostgreSQL lookup would be case-sensitive by default |
| D14 | 1 golden | **Weak** | The cap may apply per line, per unit, per order, or per SKU. One single-line golden can't tell these apart |
| D15 | Design doc only | **Guess** | An empty group may be rejected at upload, or may block lower groups |
| D18 | 2 goldens | Medium | Case, inner spaces, leading whitespace, whether the pattern is a regex (`String.matches` anchors, `find` doesn't), and ZIP codes sent as numbers |
| D21 | 3 goldens | **Exception list** | CA-QC, DE-BY and US-TX have nothing obvious in common. The dropping is probably driven by their **configuration**, or by "line tax is zero", not by the jurisdiction name |
| D22 | Design doc only | **Guess** | Lowercase category accepted or rejected. Also undecided: what a **quote** with an unknown category does |
| D25 | 1 golden | Medium | Other spellings: `" 12.50"`, `"1.25E1"`, very long numbers. For `quantity`, Jackson's default `ACCEPT_FLOAT_AS_INT` truncates `2.5` to `2`, and Go rejects it |

**Not in the list at all.** These are the most likely sources of a surprise after cutover:

- Rounding stage: per unit, per line, per rule, or on the total.
- How multiple matching rules combine.
- Line order in the response.
- Number formatting in the response.
- Duplicate SKUs in one order.
- Duplicate rule names in one upload.
- Re-upload: replace or merge, cache staleness, and whether a rejected upload leaves the old rules intact.
- Negative prices and quantities.
- Empty `lines`.
- How a jurisdiction is resolved from `shipTo` (case, missing region, unknown region).
- Precedence when a request has two errors.

## 2. Free work before the round (no stand requests)

Finish this before filing the ticket. Several items may shrink or change the round.

1. **Shadow traffic, starting now.** `POST /v1/tax/quote` is a pure computation, so mirror production or staging
   quotes to the Go port for the remaining three weeks and diff the **raw** responses, not only the normalized ones.
   Before turning it on, confirm the port writes no quote logs or audit rows to any shared database. Rule uploads
   (`PUT /v1/rules`) are mirrored only into the port's own store. This is the strongest evidence we can get, and it
   uses none of the 50 requests. Suggested cutover gate: `n` consecutive agreeing raw comparisons. For example,
   1,000 bounds the disagreement rate on the production mix at about 0.3% (95%), and says nothing about inputs
   outside that mix.
2. **Re-compare the 1,812 recorded pairs raw**, if the raw bodies were kept. Check line order, number text (scale
   and exponent), `null` versus missing fields, and error messages. Every difference is a free answer.
3. **Audit the comparator empirically.** Feed it pairs that differ in one aspect only: `1.5`/`1.50`, `1.50`/`"1.50"`,
   `null`/missing, reordered lines with and without `sku`. Record which pairs it merges.
4. **Audit which goldens actually pin which decisions:**
   - D7: does any golden for a category *outside* the list hit a tie with an even preceding digit? If none does,
     half-up for those categories is unpinned. Are r4-17, r6-02 and r8-33 from one jurisdiction, or at one rate?
   - D21: diff the CA-QC, DE-BY and US-TX configs (from earlier rounds' uploads) against the others. Look for a
     shared feature: a cap, a rule on `quantity`, number of groups, zero-rate rules.
   - Totals: is there any golden with two or more lines whose unrounded taxes would give a different total than the
     sum of the rounded line taxes?
   - Rule combination: what do the goldens show about two matching rules? This decides how Q4, Q5 and Q7 are
     encoded (see the notes on the round).
5. **Run the port on every input in §3 and write its prediction in the ticket before sending.** Any input the port
   can't predict, or predicts only by accident, is a gap in the model. Flag it.
6. **Ask the owning department.** Their answers are hypotheses until the round confirms them. Questions:
   - Jackson settings: `ACCEPT_FLOAT_AS_INT`, `FAIL_ON_UNKNOWN_PROPERTIES`, `WRITE_BIGDECIMAL_AS_PLAIN`.
   - `RoundingMode` and where rounding happens.
   - `BigDecimal` versus `double`.
   - How priority, groups and cap work.
   - Whether `/actuator/info` exists on the stand.
   - Whether DEBUG logging can be turned on for `tax-engine` during our window. The logs would show which rules
     fired, in order.
7. **Confirm a safe namespace.** Ask the stand owners whether jurisdiction ids are free-form, and how `shipTo` maps
   to a jurisdiction. This plan uses test jurisdictions `ZZ-T1`…`ZZ-T10` (`country: "ZZ"`, `region: "T1"`…). If ids
   aren't free-form, we must not overwrite any real jurisdiction on the shared stand. Re-plan the uploads with an
   export, restore and time window agreed with the two other teams.
8. **Use only match-expression syntax that appears in the goldens.** The expressions below are pseudo-syntax.
   Operators never seen in a golden (negation, `||`) appear only in `ZZ-T6`, so that if that upload is rejected,
   nothing else is lost.

## 3. Round 10: 50 requests

Rules for the round:

- Record the status, headers and body bytes of every answer, including `error.message`.
- Write the port's prediction for every request before sending (§2.5).
- All uploads go to `ZZ-*`. Requests to real jurisdictions are quotes only, so they are read-only.
- Each upload tests one thing that might be rejected, so one rejection can't hide other probes.
- Every multi-line quote lists SKUs out of alphabetical order (`Z…`, `A…`, `M…`), so line order is observed for free.

Tiers: **M** = must (27), **S** = should (17), **P** = may (6). If the budget is cut, drop the P rows first, then S
rows from the bottom up.

Let *G* be any ordinary category outside the D7 list (pick one from the goldens), and *K* an exemption code from the
goldens. Unless noted, rules match all lines and have priority 1.

### Controls and version (5)

| # | Tier | Request | Purpose |
| --- | --- | --- | --- |
| K1 | M | `GET /actuator/info` (or the build id endpoint the owners name) | Records which legacy version answered |
| K2 | M | Replay golden r7-08 | Start control (D21) |
| K3 | M | Replay golden r4-17 | Start control (D7) |
| K4 | M | Replay r7-08 again, sent last | End control. If the answer changed, the stand drifted during the round; re-check the round's other answers |
| K5 | M | Replay r4-17 again, sent last | End control |

### Rounding: D7, rounding stage and totals (4)

`ZZ-T1`: one rule, rate `0.05`. The prices below were chosen so the three candidate explanations of D7 predict
different results:

| Line | unitPrice | Exact tax | Port, *G* (half-up) | Port, FOOD (half-even) | Half-even everywhere | `new BigDecimal(double)` + HALF_UP |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0.10 | 0.005 | 0.01 | 0.00 | 0.00 | 0.01 |
| b | 2.90 | 0.145 | 0.15 | 0.14 | 0.14 | 0.14 |
| c | 0.30 | 0.015 | 0.02 | 0.02 | 0.02 | 0.01 |
| d | 2.50 | 0.125 | 0.13 | 0.12 | 0.12 | 0.13 |

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U1 | M | `PUT ZZ-T1` | Also the first test of the namespace. If it's rejected, stop and re-plan the uploads |
| Q1 | M | Quote in ZZ-T1, lines a to d, category *G* | Rounding keyed on category, versus half-even everywhere, versus `double` arithmetic |
| Q2 | M | Same lines, category FOOD | Same, plus: does FOOD round half-even in a fresh jurisdiction at the same rate? If not, the mode follows jurisdiction or rate, not category |
| Q3 | M | Quote in ZZ-T1, *G*: line X qty 3 at 0.50, line Y qty 1 at 0.50 | X: rounding per unit (0.09) versus per line (0.08). Total: sum of rounded line taxes (0.11 or 0.12) versus rounding the unrounded sum (0.10). Tests the `rapid` invariant |

### Rule combination and order: D3 (6)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U2 | M | `PUT ZZ-T2`: group [A rate 0.10, prio 5; B rate 0.20, prio 5] | |
| U3 | M | `PUT ZZ-T3`: same rules, B uploaded first | |
| Q4 | M | Quote in ZZ-T2, one *G* line at 100.00 | First match wins (10) versus stacking (30) versus compounding (32) |
| Q5 | M | Same quote in ZZ-T3 | With equal priorities, does upload order decide? This is D3's tie rule |
| U4 | S | `PUT ZZ-T4`: G1 [B 0.20 prio 9], G2 [A 0.10 prio 1] | |
| Q6 | S | Quote in ZZ-T4, *G* line at 100.00 | Is priority global or per group? Visible only under first-match or compounding. A result of 30 confirms the rules commute |

### Unknown and absent fields: D9 (2)

`ZZ-T6` uses rates that are powers of two, so the total shows exactly which rules applied (assuming rules stack; see the notes):

- U1 `unknownField == "x"` (0.01)
- U2 `!(unknownField == "x")` (0.02)
- U3 `category == G || unknownField == "x"` (0.04)
- U4 `unknownField == "x" || category == G` (0.08)
- E1 `exemptionCode == "X"`, with no exemption code in the request (0.16)
- E2 `!(exemptionCode == "X")` (0.32)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U5 | M | `PUT ZZ-T6` | If it's rejected (400 plus a message), the upload refuses unknown fields or this syntax. That's an answer in itself |
| Q7 | M | Quote in ZZ-T6, *G* line at 100.00, no `exemptionCode` | "Not applied" versus "false" (U2 applies only under "false"). Short-circuit order (U3 versus U4). Whether an absent known field behaves like an unknown one (E1, E2) |

### Cap, duplicate SKUs and re-upload: D14, D22 (8)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U6 | M | `PUT ZZ-T7`: one rule, rate 0.10, cap 5.00 | |
| Q8 | M | Quote in ZZ-T7: two *G* lines, different SKUs, 40.00 each | Cap per line (4 + 4) versus per order (5 total) |
| Q9 | M | Quote in ZZ-T7: one line, qty 4 at 20.00 | Cap per line (5) versus per unit (8) |
| Q10 | S | Like Q8, but both lines have the **same** SKU | Does the legacy service merge lines by SKU? Compare with Q8 |
| U7 | S | `PUT ZZ-T7` v2: rate 0.20, no cap | |
| Q11 | S | Quote, sent right after U7: one line at 40.00 | Does an upload replace or merge (is the cap gone)? Stale cache (4 versus 8) |
| U8 | M | `PUT ZZ-T7` v3: v2 plus a rule on `category == "NOT_A_CATEGORY"` | D22: is the upload rejected with 400? |
| Q12 | M | Quote, same line as Q11 | Did a rejected upload leave the previous rules intact, wipe them, or apply part of the upload? |

### Empty group, category case, duplicate names: D15, D22 (6)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U9 | S | `PUT ZZ-T5`: G0 `rules: []`, then G1 [A 0.10] | D15: is the upload accepted? |
| Q13 | S | Quote in ZZ-T5, *G* line at 100.00 | Is the empty group ignored, or does it block G1? |
| U11 | S | `PUT ZZ-T9`: two rules both named `dup`, rates 0.10 and 0.20 | Is a duplicate name accepted? |
| Q15 | S | Quote in ZZ-T9 at 100.00 | Both rules apply (30), the first is kept (10), or the last is kept (20) |
| U10 | P | `PUT ZZ-T8`: rule `category == "food"` (lowercase), rate 0.10 | Is category matching case-sensitive at upload? |
| Q14 | P | Quote in ZZ-T8, FOOD line at 100.00 | Does the lowercase rule match? |

### Zero-quantity dropping: D21 (4)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| U12 | M | `PUT ZZ-T10`: exact copy of the CA-QC configuration | |
| Q16 | M | Quote in ZZ-T10: one qty 0 line, one qty 1 line | Dropped: dropping is driven by the configuration. Kept: it depends on the jurisdiction name or on data outside the rules |
| Q17 | M | Quote in CA-QC: line qty 1 at 0.00, plus a normal line | Is the rule "quantity is 0" or "taxable amount is 0"? |
| Q18 | S | Quote in CA-QC: line exempted with *K* (tax 0, qty 1), plus a normal line | Is the rule "tax is 0"? |

### Exemption codes: D12 (4)

Quotes in a real jurisdiction whose goldens use *K*. The variants that might be rejected are split across quotes, so one 400 hides as little as possible.

| # | Tier | Lines | Tells apart |
| --- | --- | --- | --- |
| Q19 | M | `K`, `lower(K)` | Case-insensitive or not |
| Q20 | M | `" K "`, `"\tK"` | Whether spaces and tabs are trimmed |
| Q21 | S | `"K "`, `" K"` | JVM `trim()` (keeps both) versus Go `TrimSpace` (strips both). This is the likeliest place for the port to differ today |
| Q22 | S | `ZZZ` (unknown code) | 400, or ignored? |

### Postal codes: D18 (2)

These are quotes in the jurisdiction from r2-05 and r2-06. Each order has one `shipTo`, so each variant needs its own quote.

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| Q23 | S | Postal code in lowercase, or with the inner space removed or added (whichever applies to that country) | Is the prefix compared on raw text or on a normalized form? |
| Q24 | P | Postal code with a leading space | Is the postal code trimmed? |

### Input spellings and edge cases: D25 and missing decisions (9)

| # | Tier | Request | Tells apart |
| --- | --- | --- | --- |
| Q25 | M | `quantity: 2.5` | Jackson truncates to 2 (a wrong amount, with no error) versus a 400 |
| Q26 | M | `unitPrice: -10.00` (a refund line) | Negative tax, tax clamped to 0, or 400. Tests the `rapid` invariant |
| Q27 | S | `unitPrice: " 12.50"` | Whether a string price is trimmed |
| Q28 | S | `unitPrice: 12345678901234567.89` | Exact decimal versus float64. Also shows how the response prints a large number (scale, exponent) |
| Q29 | S | Quote with an unknown `category` | Not decided anywhere yet: 400, zero tax, or a default rate |
| Q30 | S | `shipTo` CA with no region, then (if budget allows) CA with an unknown region | Fallback to the country, zero tax, or 400 |
| Q31 | P | Key spelled `"UnitPrice"` | Go matches keys case-insensitively. Jackson ignores the unknown key, and then the price is missing |
| Q32 | P | `unitPrice: 0.69999999999999999999` as a JSON number, rate 0.05 | Exact (0.03) versus parsed into a double and printed back (0.04) |
| Q33 | P | `lines: []` | Total 0, or 400 |

Total: 5 + 4 + 6 + 2 + 8 + 6 + 4 + 4 + 2 + 9 = **50**.

### Notes on the round

- **Which rule-combination semantics?** Q4, Q5 and Q7 assume rules stack. If the goldens (§2.4) show that the first
  matching rule wins, rebuild ZZ-T6 as one unknown-field rule plus a match-all fallback at a lower priority, one
  variant per upload. Pay for the extra uploads by dropping S rows.
- **Order of sending.** Send K1, K2 and K3 first, then U1 (go or no-go for the namespace), then everything else in
  table order, and K4 and K5 last. Requests within one block depend on each other's order (U7 → Q11 → U8 → Q12);
  blocks don't depend on each other.
- **Leftovers.** The test jurisdictions stay on the stand. List them in the ticket so the other two teams know they
  aren't real.

## 4. After the answers arrive

1. Check K4 and K5 against K2 and K3. If anything drifted, re-check the round before acting on it.
2. Sort each contradiction into one of two kinds:
   - a **flipped** decision: an existing D-row takes a different value;
   - a **new** decision: a rule nobody had written down.

   New decisions mean the current measures were blind to that area. Add the input to the parity suite, and add the
   new dimension (order, SKU identity, spelling class, rounding stage) as a factor in the pairwise model and the
   `rapid` generators.
3. Write each finding as observed (cite the request and answer), inferred (name the assumption), or hypothesis (name
   the request that would settle it). Don't change the port on a hypothesis.
4. Change `comparator.yaml` for whatever the answers show clients can see. At minimum, compare line order and number
   text raw if the legacy service is consistent about them.
5. **Stopping rule for cutover.** Round 10 produces no new decisions, every M and S hypothesis has an answer, and the
   shadow-traffic gate (§2.1) has passed. If round 10 does produce new decisions, there's no round 11 before
   cutover. In that case, extend shadow traffic, or cut over with the legacy service kept as a fallback, instead of
   relying on the suite.
