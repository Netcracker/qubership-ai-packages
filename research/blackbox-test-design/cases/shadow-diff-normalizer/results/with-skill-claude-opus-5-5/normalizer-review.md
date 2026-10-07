# Review: `diff-normalizer.yaml`

## Summary

The normalizer gets the diff rate down by turning off comparison of the things a Java 8 → Kotlin port most often
gets wrong: enum spelling, money precision, timestamp format, ids, status codes and headers. With this config,
**"under 1%" doesn't show that the two services match. It shows that whatever differences remain are ones this
normalizer can't see.** Several rules hide differences that clients will notice (`"Shipped"` vs `"SHIPPED"`, 200 vs
201, a missing `Location` header, a different timestamp format). Most rules also apply to every field (`$..*`,
`$..id`, `$..status`). So they hide fields and nested objects the team never looked at, including fields added later.

Don't use this config to decide the read switch-over. The specific changes are below. Most of them come from four
principles:

1. **Measure the noise floor first.** Diff the old service against itself (A/A): mirror each request to two old
   instances, or replay it to one old instance twice. Any difference that shows up in A/A is real noise and can be
   normalized. A difference that shows up only in A/B (old vs new) is a behavior change. Someone has to decide each
   one: fix the new service, or accept it in writing.
2. **For reads, both sides must read the same data.** If the new service reads its own database, filled by mirrored
   writes, then its ids and timestamps *will* differ on GETs, and those rules are hiding a data mismatch, not a
   serialization difference. For the GET comparison, point the new service at the same Oracle data (or a replica of
   it). Then on a GET, `id`, `createdAt` and `updatedAt` must match **exactly**.
3. **Scope every rule to a path, plus a method/route where it applies.** Use no `$..*` and no recursive key-name match
   unless the rule is safe for every field that exists now and every field added later.
4. **Report what each rule absorbed.** For each rule, publish how many responses it changed, next to the raw diff rate
   and the normalized one, per endpoint. When a rule that should be rare starts absorbing 20% of traffic, that's a
   finding.

## Rule-by-rule

Severity is how much harm the rule can hide, given that this diff gates the read switch-over.

| # | Rule | Verdict | Severity |
|---|------|---------|----------|
| 1 | `$..*` `sort_arrays` | Too broad. Keep it for `errors` only, and for line items only if A/A shows their order varies | High |
| 2 | `$..*` `drop_nulls` | Fix the new service to emit nulls instead (parity). At most, list specific fields | Medium |
| 3–4 | `$..createdAt` / `$..updatedAt` `ignore` | Wrong for GETs. Hides format, timezone and precision bugs | **High** |
| 5 | `$..*` `numbers: double` | Wrong tool. Use exact decimal comparison that ignores scale, on money fields only | **High** |
| 6 | `$..status` `case_insensitive` | Remove. This is a contract break; fix the new service | **High** |
| 7 | `$.errors[*].message` `ignore` | Acceptable if error `code`/`field`/count are compared. Report message diffs separately | Low |
| 8 | `$..id` `ignore` | Remove for GETs. For POSTs, check id type/format and that ids are used consistently | **Critical** |
| 9 | `http_status: false` | Remove. Allowlist specific (route, old→new) pairs only after someone decides | **Critical** |
| 10 | `headers: false` | Compare an allowlist of headers that carry meaning | High |
| — | Rule order ("added in the order the noise showed up") | Order changes the result; see below | Medium |

### 1. `sort_arrays` on everything

The comment justifies this for line items and errors. It applies to every array:

- **List endpoints** (`GET /orders?customer=…&sort=…`, search, pagination). If the new service returns the wrong sort
  order, this rule hides it. Pages of results stay comparable element-wise but not order-wise. If a status history,
  shipment timeline or audit trail is an array, its order is the meaning.
- **Line items.** Order is noise only if the old service's order is not deterministic (e.g. an Oracle query without
  `ORDER BY`, or a Java `HashSet`). If old always returns `ORDER BY line_no`, then the new service must too, because a
  UI or an invoice renders that order. Run A/A to find out. Don't assume.
- **Errors.** Order is genuinely unspecified (Hibernate Validator collects violations in a `HashSet`). Sorting is
  right here, but sort by a key: `(field, code)`.

What it should be: `sort_arrays` on `$.errors` by `(field, code)`, and on `$.lineItems` by `lineNumber`/`sku`
**only if A/A shows the order varies**. No other arrays.

### 2. `drop_nulls` on everything

This merges `"discount": null` with an absent `discount`. That matters to JavaScript clients (`'discount' in o`,
`o.discount === null` vs `undefined`) and to schema validators that require the key. The cheapest fix is usually in
the new service, not the normalizer: one Jackson setting gives you old-style output (`default-property-inclusion:
always`, or check where the Kotlin side sets `NON_NULL`/`NON_ABSENT`). Then this rule can go.

