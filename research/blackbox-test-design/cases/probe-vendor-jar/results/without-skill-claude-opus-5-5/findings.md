# discount-engine.jar: behaviour vs. documentation

The jar was tested only through its CLI (`java -jar discount-engine.jar config.json request.json`), with no
decompiling. 54 of the 60 allowed runs were used. Every run used a fresh working directory, so `crm-calls.log` holds
only that run's lookups. The full log of each run (config, request, stdout, stderr, CRM log) is in
`findings-runs.log`. Run numbers below refer to that log.

Unless stated otherwise, the requests use customer `c9` (an unknown customer), and configs have `"default": 5` and
one rule with `"discount": 10`.

## A. Contradictions of the documentation

These must be decided explicitly for the reimplementation: copy the jar, or follow the docs.

### A1. The highest discount among matching rules wins, not the first matching rule

The docs say: "The first rule whose conditions all hold gives the discount." In fact, every rule is evaluated and the
largest discount among the matching rules is returned. Rule order does not matter.

| Run | Rules (in order), all matching | Docs predict | Actual |
| --- | --- | --- | --- |
| 1 | README example config and request verbatim (`big-orders` 10, then `vip` 20; c1, amount 120) | 10 | **20** |
| 12 | three rules `amount gte 1` with discounts 10, 30, 20 | 10 | **30** |
| 13 | `amount gte 1` → 20, then `tier eq gold` → 10 (c1) | 20 | 20 |

Run 12 rules out "the last match wins" (that would give 20). Run 13 rules out "tier rules take priority" (that would
give 10). The default does not enter the maximum: with `default: 50` and a matching rule of 10, the result is 10
(run 14).

The README's own example shows the difference: it returns 20, not 10.

### A2. CRM unavailable: the whole result becomes 0, not "skip tier rules"

The docs say: "If the CRM is unavailable, rules with a `tier` condition are skipped." In fact, as soon as a CRM lookup
fails, the engine prints `{"discount": 0}`. That discards matching non-tier rules and the configured default. Exit
code is 0 and nothing is written to stderr, so the failure is silent.

| Run | Customer | Rules | Docs predict | Actual |
| --- | --- | --- | --- | --- |
| 23 | x1 | `tier eq gold` → 10 | 5 (default) | **0** |
| 22 | x1 | `tier ne gold` → 10 | 5 (default) | **0** |
| 28 | x1 | `amount gte 1` → 30, then `tier eq gold` → 10 | 30 | **0** |
| 29 | x1 | `tier eq gold` → 10, then `amount gte 1` → 30 | 30 | **0** |
| 36 | x1 | `[amount gte 1000, tier eq gold]` → 10, then `amount gte 1` → 30 | 30 | 30 |

What triggers it is an actual lookup, not the `x` id. In run 36 the tier condition was never evaluated (see B1), the
CRM was not called, and the result was normal.

### A3. Amount `eq`/`ne` depend on how the number is written ("compared numerically" holds only for `gte`/`lte`)

`gte`/`lte` really are numeric. Runs 6 (9 ≥ 100 → false), 37 (1000 ≤ 200 → false), 17 (99.7 ≥ 99.5 → true) and
18 (99.99 ≥ 100 → false) all rule out string comparison. But `eq`/`ne` compare the value together with its number of
decimal places: `100` ≠ `100.0`. Leading zeros are ignored.

| Run | Config value | Request amount | Op | Numeric answer | Actual |
| --- | --- | --- | --- | --- | --- |
| 11 | `"100"` | `100` | eq | match | match (10) |
| 9 | `"100"` | `100.0` | eq | match | **no match (5)** |
| 16 | `"100"` | `100.0` | ne | no match | **match (10)** |
| 54 | `"100.0"` | `100.00` | eq | match | **no match (5)** |
| 15 | `"100.0"` | `100.0` | eq | match | match (10) |
| 27 | `"0100"` | `100` | eq | match | match (10) |

This matches Java `BigDecimal.equals` (value and scale) for `eq`/`ne`, and `compareTo` for `gte`/`lte`. The stack
trace in run 52 shows that amounts are parsed with `java.math.BigDecimal`.

## B. Undocumented behaviour (docs are silent; a reimplementation must choose)

### B1. Conditions short-circuit left to right, and this changes CRM traffic and the outcome

