# Review: FINE record for adaptive fetch size updates

The change is the right idea in the right place: one record, on the state transition, guarded, at a level a silent
host will not see. But as written it fails the one task it was added for. The author wants to decide whether to set
`adaptiveFetchMaximum`; the record does not say whether `adaptiveFetchMaximum` is already in force, and the numbers it
prints will not match the exception that started the investigation.

Findings are ordered by how much they cost the reader.

## 1. The numbers are locale-formatted, so they will not match the exception or the connection string

`Logger.log(Level, String, Object[])` renders the message through `java.text.MessageFormat` whenever the text contains
`{` followed by a digit, and `MessageFormat` sends numeric arguments through the locale's number format. Every value
in this call is passed as a boxed number, so on an `en-US` JVM the record prints

```
maximumResultBufferSizeBytes=103,887,667 maximumRowSizeBytes=2,048 ... query hash 1,732,371,562
```

and on a `fr` JVM `103 887 667`. The exception the author is chasing says `Current limit: 103887667`. The author greps
the log for `103887667` and gets nothing — which is very close to the failure that motivated this change in the first
place. The `query hash` is the worst case: a grouped identifier cannot be pasted into a search or compared with the
same value printed anywhere else.

Fix at the call site: pass the digits as text — `Long.toString(maximumResultBufferSize)`,
`Integer.toString(maximumRowSizeBytes)`, and so on. `{3,number,#}` in the pattern also suppresses grouping, but
stringifying the argument is harder to lose in a later edit. (SLF4J's `{}` form is not affected; `java.util.logging`'s
is, and the driver uses `java.util.logging`.)

## 2. The record names its inputs but not the branch that produced the value

A reader holding the line cannot tell which of the three paths through `adjustFetchSize` fired:

- `newFetchSize = maximumResultBufferSize / maximumRowSizeBytes`, unbounded;
- capped at `adaptiveFetchMaximum`;
- raised to `adaptiveFetchMinimum`.

Distinguishing them is the author's entire decision. The record instead prints the four inputs and asks the reader to
redo the integer division in their head and compare it with two limits — and to know, unstated, that
`adjustFetchSize` applies the maximum first and the minimum second, so when both bind the minimum wins.

Three specific misreadings this produces:

- **`-1` means three different things in one line.** A fresh `AdaptiveFetchCacheEntry` has `size == -1`, so the first
  record for every query reads `from -1 to 100`. A reader will take `-1` as a previous fetch size; it means "no
  adaptive size yet, the query used `defaultRowFetchSize`". In the same line `maximumAdaptiveFetchSize=-1` means
  "`adaptiveFetchMaximum` is not set", not "the maximum is minus one". And `getFetchSizeForQuery` returns `-1` for a
  third meaning.
- **A capped value looks like a computed one.** `to 1000` with `maximumAdaptiveFetchSize=1000` is the answer the
  author is looking for, and nothing in the text says the cap is what produced it.
- **`to 0` is not a small fetch size.** When one row is larger than `maxResultBuffer`, the division yields `0`, and
  with the default `adaptiveFetchMinimum=0` nothing raises it. `0` as a JDBC fetch size means *unlimited*, which is
  the over-confidence the author suspects. A record that prints a bare `0` here actively misleads. Worth checking
  whether this is the bug, independently of the logging.

Name the branch in the text. Re-deriving it at the call site by comparing against the unbounded value works but is
ambiguous when the values coincide; better is to have `adjustFetchSize` report which bound it applied and log that.

Note that once the branch is named, the guard `newFetchSize != previousFetchSize` reads correctly as a transition:
the cap produces one record when it starts to bind and silence while it holds, which is the right behavior. Without
the branch, that silence is indistinguishable from adaptive fetch not running at all — see finding 5.

## 3. The field names are the private field names, not the names the reader can set

