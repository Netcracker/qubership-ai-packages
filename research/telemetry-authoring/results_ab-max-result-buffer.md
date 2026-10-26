# Results of the maxResultBuffer trial

## Skills each writer invoked

```text
haiku-final-1   cost=0.016698070000000002 turns=8 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-final-2   cost=0.02685957 turns=17 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final-3   cost=0.02098633 turns=15 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final2-1  cost=0.015622040000000004 turns=13 error=False diff_lines=18 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final2-2  cost=0.01621641 turns=11 error=False diff_lines=20 skills=['english-developer-style', 'telemetry-authoring'] reads=[]
haiku-final2-3  cost=0.015452860000000002 turns=12 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final3-1  cost=0.013623829999999998 turns=10 error=False diff_lines=17 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final3-2  cost=0.017762849999999997 turns=13 error=False diff_lines=14 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-final3-3  cost=0.01474631 turns=10 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
haiku-final4-1  cost=0.01929034 turns=15 error=False diff_lines=21 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final4-2  cost=0.0165431 turns=13 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-final4-3  cost=0.01595147 turns=12 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
haiku-new-1     cost=0.011369390000000002 turns=9 error=False diff_lines=15 skills=['english-developer-style'] reads=[]
haiku-new-2     cost=0.011415709999999999 turns=7 error=False diff_lines=16 skills=['english-developer-style'] reads=[]
haiku-new-3     cost=0.011621999999999999 turns=8 error=False diff_lines=17 skills=['english-developer-style'] reads=[]
haiku-old-1     cost=0.01123229 turns=7 error=False diff_lines=16 skills=['english-developer-style'] reads=[]
haiku-old-2     cost=0.009761330000000002 turns=7 error=False diff_lines=14 skills=['english-developer-style'] reads=[]
haiku-old-3     cost=0.012272700000000001 turns=10 error=False diff_lines=16 skills=['english-developer-style'] reads=[]
sonnet-final-1  cost=0.22902750000000002 turns=13 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
sonnet-final-2  cost=0.1945611 turns=10 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final-3  cost=0.1916942 turns=10 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
sonnet-final2-1 cost=0.1806585 turns=9 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final2-2 cost=0.1912215 turns=11 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final2-3 cost=0.22560190000000002 turns=15 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final3-1 cost=0.19377080000000005 turns=10 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final3-2 cost=0.21650819999999998 turns=12 error=False diff_lines=19 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final3-3 cost=0.23056010000000002 turns=12 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final4-1 cost=0.21904690000000002 turns=12 error=False diff_lines=20 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-final4-2 cost=0.1927564 turns=10 error=False diff_lines=23 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
sonnet-final4-3 cost=0.2320195 turns=13 error=False diff_lines=21 skills=['telemetry-authoring', 'english-developer-style'] reads=['telemetry-authoring/references/jvm.md']
sonnet-new-1    cost=0.2023039 turns=10 error=False diff_lines=18 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-new-2    cost=0.1910847 turns=9 error=False diff_lines=17 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-new-3    cost=0.1939764 turns=10 error=False diff_lines=17 skills=['telemetry-authoring', 'english-developer-style'] reads=[]
sonnet-old-1    cost=0.13957099999999997 turns=5 error=False diff_lines=16 skills=['english-developer-style'] reads=[]
sonnet-old-2    cost=0.14195370000000002 turns=7 error=False diff_lines=17 skills=['english-developer-style'] reads=[]
sonnet-old-3    cost=0.1378492 turns=6 error=False diff_lines=16 skills=['english-developer-style'] reads=[]
```

## Consolidated judge


Checked against base: `PGPropertyMaxResultBufferParser` accepts a byte count, a K/M/G/T suffix (decimal, x1000, case-insensitive), or a percent of max heap (`p`, `pct`, `percent`); values above 90% of max heap are lowered to that; unset means no limit. `PGStream.increaseByteCounter` adds the row size, then calls `setBroken()` before the throw, so the counted total is the bytes read up to the failing row, not the size of the whole result. Every variant passes the numbers as strings (`Long.toString`/`String.valueOf`) or has none, so no rendered text has locale grouping or a leftover placeholder.

| code | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | R1 | R2 | R3 | R4 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TA | Y | N | P | P | Y | P | Y | P | Y | Y | Y | Y | No why; "Increase maxResultBuffer" with no place; "set a smaller fetch size" without autocommit off (G6, G8 P); bytes only. |
| TB | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Bytes only. |
| TC | P | N | P | P | Y | Y | Y | Y | Y | Y | Y | Y | Limit only, no received total; no why; "Raise maxResultBuffer" with no place; bytes only. |
| TD | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | P | Y | "raise ... for example to 100M (100 MB)" equals the current limit (G8 P); reader copies it: "maxResultBuffer=100M" (R3 P). |
| TE | Y | Y | Y | Y | N | Y | Y | P | Y | P | Y | Y | No connection state; "raise maxResultBuffer, for example to 64M" is below the limit (G8 P); reader: "The text doesn't say whether the connection is still usable" (R2 P), and it caught the 64M error. |
| TF | N | N | P | N | Y | Y | Y | Y | Y | Y | Y | Y | No numbers, no why, no unit; "Raise maxResultBuffer" with no place. |
| TG | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Byte count or "a suffix such as 2G"; fetch size "on a connection with autocommit off". |
| TH | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | P | Y | Bytes only; reader gives no value: "The error doesn't say what format the value takes" (R3 P). |
| TI | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Bytes only. |
| TJ | Y | Y | P | P | Y | Y | Y | Y | Y | Y | P | Y | "Raise maxResultBuffer to a larger size" with no place; bytes only; reader gives no value: "check the pgjdbc documentation" (R3 P). |
| TK | Y | Y | Y | P | Y | Y | Y | P | P | Y | Y | Y | "Result set of 100003200 bytes" presents the running total as the size of the whole result (G8 P); reader: "a single query whose result was 100,003,200 bytes" (R1 P); bytes only. |
| TL | Y | N | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | No why; bytes only. |
| TM | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | "Raise maxResultBuffer, such as maxResultBuffer=1G" names no connection property or URL. |
| TN | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | "set ... to a larger value, for example 100M" equals the current limit (G8 P); reader corrected to 200M. |
| TO | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | |
| TP | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Bytes only; reader reads the overshoot as the full excess ("exceeded the limit by only 3,200 bytes") but still advises headroom. |
| TQ | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Alternative is only "check for a large column or a query that returns more rows than expected" or unset; no fewer-rows or fetch-size action (G6 P). |
| TR | Y | P | Y | P | Y | P | Y | Y | Y | Y | Y | Y | Why is "bounds how many bytes one result set may read", no memory (G2 P); only raise or unset (G6 P); bytes only; reader flags memory as its inference. |
| UA | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | 500M and 10p; fetch size with autocommit off. |
| UB | Y | N | P | P | Y | Y | Y | Y | Y | Y | Y | Y | No why; "raise maxResultBuffer" with no place; bytes only. |
| UC | Y | P | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Why is "buffering more data than the application allowed", memory not named; bytes only. |
| UD | P | N | P | P | Y | P | Y | P | Y | Y | Y | Y | Limit only; no why; no place; "fetch fewer rows at a time" without autocommit off (G6, G8 P). |
| UE | Y | Y | Y | Y | Y | Y | Y | P | P | Y | Y | N | "Result set of 100003200 bytes" as whole-result size (G8 P); reader: "returned 100,003,200 bytes" (R1 P) and invents a default: "doesn't say why 100 MB is the default" (R4 N; default is unset). |
| UF | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | Y | "raise ... (for example maxResultBuffer=100M" equals the current limit (G8 P); reader used 200M. |
| UG | Y | N | P | P | Y | Y | Y | Y | Y | Y | Y | Y | No why; "raise maxResultBuffer" with no place; bytes only. |
| UH | Y | N | P | P | Y | Y | Y | Y | Y | Y | Y | Y | No why; "Raise maxResultBuffer" with no place; bytes only. |
| UI | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | "a value above 100000000 bytes, such as a byte count with a K, M, G, or T suffix"; fetch size with autocommit off. |
| UJ | Y | Y | Y | Y | Y | Y | Y | P | Y | Y | Y | N | "raise maxResultBuffer ... (a size such as 100M" equals the current limit (G8 P); reader: "The overage is about 3 KB, so a modest increase should cover this query" is false, the total stops at the first overflow (R4 N). |
| UK | Y | N | Y | P | Y | P | Y | P | Y | Y | Y | Y | No why; "set a smaller fetchSize" without autocommit off (G6, G8 P); bytes only. |
| UL | Y | N | P | P | Y | Y | Y | Y | Y | Y | Y | Y | No why; "Raise maxResultBuffer" with no place; bytes only. |
| UM | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Example "200000000" is a plain byte count (G4 P). |
| UN | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | Y | Y | "Raise maxResultBuffer, for example to 200M" names no connection property or URL. |
| UO | Y | N | P | P | Y | Y | Y | P | P | Y | Y | Y | "Result set size of 100003200 bytes" as whole-result size (G8 P); no why; no place; reader: "The report result was 100,003,200 bytes" (R1 P). |
| UP | Y | N | P | P | Y | Y | Y | P | Y | Y | Y | Y | No why; no place; "fetch fewer rows with setFetchSize" without autocommit off (G8 P). |
| UQ | Y | Y | Y | P | Y | P | Y | Y | Y | Y | Y | Y | Only raise or unset, no fewer-rows or fetch-size action (G6 P); bytes only. |
| UR | Y | P | P | Y | Y | Y | Y | Y | P | Y | Y | Y | Why is "holding a result set larger than the application allows", memory not named (G2 P); "raise maxResultBuffer, for example to 256M" with no place; reader gives no memory reason: "keeps a result set from growing past the limit the application sets" (R1 P). |

