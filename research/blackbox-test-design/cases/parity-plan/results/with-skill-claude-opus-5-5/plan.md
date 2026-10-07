# tax-engine port: blind spots and the final probe round (round 10)

Attach to the change ticket for round 10 on the shared legacy stand. Budget: at most 50 requests. Cutover is about
2026-10-28. A round takes about a week, so the ticket has to be filed by 2026-10-09. That leaves roughly one week
between the answers arriving and cutover.

Goal assumed throughout: **parity**. The Go port reproduces legacy behavior, quirks included. If any quirk below is
going to be fixed on purpose instead, list it as a deliberate difference in `decisions.md` before cutover.

## 1. Summary

The suite being green tells us the port matches what we have already asked. It does not tell us the port is
structurally right. There are four reasons:

1. **Every adequacy measure we report comes from the port itself.** The mutants are alternatives that someone on the
   port team wrote down. The pairwise factors (`jurisdiction × category × exemption kind × priority class`) are
   concepts the port computes. The `rapid` properties ("total = sum of line taxes", "tax is never negative") are
   things the port believes, and none of them has been sent to the legacy service. None of these measures can see a
   rule the port lacks: line position, upload order, sibling lines, how a value is spelled, negative amounts, or how
   the total is rounded.
2. **The comparator hides whole classes of differences.** `arrays: sort` hides the order of response lines and of
   rules. `nulls: drop` merges `null` with an absent field. `numbers: decimal-value` merges `12.5`, `12.50` and
   `1.25E+1`, and possibly `"12.50"` too. Ignoring `$.error.message` throws away the one channel that names which
   check failed. Clients parse the raw body, so they will see these differences even though the suite does not.
3. **Four decisions have no recorded answer behind them, and three rest on a single answer.** D3, D12, D15 and D22
   come only from the design doc, which was written from interviews, so they are guesses. D9, D14 and D25 are each
   pinned by one golden.
4. **Two decisions are hand-written exception lists (D7, D21).** Both are typical footprints of an unknown general
   mechanism. Section 3 lists the candidate mechanisms. Each one fits the goldens and predicts different behavior on
   inputs we have not sent.

Most of the risk can be reduced **before any stand request is made** (section 4): a raw re-diff of the stored
answers, scoring the D7 and D21 candidates offline, questions to the owning department, and shadow traffic. The 50
requests (section 5) go to the questions only the stand can answer, and money-affecting questions come first.

## 2. Decision audit

"Live alternatives" are hypotheses: each fits every recorded answer we know of and has not been separated from the
port's choice yet.

| Id | Pinned by | Strength | Live alternatives (legacy is Java 11 / Spring Boot / Jackson / PostgreSQL) |
| --- | --- | --- | --- |
| D3 | design doc | **guess** | ties broken by rule `name` (sorted, or `HashMap` order), or by PostgreSQL row order (no `ORDER BY`, which changes after an update); descending priority; ordering across groups instead of within one. The comparator's array sort would hide any order that only shows up in a list |
| D7 | 3 goldens, one per category | exception list | see section 3: legacy uses `double`; the mode depends on the rule or jurisdiction, not the category; rounding per unit; total rounded separately from the lines; the whole order rounds half-even when any line qualifies |
| D9 | 1 golden (r5-11) | weak | the unknown field reads as `null` (so `!=` and negation *do* apply); an evaluation error skips the whole group or rule set; rejected at upload |
| D12 | design doc | **guess** | case-sensitive (PostgreSQL `=` lookup); `String.trim()` (strips ≤ U+0020, not NBSP) where Go's `strings.TrimSpace` strips Unicode spaces; no trimming; `toLowerCase()` with the default locale |
| D14 | 1 golden (r3-40) | weak | cap per unit (r3-40 cannot tell this apart if its quantity was 1), per order, per rule across lines, or on the line total of all rules |
| D15 | design doc | **guess** | rejected with 400; accepted, and the empty group ends evaluation or counts as a match |
| D18 | 2 goldens | moderate | case-sensitive prefix; spaces significant or stripped; a JSON number for `postalCode` coerced to a string by Jackson (leading zeros lost) |
| D21 | 3 goldens, one per jurisdiction | exception list | see section 3: every region-level jurisdiction drops the line; the drop is driven by config (for example a `cap` divided by quantity throws, and the line is skipped); every zero-amount line is dropped, not only quantity 0 |
| D22 | design doc | **guess** | accepted and the rule never matches; 500; enum matching is case-sensitive (Jackson default) while the port's is not |
| D25 | 1 golden (r1-02) | weak | Jackson `BigDecimal` accepts exponent forms and leading zeros, may reject whitespace, and may turn `""` into `null` (then 500); unbounded precision versus Go `float64` |

