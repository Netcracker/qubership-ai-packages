# Tessary support case: field values

Portal: Tessary support portal, "New case". Each block below holds the value for one field, in the form's order. The
Description and "What do you need from us?" fields render plain text, so paste the blocks as they are.

## Severity (required)

```text
S3 - Issue resolved or mitigated; you need a root cause, a credit, or information
```

## Service (required)

```text
Object Storage
```

## Region (required)

```text
eu-north-2
```

## Subject (required, 120 characters)

```text
503 SlowDown on 8% of PUTs at about 6 PUT/s, eu-north-2, 2026-09-21 14:05–14:45 UTC
```

## Description (required)

```text
Account acc-7f3e9120, Performance plan, Object Storage in eu-north-2.

On 2026-09-21 from 14:05:12.448Z to 14:44:51.302Z (16:05 to 16:45 CEST), 1217 of 15321 PUT requests from our upload service to the buckets lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 failed with HTTP 503 SlowDown. The rate was close to 8% in every five-minute interval. The errors stopped at 14:44:51Z with no change on our side. From 14:45 to 16:00 UTC, 11860 PUT requests in eu-north-2 succeeded and none failed. No other status code above 499 appeared.

PUT requests to both eu-north-2 buckets, from our upload service's request log (UTC):

  Interval      PUT attempts   503 SlowDown   Error rate
  14:05-14:10   2031           158            7.78%
  14:10-14:15   2044           163            7.97%
  14:15-14:20   2012           161            8.00%
  14:20-14:25   2027           159            7.84%
  14:25-14:30   1806           147            8.14%
  14:30-14:35   1811           142            7.84%
  14:35-14:40   1797           146            8.12%
  14:40-14:45   1793           141            7.86%

Request rate

Averaged over the 40 minutes, we sent about 6.4 PUT/s across both buckets, and the busiest prefix, ingest/2026/09/21/, received 5.9 PUT/s. No five-minute interval had more than 2044 PUT attempts in total, which is fewer than your request-rate page allows a single prefix in one second:

  "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled."
  https://docs.tessary.cloud/storage/performance/request-rates

The same page gives an account limit of 10,000 PUT/s per region.

Same client, same 40 minutes, one thing varied

- GET requests to the same two buckets: 41210 requests, 9 returned 503 SlowDown (0.02%).
- PUT requests to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.

Client: Tessary Java SDK 2.14.3. Egress addresses: 203.0.113.41 and 203.0.113.42.

Status page

https://status.tessary.cloud showed "Object Storage, eu-north-2: Operational" when we checked at 14:12 and 14:31 UTC on 2026-09-21. Its history, read on 2026-09-22 at 09:00 UTC, showed "No incidents reported" for 2026-09-21.

Request IDs

The attached slowdown-requests-2026-09-21.csv lists all 1217 failed requests (timestamp, bucket, object key, request ID, host ID). Five of them:

  Time (UTC)      Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of them, as the SDK's debug log printed it:

  2026-09-21T14:05:47.212Z DEBUG tessary.http [upload-host-1] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: <redacted: TESS4-HMAC-SHA256 authorization header>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

The internal hostname in this log was changed, and the Authorization header was removed.

What we changed on our side

Restarting our upload clients at 14:14 UTC, rolling back an unrelated deploy at 14:18 UTC, raising the client memory limit, and flushing the DNS cache on the client nodes did not change the error rate.

Until 14:25 UTC the client did not retry a 503 on this path. At 14:25:00 UTC we deployed retries with exponential backoff and full jitter (base 100 ms, cap 5 s, at most 6 attempts). The 503 rate per attempt stayed the same, and the share of uploads that failed dropped:

  Window (UTC)            Uploads   PUT attempts   503 per attempt   Uploads failed
  14:05-14:25, no retry   8114      8114           641 (7.90%)       641 (7.90%)
  14:25-14:45, backoff    6652      7207           576 (7.99%)       21 (0.32%)

The 662 failed uploads were re-sent at 14:52 UTC and all succeeded. The backoff stays in production.

Service level

Counting our PUT requests, each of the eight intervals above had an Error Rate above 1% under §3 of https://tessary.cloud/legal/storage-sla. By our count, none of the 503 responses came from exceeding the documented request rates. With 8 of the 8640 five-minute intervals in September 2026 unavailable, we compute a Monthly Uptime Percentage of 99.907% for eu-north-2, which falls in the "Below 99.99%" tier of §5.
```

## What do you need from us? (required)

```text
1. Did Object Storage in eu-north-2 have a problem on 2026-09-21 that affected PUT requests? If so, when did it start and end?

2. Did Tessary throttle account acc-7f3e9120, the buckets lm-prod-ingest-eun2 or lm-prod-thumbs-eun2, or any prefix in them between 14:05 and 14:45 UTC? If so, what triggered it at about 6 PUT/s, for example a partition being scaled?

3. A service credit for eu-north-2 for September 2026 under §5 of the Storage SLA. Please confirm whether these 503 responses count toward the Error Rate under §3, and if they do, apply the credit. The dates, times, and request IDs that §6 asks for are in the description and the attached CSV.
```

## Attachments (optional)

```text
slowdown-requests-2026-09-21.csv (118 KB, 1217 rows)
```
