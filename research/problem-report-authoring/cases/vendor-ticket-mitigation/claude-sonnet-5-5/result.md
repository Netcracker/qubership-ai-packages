Tessary support portal, "New case". The headings below only separate the fields; paste each value as plain text.

## Severity

S3

## Service

Object Storage

## Region

eu-north-2

## Subject

eu-north-2: PUT 503 SlowDown 2026-09-21 14:05-14:45 UTC at 6.4 PUT/s from us; documented 3500/s per prefix

## Description

On 2026-09-21 from 14:05:12.448Z to 14:44:51.302Z, PUT requests from our upload cluster to two buckets in eu-north-2 were rejected with HTTP 503 SlowDown. 1217 of 15321 PUT attempts failed (7.9%). The errors stopped on their own at 14:44:51 UTC. The retry change we deployed at 14:25 did not stop them. All times below are UTC (CEST is UTC+2).

Account: acc-7f3e9120, plan Performance.
Buckets: lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 (eu-north-2).
Source addresses: 203.0.113.41 and 203.0.113.42, using the Tessary Java SDK 2.14.3.

PUT attempts and 503 SlowDown responses per five-minute interval, both buckets, from our request log:

    Interval       PUT attempts   503 SlowDown
    14:05-14:10    2031           158
    14:10-14:15    2044           163
    14:15-14:20    2012           161
    14:20-14:25    2027           159
    14:25-14:30    1806           147
    14:30-14:35    1811           142
    14:35-14:40    1797           146
    14:40-14:45    1793           141

That is 6.4 PUT/s over the 40 minutes. The busiest prefix, ingest/2026/09/21/, took 5.9 PUT/s. We saw no 5xx status other than these 503 responses.

Over the same 40 minutes, on the same two buckets, 9 of 41210 GET requests returned SlowDown (0.02%). PUTs to our bucket lm-prod-ingest-euw3 in eu-west-3 numbered 14870, and none failed. From 14:45 to 16:00, 11860 PUTs to eu-north-2 all succeeded.

Five of the failed requests (all 1217 are in the attached slowdown-requests-2026-09-21.csv: timestamp, bucket, object key, request ID, host ID):

    Time           Bucket                x-tess-request-id   x-tess-host-id
    14:05:47.212Z  lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
    14:12:03.884Z  lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
    14:21:39.017Z  lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
    14:33:10.551Z  lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
    14:44:51.302Z  lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first one as the SDK's debug log printed it. We replaced our internal host name, the access key ID, and the signature with placeholders:

    2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal host>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
    > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
    < HTTP/1.1 503 Service Unavailable
    < x-tess-request-id: 9c41e0b27a6d4f18
    < x-tess-host-id: eun2-fe-3a71
    <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

Retries. Until 14:25 our uploader did not retry a 503. From 14:25 it retries with exponential backoff and full jitter (base 100 ms, cap 5 s, at most 6 attempts). The share of attempts that got a 503 did not change:

    Window         Uploads   PUT attempts   503 per attempt   Uploads failed
    14:05-14:25    8114      8114           641 (7.90%)       641 (7.90%)
    14:25-14:45    6652      7207           576 (7.99%)       21 (0.32%)

The 662 uploads that failed were re-queued by hand at 14:52 and all succeeded. The backoff stays in production.

On our side, our on-call engineer restarted the uploader processes at 14:14 and flushed the DNS cache on the hosts during the incident. Neither changed the error ratio.

What Tessary publishes:

- Status page https://status.tessary.cloud: we looked at 14:12 and 14:31 UTC on 2026-09-21 and it showed "Object Storage, eu-north-2: Operational". Its history, read on 2026-09-22 at 09:00 UTC, showed "No incidents reported" for 2026-09-21.
- https://docs.tessary.cloud/storage/performance/request-rates: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The account limit on that page is 10,000 PUT/s per region. Our busiest prefix ran at about 1/600 of the prefix figure.
- SLA https://tessary.cloud/legal/storage-sla, Performance plan, section 3: "A 5-minute interval is unavailable when its Error Rate exceeds 1%. Error Rate counts HTTP 500 and HTTP 503 responses, except 503 responses caused by exceeding the documented request rates."

Each of the eight intervals from 14:05 to 14:45 had a PUT 503 ratio between 7.8% and 8.1%. By our own count, eight unavailable intervals out of the 8640 in September give a Monthly Uptime Percentage of 99.907%, if no other interval in the month was unavailable, which we cannot see. We read section 5 as a 10% credit for that figure.

## What do you need from us?

1. Was there a fault, a capacity change, or a partition scaling in eu-north-2 that affected lm-prod-ingest-eun2 or lm-prod-thumbs-eun2 between 14:05 and 14:45 UTC on 2026-09-21? If so, the start and end times in UTC, and an incident or root-cause reference we can cite.
2. Was any throttle applied to account acc-7f3e9120 or to a prefix of those buckets? If so, which limit, and what reason do your logs show for the request IDs in the attached file?
3. Do you count the eight intervals from 14:05 to 14:45 UTC as unavailable under section 3 of the Storage SLA? We do not believe the 503 responses were caused by exceeding the documented request rates. If you disagree, tell us which rate we exceeded and by how much.
4. If they count, the service credit due under section 5, and how we claim it. Please treat this case as our notice under section 6, with the dates, times, and request IDs above.

## Attachments

slowdown-requests-2026-09-21.csv (118 KB)
