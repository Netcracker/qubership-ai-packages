# Tessary support case: field values

The portal renders plain text, so paste the contents of each block below as they are.

## Severity

S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

## Service

Object Storage

## Region

eu-north-2

## Subject

```text
503 SlowDown on 7.9% of PUTs at 6.4 PUT/s, eu-north-2, 2026-09-21 14:05–14:45 UTC
```

## Description

```text
On 2026-09-21 from 14:05:12 to 14:44:51 UTC, PUT requests from our upload service to two buckets in eu-north-2 failed with HTTP 503 SlowDown: 1217 of 15321 PUT attempts (7.9%). Our rate was about 6.4 PUT/s across both buckets and 5.9 PUT/s on the busiest prefix, ingest/2026/09/21/. The errors stopped on their own at 14:44:51 UTC.

Account: acc-7f3e9120, Performance plan
Buckets: lm-prod-ingest-eun2 and lm-prod-thumbs-eun2, both in eu-north-2
Client: Tessary Java SDK 2.14.3, from egress addresses 203.0.113.41 and 203.0.113.42

PUT attempts and 503 SlowDown responses per 5-minute interval, both buckets together, from our request log (UTC). No other status code above 499 occurred in this window.

  Interval      PUT attempts   503 SlowDown   Share
  14:05-14:10   2031           158            7.8%
  14:10-14:15   2044           163            8.0%
  14:15-14:20   2012           161            8.0%
  14:20-14:25   2027           159            7.8%
  14:25-14:30   1806           147            8.1%
  14:30-14:35   1811           142            7.8%
  14:35-14:40   1797           146            8.1%
  14:40-14:45   1793           141            7.9%

Five of the failed requests. All 1217 are in the attached file slowdown-requests-2026-09-21.csv, one row per request: timestamp, bucket, object key, request ID, and host ID.

  Time (UTC)      Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of them as the SDK debug log printed it. We replaced our internal host name and removed the access key ID and the signature:

2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal host name>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
> Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
< HTTP/1.1 503 Service Unavailable
< x-tess-request-id: 9c41e0b27a6d4f18
< x-tess-host-id: eun2-fe-3a71
<Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

Other traffic from the same uploader and account:
- GETs on the same two buckets, 14:05-14:45 UTC: 41210 requests, 9 SlowDown (0.02%).
- PUTs to lm-prod-ingest-euw3 in eu-west-3, 14:05-14:45 UTC: 14870 requests, none failed.
- PUTs to the two eu-north-2 buckets, 14:45-16:00 UTC: 11860 requests (about 2.6 PUT/s), none failed.

Your status page showed "Object Storage, eu-north-2: Operational" when we checked it at 14:12 and 14:31 UTC. Its history showed "No incidents reported" for 2026-09-21 when we read it on 2026-09-22 at 09:00 UTC.

Your request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) says: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10000 PUT/s per region. Our busiest prefix ran at 5.9 PUT/s and the whole account at about 6.4 PUT/s in the region, so we did not exceed either documented rate.

Mitigation: until 14:25 UTC our client did not retry a 503 on this path. At 14:25:00 UTC we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts). The share of attempts that got a 503 stayed the same, and the share of failed uploads dropped:

  Window (UTC)            Uploads   PUT attempts   503 per attempt   Uploads failed
  14:05-14:25, no retry   8114      8114           641 (7.90%)       641 (7.90%)
  14:25-14:45, backoff    6652      7207           576 (7.99%)       21 (0.32%)

Service credit: SLA section 3 for the Performance plan (https://tessary.cloud/legal/storage-sla) counts a 5-minute interval as unavailable when its Error Rate exceeds 1%, and excludes only 503 responses caused by exceeding the documented request rates. By our counts, 7.8% to 8.1% of PUT attempts in each of the eight intervals above got a 503, at the rates stated above. Our counts cover PUTs only, as our client saw them; your records decide the Error Rate. If these eight are the only unavailable intervals in September, the Monthly Uptime Percentage is 8632 of 8640 intervals, 99.907%, which is below the 99.99% threshold in section 5.
```

## What do you need from us?

```text
1. Did Object Storage in eu-north-2 have a problem on 2026-09-21 that affected these two buckets? If so, when did it start and end?
2. Did Tessary throttle account acc-7f3e9120, or any prefix in lm-prod-ingest-eun2 or lm-prod-thumbs-eun2, between 14:05 and 14:45 UTC, or scale a partition behind them? If so, which prefixes, and why at these request rates?
3. A service credit under the Storage SLA for the eight intervals from 14:05 to 14:45 UTC on 2026-09-21. The dates, times, and request IDs that section 6 asks for are in the description and the attached file.
```

## Attachments

slowdown-requests-2026-09-21.csv (118 KB, 1217 rows)
