# Tessary support case: New case

Severity: S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

Service: Object Storage

Region: eu-north-2

Subject:

```text
eu-north-2: 503 SlowDown on 7.9% of PUTs at about 6 PUT/s, 2026-09-21 14:05–14:45 UTC
```

Description:

```text
Account: acc-7f3e9120 (Performance plan)
Region: eu-north-2
Buckets: lm-prod-ingest-eun2, lm-prod-thumbs-eun2
Client: Tessary Java SDK 2.14.3, egress addresses 203.0.113.41 and 203.0.113.42
Window: 2026-09-21 14:05:12.448Z to 14:44:51.302Z (first and last SlowDown in our request log)

What happened

On 2026-09-21 from 14:05 to 14:45 UTC (16:05–16:45 CEST), our upload service sent 15321 PUT requests to lm-prod-ingest-eun2 and lm-prod-thumbs-eun2. 1217 of them (7.9%) returned HTTP 503 SlowDown. No response in that window had any other status code above 499. From 14:45 to 16:00 UTC, all 11860 PUTs to the same buckets succeeded.

The PUT rate across both buckets averaged 6.4 requests per second over the 40 minutes. The busiest prefix, ingest/2026/09/21/, averaged 5.9 per second. We have not computed per-second peaks.

PUTs to both buckets per five-minute interval, from our request log:

  Interval (UTC)   PUT attempts   503 SlowDown   Error rate
  14:05–14:10      2031           158            7.78%
  14:10–14:15      2044           163            7.97%
  14:15–14:20      2012           161            8.00%
  14:20–14:25      2027           159            7.84%
  14:25–14:30      1806           147            8.14%
  14:30–14:35      1811           142            7.84%
  14:35–14:40      1797           146            8.12%
  14:40–14:45      1793           141            7.86%

What we compared in the same 40 minutes, from the same request log:

- PUTs from the same upload service to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.
- GETs on the two eu-north-2 buckets: 41210 requests, 9 SlowDown (0.02%). We have not split these by interval.
- Until 14:25 UTC our client did not retry a 503 on this path, so the first 20 minutes of SlowDown responses came with no retry traffic from us.

Your status page (https://status.tessary.cloud) showed "Object Storage, eu-north-2: Operational" when we checked at 14:12 and 14:31 UTC. Its history, read on 2026-09-22 at 09:00 UTC, showed "No incidents reported" for 2026-09-21.

What we expected

The request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) says: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10000 PUT/s per region. Our busiest prefix averaged 5.9 PUT/s, so we did not expect SlowDown responses at this rate.

Storage SLA (https://tessary.cloud/legal/storage-sla), Performance plan: under §3, each of the eight intervals above has an Error Rate over 1% from 503 responses, at request rates far below the documented ones. If these eight are the only unavailable intervals in September (8640 intervals), the Monthly Uptime Percentage under §4 is 99.907%, which is below the 99.99% threshold in §5.

Example failed request

From the SDK debug log. We removed the internal host name and the request credential; nothing else is changed.

  2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal host name>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

Five of the failed requests:

  Time (UTC)       Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z    lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z    lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z    lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z    lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z    lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

All 1217 failed requests are in the attached slowdown-requests-2026-09-21.csv, one row each: timestamp, bucket, object key, request ID, host ID.

Mitigation on our side

At 14:25 UTC we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts). It did not change the share of attempts that got a 503: 7.90% of 8114 attempts from 14:05 to 14:25, and 7.99% of 7207 attempts from 14:25 to 14:45. Failed uploads fell from 7.90% (641 of 8114) to 0.32% (21 of 6652). We re-ran all 662 failed uploads at 14:52 UTC, and all succeeded.
```

What do you need from us?:

```text
1. Was there an event in Object Storage in eu-north-2 on 2026-09-21 that affected these buckets, for example a partition being scaled? If so, when did it start and end?
2. Did Tessary throttle account acc-7f3e9120, either bucket, or the prefix ingest/2026/09/21/ between 14:05 and 14:45 UTC? If so, what triggered it at the rates above?
3. A service credit under §5 of the Storage SLA for the eight 5-minute intervals from 14:05 to 14:45 UTC on 2026-09-21, or the reason they do not qualify.
```

Attachments:

- `slowdown-requests-2026-09-21.csv` (118 KB, 1217 rows)