The message says `maximumResultBufferSizeBytes`, `minimumAdaptiveFetchSize`, `maximumAdaptiveFetchSize`. The reader
holds a JDBC URL containing `maxResultBuffer`, `adaptiveFetchMinimum`, `adaptiveFetchMaximum`, and the driver
documentation uses those spellings too. None of the three logged names greps against anything the reader can change,
and `maximumResultBufferSizeBytes` is not even the field name (`maximumResultBufferSize`).

Use the connection property spellings, and keep the unit out of the name and in the text: `maxResultBuffer=103887667
bytes`. `maxResultBuffer` accepts forms like `90p` and `99M`, so printing the resolved byte count under the property's
own name is exactly what the reader needs to see.

Renaming the Java fields to match the properties is the wrong direction; only the message text needs to change.

## 4. `query.hashCode()` does not identify what the record is about

The cache is keyed on `query.getNativeSql().trim()`, not on the `Query` object. Two `Query` instances carrying the
same SQL share one cache entry, and `Query` implementations do not override `hashCode`, so successive records about
the *same* entry can print *different* hashes. The reader who groups the log by "query hash" to watch one query's
fetch size evolve will split one entry across several groups and may merge nothing correctly.

Log the cache key. `sql` is already in scope on this path:

- the trimmed native SQL is what the reader needs to connect the record to their statement, and `String.hashCode` is
  at least stable across JVMs if the SQL text is too long or too sensitive to print at FINE;
- if you log the hash rather than the text, make sure the same key is printed somewhere the reader can also obtain,
  or the identifier joins nothing.

Separately, the record carries no connection or session identifier. `AdaptiveFetchCache` is per connection, every
instance logs under the same logger name, and a pooled application will interleave records from several connections
with nothing to separate them — the thread id `java.util.logging` prints is not a connection id, because a pooled
connection moves between threads. Either thread the identifier the driver's other records use into the constructor,
or state in the pull request that this record is only usable in single-connection debugging. The latter is a real
limitation for the support case that motivated the change.

## 5. The configuration is still invisible — the author's "there are none" is only half fixed

Nothing is emitted when `AdaptiveFetchCache` is constructed. That leaves two common support cases silent:

- `adaptiveFetch=true` with `maxResultBuffer` unset. `maximumResultBufferSize == -1`, every method returns
  immediately, and the whole feature is inert. The reader sees no records and concludes the feature is working
  quietly.
- `adaptiveFetchMaximum` already set, and the computed size pinned at it. After finding 2's transition record, also
  silence.

Both are answered by one record in the constructor, once per connection, reporting the effective configuration:
whether adaptive fetch is on, the resolved `maxResultBuffer` in bytes or that it is unset, and
`adaptiveFetchMinimum` / `adaptiveFetchMaximum` or that they are unset. Once per connection is a rate a pool can
afford at FINE, and it is the record that makes a silent log readable instead of ambiguous.

This is also the place to tell the caller that `adaptiveFetch=true` without `maxResultBuffer` does nothing. That is an
avoidable condition the caller can fix, and a `java.sql.SQLWarning` on the connection would be the stronger channel;
if the driver has no convention for that, a record at the constructor is the fallback and should say plainly that
adaptive fetch will have no effect.

## 6. The failure itself still carries no adaptive fetch context

`Result set exceeded maxResultBuffer limit. Received: 103887670; Current limit: 103887667` reaches the caller, who can
act on it — so it correctly stays an exception and should not also be logged. But it names neither the query, nor the
fetch size in force, nor the row size the cache believed. The reader is left joining two streams by timestamp, and the
FINE record nearest the failure may be thousands of rows earlier, because the fetch size stopped changing long before
the buffer overflowed.

Adding the adaptive fetch size and the largest row size seen to that exception message costs nothing and would likely
have answered the original question without this diff. It is outside the two files here, so it is a suggestion rather
than a blocker on this change.

## 7. Level: defensible, but say why

