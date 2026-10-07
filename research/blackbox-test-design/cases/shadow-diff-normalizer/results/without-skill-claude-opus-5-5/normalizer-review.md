# Review: `diff-normalizer.yaml`

**Verdict: don't use this normalizer as the gate for switching reads over.**
The diff rate will go under 1%, but mostly because several rules hide the
regressions the shadow diff is there to catch, not because the services agree.
Most rules apply to every field (`$..*`, `$..id`, `$..status`) and both
`http_status` and `headers` are switched off. With this setup, an order
with the wrong ids, a `"Shipped"` enum that clients can't parse, a money field
that lost precision, timestamps shifted by a timezone, or a 404 where the old
service returned 200 can all show up as "no diff".

The normalizer should only hide differences that are **encoding-only**: the
same value written differently, where no client can tell them apart. It
must not hide differences in **meaning**: a different value, a different type,
a different enum spelling, a different status code or a different entity. And
when it isn't certain which kind a difference is, it should report it as its
own category instead of folding it into "equal".

Assumptions: I only have the YAML, not the diff engine, so the review assumes
the obvious semantics. Rules run top to bottom, `$..x` is JSONPath recursive
descent (any depth), and `sort_arrays` sorts elements by their serialized
value. If the engine does something different, the findings to recheck are
marked *(engine-dependent)*.

---

## Findings, most severe first

### 1. `$..id` → `ignore` hides wrong-entity bugs, including data leaks — **blocker**

