# Hand-over note: Tessary support case for the 2026-09-21 SlowDown burst

Not part of the case. The case text is in `result.md`; paste each block into the portal field of the same name. Nothing was filed, and no network lookup was made: everything comes from the session notes.

## Before you file

- **Deadline.** SLA §6 wants the ticket within 30 days of the incident, so file by 2026-10-20 to be safe (30 days after 2026-09-21 is 2026-10-21).
- **Severity S3.** The workload recovered at 14:44:51 UTC and the backoff is still in place; S3 matches the portal's own definition ("resolved or mitigated; you need a root cause, a credit, or information"). S2 would claim an ongoing impairment we do not have.
- **Read the CSV before attaching it.** I did not open `slowdown-requests-2026-09-21.csv`. The notes say it holds timestamp, bucket, object key, request ID, and host ID for 1217 rows. Check that it has no other column (for example our hostname or the service name) and that the row count is 1217.
- **Source addresses.** `203.0.113.41` and `203.0.113.42` sit in 203.0.113.0/24, which is the documentation range (TEST-NET-3). If the notes carry sanitized values, put the real egress addresses in the case or delete that line; Tessary may use them to find the traffic.
- **Access key ID.** I replaced the key ID and the signature in the debug log with placeholders. Tessary can find the requests by request ID, so the key ID should not be needed; if they ask for it, give only the key ID, never the secret.

## Company rule on vendor tickets

The rule "No internal hostnames, internal service names, or credentials in tickets to vendors" is applied: `ingest-07.lm-prod.internal` is redacted, `mediapipe-uploader` is called "our client", and the credentials are placeholders. Bucket names, the account ID, request IDs, and Tessary's host IDs stay, because Tessary locates the resources by them. The `lm-prod` in the bucket names is part of a Tessary resource name, not an internal hostname; confirm you read the rule the same way.

## Left out of the case on purpose

- The on-call Slack thread and the link to last week's bad-deploy incident: nothing in them is evidence about Tessary.
- The Grafana "Uploads Overview" panels (CPU, memory, GC, queue depth): internal, and no question from Tessary depends on them.
- Rolling back the thumbnail-service deploy and raising the pod memory limit: internal changes with no effect, and naming the service would break the vendor rule. The pod restart and the DNS cache flush stay, stated without service names, because they rule out a stuck client or a stale endpoint.
- The queue backlog draining by 14:58 UTC: internal, and the failed-upload counts already carry the impact.

## Not established, and how to close it

- **Tessary known-issues page.** Not checked; the notes cite only the status page. Look for a known-issues or incident-history page for Object Storage eu-north-2 on 2026-09-21 and, if it lists something, cite it in the case.
- **GET counts per five-minute interval.** The SLA Error Rate may be computed over all requests, not only PUT. The case gives the 40-minute total (2.17%, above 1%) but not the per-interval figure. Pull GET counts per interval from the request log if Tessary disputes any interval.
- **Billing month.** The 99.907% figure assumes the billing month is the calendar month of September (8640 intervals) and that no other interval this month was unavailable. September has not ended.
- **Credit tier.** 99.907% is below 99.99% and above 99.9%, which is the 10% tier of §5, not the 25% tier. The case asks Tessary to apply the §5 credit rather than naming a percentage, since Tessary's own interval count decides it. Tell Finance to expect 10% of the September eu-north-2 storage charges if Tessary accepts the intervals.
- **Time of the DNS cache flush.** The notes do not give it; the case says only "during the event". Add the time if you have it.
- **Which bucket the busiest prefix belongs to.** The notes give `ingest/2026/09/21/` at 5.9 PUT/s without a bucket; the case does the same.
- **Whether our backoff ended the burst.** The per-attempt 503 rate stayed at about 8% for twenty minutes after the backoff went in, then stopped at 14:44:51 UTC. The case states those facts and draws no conclusion; Tessary's answer to question 1 decides it.

## Numbers I computed from the notes

The per-interval error rates, the 7.94% total, the 2.17% combined PUT and GET rate (1226 of 56531), and 8632/8640 = 99.907% are my arithmetic on the notes' tables. I did not re-derive any count from the raw request log.

## Disclosure

Neither Tessary nor Lindqvist Media has an AI policy, so the case says nothing about how it was drafted.
