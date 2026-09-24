Tessary support portal, New case. Field values below; the Description and "What do you need from us?" blocks are plain text for the portal's plain-text boxes.

Severity: S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

Service: Object Storage

Region: eu-north-2

Subject: PUT returns 503 SlowDown at 6 PUT/s in eu-north-2, 2026-09-21 14:05-14:45 UTC

Attachments: slowdown-requests-2026-09-21.csv (118 KB)

Description:

On 2026-09-21 from 14:05:12 to 14:44:51 UTC (16:05-16:45 CEST), 7.94% of our PUT requests to two buckets in eu-north-2 failed with HTTP 503 SlowDown. Our PUT rate to the region was about 6.4 requests per second. Your request-rate page documents at least 3,500 PUT/s per prefix and 10,000 PUT/s per region, and your status page showed Object Storage in eu-north-2 as Operational throughout. All times in this case are UTC.

ACCOUNT AND CLIENT

  Account:           acc-7f3e9120, plan Performance
  Region:            eu-north-2
  Buckets:           lm-prod-ingest-eun2, lm-prod-thumbs-eun2
  Client:            Tessary Java SDK 2.14.3
  Source addresses:  203.0.113.41, 203.0.113.42

WHAT WE OBSERVED

Counts from our client's request log, PUT to both eu-north-2 buckets, per five-minute interval:

  Interval (UTC)   PUT attempts   503 SlowDown   Error rate
  14:05-14:10      2031           158            7.78%
  14:10-14:15      2044           163            7.97%
  14:15-14:20      2012           161            8.00%
  14:20-14:25      2027           159            7.84%
  14:25-14:30      1806           147            8.14%
  14:30-14:35      1811           142            7.84%
  14:35-14:40      1797           146            8.12%
  14:40-14:45      1793           141            7.86%
  Total            15321          1217           7.94%

The first SlowDown came at 14:05:12.448Z and the last at 14:44:51.302Z. No other status code above 499 appeared. The busiest prefix, ingest/2026/09/21/, received 5.9 PUT/s.

In the same 40 minutes, with one thing varied at a time:

- GET to the same two buckets: 41210 requests, 9 SlowDown (0.02%).
- PUT from the same client to lm-prod-ingest-euw3 in eu-west-3: 14870 requests, none failed.
- Restarting our client processes at 14:14 UTC and flushing the DNS cache on our nodes did not change the error rate.

From 14:45 to 16:00 UTC, 11860 PUTs to eu-north-2 succeeded with no failures.

Five of the failed requests (all 1217 are in the attached CSV, with timestamp, bucket, object key, request ID, and host ID):

  Time (UTC)      Bucket                x-tess-request-id  x-tess-host-id
  14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18   eun2-fe-3a71
  14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46   eun2-fe-3a64
  14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973   eun2-fe-3a71
  14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865   eun2-fe-3a58
  14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537   eun2-fe-3a64

The first of them as the SDK debug log printed it. Our internal hostname and the request credentials are redacted; nothing else is changed.

  2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal hostname>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: request signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

STATUS PAGE

https://status.tessary.cloud, checked at 14:12 and 14:31 UTC on 2026-09-21: "Object Storage, eu-north-2: Operational". Its history, read at 09:00 UTC on 2026-09-22, shows "No incidents reported" for 2026-09-21.

REQUEST RATES AND THE SLA

https://docs.tessary.cloud/storage/performance/request-rates states: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10,000 PUT/s per region. Our busiest prefix received 5.9 PUT/s and the region 6.4 PUT/s. We cannot see whether a partition was being scaled.

https://tessary.cloud/legal/storage-sla section 3 counts 503 responses toward the Error Rate "except 503 responses caused by exceeding the documented request rates", and marks a 5-minute interval unavailable when its Error Rate exceeds 1%. Each of the eight intervals above has a PUT error rate between 7.78% and 8.14%. Counting GET as well, the 40 minutes had 1226 errors in 56531 requests (2.17%); we do not have the GET counts per interval.

Our calculation: if these eight are the only unavailable intervals in September (8640 intervals), the Monthly Uptime Percentage under section 4 is 8632/8640 = 99.907%, below the 99.99% threshold of section 5. September has not ended, so this covers the month only up to the date of this case.

MITIGATION ON OUR SIDE

Until 14:25:00 UTC our client made one attempt per upload and did not retry a 503. At 14:25:00 UTC we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts), and it remains in place.

  Window (UTC)          Uploads  PUT attempts  503 per attempt  Uploads failed
  14:05-14:25 no retry  8114     8114          641 (7.90%)      641 (7.90%)
  14:25-14:45 backoff   6652     7207          576 (7.99%)      21 (0.32%)

The backoff cut failed uploads from 7.90% to 0.32%; the 503 rate per attempt stayed at about 8%. The 503s stopped at 14:44:51 UTC, twenty minutes after the backoff went in. The 662 uploads that failed were re-submitted at 14:52 UTC and all succeeded.

What do you need from us?:

1. Was there an event in Object Storage in eu-north-2 on 2026-09-21 that caused these 503 SlowDown responses? If so, when did it start and when did it end?

2. Did Tessary throttle account acc-7f3e9120, the buckets lm-prod-ingest-eun2 and lm-prod-thumbs-eun2, or their prefixes, or was a partition being scaled? At about 6 PUT/s, what triggered it?

3. Under section 6 of the Storage SLA, this case is our service credit request for the eight intervals from 14:05 to 14:45 UTC on 2026-09-21, with the request IDs in the attached CSV. Confirm whether these 503 responses count toward the Error Rate under section 3, and apply the credit section 5 gives for September on the eu-north-2 storage charges.
