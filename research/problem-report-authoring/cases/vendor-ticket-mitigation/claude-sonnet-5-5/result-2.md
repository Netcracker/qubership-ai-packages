Severity: S3 (Issue resolved or mitigated; you need a root cause, a credit, or information)

Service: Object Storage

Region: eu-north-2

Subject: 503 SlowDown on PUT in eu-north-2, 2026-09-21 14:05 to 14:45 UTC, at about 6 PUT/s: cause and SLA credit

Attachments: slowdown-requests-2026-09-21.csv (118 KB)

Description:

Account acc-7f3e9120 (plan "Performance"). On 2026-09-21 from 14:05:12.448Z to 14:44:51.302Z (16:05 to 16:45 CEST), our upload service got HTTP 503 SlowDown on 1217 of 15321 PUT requests to lm-prod-ingest-eun2 and lm-prod-thumbs-eun2 in eu-north-2. Our PUT rate over those 40 minutes was about 6.4/s in total and 5.9/s on the busiest prefix, ingest/2026/09/21/. The documented rate is at least 3,500 PUT/s per prefix. The errors stopped on their own at 14:44:51Z.

All times below are UTC. The client is Tessary Java SDK 2.14.3, sending from 203.0.113.41 and 203.0.113.42.

What we observed, from our client's request log (PUT attempts to both eu-north-2 buckets, per five-minute interval):

  Interval        PUT attempts   503 SlowDown
  14:05 to 14:10  2031           158
  14:10 to 14:15  2044           163
  14:15 to 14:20  2012           161
  14:20 to 14:25  2027           159
  14:25 to 14:30  1806           147
  14:30 to 14:35  1811           142
  14:35 to 14:40  1797           146
  14:40 to 14:45  1793           141

No other status code above 499 occurred. Five of the failed requests follow. All 1217 are in the attached CSV (timestamp, bucket, object key, request ID, host ID).

  Time           Bucket               x-tess-request-id  x-tess-host-id
  14:05:47.212Z  lm-prod-ingest-eun2  9c41e0b27a6d4f18   eun2-fe-3a71
  14:12:03.884Z  lm-prod-ingest-eun2  2f7b93c05e1a8d46   eun2-fe-3a64
  14:21:39.017Z  lm-prod-thumbs-eun2  d05e6a18b4c2f973   eun2-fe-3a71
  14:33:10.551Z  lm-prod-ingest-eun2  71ac2d9e0f4b3865   eun2-fe-3a58
  14:44:51.302Z  lm-prod-ingest-eun2  e8d4f16a2b90c537   eun2-fe-3a64

One request as the SDK's debug log printed it. We replaced the uploader host name, the access key ID, and the signature with placeholders and changed nothing else.

  2026-09-21T14:05:47.212Z DEBUG tessary.http [<redacted: uploader host>] PUT https://lm-prod-ingest-eun2.eun2.storage.tessary.cloud/ingest/2026/09/21/0f/7c2e91d4-3b6a-4f0e-9d21-5a8e0c7b11f3.mxf
  > Authorization: TESS4-HMAC-SHA256 Credential=<redacted: access key ID>/20260921/eu-north-2/storage/tess4_request, SignedHeaders=host;x-tess-content-sha256;x-tess-date, Signature=<redacted: signature>
  < HTTP/1.1 503 Service Unavailable
  < x-tess-request-id: 9c41e0b27a6d4f18
  < x-tess-host-id: eun2-fe-3a71
  <Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message><RequestId>9c41e0b27a6d4f18</RequestId></Error>

What we compared, from the same request log:

- PUTs to lm-prod-ingest-euw3 in eu-west-3, same account and same client, in the same 40 minutes: 14870 requests, none failed.
- GETs on the two eu-north-2 buckets in the same 40 minutes: 41210 requests, 9 SlowDown.
- PUTs in eu-north-2 from 14:45 to 16:00: 11860 requests, none failed.
- Restarting the uploader pods, rolling back an unrelated deploy, raising the pod memory limit, and flushing the node DNS cache did not change the error rate.

What Tessary publishes:

- https://status.tessary.cloud showed "Object Storage, eu-north-2: Operational" when we checked at 14:12 and 14:31 on 2026-09-21. Its history, read on 2026-09-22 at 09:00, said "No incidents reported" for that day.
- https://docs.tessary.cloud/storage/performance/request-rates: "Tessary returns 503 SlowDown when a prefix exceeds this rate or while a partition is being scaled."
- SLA (https://tessary.cloud/legal/storage-sla), section 3: "A 5-minute interval is unavailable when its Error Rate exceeds 1%. Error Rate counts HTTP 500 and HTTP 503 responses, except 503 responses caused by exceeding the documented request rates."

In each of the eight intervals above, 7.8% to 8.1% of our PUT attempts got a 503. September has 8640 five-minute intervals, so eight unavailable intervals give 99.907% under SLA section 4. This is our estimate from our own traffic only. We do not know how Tessary measures Error Rate.

Effect on us: before 14:25 our uploader did not retry a 503 on this path, so 641 of 8114 uploads (7.90%) failed. At 14:25:00 we deployed exponential backoff with full jitter (base 100 ms, cap 5 s, at most 6 attempts). From 14:25 to 14:45, 576 of 7207 attempts (7.99%) still got a 503, and 21 of 6652 uploads (0.32%) failed. The share of attempts that got a 503 did not change. The upload queue backed up and drained by 14:58. We re-queued the 662 failed uploads by hand at 14:52, and all succeeded. The backoff stays in production.

Not established: we have no view of Tessary's side, so we do not know the cause. This case is opened more than 30 days after the incident, which is outside the window in SLA section 6.

What do you need from us? (field value):

1. Tell us whether Tessary had a problem in eu-north-2 on 2026-09-21, including a partition scale-up that touched our buckets or prefixes, and when it started and ended on your side. Our window is 14:05:12Z to 14:44:51Z.
2. Tell us whether the account, either bucket, or any prefix was throttled, and which limit applied. Our rates were far below the documented ones.
3. Tell us whether these 503 responses count toward Error Rate under SLA section 3, using the request IDs in the CSV. If they do, apply the service credit that SLA section 5 gives for the resulting Monthly Uptime Percentage, and tell us what you computed. Please also tell us whether you will accept this case after the 30 days in section 6.
