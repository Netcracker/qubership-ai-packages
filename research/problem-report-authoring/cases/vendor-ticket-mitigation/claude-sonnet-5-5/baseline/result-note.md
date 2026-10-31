# Hand-over note: Tessary case for the 2026-09-21 SlowDown burst

Nothing is filed. `draft.md` holds the field values in the portal's order. The Description and "What do you need from us?" are plain text.

## Decide before filing

1. **The SLA window has passed.** SLA section 6 asks for a ticket within 30 days of the incident, so by 2026-10-21. Today is 2026-10-31. The draft says so in the Description and asks in item 4 whether the credit can still be applied. Expect Tessary to refuse the credit on timing alone. The root cause, timeline, and throttling questions (items 1 and 2) do not depend on it. Tell Finance before filing.
2. **Was there earlier contact with Tessary?** If anyone opened a case, sent an email, or used a chat about this on or soon after 2026-09-21, cite it in the Description. It could satisfy section 6. The notes show none.
3. **File soon.** Tessary may no longer hold detailed logs for 2026-09-21. The request IDs are the best chance of a lookup.
4. **The credit tier is 10%, not 25%.** 99.907% is below 99.99% and above 99.9%. The 25% tier needs a Monthly Uptime Percentage below 99.9%.
5. **Voice.** The draft says "we" for Lindqvist Media. Neither side has an AI policy, so there is no disclosure to make. Read it as the sender, since the portal shows the case to Tessary support and engineering.

## Not established, with what would close it

- **Whether 503s began before 14:05:12Z.** The notes give the first SlowDown but no counts before that time. The draft claims nothing about it. Count PUT attempts and 503 responses per five-minute interval in the uploader request log for 13:30-14:05 UTC, then add a sentence if any appear.
- **Known issues and other cases.** The draft says they were not searched. Check Tessary's known-issues list, if one exists, and the portal's case list for eu-north-2 around 2026-09-21. Edit that sentence to match.
- **Status page history.** It was read on 2026-09-22 at 09:00 UTC. Re-read the history for 2026-09-21 before filing. If an incident was added later, change that paragraph and item 1.
- **SLA and request-rate wording.** The quotes come from the notes, and the notes do not say when they were read. Compare them with the live pages and update the quotes if they changed.
- **The CSV.** The notes describe the columns (timestamp, bucket, object key, request ID, host ID) and say the keys are UUIDs, and nobody opened the file for this draft. Check that it holds no other data, that the timestamps are UTC, and that it has 1217 rows.
- **Error Rate scope.** The quoted SLA text does not say whether Tessary computes it per account, per bucket, or region-wide. The draft leaves the calculation to Tessary. The 2.17% across PUT and GET is a window average, because per-interval GET counts are not in the notes.
- **SDK support.** Whether Java SDK 2.14.3 is a supported version was not checked. The failure is a server response, so it matters little here, but support may ask.

## What was left out or changed

- Removed: the uploader hostname, the service name of the uploader, the name of the unrelated service whose deploy was rolled back, and the access key ID and signature in the Authorization header. The log line is labeled as redacted in place. If Tessary asks for the access key ID, send it through the portal's private channel.
- Left out as not relevant to Tessary: the on-call Slack thread, the Grafana dashboard, and the previous week's incident.
- Kept on purpose: the account ID, bucket names, request and host IDs, and the two egress addresses, since Tessary finds the requests by them. The addresses are public, but confirm they fall within the vendor-communication rule.
- Times are in UTC. The notes' CEST times are two hours ahead, and the draft uses 14:14 and 14:18 for the pod restart and the rollback.

## Form values

- Severity S3 follows the form's own definition, since the workload is mitigated and the ask is a root cause and a credit.
- The Service dropdown label "Object Storage" is taken from the status page. Pick the closest entry if the dropdown differs.
- The Subject is 91 characters, and the Description is well under the 10000-character limit.