Best:

- UA: every ledger row met, with both a size (500M) and a heap percent (10p), fetch size with autocommit off, and a clean reader reply.
- TG: every ledger row met, states the raise must exceed the current limit, and gives the fetch-size advice with its autocommit condition.
- UI: every ledger row met, lists the accepted K/M/G/T suffixes and ties the raise to a value above the printed limit.

Worst:

- TF: no numbers, no reason, no unit, and no place to set the property; only the connection state and the actions survive.
- UD: limit only, no reason, no place, and fetch-size-style advice without the autocommit condition.
- TC: limit only, no received total, no reason, and no place to set the property.

## Key

| code | run |
| --- | --- |
| TA | sonnet-new-2 |
| TB | haiku-final4-2 |
| TC | haiku-new-1 |
| TD | sonnet-final3-3 |
| TE | haiku-final3-3 |
| TF | haiku-old-2 |
| TG | haiku-final4-1 |
| TH | sonnet-final2-1 |
| TI | haiku-final2-3 |
| TJ | haiku-final4-3 |
| TK | sonnet-final2-2 |
| TL | sonnet-old-2 |
| TM | haiku-final-2 |
| TN | sonnet-final3-1 |
| TO | haiku-final2-2 |
| TP | haiku-final2-1 |
| TQ | haiku-final-3 |
| TR | haiku-final-1 |
| UA | sonnet-final4-3 |
| UB | haiku-new-3 |
| UC | sonnet-final2-3 |
| UD | haiku-old-1 |
| UE | sonnet-final3-2 |
| UF | sonnet-final-1 |
| UG | haiku-new-2 |
| UH | haiku-old-3 |
| UI | sonnet-final4-1 |
| UJ | sonnet-final-2 |
| UK | sonnet-new-1 |
| UL | sonnet-old-3 |
| UM | sonnet-final4-2 |
| UN | haiku-final3-1 |
| UO | sonnet-old-1 |
| UP | sonnet-new-3 |
| UQ | sonnet-final-3 |
| UR | haiku-final3-2 |

## Aggregates

| run | code | G1..G8 | ledger /8 | reader /4 |
| --- | --- | --- | ---: | ---: |
| haiku-final-1 | TR | Y P Y P Y P Y Y | 6.5 | 4 |
| haiku-final-2 | TM | Y Y P Y Y Y Y Y | 7.5 | 4 |
| haiku-final-3 | TQ | Y Y Y Y Y P Y Y | 7.5 | 4 |
| haiku-final2-1 | TP | Y Y Y P Y Y Y Y | 7.5 | 4 |
| haiku-final2-2 | TO | Y Y Y Y Y Y Y Y | 8 | 4 |
| haiku-final2-3 | TI | Y Y Y P Y Y Y Y | 7.5 | 4 |
| haiku-final3-1 | UN | Y Y P Y Y Y Y Y | 7.5 | 4 |
| haiku-final3-2 | UR | Y P P Y Y Y Y Y | 7 | 3.5 |
| haiku-final3-3 | TE | Y Y Y Y N Y Y P | 6.5 | 3.5 |
| haiku-final4-1 | TG | Y Y Y Y Y Y Y Y | 8 | 4 |
| haiku-final4-2 | TB | Y Y Y P Y Y Y Y | 7.5 | 4 |
| haiku-final4-3 | TJ | Y Y P P Y Y Y Y | 7 | 3.5 |
| haiku-new-1 | TC | P N P P Y Y Y Y | 5.5 | 4 |
| haiku-new-2 | UG | Y N P P Y Y Y Y | 6 | 4 |
| haiku-new-3 | UB | Y N P P Y Y Y Y | 6 | 4 |
| haiku-old-1 | UD | P N P P Y P Y P | 4.5 | 4 |
| haiku-old-2 | TF | N N P N Y Y Y Y | 4.5 | 4 |
| haiku-old-3 | UH | Y N P P Y Y Y Y | 6 | 4 |
| sonnet-final-1 | UF | Y Y Y Y Y Y Y P | 7.5 | 4 |
| sonnet-final-2 | UJ | Y Y Y Y Y Y Y P | 7.5 | 3 |
| sonnet-final-3 | UQ | Y Y Y P Y P Y Y | 7 | 4 |
| sonnet-final2-1 | TH | Y Y Y P Y Y Y Y | 7.5 | 3.5 |
| sonnet-final2-2 | TK | Y Y Y P Y Y Y P | 7 | 3.5 |
| sonnet-final2-3 | UC | Y P Y P Y Y Y Y | 7 | 4 |
| sonnet-final3-1 | TN | Y Y Y Y Y Y Y P | 7.5 | 4 |
| sonnet-final3-2 | UE | Y Y Y Y Y Y Y P | 7.5 | 2.5 |
| sonnet-final3-3 | TD | Y Y Y Y Y Y Y P | 7.5 | 3.5 |
| sonnet-final4-1 | UI | Y Y Y Y Y Y Y Y | 8 | 4 |
| sonnet-final4-2 | UM | Y Y Y P Y Y Y Y | 7.5 | 4 |
| sonnet-final4-3 | UA | Y Y Y Y Y Y Y Y | 8 | 4 |
| sonnet-new-1 | UK | Y N Y P Y P Y P | 5.5 | 4 |
| sonnet-new-2 | TA | Y N P P Y P Y P | 5 | 4 |
| sonnet-new-3 | UP | Y N P P Y Y Y P | 5.5 | 4 |
| sonnet-old-1 | UO | Y N P P Y Y Y P | 5.5 | 3.5 |
| sonnet-old-2 | TL | Y N Y P Y Y Y Y | 6.5 | 4 |
| sonnet-old-3 | UL | Y N P P Y Y Y Y | 6 | 4 |

| model | arm | mean ledger /8 | G2 why | G3 property | G4 value forms | G6 alternative | G8 clean | mean reader /4 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| haiku | old | 5.0 | 0/3 | 0/3 | 0/3 | 2/3 | 2/3 | 4.0 |
| haiku | new | 5.8 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 4.0 |
| haiku | final | 7.2 | 2/3 | 2/3 | 2/3 | 1/3 | 3/3 | 4.0 |
| haiku | final2 | 7.7 | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 | 4.0 |
| haiku | final3 | 7.0 | 2/3 | 1/3 | 3/3 | 3/3 | 2/3 | 3.7 |
| haiku | final4 | 7.5 | 3/3 | 2/3 | 1/3 | 3/3 | 3/3 | 3.8 |
| sonnet | old | 6.0 | 0/3 | 1/3 | 0/3 | 3/3 | 2/3 | 3.8 |
| sonnet | new | 5.3 | 0/3 | 1/3 | 0/3 | 1/3 | 0/3 | 4.0 |
| sonnet | final | 7.3 | 3/3 | 3/3 | 2/3 | 2/3 | 1/3 | 3.7 |
| sonnet | final2 | 7.2 | 2/3 | 3/3 | 0/3 | 3/3 | 2/3 | 3.7 |
| sonnet | final3 | 7.5 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 3.3 |
| sonnet | final4 | 7.8 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 4.0 |

## haiku-final-1 (code TR)

### Rendered message

```text
Result set exceeded maxResultBuffer limit. Received: 100003200 bytes; current limit: 100000000 bytes. The limit bounds how many bytes one result set may read, and the driver closes the connection because the rows after this one cannot be read. To allow a larger result set, set the maxResultBuffer connection property to a larger size, or unset it to remove the limit.
```

### Reader reply

```markdown
**1. Failure:** The result set read 100,003,200 bytes against a `maxResultBuffer` limit of 100,000,000, overshooting by only 3,200 bytes. The check caps how many bytes one result set may read. The text doesn't give a reason. Client memory protection is my inference.

**2. Connection:** The driver closed it, so it can't be reused. Uncommitted work on that session is rolled back. The text doesn't say whether the server-side query was cancelled.

**3. Change:** Reconnect with a larger limit, for example `jdbc:postgresql://host:5432/db?maxResultBuffer=200M`. The text doesn't list accepted size formats, so confirm the `M` suffix against your pgjdbc version or use a byte count such as `200000000`. The overshoot was small, so the report will fail again as the data grows.

**4. Alternatives:** Select fewer or smaller columns, or page with keyset pagination, assuming an indexed `id` column: `WHERE id > ? ORDER BY id LIMIT 10000`. Or unset `maxResultBuffer`, which the text allows but removes the guard.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:15:44.179649965 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set exceeded maxResultBuffer limit. Received: {0} bytes; current limit: {1} bytes."
+                + " The limit bounds how many bytes one result set may read, and the driver closes the"
+                + " connection because the rows after this one cannot be read. To allow a larger result"
+                + " set, set the maxResultBuffer connection property to a larger size, or unset it to"
+                + " remove the limit.",
+            String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final-2 (code TM)