Behavior that the port decides but that is missing from this excerpt (check the full `decisions.md`; if a behavior
is missing there too, it is a **new decision** with no answer behind it):

- Quantity coercion through Jackson's `int` binding: by default `2.5` becomes `2`, and `null` becomes `0`, which
  then triggers D21. Go's `encoding/json` rejects `2.5`.
- JSON property names: Jackson matches case-sensitively and ignores unknown properties under the Spring Boot
  default. Go matches names case-insensitively, so `"UnitPrice"` binds in the port and is ignored by the legacy
  service.
- Negative quantity or price (refunds): the port's "never negative" property has never been asked of the legacy
  service.
- Whether the total is rounded on its own or summed from rounded lines.
- Whether rules are cached after a `PUT`, and whether a re-upload replaces or merges.
- Category spelling inside a *quote* (`"food"`): taxed as `FOOD`, taxed as an unknown category, or rejected.
- How number scale and format are printed in the response (`BigDecimal` keeps `12.50`; `toString` can print
  `1.25E+1`).

## 3. The two exception lists

**D7 rounding.** The answer says those three lines rounded *down* at an apparent tie. "Half-even for three
categories" is one mechanism that explains this. Another is ordinary Java `double` arithmetic: `2.01 * 0.5` is stored
as just under `1.005`, so it rounds to `1.00` whatever the mode. Computed offline (rate 0.5 and 0.1, quantity 1):

| unitPrice × rate | BigDecimal HALF_UP | BigDecimal HALF_EVEN | `double` + `Math.round` | `new BigDecimal(double)` HALF_UP | `BigDecimal.valueOf(double)` HALF_UP | `valueOf` HALF_EVEN |
| --- | --- | --- | --- | --- | --- | --- |
| 0.25 × 0.5 | 0.13 | 0.12 | 0.13 | 0.13 | 0.13 | 0.12 |
| 2.01 × 0.5 | 1.01 | 1.00 | 1.00 | 1.00 | 1.01 | 1.00 |
| 2.03 × 0.5 | 1.02 | 1.02 | 1.01 | 1.01 | 1.02 | 1.02 |
| 2.69 × 0.5 | 1.35 | 1.34 | 1.35 | 1.34 | 1.35 | 1.34 |
| 1.15 × 0.1 | 0.12 | 0.12 | 0.12 | 0.11 | 0.11 | 0.11 |
| 0.35 × 0.1 | 0.04 | 0.04 | 0.03 | 0.03 | 0.03 | 0.03 |
| 4.45 × 0.1 | 0.45 | 0.44 | 0.45 | 0.45 | 0.45 | 0.45 |

Every column has a different pattern, so one request per category tells the mechanisms apart. Before filing the
ticket, run the same scoring over all 1,812 goldens (task F2). If the `double` columns fit every recorded tie, D7 is
probably a `double` artifact, not a category rule. A port with the wrong mechanism passes every golden and is off by
a cent on other prices.

**D21 dropped zero-quantity lines.** Things to notice: the three jurisdictions are all region-level (`XX-YY`), and
D14's cap is the obvious place where a quantity could be a divisor. Candidates: (a) a list of jurisdiction codes,
which is what the port does; (b) every region-level jurisdiction; (c) something in those jurisdictions' configs; (d)
every line whose taxable amount is zero. Requests Z1 to Z6 separate these.

## 4. Free work before and alongside the round (no stand requests)

