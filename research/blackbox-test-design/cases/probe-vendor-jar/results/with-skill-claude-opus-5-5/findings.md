# discount-engine.jar: behaviour vs. README

The jar was treated as a black box and run only through its CLI (`java -jar discount-engine.jar config.json request.json`).
54 of the 60 allowed runs were used.

- Reference: `discount-engine.jar`, sha256 `3d51449345a79e5172dc45b94058961c90c9fd6dc98e384b5483110c719aba76`
- Runtime: OpenJDK 21.0.9 (Corretto), macOS
- Each run used a fresh temporary working directory, so every `crm-calls.log` belongs to exactly one run.
- The raw record of every run (config, request, stdout, stderr, exit code, CRM log) is in `findings-runs.jsonl`.
  The `#n` references below are the `n` field in that file.
- Every run exited with code 0 and wrote nothing to stderr.
- The first run (#1) was repeated as the last run (#53) and gave the same answer, so the engine behaved the same
  throughout.

**Conventions used below.** Unless a finding says otherwise:
- the request is `{"customerId":"c9","coupon":"SAVE10","amount":120,"categories":"books,toys"}`. `c9` is an unknown
  customer.
- the config is `{"default":1,"rules":[{"name":"r","when":[<cond>],"discount":50}]}`.

So `50` means the rule matched and `1` means it did not. `A` means the condition `amount gte "100"`, which this request
always meets.

**Evidence labels:**
- *Observed*: a run shows it directly.
- *Inferred*: follows from runs under the stated assumption.
- *Hypothesis*: not yet separated by any run.

---

## Differences from the documentation

### 1. The highest matching discount wins, not the first matching rule (Observed)

The README says the first rule whose conditions all hold gives the discount. In practice the engine evaluates every
rule and returns the largest discount among those that match.

| # | Rules (in order) | README | Jar |
|---|---|---|---|
| 30 | a: A → 20, b: A → 10 | 20 | 20 |
| 31 | a: A → 10, b: A → 20 | 10 | **20** |
| 52 | a: A → 10, b: A → 30, c: A → 20 | 10 | **30** |
| 1 / 53 | README example config, request `c1`, amount 120 | 10 (big-orders) | **20** (vip) |
| 19 | a: A → 10, t: `tier eq gold` → 20, request `c1` | 10 | **20** |
| 33 | a: A → 20, t: `tier eq gold` → 10, request `c1` | 20 | 20 |

- #31 rules out "first match wins".
- #30 rules out "last match wins".
- #52 rules out both, and also rules out summing.
- #33 rules out "tier rules take priority".

The README's own example therefore gives 20, not 10, for its own sample request.

`default` is not part of the maximum. It applies only when no rule matches: in #34 (`default` 30, one matching rule
→ 10) the jar returned 10.

### 2. Rules with the same `name`: the later one silently replaces the earlier one (Observed)

The README says nothing about rule names. In practice a later rule with the same name removes the earlier rule, even
when the later rule does not match.

| # | Rules | Result if both are kept (max-wins) | Jar |
|---|---|---|---|
| 29 | r: A → 10, r: A → 20 | 20 | 20 |
| 32 | r: A → 20, r: A → 10 | 20 | **10** |
| 50 | r: A → 20, r: `coupon eq NOPE` → 10 | 20 | **1** (default) |

- #50 shows that the first `r` is gone completely, not just outranked.
- Inferred: rules are stored in a map keyed by name, with the last definition winning.

### 3. CRM unavailable: the whole result becomes 0, instead of tier rules being skipped (Observed)

The README says that if the CRM is unavailable, rules with a `tier` condition are skipped. In practice the jar
returns `{"discount": 0}` as soon as a lookup fails. It ignores `default` and ignores other rules that match.

| # | Request | Rules | README | Jar | CRM log |
|---|---|---|---|---|---|
| 23 | `x1` | t: `tier eq gold` → 20, a: A → 10 | 10 | **0** | `lookup x1` |
| 36 | `x1` | a: A → 10, t: `tier eq gold` → 20 | 10 | **0** | `lookup x1` |
| 37 | `x1` | t: `tier eq gold` → 20, default 7 | 7 | **0** | `lookup x1` |
| 22 | `x1` | `tier ne gold` → 50, default 1 | 1 | **0** | `lookup x1` |
| 35 | `x1` | a: A → 10 only (no tier rule) | 10 | 10 | none |
| 38 | `x1` | t: [`amount gte 1000`, `tier eq gold`] → 20, default 7 | 7 | 7 | none |

- The zero result only appears when a lookup actually happens: see #35, and #38, where the lookup was skipped because
  of short-circuiting (finding 5).
- Exit code is 0 and stderr is empty, so callers cannot tell this 0 apart from a real "no discount".

### 4. `amount eq` / `ne` depend on decimal scale, not just numeric value (Observed)