### Rendered message

```text
Result set exceeded maxResultBuffer limit. Received: 100003200 bytes; current limit: 100000000 bytes. The limit keeps one large result from exhausting client memory. The connection is closed, because the stream is left in the middle of a message. Raise maxResultBuffer, such as maxResultBuffer=1G, or select fewer columns or rows.
```

### Reader reply

```markdown
**1. What failed:** The report query's result reached 100,003,200 bytes, over the driver's `maxResultBuffer` limit of 100,000,000 bytes. The driver enforces this so one large result can't exhaust client memory. The message doesn't give the full result size, only the point where the check tripped.

**2. Connection state:** The message says the connection is closed because the stream stopped mid-message. I can't verify this here, so reconnect rather than reuse it.

**3. Change:** Add the property to the JDBC URL:

`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=1G`

Or set `props.setProperty("maxResultBuffer", "1G")` on the `Properties` you pass to `DriverManager.getConnection`. The message uses `1G` as its example. It doesn't say whether other suffixes work.

**4. Alternative:** Return less data: select fewer columns, filter rows, or paginate. The message doesn't say whether `setFetchSize` avoids this check, so test it before relying on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:14.173801859 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set exceeded maxResultBuffer limit. Received: {0} bytes;"
+                + " current limit: {1} bytes. The limit keeps one large result from exhausting"
+                + " client memory. The connection is closed, because the stream is left in the middle"
+                + " of a message. Raise maxResultBuffer, such as maxResultBuffer=1G, or select fewer"
+                + " columns or rows.",
+            Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final-3 (code TQ)

### Rendered message

```text
The result set reached 100003200 bytes, over the maxResultBuffer limit of 100000000 bytes. The limit bounds how many bytes of one result set the driver reads into memory. To allow larger results, raise maxResultBuffer, for example with maxResultBuffer=200M in the connection URL, or remove it to read without a limit. To find the cause, check for a large column or a query that returns more rows than expected. The connection is closed, because the rest of the row is left unread.
```

### Reader reply

```markdown
**1. What failed.** The query's result reached 100,003,200 bytes, over the `maxResultBuffer` limit of 100,000,000 bytes. The limit bounds how much of one result set the driver reads into memory. The text doesn't say more about why the check exists.

**2. Connection state.** Closed, because the rest of the row was left unread. The text doesn't say whether your pool reconnects automatically.

**3. Change.** Add the option to the JDBC URL, using `&` if parameters already exist:

`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M`

Then reconnect. Also check the query: the text points to a large column or an unexpected row count. `SELECT count(*)` and `pg_column_size(col)` on suspect columns will show which. I can't see your URL, host, or database name.

**4. Alternative.** Return less data: select fewer or smaller columns, or page with keyset pagination, such as `WHERE id > :last ORDER BY id LIMIT 1000`.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:04.670452693 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "The result set reached {0} bytes, over the maxResultBuffer limit of {1} bytes."
+                + " The limit bounds how many bytes of one result set the driver reads into memory."
+                + " To allow larger results, raise maxResultBuffer, for example with"
+                + " maxResultBuffer=200M in the connection URL, or remove it to read without a limit."
+                + " To find the cause, check for a large column or a query that returns more rows"
+                + " than expected. The connection is closed, because the rest of the row is left unread.",
+            Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final2-1 (code TP)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes; it reached 100003200 bytes. The limit keeps one result set from using more client memory than the connection allows. To stay under it, select fewer or narrower columns, or add a LIMIT clause. To accept results this large, raise the maxResultBuffer connection property. The connection is closed, because the unread rows leave the stream out of step with the protocol.
```

### Reader reply

```markdown
**1. What failed:** The report query returned more data than the driver's `maxResultBuffer` limit of 100,000,000 bytes. It reached 100,003,200 bytes. The check caps how much client memory one result set can use.

**2. Connection state:** Closed. Unread rows left the stream out of sync with the protocol, so the driver closed the connection. Open a new one before retrying.

**3. What to change:** Raise the limit on the connection, for example in the JDBC URL:

```
jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200000000
```

You can also pass `maxResultBuffer` as a connection property. The result exceeded the limit by only 3,200 bytes, so choose a value with headroom. The text doesn't say whether your application's heap can hold a larger result.

**4. Alternative:** Select fewer or narrower columns, or add a `LIMIT` clause and page through the results.

The text doesn't say whether the limit is already set somewhere, or how many rows the report needs.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:39:05.430894180 +0300
@@ -1014,7 +1014,13 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        String message = GT.tr("Result set exceeded the maxResultBuffer limit of {1} bytes; it reached {0} bytes."
+            + " The limit keeps one result set from using more client memory than the connection allows."
+            + " To stay under it, select fewer or narrower columns, or add a LIMIT clause."
+            + " To accept results this large, raise the maxResultBuffer connection property."
+            + " The connection is closed, because the unread rows leave the stream out of step with the protocol.",
+            String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer));
+        throw new PSQLException(message, PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final2-2 (code TO)

### Rendered message

```text
The result set has read 100003200 bytes, more than the maxResultBuffer limit of 100000000 bytes. The limit keeps one result set from filling the memory of the application. Select fewer rows or fewer columns, for example with a LIMIT clause, or raise the limit, for example with maxResultBuffer=256M in the connection URL. The driver closes the connection here, so the rest of the result set is lost, and the next query needs a new connection.
```

### Reader reply

```markdown
**1. What failed:** The report query returned 100,003,200 bytes, over the driver's `maxResultBuffer` limit of 100,000,000 bytes. The driver caps how much one result set can hold, so a single query can't fill the application's memory.

**2. Connection state:** Closed. The driver dropped it, so the rest of the result is lost, and the next query needs a new connection.

**3. Change:** Add the parameter to the JDBC URL your application uses:

```
jdbc:postgresql://<host>:<port>/<database>?maxResultBuffer=256M
```

Replace the placeholders with your existing values. The text doesn't show your current URL or heap size, so confirm that 256M fits your heap.

**4. Alternative:** Keep the limit and make the query return less data, either with a `LIMIT` clause or by selecting fewer columns.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:39:15.353474746 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "The result set has read {0} bytes, more than the maxResultBuffer limit of {1} bytes. "
+                + "The limit keeps one result set from filling the memory of the application. "
+                + "Select fewer rows or fewer columns, for example with a LIMIT clause, or raise the limit, "
+                + "for example with maxResultBuffer=256M in the connection URL. "
+                + "The driver closes the connection here, so the rest of the result set is lost, "
+                + "and the next query needs a new connection.",
+            Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final2-3 (code TI)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes after 100003200 bytes were read. The limit keeps the driver from buffering an unbounded result set in memory. The connection is no longer usable, because the rest of the result is still on the wire. Select fewer or narrower columns, or split the query into pages, so that each result set stays under the limit. If results this large are expected, raise maxResultBuffer in the connection properties.
```

### Reader reply

```markdown
**1. Failure.** The report query returned more than `maxResultBuffer`, the driver's 100,000,000-byte cap. The driver stopped after reading 100,003,200 bytes. The check keeps the driver from buffering an unbounded result set in memory.

**2. Connection.** Per the message, it is unusable because the rest of the result is still on the wire. Close it and open a new one.

**3. Change.** Either:
- Select fewer columns, and page by key, for example `SELECT ... FROM report WHERE id > ? ORDER BY id LIMIT 10000`, passing the last `id` each time.
- Or raise the cap in the JDBC URL: `jdbc:postgresql://host:5432/db?maxResultBuffer=200000000`. If the URL already has `?`, use `&` instead.

I can't see your query or connection setup, so I can't give exact lines.

**4. Alternative.** Paging with fewer columns keeps memory bounded without raising the cap.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:39:06.442861552 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set exceeded the maxResultBuffer limit of {0} bytes after {1} bytes were read."
+                + " The limit keeps the driver from buffering an unbounded result set in memory."
+                + " The connection is no longer usable, because the rest of the result is still on"
+                + " the wire. Select fewer or narrower columns, or split the query into pages, so that"
+                + " each result set stays under the limit. If results this large are expected, raise"
+                + " maxResultBuffer in the connection properties.",
+            String.valueOf(maxResultBuffer), String.valueOf(resultBufferByteCount)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final3-1 (code UN)

### Rendered message

```text
Result set exceeded maxResultBuffer: 100003200 bytes, over the limit of 100000000 bytes. The limit bounds the memory one result set may use. The connection is dropped, because the rest of the result cannot be read in step with the protocol. Raise maxResultBuffer, for example to 200M, or limit the rows or the columns the query returns.
```

### Reader reply

```markdown
**1. What failed.** The report query's result set reached 100,003,200 bytes, over the driver's `maxResultBuffer` limit of 100,000,000 bytes. The check caps the memory one result set can use, so the driver stops instead of buffering without bound.

**2. Connection state.** The text says the connection was dropped. Treat it as closed and reconnect.

**3. What to change.** In pgjdbc, `maxResultBuffer` is a connection property, so add it to the JDBC URL:

```
jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M
```

Restart the app or connection pool so new connections use it. I can't see where your application builds its URL.

**4. Alternative.** Return fewer rows or columns: add a `WHERE` filter, select only the columns you need, or aggregate in SQL. The text doesn't say whether `setFetchSize` avoids this limit, so test it before relying on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:44.741921004 +0300
@@ -1014,7 +1014,12 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer: {0} bytes, over the limit of {1} bytes."
+            + " The limit bounds the memory one result set may use. The connection is dropped, because the rest"
+            + " of the result cannot be read in step with the protocol. Raise maxResultBuffer, for example to"
+            + " 200M, or limit the rows or the columns the query returns.",
+            String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final3-2 (code UR)

### Rendered message

```text
Result set grew to 100003200 bytes, over the maxResultBuffer limit of 100000000 bytes. The limit keeps the driver from holding a result set larger than the application allows, and the connection is closed. Select fewer rows or narrower columns, or raise maxResultBuffer, for example to 256M, if the whole result set is needed.
```

### Reader reply

```markdown
**1. What failed:** The report's result set reached 100,003,200 bytes, over the `maxResultBuffer` cap of 100,000,000 bytes. The driver keeps a result set from growing past the limit the application sets.

**2. Connection state:** The message says the connection is closed. I can't see the application code, so I don't know whether it reconnects. Check `connection.isClosed()` before reusing the connection.

**3. Change:** Add the property to the JDBC URL and reconnect:

`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=256M`

Replace `HOST` and `DBNAME` with your values. If the URL is built in code, set the `maxResultBuffer` property to `256M` there. The new value applies only to new connections, so restart the app. The message doesn't say how large the report can get, so 256M may not be enough.

**4. Alternatives:** Select fewer rows or narrower columns, or fetch the report in pages with `LIMIT`/`OFFSET` or keyset pagination. The message doesn't say whether `fetchSize` gets around the limit, so test it before relying on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:58.908615473 +0300
@@ -1014,7 +1014,9 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set grew to {0} bytes, over the maxResultBuffer limit of {1} bytes. The limit keeps the driver from holding a result set larger than the application allows, and the connection is closed. Select fewer rows or narrower columns, or raise maxResultBuffer, for example to 256M, if the whole result set is needed.",
+            String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)), PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final3-3 (code TE)