If the team accepts the difference instead, list the fields it applies to.

Also be aware:

- With `$..*`, the rule probably also removes `null` *elements* from arrays, which would merge `[null, x]` with
  `[x]`. Check what the tool does.
- Oracle stores `''` as `NULL`, so the old service returns `null` where a Kotlin service with non-null `String` types
  may return `""`. Today that still shows up as a diff, which is correct. When it does, don't add a rule for it. It's
  a real difference for clients doing `if (x == null)`.

### 3–4. Ignoring `createdAt` / `updatedAt`

Timestamps are where a Java 8 → Kotlin port is most likely to differ, and this rule removes them completely:

- **Format.** Java 8 `Date` + Jackson defaults give epoch millis. `java.time` gives ISO-8601 text. Kotlin services
  often differ in offset (`Z` vs `+00:00` vs none) and in fractional digits.
- **Timezone.** The JVM default zone, Oracle `DATE` (no zone) vs `TIMESTAMP WITH TIME ZONE`, and DST.
- **Precision.** Oracle `DATE` truncates to seconds. `TIMESTAMP` gives micro/nanoseconds. The new code may round
  differently.
- `$..` also matches nested `createdAt`s: line items, payments, shipments.

What it should be:

- **GET:** compare exactly. If the formats differ, add a rule that parses both sides to an instant and compares those
  for equality. Report every format difference as its own diff class; consumers parse these strings.
- **POST / PUT responses** for an entity the shadow side just created or changed: check that both are the same JSON
  type and format, and that the value falls within the request's time window. Don't ignore them.

### 5. `numbers: double` on everything

The comment's examples are real old-service behavior: Java's `BigDecimal.toString()` prints `1E+1`, and scale is
kept (`10.10`). But converting to `double` is the wrong way to compare them:

- Integers above 2^53 merge (`9007199254740993` == `9007199254740992`). That matters for long ids, order numbers and
  amounts in minor units.
- Decimals beyond about 15–17 significant digits merge.
- If the comparison uses a tolerance (check the tool), it also hides rounding-mode differences. `HALF_UP` vs
  `HALF_EVEN` on `x.xx5`, or rounding per line vs per total, is exactly the kind of one-cent difference a money diff
  must catch.
- Check what happens to `"10.10"` (string) vs `10.1` (number). That changes the JSON type, and clients care.

What it should be: compare as exact decimals, ignoring scale (`BigDecimal.compareTo == 0`), on money/quantity fields
only. Integers must be equal exactly. Report scale and notation differences (`10.10` vs `10.1`, `1E+1` vs `10`) as a
separate low-severity class, and confirm they're harmless. A client that shows `amount` as text would show "10.1".

### 6. `status` case-insensitive

`"SHIPPED"` → `"Shipped"` is a change to the API contract, not noise. Any client doing `status == "SHIPPED"`, a
`switch` on it, or Jackson deserializing it into a Java enum (case-sensitive by default) will break or fall into a
default branch. It looks like the new service serializes enums with a different naming strategy or a `@JsonValue`.
Fix the new service, and remove this rule.

`$..status` also matches every nested `status` field (payment, shipment, line item), so it hides the same bug there.

### 7. Ignoring `errors[*].message`

This is reasonable if clients don't parse the message text. But keep comparing the number of errors, each error's
`code`/`field`, and the HTTP status (rule 9). Otherwise "an error happened" is the only thing left to compare. Log
message differences to a separate report, so someone can check them once for clients that show or match on the
message.

### 8. Ignoring `$..id`

This is the most dangerous rule.

- **On GETs, ids must be equal.** A different `id` on a GET means the wrong record, the wrong join, or a child
  attached to the wrong parent. "Generates ids differently" can only apply to entities the shadow side created
  itself. If GET ids differ, the two services aren't reading the same data (see principle 2).
- `$..id` matches every nested `id`: line items, addresses, products, customer. With rule 1, a line item can be
  matched against a *different* line item and still pass.
- If the new service uses a different id scheme (UUID vs Oracle sequence number), then the id's JSON type and format
  changed. That's a contract break, and this rule hides it.

What it should be:

- **GET:** compare exactly.
- **POST** (newly created entities only): check the id's type and format. Check that ids are used consistently:
  build an old-id ↔ new-id map from the response, and verify the same entity has the same mapped id everywhere it
  appears in the body, in `Location`, and in any links.

### 9. `http_status: false`

200 vs 201 is a real difference: clients written against the old service may check `== 200`. Turning off the status
comparison entirely also hides:

- 404 vs 200 with an empty or default body;
- 400 vs 422;
- 409 vs 200, where both bodies are the order;
- 500 vs 503;
- 204 vs 200.

After the rules above have stripped messages, ids and timestamps, an error response and a success response can look
much more alike than they should.