The README says amounts are compared numerically. That holds for `gte` and `lte`, but `eq` treats numbers with
different scale as different.

| # | Condition | Request amount | README | Jar |
|---|---|---|---|---|
| 39 | `eq "100"` | `100` | 50 | 50 |
| 49 | `eq "0100"` | `100` | 50 | 50 |
| 8 | `eq "100"` | `100.0` | 50 | **1** |
| 9 | `eq "100.0"` | `100` | 50 | **1** |
| 40 | `eq "100.5"` | `100.50` (raw JSON text) | 50 | **1** |
| 41 | `ne "100"` | `100.0` | 1 | **50** |

- #49 shows the comparison is not textual: `"0100"` equals `100`.
- #8, #9 and #40 show that scale matters.
- #40 also shows that the request number keeps its original text: if it had been parsed as a `double`, `100.50` would
  have become `100.5` and matched.
- Inferred mechanism: both sides are parsed as `BigDecimal`. `eq`/`ne` use `BigDecimal.equals`, which also compares
  scale, while `gte`/`lte` use `compareTo`.
- The ordering operators really are numeric:
  - #6: `gte "100"` with amount 20 → no match (a text comparison would match).
  - #7: `lte "50"` with amount 100 → no match.
  - #43: `gte "1e2"` with amount 100 → match.
  - #4, #5: both boundaries are inclusive.
  - #10, #11: 99.5 and 99.99 are not ≥ 100.

### 5. CRM lookups are not cached, and they run for every rule (Observed)

The README says only that the CRM is asked "only for rules with a `tier` condition". In practice:

- **Lookups run even after an earlier rule has already matched.** This follows from finding 1, where every rule is
  evaluated. Runs #1, #19 and #33 each log `lookup c1`, although a non-tier rule matched earlier.
- **No caching.** Two tier rules for the same customer cause two lookups: in #21 the log is `lookup c1` twice.
- **Conditions short-circuit left to right inside a rule.** With [`amount gte 1000`, `tier eq gold`] no lookup
  happened (#20, #38).
  - Hypothesis, not tested: putting the tier condition first would make it look up anyway.
- **The lookup happens even without a `customerId`.** In #51, with the key absent, the log is `lookup ` (empty id). The
  customer is treated as unknown and the result is 1.

For the reimplementation, this matters because of finding 3: an unavailable CRM zeroes the result whenever *any*
tier condition is reached, whatever the rule order.

---

## Behaviour the README does not mention (Observed; decide whether to copy it)

| # | Input | Jar | Note |
|---|---|---|---|
| 15 | `category eq "Toys"`, categories `books,toys` | 50 | Categories are case-insensitive. The README only says this for coupons |
| 14 | `category eq "toys"`, categories `"books, toys"` | 1 | Category items are **not** trimmed, so `" toys"` does not equal `"toys"` |
| 48 | `coupon eq "SAVE10"`, coupon `" SAVE10"` | 50 | Coupons **are** trimmed. This is not a substring match: #54, `"XSAVE10"`, gave 1 |
| 46 | `tier eq "GOLD"`, `c1` | 50 | Tier comparison is case-insensitive |
| 24 | `tier ne "gold"`, unknown customer `c9` | 1 | For an unknown customer, `ne` does not hold. Hypothesis: unknown tier is null, and every tier condition is false |
| 47 | `coupon ne "X"`, no `coupon` key | 1 | A missing field makes `ne` false, not true |
| 44 | `amount lte "100"`, no `amount` key | 1 | A missing amount is not treated as 0 |
| 42 | `amount gte "100"`, amount `"120"` (JSON string) | 50 | A numeric string is accepted as the amount |

## Documented behaviour that held (Observed)

- Coupon `eq` and `ne` are case-insensitive (#2, #3).
- Category `eq` means "the order has the category". `ne` means "the order lacks it" (#12, #13, #45), not "some category
  differs". `eq` is not a substring match (#16).
- All conditions in a rule must hold (AND, #25). An empty `when` list always matches (#26).
- If `default` is omitted, the result is 0 (#27).
- Tier lookups return the documented tiers (#17 `c1` = gold, #18 `c2` ≠ gold). A rule with a tier condition triggers
  the lookup, and a config without one does not (#35).

## Not probed (open questions for a later round, 6 runs left)

- Unknown fields or operators, malformed JSON, a non-numeric `value` for amount, and fractional or negative
  `discount` values. These are error-path questions. Not one run checked what the jar does on invalid input.
- The tie-break between two matching rules with equal discounts. It is invisible in the output unless a later
  feature exposes the rule name.
- Whether a condition order of [`tier`, falsy condition] still looks up. This is the twin of #20.
- Case-folding locale (for example Turkish `İ`/`ı` in coupons), other whitespace classes (tab, NBSP) in coupons and
  categories, and empty items in `categories` such as `"books,,toys"`.
- The case of `customerId` (`C1` vs `c1`) as sent to the CRM.
