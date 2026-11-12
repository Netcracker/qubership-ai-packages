# Hand-over note: Tessary SlowDown case

The case itself is in `draft.md`. I did not file it, use a browser, or touch the network. Everything in the draft comes
from the session notes of 2026-09-22 and 2026-09-23.

## Decide before filing

- **The SLA claim window has probably closed.** SLA §6 asks for a support ticket "within 30 days of the incident". The
  incident was on 2026-09-21, so the window ended on 2026-10-21, and today is 2026-10-31. If no case was opened by
  2026-10-21, decide whether to keep item 3 of "What do you need from us?" as it stands, ask Tessary for the credit as a
  goodwill exception, or drop it and tell Finance. Items 1 and 2 stand without item 3, so you can delete item 3 and
  leave the rest unchanged.
- **The credit arithmetic assumes no other unavailable interval in September.** The 99.907% figure counts only the
  eight intervals we know of. Check whether any other September interval had more than 1% 500 or 503 responses in
  eu-north-2, including the incident the week before. The Slack thread traced that one to a bad deploy on our side,
  but our deploy does not decide whether Tessary returned 5xx. One more unavailable interval gives 99.896%, which is
  below 99.9%, where §5 gives 25%. The ticket asks Tessary to confirm against its own measurements, so it makes no
  claim beyond our log.
- **Severity S3.** The errors ended at 14:44:51 UTC, the failed uploads were re-sent and succeeded, and you are asking
  for a root cause, a throttling answer, and a credit. That fits the form's S3 definition. S1 and S2 require a
  production workload that is down or impaired now.
- **Source IPs stay in the ticket.** `203.0.113.41` and `203.0.113.42` are the cluster's public egress addresses, not
  internal hostnames. Tessary can look up requests and per-IP throttling by them. If the vendor-communication rule
  covers them, delete the line in "Account and client" and the IPs in item 2.

## Before you attach the CSV

I did not open `slowdown-requests-2026-09-21.csv`. The notes say it has 1217 rows (timestamp, bucket, object key,
request ID, host ID) and is 118 KB, well under the 25 MB limit. Open it and check that:

- it has only those five columns, with no internal hostname, service name, or `Authorization` value;
- the host ID column holds Tessary's `x-tess-host-id` values (`eun2-fe-…`), not our host names;
- it has 1217 data rows. If the 1217 rows include a header line, the "1217 rows" label under Attachments is off by one.

## What I changed for the vendor rule

- `ingest-07.lm-prod.internal` in the debug log became `uploader-01.example.internal`.
- The `Authorization` header value was replaced with a placeholder, because it carried the access key ID and the
  request signature. The account ID identifies the account and the request IDs identify the requests, so Tessary needs
  neither credential value.
- `mediapipe-uploader` is written as "our upload service".
- Bucket names, the account ID, object keys (UUIDs), request IDs, Tessary host IDs, and the Tessary endpoint URL are
  kept, because Tessary finds the requests by them.

## Lookups I could not make (no network)

- Re-read https://status.tessary.cloud and its history for 2026-09-21. Tessary may have added an incident after
  2026-09-22. If an incident covers 14:05 to 14:45 UTC, cite it in the description and ask item 1 against it.
- Check whether Tessary has a known-issues page. The notes mention only the status page.
- Re-read the request-rates page and the SLA (§3 to §6). The quotes are from the session notes. Confirm that the
  wording is the same today, especially the "while a partition is being scaled" sentence and the §3 exclusion.
- The rates in the ticket (6.4 PUT/s total, 5.9 PUT/s on the busiest prefix) are averages over 40 minutes. If Tessary
  asks about per-second peaks, compute them from the uploader's request log. The total was 15321 attempts in 40
  minutes, so no second can have reached 3500 PUT/s, but I did not measure peaks.

## Left out of the case on purpose

None of these items helps Tessary answer the three questions. Add any of them back only if Tessary asks.

- The on-call Slack thread and the earlier incident it linked.
- The 14 Grafana "Uploads Overview" panels.
- Things the team tried that changed nothing: pod restarts (16:14 CEST), the thumbnail-service rollback (16:18 CEST),
  the higher pod memory limit, and the DNS cache flush.
- The queue backlog that drained by 14:58 UTC.

## Disclosure

Neither Tessary nor Lindqvist Media has an AI policy, so the case says nothing about how it was drafted.

## Length check

The Subject is 99 characters, under the 120 limit. The Description field is about 4000 characters by my estimate,
well under the 10000 limit. The portal's counter gives the exact figure.
