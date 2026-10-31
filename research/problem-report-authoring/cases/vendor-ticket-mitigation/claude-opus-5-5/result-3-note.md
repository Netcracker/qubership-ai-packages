# Hand-over note: Tessary support case for the 2026-09-21 SlowDown errors

The case is in `draft.md` and nothing has been filed. Everything in it comes from the session notes. I had no
network access, so I checked nothing against Tessary, and I didn't open the CSV.

## Decide before filing

- **The SLA claim window has closed.** §6 of the SLA requires a support ticket "within 30 days of the
  incident". The incident was on 2026-09-21, so the window closed on 2026-10-21. Today is 2026-10-31. If a
  case about this incident was already opened before 2026-10-21, add this material to that case and don't open
  a new one. If none was opened, choose one of these:
  - Keep item 3 of "What do you need from us?" and the "Service level" paragraph, and add a sentence asking
    Tessary to accept the claim late.
  - Delete both, and send only the questions about root cause and throttling.

  Finance asked for the credit, so they may want to make this call.
- **Severity S3.** The form defines S3 as "Issue resolved or mitigated; you need a root cause, a credit, or
  information", and the errors stopped at 14:44:51 UTC. Raise it only if errors are happening again.

## Check before filing

- **Read `slowdown-requests-2026-09-21.csv` before attaching it.** I worked from the notes' description
  (1217 rows: timestamp, bucket, object key, request ID, host ID; 118 KB). Check three things: the file has
  no column beyond those five, no row contains a credential or an internal host name, and the timestamps are
  in UTC like the rest of the case.
- **Find out whether Error Rate counts GETs.** The per-interval table and the "over 1%" claim count PUTs
  only. Over the full 40 minutes, PUTs and GETs together were 1226 errors in 56531 requests (2.17%). The
  notes have no per-interval GET counts. If SLA §3 counts all requests together, run the request-log query
  per 5-minute interval to confirm that every interval is still above 1%.
- **Check the 99.907% figure.** It assumes the billing month is the calendar month (8640 intervals) and that
  no other interval in September was unavailable. The case states both assumptions.
- **Re-read the cited pages** in case they changed after the session notes: the request-rate page, SLA §3–§6,
  and the status-page history for 2026-09-21. Tessary may have added a post-incident note after 2026-09-22.
  Also check for a known-issues page; I couldn't look.

## What I changed for the vendor channel

Lindqvist Media's rule is "No internal hostnames, internal service names, or credentials in tickets to
vendors." Here's what I changed:

- The SDK log line is redacted in place, and the case says so. I replaced the whole Authorization header
  (access key ID and signature) and the client host name `ingest-07.lm-prod.internal` with placeholders. If
  Tessary needs the key ID, send it on request. They can also find the requests by request ID.
- I wrote `mediapipe-uploader` as "our upload service".
- I kept the account ID, bucket names, object key, request IDs, host IDs, and egress addresses
  `203.0.113.41` and `203.0.113.42`. Tessary needs them to find the traffic.

## Left out of the case on purpose

None of these answers a question Tessary will ask:

- The on-call Slack thread and the Grafana "Uploads Overview" panels.
- What was tried during the incident and changed nothing: the pod restart at 16:14 CEST, the rollback of the
  thumbnail-service deploy at 16:18 CEST, the higher pod memory limit, and the DNS cache flush. Add them if
  Tessary asks whether the client was at fault.
- The queue drained by 14:58 UTC, and the 662 failed uploads were re-queued by hand at 14:52 UTC and
  succeeded.
- Times in CEST. The case uses UTC throughout (16:05–16:45 CEST is 14:05–14:45 UTC).

The case lists 11860 clean PUTs from 14:45 to 16:00 UTC. That's about 2.6 PUT/s, below the incident rate of
6.4 PUT/s. So the case doesn't say the rate was the same after the errors stopped.

## Disclosure

Neither Tessary nor Lindqvist Media has an AI policy, so the case doesn't mention that a tool drafted it.
