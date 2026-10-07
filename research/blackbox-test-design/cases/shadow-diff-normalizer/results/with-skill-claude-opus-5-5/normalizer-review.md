# Review: `diff-normalizer.yaml` (orders-api shadow diff)

## Verdict

Don't use this normalizer to decide the read cutover yet. A diff rate under 1% after
this normalizer says little about parity. Most rules apply to `$..*` or to a key name
anywhere in the document, so each erases a whole class of differences across every
endpoint. That class includes some of the regressions the shadow run is meant to catch:

| Regression in the new service | Visible after this normalizer? |
| --- | --- |
| `GET /orders?sort=...` returns the wrong order, or pages overlap | **No** (`sort_arrays` on `$..*`) |
| Order shows the wrong customer, address or product (nested `{"id": ...}`) | **No** if the other fields match (`$..id`) |
| Status enum spelled `"Shipped"` instead of `"SHIPPED"` (breaks Jackson clients) | **No** (`case_insensitive`) |
| Endpoint returns 500, 404 or 422 where the old one returned 400 | **No** if the bodies have the same shape (`http_status: false`) |
| Dates shift by the server time zone, or change from epoch millis to ISO strings | **No** for `createdAt`/`updatedAt` (ignored) |
| Large integer (above 2^53) changes in its last digits | **No** (`numbers: double`) |
| `Location` header missing on create, `Content-Type` or pagination headers changed | **No** (`headers: false`) |
| Different validation error returned (other field, other rule) | Only if a field besides `message` differs |

Every rule in the file has a real noise source behind it. The problem is that each one
is broader than its noise. The rest of this review goes through what each rule should
normalize, what it must keep visible, and how to show the normalizer is hiding only noise.

Labels used below: **observed** means the comment in the YAML reports it; **likely**
follows from the stack (Java 8 / Spring Boot / Jackson / Oracle) but nobody has checked it
against traffic yet; **question** means the team has to answer it.

---

## Rule by rule

### 1. `sort_arrays: true` on `$..*`

*Noise (observed):* line items and errors come back in different orders.

