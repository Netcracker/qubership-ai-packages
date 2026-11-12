# Hand-over note: Tessary support case for the 2026-09-21 SlowDown burst

The case is in `draft.md`. Nothing has been filed. Paste each free-text field from inside its block, without the fence lines.

## Decide before filing

- **The SLA claim window has closed.** SLA §6 requires a ticket "within 30 days of the incident". The incident was on 2026-09-21, so the window ended on 2026-10-21. Today is 2026-10-31. The draft still asks for the credit, says the window has passed, and asks whether Tessary can grant it anyway. Decide whether to keep that request, and tell Finance. If you drop it, delete item 3 from "What do you need from us?". Keep the CSV attached either way, because the root-cause and throttling questions also need the request IDs.
- **Severity S3.** The failures stopped on 2026-09-21, and you are asking for a root cause, an answer about throttling, and a credit. That matches the portal's S3 definition. S2 requires a workload that is impaired now.

## Check before attaching or sending

- **Read `slowdown-requests-2026-09-21.csv` before attaching it.** I could not open it. The notes list five columns: timestamp, bucket, object key, request ID, and host ID. Before attaching, confirm that it has no other columns and that the host ID column holds Tessary's `x-tess-host-id` values (`eun2-fe-…`) and not our own hostnames, because the vendor rule forbids internal hostnames. The file is 118 KB, well under the portal's 25 MB limit.
- **Redaction.** In the description, the SDK log line has the internal hostname `ingest-07.lm-prod.internal`, the access key ID, and the request signature replaced with placeholders. `mediapipe-uploader` is called "our upload client". The account ID, bucket names, object key, request IDs, and Tessary host IDs stay because Tessary finds the requests by them.
- **Egress addresses kept.** `203.0.113.41` and `203.0.113.42` are in the description because Tessary may throttle by source address. They are not internal hostnames, service names, or credentials, so the vendor rule does not cover them. Remove them if you read the rule more strictly.
- **Service dropdown label.** I wrote "Object Storage", the name the status page uses. I could not see the portal's dropdown.

## Not established

Neither the case nor the notes establish the following. None of it is claimed in the case.

- **Peak per-second rate.** The 6.4 PUT/s and 5.9 PUT/s figures are 40-minute averages. Both are far below the documented 3500 PUT/s per prefix, so a peak is unlikely to matter, but Tessary may ask for it. To get it, group the uploader's request log for 2026-09-21 14:05–14:45 UTC by second and by key prefix, and take the maximum PUT count.
- **Which bucket the busiest prefix is in.** The notes name the prefix `ingest/2026/09/21/` without its bucket. The sample request puts it in `lm-prod-ingest-eun2`, but the case does not say so. The same request log answers this.
- **SLA error rate if GETs count.** SLA §3 does not say whether Error Rate covers all requests or PUTs only. The case gives per-interval rates for PUTs only, because the notes have no per-interval GET counts. Averaged across the 40 minutes, PUTs and GETs together give about 2.2% errors (1226 errors in 56531 requests), which is still above 1%. Per-interval GET counts from the request log would settle this for each interval.
- **Other unavailable intervals in September.** The 99.907% figure counts only these eight intervals. Any other unavailable interval in eu-north-2 in September lowers it further, and nine or more unavailable intervals would move the claim into the 25% tier. The case says "these eight intervals alone".
- **Duplicates and known issues.** The status-page checks are from 2026-09-21 and 2026-09-22, and they were made by someone on our side. The notes do not mention a Tessary known-issues page. Before filing, reload the status page history for 2026-09-21 in case Tessary has since posted an incident. Also check whether the account has an earlier open case about eu-north-2 SlowDown responses. If one exists, add this evidence to that case instead of opening a new one.

## Left out of the case on purpose

These items answer no question Tessary needs answered, or they would expose internal names:

- The on-call Slack thread, including the link to the previous week's incident, which was caused by our own deploy.
- The Grafana "Uploads Overview" panels.
- The actions that changed nothing during the incident: pod restarts, the rollback of the thumbnail-service deploy, the higher pod memory limit, and the DNS cache flush. The eu-west-3 and GET comparisons do more to show the problem was in eu-north-2 PUTs. Restating these actions would also mean naming internal services. If Tessary asks what we tried, you can name them then.
- The queue backlog and the 662 uploads re-queued by hand.

## Policy

Neither Tessary nor Lindqvist Media has an AI policy, so the case carries no disclosure.