What it should be: always compare the status. Add an allowlist of exact `(method, route, old, new)` entries, e.g.
`POST /orders 200→201`. Add an entry only after someone has decided to accept the change (and checked the clients) or
filed a ticket to fix it. For a read switch-over, GETs should have no status entries at all.

### 10. `headers: false`

Compare an allowlist:

- `Content-Type` (media type and charset; `application/json;charset=UTF-8` vs `application/json` is a real Spring
  Boot version difference);
- `Location`;
- `ETag` / `Last-Modified` / `Cache-Control`, if used;
- pagination headers (`Link`, `X-Total-Count`, …);
- `Retry-After`;
- any custom `X-` header a client reads.

Ignore `Date`, `Server`, request/trace ids, `Content-Length`/`Transfer-Encoding`/`Connection`, and `Vary` (only
after checking it).

### Rule order

The file applies rules in the order the noise was discovered. But the order changes the result:

- Sorting happens *before* `id`/`createdAt` are dropped and numbers are canonicalized. So if sorting uses the whole
  element as its key, the two sides sort on values known to differ (ids, `10.10` vs `10.1`). Elements then end up
  matched against the wrong partners, which produces fake diffs and pressure to add more `ignore` rules.
- The canonical order is: remove fields → canonicalize values (nulls, numbers, timestamps) → sort arrays by an
  explicit key.

Confirm how the tool applies rules, with a test (below).

## What else the diff can't see

- **The normalizer itself is untested.** Add tests that feed it pairs differing in one aspect, and assert which ones
  it must *not* merge. Planted bugs make good negative controls:
  - two line items swapped on an endpoint where order matters;
  - `SHIPPED` → `Shipped`;
  - a GET with a different `id`;
  - `10.125` rounded two ways;
  - a 200 that became a 404;
  - an epoch-millis vs ISO `createdAt`;
  - `"10"` vs `10`;
  - `null` vs `""`.

  Each must produce a diff. Run these in CI whenever the YAML changes.
- **The 1% is an average over the traffic mix.** Report it per endpoint and per response class (2xx/4xx/5xx). Rare
  paths can be broken with no effect on the total: cancellations, refunds, partial shipments, multi-currency, large
  orders, the last page of a list, legacy orders with odd data. For those, replay targeted requests in addition to
  the mirrored traffic. Use a clean run of *n* agreeing requests on an endpoint as a bound: it limits that endpoint's
  disagreement rate to about 3/*n* (95%), and only for inputs like the ones sent.
- **Spot-check the raw diff, not only the normalized one.** Each week, take a random sample of normalized-equal pairs
  and look at their raw diff. That's how a rule that's too broad gets noticed.
- **Mirrored writes.** POST/PUT/DELETE responses are comparable only if the shadow side's writes go to isolated
  storage and its downstream calls (payments, notifications, events) are stubbed. Confirm that's the case. A mirrored
  write that reaches shared state duplicates real orders. Response diffs also don't show what was *written*. If writes
  will move later, compare the stored rows and the emitted events too, not just the responses.
- **Record the build.** Store the old and new build/version with each diff batch, so a change in the diff rate can be
  traced to a deploy rather than to traffic.

## Proposed shape (sketch)

```yaml
# Order matters: remove → canonicalize → sort.
rules:
  - match: "$.errors[*].message"
    ignore: true                      # wording only; code/field/count still compared
    report: error-message-wording
  - match: "$..[createdAt,updatedAt]"
    when: { method: [POST, PUT] , created_by_request: true }
    compare_as: timestamp_shape       # same JSON type/format, within request window
  - match: "$..[createdAt,updatedAt]"
    when: { method: GET }
    compare_as: instant               # parse both, compare equality; report format diffs
    report: timestamp-format
  - match: "$..id"
    when: { method: POST, created_by_request: true }
    compare_as: id_mapping            # same type/format, consistent old↔new mapping
  - match: ["$..total", "$..amount", "$..price", "$..discount"]   # explicit list
    numbers: decimal_compare          # BigDecimal.compareTo; never double, never epsilon
    report: number-scale-or-notation
  - match: "$.errors"
    sort_arrays: { key: [field, code] }
  # - match: "$.lineItems"            # only if A/A shows old order is nondeterministic
  #   sort_arrays: { key: [lineNumber] }
compare:
  http_status: true
  http_status_allow: []               # e.g. {method: POST, route: /orders, old: 200, new: 201, ticket: ORD-123}
  headers: [Content-Type, Location, ETag, Cache-Control, Link, X-Total-Count]
```

The `when`, `compare_as` and `report` keys are made up for this sketch. Check what the diff tool supports, and
implement whatever it lacks as a pre-processing step.

The fixes belong in the new service, not here:

- `status` enum spelling;
- `null` vs absent;
- 201 vs 200 (unless someone decides to keep 201).
