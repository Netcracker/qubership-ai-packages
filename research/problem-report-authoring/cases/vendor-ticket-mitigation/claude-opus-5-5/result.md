Tessary support portal, "New case". Each field below is pasted into the portal field of the same name. The portal renders plain text, so the Description and the answer to "What do you need from us?" contain no Markdown.

---

Severity:
S3 "Issue resolved or mitigated; you need a root cause, a credit, or information"

Service:
Object Storage

Region:
eu-north-2

Subject:
PUT returns 503 SlowDown at 6 requests/s in eu-north-2, 2026-09-21 14:05-14:45 UTC (account acc-7f3e9120)

Description:

On 2026-09-21 from 14:05:12 UTC to 14:44:51 UTC (16:05 to 16:44 CEST), 1,217 of 15,321 PUT requests to our two eu-north-2 buckets failed with HTTP 503 SlowDown, about 8% in every 5-minute interval. Our PUT rate across both buckets was 6.4 requests/s, and the busiest prefix, ingest/2026/09/21/, received 5.9 requests/s. The errors stopped at 14:44:51 UTC without any change on our side that lowered the error rate. Your status page showed eu-north-2 Object Storage as Operational during the incident.

Account and resources
- Account: acc-7f3e9120, plan Performance
- Buckets: lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 (eu-north-2); for comparison, lm-prod-ingest-euw3 (eu-west-3)
- Client: Tessary Java SDK 2.14.3
- Source addresses: 203.0.113.41 and 203.0.113.42
- All times are UTC.

PUT attempts and 503 SlowDown responses, both eu-north-2 buckets, per 5-minute interval (from our client's request log)

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

No other status code above 499 was returned in this window.

Five of the failed requests (all 1,217 are in the attached slowdown-requests-2026-09-21.csv, with timestamp, bucket, object key, request ID, and host ID)

  Time (UTC)       Bucket                x-tess-request-id   x-tess-host-id
  14:05:47.212Z    lm-prod-ingest-eun2   9c41e0b27a6d4f18    eun2-fe-3a71
  14:12:03.884Z    lm-prod-ingest-eun2   2f7b93c05e1a8d46    eun2-fe-3a64
  14:21:39.017Z    lm-prod-thumbs-eun2   d05e6a18b4c2f973    eun2-fe-3a71
  14:33:10.551Z    lm-prod-ingest-eun2   71ac2d9e0f4b3865    eun2-fe-3a58
  14:44:51.302Z    lm-prod-ingest-eun2   e8d4f16a2b90c537    eun2-fe-3a64

The first of these as the SDK debug log printed it. We removed our internal host name, the access key ID, and the signature; the rest is as logged.

  2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: internal host name>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

What else we saw in the same 40 minutes, from the same client's request log
- GET requests to the same two eu-north-2 buckets: 41,210 requests, 9 SlowDown (0.02%).
- PUT requests to lm-prod-ingest-euw3 in eu-west-3: 14,870 requests, none failed.
- From 14:45 to 16:00 UTC: 11,860 PUT requests to the eu-north-2 buckets, none failed.
- Restarting our client processes at 14:14 UTC and flushing the DNS cache on our nodes did not change the error rate.

Why we do not think we exceeded a documented rate
Your request-rate page (https://docs.tessary.cloud/storage/performance/request-rates) states: "Each prefix supports at least 3,500 PUT, COPY, POST, or DELETE requests per second. Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled." The same page gives an account limit of 10,000 PUT/s per region. Our peak was 5.9 PUT/s on one prefix and 6.4 PUT/s in the region.

Status page
We checked https://status.tessary.cloud at 14:12 and 14:31 UTC on 2026-09-21; both times it showed "Object Storage, eu-north-2: Operational". On 2026-09-22 at 09:00 UTC its history showed "No incidents reported" for 2026-09-21.

Mitigation on our side
Until 14:25 UTC our client did not retry a 503 on this path. At 14:25:00 UTC we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts), and it remains in place. The backoff reduced failed uploads from 7.90% to 0.32%; the 503 rate per attempt was 7.90% before and 7.99% after, so the retries did not lower the error rate.

  Window (UTC)             Uploads   PUT attempts   503 per attempt   Uploads failed
  14:05-14:25, no retry    8114      8114           641 (7.90%)       641 (7.90%)
  14:25-14:45, backoff     6652      7207           576 (7.99%)       21 (0.32%)

Impact: 662 uploads failed. We re-sent them at 14:52 UTC and all succeeded; our upload backlog cleared by 14:58 UTC.

Service credit
Your Storage SLA (https://tessary.cloud/legal/storage-sla), §3, counts a 5-minute interval as unavailable when its Error Rate exceeds 1%, excluding "503 responses caused by exceeding the documented request rates". By our client-side count, computed over PUT requests, the eight intervals from 14:05 to 14:45 UTC each had an error rate between 7.78% and 8.14%. Eight unavailable intervals out of the 8,640 in September give a Monthly Uptime Percentage of 99.907% under §4, below the 99.99% threshold in §5. This assumes no other unavailable intervals in September. This case is opened under §6 with the dates, times, and request IDs above and in the attachment.

What do you need from us?:

1. Did Object Storage in eu-north-2 have a problem affecting PUT requests on 2026-09-21, and if so, when did it start and end?
2. Did Tessary throttle account acc-7f3e9120, the buckets lm-prod-ingest-eun2 and lm-prod-thumbs-eun2, or the prefix ingest/2026/09/21/ in that window, or was a partition for these buckets being scaled? If so, why at about 6 PUT requests/s?
3. Can you confirm that the 503 responses in the eight intervals from 14:05 to 14:45 UTC count toward the Error Rate under SLA §3, and apply the §5 service credit (10% of the eu-north-2 storage charges for September 2026) to account acc-7f3e9120?

Attachments:
slowdown-requests-2026-09-21.csv (118 KB, 1,217 rows: timestamp, bucket, object key, request ID, host ID)