| # | Task | What it closes | Owner / by |
| --- | --- | --- | --- |
| F1 | Re-run the parity suite on the stored **raw** responses with each normalization disabled in turn (array sort, null drop, decimal-value, error message). Feed the comparator pairs that differ in exactly one aspect (`12.5` vs `12.50`, `12.50` vs `"12.50"`, `null` vs absent) to confirm which ones it merges. If raw bodies were not stored, that is itself a gap: store them from round 10 on | number format and scale, line order, null versus absent, error text: all differences clients can see | port team, 2026-10-09 |
| F2 | Score the D7 columns above and the D21 candidates (a) to (d) against every recorded answer. Drop the candidates that contradict an answer | narrows section 5 blocks R and Z; may rewrite D7 without a single request | port team, 2026-10-09 |
| F3 | Ask the owning department (treat the answers as hypotheses until a probe confirms them): which expression engine evaluates `match` (SpEL? JEXL?); the exact rounding code (`RoundingMode`, `double` or `BigDecimal`); the Jackson settings (`ACCEPT_FLOAT_AS_INT`, `FAIL_ON_NULL_FOR_PRIMITIVES`, `FAIL_ON_UNKNOWN_PROPERTIES`, coercion of empty strings); whether rule loading has an `ORDER BY`; how exemption codes are looked up (SQL `=` or Java); rule caching; whether `/v1/tax/quote` writes anything to PostgreSQL; **whether the stand runs the same build as production**; whether test jurisdictions `ZZ-*` may be created on the stand and how to remove them | many alternatives in section 2; safety of section 5 | change-ticket owner, 2026-10-09 |
| F4 | **Shadow traffic.** Mirror production `POST /v1/tax/quote` to the Go port and diff raw. Before mirroring, confirm with F3 that a quote writes nothing; if it does, give the shadow side its own database. Never mirror `PUT /v1/rules`. Run it until cutover and keep it running in reverse (Go serves, legacy shadows) for two weeks after | the real input distribution: spellings, refunds and combinations nobody thought of | platform team, start this week |
| F5 | Look up whether rounds 1 to 9 recorded the legacy build version. If they did not, the controls in section 5 are the only check that the stand has not changed since round 1 | tells a model error apart from a legacy change | port team |
| F6 | Prepare **both branches** in the port, behind a config switch, for every must-tier decision (D7 mechanism, D21 mechanism, D12 normalization, D14 scope, quantity coercion). When the answers arrive, picking a branch is then a one-line change, not new code in the last week | the one-week gap between answers and cutover | port team, before answers arrive |

Stopping rule for shadow traffic: if `n` consecutive mirrored production quotes agree on the raw comparison, the
disagreement rate on production-like traffic is below about `3/n` at 95% confidence. For example, 30,000 agreeing
quotes bound it at 0.01%. That bound says nothing about inputs production does not send.

## 5. Round 10: the 50 requests

### Ground rules

- **Isolation.** Every probe that changes configuration goes to a new jurisdiction in the `ZZ-*` namespace (approved
  under F3). Do not `PUT` to any jurisdiction the other two teams or the goldens use. Probes against real
  jurisdictions are quotes only. If `ZZ-*` is not allowed, drop blocks E, X and V, and run S1/S2 only in a
  jurisdiction the other teams have agreed to give up for the day, after exporting its rules and with a restore
  step at the end.
- **Independence.** Each question is either one request or a marked sequence on its own jurisdiction, so the
  questions can run in any order relative to each other.
- **Validity.** A request that is rejected answers nothing about evaluation. Risky spellings therefore go in their
  own requests, and only spellings that every candidate accepts share a request.
- **Predictions first.** Before sending, run every payload through the Go port and commit its answer to
  `parity/round10/predictions/`, together with the alternative predictions from sections 2 and 3. Send each line with
  a unique `sku` so lines can be matched even if one is dropped.
- **Record raw.** Store the full raw status, headers and body (including `error.message`) of every answer, plus the
  build version from K1/K6.
