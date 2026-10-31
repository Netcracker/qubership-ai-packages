# Hand-over note for the person filing

Not part of the issue. Nothing has been filed or sent.

## Title

`p99 latency 3.3x higher on 4.7.0 than on 4.6.2 with default worker.io_batch`

The template has no prefix convention in my notes; add one if recent issues use it. Select the Performance template in the "Description" dropdown. The body in `draft.md` already uses its headings and ends with the `/label` line. If you file with `glab`, something like:

```bash
glab issue create -R ferrygate/ferrygate --title "p99 latency 3.3x higher on 4.7.0 than on 4.6.2 with default worker.io_batch" --description "$(cat draft.md)"
```

Check that the quick action line on the last line is applied, as I could not confirm that `glab` processes it.

## Open questions for you

- Can you explain and defend the numbers without me? The project has no AI policy in `CONTRIBUTING.md`, so the draft carries no disclosure. Look again at the live page and the template in case that changed.
- Do you want the production figures in the issue? The draft says "a production deployment" and leaves out the company and the contract. The 7 ms figure and the roughly 2.4 ms after `io_batch = "off"` are from the edge team's dashboard. I did not see them, and the draft attributes them to the owners. Remove the paragraph if you do not want it public.
- Would a comment on !1482 serve better than a new issue? I think a new issue does, as !1482 is merged and the report concerns 4.7.0, but it is your call.

## Not established (the report says so where a triager would ask)

- Newer versions: I tested only 4.7.0. Please run the same measurement on the newest 4.7.x release and on the development branch, if any exists. The report currently states this gap.
- Launch commands: my notes say only that Ferrygate, the upstream, and `wrk` ran under `taskset` on the stated cores. The exact `ferrygate` and `bench-upstream` command lines were not recorded. Add them to "How to measure" so the reproducer is complete.
- Bisect: I have not re-run `bench/bisect-p99.sh` after drafting. The table and medians were recomputed from the raw per-run numbers and agree.
- Production figures: not mine, as above.

## Lookups I could not make

- The live issue template, `CONTRIBUTING.md`, the supported versions page, and `SECURITY.md` at `git.ferrygate.dev/ferrygate/ferrygate`. The headings come from my session notes. Compare them with `.gitlab/issue_templates/Performance.md`, and check whether the project asks for one problem per issue (the draft has one problem).
- The tracker search was done in the session, so rerun it for anything filed since: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`, issues and merge requests, all states. It found !1482 (the bisected change), #2291 (open, memory growth with HTTP/2 upstreams), and #2140 and #1977 (closed, unrelated). The template has no search field, so the draft names only the nearest hit in the last section.
- How a code block renders in a GitLab issue was not checked against an existing issue. GitLab Markdown normally renders fences.

## Left out on purpose

- The company name, the shipper contract, and the bench hostname. The tracker is public.
- The gzip and config-reload benchmarks (`bench/gzip.sh`, `bench/reload.sh`) showed under 1% difference between the versions. They answer nobody's question here. Add them if a maintainer asks what else was checked.
- The flame graph (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB), which exceed the 10 MB attachment limit. The draft offers them on request. Decide where they could be hosted if someone asks, and note that they may hold process memory addresses and host details; review them before sharing.
- A proposed fix. The cause in the draft is marked as a guess, and the report does not depend on it.