*What it hides:*
- **Order on list endpoints.** Anything that returns a sorted or paged list
  (`/orders?sort=createdAt&page=2`, order history, a customer's orders) has order as
  part of its contract. A broken `ORDER BY`, the wrong sort direction or an unstable
  tiebreaker all disappear. Unstable tiebreakers also cause duplicate or skipped rows
  between pages.
- **Order that clients rely on.** UIs and clients often show `errors[0]` or render line
  items in response order. If the old service sorted line items (by line number or
  insertion), that order is part of the contract even if nobody wrote it down.
- **Duplicates, possibly.** Whether the tool's sort keeps duplicates is unknown. If it
  dedups, a doubled line item disappears. *Question:* check this.

*Rule-order bug:* sorting is rule 1, so it sorts on **raw** values, before ids,
timestamps and number spellings are normalized. Two lists that differ only by noise
(other `id`s, `10.10` vs `10.1`) can sort differently, and then elements are compared
against the wrong partner. That creates spurious diffs, which push the team toward
adding more ignore rules.

*Recommendation:*
- Remove the global rule. Sort only at named paths where order really is unspecified,
  and sort **by an explicit key** (for example `lineItems` by `lineNumber` or `sku`, and
  `errors` by `code`+`field`).
- First find out whether the old order is specified at all. *Likely:* the old order comes
  from an Oracle query with no `ORDER BY` (unspecified, usually insertion order) or from
  a Java `HashMap`/`HashSet` (hash order). If clients can see it, keep it, or document it
  as an intended change.
- Never sort the top-level array of a list endpoint.
- Run sorting **last**, after all value normalization.

### 2. `drop_nulls: true` on `$..*`

*Noise (observed):* the old service writes `"discount": null` and the new one omits it.

*What it hides:* the difference between `null` and an absent key, everywhere. This is
usually harmless for JSON consumers, but not always:
- A client written in Kotlin (kotlinx.serialization, or Jackson with the Kotlin module)
  that declares a non-nullable property without a default fails on a missing key.
  JavaScript code using `'discount' in obj` or `hasOwnProperty` behaves differently.
- If the tool also drops `null` **elements** of arrays, `[null, x]` becomes `[x]`. That
  hides a broken mapping that produces null entries.

It does **not** hide `null` vs `""`. That difference will show up soon because of
Oracle: Oracle stores `''` as `NULL`, so the old service can never return an empty
string. If the new service uses a different database, or maps differently, it will
return `""` where the old one returned `null` (*likely*). Decide that case per field and
don't fold it into a global rule.

*Recommendation:* keep the rule, but limit it to object members (never array elements),
and ideally to a list of fields known to be optional. Ask the main consumers whether
they tolerate a missing key. If any of them don't, configure the new service's Jackson
or kotlinx inclusion to match instead of normalizing the difference away.

### 3–4. Ignore `$..createdAt` and `$..updatedAt`

*Legitimate noise:* on **mirrored writes**, the two services create the record at
slightly different moments, so the timestamps differ.

*What it hides:* on **reads of the same stored order**, these values must be identical.
The rule also matches at every depth (line items, shipments, payments). Date handling
is one of the most likely places for a Java 8 → Kotlin port to differ:
- **Format.** Jackson writes `java.util.Date` and `java.sql.Timestamp` as epoch
  milliseconds by default (`WRITE_DATES_AS_TIMESTAMPS` is on). The Kotlin service
  probably writes ISO-8601 strings. Every client parsing the field breaks.
- **Time zone.** Oracle `DATE` and `TIMESTAMP` without a time zone are read in the
  JVM's default zone. A different default zone in the new deployment, or
  `LocalDateTime` vs `Instant`, shifts every value by hours.
- **Precision.** Milliseconds vs microseconds vs seconds, and trailing zeros.

*Recommendation:*
- For reads: don't ignore these fields. Parse both sides to an instant and compare
  exactly. Report a **format** difference (epoch vs ISO, offset vs `Z`, precision) as
  its own diff category, not as noise.
- For mirrored creates and updates: allow a time window (for example ±5 s) rather than
  ignoring the field. Still require the same format, and the same presence of the field.
- Apply the same handling to the other timestamps (`shippedAt`, `deliveredAt`,
  `cancelledAt`, and so on) rather than adding ignore rules for them when they show up.

### 5. `numbers: double` on `$..*`

*Noise (observed):* `10.10` vs `10.1`, and `1E+1` vs `10`. *Likely:* the old service
serializes `BigDecimal` with `toString()`, which uses scientific notation after
`stripTrailingZeros()`, because Jackson's `WRITE_BIGDECIMAL_AS_PLAIN` is off by default.

*What it hides:*
- **Integers above 2^53.** Different values become equal. Oracle `NUMBER(19)` keys,
  external references, and epoch micro- or nanoseconds can all exceed 2^53. Ids are
  already ignored (rule 8), but any other long field is exposed.
- **Scale and notation as a contract difference.** A consumer that binds amounts into
  `BigDecimal` and prints them, or compares them with `equals` (where `10.1` ≠ `10.10`),
  or a downstream system that expects two decimals for money, sees a real change. It
  may be an acceptable change, but someone should decide that.
- Converting through `double` is the wrong model for money in any case. It happens not
  to merge distinct two-decimal amounts, but it does merge distinct values once a
  number has about 16 significant digits.

*Question:* does the tool also turn numeric **strings** into numbers? If so, it hides
`"10.10"` (string) vs `10.1` (number), which is a type change that breaks typed
clients. Test it (see "Audit the normalizer" below).

*Recommendation:* compare numbers as exact decimals (equal when
`BigDecimal.compareTo` returns 0), never through `double`. Report scale and notation
differences on money fields (`price`, `amount`, `total`, `tax`, `discount`) in a
separate, low-severity bucket rather than erasing them. Keep JSON types strict.

### 6. `case_insensitive` on `$..status`

*Noise (observed):* `"SHIPPED"` vs `"Shipped"`.

**This is not noise; it's a bug in the new service.** Jackson matches enums by exact
name by default (`ACCEPT_CASE_INSENSITIVE_ENUMS` is off). Any Java or Kotlin client
with an `OrderStatus` enum fails to deserialize `"Shipped"`, and any
`if (status === "SHIPPED")` in a frontend stops matching. The likely cause is a
`@JsonValue` or `@SerialName` display name, or `toString()`, on the Kotlin enum.

The rule also matches every `status` key: payment status, shipment status, and the
`status` member of a Spring-style error body.

*Recommendation:* delete the rule and fix the new service to emit the exact old enum
names. Also check enum values the old service emits that the new one doesn't know
about (and the reverse), using the rarest statuses in traffic.

### 7. Ignore `$.errors[*].message`

*Noise (observed):* wording differs.

*What it hides:* the rule is fine by itself, as long as clients don't parse messages
(*question:* does any UI display them, or does any client match on them?). What makes
it dangerous is how it combines with rule 1 (errors sorted) and `http_status: false`. If
an error entry has no fields besides `message`, every error response reduces to "a
list of N empty objects". Then a 400 for a missing field and a 500 from a
`NullPointerException` compare as equal whenever both return one error.

*Recommendation:* keep comparing everything else in the error entries (`code`, `field`,
`rejectedValue`, the error count). If the entries have no machine-readable code,
compare the HTTP status and the error count at least. Put message differences in a
separate low-severity bucket and sample it periodically instead of discarding it.

### 8. Ignore `$..id`

*Noise (observed):* the new service generates ids differently.

*What it hides:* this is the most dangerous rule in the file. `$..id` matches **every**
key named `id` at any depth: `customer.id`, `shippingAddress.id`,
`lineItems[*].product.id`, `payment.id`. If the new service joins to the wrong
customer, attaches the wrong address, or links a line item to the wrong product, the
diff stays clean as long as the denormalized fields happen to match.

The noise also only exists for **newly created** records:
- On a mirrored `POST`, the new service creates its own row and assigns its own id.
  That difference is real and expected.
- On a `GET` of an existing order, the id is the key you looked it up by. It must be
  identical. If the two sides return different ids for a read, they're reading
  different data, and the whole comparison for that request is invalid.

*Recommendation:* don't ignore ids. Build an **id map** from the responses to mirrored
creates (old id → new id). Rewrite new-side ids through that map before comparing
later responses, and treat any id that doesn't map as a diff. That covers newly
created records and keeps referential correctness visible. On reads of records created
before the shadow run, compare ids exactly.

### `compare.http_status: false`

*Noise (observed):* some 200 vs 201 on POST.

*What it hides:* every status difference, on every endpoint, including 200 vs 404,
400 vs 500, 409 vs 200 (a duplicate check that's missing), and 422 vs 400. Status is
the first thing every client checks.

200 vs 201 is also a real contract change. Clients that check `== 200` break, and a
201 should come with a `Location` header (see headers).

*Recommendation:* always compare status. Allow exactly one known difference,
`POST <create endpoints>: 200 ↔ 201`, and record it as an intended change with the
consumers' agreement, or make the new service return 200.

### `compare.headers: false`

*What it hides:* `Content-Type` (including charset), `Location`, `Cache-Control`,
`ETag`/`Last-Modified`, `Content-Disposition`, pagination headers (`Link`,
`X-Total-Count`), CORS headers, and `Vary`.

*Recommendation:* compare an allow-list of those headers. Ignore the rest, such as
`Date`, trace and request ids, `Server`, `Content-Length`, and the transfer encoding.

---

## What the normalizer should normalize (noise it's missing)

The current rules hide too much in some places and miss some genuine noise in others.
Expect these to show up and inflate the raw diff. Handle each narrowly:

- Per-request values in bodies: `timestamp`, `path` and `traceId` in Spring Boot's
  default error body. Ignore them only in error bodies.
- Hostnames or ports inside `Location` headers and HATEOAS links (old host vs new
  host). Rewrite the host, then compare the path.
- Key order inside objects. It doesn't matter in JSON; check that the tool already
  ignores it.
- Number spelling, as exact decimals (rule 5, replaced).
- Ids of records created during the shadow run, through the id map (rule 8, replaced).
- Timestamps of records created during the shadow run, within a window (rules 3–4,
  replaced).
- Error message wording (rule 7, kept but reported in its own bucket).

---

## Process problems (more important than any single rule)

### The normalizer itself has never been tested

So far the only measure of the normalizer is the diff rate it produces. That's
circular: a normalizer that erased everything would score 0%. Before relying on it:

1. **Planted-difference test (negative controls).** Take a sample of real response
   pairs that come out equal. Inject one known regression at a time and confirm the
   pipeline reports each one:
   - swap two rows of a list endpoint
   - remove a line item
   - change one amount by 0.01
   - change `customer.id`
   - change the case of a status
   - turn a 400 into a 500
   - turn an epoch timestamp into an ISO one, and shift a timestamp by one hour
   - change `"10.10"` into `10.10`
   - drop the `Location` header

   Any planted difference that comes out equal is something the normalizer hides. Run
   this in CI whenever `diff-normalizer.yaml` changes.
2. **Map the equivalence classes empirically** for each rule: feed the tool pairs that
   differ in exactly one aspect (null vs absent, null in an array, numeric string vs
   number, duplicate array elements, `1E+1` vs `10`) and record which pairs it merges.
3. **Count hits per rule.** For each rule, log how many responses it changed, by
   endpoint. A rule that changes 20% of responses either covers one large, real source
   of noise, which is fine once someone has looked, or is hiding a defect. Review a
   sample of what each rule erased.

### Rule order

Rules run "in the order the noise showed up". Normalization should run in a fixed,
deliberate order: id mapping → value canonicalization (numbers, timestamps) → field
ignores → null handling → keyed sorting **last**.

### Rate the diffs by severity, not one number

Keep the raw diff for every request, and report several categories instead of a single
percentage:

| Bucket | Examples | Cutover gate |
| --- | --- | --- |
| Critical | status code, amounts, ids/references, enum values, list order on sorted endpoints, missing/extra items | **0** unexplained cases |
| Contract | date/number format, null vs absent, `""` vs null, headers | each class decided as "fix" or "accepted change" with consumers |
| Cosmetic | error message wording, number scale on non-money fields | tracked, not gating |

A 1% overall diff rate can still contain hundreds of wrong totals per day. Gate on
critical diffs per endpoint, not on the overall rate.

### Coverage of the traffic

Mirrored traffic is dominated by the common `GET`s. Cancellations, refunds, partial
shipments, validation failures, and old orders with legacy data (nulls in old columns,
retired statuses) are rare in the traffic but are where a port is most likely wrong.
Report the number of compared requests **per endpoint and per status code**. As a rule
of thumb, if `n` requests of a kind compared clean, the disagreement rate for that kind
of traffic is below about `3/n` (95% confidence). Fewer than a few hundred clean
comparisons on an endpoint therefore proves little, and the bound says nothing about
inputs the traffic never sent. Add targeted replays for the rare paths.

### Shadow writes (question for the team)

The 200 vs 201 note means **POSTs are being mirrored**. Confirm that the new service
writes to its own storage and stubs every downstream side effect: payments, emails,
inventory reservations, and events or messages to other services. A mirrored create
that reaches shared Oracle tables or a real downstream system duplicates orders and
payments for real. Also confirm what data the new service *reads*. If it reads the
same Oracle schema, ids on reads must match exactly (see rule 8). If it reads a copy,
replication lag explains some diffs, and those should be measured, not ignored.

---

## Proposed replacement (sketch)

The tool's DSL may not support all of this (keyed sort, an id map, time windows,
per-endpoint scoping, severity buckets). Where it doesn't, those features are worth
adding to the tool rather than falling back to global ignores.

```yaml
# Order is deliberate: map ids → canonicalize values → ignore → nulls → sort.
rules:
  - endpoints: ["POST /orders", "POST /orders/*/..."]
    capture_id_map: { old: "$.id", new: "$.id" }   # feeds later comparisons
  - match: "$..*"
    remap_ids_through_map: true                    # unmapped id => diff
  - match: "$..[?(@ is number)]"
    numbers: exact_decimal                         # compareTo, never double; JSON types strict
    report_scale_diff: { paths: ["$..price", "$..amount", "$..total", "$..tax", "$..discount"], bucket: contract }
  - match: ["$..createdAt", "$..updatedAt", "$..*At"]
    timestamps: { compare: instant, report_format_diff: contract }
  - endpoints: [mirrored writes]
    match: ["$..createdAt", "$..updatedAt"]
    timestamps: { tolerance: 5s }
  - match: "$.errors[*].message"
    bucket: cosmetic                               # reported, not erased
  - endpoints: [error responses]
    match: ["$.timestamp", "$.path", "$.traceId"]
    ignore: true
  - match: "$..*"
    drop_nulls: { members_only: true }             # never array elements; bucket: contract
  - match: "$.errors"
    sort_by: ["code", "field"]
  - match: "$..lineItems"                          # only if the old order is shown to be unspecified
    sort_by: ["lineNumber"]
  # no sort on top-level arrays of list endpoints
  # no case-insensitive status: fix the new service's enum serialization
compare:
  http_status: true
  http_status_allowed: [{ endpoint: "POST /orders", old: 200, new: 201 }]   # only after consumers agree
  headers: { compare: [Content-Type, Location, Cache-Control, ETag, Link, X-Total-Count, Content-Disposition, Vary] }
```

## Action list

1. Fix the new service: enum names (`status`), and the 201/`Location` decision.
2. Delete `case_insensitive` on `status`, the global `sort_arrays`, `ignore $..id`,
   and `http_status: false`.
3. Replace `numbers: double` with exact decimal comparison, and replace the timestamp
   ignores with instant comparison on reads and a time window on writes.
4. Add the planted-difference test and per-rule hit counts. Re-run the shadow diff and
   expect the rate to go **up**. Triage what appears; that's the point of the exercise.
5. Gate the cutover on zero unexplained critical diffs per endpoint, with stated
   per-endpoint volumes, and not on the overall rate.
6. Confirm shadow write isolation and what data the new service reads.