- **Placeholders.** Fill these from the goldens before filing:
  - `STD1`, `STD2`, `STD3`: three categories that appear in goldens and are not in D7's list.
  - `EX`: an exemption code accepted in some golden.
  - `J_EX`: that golden's jurisdiction.
  - `J_R4`: the jurisdiction of golden r4-17.
  - `J_REG`: a region-level jurisdiction from the goldens that is not in D21's list.
  - Match expressions use the syntax of existing uploads.

### Configurations uploaded

- **ZZ-T1** (rounding and quantity): one group, two rules. `R50` has rate `0.5`, matches categories `STD1`, `FOOD`,
  `BOOKS`, `KIDS_CLOTHING` and `STD2`, and has no cap. `R10` has rate `0.1` and matches `STD3`.
- **ZZ-T6** (cap and postal code): `CAPA` has rate `0.5`, cap `1.00` and matches `STD1`. `CAPB` has rate `0.5`,
  cap `1.00` and matches `STD2`. `PLUS` has rate `0.1`, matches `STD2` and has no cap. `POST` has rate `0.2`, matches
  `STD3` and postal prefix `H2X`.
- **ZZ-T2 / ZZ-T3** (order): rules `zeta` (priority 10), `alpha` (priority 10) and `mid` (priority 5), all on
  `STD1`, with rates that make application order visible *under the port's own combining semantics* (for example
  first match wins, compounding, or a cap on the running total). ZZ-T2 uploads them in the order `zeta, alpha,
  mid`; ZZ-T3 in reverse. If application order cannot change any output under the port's semantics, say so in the
  ticket: D3 is then unobservable, and E1 to E4 become reserve.
- **ZZ-T4**: two rules both named `dup`, on `STD1`, with rates `0.1` and `0.2`.
- **ZZ-T5** (D9): one group with rates chosen so that the sum identifies which rules applied: `a` `nosuch == 'x'`
  0.01; `b` `nosuch != 'x'` 0.02; `c` `nosuch == 'x' or category == STD1` 0.04; `d` `category == STD1` 0.08 (same
  group, after a to c). A second group has `e` `category == STD1` 0.16.

### Requests

Tier: **M** = must, **S** = should, **Y** = may. Numbering is the execution order.

