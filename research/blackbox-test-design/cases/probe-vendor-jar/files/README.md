# Discount engine (vendor documentation)

`discount-engine.jar` computes the discount, in percent, for an order. Run it as:

```bash
java -jar discount-engine.jar config.json request.json
```

It prints `{"discount": N}`.

## Configuration

```json
{
  "default": 5,
  "rules": [
    {"name": "big-orders", "when": [{"field": "amount", "op": "gte", "value": "100"}], "discount": 10},
    {"name": "vip", "when": [{"field": "tier", "op": "eq", "value": "gold"}], "discount": 20}
  ]
}
```

- Rules are evaluated in the order they are listed. The first rule whose conditions all hold gives the discount.
- If no rule matches, `default` applies (0 when omitted).
- A condition has a `field`, an `op` and a `value`.

| Field | Request key | Operators | Notes |
| --- | --- | --- | --- |
| `coupon` | `coupon` | `eq`, `ne` | Coupon codes are case-insensitive |
| `amount` | `amount` | `eq`, `ne`, `gte`, `lte` | Amounts are compared numerically |
| `category` | `categories` (comma-separated) | `eq`, `ne` | `eq` holds when the order has the category |
| `tier` | `customerId` | `eq`, `ne` | The customer's tier is looked up in the CRM |

## Request

```json
{"customerId": "c1", "coupon": "SAVE10", "amount": 120, "categories": "books,toys"}
```

## CRM

The engine asks the CRM for a customer's tier only for rules with a `tier` condition. If the CRM is unavailable, rules
with a `tier` condition are skipped. In this test environment the CRM is a stub: every lookup is appended to
`crm-calls.log` in the working directory. Known customers: `c1` (gold), `c2` (silver), `c3` (bronze). Any customer id
starting with `x` makes the CRM unavailable. Other ids are unknown customers.
