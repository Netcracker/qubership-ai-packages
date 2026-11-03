# Hand-over note for the person filing (not part of the case)

Nothing has been filed or sent. I had no network or portal access, so every quotation from Tessary's pages comes from the session notes, not from a fresh read.

## Decide before filing

1. **The SLA claim window may have closed.** SLA section 6 (as quoted in the notes) requires a ticket within 30 days of the incident. The incident was on 2026-09-21, so the window ended on 2026-10-21. This session's date is 2026-10-31. If no earlier ticket exists (the notes say nothing was written up), a case opened now is about 10 days late. Check whether anything was sent to Tessary or an account manager after the incident. If not, decide whether to ask for the credit anyway. The draft does ask for it and asks Tessary to treat the case as the section 6 notice (ask 4 and the last sentence of the description). It does not claim the case is in time. Cut or reword that sentence if you prefer to ask first whether a late claim is possible.
2. **Severity S3.** The workload recovered and the backoff mitigates it, and you want a root cause and a credit, which matches the form's S3 definition. S2 and S1 do not apply.
3. **Who sends it.** The portal shows the case to Tessary support and engineering. I kept the account ID, bucket names, request and host IDs, and the two egress addresses, because Tessary finds the requests by them.

## Check before filing

- **Redactions.** Your rule says no internal hostnames, internal service names, or credentials. I removed the uploader host name from the debug line, the uploader's service name everywhere, and the access key ID and signature from the Authorization header. Tessary can find the request by request ID. If they ask for the key ID, give it in the case.
- **The CSV.** I did not see `slowdown-requests-2026-09-21.csv`. Confirm it has 1217 rows, that the five sample requests are in it, and that no column carries an internal host name or anything else beyond timestamp, bucket, object key, request ID, and host ID.
- **Pages may have changed since 2026-09-22.** Reread the status page history, any known-issues page, the request-rates page, and the SLA as they stood on 2026-09-21. A post-incident entry may exist now and answer ask 1.

## Gaps that Tessary may raise

- **Load before and after.** The notes have no PUT counts before 14:05. The 75 minutes after the window average about 2.6 PUT/s (11860 in 4500 s), against 6.4 PUT/s during it. The draft gives the counts and draws no conclusion. Pull 13:00 to 14:05 UTC from the request log so you can answer a question about load.
- **Other writers.** The draft says "from us" about the rate. The notes do not say that no other client or egress address writes to those buckets or prefixes. Confirm that, because "far below the documented rate" holds for the account only if nothing else writes.
- **SLA arithmetic.** It uses PUT counts only and assumes five-minute intervals aligned to the clock. The notes lack per-interval GET counts. If Tessary counts all requests, the ratio is lower than 7.8% to 8.1%. From the 40-minute totals I estimate about 2% per interval, still above 1%, but verify with the per-interval GET numbers. The 99.907% figure also assumes no other unavailable interval in September, and Tessary measures its own Error Rate.
- **Credit tier.** 99.907% is above 99.9%, so by the quoted section 5 the tier is 10%, not 25%.

## Left out on purpose

- The on-call Slack thread (internal names, a link to a different incident) and the Grafana dashboard (no Tessary-side information).
- The memory-limit change and the rollback of an unrelated deploy. They changed nothing, and naming the other service would disclose an internal name.
- Times in CEST, except one conversion in the first paragraph. All other times are UTC; I converted the CEST times in the notes (for example, the pod restart at 16:14 CEST is 14:14 UTC).
- No AI policy applies on either side, so the case carries no disclosure.