### Rendered message

```text
Result set exceeded maxResultBuffer limit: the result reached 100003200 bytes, and the limit is 100000000 bytes. The limit keeps one result set from holding more memory than the client allows. Narrow the query with a WHERE or LIMIT clause, or select fewer or smaller columns, to stay under it. To accept a result this large, raise maxResultBuffer, for example to 64M, in the connection URL or the driver properties.
```

### Reader reply

```markdown
**1. What failed:** The query result reached 100,003,200 bytes, over the `maxResultBuffer` limit of 100,000,000 bytes. The driver caps this so one result set can't use more client memory than allowed.

**2. Connection state:** The text doesn't say whether the connection is still usable, whether it's in a transaction, or whether the statement was closed. Roll back and close the connection, or check its state before reusing it.

**3. Change:** Don't use the message's example of 64M. It's below the current limit, so the query would still fail. Use a larger value, such as 256M, in the URL:

`jdbc:postgresql://HOST:PORT/DB?maxResultBuffer=256M`

Or set it as a driver property:

`props.setProperty("maxResultBuffer", "256M");`

Size it above your largest expected result.

**4. Alternatives:** Add a `WHERE` or `LIMIT` clause, or select fewer or smaller columns. The text doesn't say whether streaming with `setFetchSize` and autocommit off avoids this limit, so verify that before relying on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:54.343645010 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer limit: the result reached {0} bytes, and the"
+                + " limit is {1} bytes. The limit keeps one result set from holding more memory than"
+                + " the client allows. Narrow the query with a WHERE or LIMIT clause, or select fewer"
+                + " or smaller columns, to stay under it. To accept a result this large, raise"
+                + " maxResultBuffer, for example to 64M, in the connection URL or the driver properties.",
+                String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final4-1 (code TG)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes: reading the next row would bring the total to 100003200 bytes. The limit keeps one result set from holding more memory than the connection is allowed to use. The connection is closed, so the rest of the result cannot be read. To read fewer rows in each round trip, set a smaller fetch size with Statement.setFetchSize on a connection with autocommit off. To keep the rows in one result, raise the maxResultBuffer connection property to a size above 100000000 bytes, written as a byte count or with a suffix such as 2G.
```

### Reader reply

```markdown
**1. What failed:** The report's result set grew past the driver's `maxResultBuffer` limit of 100,000,000 bytes. The driver enforces this so one result cannot use more memory than the connection is allowed.

**2. Connection state:** Closed. The rest of the result cannot be read on this connection. The text does not say whether any rows were processed before the failure.

**3. Change:** Pick one:
- **Read in batches:** call `connection.setAutoCommit(false);`, then `statement.setFetchSize(1000);`. The value 1000 is only an example.
- **Raise the limit:** set the connection property `maxResultBuffer` to `2G`. The text does not say how to pass it, so add it to the JDBC URL or `Properties` as your setup allows.

**4. Alternative:** Use the fetch-size approach, or make the query return fewer rows or columns. The message does not confirm that fetch-size reads avoid the limit, so test it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:49:02.301185041 +0300
@@ -1014,7 +1014,16 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit of {0} bytes: reading the next row "
+                + "would bring the total to {1} bytes. The limit keeps one result set from holding "
+                + "more memory than the connection is allowed to use. The connection is closed, so "
+                + "the rest of the result cannot be read. To read fewer rows in each round trip, set "
+                + "a smaller fetch size with Statement.setFetchSize on a connection with autocommit "
+                + "off. To keep the rows in one result, raise the maxResultBuffer connection property "
+                + "to a size above {0} bytes, written as a byte count or with a suffix such as 2G.",
+                Long.toString(maxResultBuffer), Long.toString(resultBufferByteCount)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final4-2 (code TB)

### Rendered message

```text
Result set exceeded maxResultBuffer: read 100003200 bytes, past the limit of 100000000 bytes. The limit bounds the memory the rows of one query may take, and the connection is closed because the remaining rows cannot be read. To read all the rows, raise maxResultBuffer in the connection URL or properties. To stay under the limit, select fewer or smaller columns, or limit the number of rows the query returns.
```

### Reader reply

```markdown
**1. What failed.** One query's result exceeded `maxResultBuffer`, the 100,000,000-byte cap on memory that one query's rows may use. The driver read 100,003,200 bytes before stopping. The check keeps a large result from exhausting the application's memory.

**2. Connection state.** Closed. The driver closed it because the remaining rows can't be read. Open a new connection before retrying.

**3. What to change.** Raise `maxResultBuffer` in the JDBC URL, above the full result size:

`jdbc:postgresql://HOST:5432/DB?maxResultBuffer=200000000`

The text doesn't say whether suffixes like `200M` are accepted, or how large the full result is, so choose the value from your data size.

**4. Alternative.** Select fewer or smaller columns, or limit the rows returned (for example with `LIMIT` and `OFFSET` pages), so each result stays under the limit.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:48:54.400981491 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: read {0} bytes, past the limit of {1} bytes."
+                + " The limit bounds the memory the rows of one query may take, and the connection is"
+                + " closed because the remaining rows cannot be read. To read all the rows, raise"
+                + " maxResultBuffer in the connection URL or properties. To stay under the limit, select"
+                + " fewer or smaller columns, or limit the number of rows the query returns.",
+                String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-final4-3 (code TJ)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes, with 100003200 bytes read. The limit keeps one result set from filling client memory. Raise maxResultBuffer to a larger size, or make the query return fewer or narrower rows, for example with a WHERE or LIMIT clause. The connection is closed, because the rest of the result set cannot be read.
```

### Reader reply

```markdown
**1. What failed:** The result set grew past `maxResultBuffer`, the driver's cap of 100,000,000 bytes per result set. It read 100,003,200 bytes. The check keeps one large result from exhausting client memory.

**2. Connection state:** The connection is closed. The text doesn't say whether an open transaction was rolled back, so open a new connection before running more queries.

**3. What to change:** Raise `maxResultBuffer` in the connection settings. The text doesn't give the value format or whether it goes in the JDBC URL or in `Properties`, so check the pgjdbc documentation for your driver version. To shrink the result, add a `WHERE` filter or a `LIMIT` to the report query, or select only the columns you need.

**4. Alternative:** Keep the default limit and make the query return fewer or narrower rows, as above. The text doesn't say whether paging the query would help.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:48:51.801609154 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit of {1} bytes, with {0} bytes read. "
+                + "The limit keeps one result set from filling client memory. "
+                + "Raise maxResultBuffer to a larger size, or make the query return fewer or narrower rows, "
+                + "for example with a WHERE or LIMIT clause. "
+                + "The connection is closed, because the rest of the result set cannot be read.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-new-1 (code TC)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes. Raise maxResultBuffer, or select fewer or smaller rows. The connection is closed.
```

### Reader reply

```markdown
**1. What failed:** The report query's result exceeded `maxResultBuffer` (100,000,000 bytes, about 95 MiB). The driver buffers results in client memory, and this check caps that so one large query can't exhaust the JVM heap. The text doesn't say how many rows were returned.

**2. Connection state:** Closed. Open a new connection. The text doesn't say whether an open transaction was rolled back, so treat any uncommitted work from that session as lost.

**3. Change:** Add the property to the JDBC URL:

```
jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200000000
```

