# Review: add FINE logging to `AdaptiveFetchCache.updateQueryFetchSize`

## Verdict

The instrumentation is placed in the one spot that cannot answer the question that motivated it, and the correlation id
it prints is not the key the cache is stored under. It also prints byte counts through `MessageFormat` without a number
format, so the values come out locale-formatted (`103,887,667`) and unparseable. I would not merge it as is.

What is right: the `isLoggable` guard before allocating the `Object[]` is the correct idiom for a path that runs per
fetch; `previousFetchSize` is read before `setSize`, so the "from" value is genuinely the old one; and the concatenated
format string has its spaces in the right places.

## 1. The log is silent in the case being debugged

The author's hypothesis is *"adaptive fetch gets over-confident and sets too high a fetch size"*, and their plan is
*"I expect I will need to set `adaptiveFetchMaximum`"*. The new log makes both of those harder to see, not easier:

- **It only fires when the largest row grows.** The enclosing `if (adaptiveMaximumRowSize < maximumRowSizeBytes && ...)`
  means nothing is emitted for the fetch that actually overflowed the buffer, because that fetch's rows are not
  necessarily larger than the running maximum. The overflow is a *cumulative* condition (`Received: 103887670` against a
  limit of `103887667` — 3 bytes over), so it is reached by a fetch size that is one row too large, which is a property
  of the fetch size in effect, not of a new row-size record.
- **It is suppressed exactly when the clamp is active.** `if (newFetchSize != previousFetchSize)` means that once
  `adaptiveFetchMaximum` (or the minimum) pins the value, further row growth recomputes the same clamped number and logs
  nothing. The reader then cannot distinguish "rows stopped growing" from "the clamp is holding the size while rows keep
  growing" — and the second is precisely the state the author wants to confirm. Drop this condition: the update is worth
  one line every time the row-size record moves, changed value or not.
- **The value that is used is never logged.** `getFetchSizeForQuery` is what hands a number to the executor, and it is
  silent. A reader gets a sequence of "updated to N" lines with no record of which N was in effect for the fetch that
  failed, and no way to tell whether the executor used the adaptive value at all or fell back to `defaultRowFetchSize`.

**Change:** log on every row-size record (not only on change); add a FINEST line in `getFetchSizeForQuery` for the value
returned. The real fix for this bug report, though, is on the failure path — see §7.

## 2. `query.hashCode()` is not the cache key, so the correlation id is wrong

The cache is keyed by `query.getNativeSql().trim()`. The log prints `query.hashCode()`, a different identity:

- Two `Query` objects for the same SQL share one cache entry — that sharing is the documented behaviour of this class
  ("same queries have it shared"). If `Query` does not override `hashCode`, those objects print *different* values, so
  one entry's history appears in the log as several unrelated series and the reader concludes the driver is tracking
  queries it is not.
- Identity hash codes are also recycled after GC, so two genuinely different queries can print the same value. The id is
  untrustworthy in both directions, and it is the only thing tying the lines together.
- Calling it "query hash" invites the reader to treat it as a stable, comparable query identity. It is not.

**Change:** derive the id from the cache key and format it so it does not read as a quantity, e.g.
`Integer.toHexString(sql.hashCode())`. Emit the id-to-SQL mapping once, when the entry is created in `addNewQuery`, at
FINEST — the level `QueryExecutorImpl` already uses for per-execution detail. That keeps SQL text (which can carry
literal values from the application, in a library whose logs the driver authors never see) out of the repeated FINE
lines while still letting a reader resolve an id.

```java
// in addNewQuery, when adaptiveFetchCacheEntry == null
LOGGER.log(Level.FINEST, "adaptiveFetch: tracking query {0}: {1}",
    new Object[]{Integer.toHexString(sql.hashCode()), sql});
```

## 3. The numbers are printed through `MessageFormat` with no number format

`java.util.logging` formats a message containing `{0}` with `java.text.MessageFormat`, which formats a bare numeric
argument through the **default locale's** `NumberFormat`. Every value in this line is a number, so:

- `maximumResultBufferSize` prints as `103,887,667` — or `103.887.667`, or `103 887 667` with a non-breaking space,
  depending on the JVM's default locale on a machine the driver authors never see.
- `query.hashCode()` prints as `-1,234,567,890`, which is unreadable as an identifier.
- None of it survives a `grep`, a `cut`, or a comparison against the exception's `Received: 103887670; Current limit:
  103887667`, which is the whole point of logging it. Two numbers for the same quantity, formatted two different ways,
  in the same investigation.

The existing `"simple execute, handler={0}, maxRows={1}, fetchSize={2}, flags={3}"` has the same latent problem, but its
values are small enough that grouping rarely shows. Here the values are around 10^8, so it shows every time.

**Change:** use `{n,number,#}` for every numeric placeholder (this keeps the parameters typed for any handler that reads
`LogRecord.getParameters()`), or pass `String.valueOf(x)`.

## 4. Nothing says whether adaptive fetch is even on, or with what limits

`updateQueryFetchSize` has four silent exits: `adaptiveFetch` false, `maximumResultBufferSize == -1`, no cache entry, and
row size not a new record. The author's actual complaint was *"I went to turn on debug logs and discovered there are
none"* — and after this change, a user whose `maxResultBuffer` is unset still gets none, with no hint why. They cannot
tell a broken feature from a disabled one.

