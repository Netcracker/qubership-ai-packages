# Hand-over note: Tessary support case

Nothing has been filed or sent. `draft.md` holds the field values for the portal's "New case" form.

## Decide before filing

1. **The SLA credit window has probably passed.** SLA section 6 requires a ticket within 30 days of the incident. The incident was 2026-09-21, so the window closed on 2026-10-21, and today is 2026-10-31. If anyone already contacted Tessary about this before 2026-10-21, say so in the case and cite that contact. If not, the last sentence of question 4 in "What do you need from us?" is mine: it states the lateness and asks for an exception. Keep it, reword it, or remove it. Whether to pursue a credit that is likely time-barred is Finance's and your call. Questions 1 to 3 do not depend on it.
2. **File soon.** I don't know how long Tessary keeps request-level records, and the incident is already six weeks old.
3. **Severity S3** follows the form's definition (mitigated; root cause, credit, or information needed). S1 and S2 do not apply, since the workload is not impaired now.

## Gaps the case does not claim to have closed

- Status page: the notes record checks at 14:12 and 14:31 UTC on 2026-09-21 and a history read on 2026-09-22. The case says it was not re-read since. Re-read the history and the known-issues page before filing, and add any incident for 2026-09-21 that now appears. I don't know who made the two checks on the day; the case says "we".
- Start of the incident: the notes give the first SlowDown at 14:05:12.448Z but no data from before 14:05. Confirm the log shows normal traffic with no errors just before 14:05. If it does not, the "started" time in the case is only the first error in our log.
- Other clients: the counts come from one application's log. I don't know whether anything else wrote to the account or these prefixes. The case says our log can't show that.
- SDK retries: not established whether the SDK retries a 503 by default, and the case doesn't say. The case says only that the uploader had no retry of its own on this path until 14:25.
- SLA arithmetic: 8 of 8640 intervals gives 99.907%, which is above 99.9%, so by section 5 it would be the 10% tier, not 25%. This counts only this incident, assumes UTC-aligned five-minute intervals, and assumes Error Rate is measured on our traffic. The case asks Tessary to compute it. Finance should not budget the figure.
- The cause: nothing in the notes shows why Tessary returned SlowDown. The case does not guess. The "partition being scaled" condition on the rate page is cited only as something we cannot see.

## Redaction

I left out of the case: the uploader's and the host's names, the thumbnail-service name (it appears as "another internal service"), the Slack thread, the Grafana dashboard, and the access key ID and signature in the debug log. The internal host name and the Authorization line in the log excerpt are marked as redacted in the case; the rest of the excerpt is verbatim. Bucket names, account ID, request and host IDs, and egress addresses stay because Tessary finds the requests by them. The case offers the access key ID privately if Tessary asks.

I did not open `slowdown-requests-2026-09-21.csv`. Before attaching, check that it has 1217 rows, that the object keys are UUIDs only, and that no column holds an internal name. The 25 MB limit is no issue at 118 KB.

## Other details to check

- Times are converted from CEST (UTC+2): the pod restart at 16:14 CEST is 14:14 UTC, and the rollback at 16:18 CEST is 14:18 UTC. The notes give no times for the memory-limit change or the DNS flush, so the case gives none.
- Exact names in the Service and Region dropdowns: I used "Object Storage" (the status page's wording) and "eu-north-2".
- The subject is under 120 characters. The description is plain text and well under 10000 characters; the indented blocks stand in for tables.
- Neither side has an AI policy, so the case carries no disclosure.
