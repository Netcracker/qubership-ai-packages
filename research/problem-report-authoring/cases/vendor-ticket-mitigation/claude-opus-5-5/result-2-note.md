# Hand-over note: Tessary case for the 2026-09-21 SlowDown errors

This note is for you, not for Tessary. The case is in `draft.md`, with one block per portal field in the form's order.
I didn't file anything or open any page. Everything in the case comes from the session notes of 2026-09-22 and
2026-09-23.

## Decide before filing

- **The credit window may have closed.** SLA §6 asks for a ticket "within 30 days of the incident". Counted from
  2026-09-21, that deadline was 2026-10-21, and today is 2026-10-31. If no case was opened before then, you have
  three options. You can keep request 3 and the "Service level" section and ask anyway. You can open the case with
  only requests 1 and 2. Or you can check first whether an earlier case or email to Tessary support counts as the
  claim. Finance asked for the credit, so they may want a say in this.
- **Severity S3.** I picked it because the form defines S3 as "Issue resolved or mitigated; you need a root cause, a
  credit, or information". That matches this case: the errors stopped on 2026-09-21 and the backoff is in production.
- **Service and Region dropdowns.** I used "Object Storage" because the status page uses that name, and "eu-north-2".
  I couldn't see the dropdown labels, so pick the closest options.

## Check before attaching or pasting

- **Open `slowdown-requests-2026-09-21.csv` before you attach it.** I haven't seen the file, only its description
  (columns timestamp, bucket, object key, request ID, host ID; 1217 rows; 118 KB). Make sure it has no hostname,
  service name, or credential column. The object keys are UUIDs, and Tessary needs them along with the request IDs.
- **Re-open the three Tessary pages the case quotes**, because they may have changed since the session notes were
  written:
  - https://docs.tessary.cloud/storage/performance/request-rates: check the quoted sentence and the 10,000 PUT/s
    account limit.
  - https://tessary.cloud/legal/storage-sla: check §3–§6, and whether a different version applied on 2026-09-21.
  - https://status.tessary.cloud history for 2026-09-21: check whether Tessary posted an incident after
    2026-09-22 09:00 UTC. If it did, cite it in the case and shorten question 1.
- **Check for a known-issues page.** The notes mention only the status page. If Tessary has a known-issues page for
  Object Storage, look at 2026-09-21 there too.

## What the 99.907% figure assumes

I didn't change these assumptions in the case, but Tessary may question them:

- **The eight intervals are September's only unavailable intervals in eu-north-2.** The Slack thread links an incident
  from the week before, which turned out to be our own bad deploy. If that incident also produced 503 or 500 responses
  in eu-north-2, Tessary will count those intervals too, or exclude them as over the rate limit. Check the request log
  for September outside 14:05–14:45 on 2026-09-21.
- **The billing month is the calendar month.** 8640 intervals is 30 days. If your billing month runs on other dates,
  recompute.
- **The Error Rate counts PUT requests only.** If Tessary includes the 41210 GET requests, the 40-minute average is
  about 2.2% (1226 errors in 56531 requests), still above 1%. The notes don't have per-interval GET counts, so I
  couldn't check each interval. To check, count GET requests and 503 responses per five-minute interval from the
  request log.
- **Our own five-minute boundaries match Tessary's.** The errors run from 14:05:12 to 14:44:51, so eight intervals
  on either alignment is likely, but not established.
- **The rate argument covers our upload service only.** The counts come from its request log. If other clients of
  ours wrote to these buckets in that window, Tessary will see their traffic too. The 2044-per-interval bound is the
  strongest point in the case, and it holds only for that one service's traffic.

## What I changed for the vendor rule

The rule is "No internal hostnames, internal service names, or credentials in tickets to vendors."

- `ingest-07.lm-prod.internal` in the debug log became `upload-host-1`.
- `mediapipe-uploader` became "our upload service" or "our upload clients". "Pod" became "client" in the list of
  changes we tried.
- The whole Authorization header value is replaced with `<redacted: TESS4-HMAC-SHA256 authorization header>`. That
  removes the signature and the access key ID in its Credential field. If support asks which key made the requests,
  you can give them the key ID without the signature.
- I kept everything Tessary needs to find the requests: the account ID, bucket names, the object key in the logged
  URL, request IDs, host IDs, and the egress addresses.
- I converted all times to UTC and gave CEST once, in the opening sentence.

## What I left out, and why

- **The on-call Slack thread and the Grafana "Uploads Overview" panels.** Tessary can't act on either, and the
  request log already gives the error counts.
- **The previous week's incident.** It was our own deploy, and Tessary has nothing to answer about it. It matters
  only for the uptime figure above.
- **Restart and rollback times in CEST.** I converted them to UTC. The notes give no time for the memory-limit
  change or the DNS cache flush, so the case lists them without times.

## Gaps

- **I didn't run any lookup or command.** The session had no network, and I re-ran nothing from the request log. The
  numbers in the case are the ones in the notes. I computed only the per-interval error rates (503 divided by
  attempts) and the 2.2% GET-inclusive average.
- **There's no AI policy on either side**, so the case doesn't disclose how it was drafted.