`$..id` matches *every* `id` at any depth: the order id, line item ids,
customer id, product id, shipment id, address id. The stated reason ("new
service generates ids differently") only applies to entities **created by a
mirrored write**. For GETs of existing orders, both services read the same
Oracle rows, so the ids must be byte-identical.

What this hides:
- A bad join or a wrong WHERE clause that returns *another* order's line
  items, or another customer's address. If the content happens to match
  (same SKU, same price), the diff is empty. This is a correctness bug and a
  privacy bug.
- An id type change, such as `12345` vs `"12345"` or numeric vs UUID. That is a
  contract break for every client that stores or compares ids.
- `$..id` also doesn't match `orderId`, `customerId` or `productId`, so the
  rule is inconsistent about which references it hides.

**Do instead:** compare ids strictly on read endpoints. For mirrored writes,
build an id mapping from the create response (old id ↔ new id) and rewrite
the new side's ids through it before comparing. That checks that references
point to the *corresponding* entity instead of discarding them. If a mapping
isn't possible yet, scope the ignore to `POST` responses and the specific
generated paths (e.g. `$.id`, `$.lineItems[*].id` on `POST /orders`), and
nothing else.

Related question to answer before going further: **are writes mirrored into
the same Oracle database?** If they are, every mirrored POST creates a second
order (plus any side effects: payment, email, stock reservation). If the new
service writes to a shadow DB, its reads of those orders will diverge from the
old service's forever after, and that is where the "ids differ" noise really
comes from. In that case, segment mirrored writes and reads of shadow-created
entities into their own bucket instead of ignoring ids globally.

### 2. `compare.http_status: false` hides failures, not just 200 vs 201 — **blocker**

The comment describes 200 vs 201 on POST, but the setting turns off status
comparison everywhere. Hidden cases include:
- 200 vs 404/500 when bodies are empty or both are error bodies. Error
  messages are ignored too (rule 7), so only `errors[*].code` stands between a
  400 and a 500.
- 204 vs 200 on DELETE/PUT, and 200 vs 304 for conditional GETs.
- 409/412 vs 200 for concurrency checks, and 401/403 vs 200 for authorization.
  An authz check the new service forgot shows up as *nothing*.

200 vs 201 itself isn't harmless either: generated clients and some
integrations check `== 201` or `== 200` exactly.

**Do instead:** compare status always. Add one explicit, method- and
route-scoped equivalence (for example `POST /orders: {old: 201, new: 200}`),
report it as its own diff category, and file a ticket to fix it in the new
service before cutover.

### 3. `$..status` → `case_insensitive` hides a contract break — **blocker**

`"SHIPPED"` vs `"Shipped"` is not noise. It is a different enum serialization.
Java clients using Jackson fail on it (`InvalidFormatException`, because enum
deserialization is case-sensitive by default). JS/TS clients doing
`status === 'SHIPPED'` silently take the wrong branch. Most likely the Kotlin
enum is serialized with a `@JsonValue`/`toString()`/`@SerialName` that
differs from the Java `name()`.

`$..status` also matches nested fields (`payment.status`,
`lineItems[*].status`, `shipments[*].status`), and possibly numeric `status`
fields in error payloads.

**Do instead:** remove the rule and fix the new service's enum serialization.
This is exactly the kind of diff the shadow traffic is meant to find.

### 4. `numbers: double` on `$..*` compares money as floating point — **high**

`10.10` vs `10.1` and `1E+1` vs `10` are encoding differences, and that part is
fine. Old Jackson writes `BigDecimal` with its scale preserved, via
`toString()`, which is why `1E+1` appears. Converting to IEEE double to compare
them is wrong, though:

- Values with more than ~15–17 significant digits collapse. Two different
  amounts, or two different 64-bit ids above 2^53 (`9007199254740993` vs
  `9007199254740992`), compare equal.
- It hides the probable *cause* of the `10.10` vs `10.1` diff: the new
  service may map Oracle `NUMBER` to `Double`/`Float` instead of `BigDecimal`.
  That is a real money bug, which shows up later as `0.30000000000000004`,
  wrong rounding, or totals that don't add up.
- *(engine-dependent)* If "numbers" also coerces numeric strings, it hides
  `"10.10"` (string) vs `10.1` (number), which is a type change that breaks
  clients.
- Scale differences (`10.10` vs `10.1`) can matter to clients that display
  the raw value. Check whether any do before treating scale as noise.

**Do instead:** compare numbers as exact decimals (`BigDecimal.compareTo`
semantics: `10.10 == 10.1 == 1.01E+1`, no tolerance), keep JSON types strict
(number vs string still differs), and report "same value, different scale or
notation" as a separate, low-priority category rather than "equal". Confirm
the Kotlin DTOs use `BigDecimal` for money, quantities and rates.

### 5. `$..createdAt` / `$..updatedAt` → `ignore` hides timestamp bugs — **high**

For reads, both services read the same row, so these values should denote the
same instant. Usual Java 8 → Kotlin migration differences:

- **Format.** Jackson serializes `java.util.Date` as epoch milliseconds by
  default (`WRITE_DATES_AS_TIMESTAMPS`). The new service probably writes
  ISO-8601 strings. That changes the JSON type, which is a contract break.
- **Timezone.** Oracle `DATE`/`TIMESTAMP` has no zone. The old service
  interprets it in the JVM default zone, while the new one may use UTC or the
  container's zone. That is an hours-long shift in every timestamp, which is
  a real bug.
- **Precision.** Millis vs micros/nanos (`.123` vs `.123456`) is encoding,
  provided the source column really has that precision.

`$..` also ignores timestamps in line items, shipments and payments, along
with any other `createdAt` added later.

`updatedAt` is also the field that tells you a diff is a **race**, not a bug:
if the order changed between the two mirrored reads, `updatedAt` differs. A
better approach is to *use* `updatedAt` for that. When the two values denote
different instants, classify the whole response as "concurrent modification"
and exclude it from the rate. Don't ignore the field in every response.

**Do instead:** parse both sides to an instant and compare instants, truncated
to the coarser precision if that is justified. Keep reporting
representation differences (epoch number vs ISO string, offset format) as
their own category until you've confirmed clients accept both. Ignore
timestamps only on mirrored creates, where each service generates its own
`now()`, and even there allow only a tolerance (for example ±5 s), not a
full ignore.

### 6. `sort_arrays` on `$..*` hides ordering that is part of the contract — **high**

Order is noise for some arrays (`errors`, maybe `lineItems` if there is no
defined order) and the contract for others:
- **List and search endpoints** (`GET /orders?sort=...`, paged results). A
  missing or different `ORDER BY` in the new service breaks pagination, with
  items skipped or repeated across pages, and this rule hides it completely.
- **History and timeline arrays**: status history, events, price adjustments
  applied in sequence.
- Line items if clients show them in returned order, or if the old service
  sorts them by `lineNumber`.

Note also that Oracle doesn't guarantee row order without `ORDER BY`. If the
*old* service relies on implicit order, both sides are nondeterministic. That
is worth knowing, but it means "fix it with an ORDER BY", not "sort
everything".

**Do instead:** sort only named arrays whose order isn't specified, and sort
by a key (`errors` by `code`+`field`, `lineItems` by `lineNumber`/`sku`),
not by whole-element content. Leave all other arrays order-sensitive.

### 7. Rule order: sorting runs before the other normalizations — **medium**

The file header says rules were "added in the order the noise showed up", and
it shows. `sort_arrays` runs first, on raw values, before nulls are dropped,
ids and timestamps removed, numbers normalized, or case folded. If elements
sort by content *(engine-dependent)*, two arrays that are equal after
normalization can still sort differently (by differing ids or timestamps,
`10.10` vs `10.1`, or a null key present on one side only). The result is
spurious diffs, which then push the team to add more ignores.

**Do instead:** put value normalization first, then removals, then keyed
sorting last. Better still, make the engine apply rules in a fixed phase
order regardless of where they appear in the file.

### 8. `drop_nulls` on `$..*` is too broad — **medium**

`"discount": null` vs absent is a classic Jackson-inclusion difference, and
normalizing it is reasonable if clients don't care. Applied to every field,
though:
- It hides `null` vs absent in fields where a client distinguishes "known to
  be empty" from "not provided". For example, PATCH-style semantics, or strict
  deserializers (Kotlin non-null types with no default, JSON Schema
  `required`) that fail on a missing key.
- *(engine-dependent)* If it also drops null *array elements*, it hides
  `[a, null, b]` vs `[a, b]`.
- If an object becomes `{}` after dropping nulls, it may then differ from
  absent. That pressure leads to an "empty object = absent" rule next, and
  then `[]` vs absent. Each of those is a real contract difference.

**Do instead:** scope it to the specific fields observed (start with
`discount`), or fix it at the source: decide which inclusion policy is the
contract and configure the new service's serializer (`@JsonInclude` /
`explicitNulls`) to match. Matching the old service is safest during the
migration.

