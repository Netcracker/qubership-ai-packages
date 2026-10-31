# Tessary support case: draft field values

Tessary support portal, "New case". Copy each free-text value from inside its block; the portal renders plain text, so the blocks contain no Markdown.

**Severity:** S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

**Service:** Object Storage

**Region:** eu-north-2

**Subject:**

```text
503 SlowDown on about 8% of PUTs at 6.4 PUT/s, eu-north-2, 2026-09-21 14:05–14:45 UTC
```

**Description:**

```text
On 2026-09-21 from 14:05:12 to 14:44:51 UTC (16:05 to 16:45 CEST), about 8% of our PUT requests to two buckets in eu-north-2 failed with HTTP 503 SlowDown. Our request rate was far below the documented limits, and the status page showed eu-north-2 as Operational.

Account: acc-7f3e9120, plan Performance
Region: eu-north-2
Buckets: lm-prod-ingest-eun2, lm-prod-thumbs-eun2
Client: Tessary Java SDK 2.14.3, egress addresses 203.0.113.41 and 203.0.113.42
First SlowDown: 2026-09-21T14:05:12.448Z
Last SlowDown: 2026-09-21T14:44:51.302Z


WHAT WE OBSERVED

PUT attempts to both eu-north-2 buckets per 5-minute interval, counted from our upload client's request log:

  Interval (UTC)   PUT attempts   503 SlowDown   Share
  14:05–14:10      2031           158            7.78%
  14:10–14:15      2044           163            7.97%
  14:15–14:20      2012           161            8.00%
  14:20–14:25      2027           159            7.84%
  14:25–14:30      1806           147            8.14%
  14:30–14:35      1811           142            7.84%
  14:35–14:40      1797           146            8.12%
  14:40–14:45      1793           141            7.86%
  Total            15321          1217           7.94%

Averaged over the 40 minutes, that is 6.4 PUT/s across both buckets. The busiest key prefix, ingest/2026/09/21/, took 5.9 PUT/s. No response in the log had any other status code above 499.

In the same 40 minutes, from the same client:
- GETs on the same two buckets: 41210 requests, 9 SlowDown (0.02%).
- PUTs to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.
From 14:45 to 16:00 UTC, 11860 PUTs in eu-north-2, none failed.

One failed request as the SDK debug log printed it. We replaced the client hostname, the access key ID, and the signature with placeholders; nothing else is changed.

  2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: client hostname>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

Five of the failed requests. All 1217 are in the attached slowdown-requests-2026-09-21.csv, with timestamp, bucket, object key, request ID, and host ID.

  Time (UTC)      Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64


WHAT WE EXPECTED

https://docs.tessary.cloud/storage/performance/request-rates says: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10000 PUT/s per region. At 5.9 PUT/s on our busiest prefix and 6.4 PUT/s in the region, we expected no SlowDown responses unless a partition was being scaled.

We checked https://status.tessary.cloud at 14:12 and 14:31 UTC on 2026-09-21. It showed "Object Storage, eu-north-2: Operational". Its history, read on 2026-09-22 at 09:00 UTC, shows "No incidents reported" for 2026-09-21.


WHAT WE CHANGED ON OUR SIDE

Until 14:25:00 UTC our client did not retry a 503 on this path, so every attempt before then was a first attempt. At 14:25:00 UTC we deployed retries with exponential backoff and full jitter (base 100 ms, cap 5 s, at most 6 attempts). The share of attempts that received a 503 stayed the same: 7.90% from 14:05 to 14:25 UTC and 7.99% from 14:25 to 14:45 UTC. Only the share of uploads that failed after all retries dropped, from 7.90% to 0.32%.
```

**What do you need from us?:**

```text
1. Root cause: did Object Storage in eu-north-2 have a problem on 2026-09-21 that caused these responses? If so, what was it, and when did it start and end (UTC)?

2. Throttling: between 14:05 and 14:45 UTC, did Tessary throttle account acc-7f3e9120, the buckets lm-prod-ingest-eun2 or lm-prod-thumbs-eun2, or a prefix in them, for example while a partition was being scaled? If so, which resource was throttled, and what triggered it at these request rates?

3. Service credit under https://tessary.cloud/legal/storage-sla for eu-north-2. By our count, the eight 5-minute intervals from 14:05 to 14:45 UTC had a PUT error rate between 7.78% and 8.14%, above the 1% in §3. Our rate was far below the documented request rates, so as we read §3 these 503 responses are not excluded. These eight intervals alone put September at 99.907% (8632 of 8640 intervals), below the 99.99% in §5. The request IDs of all 1217 errors are in the attached CSV. We are past the 30-day window in §6, which ended on 2026-10-21. Can a credit still be granted for this incident?
```

**Attachments:** `slowdown-requests-2026-09-21.csv` (1217 rows, 118 KB)
