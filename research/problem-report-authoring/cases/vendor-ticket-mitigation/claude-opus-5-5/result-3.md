# Tessary support case: field values

Portal: Tessary support, "New case". Each value below is in a `text` block so it pastes unchanged; the
Description and "What do you need from us?" fields are plain text and do not render Markdown.

## Severity

```text
S3
```

## Service

```text
Object Storage
```

## Region

```text
eu-north-2
```

## Subject

```text
PUT returns 503 SlowDown on 7.9% of requests at 6 PUT/s, eu-north-2, 2026-09-21 14:05-14:45 UTC
```

## Description

```text
On 2026-09-21 from 14:05:12 to 14:44:51 UTC, 1217 of 15321 PUT requests (7.9%) from our upload service to two buckets in eu-north-2 returned HTTP 503 SlowDown. Our rate was about 6.4 PUT/s across both buckets and 5.9 PUT/s on the busiest prefix, ingest/2026/09/21/. The request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) documents at least 3500 PUT/s per prefix and 10000 PUT/s per region. No other 5xx response occurred in the window. The errors stopped at 14:44:51 UTC, and we made no change at that time.

Account and resources
- Account acc-7f3e9120, plan Performance, region eu-north-2
- Buckets lm-prod-ingest-eun2 and lm-prod-thumbs-eun2
- Client: Tessary Java SDK 2.14.3, sending from 203.0.113.41 and 203.0.113.42

Five of the failed requests (all 1217 are in the attached slowdown-requests-2026-09-21.csv, with timestamp, bucket, object key, request ID, and host ID):

    Time (UTC)      Bucket               x-tess-request-id   x-tess-host-id
    14:05:47.212Z   lm-prod-ingest-eun2  9c41e0b27a6d4f18    eun2-fe-3a71
    14:12:03.884Z   lm-prod-ingest-eun2  2f7b93c05e1a8d46    eun2-fe-3a64
    14:21:39.017Z   lm-prod-thumbs-eun2  d05e6a18b4c2f973    eun2-fe-3a71
    14:33:10.551Z   lm-prod-ingest-eun2  71ac2d9e0f4b3865    eun2-fe-3a58
    14:44:51.302Z   lm-prod-ingest-eun2  e8d4f16a2b90c537    eun2-fe-3a64

The first of them, as the SDK debug log printed it (the Authorization header and our host name are redacted):

    2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: client host name>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
    > Authorization: <redacted: TESS4-HMAC-SHA256 credential and signature>
    < HTTP/1.1 503 Service Unavailable
    < x-tess-request-id: 9c41e0b27a6d4f18
    < x-tess-host-id: eun2-fe-3a71
    <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

PUT attempts and 503 SlowDown responses per 5-minute interval, both eu-north-2 buckets together:

    Interval (UTC)   PUT attempts   503 SlowDown   Share
    14:05-14:10      2031           158            7.78%
    14:10-14:15      2044           163            7.97%
    14:15-14:20      2012           161            8.00%
    14:20-14:25      2027           159            7.84%
    14:25-14:30      1806           147            8.14%
    14:30-14:35      1811           142            7.84%
    14:35-14:40      1797           146            8.12%
    14:40-14:45      1793           141            7.86%

What did not fail, from the same client:
- GETs on the same two buckets in the same 40 minutes: 41210 requests, 9 SlowDown (0.02%).
- PUTs to lm-prod-ingest-euw3 in eu-west-3 in the same 40 minutes: 14870 requests, none failed.
- PUTs to the two eu-north-2 buckets from 14:45 to 16:00 UTC: 11860 requests, none failed.

Status page: https://status.tessary.cloud showed "Object Storage, eu-north-2: Operational" when we checked at 14:12 and 14:31 UTC on 2026-09-21. Its history, read on 2026-09-22 at 09:00 UTC, shows "No incidents reported" for 2026-09-21.

Retry: until 14:25:00 UTC our client did not retry a 503 on this path. From then on it retried with exponential backoff and full jitter (base 100 ms, cap 5 s, at most 6 attempts). The share of attempts answered with 503 did not change: 7.90% from 14:05 to 14:25 and 7.99% from 14:25 to 14:45. The share of uploads that failed after all attempts fell from 7.90% to 0.32%.

Service level: under §3 of the Storage SLA (https://tessary.cloud/legal/storage-sla), each of the eight intervals above has an Error Rate over 1%. The §3 exception for exceeding the documented request rates does not fit a rate of 6.4 PUT/s. If no other interval in September was unavailable, the Monthly Uptime Percentage for eu-north-2 is 99.907% (8632 of 8640 intervals), which §5 puts below 99.99%. The attached CSV carries the dates, times, and request IDs that §6 asks for.
```

## What do you need from us?

```text
1. Did Object Storage in eu-north-2 have a problem on 2026-09-21 that caused these 503 SlowDown responses? If so, when did it start and end? The status page showed the region as Operational while the errors occurred.
2. Did Tessary throttle account acc-7f3e9120, the bucket lm-prod-ingest-eun2 or lm-prod-thumbs-eun2, or a prefix in them, for example while scaling a partition? If so, what triggered it at about 6 PUT/s?
3. A service credit under the Storage SLA for the eight 5-minute intervals from 14:05 to 14:45 UTC on 2026-09-21, which we count as unavailable under §3.
```

## Attachments

```text
slowdown-requests-2026-09-21.csv (118 KB, 1217 rows)
```