The conditions of a rule are evaluated in order, and evaluation stops at the first false one. A `tier` condition after
a false condition makes no CRM call (run 26: `[amount gte 1000, tier eq gold]`, c1 → no `crm-calls.log`). With the
order reversed, the CRM is called (run 30). Together with A2, condition order decides whether a CRM outage zeroes the
result (runs 36 vs. 23).

### B2. The CRM is called once per evaluated tier condition, with no caching, even when the result can't change

- Two tier rules → `lookup c1` logged twice (run 20). The same happens for c2 (run 43).
- Because every rule is evaluated (A1), the tier rule in the README example triggers a lookup even though a rule
  above it already matched (run 1). Under the documented first-match behaviour, no call would happen.
- Requests without any tier rule make no CRM call (runs 3–19 and others), as documented.
- `crm-calls.log` is appended to, not truncated (run 53: a pre-existing line was kept), as documented.

### B3. Missing request fields make every condition on them false, including `ne`

| Run | Missing key | Condition | Result |
| --- | --- | --- | --- |
| 31 | `coupon` | `coupon ne save10` | false (5) |
| 39 | `categories` | `category ne toys` | false (5) |
| 38 | `amount` | `amount lte 100` | false (5) |
| 25 | `customerId` | `tier eq gold` | false (5); the CRM **is** called with an empty id (`lookup `) |

### B4. Unknown customers: every tier condition is false, including `ne`

`tier ne gold` for unknown customer c9 → no match (run 21). The lookup is logged and the result is not zeroed (unlike
A2).

### B5. Case and whitespace handling beyond the documented coupon rule

- Tier values are case-insensitive: `tier eq GOLD` matches c1 (run 24).
- Category values are case-insensitive: `category eq Toys` matches `"books,toys"` (run 32). The docs mention case
  insensitivity only for coupons.
- Coupons are trimmed: `" SAVE10 "` matches `coupon eq SAVE10` (run 51). Coupon `eq`/`ne` are case-insensitive as
  documented (runs 4 and 5).
- Categories are **not** trimmed: `"books, toys"` does not match `category eq toys` (run 33).
- Category matching is exact per element, not by substring: `category eq toy` does not match `"books,toys"` (run 35).
  `category ne toys` is false when the order has toys (run 34).
- Customer ids are case-sensitive. `C1` is an unknown customer (run 46). `X1` is an unknown customer, **not** "CRM
  unavailable" (run 45). Only a lowercase `x` prefix triggers A2.

### B6. Discounts are truncated to an integer and not clamped

- `discount: 12.5` → 12 (run 41). `discount: 12.7` → 12 (run 44), so it truncates rather than rounds.
- `discount: 150` → 150 (run 42). There is no 0–100 bound.

### B7. Invalid or unsupported config is ignored silently

- Unknown operator (`amount gt 10`) → the condition is false, no error (run 47).
- Unknown field (`country eq de`) → false, no error (run 48).
- An operator not listed for the field (`coupon gte A`) → false (run 49).
- A rule with an empty `when` list always matches (run 40).
- A condition `value` given as a JSON number (`100`) instead of a string works (run 50).
- A request `amount` given as a string (`"120"`) is accepted and compared numerically (run 19).

### B8. A non-numeric amount crashes the engine

`"amount": "abc"` with an amount condition → exit code 1, uncaught `java.lang.NumberFormatException` stack trace on
stderr, nothing on stdout (run 52).

## C. Confirmed as documented

- If no rule matches and `default` is omitted, the result is 0 (run 3).
- Coupon `eq`/`ne` are case-insensitive (runs 4 and 5).
- `gte`/`lte` are inclusive at the boundary (runs 7 and 8) and numeric (runs 6, 17, 18, 37).
- `category eq` holds when the order has the category (run 10).
- Known tiers: c1 gold (runs 1 and 24), c2 silver (run 43).
- A CRM lookup happens only for rules that have a tier condition, and the log is appended to (B2).
- Output format: `{"discount":N}`, with N an integer.

## Not tested (for lack of runs or of relevance)

- What happens with ties in discount. The output can't show which rule won, and only the number matters.
- c3/bronze specifically. Only c1 and c2 were used for positive tier matches.
- Malformed JSON, a missing `rules` key, and `categories` given as a JSON array.
- Whether category case-insensitivity also applies when the request side is uppercase. Run 32 tested only an uppercase
  config value.
