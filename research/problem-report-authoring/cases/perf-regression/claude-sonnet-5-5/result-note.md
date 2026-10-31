# Hand-over note for the person filing

Nothing was filed or sent. `draft.md` is the issue body for `git.ferrygate.dev/ferrygate/ferrygate`, written into the headings of `.gitlab/issue_templates/Performance.md`, in the template's order. The title is the first line of the draft; move it into the title field and delete the line. The last line is the template's label command. I had no network, so I took the template headings and the supported-versions page from my notes and read neither again.

## Fill in or confirm before filing

1. **Launch commands.** My notes do not have the exact `taskset` lines or the commands that started Ferrygate and `tools/bench-upstream`. "How to measure" says so. Replace that sentence with the real commands if you have them, because the template requires the exact command.
2. **`bench/bisect-p99.sh`.** My notes do not say whether the script is committed upstream or is local to our bench machine. If it is local, paste it into the issue or link it. The Bisect section does not reproduce without it.
3. **Ferrygate 4.7.0 is the newest release I know of.** I did not check whether a later 4.7.x exists, or whether the development branch still shows the regression. Both would answer a triager's first question. Run the same ten-run measurement on the newest 4.7.x if there is one.
4. **Tracker search.** Run it again if it is more than a few days old, since it may be stale. The queries were `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`, over issues and merge requests in all states. Hits: !1482 (the bisected change), #2291 (open, different symptom), and #2140 and #1977 (closed, unrelated). The template has no slot for the queries, so the draft names only the nearest hit and the difference. If a search finds a duplicate, comment on it instead of filing.
5. **Measurement conditions.** Production numbers (about 7 ms after the upgrade, about 2.4 ms after `io_batch = "off"`) come from the edge team's dashboard. The draft attributes them to the operators and says I have not seen the dashboard. Confirm with them that they are fine to share.
6. **Attachments.** The flame graph (40.2 MB) and `perf.data` (1.3 GB) are over the 10 MB limit. The draft offers them "through another route on request". Decide what that route is, such as a private share link, and note that `perf.data` can contain process memory addresses and host details, so check it before you hand it over.

## Left out on purpose

- **Customer and contract.** The draft does not name Oakridge Freight, its largest shipper, or the "p99 under 5 ms, measured monthly" contract term. The channel is a public tracker. The measured numbers carry the report. Add the target if you want to show business impact, and clear it with the customer first.
- **Host name.** The draft does not name `bench-03`. It says that host and operator names are omitted.
- **Gzip and reload benchmarks.** I ran `bench/gzip.sh` and `bench/reload.sh` on both versions for another ticket and saw no difference above 1%. I have no transcript in these notes, so I left the result out. Add one sentence to the Results section if you re-run them.
- **Fix proposals.** The draft proposes no change to the coalescer. The expected block gives a requirement, with a 4 ms threshold taken from my bisect script, and leaves the tolerance and the mechanism to the project.

## Open questions for you

- The project's guide has no AI policy, so the draft carries no disclosure. Whether to say the draft was written with a tool is your call. You should be able to explain and defend the numbers yourself in the thread.
- The "Possible cause" section is a guess from the commit title and the profile. Keep it only if you are happy to have it in the thread. The report reads the same without it.
- The upgrade date (2026-09-15), the rollout date of `io_batch = "off"` (2026-09-22), and the bench dates (2026-09-22 and 2026-09-23) come from my notes. I did not check them against the dashboard.