Use `&` instead of `?` if the URL already has parameters. The value is in bytes. The text doesn't say whether suffixes like `200M` are accepted.

**4. Alternatives:** Select fewer or smaller columns, or page with `LIMIT`/`OFFSET` or keyset paging. Or stream rows by calling `connection.setAutoCommit(false)` and `statement.setFetchSize(1000)`. The text doesn't say whether streaming avoids this limit in your driver version, so verify it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:15:45.732329607 +0300
@@ -1014,7 +1014,10 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set exceeded the maxResultBuffer limit of {0} bytes. Raise maxResultBuffer, or"
+                + " select fewer or smaller rows. The connection is closed.",
+            String.valueOf(maxResultBuffer)), PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-new-2 (code UG)

### Rendered message

```text
Result set exceeded maxResultBuffer limit of 100000000 bytes after 100003200 bytes were received. The connection is closed; raise maxResultBuffer or select fewer rows.
```

### Reader reply

```markdown
**1. What failed:** The driver stopped the query because the result passed `maxResultBuffer`, set to 100,000,000 bytes (about 100 MB). The check is a client-side guard that keeps the JVM from buffering an unbounded result set in memory. The text doesn't say which query or how many rows.

**2. Connection state:** The message says the connection is closed. Don't reuse it. Open a new one before retrying. The text doesn't say whether any transaction was rolled back.

**3. What to change:** Raise the limit in the JDBC URL. Use bytes, since the text doesn't confirm unit suffixes:

```
jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200000000
```

Choose a value above your largest expected report.

**4. Alternatives:** Select fewer columns or rows, or aggregate in SQL. Or set `fetchSize` (for example, `1000`) on the statement with autocommit off, so rows arrive in batches. The text doesn't confirm that this avoids the limit, so test it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:15:40.548989347 +0300
@@ -1014,7 +1014,11 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer limit of {1} bytes after {0} bytes were received. "
+                + "The connection is closed; raise maxResultBuffer or select fewer rows.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-new-3 (code UB)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes after 100003200 bytes were received. Select fewer or smaller rows, or raise maxResultBuffer. The connection is no longer usable.
```

### Reader reply

```markdown
**1. What failed:** The query's result reached 100,003,200 bytes, past the driver's `maxResultBuffer` cap of 100,000,000 bytes. The cap keeps one large result from exhausting client memory. The text doesn't say which query or columns caused it.

**2. Connection state:** The message says the connection is no longer usable. Close it and open a new one. The text doesn't say whether the server cancelled the query.

**3. If you raise the limit:** Add the parameter to the JDBC URL:
`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M`
The `200M` suffix format comes from my knowledge of the driver, not this text. Confirm it against your driver version, and pick a size your heap can hold.

**4. Alternatives:** Select only needed columns, add a `WHERE` clause or `LIMIT`, or page through rows with keyset pagination. The text doesn't say whether `setFetchSize` avoids this limit, so test that before relying on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:15:44.490875639 +0300
@@ -1014,7 +1014,12 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        // Pass the counts as text so that MessageFormat does not group their digits by locale.
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit of {1} bytes after {0} bytes were received."
+                + " Select fewer or smaller rows, or raise maxResultBuffer. The connection is no longer usable.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-old-1 (code UD)

### Rendered message

```text
Result set exceeded maxResultBuffer limit of 100000000 bytes. Raise maxResultBuffer or fetch fewer rows at a time. The connection is closed, because the unread part of the row leaves the stream out of sync.
```

### Reader reply

```markdown
**1. What failed:** The query's result exceeded the driver's `maxResultBuffer` cap of 100,000,000 bytes (about 100 MB). The cap likely bounds client memory use, but the text doesn't state its purpose.

**2. Connection state:** Closed. Discard it and open a new one.

**3. Raise the limit:** Add the parameter to the JDBC URL, choosing a value your report needs:
```
jdbc:postgresql://host:5432/dbname?maxResultBuffer=300M
```
The text doesn't say where your code sets the URL, so check there.

**4. Alternative:** Fetch in batches. Disable autocommit, then call `statement.setFetchSize(1000);` before executing. The driver ignores fetch size when autocommit is on. I can't tell whether your code already does this.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:08.559290179 +0300
@@ -1014,7 +1014,11 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer limit of {0} bytes. Raise maxResultBuffer or fetch"
+                + " fewer rows at a time. The connection is closed, because the unread part of the row"
+                + " leaves the stream out of sync.", String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-old-2 (code TF)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit. Raise maxResultBuffer, or select fewer rows or columns. The connection is out of sync with the server and must not be reused.
```

### Reader reply

```markdown
1. **What failed:** One query's result grew past the driver's `maxResultBuffer` cap, so the driver aborted. The check bounds client memory when a whole result is buffered. The text doesn't give the configured limit or the result size.

2. **Connection state:** It is out of sync with the server. Close it and don't return it to the pool. The text doesn't say whether the server-side transaction was rolled back.

3. **Change:** Raise the limit in the JDBC URL, for example `jdbc:postgresql://HOST:5432/DB?maxResultBuffer=500M`. Choose a value that fits your heap; I can't see your setup.

4. **Alternatives:** Select fewer rows or columns, using a `WHERE` or `LIMIT`. Or stream: turn off autocommit and call `setFetchSize(1000)` on the statement. I haven't verified that this avoids the limit with your driver version.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:11.691085903 +0300
@@ -1014,7 +1014,9 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr("Result set exceeded the maxResultBuffer limit. Raise"
+            + " maxResultBuffer, or select fewer rows or columns. The connection is out of sync"
+            + " with the server and must not be reused."), PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## haiku-old-3 (code UH)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit. Received: 100003200 bytes; current limit: 100000000 bytes. The connection is no longer usable. Raise maxResultBuffer, or select fewer rows or columns.
```

### Reader reply

```markdown
**1. What failed:** The driver stopped reading the report because the buffered result passed `maxResultBuffer`. It had received 100,003,200 bytes against a 100,000,000-byte cap. The check keeps a large result from exhausting the JVM heap. The text doesn't say whether the final result would have been larger.

**2. Connection state:** Unusable, per the message. Close it and discard it. Don't return it to a pool. The text doesn't say whether the transaction was rolled back.

**3. Change:** Raise the limit in the JDBC URL, above the observed size:

```
jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M
```

Replace `HOST` and `DBNAME` with your values. I can't see your URL or config, and I haven't verified that the `200M` suffix parses in your driver version. Check your pgjdbc docs, then rerun the report.

**4. Alternative:** Select fewer columns or rows, or page through results with `ORDER BY` plus `LIMIT`/`OFFSET` or keyset pagination. Choose this if the report can accept smaller pages.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:13.584621135 +0300
@@ -1014,7 +1014,11 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit. Received: {0} bytes; current limit: {1} bytes. "
+                + "The connection is no longer usable. Raise maxResultBuffer, or select fewer rows or columns.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final-1 (code UF)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit of 100000000 bytes after reading 100003200 bytes. The limit stops a large result set from exhausting the client heap, and the connection is closed because the rest of the result is not read. Select fewer rows or columns, raise maxResultBuffer in the connection URL or properties (for example maxResultBuffer=100M, or a percent of the maximum heap such as maxResultBuffer=10p), or leave maxResultBuffer unset to remove the limit.
```

### Reader reply

```markdown
**1. What failed:** The result set grew past `maxResultBuffer`, set to 100,000,000 bytes (about 100 MB). The driver stopped after reading 100,003,200 bytes. The check protects the client heap from very large results. The text doesn't give the full result size.

**2. Connection state:** Closed. The driver closed it because the rest of the result wasn't read, so discard it and reconnect.

**3. Change:** Add the property to your JDBC URL:

```
jdbc:postgresql://host:5432/dbname?maxResultBuffer=200M
```

The overage is small, but the text doesn't give the full size, so 200M may not be enough. Alternatively, use `maxResultBuffer=10p`, which the text describes as a percent of max heap.

**4. Alternatives:** Select fewer rows or columns. Or leave `maxResultBuffer` unset to remove the limit, which risks exhausting client heap on large results. The text doesn't mention streaming or fetch-size options.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:30.370062699 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit of {0} bytes after reading {1} bytes."
+                    + " The limit stops a large result set from exhausting the client heap, and the connection"
+                    + " is closed because the rest of the result is not read."
+                    + " Select fewer rows or columns, raise maxResultBuffer in the connection URL or"
+                    + " properties (for example maxResultBuffer=100M, or a percent of the maximum heap"
+                    + " such as maxResultBuffer=10p), or leave maxResultBuffer unset to remove the limit.",
+                Long.toString(maxResultBuffer), Long.toString(resultBufferByteCount)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final-2 (code UJ)

### Rendered message

```text
Result set exceeded the maxResultBuffer limit: 100003200 bytes read, limit is 100000000 bytes. The limit keeps a query from buffering more result data than the client can hold. The driver closed the connection because the rest of the result cannot be read. To allow larger results, raise maxResultBuffer in the connection properties (a size such as 100M, or a percent of the maximum heap such as 10p), or unset it to remove the limit. Otherwise, select fewer rows or columns.
```

### Reader reply

