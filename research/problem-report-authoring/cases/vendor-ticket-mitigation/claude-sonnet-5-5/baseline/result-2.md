Tessary support portal, "New case". The Description and "What do you need from us?" fields render plain text, so both are written without Markdown.

SEVERITY
S3 (Issue resolved or mitigated; you need a root cause, a credit, or information)

SERVICE
Object Storage

REGION
eu-north-2

SUBJECT
eu-north-2: 1217 PUT 503 SlowDown on 2026-09-21 14:05-14:45 UTC at 6 PUT/s; cause, throttling, SLA credit

DESCRIPTION

On 2026-09-21 from 14:05 to 14:45 UTC (16:05 to 16:45 CEST), PUT requests from our upload service to the buckets lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 in eu-north-2 failed with HTTP 503 SlowDown. 1217 of 15321 PUT attempts failed (7.9%). The first SlowDown in our request log is at 14:05:12.448Z and the last at 14:44:51.302Z, after which the errors stopped without a change on our side. We need to know whether the cause was on the Tessary side and whether the account or its prefixes were throttled.

Account and client
- Account: acc-7f3e9120, plan Performance, region eu-north-2
- Buckets: lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 (eu-north-2); lm-prod-ingest-euw3 (eu-west-3, unaffected)
- Client: Tessary Java SDK 2.14.3
- Egress addresses: 203.0.113.41, 203.0.113.42
- All times below are UTC. All counts come from our upload service's request log. The log does not show other traffic to the account, if there was any.

PUT attempts and 503 SlowDown responses, both eu-north-2 buckets, per five-minute interval

    Interval       PUT attempts   503 SlowDown
    14:05-14:10    2031           158
    14:10-14:15    2044           163
    14:15-14:20    2012           161
    14:20-14:25    2027           159
    14:25-14:30    1806           147
    14:30-14:35    1811           142
    14:35-14:40    1797           146
    14:40-14:45    1793           141

The average was about 6.4 PUT/s. The busiest prefix, ingest/2026/09/21/, received 5.9 PUT/s. No response with a status code above 499 other than 503 appears in the log.

Five of the failed requests (all 1217 are in the attached slowdown-requests-2026-09-21.csv, with columns timestamp, bucket, object key, request ID, and host ID)

    Time (UTC)      Bucket                x-tess-request-id   x-tess-host-id
    14:05:47.212Z   lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
    14:12:03.884Z   lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
    14:21:39.017Z   lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
    14:33:10.551Z   lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
    14:44:51.302Z   lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of these requests as the SDK's debug log printed it. The internal host name and the Authorization header are redacted; the rest is verbatim.

    2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal host name>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
    > Authorization: <redacted: request signature header>
    < HTTP/1.1 503 Service Unavailable
    < x-tess-request-id: 9c41e0b27a6d4f18
    < x-tess-host-id: eun2-fe-3a71
    <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

What we compared
- GET requests to the same two buckets in the same 40 minutes: 41210 requests, 9 SlowDown (0.02%).
- PUT requests to lm-prod-ingest-euw3 in eu-west-3 from the same client in the same 40 minutes: 14870 requests, none failed.
- PUT requests in eu-north-2 from 14:45 to 16:00: 11860 requests, none failed.
- Changes on our side that did not change the error rate: restarting the upload service's processes at 14:14, rolling back an unrelated deploy of another internal service at 14:18, raising the memory limit of the upload service, and flushing the DNS cache on the hosts.

Why we do not think we exceeded a documented limit
The request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) says: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10,000 PUT/s per region. Our peak-prefix average of 5.9 PUT/s is far below both. The second condition on that page, a partition being scaled, is something we cannot see from the client.

Status page
We checked https://status.tessary.cloud at 14:12 and 14:31 on 2026-09-21: "Object Storage, eu-north-2: Operational". Its history, read on 2026-09-22 at 09:00, showed "No incidents reported" for 2026-09-21. We have not re-read it since.

What we did about it, and its effect
Until 14:25 our upload service did not retry a 503 on this path. At 14:25 we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts). It stays in production.

    Window         Uploads   PUT attempts   503 per attempt   Uploads failed
    14:05-14:25    8114      8114           641 (7.90%)       641 (7.90%)
    14:25-14:45    6652      7207           576 (7.99%)       21 (0.32%)

The 503 rate per attempt did not change with the backoff. Only the share of uploads that ended in failure fell. The upload queue backed up during the second window and drained by 14:58. The 662 uploads that had failed were re-queued by hand at 14:52 and all succeeded. This is the only impact we observed.

SLA
Section 3 of the Performance plan SLA (https://tessary.cloud/legal/storage-sla) says: "A 5-minute interval is unavailable when its Error Rate exceeds 1%. Error Rate counts HTTP 500 and HTTP 503 responses, except 503 responses caused by exceeding the documented request rates." All eight intervals above had a PUT error rate of at least 7%. Counting these eight of the 8640 five-minute intervals in September as unavailable, and nothing else, gives 99.907% by the formula in section 4. We do not know how Tessary aligns its intervals, or whether it measures Error Rate for all requests of the account, the region, or the bucket, so we ask you to do this calculation rather than rely on ours.

Redaction
Internal host and service names, and the request signature, were removed or replaced with generic wording. Bucket names, the account ID, request IDs, host IDs, and the egress addresses are unchanged so you can find the requests.

WHAT DO YOU NEED FROM US?

1. Did Tessary have a fault, a maintenance event, or a partition scaling operation in eu-north-2 on 2026-09-21 that affected the front ends eun2-fe-3a58, eun2-fe-3a64, or eun2-fe-3a71, or the prefix ingest/2026/09/21/ in either bucket? If so, when did it start and end?
2. Was acc-7f3e9120 or any of its prefixes throttled between 14:05 and 14:45 UTC? For the request IDs in the attached CSV, which condition produced each SlowDown: a prefix over its rate, an account over its limit, or a partition being scaled? What request rate per prefix does Tessary's own data show for that period?
3. Should the status page have shown an incident for that period?
4. Do the eight intervals count as unavailable under section 3 of the SLA, and if so, what credit applies under section 5? We are opening this case more than 30 days after the incident, which is outside the window in section 6. We ask you to consider the credit despite that, and to answer questions 1 to 3 in any case.

If you need anything else from us, such as the access key ID or more of the request log, tell us which and we will send it through whatever private channel you name.

ATTACHMENTS
slowdown-requests-2026-09-21.csv (118 KB, 1217 rows)