The one neighbor quoted in the issue, `QueryExecutorImpl`'s `"  simple execute, handler={0}, maxRows={1},
fetchSize={2}, flags={3}"`, logs the fetch size actually used at FINEST. FINE for this record is a defensible choice
— it fires on change rather than per execute, and a user asked for a reproduction can realistically enable FINE on one
logger, whereas FINEST on pgjdbc produces the whole protocol stream. Check it against the other calls in
`org.postgresql.core.v3`, and if it stays at FINE, put the reason in the commit message.

One consequence to be aware of: at FINE the reader sees the decision but not its application, since the execute line
is at FINEST. That is another reason finding 4's identifier and finding 5's configuration record matter.

## What the change gets right

Worth keeping as is:

- **The transition guard.** `newFetchSize != previousFetchSize` compares the state, not a clock, so the steady state
  is quiet. Without it this call would fire on every row-size growth, which is unbounded in the result-set size.
- **The `isLoggable` guard.** `java.util.logging` evaluates the argument array before the call, so the guard is not
  redundant, and the placeholder count matches the array length (`{0}`–`{6}`, seven elements).
- **The message contains no apostrophe**, which in `MessageFormat` would silently stop substitution from that point.
- **Library mode is respected.** `Logger.getLogger(AdaptiveFetchCache.class.getName())` is acquisition by name with no
  configuration call, so the host routes it, and FINE sits below `java.util.logging`'s default console level. A host
  that configures nothing stays as quiet as it was.

## Proposed call site

```java
int previousFetchSize = adaptiveFetchCacheEntry.getSize();
if (newFetchSize != previousFetchSize && LOGGER.isLoggable(Level.FINE)) {
  LOGGER.log(Level.FINE,
      "adaptiveFetch: fetch size changed from {0} to {1} ({2}); maxResultBuffer={3} bytes, "
          + "largest row so far={4} bytes, adaptiveFetchMinimum={5}, adaptiveFetchMaximum={6}, sql={7}",
      new Object[]{
          previousFetchSize == -1 ? "defaultRowFetchSize" : Integer.toString(previousFetchSize),
          Integer.toString(newFetchSize),
          bound,  // "computed from maxResultBuffer", "capped at adaptiveFetchMaximum", "raised to adaptiveFetchMinimum"
          Long.toString(maximumResultBufferSize),
          Integer.toString(maximumRowSizeBytes),
          minimumAdaptiveFetchSize == 0 ? "not set" : Integer.toString(minimumAdaptiveFetchSize),
          maximumAdaptiveFetchSize == -1 ? "not set" : Integer.toString(maximumAdaptiveFetchSize),
          sql});
}
```

`bound` comes from `adjustFetchSize`, which is the only code that knows which limit it applied; returning it is
cleaner than re-deriving it here by comparison.

## Checklist

- **Mode / configuration call**: none. Library mode; logger acquired by name, no handler, level, or appender is set.
- **Existing signal**: partially covered. `QueryExecutorImpl`'s FINEST execute line already prints the fetch size in
  force; it does not carry the row size or the limit that produced it, so the new record is justified. It should be
  joinable with that line — see finding 4.
- **Log and rethrow**: none. No error path is touched.
- **Rate**: passes. One record per fetch-size change per cache entry, and the compared value is the state.
- **Contents**: fails on the joining identifier (4), the branch (2), and the settable names (3).
- **Fields in the text**: not applicable. `java.util.logging` with no structured-field mechanism; the driver
  interpolates, and this call agrees with it.
- **Guard**: passes. `isLoggable` is present and `java.util.logging` would otherwise build the argument array.
- **Instrument**: suppressed by mode. The driver ships no metrics facility, so "how often does the cap bind" cannot be
  a counter here.
- **Threshold**: none. No compiled-in constant decides whether to emit.
- **Span**: none.
- **Level**: see finding 7 — defensible, unverified against the surrounding package.
- **Context**: none. No thread is started and `java.util.logging` has no ambient context to leak.
- **Vacuous**: finding 2 — the record prints its inputs and not the branch.
- **Nothing**: the buffer-overflow failure correctly stays on the caller's channel and is not logged; finding 6 asks
  only that the exception carry more, not that a record be added.