```markdown
1. **What failed:** The query's result exceeded the driver's `maxResultBuffer` limit. About 100,003,200 bytes were read against a 100,000,000-byte limit. The check keeps one query from buffering more data in client memory than the application can hold.

2. **Connection state:** The driver closed the connection. The text doesn't say whether a transaction was rolled back, so open a new connection before retrying.

3. **Change:** Add the property to the JDBC URL, for example:
`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M`
The overage is about 3 KB, so a modest increase should cover this query. To remove the limit, drop the property. The text doesn't say how much heap your application has, so `maxResultBuffer=10p` (10% of max heap) is a sizing option only if that fits your memory.

4. **Alternative:** Select fewer rows or columns in the report query. The text doesn't describe other options.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:34.996374662 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer limit: {0} bytes read, limit is {1} bytes. "
+                + "The limit keeps a query from buffering more result data than the client can hold. "
+                + "The driver closed the connection because the rest of the result cannot be read. "
+                + "To allow larger results, raise maxResultBuffer in the connection properties "
+                + "(a size such as 100M, or a percent of the maximum heap such as 10p), "
+                + "or unset it to remove the limit. Otherwise, select fewer rows or columns.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final-3 (code UQ)

### Rendered message

```text
Result set exceeded maxResultBuffer: read 100003200 bytes, the limit is 100000000 bytes. The limit keeps a large result set from exhausting the memory of the application. The driver closed the connection because the rest of the result set was not read. If the result set is expected to be that large, raise the maxResultBuffer connection property, or leave it unset to remove the limit.
```

### Reader reply

```markdown
**1. Failure:** The driver read 100,003,200 bytes, which exceeded the `maxResultBuffer` limit of 100,000,000 bytes. The check stops one large result set from exhausting application memory. The text does not give the full result size.

**2. Connection:** The driver closed it. The text does not say whether an open transaction was rolled back, so assume uncommitted work is lost.

**3. Change:** Raise the limit in the JDBC URL:

`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=300000000`

Use bytes, since the text does not say whether suffixes like `300M` work. Choose a value above the expected result size, and confirm the application has enough heap to hold the result.

**4. Alternative:** Keep the limit and shrink the result. Select fewer columns, aggregate in SQL, or page with `LIMIT`/`OFFSET` or keyset pagination.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:39.706381191 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: read {0} bytes, the limit is {1} bytes. "
+                    + "The limit keeps a large result set from exhausting the memory of the application. "
+                    + "The driver closed the connection because the rest of the result set was not read. "
+                    + "If the result set is expected to be that large, raise the maxResultBuffer connection property, "
+                    + "or leave it unset to remove the limit.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final2-1 (code TH)

### Rendered message

```text
Result set exceeded maxResultBuffer: 100003200 bytes read, limit is 100000000 bytes. The limit keeps a result set from holding more client memory than that, and the connection can no longer be used. Fetch fewer rows at a time by setting fetchSize on the statement (autocommit must be off), or raise the maxResultBuffer connection property if results this large are expected.
```

### Reader reply

```markdown
**1. What failed and why:** The report query returned more data than the driver allows. It had read 100,003,200 bytes against a `maxResultBuffer` limit of 100,000,000. The check caps how much client memory one result set can hold.

**2. Connection state:** The error says the connection can no longer be used. Close it and open a new one. The error doesn't say whether other statements on it are affected.

**3. What to change:**
- **Stream the rows (preferred):** Call `connection.setAutoCommit(false);`, then `statement.setFetchSize(1000);` before executing the query. The error doesn't give a required fetch size, so 1000 is only a starting value.
- **Raise the limit:** Set the `maxResultBuffer` connection property above your expected result size. The error doesn't say what format the value takes, so check your driver version's documentation.

**4. Alternative:** Reduce the result instead, by selecting fewer columns, adding a `WHERE` filter, or aggregating in SQL.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:38:58.095483916 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: {0} bytes read, limit is {1} bytes. "
+                + "The limit keeps a result set from holding more client memory than that, "
+                + "and the connection can no longer be used. "
+                + "Fetch fewer rows at a time by setting fetchSize on the statement (autocommit must be off), "
+                + "or raise the maxResultBuffer connection property if results this large are expected.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final2-2 (code TK)

### Rendered message

```text
Result set of 100003200 bytes exceeds the maxResultBuffer limit of 100000000 bytes. The limit keeps one query from buffering more than that much of the result in driver memory, and the connection is closed because the rest of the result is not read. Fetch the rows in batches by calling Statement.setFetchSize with autocommit off, or select fewer rows or columns. If results this large are expected, raise the maxResultBuffer connection property.
```

### Reader reply

```markdown
1. **What failed:** The driver rejected a single query whose result was 100,003,200 bytes, above the `maxResultBuffer` limit of 100,000,000 bytes. The check stops one query from buffering an unbounded result in driver memory.

2. **Connection state:** Per the message, the connection is closed because the unread rest of the result was never drained. Discard it and open a new one. If you use a pool, evict it.

3. **Changes:**
   - **Batched reads (preferred):** call `conn.setAutoCommit(false);`, then `stmt.setFetchSize(1000);` before `stmt.executeQuery(sql)`, and read rows in a loop.
   - **Raise the limit:** append `?maxResultBuffer=200000000` (or `&maxResultBuffer=...` if the URL already has parameters) to the JDBC URL. Choose a value above 100003200.

4. **Alternative:** Select fewer rows or columns, or add a `WHERE` or `LIMIT` clause.

The text doesn't say the query, row count, or whether a pool is used, and I can't check the property syntax for your driver version.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:38:57.815839830 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set of {0} bytes exceeds the maxResultBuffer limit of {1} bytes. "
+                    + "The limit keeps one query from buffering more than that much of the result in driver memory, "
+                    + "and the connection is closed because the rest of the result is not read. "
+                    + "Fetch the rows in batches by calling Statement.setFetchSize with autocommit off, "
+                    + "or select fewer rows or columns. "
+                    + "If results this large are expected, raise the maxResultBuffer connection property.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final2-3 (code UC)

### Rendered message

```text
Result set exceeded maxResultBuffer: 100003200 bytes read, limit is 100000000 bytes. The limit keeps one result set from buffering more data than the application allowed, and the connection is now closed because the rest of the row was not read. Fetch fewer rows at a time with Statement.setFetchSize (autocommit must be off), or raise the maxResultBuffer connection property if results this large are expected.
```

### Reader reply

```markdown
**1. What failed:** The result set reached 100,003,200 bytes, over the 100,000,000-byte `maxResultBuffer` limit. The driver enforces this cap so one result set can't fill client memory without bound.

**2. Connection state:** The error says the connection is closed. I can't verify that from here, so open a new connection before retrying.

**3. What to change:**

Option A (recommended): stream rows with a fetch size.
```java
connection.setAutoCommit(false);
try (Statement st = connection.createStatement()) {
    st.setFetchSize(1000);
    try (ResultSet rs = st.executeQuery(sql)) { /* read rows */ }
}
connection.commit();
```

Option B: raise the limit in the JDBC URL:
`jdbc:postgresql://host:5432/db?maxResultBuffer=200000000`

I can't confirm from the text whether your driver version accepts unit suffixes like `200M`, so use the byte count.

**4. Alternative:** Select fewer or narrower columns, or aggregate in SQL. The text doesn't say whether a single row larger than the limit would still fail, so check that if Option A doesn't help.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:39:05.225254255 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: {0} bytes read, limit is {1} bytes. "
+                + "The limit keeps one result set from buffering more data than the application "
+                + "allowed, and the connection is now closed because the rest of the row was not read. "
+                + "Fetch fewer rows at a time with Statement.setFetchSize (autocommit must be off), "
+                + "or raise the maxResultBuffer connection property if results this large are expected.",
+                String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final3-1 (code TN)

### Rendered message

```text
Result set read 100003200 bytes, which exceeds the maxResultBuffer limit of 100000000 bytes. The limit keeps a result set from using more client memory than that, and the connection was closed because the rest of the result could not be read. Fetch fewer rows per round trip with Statement.setFetchSize (autocommit must be off), or set the maxResultBuffer connection property to a larger value, for example 100M.
```

### Reader reply

```markdown
**1. What failed:** The query returned 100,003,200 bytes, over the driver's `maxResultBuffer` limit of 100,000,000 bytes. The driver caps result-set size so one query can't exhaust client memory.

**2. Connection state:** Closed. The message says the driver closed it because the rest of the result couldn't be read, so reconnect before retrying.

**3. Changes (choose one):**
- **Stream the rows:** Turn autocommit off, then set a fetch size before executing:
  ```java
  conn.setAutoCommit(false);
  stmt.setFetchSize(1000);
  ```
  Commit or roll back when finished. The message doesn't say whether this avoids the limit for your query, so test it.
- **Raise the limit:** Append `?maxResultBuffer=200M` to the JDBC URL, or set the `maxResultBuffer` property to `200M`.

**4. Alternative:** Reduce the result size in SQL with a narrower column list, a `WHERE` filter, or aggregation.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:47.094389070 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set read {0} bytes, which exceeds the maxResultBuffer limit of {1} bytes. "
+                    + "The limit keeps a result set from using more client memory than that, and the "
+                    + "connection was closed because the rest of the result could not be read. "
+                    + "Fetch fewer rows per round trip with Statement.setFetchSize (autocommit must be "
+                    + "off), or set the maxResultBuffer connection property to a larger value, "
+                    + "for example 100M.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final3-2 (code UE)

### Rendered message

```text
Result set of 100003200 bytes exceeds maxResultBuffer=100000000 bytes, and the connection was closed. The limit keeps one result set from holding more client memory than that. Select fewer rows or columns, for example with LIMIT, or raise the maxResultBuffer connection property, for example to 200M or to a percent of the maximum heap such as 20p.
```

### Reader reply

```markdown
**1. What failed:** The report query returned 100,003,200 bytes, which exceeds the `maxResultBuffer` limit of 100,000,000 bytes (about 100 MB). The driver checks this so one result set can't hold more client memory than the limit allows. The message doesn't say why 100 MB is the default.

