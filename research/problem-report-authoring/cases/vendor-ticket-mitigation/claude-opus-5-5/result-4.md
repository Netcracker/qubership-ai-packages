# Tessary support case: draft

Field values for the Tessary support portal, "New case", in the form's order. The text inside each
`text` block is the field value. Description and "What do you need from us?" are plain text in the
portal, so they carry no Markdown.

## Severity

S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

## Service

Object Storage

## Region

eu-north-2

## Subject

```text
PUT requests failed with 503 SlowDown in eu-north-2 on 2026-09-21, 14:05 to 14:45 UTC, at 6.4 PUT/s
```

## Description

```text
On 2026-09-21 between 14:05 and 14:45 UTC (16:05 to 16:45 CEST), PUT requests from our upload service to two buckets in eu-north-2 failed with HTTP 503 SlowDown: 1217 of 15321 PUT attempts, about 8% in every 5-minute interval. Averaged over the 40 minutes, we sent about 6.4 PUT/s in total. The first SlowDown arrived at 14:05:12.448Z and the last at 14:44:51.302Z. The errors stopped with no change on our side at that time.

Account and client
  Account:        acc-7f3e9120, Performance plan
  Buckets:        lm-prod-ingest-eun2, lm-prod-thumbs-eun2 (both eu-north-2)
  Source IPs:     203.0.113.41, 203.0.113.42
  Client:         Tessary Java SDK 2.14.3

Request rate
The busiest prefix, ingest/2026/09/21/, received 5.9 PUT/s averaged over the same 40 minutes. Your request-rates page (https://docs.tessary.cloud/storage/performance/request-rates) states: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10000 PUT/s per region.

PUT attempts and 503 SlowDown responses per 5-minute interval, both buckets, from our client's request log:

  Interval (UTC)   PUT attempts   503 SlowDown
  14:05-14:10      2031           158
  14:10-14:15      2044           163
  14:15-14:20      2012           161
  14:20-14:25      2027           159
  14:25-14:30      1806           147
  14:30-14:35      1811           142
  14:35-14:40      1797           146
  14:40-14:45      1793           141

No response in the window had any other status code of 500 or above.

Other traffic from the same client
  - Same 40 minutes, PUTs to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.
  - Same 40 minutes, GETs on the two eu-north-2 buckets: 41210 requests, 9 SlowDown (0.02%).
  - 14:45 to 16:00 UTC, PUTs to the two eu-north-2 buckets: 11860 requests, none failed.

Status page
https://status.tessary.cloud showed "Object Storage, eu-north-2: Operational" when we checked it at 14:12 and 14:31 UTC on 2026-09-21. Its history, read on 2026-09-22 at 09:00 UTC, showed "No incidents reported" for 2026-09-21.

Failed requests
Five of the 1217 are below. All 1217 are in the attached slowdown-requests-2026-09-21.csv (timestamp, bucket, object key, request ID, host ID).

  Time (UTC)       Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z    lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z    lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z    lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z    lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z    lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of them as the SDK debug log printed it (our host name replaced, Authorization header value removed):

  2026-09-21T14:05:47.212Z DEBUG tessary.http [uploader-01.example.internal] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: <redacted: TESS4-HMAC-SHA256 access key ID and signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

Retries
Until 14:25:00 UTC our client did not retry a 503 on this path. From 14:25:00 UTC it retried with exponential backoff and full jitter (base 100 ms, cap 5 s, at most 6 attempts), so the attempt counts from 14:25 include retries. The share of attempts answered with 503 did not change: 7.90% from 14:05 to 14:25 and 7.99% from 14:25 to 14:45. The 662 uploads that failed were sent again at 14:52 UTC and all succeeded.
```

## What do you need from us?

```text
1. Root cause: did Object Storage in eu-north-2 have a problem affecting lm-prod-ingest-eun2 or lm-prod-thumbs-eun2 between 14:05 and 14:45 UTC on 2026-09-21, for example a partition being scaled? If so, when did it start and when did it end?

2. Throttling: did Tessary throttle account acc-7f3e9120, either bucket, a prefix, or the source IPs 203.0.113.41 and 203.0.113.42 in that window? If so, which limit applied, given that the busiest prefix received 5.9 PUT/s?

3. Service credit under the Object Storage SLA (https://tessary.cloud/legal/storage-sla), Performance plan, for eu-north-2. In our client's log, each of the eight 5-minute intervals from 14:05 to 14:45 UTC had an Error Rate between 7.78% and 8.14%, above the 1% threshold of section 3. Our request rates were far below the documented rates, so we read the section 3 exclusion as not applying to these 503 responses. If no other interval in September 2026 was unavailable, 8632 of 8640 intervals were available, a Monthly Uptime Percentage of 99.907%. Section 5 gives a 10% credit of the region's storage charges below 99.99%. Please confirm the intervals against your own measurements and apply the credit. Dates, times, and request IDs are in the description and the attached CSV, as section 6 asks.
```

## Attachments

`slowdown-requests-2026-09-21.csv` (118 KB, 1217 rows)
