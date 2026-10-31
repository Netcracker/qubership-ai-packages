# Hand-over note: Tessary case for the 2026-09-21 SlowDown burst

Nothing has been filed or sent. The case text is in `draft.md`, one block per portal field.

## Decide before filing

- **The SLA claim window has probably closed.** SLA section 6 says to open a ticket "within 30 days of the incident". The incident was on 2026-09-21, so the window ended around 2026-10-21, and today is 2026-10-31. Decide whether to keep the credit request anyway, take it to the Tessary account manager, or drop it. To drop it, delete the "Service credit" paragraph at the end of the description and item 3 under "What do you need from us?". The case still stands without them, and S3 still fits because it asks for a root cause.
- **Severity S3.** The errors stopped at 14:44:51 UTC, the backoff mitigated them, and the ask is a root cause and a credit. That matches the S3 definition. Change it if you see it differently.
- **The SLA figure is our arithmetic, not Tessary's.** The 99.907% assumes two things. First, the eight intervals count as unavailable on a PUT-only basis. The SLA text in the notes doesn't say what the Error Rate denominator is. If it includes GETs, we need per-interval GET counts to check each interval, and the notes only have the 40-minute total (41210 GETs, 9 SlowDown). Second, no other September interval was unavailable. 99.907% is above 99.9%, so the claim is for the 10% tier, not 25%. The case says this conditionally and leaves the Error Rate to Tessary's records.

## Not established

Tessary is likely to ask about these:

- **Our PUT rate before 14:05 UTC, and whether anything changed on our side at 14:05.** The notes don't cover either. Tessary will want to know whether the burst started with a jump in our traffic. The on-call thread links to a SlowDown incident the week before that turned out to be a bad deploy. Check the uploader request log for 13:00–14:05 UTC and the deploy history for 2026-09-21 before 14:05 UTC. If the rate was steady, add one line to the description saying so, with the numbers.
- **The PUT rate after 14:45 UTC was lower** (about 2.6 PUT/s against about 6.4 PUT/s during the burst). The case states this. Tessary may point to it, but both rates are far below the documented 3,500 per prefix.
- **Known-issues page.** The notes cover only the status page and its history. If Tessary has a known-issues or incident-history page apart from the status page, check it for 2026-09-21 in eu-north-2.
- **Status page and docs quotes** come from the notes taken on 2026-09-21 and 2026-09-22. I did not re-fetch them, because this session had no network access. Before filing, check that the request-rate page and the SLA sections still say what the case quotes.

## Check before attaching

- **`slowdown-requests-2026-09-21.csv`**: I couldn't open it. Per the notes it has 1217 rows with timestamp, bucket, object key, request ID, and host ID, and it's 118 KB, which is under the 25 MB limit. Before attaching it, confirm that no column or row contains an internal host name, an internal service name, or credentials, as the vendor-communication rule requires. The object keys are UUIDs under `ingest/...` prefixes. Tessary can look requests up by them.

## What was redacted, and what was kept

- Replaced in the debug log line: the internal host name `ingest-07.lm-prod.internal`. Removed: the access key ID in the `Credential=` part and the request signature. The service name `mediapipe-uploader` is called "our upload service" in the case.
- Kept, because Tessary finds the requests and resources by them: the account ID, the bucket names, the object key in the log line, the request IDs, the host IDs, and the egress addresses.

## Left out of the case

None of these helps Tessary answer the three questions. They're available if Tessary asks.

- The on-call Slack thread and the Grafana "Uploads Overview" panels.
- Actions that changed nothing during the incident: restarting the uploader pods (16:14 CEST), rolling back the thumbnail-service deploy (16:18 CEST), raising the pod memory limit, and flushing the node DNS cache.
- The manual re-queue of the 662 failed uploads at 14:52 UTC, which all succeeded, and the queue backlog that drained by 14:58 UTC.

## Other

- All times in the case are UTC. The on-call thread uses CEST (UTC+2), so 16:05–16:45 CEST is 14:05–14:45 UTC.
- Neither Tessary nor Lindqvist Media has an AI policy, so the case carries no disclosure. You should still be able to answer Tessary's follow-up questions without this draft.
