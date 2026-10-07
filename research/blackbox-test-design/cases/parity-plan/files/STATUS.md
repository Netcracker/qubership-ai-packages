# tax-engine port: status before cutover

We are replacing the legacy `tax-engine` (Java 11, Spring Boot, Jackson, PostgreSQL; source owned by another
department, we cannot see it) with a Go port. The legacy service runs on a stand we can send requests to; the stand
is shared with the integration tests of two other teams. Each round of requests needs a change ticket and takes about
a week, so we get one more round before cutover.

## What the service does

`POST /v1/tax/quote` takes an order (lines with `sku`, `category`, `quantity`, `unitPrice`, optional `exemptionCode`;
a `shipTo` address with `country`, `region`, `postalCode`) and returns per-line tax and a total. Tax rules come from a
configuration upload (`PUT /v1/rules/{jurisdiction}`): a list of rule groups, each with rules that have a `name`, a
`match` expression, a `rate`, a `priority` and an optional `cap`.

## How we test the port

- **Parity suite**: 1,812 recorded request/response pairs from the legacy stand (rounds 1 to 9). The Go port matches
  all of them, compared with `parity/comparator.yaml` (below).
- **Mutation testing** (go-mutesting) on the port: 94% score; every survivor reviewed.
- **Property-based tests** with `rapid` (generators in `port/internal/gen`), checking invariants such as "total equals
  the sum of line taxes" and "tax is never negative".
- **Pairwise coverage** over `jurisdiction × category × exemption kind × priority class`: 100%.

`parity/comparator.yaml`:

```yaml
normalize:
  arrays: sort
  nulls: drop
  numbers: decimal-value
ignore:
  headers: [X-Trace, Date]
  body: [$.error.message]
```

## Decisions in the port (excerpt from `decisions.md`)

| Id | Decision | Source |
| --- | --- | --- |
| D3 | Rules are applied by ascending `priority`; equal priorities keep upload order | design doc §4.2 |
| D7 | Rounding is half-up to 2 decimals, except for categories `FOOD`, `BOOKS` and `KIDS_CLOTHING`, which round half-even | goldens r4-17, r6-02, r8-33 |
| D9 | A `match` expression that references an unknown field makes the rule not apply | golden r5-11 |
| D12 | An `exemptionCode` is compared case-insensitively after trimming spaces | design doc §5.1 |
| D14 | `cap` applies per line | golden r3-40 |
| D15 | A rule group with no rules is ignored | design doc §4.4 |
| D18 | `postalCode` is matched as a string prefix | goldens r2-05, r2-06 |
| D21 | A line whose `quantity` is 0 gets tax 0 and is kept in the response, except in jurisdictions `CA-QC`, `DE-BY` and `US-TX`, where it is dropped | goldens r7-08, r8-12, r9-21 |
| D22 | An upload with an unknown `category` value is rejected with 400 | design doc §6 |
| D25 | `unitPrice` may be a JSON number or a numeric string | golden r1-02 |

The design doc is the port team's own document, written from interviews with former users of the legacy service.

## Question

The suite is green and we cut over in three weeks. Where could we still be blind, and what should the last round of
at most 50 requests to the legacy stand be? We need a concrete plan we can file as the change ticket.
