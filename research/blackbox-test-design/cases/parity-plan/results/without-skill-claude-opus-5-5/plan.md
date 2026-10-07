# tax-engine port: final legacy probe round (round 10) and blind-spot review

Change ticket attachment. Budget: at most 50 HTTP requests to the shared legacy stand, retries included. This plan
uses 43 planned requests and keeps 7 in reserve.

## 1. Why a green suite does not settle it

Only one of the four test layers asks the legacy service anything. The other three check the port against the port
team's own model of the legacy service.

| Layer | What it shows | What it cannot show |
| --- | --- | --- |
| Parity suite (1,812 pairs) | The port reproduces the recorded responses, as far as `comparator.yaml` looks | Anything not recorded. Several decisions were *fitted* to these goldens (D7, D21), so matching them is training-set accuracy, not evidence the rule is right |
| Mutation testing, 94% | The port's tests pin the port's behavior tightly | Whether that behavior is the legacy's. A wrong decision with a strong test kills every mutant |
| Property tests (`rapid`) | The port keeps the invariants the team wrote down | Whether the legacy keeps them. "Total = sum of line taxes" and "tax is never negative" are assumptions; the legacy may round the total separately, or return negative tax on refunds |
| Pairwise, 100% | Every pair of *class-level* values of the four chosen factors appears | Factors not in the model (rounding ties, quantity edge values, input formats, postal formats, rule order, multi-line caps), value boundaries inside a class, and three-way interactions. D21 is jurisdiction × quantity = 0 and D7 is category × exact tie: pairwise over these factors never targets either |

### 1.1 The comparator hides whole classes of difference

| Setting | What it hides | Who could break |
| --- | --- | --- |
| `arrays: sort` | Order of response lines and of any other array. Combined with D21 (lines dropped), a client that matches response lines to request lines by index gets the wrong tax on the wrong line | Any client that does not key by `sku`; duplicate `sku`s make keying impossible |
| `nulls: drop` | `"x": null` vs a missing `x`, in both directions. A line that legacy returns with `"tax": null` and the port omits looks equal | JS clients (`'x' in obj`), strict schema validators, anything that maps null and absent differently |
| `numbers: decimal-value` | Scale (`10` vs `10.00`), exponent form (Jackson writes `BigDecimal` as `1E+1` unless `WRITE_BIGDECIMAL_AS_PLAIN` is on), and possibly number vs numeric string | Clients that print, hash, sign or string-compare amounts; invoices and reconciliation |
| `$.error.message` ignored | Error text | Clients that branch on the message (common when no error code exists) |

Not stated in `comparator.yaml`: whether the HTTP status code and `Content-Type` are compared. Confirm both are.

### 1.2 Evidence behind each decision