**2. Connection state:** Closed. The message says "the connection was closed," so you need a new connection.

**3. Change:** Set the connection property `maxResultBuffer` to `200M`, or to `20p` (20% of max heap). The message doesn't say where to set it. Standard pgjdbc usage is the JDBC URL, for example `jdbc:postgresql://host:5432/db?maxResultBuffer=200M`, but confirm that for your driver version.

**4. Alternative:** Add a `LIMIT` to the query, or select fewer rows or columns. The message doesn't mention paging or streaming.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:54.755128990 +0300
@@ -1014,7 +1014,14 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set of {0} bytes exceeds maxResultBuffer={1} bytes, and the connection was closed."
+                + " The limit keeps one result set from holding more client memory than that."
+                + " Select fewer rows or columns, for example with LIMIT,"
+                + " or raise the maxResultBuffer connection property,"
+                + " for example to 200M or to a percent of the maximum heap such as 20p.",
+                String.valueOf(resultBufferByteCount), String.valueOf(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final3-3 (code TD)

### Rendered message

```text
Result set exceeded maxResultBuffer=100000000 bytes after reading 100003200 bytes of row data. The limit keeps a result set from using more client memory than that, so the driver stopped reading and the connection can no longer be used. Select fewer rows or columns, for example with a LIMIT clause, or raise the maxResultBuffer connection property, for example to 100M (100 MB) or to 10p (10 percent of the maximum heap), if results this large are expected.
```

### Reader reply

```markdown
**1. What failed.** The report returned more row data than the `maxResultBuffer` limit of 100,000,000 bytes. The driver stopped after reading 100,003,200 bytes. The check caps how much client memory one result set can use.

**2. Connection state.** Unusable. Close it and don't return it to a pool.

**3. Change.** Add the property to the JDBC URL:

`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=100M`

Or put `maxResultBuffer=100M` in the `Properties` passed to `DriverManager.getConnection`.

**4. Alternatives.** Select fewer rows or columns, for example with `LIMIT`. Or use `maxResultBuffer=10p` to cap the buffer at 10 percent of max heap instead of a fixed size.

The text doesn't say how large your reports can get, or whether a cursor or fetch size avoids the limit.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:43:52.291876812 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(GT.tr(
+            "Result set exceeded maxResultBuffer={1} bytes after reading {0} bytes of row data."
+                + " The limit keeps a result set from using more client memory than that, so the"
+                + " driver stopped reading and the connection can no longer be used."
+                + " Select fewer rows or columns, for example with a LIMIT clause, or raise the"
+                + " maxResultBuffer connection property, for example to 100M (100 MB) or to 10p"
+                + " (10 percent of the maximum heap), if results this large are expected.",
+            Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final4-1 (code UI)

### Rendered message

```text
The result set reached 100003200 bytes, which exceeds maxResultBuffer=100000000 bytes. The limit keeps the driver from holding more result data than that in memory. The connection cannot be used after this error. Fetch fewer rows at a time with Statement.setFetchSize (autocommit must be off), or set the maxResultBuffer connection property to a value above 100000000 bytes, such as a byte count with a K, M, G, or T suffix.
```

### Reader reply

```markdown
**1. What failed:** The report query's result reached 100,003,200 bytes, over the driver's `maxResultBuffer` limit of 100,000,000 bytes. The driver enforces this cap to limit how much result data it holds in memory.

**2. Connection state:** Unusable. The error says the connection cannot be used after it, so close it and open a new one.

**3. Change (preferred):** Fetch rows in batches instead of all at once:

```java
connection.setAutoCommit(false);
try (Statement st = connection.createStatement()) {
    st.setFetchSize(1000); // example value; the text gives no guidance on size
    try (ResultSet rs = st.executeQuery(reportSql)) {
        while (rs.next()) { /* process row */ }
    }
}
connection.commit();
```

**4. Alternative:** Raise the cap in the JDBC URL: `jdbc:postgresql://host:5432/db?maxResultBuffer=500M`. This allows more memory use, and the text doesn't say what a safe value is for your report.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:49:00.336278966 +0300
@@ -1014,7 +1014,15 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("The result set reached {0} bytes, which exceeds maxResultBuffer={1} bytes."
+                + " The limit keeps the driver from holding more result data than that in memory."
+                + " The connection cannot be used after this error."
+                + " Fetch fewer rows at a time with Statement.setFetchSize (autocommit must be off),"
+                + " or set the maxResultBuffer connection property to a value above {1} bytes,"
+                + " such as a byte count with a K, M, G, or T suffix.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final4-2 (code UM)

### Rendered message

```text
Result set exceeded the maxResultBuffer connection property: 100003200 bytes read, limit is 100000000 bytes. The limit keeps one result set from using more client memory than you allow, and the connection is closed after it is exceeded. To stay under the limit, fetch fewer rows at a time: turn off autocommit and call Statement.setFetchSize with a positive row count, or select fewer rows or columns. If results this large are expected, raise maxResultBuffer, for example to 200000000, or remove the property to turn the limit off.
```

### Reader reply

```markdown
**1. What failed:** The query returned about 100 MB (100,003,200 bytes against a 100,000,000-byte `maxResultBuffer` limit). The driver caps client memory for one result set.

**2. Connection state:** Closed. The message says the connection closes once the limit is exceeded. The text doesn't say whether your application reconnects automatically.

**3. What to change:** Stream the rows instead of loading them all:
```java
connection.setAutoCommit(false);
statement.setFetchSize(1000);
```
Autocommit must be off, or the fetch size is ignored. If you'd rather raise the limit, add `maxResultBuffer=200000000` to the JDBC URL. I can't see your code, so I don't know whether a fetch size is already set.

**4. Alternative:** Reduce what the query returns, using a `WHERE` or `LIMIT` clause or fewer columns.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:48:49.593514649 +0300
@@ -1014,7 +1014,18 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        long suggestedLimit = maxResultBuffer > Long.MAX_VALUE / 2 ? Long.MAX_VALUE : maxResultBuffer * 2;
+        throw new PSQLException(
+            GT.tr("Result set exceeded the maxResultBuffer connection property: {0} bytes read, limit is {1} bytes. "
+                    + "The limit keeps one result set from using more client memory than you allow, and the connection "
+                    + "is closed after it is exceeded. "
+                    + "To stay under the limit, fetch fewer rows at a time: turn off autocommit and call "
+                    + "Statement.setFetchSize with a positive row count, or select fewer rows or columns. "
+                    + "If results this large are expected, raise maxResultBuffer, for example to {2}, "
+                    + "or remove the property to turn the limit off.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer),
+                Long.toString(suggestedLimit)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-final4-3 (code UA)

### Rendered message

```text
Result set exceeded maxResultBuffer: the driver has read 100003200 bytes and the limit is 100000000 bytes. The limit keeps one result from using more client memory than you allow. The connection is closed because the rest of the result was not read. To stay under the limit, set a fetch size with Statement.setFetchSize with autocommit off, or select fewer rows or columns. If results this large are expected, set the maxResultBuffer connection property to a size larger than the result, such as 500M, or to a percentage of the heap, such as 10p.
```

### Reader reply

```markdown
**1. What failed:** The report query returned more data than the driver's `maxResultBuffer` allows. The driver read 100,003,200 bytes against a 100,000,000-byte cap and stopped. The check limits how much client memory one result can use.

**2. Connection state:** The connection is closed, because the unread rest of the result was discarded. Open a new connection before retrying. The text doesn't say whether an open transaction was rolled back, so assume it was lost.

**3. Changes (choose one):**
- Raise the limit in the JDBC URL, using a value above the report's full size, which the text doesn't give:
  `jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=500M`
  If the app passes properties programmatically, set `maxResultBuffer` there instead. I can't see the code to confirm.
- Stream rows instead:
  ```java
  conn.setAutoCommit(false);
  stmt.setFetchSize(1000);
  ```

**4. Alternative:** Select fewer rows or columns, or use the fetch-size approach above, which keeps the limit in place.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:49:09.856810675 +0300
@@ -1014,7 +1014,16 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: the driver has read {0} bytes and the limit is {1} bytes. "
+                    + "The limit keeps one result from using more client memory than you allow. "
+                    + "The connection is closed because the rest of the result was not read. "
+                    + "To stay under the limit, set a fetch size with Statement.setFetchSize with autocommit off, "
+                    + "or select fewer rows or columns. "
+                    + "If results this large are expected, set the maxResultBuffer connection property "
+                    + "to a size larger than the result, such as 500M, or to a percentage of the heap, such as 10p.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-new-1 (code UK)

### Rendered message

```text
Result set exceeded maxResultBuffer: read 100003200 bytes, limit is 100000000 bytes. The connection is closed because the rest of the result was not read. Raise the maxResultBuffer connection property, or set a smaller fetchSize so that each fetch stays within the limit.
```

### Reader reply

```markdown
**1. What failed:** One result set reached 100,003,200 bytes, just over the 100,000,000-byte `maxResultBuffer` limit. The driver caps buffered result size so a large query can't exhaust client memory.

**2. Connection state:** Closed. The driver shut it down because the unread rows couldn't be drained. Open a new connection before retrying. The text doesn't say whether the transaction was rolled back.

**3. What to change:**
- **Raise the limit:** add it to the JDBC URL, using your actual host and database:
  `jdbc:postgresql://host:5432/dbname?maxResultBuffer=200000000`
- **Or stream rows:** call `connection.setAutoCommit(false)`, then `statement.setFetchSize(1000)` before running the query. From general pgjdbc behavior, not this message, fetchSize only takes effect with autocommit off.

**4. Alternative:** Shrink the result. Aggregate or filter in SQL, or select fewer columns, so the report stays under the limit.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:39.681109765 +0300
@@ -1014,7 +1014,13 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set exceeded maxResultBuffer: read {0} bytes, limit is {1} bytes. "
+                + "The connection is closed because the rest of the result was not read. "
+                + "Raise the maxResultBuffer connection property, or set a smaller fetchSize "
+                + "so that each fetch stays within the limit.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-new-2 (code TA)

### Rendered message

```text
The result set read 100003200 bytes, which exceeds the maxResultBuffer limit of 100000000 bytes. Increase maxResultBuffer, or set a smaller fetch size so that fewer rows are read per fetch. The connection is closed because the rest of the result cannot be read.
```

### Reader reply

```markdown
1. **What failed:** The report returned about 100 MB (100,003,200 bytes), over the driver's `maxResultBuffer` cap of 100,000,000 bytes. The cap keeps one large result from exhausting JVM memory. The text doesn't say where the limit was set.

2. **Connection state:** Closed, according to the message. Reconnect before retrying. Any open transaction on it is lost.

3. **Changes:**
   - Raise the cap in the JDBC URL, for example `jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M`. Choose a value above your largest expected result.
   - Or set `connection.setAutoCommit(false)`, then call `statement.setFetchSize(1000)` before executing. The text says this helps, but it doesn't confirm that it avoids this error, so test it.

4. **Alternative:** Reduce the result in SQL with a `WHERE` filter, an aggregate, or a `LIMIT`, or write rows out as they arrive instead of holding them all.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:39.452566258 +0300
@@ -1014,7 +1014,12 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("The result set read {0} bytes, which exceeds the maxResultBuffer limit of {1} bytes. "
+                + "Increase maxResultBuffer, or set a smaller fetch size so that fewer rows are read per fetch. "
+                + "The connection is closed because the rest of the result cannot be read.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-new-3 (code UP)

### Rendered message

```text
The result set has read 100003200 bytes, which exceeds the maxResultBuffer limit of 100000000 bytes. The connection is dropped because the rest of the result cannot be read. Raise maxResultBuffer, or fetch fewer rows with setFetchSize or a LIMIT clause.
```

### Reader reply

```markdown
**1. What failed:** The report's result exceeded `maxResultBuffer`, set to 100,000,000 bytes. The driver holds the full result in memory, and this cap keeps one large query from exhausting the JVM heap. The read reached 100,003,200 bytes, just over the limit.

**2. Connection state:** The message says the connection was dropped. Treat it as unusable, close it, and open a new one. The text doesn't say whether any transaction was left open.

**3. Change:** Raise the limit in the JDBC URL, using a value above your report's real size, which the text doesn't give:
`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=200M`

**4. Alternative:** Stream rows instead of buffering them. Call `connection.setAutoCommit(false)`, then `statement.setFetchSize(1000)`. Add a `LIMIT` or narrower `WHERE` clause if the report doesn't need every row. The text doesn't confirm that fetch size alone avoids this limit on your driver version, so test it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:48.511262544 +0300
@@ -1014,7 +1014,12 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("The result set has read {0} bytes, which exceeds the maxResultBuffer limit of {1} bytes. "
+                + "The connection is dropped because the rest of the result cannot be read. "
+                + "Raise maxResultBuffer, or fetch fewer rows with setFetchSize or a LIMIT clause.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-old-1 (code UO)

### Rendered message

```text
Result set size of 100003200 bytes exceeds the maxResultBuffer limit of 100000000 bytes. Raise maxResultBuffer or read fewer rows. The connection is closed.
```

### Reader reply

```markdown
1. **Failure:** The report result was 100,003,200 bytes, 3,200 bytes over the 100,000,000-byte `maxResultBuffer` limit. The message doesn't state the reason for the check. It most likely guards against loading an unbounded result into memory. The text doesn't say which query or driver version caused this.

2. **Connection:** Closed, per the message. The text doesn't say whether the server cancelled the query. Open a new connection before retrying.

3. **Change:** Raise the limit in the JDBC URL, for example `jdbc:postgresql://HOST:5432/DB?maxResultBuffer=200M`. I haven't verified this syntax for your driver version or your configuration method, so check the pgjdbc docs for that version.

4. **Alternatives:** Shrink the result in SQL with fewer columns, `WHERE` filters, aggregation, or `LIMIT` with keyset paging. The text doesn't say whether streaming (`setFetchSize` with autocommit off) avoids this limit, so test it first.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:16:58.151045784 +0300
@@ -1014,7 +1014,11 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set size of {0} bytes exceeds the maxResultBuffer limit of {1} bytes. "
+                + "Raise maxResultBuffer or read fewer rows. The connection is closed.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-old-2 (code TL)

### Rendered message

```text
Result set size exceeds the maxResultBuffer limit of 100000000 bytes after reading 100003200 bytes. Fetch fewer rows per query or raise the maxResultBuffer connection property. The connection has been closed.
```

### Reader reply

```markdown
**What failed:** The query's result exceeded the driver's 100 MB `maxResultBuffer` cap and stopped after 100,003,200 bytes. The driver enforces this cap so one result cannot exhaust JVM heap.

**Connection state:** Closed, per the message. Reconnect, and any uncommitted work is lost. The text doesn't say whether your pool replaces closed connections.

**Option A, raise the limit:** Add it to the JDBC URL:
`jdbc:postgresql://HOST:5432/DB?maxResultBuffer=200M`

I haven't confirmed the `M` suffix from this text. If it's rejected, use bytes: `maxResultBuffer=200000000`. Check that your heap (`-Xmx`) can hold the larger result.

**Option B, shrink the result:** Add a `LIMIT` or a date-range filter, or page through key ranges and aggregate in batches. The text doesn't say whether `setFetchSize` avoids the cap, so don't rely on it.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:17:07.866732411 +0300
@@ -1014,7 +1014,12 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("Result set size exceeds the maxResultBuffer limit of {0} bytes after reading {1} bytes. "
+                + "Fetch fewer rows per query or raise the maxResultBuffer connection property. "
+                + "The connection has been closed.",
+                Long.toString(maxResultBuffer), Long.toString(resultBufferByteCount)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```

## sonnet-old-3 (code UL)

### Rendered message

```text
The result set has reached 100003200 bytes, which exceeds the maxResultBuffer limit of 100000000 bytes. Raise maxResultBuffer or fetch fewer rows per query. The connection is closed.
```

### Reader reply

```markdown
**1. What failed:** The report query's result set reached about 100 MB, over the driver's `maxResultBuffer` cap of 100,000,000 bytes. The driver enforces the cap so one large result can't exhaust the JVM heap.

**2. Connection state:** Closed, per the message. Open a new connection before retrying. Any uncommitted work was lost.

**3. Change:** Add the property to the JDBC URL, for example:
`jdbc:postgresql://HOST:5432/DBNAME?maxResultBuffer=500000000`
Make sure the value fits your heap. I can't confirm from this text whether suffixes like `500M` are accepted.

**4. Alternative:** Stream rows instead. Call `connection.setAutoCommit(false)` and `statement.setFetchSize(1000)`. With autocommit on, the driver usually ignores fetch size and buffers the whole result. Or narrow the query with fewer columns, a `LIMIT`, or aggregation in SQL.

I can't see whether autocommit is on, your driver version, or where the cap is set.
```

### Diff

```diff
diff -ru -x .claude a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java
--- a/pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:14:53.603585410 +0300
+++ ./pgjdbc/src/main/java/org/postgresql/core/PGStream.java	2026-10-26 16:17:05.338264772 +0300
@@ -1014,7 +1014,11 @@
         // The row is not read, so the stream is off its message boundary. Drop the connection
         // here rather than refuse it at the next message.
         setBroken();
-        throw new PSQLException(GT.tr("Result set exceeded maxResultBuffer"), PSQLState.COMMUNICATION_ERROR);
+        throw new PSQLException(
+            GT.tr("The result set has reached {0} bytes, which exceeds the maxResultBuffer limit of {1} bytes. "
+                + "Raise maxResultBuffer or fetch fewer rows per query. The connection is closed.",
+                Long.toString(resultBufferByteCount), Long.toString(maxResultBuffer)),
+            PSQLState.COMMUNICATION_ERROR);
       }
     }
   }
```
