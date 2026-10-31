# Hand-over note: Tessary case for the 2026-09-21 SlowDown burst

This note is for you, the person filing. It is not part of the case. Nothing has been filed or sent.

## Decide before filing

- **The SLA claim window may have closed.** SLA §6, as quoted in the notes, says: "Open a support ticket within 30 days of the incident with the dates, times, and request IDs of the errors." The incident was on 2026-09-21, so the 30 days ended on 2026-10-21. Today is 2026-10-31. You and Finance need to decide whether to keep item 3 (the credit) in "What do you need from us?", drop it, or take it up with your Tessary account contact instead. The draft does not mention the deadline. Whether to acknowledge the late filing in the case is up to you. Items 1 and 2 (root cause, throttling) are not affected by the deadline.
- **Severity S3.** I chose it because the errors stopped at 14:44:51 UTC, the backoff is still in production, and the case asks for a root cause, a credit, and information. The portal's S3 definition covers exactly that.
- **Disclosure.** Neither Tessary nor Lindqvist Media has an AI policy, so the case says nothing about how it was drafted. Add a line if you want to.

## Lookups I could not make (no network in this session)

- Re-check https://status.tessary.cloud history for 2026-09-21, and any known-issues or post-incident page. The draft cites the reading from 2026-09-22 09:00 UTC. A report published after that changes items 1 and 2.
- Re-read https://docs.tessary.cloud/storage/performance/request-rates and https://tessary.cloud/legal/storage-sla. The quotes in the draft come from the session notes, not from a fresh fetch. In the SLA, check two things: how the billing month is defined, and which requests the §3 Error Rate counts (all requests in the region, or per bucket or method).

## Claims that rest on assumptions

- **99.907% assumes September is the billing month and these eight are the only unavailable intervals in it.** The draft says "if". Before claiming a credit, check that no other September interval had an error rate above 1%.
- **The per-interval error rates count PUTs only.** The GETs (41210 requests, 9 SlowDown) are not split by interval. As an average across both methods, the rate is still about 2.2% (1226 of 56531). Spread evenly, every interval would stay above 1%, but that is not established per interval. To close the gap, count GET requests and GET 503s per five-minute interval from 14:05 to 14:45 UTC in the uploader's request log.
- **5.9 PUT/s for the busiest prefix is a 40-minute average.** Per-second peaks were not computed. Tessary may ask for them. Bucket the same log by second for `ingest/2026/09/21/`.
- **"The errors stopped on their own."** The draft only states the time of the last SlowDown and that all 11860 PUTs after it succeeded. The backoff went in 20 minutes earlier and did not change the per-attempt 503 rate (7.90% before, 7.99% after), so the draft does not credit it with the end of the burst.

## Redaction (vendor rule: no internal host names, service names, or credentials)

- Removed from the debug log excerpt: the host `ingest-07.lm-prod.internal`, the access key ID in `Credential=`, and the `Signature=` value. Each is replaced with a labeled placeholder. The rest of the excerpt is verbatim.
- `mediapipe-uploader` is called "our upload service" throughout.
- Kept, because Tessary finds the requests by them: the account ID, the bucket names, the object URL in the log excerpt, the request IDs, the host IDs, and the egress addresses `203.0.113.41` and `203.0.113.42`. If Tessary asks which access key sent the requests, give it the access key ID through the case. Never give it the secret key.
- **I did not open `slowdown-requests-2026-09-21.csv`.** Before attaching it, read it for internal host names, credentials, or extra columns beyond the five the notes describe (timestamp, bucket, object key, request ID, host ID). The object keys are UUIDs under bucket prefixes, which Tessary needs. At 118 KB it is within the 25 MB attachment limit. SLA §6 asks for the request IDs of the errors, so the attachment matters for the credit.

## Left out of the case on purpose

These don't help Tessary find or explain the throttling:

- The on-call Slack thread, including the link to the previous week's incident, which turned out to be your own bad deploy.
- The Grafana "Uploads Overview" panels.
- The steps that changed nothing: restarting the uploader pods (16:14 CEST), rolling back the thumbnail-service deploy (16:18 CEST), raising the pod memory limit, and flushing the node DNS cache. They involve internal names and say nothing about Tessary's side. The eu-west-3 comparison is the stronger evidence that the client was not the cause.
- The queue backlog that drained by 14:58 UTC.

## Format

- Description and "What do you need from us?" are plain-text fields with no Markdown rendering. Paste only what is between the ```text fence lines, not the fence lines themselves. The tables and the log excerpt are aligned with spaces for that reason.
- The Subject is 85 characters, under the 120-character limit.
- All times in the case are UTC, with CEST given once.