| # | Id | T | Request | Separates |
| --- | --- | --- | --- | --- |
| 1 | K1 | M | `GET` the build or version endpoint (actuator info or equivalent) | stand version for this round |
| 2 | K2 | M | replay golden r8-33 verbatim | drift since round 8 (D7) |
| 3 | K3 | M | replay golden r9-21 verbatim | drift since round 9 (D21) |
| 4 | S1 | M | `PUT /v1/rules/ZZ-T1` | whether a test jurisdiction is accepted (gates everything that uses `ZZ-*`) |
| 5 | S2 | M | `PUT /v1/rules/ZZ-T6` | sets up blocks C and P |
| 6 | R1 | M | quote ZZ-T1, four `STD1` lines with unitPrice `0.25`, `2.01`, `2.03`, `2.69`, quantity 1 | rounding columns in section 3 for an unlisted category |
| 7 | R2 | M | same as R1 with `FOOD` | whether `FOOD` differs, and how |
| 8 | R3 | M | same prices: `BOOKS` 0.25 and 2.01; `KIDS_CLOTHING` 2.69 and 2.03 | the rest of D7's list |
| 9 | R4 | M | R1 and R2 lines interleaved in one quote | rounding per line versus per order (one `FOOD` line switches the whole order) |
| 10 | R5 | M | quote ZZ-T1, `STD3` lines `1.15`, `0.35`, `4.45`, `10.05` | `double` versus `BigDecimal`; rate held as `double` |
| 11 | R6 | M | quote ZZ-T1: `STD1` unitPrice `0.25` quantity 3; `FOOD` unitPrice `0.25` quantity 3 | rounding per unit (0.39 / 0.36) versus per line (0.38 / 0.38) |
| 12 | R7 | M | quote ZZ-T1, three `STD3` lines of `0.35` | total of rounded lines (0.12 or 0.09 under `double`) versus rounded total (0.11 or 0.10) |
| 13 | R8 | M | quote `J_R4`, `FOOD` and `STD1` lines at prices that tie under `J_R4`'s known rate (compute from goldens) | rounding driven by jurisdiction config rather than category |
| 14 | Z1 | M | quote ZZ-T1, `STD1` lines with quantity 0 and quantity 1 | D21 (b): does a new region-level jurisdiction drop the line |
| 15 | Z2 | M | quote `J_REG`, quantity 0 and quantity 1 | D21 (a) versus (b) on a real jurisdiction |
| 16 | Z3 | M | quote `CA-QC`: quantity 1 with unitPrice 0; quantity 0 with `EX`; quantity 0 in a category no rule matches | D21 (d): zero amount versus zero quantity; whether the drop depends on a rule matching |
| 17 | Z4 | M | `GET` the `CA-QC` rules (only if a read endpoint exists; otherwise Z4 to Z6 are reserve) | export for Z5 |
| 18 | Z5 | M | `PUT /v1/rules/ZZ-QC` with `CA-QC`'s rules verbatim | — |
| 19 | Z6 | M | quote ZZ-QC with K3's lines | D21 (c) config versus (a) jurisdiction code |
| 20 | Z7 | M | quote ZZ-T1, `STD1` quantity `2.5` | Jackson truncating to 2 versus a 400 (the port's behavior) |
| 21 | Z8 | M | quote ZZ-T1, `STD1` quantity `-1` | negative tax versus 0 versus 400 (the port's "never negative") |
| 22 | Z9 | M | quote `US-TX`, one line with `"quantity": null` and one normal line | `null` becomes 0 and the line is silently dropped, versus a 400 |
| 23 | C1 | M | quote ZZ-T6: `STD1` unitPrice 3.00 qty 1; `STD1` unitPrice 1.00 qty 3; and the second line again | cap per unit (total 4.00) / per line (3.00) / per order or per rule across lines (1.00) (D14) |
| 24 | C2 | M | quote ZZ-T6: `STD2` unitPrice 3.00 qty 1 (matches `CAPB` and `PLUS`) | cap on the rule's own tax (1.30) versus on the line's total tax (1.00) |
| 25 | G1 | M | quote `J_EX`: one line with code `ZZNOPE`, one line without a code | whether an unknown code is tolerated per line, which is what makes G2 valid |
| 26 | G2 | M | quote `J_EX`, one line each: `EX`, lowercase, `" EX "`, `"EX\t"`, `" EX"`, `"EX "`, `""`, `null` | D12 normalization per spelling (Java `trim` versus Go `TrimSpace` on NBSP and em space). If `EX` contains `i`, add a Turkish dotless `ı` line |
| 27 | G3 | M | quote `J_EX`, single line, lowercase `EX` | D12 case, even if G2 is rejected |
| 28 | G4 | M | quote `J_EX`, single line, `" EX "` | D12 trimming, even if G2 is rejected |
| 29 | E1 | S | `PUT ZZ-T2` (order `zeta, alpha, mid`) | — |
| 30 | E2 | S | quote ZZ-T2, one `STD1` line | ascending versus descending priority; tie broken by upload order versus name |
| 31 | E3 | S | `PUT ZZ-T3` (reverse order) | — |
| 32 | E4 | S | quote ZZ-T3, same line | with E2: upload order (answers differ) versus name or hash order (answers agree) |
| 33 | E5 | S | `PUT ZZ-T4` (two rules named `dup`) | rejected versus accepted |
| 34 | E6 | S | quote ZZ-T4, one `STD1` line | first wins / last wins / both apply |
| 35 | E7 | S | re-`PUT ZZ-T2` without `alpha`, and with `mid`'s rate changed | — |
| 36 | E8 | S | quote ZZ-T2 immediately after E7 | replace versus merge; stale cache after an upload |
| 37 | X1 | S | `PUT ZZ-T5` | a rejection here is itself the answer for D9: unknown fields are checked at upload |
| 38 | X2 | S | quote ZZ-T5, one `STD1` line, unitPrice 100 | which of a to e applied: "rule does not apply" (port) versus `null` semantics (b, c apply) versus "error stops the group" (d missing) |
| 39 | N1 | S | quote ZZ-T1, `STD1` lines with unitPrice `1.25E1`, `"1.25E1"`, `"0012.50"`, `12345678901234567.89`, `"12345678901234567.89"` | D25 spellings Jackson accepts; Go `float64` precision; response number format in the raw body |
| 40 | N2 | S | quote ZZ-T1, unitPrice `" 12.50 "` | whitespace accepted versus 400 |
| 41 | N3 | S | quote ZZ-T1, unitPrice `-10.00` | negative price (refund) |
| 42 | N4 | S | quote ZZ-T1: one line with category `"food"`, one with `"FOOD"` | quote category matching: case-insensitive / unknown category / 400 |
| 43 | N5 | S | quote ZZ-T1, a line using the keys `"UnitPrice"` and `"Quantity"` | Jackson case-sensitive binding (fields missing) versus Go case-insensitive binding |
| 44 | P1 | Y | quote ZZ-T6, `STD3`, postalCode `"h2x 1y4"` | D18 case sensitivity |
| 45 | V1 | Y | `PUT ZZ-T7` with category `NOPE` in one rule | D22: 400 versus accepted versus 500 |
| 46 | V2 | Y | `PUT ZZ-T8` with an empty group followed by one `STD1` rule | D15 at upload |
| 47 | V3 | Y | quote ZZ-T8, one `STD1` line | D15 at evaluation: ignored versus ends evaluation |
| 48 | K4 | M | replay golden r8-33 | drift during the round |
| 49 | K5 | M | replay golden r9-21 | drift during the round |
| 50 | K6 | M | `GET` the build or version endpoint | stand redeployed during the round |

Reserve, used only if Z4 to Z6 or E1 to E4 drop out: P2 (postalCode `" H2X 1Y4"`); a second ZZ-T1 quote with
quantity `"2"` as a string; a `PUT` to ZZ-T5 with `exemptionCode == null` as the match.

### Drop order if the budget is cut

Remove from the bottom up: V3, V2, V1, P1, N5, N2, E5 and E6, E7 and E8, N4, N1, X1 and X2, E1 to E4, N3. Do not cut
the controls (K*), S1 or S2, or any request in blocks R, Z, C or G. Those blocks decide amounts of money and whether
lines are silently dropped.

## 6. After the answers arrive

1. **Check the controls first.** If K2/K3 differ from K4/K5 or from the goldens, or K1 differs from K6, the stand
   drifted. Every answer from this round then needs a second look before it changes the port.
2. Compare every answer **raw** with the port's prediction. Classify each mismatch:
   - **flipped**: another value of an existing decision. Switch the F6 branch.
   - **new decision**: behavior the decision list did not have. Add it to `decisions.md` together with its
     answer. New decisions are the measure of how much the old measures could not see.
3. Record each finding as one of:
   - **observed**: cite the request and the answer;
   - **inferred**: name the assumption it rests on;
   - **hypothesis**: name the question that would settle it.

   Do not record a mechanism (for example "legacy uses `double`") unless the request that separates it from its
   nearest alternative has been answered.
4. Re-run the full parity suite with the comparator also in raw mode after every change.
5. **Go / no-go for 2026-10-28:**
   - the controls are stable;
   - every M-tier answer either matches the port or has been applied and re-verified;
   - shadow traffic (F4) shows no raw disagreement in the last 7 days over a volume large enough for the agreed
     `3/n` bound;
   - the rollback path to the legacy service has been rehearsed.

   Unanswered S/Y questions stay listed in the ticket as known open hypotheses. Reverse shadowing after cutover
   watches for them in production.

## 7. What stays blind even after this round

- Inputs production never sends and this round did not ask. Shadow traffic does not cover them, and neither do
  50 requests.
- How rules interact across country-level and region-level configurations, if the legacy service has such a
  hierarchy (ask under F3).
- Behavior under concurrent uploads and quotes.
- An independent second model of the legacy service, built from the goldens alone, would find structural gaps that
  none of the above can. It does not fit in three weeks; if issues show up after cutover, it is the next step.