`minimumAdaptiveFetchSize` and `maximumAdaptiveFetchSize` are fixed for the life of the connection, so repeating them on
every update line is noise and still does not cover the case where no update ever happens. Log the effective
configuration once, in the constructor, and drop `{5}`/`{6}` from the per-update line:

```java
if (LOGGER.isLoggable(Level.FINE)) {
  LOGGER.log(Level.FINE,
      "adaptiveFetch={0}, adaptiveFetchMinimum={1,number,#}, adaptiveFetchMaximum={2,number,#}, "
          + "maxResultBuffer={3,number,#} bytes",
      new Object[]{adaptiveFetch, minimumAdaptiveFetchSize, maximumAdaptiveFetchSize,
          maximumResultBufferSize});
}
```

## 5. The line names fields, not the properties the user can set

`maximumResultBufferSizeBytes`, `minimumAdaptiveFetchSize`, `maximumAdaptiveFetchSize` are internal field names. The
connection properties a user sets — and the ones the author intends to change — are `maxResultBuffer`,
`adaptiveFetchMinimum`, `adaptiveFetchMaximum`. A reader who greps their own config for `maximumAdaptiveFetchSize` finds
nothing. Naming the property in the message is what turns the log line into an action.

Keeping `Bytes` on a byte quantity is right; prefer spelling the unit out as a suffix (`maxResultBuffer=... bytes`) so it
stays attached to the value rather than to a name that no longer matches the property.

## 6. The clamp itself is invisible, and `-1` reads as a real fetch size

- `newFetchSize` is reassigned by `adjustFetchSize`, so by the time it is logged the raw `maximumResultBufferSize /
  maximumRowSizeBytes` quotient is gone. The reader has to divide the two logged numbers by hand to find out whether the
  clamp fired — for the one question the author came to ask. Capture the quotient in its own variable and log both.
- On the first update `previousFetchSize` is the `-1` sentinel from `AdaptiveFetchCacheEntry`, and the line reads
  "from -1 to 1650", which looks like a real prior value to anyone who has not read the entry class.

Together with §1–§5, the per-update line becomes:

```java
int computedFetchSize = (int) (maximumResultBufferSize / maximumRowSizeBytes);
int newFetchSize = adjustFetchSize(computedFetchSize);
int previousFetchSize = adaptiveFetchCacheEntry.getSize();

if (LOGGER.isLoggable(Level.FINE)) {
  LOGGER.log(Level.FINE,
      "adaptiveFetch query {0}: largest row now {1,number,#} bytes, computed fetchSize {2,number,#}, "
          + "using {3,number,#} (previously {4})",
      new Object[]{Integer.toHexString(sql.hashCode()), maximumRowSizeBytes, computedFetchSize,
          newFetchSize, previousFetchSize == -1 ? "unset" : String.valueOf(previousFetchSize)});
}
```

`computed` versus `using` shows the clamp without arithmetic; the buffer size and the two limits have already been
logged once per connection by §4.

## 7. What is missing: the failure path carries no adaptive-fetch context

The message the author is actually staring at —

```
Result set exceeded maxResultBuffer limit. Received: 103887670; Current limit: 103887667
```

— names neither the query, nor the fetch size in effect, nor the largest row size learned for it. No amount of logging in
`AdaptiveFetchCache` closes that gap reliably: the reader still has to correlate by timestamp across an interleaved log
from a connection pool, and the adaptive value may not even be the one the executor used. Attaching the fetch size and
the learned maximum row size to that exception would answer "did adaptive fetch cause this, and with what number" at the
point of failure, in a report a user can paste. That is the change worth making; the FINE logging here is the supporting
detail, not the fix.

## 8. Smaller points

- **Eviction is silent.** When `removeQuery` drops the counter to zero, the entry and its learned row size are discarded,
  and the next execution of the same SQL starts over from `defaultRowFetchSize`. A reader following one query id sees the
  fetch size fall back with nothing explaining it. One FINEST line on removal.
- **No connection identity.** `AdaptiveFetchCache` is per connection, but `LOGGER` is static and the line carries nothing
  connection-scoped. In a pooled application, two connections learning the same SQL produce two interleaved series that
  look like one oscillating value.
- **Separator style.** The driver's nearby lines use `key={0}, key={1}` with commas; this one mixes a prose sentence with
  space-separated pairs. Worth matching.
- **Level.** FINE is the right choice for the update — pgjdbc's `loggerLevel=DEBUG` maps to FINE, and this is what the
  author would turn on. Keep the higher-volume additions suggested above (entry creation, eviction, value read) at
  FINEST, matching `QueryExecutorImpl`.
- **Test.** `AdaptiveFetchCacheTest` already drives this method. A test that attaches a `Handler`, runs an update under a
  non-English default locale, and asserts the rendered message contains `103887667` would have caught §3 and is cheap.
- **The patch does not apply to the files given.** `change.diff`'s context has `private boolean adaptiveFetch = false;`
  and `private int minimumAdaptiveFetchSize = 0;` plus a `@NonNull` on the method, while `src/AdaptiveFetchCache.java` has
  `private boolean adaptiveFetch;`, `private final int minimumAdaptiveFetchSize;` and no annotation. Rebase before
  sending it on.
