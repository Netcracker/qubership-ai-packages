# Hand-over note for the Tessary case

This note is for you, not for Tessary. The case fields are in `result.md`; paste each one into the portal field of the same name. Nothing was filed.

## Before you file

- **Read the attachment before you upload it.** I did not open `slowdown-requests-2026-09-21.csv`. Your notes list its columns as timestamp, bucket, object key, request ID, and host ID, which the vendor rule allows. Check that it carries no internal host name, service name, or credential column, and that it has 1,217 data rows: `head -3 slowdown-requests-2026-09-21.csv; grep -Ei 'lm-prod.internal|mediapipe|Credential|Signature' slowdown-requests-2026-09-21.csv | wc -l` should print the header and two rows, then `0`.
- **SLA deadline.** SLA §6 requires the case within 30 days of the incident, so file by 2026-10-21.
- **Re-check the status page history** for 2026-09-21 on the day you file. The case cites the reading from 2026-09-22 09:00 UTC; if Tessary has since posted an incident, cite it in the case and adjust question 1.
- **Pick the Service dropdown entry** that corresponds to Object Storage; the notes do not give the exact label.

## Gaps the case states or depends on

- **The SLA figure is computed over PUT requests only.** Tessary's §3 Error Rate may count every request in the region. Your notes have GET counts only for the whole 40 minutes (41,210 requests, 9 SlowDown), not per interval. Spread evenly, GETs would bring each interval to about 2%, still above 1%, but that is an estimate. To close it, count GETs and their 503s per 5-minute interval from the uploader's request log and recompute each interval's error rate over all requests. The case says the count is client-side and over PUT requests.
- **99.907% assumes no other unavailable interval in September**, and the month is not over. The case says so. The credit tier (10%) changes only if the month drops below 99.9%.
- **Same client for eu-west-3.** The case says the eu-west-3 PUTs came from the same client's request log, as your notes put them under the uploader's request log. Confirm the eu-west-3 bucket is written by the same uploader from the same egress addresses; if not, drop "from the same client's request log" from that heading.
- **Egress addresses 203.0.113.41 and 203.0.113.42 are in the case.** They are not internal host names, and Tessary sees them on every request, but confirm your vendor rule allows them. Tessary can use them to look up throttling on its side.

## What I changed or left out, and why

- Removed, per the vendor-communication rule: the internal host name in the SDK log line, the uploader's internal service name, the access key ID, and the request signature. The case says in one sentence what was removed.
- Kept, because Tessary locates the resources by them: account ID, bucket names, prefix, the Tessary endpoint host name, request IDs, and host IDs.
- Left out: the on-call Slack thread, the Grafana panels, the previous week's unrelated incident, the unrelated thumbnail-service rollback, and the pod memory change. None of them tells Tessary anything about its side. The pod restart and the DNS cache flush stay, stated generically, because they show the errors did not depend on our client processes or DNS resolution.
- All times are converted to UTC; the opening gives the CEST range once.

## Decisions that are yours

- **Severity.** I set S3: the errors ended at 14:44:51 UTC, the backoff mitigates them, and you want a root cause, information, and a credit, which is the S3 definition. Change it if you see it differently.
- **Credit request.** Finance asked for a credit, so question 3 asks for the §5 credit of 10% of eu-north-2 storage charges for September 2026. Remove it if Finance wants to wait for Tessary's root cause first.
- **Disclosure.** Neither Tessary nor Lindqvist Media has an AI policy, so the case carries no tool disclosure. The case was drafted with an AI tool; you file it under your name, so read it through and make sure you can answer Tessary's follow-up questions without it.
