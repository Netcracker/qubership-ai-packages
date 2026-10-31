# Hand-over note: Tessary support case, 2026-09-21 SlowDown burst

Nothing has been filed. The case is in `draft.md`, with the field values (Severity, Service, Region, Subject, Attachments), the Description, and the "What do you need from us?" text. The portal renders plain text, so the draft has no Markdown.

## Decide before filing

1. **The SLA section 6 window has closed.** Section 6 asks for a ticket within 30 days of the incident. The incident was on 2026-09-21, so the window ended on 2026-10-21, and today (2026-10-31) is 10 days past it. The draft says this in one sentence and asks Tessary whether it will accept the case. Please check with Finance whether an earlier case or a billing contact already covers this, and whether to file anyway. The root-cause and throttling questions do not depend on the window, so I did not drop them.
2. **The credit is probably the lower tier.** The 99.907% figure is above 99.9%, so SLA section 5 gives the 10% tier (below 99.99%), not the 25% tier. The draft does not name a tier and asks Tessary to compute it. Tell Finance not to expect 25%.
3. **The 99.907% depends on how Tessary measures Error Rate.** I counted only our PUT attempts (eight intervals at 7.8% to 8.1%). If Tessary measures over all requests in the region or the account, the figure could differ. Our GETs would dilute it, since there were about 41210 over 40 minutes. At that average the share is still about 2% per interval, but I have no per-interval GET counts, so I left this out of the case.
4. **Possible SLA exclusion.** Section 3 excludes 503 responses "caused by exceeding the documented request rates". Our 6.4 PUT/s against 3,500 per prefix argues against it. The request-rate page also says 503 appears "while a partition is being scaled", which Tessary may call an exclusion. Question 1 in the case asks about that directly.

## Not established (gaps)

- **Status page.** The history was read on 2026-09-22. Re-read https://status.tessary.cloud for 2026-09-21 before filing. If an incident now appears, change the "What Tessary publishes" bullet and drop question 1's premise. I did not check a known-issues page, and I did not search for one.
- **Dropdown entries.** I do not know the exact names in the Service and Region dropdowns. Pick the entries for Object Storage and eu-north-2.
- **Which egress address sent the failures.** The notes give both addresses for the cluster but not whether both saw 503s. The case lists both as the sender and does not claim more.
- **Tessary's log retention.** I do not know how long Tessary keeps request logs. Filing sooner is better for question 1.

## Left out of the case on purpose

- **Internal names.** The portal is visible outside Lindqvist Media, and the vendor rule bans internal hostnames, service names, and credentials. I removed the uploader host name and service name, the access key ID, and the request signature from the debug line, and marked them as redacted. Bucket names, the account ID, egress addresses, request IDs, and host IDs stay, because Tessary finds the requests by them.
- **The Slack thread and the Grafana dashboard.** They answer none of Tessary's questions and name internal systems. The previous week's bad-deploy incident is also left out.
- **Attachment check.** I have not seen `slowdown-requests-2026-09-21.csv`. Before attaching, open it and confirm it holds only the five columns (timestamp, bucket, object key, request ID, host ID) and no internal host names. The keys are UUIDs, so I left them in.

## Things I chose

- **Severity S3,** because the errors stopped and the ask is a root cause, a credit, and information. S1 and S2 need an ongoing impairment.
- **UTC throughout.** The on-call notes use CEST (UTC+2), and the draft shows both only once, in the first paragraph.
- **Token and number style.** Digits are unseparated, except inside the quoted documentation text.
- **No AI policy** on either side, so the draft carries no disclosure.