### 9. `$.errors[*].message` → `ignore` is acceptable, if `code` is compared — **low**

Human-readable wording is legitimately noise. Make sure the rest of each
error *is* compared: `code`, `field`/`path`, the number of errors, and the
HTTP status (see #2). Because messages, statuses and order are all ignored
today, two completely different validation failures can compare equal. Log a
sample of message pairs anyway, because messages sometimes embed values
(limits, ids) that clients parse.

### 10. `compare.headers: false` — **medium**

Some headers are part of the contract and should be compared, with
normalization:
- `Content-Type`: compare the media type. `application/json;charset=UTF-8`
  vs `application/json` is encoding, but `text/plain` vs `application/json` is
  not.
- `Location` on 201 responses, through the id mapping from #1.
- `ETag` / `Last-Modified` presence, `Cache-Control`, `Vary`.
- Pagination headers (`Link`, `X-Total-Count`), `Retry-After`,
  `WWW-Authenticate`, CORS headers if browsers call the service directly.

Ignore `Date`, `Server`, trace and request ids, and `Content-Length`. The
length follows from the body, which is already compared.

---

## Problems with the "< 1%" target itself

- **1% of what?** Diffs concentrate in low-volume, high-value endpoints such as
  cancellations, refunds and order edits. Those can be 100% broken and still
  be well under 1% of total traffic, which is dominated by `GET /orders/{id}`.
  Report the rate **per endpoint and method**, and require every remaining
  diff *class* to be explained, not a global percentage.
- **No visibility into what was suppressed.** Make each rule report how
  many responses it changed and keep the raw (pre-normalization) diff. If
  `$..id` ignore fires on 20% of GET responses, that is a finding, not noise.
  Check per-rule hit counts in review before trusting the headline number.
- **Zero tolerance for certain fields.** Money amounts, totals, currency,
  quantities, order status, customer/owner ids, and HTTP status on
  error-vs-success should be exact match, with no rule allowed to touch them
  except decimal-equality normalization.
- **Races.** Mirrored reads run at slightly different times, so some diffs are
  real state changes. Classify them (via `updatedAt`/version, or by
  re-fetching both sides on diff) instead of weakening field comparisons.
- **Seed the check with known bugs.** Replay a few responses with deliberately
  injected regressions (wrong line item id, `"Shipped"` casing, a 404, a
  timezone-shifted timestamp, a money value off by 0.01) and confirm the
  normalizer reports every one of them. Today it would report none of the
  first four.

---

## What the normalizer *should* normalize (sketch)

Syntax below extends the existing file's style. Options like `sort_by`,
`numbers: decimal`, `timestamps: instant` and `when:` are what the engine
needs to support; add them if it doesn't.

```yaml
rules:
  # 1. Value encoding — same value, different spelling. Strict JSON types.
  - match: ["$..total", "$..subtotal", "$..price", "$..amount", "$..discount", "$..tax", "$..quantity"]
    numbers: decimal              # BigDecimal.compareTo; no double, no tolerance
    report_as: "number-scale"     # still counted, separately
  - match: ["$..createdAt", "$..updatedAt"]
    timestamps: instant           # parse to instant; precision: millis
    report_as: "timestamp-format"

  # 2. Known inclusion-policy difference — scoped, pending a serializer fix.
  - match: "$..discount"
    drop_nulls: true

  # 3. Genuinely non-deterministic values — only where they really are.
  - when: { method: POST, path: "/orders" }
    match: ["$.id", "$.lineItems[*].id"]
    id_mapping: order             # rewrite new ids to old via the mapping; don't ignore
  - when: { method: POST, path: "/orders" }
    match: ["$.createdAt", "$.updatedAt"]
    tolerance: 5s

  # 4. Human text.
  - match: "$.errors[*].message"
    ignore: true

  # 5. Ordering — last, keyed, only where order is unspecified.
  - match: "$.errors"
    sort_by: [code, field]
  # - match: "$.lineItems"        # only if confirmed order isn't part of the contract
  #   sort_by: [lineNumber]

compare:
  http_status: true
  status_equivalences:            # explicit, reported, ticketed for removal
    - { method: POST, path: "/orders", old: 201, new: 200 }
  headers:
    compare: [Content-Type, Location, ETag, Cache-Control, Link, X-Total-Count, Retry-After]
    normalize: { Content-Type: media-type-only }
  classify:
    concurrent_modification: "$.updatedAt"   # differing instants → bucket as race, exclude from rate
```

## Must not be hidden (fix in the new service instead)

| Diff | Why it matters |
|---|---|
| Enum casing (`SHIPPED` vs `Shipped`) | Breaks Java/Jackson clients; string comparisons go wrong |
| Ids on reads, id type (number ↔ string) | Wrong entity / data leak; client contract |
| Epoch-millis vs ISO timestamp, timezone shift | Type change; wrong times |
| HTTP status (other than one explicit, ticketed equivalence) | Error vs success, authz, concurrency |
| Money as double / precision loss | Financial correctness |
| Order of list/search results and history arrays | Pagination and timeline semantics |
| `Content-Type`, `Location`, cache and pagination headers | Client and proxy behavior |
| JSON type changes of any field | Strict clients fail |
