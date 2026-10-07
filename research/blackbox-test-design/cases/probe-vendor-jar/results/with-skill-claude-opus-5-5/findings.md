# discount-engine.jar: where its behaviour differs from README.md

I treated the jar as a black box and only ran its CLI (`java -jar discount-engine.jar config.json request.json`). Each
run used a fresh working directory, so every `crm-calls.log` belongs to exactly one run. The jar was run 58 times out of a
budget of 60, on OpenJDK 21.0.9 (Corretto). Runs #56 and #57 repeated runs #1 and #9 at the end of the session and gave
identical answers, so the engine behaved the same from start to finish.

Unless a finding says otherwise, configs use `default: 5` and give each rule its own discount, so the output shows which
rule fired. Run numbers (#N) point to the full log in the appendix.

Each claim is labelled:
- **Observed**: a run shows it directly.
- **Inferred**: it follows from runs under a stated assumption.
- **Hypothesis**: no run has tested it yet.

## A. Contradictions of the README

### A1. The highest matching discount wins, not the first matching rule (Observed)
The README says the first rule whose conditions all hold gives the discount. In fact the engine checks every rule and
returns the largest discount among those that match.

| # | Rules (in listed order) | Request | Out |
|---|---|---|---|
| 1 | README example: big-orders (amount gte 100 → 10), vip (tier eq gold → 20) | README example request (c1, 120) | **20** (README implies 10) |
| 4 | amount≥100 → 10, coupon eq SAVE10 → 20 | both hold | 20 |
| 5 | amount≥100 → 20, coupon eq SAVE10 → 10 | both hold | 20 |
| 41 | amount≥100 → 2 (default 5) | holds | 2 |

- Runs #4 and #5 rule out "last match wins".
- Run #41 shows that `default` is only a fallback. A matching rule below the default still wins, so the result is not
  max(default, rules).
- Every rule is evaluated even after an earlier rule matched. In #6 (amount → 20 listed first, tier → 10 second) the CRM
  was still called.

### A2. If the CRM is unavailable, the whole result becomes 0 (Observed)
The README says rules with a `tier` condition are skipped. In fact, as soon as a tier lookup fails, the engine returns
`{"discount":0}` with exit code 0. Every other rule is discarded, and so is `default`.

| # | Setup | Out | CRM log |
|---|---|---|---|
| 13 | amount≥100 → 10 (holds), tier eq gold → 30; customer `x9` | **0** (README: 10) | lookup x9 |
| 10 | same, but tier **ne** gold | **0** | lookup x9 |
| 15 | only tier eq gold → 30; customer `x9` | **0** (README: default 5) | lookup x9 |
| 44 | two tier rules; customer `x9` | 0 | lookup x9 (**one** call: evaluation stops at the first failure) |
| 14 | amount≥100 → 10; second rule `amount≥1000 AND tier eq gold` | **10** | none (no lookup was made, so no failure) |

Run #14 shows that the outcome depends on whether a lookup actually happens. Short-circuiting (B1) decides that.

Only ids that start with a lowercase `x` make the CRM unavailable. `X9` was treated as an unknown customer (#51:
default 5, lookup X9).

### A3. Amount `eq`/`ne` depend on how many decimal places are written (Observed)
The README says amounts are compared numerically. That holds for `gte`/`lte`. For `eq`/`ne`, though, numbers with the
same value but a different number of decimal places count as different.

| # | Condition | Request amount | Out | Numeric expectation |
|---|---|---|---|---|
| 26 | eq "100" | 100 | 30 (match) | match |
| 27 | eq "+100" | 100 | 30 (match) | match. So it is not a plain text comparison |
| 25 | eq "100.0" | 100 | 5 (no match) | **match** |
| 28 | eq "100" | 100.0 | 5 (no match) | **match** |
| 29 | eq "100.5" | 100.50 | 5 (no match) | **match** |
| 30 | ne "100.0" | 100 | 30 (holds) | **does not hold** |
| 31 | lte "100.0" | 100 | 30 (holds) | holds |

**Mechanism (inferred):** `eq` uses `BigDecimal.equals`, which compares scale (the number of decimal places), while
`gte`/`lte` use `compareTo`. The request amount keeps the scale it was written with in the JSON. Run #54's stack trace
shows that the config value is parsed with `new BigDecimal(String)`. #27 rules out plain text equality. #45 rules out a
`double` conversion: 99.99999999999999999 is not ≥ 100, although as a `double` it would round to 100.

### A4. Coupon matching trims whitespace, but only ASCII whitespace (Observed)
The README only mentions case-insensitivity. The engine also trims the coupon.

| # | Config | Request coupon | Out |
|---|---|---|---|
| 18 | eq "save10" | "SAVE10" | 30 (case-insensitive, as documented) |
| 19 | ne "save10" | "SAVE10" | 5 (ne is case-insensitive too) |
| 20 | eq "save10" | " save10 " | **30**: surrounding spaces are ignored |
| 53 | eq "save10" | " SAVE10" (no-break space) | 5: not trimmed |
| 58 | eq "save10" | " SAVE10" (em space) | 5: not trimmed |

**Mechanism (inferred):** Java `String.trim()`, which strips characters ≤ U+0020. `strip()` would have removed the em
space in #58. I did not test whether the config side is trimmed too.

### A5. Category matching is case-insensitive, and items are not trimmed (Observed)
The README says nothing about case or whitespace for categories. Unlike coupons, category items are **not** trimmed.

| # | Condition | Request categories | Out |
|---|---|---|---|
| 38 | eq toys | "books,toys" | 30 (control: the second item matches) |
| 35 | eq toys | "books, toys" | **5**: " toys" does not match |
| 39 | ne toys | "books, toys" | **30**: the order "lacks" toys |
| 40 | eq books | " books,toys" | **5**: the whole string is not trimmed either |
| 37 | eq books | "Books,toys" | **30**: case-insensitive |
| 36 | eq book | "books,toys" | 5: whole items only, no substring match |
| 34 | ne books | "books,toys" | 5: `ne` means "the order does not have it", as documented |

### A6. A non-numeric amount in the config crashes the run (Observed)
Run #54: one rule used `amount gte "abc"`, and a second, independent coupon rule would have matched. The jar exited
with **code 1** and printed nothing on stdout, only a `java.lang.NumberFormatException` stack trace on stderr (from
`BigDecimal.<init>`, called by `DiscountEngine.holds`). The README does not mention errors, and the good rule's discount
was lost. Because amount conditions are short-circuited (B1), the crash probably happens only when the bad condition is
actually evaluated. That is a hypothesis; I did not test it.

## B. Undocumented behaviour (the README is silent)

### B1. Conditions are short-circuited left to right, and the CRM is called once per evaluated tier condition (Observed)
- #7 `[amount≥100, tier eq gold]` with amount 50: no CRM call.
- #8 `[tier eq gold, amount≥100]` with amount 50: `lookup c1`.
- #9 two tier rules: `lookup c2` twice. Results are not cached.
- #4 and #5, with no tier conditions: no CRM calls, as documented.

The order of conditions matters both for the CRM call log and for A2 (whether an outage zeroes the result).

### B2. Missing fields make both `eq` and `ne` false (Observed)
- #21 coupon ne "save10" with no coupon: 5.
- #33 amount ne "100" with no amount: 5.

An empty string counts as present: #52 coupon `""` ne "save10" gave 30.

### B3. Tier and customer id handling (Observed)
- Tier values compare case-insensitively: #16 eq "GOLD" with c1 gave 30.
- Customer ids are case-sensitive: #17 `C1` is an unknown customer.
- For an unknown customer, `tier ne gold` does **not** hold (#11, c9). Neither `eq` nor `ne` hold for an unknown tier.
- With no `customerId`, the engine still calls the CRM with an empty id (#12, `lookup ` followed by an empty id) and
  treats the customer as unknown.

### B4. Fractional discounts are truncated (Observed)
- Discount 12.5 gave 12 (#46).
- Discount 12.7 gave 12 (#49). So it truncates rather than rounds.
- Default 7.9 gave 7 (#55).
- Output is always an integer. I did not test negative values, so floor and truncation toward zero are both still
  possible.

### B5. Other observations (all Observed)
- An unknown `op` (#47, `gt`) or an unknown `field` (#48, `country`) is silently false. There is no error.
- An empty `when: []` always matches (#43).
- Discounts are not capped: 150 gave 150 (#50).
- A request amount given as a JSON string works numerically (#32, `"120"` gte 100).
- With `default` omitted the result is 0, as documented (#42).

## C. Open hypotheses (not tested; budget left: 2 runs)
- A tier rule that matches but has a lower discount: with all rules evaluated, its lookup still happens (#6), so A2
  applies even when the tier rule could not have won.
- Whether the config coupon or category values are trimmed or lower-cased (only the request side was tested).
- A trailing comma or empty item in `categories` (`"books,"`, `eq ""`). Java `split` drops trailing empty items.
- A `null` value for a request field, and a request coupon sent as a JSON number.
- A bad config number in a condition that is never evaluated (does A6 still crash?).
- Duplicate rule names, and two tier conditions in one rule (expected: 2 lookups).
- Negative discounts (truncate vs floor).
- Whether case-insensitivity depends on the locale (`toLowerCase()` vs `equalsIgnoreCase`, e.g. the Turkish dotless i).

## Appendix: every run

The CRM column shows the contents of `crm-calls.log` (`—` means the file was not created).

| # | Probe | config.json | request.json | stdout | CRM |
|---|---|---|---|---|---|
| 1 | readme-example | `{"default":5,"rules":[{"name":"big-orders","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"vip","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId": "c1", "coupon": "SAVE10", "amount": 120, "categories": "books,toys"}` | `{"discount":20}` | lookup c1 |
| 2 | readme-small-gold | `{"default":5,"rules":[{"name":"big-orders","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"vip","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId": "c1", "amount": 50}` | `{"discount":20}` | lookup c1 |
| 3 | readme-small-silver | `{"default":5,"rules":[{"name":"big-orders","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"vip","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId": "c2", "amount": 50}` | `{"discount":5}` | lookup c2 |
| 4 | order-two-plain-lowfirst | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"b","when":[{"field":"coupon","op":"eq","value":"SAVE10"}],"discount":20}]}` | `{"customerId":"c3","coupon":"SAVE10","amount":120}` | `{"discount":20}` | — |
| 5 | order-two-plain-highfirst | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":20},{"name":"b","when":[{"field":"coupon","op":"eq","value":"SAVE10"}],"discount":10}]}` | `{"customerId":"c3","coupon":"SAVE10","amount":120}` | `{"discount":20}` | — |
| 6 | order-tier-second-lower | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":20},{"name":"vip","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":10}]}` | `{"customerId":"c1","amount":120}` | `{"discount":20}` | lookup c1 |
| 7 | crm-after-failing-cond | `{"default":5,"rules":[{"name":"r","when":[{"field":"amount","op":"gte","value":"100"},{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId":"c1","amount":50}` | `{"discount":5}` | — |
| 8 | crm-before-failing-cond | `{"default":5,"rules":[{"name":"r","when":[{"field":"tier","op":"eq","value":"gold"},{"field":"amount","op":"gte","value":"100"}],"discount":20}]}` | `{"customerId":"c1","amount":50}` | `{"discount":5}` | lookup c1 |
| 9 | crm-two-tier-rules | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20},{"name":"s","when":[{"field":"tier","op":"eq","value":"silver"}],"discount":15}]}` | `{"customerId":"c2"}` | `{"discount":15}` | lookup c2;lookup c2 |
| 10 | crm-unavail-ne | `{"default":5,"rules":[{"name":"plain","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"notgold","when":[{"field":"tier","op":"ne","value":"gold"}],"discount":30}]}` | `{"customerId":"x9","amount":120}` | `{"discount":0}` | lookup x9 |
| 11 | crm-unknown-ne | `{"default":5,"rules":[{"name":"plain","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"notgold","when":[{"field":"tier","op":"ne","value":"gold"}],"discount":30}]}` | `{"customerId":"c9","amount":120}` | `{"discount":10}` | lookup c9 |
| 12 | crm-missing-customer-ne | `{"default":5,"rules":[{"name":"plain","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"notgold","when":[{"field":"tier","op":"ne","value":"gold"}],"discount":30}]}` | `{"amount":120}` | `{"discount":10}` | lookup  |
| 13 | crm-unavail-eq-other-rule | `{"default":5,"rules":[{"name":"plain","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":30}]}` | `{"customerId":"x9","amount":120}` | `{"discount":0}` | lookup x9 |
| 14 | crm-unavail-shortcircuited | `{"default":5,"rules":[{"name":"plain","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"g","when":[{"field":"amount","op":"gte","value":"1000"},{"field":"tier","op":"eq","value":"gold"}],"discount":30}]}` | `{"customerId":"x9","amount":120}` | `{"discount":10}` | — |
| 15 | crm-unavail-nomatch-default | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":30}]}` | `{"customerId":"x9","amount":120}` | `{"discount":0}` | lookup x9 |
| 16 | tier-value-uppercase | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"GOLD"}],"discount":30}]}` | `{"customerId":"c1"}` | `{"discount":30}` | lookup c1 |
| 17 | tier-custid-uppercase | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":30}]}` | `{"customerId":"C1"}` | `{"discount":5}` | lookup C1 |
| 18 | coupon-eq-case | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"eq","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":"SAVE10"}` | `{"discount":30}` | — |
| 19 | coupon-ne-case | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"ne","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":"SAVE10"}` | `{"discount":5}` | — |
| 20 | coupon-eq-ws | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"eq","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":" save10 "}` | `{"discount":30}` | — |
| 21 | coupon-ne-missing | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"ne","value":"save10"}],"discount":30}]}` | `{"customerId":"c3"}` | `{"discount":5}` | — |
| 22 | amt-gte-boundary | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":30}` | — |
| 23 | amt-gte-99-lexico | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":99}` | `{"discount":5}` | — |
| 24 | amt-gte-1000 | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"200"}],"discount":30}]}` | `{"customerId":"c3","amount":1000}` | `{"discount":30}` | — |
| 25 | amt-eq-scale | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"eq","value":"100.0"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":5}` | — |
| 26 | amt-eq-control | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"eq","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":30}` | — |
| 27 | amt-eq-plus | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"eq","value":"+100"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":30}` | — |
| 28 | amt-eq-req-decimal | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"eq","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":100.0}` | `{"discount":5}` | — |
| 29 | amt-eq-both-decimal | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"eq","value":"100.5"}],"discount":30}]}` | `{"customerId":"c3","amount":100.50}` | `{"discount":5}` | — |
| 30 | amt-ne-scale | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"ne","value":"100.0"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":30}` | — |
| 31 | amt-lte-scale-boundary | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"lte","value":"100.0"}],"discount":30}]}` | `{"customerId":"c3","amount":100}` | `{"discount":30}` | — |
| 32 | amt-req-string | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":"120"}` | `{"discount":30}` | — |
| 33 | amt-missing-ne | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"ne","value":"100"}],"discount":30}]}` | `{"customerId":"c3"}` | `{"discount":5}` | — |
| 34 | cat-ne-has | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"ne","value":"books"}],"discount":30}]}` | `{"customerId":"c3","categories":"books,toys"}` | `{"discount":5}` | — |
| 35 | cat-eq-second-space | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"eq","value":"toys"}],"discount":30}]}` | `{"customerId":"c3","categories":"books, toys"}` | `{"discount":5}` | — |
| 36 | cat-eq-substring | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"eq","value":"book"}],"discount":30}]}` | `{"customerId":"c3","categories":"books,toys"}` | `{"discount":5}` | — |
| 37 | cat-eq-case | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"eq","value":"books"}],"discount":30}]}` | `{"customerId":"c3","categories":"Books,toys"}` | `{"discount":30}` | — |
| 38 | cat-eq-second-nospace | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"eq","value":"toys"}],"discount":30}]}` | `{"customerId":"c3","categories":"books,toys"}` | `{"discount":30}` | — |
| 39 | cat-ne-space-item | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"ne","value":"toys"}],"discount":30}]}` | `{"customerId":"c3","categories":"books, toys"}` | `{"discount":30}` | — |
| 40 | cat-eq-leading-space-first | `{"default":5,"rules":[{"name":"k","when":[{"field":"category","op":"eq","value":"books"}],"discount":30}]}` | `{"customerId":"c3","categories":" books,toys"}` | `{"discount":5}` | — |
| 41 | match-below-default | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":2}]}` | `{"customerId":"c3","amount":120}` | `{"discount":2}` | — |
| 42 | default-omitted | `{"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":2}]}` | `{"customerId":"c3","amount":50}` | `{"discount":0}` | — |
| 43 | empty-when | `{"default":5,"rules":[{"name":"a","when":[],"discount":7}]}` | `{"customerId":"c3","amount":50}` | `{"discount":7}` | — |
| 44 | crm-unavail-two-tier-rules | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20},{"name":"s","when":[{"field":"tier","op":"eq","value":"silver"}],"discount":15}]}` | `{"customerId":"x9"}` | `{"discount":0}` | lookup x9 |
| 45 | amt-precision | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":99.99999999999999999}` | `{"discount":5}` | — |
| 46 | discount-fraction | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":12.5}]}` | `{"customerId":"c3","amount":120}` | `{"discount":12}` | — |
| 47 | unknown-op | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gt","value":"100"}],"discount":30}]}` | `{"customerId":"c3","amount":120}` | `{"discount":5}` | — |
| 48 | unknown-field | `{"default":5,"rules":[{"name":"a","when":[{"field":"country","op":"eq","value":"DE"}],"discount":30}]}` | `{"customerId":"c3","amount":120,"country":"DE"}` | `{"discount":5}` | — |
| 49 | discount-fraction-12.7 | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":12.7}]}` | `{"customerId":"c3","amount":120}` | `{"discount":12}` | — |
| 50 | discount-over-100 | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"100"}],"discount":150}]}` | `{"customerId":"c3","amount":120}` | `{"discount":150}` | — |
| 51 | crm-unavail-uppercase-X | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId":"X9"}` | `{"discount":5}` | lookup X9 |
| 52 | coupon-empty-ne | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"ne","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":""}` | `{"discount":30}` | — |
| 53 | coupon-nbsp | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"eq","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":" SAVE10"}` | `{"discount":5}` | — |
| 54 | amt-config-garbage | `{"default":5,"rules":[{"name":"a","when":[{"field":"amount","op":"gte","value":"abc"}],"discount":30},{"name":"b","when":[{"field":"coupon","op":"eq","value":"SAVE10"}],"discount":9}]}` | `{"customerId":"c3","amount":120,"coupon":"SAVE10"}` | `(exit 1, NumberFormatException)` | — |
| 55 | default-fraction | `{"default":7.9,"rules":[]}` | `{"customerId":"c3","amount":120}` | `{"discount":7}` | — |
| 56 | control-replay-1 | `{"default":5,"rules":[{"name":"big-orders","when":[{"field":"amount","op":"gte","value":"100"}],"discount":10},{"name":"vip","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20}]}` | `{"customerId": "c1", "coupon": "SAVE10", "amount": 120, "categories": "books,toys"}` | `{"discount":20}` | lookup c1 |
| 57 | control-replay-9 | `{"default":5,"rules":[{"name":"g","when":[{"field":"tier","op":"eq","value":"gold"}],"discount":20},{"name":"s","when":[{"field":"tier","op":"eq","value":"silver"}],"discount":15}]}` | `{"customerId":"c2"}` | `{"discount":15}` | lookup c2;lookup c2 |
| 58 | coupon-emspace | `{"default":5,"rules":[{"name":"c","when":[{"field":"coupon","op":"eq","value":"save10"}],"discount":30}]}` | `{"customerId":"c3","coupon":" SAVE10"}` | `{"discount":5}` | — |