| Id | Evidence | Concern |
| --- | --- | --- |
| D3 | Design doc only (interviews) | No legacy evidence at all. Java has three plausible tie orders: upload order (stable `List.sort`), name order (`TreeMap`), hash order (`HashMap` keyed by group name), plus unstable `PriorityQueue` order. Also: legacy reads rules back from PostgreSQL; without `ORDER BY`, "upload order" can change after an `UPDATE` or a restart. That last part cannot be probed on a shared stand |
| D7 | 3 goldens, one per category | An enumeration of exactly what was observed. Half-up and half-even differ only on exact ties, so the other categories may simply never have hit a tie. Also unknown: whether legacy computes in `double` (then `1.005` is `1.00499…` and rounds *down* under half-up), and at which stage it rounds (per unit, per line, per rule, on the total) |
| D9 | 1 golden | If legacy evaluates an unknown field as `null` (SpEL-like), `x == 'A'` is false but `x != 'A'` is **true**, so the rule applies. One golden with `==` cannot tell. Same question for a *known* optional field that is absent (`exemptionCode`), which matters far more in real configs |
| D12 | Design doc only | Java `trim()` strips U+0000–U+0020 and not NBSP; Go `strings.TrimSpace` strips NBSP and U+2003 but not U+0001. Java `equalsIgnoreCase("i", "İ")` is true; Go `strings.EqualFold` is false |
| D14 | 1 golden | If r3-40 has one line with quantity 1, per-unit, per-line, per-rule and per-order caps all give the same answer |
| D15 | Design doc only | Legacy may reject the upload, or fail at quote time |
| D18 | 2 goldens | Normalization (case, spaces, hyphens), ZIP+4, overlapping prefixes, and Jackson coercing a JSON number `2139` into the string `"2139"` (Go's `encoding/json` rejects a number into a string) |
| D21 | 3 goldens, one per jurisdiction | Again an enumeration of what was observed. A hard-coded list of three unrelated jurisdictions is unlikely; the real trigger is more likely a property of those jurisdictions' rule configs. The stand is shared, so those configs may have been uploaded by the other two teams |
| D22 | Design doc only | And the quote side is undecided: what does a quote with an unknown or lower-case `category` do? Jackson enums are case-sensitive and reject unknown values by default |
| D25 | 1 golden | Jackson (Spring Boot defaults) also coerces `"2"` → `2` for `quantity`, truncates `2.7` → `2` (`ACCEPT_FLOAT_AS_INT`), turns `null` into `0` for a primitive `int`, rejects `2147483648` for `int`, and matches property names case-sensitively. Go's `encoding/json` does the opposite on almost every one of these and matches names **case-insensitively** (`"UnitPrice"` binds to `unitPrice`) |

### 1.3 Blind spots no stand request can close

- **Recording conditions.** Rounds 1–9 ran on a stand whose rules other teams change, and possibly across legacy
  deploys. A golden is evidence about the config in force at that moment, which nobody recorded.
- **Production rule configs.** Has every production rule upload been loaded into the port? An expression the legacy
  accepts lazily and the port rejects at upload breaks a jurisdiction at cutover.
- **Production input distribution.** The stand traffic was written by us. Real clients send what they send.
- **State and operations.** Rule migration from the legacy PostgreSQL, ordering after migration (D3), quotes during a
  rule upload, restart behavior.

## 2. Before the round (no stand requests)

Do these first; several of them change which probes are worth sending.

1. **Strict re-comparison of the 1,812 recordings.** Re-run parity with each normalization switched off in turn
   (no sort, keep nulls, compare numbers as text, compare error messages). Classify every diff. If raw response bytes
   were not kept, only normalized ones, record that as a finding: the round below must keep raw bytes.
2. **Evidence ledger per decision.** From the goldens, count the cases that could *distinguish* each decision from its
   alternatives: exact rounding ties per category and jurisdiction; quantity-0 lines per jurisdiction, kept vs
   dropped; caps hit by more than one line or quantity > 1; equal-priority rules whose order changes the result.
   A decision with zero distinguishing goldens is untested, whatever the pass count.
3. **Production exposure.** From production rule configs and request logs (or client payload samples): how often
   quantity 0 occurs and where; which `unitPrice` forms occur (string, exponent, whitespace); exemption code shapes;
   postal code shapes; duplicate `sku`s; equal priorities in configs; expressions that reference optional or unknown
   fields; caps in multi-line orders. Load every production config into the port and record rejections. Use this to
   drop or reorder probes below: a probe for an input production never sends moves to the reserve.
4. **Pre-register predictions.** Run every probe below against the port, commit its responses to the repository with
   the ticket number, and for each probe write the competing hypotheses and what each would return. A probe where all
   plausible hypotheses give the port's answer cannot fail and is replaced. For D7 traps, compute the `double` and
   `BigDecimal` outcomes in `jshell` locally.
5. **Stand coordination** (in the ticket): ask the stand owner for free synthetic jurisdiction codes (written `ZZ-P1`…
   `ZZ-P4` below) and a fallback real jurisdiction we may overwrite and restore; ask the two other teams not to upload
   rules for `CA-QC`, `DE-BY`, `US-TX`, `CA-ON`, `US-CA`, `DE-BE` during our window. We only *read* (quote) real
   jurisdictions; every upload goes to a synthetic one.

## 3. Rules for the round

- Capture raw bytes: status, all headers, body exactly as received, timestamp. Compare later with the strict and the
  normalized comparator.
- Every line carries a unique `sku` (`P<request>-<n>`), so results never depend on line order.
- Each rule in `ZZ-P1` is gated by `sku` (for example `sku startsWith 'P05-' && …`) so probes do not interfere.
  Check with the port that gating gives the intended isolation.
- An input that may be rejected is sent alone: one rejected value in a packed request hides the rest.
- Every quote against a real jurisdiction includes a calibration line (`unitPrice` 100.00, quantity 1) to read the
  rate in force today.
- Run in the order below. Uploads that replace `ZZ-P1` (#40) go after every quote that relies on it.

## 4. The requests

"Port says" is filled in from step 2.4 before submission.

### A. Setup (1)

| # | Request | Question |
| --- | --- | --- |
| 1 | `PUT /v1/rules/ZZ-P1`: the probe config. Groups `g-tax`, `g-exempt`, `g-surcharge` uploaded in that order, so upload order, name order (`g-exempt, g-surcharge, g-tax`) and Java `HashMap` order (`g-exempt, g-tax, g-surcharge`) all differ. Contains the rules for blocks B–F | Does the legacy accept a synthetic jurisdiction? If not, switch to the agreed fallback (reserve) |

### B. Rounding: D7 and rounding stage (4)

| # | Request | Question |
| --- | --- | --- |
| 2 | Quote `ZZ-P1`: every `category` value, each with two exact-tie lines (even and odd preceding digit, e.g. tax 0.005 and 0.025 at rate 0.05) plus one `double` trap (a decimal tie that is below the tie in binary) | Rounding mode per category, outside the three golden jurisdictions; `double` vs `BigDecimal` |
| 3 | Quote `ZZ-P1`: quantity 3 at a price whose unit tax is a fraction of a cent; a line hit by two rules that each produce a half cent; three lines each with tax 0.004 | Rounding per unit, per line, or per rule; total rounded separately or summed from rounded lines (the property test assumes the latter) |
| 4 | Quote in the jurisdiction of r4-17, same lines as #2, plus calibration | Is the D7 exception per category or per jurisdiction? |
| 5 | Quote in the jurisdiction of r8-33, same | Same |

### C. Quantity: D21 and coercion (11)

| # | Request | Question |
| --- | --- | --- |
| 6 | Quote `ZZ-P1`: a quantity-0 line, a quantity-0 line with an exemption, a quantity-0 line under a capped rule, one normal line | Drop or keep in a jurisdiction we fully control |
| 7 | Quote `CA-ON`, same shape, plus calibration | Is the drop per country (CA) or per region? |
| 8 | Quote `US-CA`, same | Same, for US |
| 9 | Quote `DE-BE`, same | Same, for DE |
| 10 | Quote `US-TX`, same | Does the r9-21 drop still happen with today's config? If not, the trigger is config, not jurisdiction |
| 11 | Quote `ZZ-P1`: one line, quantity −1 | Refunds: rejected, negative tax, or zero? Tests the "never negative" property |
| 12 | Quote `ZZ-P1`: one line, `unitPrice` −10.00 | Same, for price |
| 13 | Quote `ZZ-P1`: `quantity` `"2"` and `quantity` 2.0 on two lines | Jackson coercion. If 400, split with the reserve |
| 14 | Quote `ZZ-P1`: `quantity` 2.7 | Truncated to 2, rejected, or used as 2.7? |
| 15 | Quote `ZZ-P1`: `quantity` `null` | Becomes 0 (then D21 applies), 400, or 500? |
| 16 | Quote `ZZ-P1`: `quantity` 2147483648 | `int` overflow: 400 in Java; the port may compute |

### D. `unitPrice` forms: D25 (5)

| # | Request | Question |
| --- | --- | --- |
| 17 | Quote `ZZ-P1`, one form per line: `"1e2"`, `".5"`, `"+5"`, `"12.500"`, `12.500`, `1E2`, `"0.123456789"` | Which forms legacy accepts, and whether input scale reaches the output. If 400, split with the reserve |
| 18 | `unitPrice` `" 12.50 "` | Whitespace in a numeric string |
| 19 | `unitPrice` `"NaN"` | Java accepts `NaN` for `double`, rejects it for `BigDecimal`; Go `ParseFloat` accepts it |
| 20 | `unitPrice` `"12,50"` | Locale decimal comma |
| 21 | `unitPrice` `""` | Empty string: null, 0, or 400? |

### E. JSON binding and categories in quotes (5)

| # | Request | Question |
| --- | --- | --- |
| 22 | Quote `ZZ-P1` with `"postalCode": 2139` (JSON number); P1 has postal rules `"21"` and `"02"` | Jackson coerces to `"2139"`; Go rejects |
| 23 | Quote with `"UnitPrice"` instead of `"unitPrice"` on one line | Go binds it, Jackson ignores it (then `unitPrice` is missing) |
| 24 | Quote with an unknown extra field and a duplicated `quantity` key (`1` then `3`) | Ignored? Which duplicate wins? |
| 25 | Quote with `category` `"food"` | Case sensitivity on the quote side |
| 26 | Quote with an unknown `category` | D22 covers uploads only; what do quotes do? |

### F. Rule semantics in `ZZ-P1`: D3, D9, D12, D14, D18 (8)

| # | Request | Question |
| --- | --- | --- |
| 27 | Quote: lines that hit equal-priority rules within one group and across `g-tax`/`g-exempt`/`g-surcharge`, built so the port's result changes when the order changes (confirm with the port by reversing the upload locally) | D3: upload, name, or hash order? |
| 28 | Quote: lines whose rules use an unknown field with `==`, `!=`, `== null`, `\|\|` with a true clause, and `!(…)`; and lines without `exemptionCode` whose rules test `exemptionCode == null` and `exemptionCode != 'X'` | D9 per operator; absent optional field. If the whole quote fails, that alone says "throws"; split with the reserve |
| 29 | Quote: two lines each under a cap whose sum is over it; one line with quantity 5 where the unit tax is under the cap and the line tax is over; one line hit by two capped rules | D14: per unit, per line, per rule, or per order |
| 30 | Quote: exemption codes `resale`, `" RESALE "`, `"\tRESALE\n"`, `" RESALE"`, `"RESALE\u0001"`, `"RESALE "`, and a code containing `I` written with `İ` | D12: which trim and which case folding |
| 31 | Quote with `postalCode` `"sw1a 1aa"` against a rule prefix `"SW1A1"` | D18: normalization of case and spaces |
| 32 | Quote with `postalCode` `"94105-1234"` against a rule prefix `"94105"` | ZIP+4 |
| 33 | Quote with `postalCode` `"9410"` (shorter than the prefix `"94105"`) | Which side is the prefix of which |
| 34 | Quote with `postalCode` `"94105"` where rules `"941"` and `"9410"` both match | Longest prefix, priority, or both apply? |

### G. Uploads: D15, D22, validation, replace semantics (7)

| # | Request | Question |
| --- | --- | --- |
| 35 | `PUT /v1/rules/ZZ-P2`: one normal group and one group with no rules | D15: accepted or rejected? |
| 36 | Quote `ZZ-P2` (only if #35 was accepted; otherwise the request goes to the reserve) | Is the empty group really ignored? |
| 37 | `PUT /v1/rules/ZZ-P3` with an unknown category | D22 |
| 38 | `PUT /v1/rules/ZZ-P4` with a syntactically invalid `match` | Rejected at upload, or accepted and failing at quote time? This decides how production configs migrate |
| 39 | Quote `ZZ-P4` (only if #38 was accepted) | What the failure looks like at quote time |
| 40 | `PUT /v1/rules/ZZ-P1` with group `g-surcharge` removed | Accepted? |
| 41 | Quote `ZZ-P1` hitting a `g-surcharge` rule | PUT replaces the jurisdiction, or merges groups? |

### H. Request shape (2)

| # | Request | Question |
| --- | --- | --- |
| 42 | Quote `ZZ-P1` with `lines: []` | Empty order |
| 43 | Quote `ZZ-P1` with two lines sharing one `sku` | Merged, kept as two, or rejected? With `arrays: sort` this was never observable |

### Reserve (7)

Used, in this order of priority: fallback jurisdiction if #1 is rejected; splitting a packed request that returned an
error (#13, #17, #28); re-sending after a transport failure; a quote for a jurisdiction with no rules; a follow-up on
the largest surprise (for example, if #2 shows half-even in more categories, a confirming quote in a second real
jurisdiction). Unused reserve is not spent.

## 5. What each outcome changes

| If the legacy shows | Then |
| --- | --- |
| Half-even (or half-up) outside the three D7 categories, or per jurisdiction | Rewrite D7 from #2–#5; re-check every golden with a tie |
| `double` rounding (#2 trap) | Port must reproduce `double` arithmetic for the affected path; block cutover until done |
| Drop of quantity-0 lines outside the three D21 jurisdictions, or no drop in `US-TX` today | Rewrite D21 around the config trigger; ask the rule owners what those configs had in common |
| `!=` on an unknown or absent field applies the rule | Rewrite D9; scan production configs for such expressions (step 2.3) |
| Different trim or case folding | Port D12 to Java `trim()` and `equalsIgnoreCase` semantics exactly |
| Cap other than per line | Rewrite D14 |
| Invalid expression accepted at upload (#38) | Port must accept it too, or every production config is validated before cutover |
| A Jackson coercion the port does not do (#13–#16, #18–#24) | Match it only where step 2.3 shows production sends that form; otherwise document the difference for clients |
| Strict comparison (step 2.1) shows format diffs | Decide per field whether clients depend on it; the default is to match the legacy bytes |

Severity: a difference in a tax amount for an input production sends blocks cutover. A difference in format, or for an
input production never sends, is documented and accepted by the owners of the affected clients.

## 6. Recommended beyond the round

50 probes cannot cover the input space; production traffic can. Before cutover:

- **Shadow run.** Send a copy of production `POST /v1/tax/quote` traffic to the port for at least a week, compare with
  the strict comparator, and triage every diff. Confirm first that a quote has no side effects in the legacy service.
- **Cutover gate:** zero unexplained amount diffs in the shadow run; every production rule config accepted by the
  port; this round's divergences resolved per §5.
- **Rollback:** a switch back to the legacy service that works without a deploy, kept for an agreed period after
  cutover, with the legacy rules kept in sync during that period.
