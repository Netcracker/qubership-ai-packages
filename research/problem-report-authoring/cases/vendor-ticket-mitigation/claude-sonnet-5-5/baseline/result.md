Tessary support portal, New case. Each field below is plain text, as the portal does not render Markdown. Indented blocks are pasted output or tables.

## Severity

S3 (Issue resolved or mitigated; you need a root cause, a credit, or information)

## Service

Object Storage

## Region

eu-north-2

## Subject

eu-north-2 PUT 503 SlowDown, 2026-09-21 14:05-14:45 UTC, at 6.4 PUT/s: cause and SLA credit

## Description

Between 14:05:12 UTC and 14:44:51 UTC on 2026-09-21, our upload cluster sent PUT requests to two buckets in eu-north-2, and 1217 of 15321 returned HTTP 503 SlowDown. The total rate was about 6.4 PUT/s. We were uploading media files, and 662 uploads failed before we re-queued them by hand. We need to know whether Tessary had a problem in eu-north-2, when it started and ended, and whether the account or a prefix was throttled.

All times are UTC.

Identifiers
  Account:   acc-7f3e9120 (plan Performance)
  Region:    eu-north-2
  Buckets:   lm-prod-ingest-eun2, lm-prod-thumbs-eun2 (eu-north-2); lm-prod-ingest-euw3 (eu-west-3)
  Egress:    203.0.113.41, 203.0.113.42
  Client:    Tessary Java SDK 2.14.3

What we observed
The counts come from our uploader's request log and cover both eu-north-2 buckets. The first SlowDown is at 14:05:12.448Z and the last at 14:44:51.302Z. No other status code above 499 appears in the log.

    Interval        PUT attempts   503 SlowDown   Share
    14:05-14:10     2031           158            7.8%
    14:10-14:15     2044           163            8.0%
    14:15-14:20     2012           161            8.0%
    14:20-14:25     2027           159            7.8%
    14:25-14:30     1806           147            8.1%
    14:30-14:35     1811           142            7.8%
    14:35-14:40     1797           146            8.1%
    14:40-14:45     1793           141            7.9%
    Total           15321          1217

The busiest prefix, ingest/2026/09/21/, took 5.9 PUT/s. From 14:45 to 16:00, 11860 PUTs to the same two buckets returned no 503.

What we compared it with, in the same log and the same 40 minutes:
  - PUTs to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.
  - GETs on the two eu-north-2 buckets: 41210 requests, 9 SlowDown (0.02%).

Changes on our side that made no difference: restarting the uploader processes at 14:14, rolling back an unrelated deploy at 14:18, raising the memory limit of the uploader, and flushing the DNS cache on the hosts. The retry change at 14:25 is described under "Our mitigation".

Five of the failed requests (all 1217 are in the attached CSV):

    Time (UTC)      Bucket                x-tess-request-id   x-tess-host-id
    14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
    14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
    14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
    14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
    14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of them, as the SDK's debug log printed it. The host name and the Authorization header are redacted in place:

    2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: uploader hostname>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
    > Authorization: <redacted: request signature>
    < HTTP/1.1 503 Service Unavailable
    < x-tess-request-id: 9c41e0b27a6d4f18
    < x-tess-host-id: eun2-fe-3a71
    <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

What Tessary documents
The request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) says: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." It gives an account limit of 10,000 PUT/s per region. Our busiest prefix ran at 5.9 PUT/s and the whole account at about 6.4 PUT/s, so we do not see how either limit applies. We cannot see whether a partition was being scaled.

The status page (https://status.tessary.cloud) showed "Object Storage, eu-north-2: Operational" when we checked at 14:12 and 14:31. Its history, read on 2026-09-22 at 09:00, said "No incidents reported" for 2026-09-21. We have not searched for known issues or other cases for this period.

The Storage SLA (https://tessary.cloud/legal/storage-sla), Performance plan, says in section 3: "A 5-minute interval is unavailable when its Error Rate exceeds 1%. Error Rate counts HTTP 500 and HTTP 503 responses, except 503 responses caused by exceeding the documented request rates." Section 5 sets a 10% credit of the region's storage charges below 99.99% and 25% below 99.9%. Section 6 says: "Open a support ticket within 30 days of the incident with the dates, times, and request IDs of the errors."

Our own arithmetic, which Tessary's calculation replaces: the eight intervals above each had a PUT 503 share above 1%. September has 8640 intervals, so (8640 - 8) / 8640 is 99.907%. Counting the GETs as well, 1226 of 56531 requests in the 40 minutes returned 503, which is 2.17% on average. We do not have GET counts per interval.

This case is opened after the 30-day period in section 6 ended on 2026-10-21.

Impact
662 uploads failed: 641 before 14:25 and 21 after. We re-queued them by hand at 14:52, and all succeeded. The upload queue backed up during the retry window and drained by 14:58.

Our mitigation
Until 14:25 the uploader did not retry a 503 on this path. At 14:25:00 we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts). It stays in production.

    Window          Uploads   PUT attempts   503 per attempt   Uploads failed
    14:05-14:25     8114      8114           641 (7.90%)       641 (7.90%)
    14:25-14:45     6652      7207           576 (7.99%)       21 (0.32%)

The backoff cut failed uploads from 7.90% to 0.32%. The 503 share per attempt did not change, and the errors ended at 14:44:51 with no change on our side at that time.

Redaction
We removed the names of our internal hosts and services and the request signature. Account, bucket, request, and host identifiers are as they appear in your systems.

## What do you need from us?

1. Tell us whether Tessary had a fault or maintenance in eu-north-2 that affected PUT requests between 14:05:12Z and 14:44:51Z on 2026-09-21. If it did, give the start time, the end time, and the cause, checked against the request IDs in the attached CSV.
2. Tell us whether Tessary throttled account acc-7f3e9120 or any prefix in lm-prod-ingest-eun2 or lm-prod-thumbs-eun2 in that period, or scaled a partition. If it did, name the prefix and the limit that applied.
3. Tell us whether these 503 responses count as Error Rate under section 3 of the SLA or fall under the exclusion for documented request rates. If they count, tell us the service credit under section 5 and your calculation of the Monthly Uptime Percentage for September 2026.
4. Tell us whether the credit can still be applied, as this case is opened after the 30 days in section 6.

## Attachments

slowdown-requests-2026-09-21.csv (118 KB): 1217 rows with timestamp (UTC), bucket, object key, request ID, and host ID, one row per 503 SlowDown. Object keys are UUIDs.
