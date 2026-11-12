# Hand-over note: Ferrygate 4.7.0 p99 regression

The issue body is in `draft.md`. It targets `git.ferrygate.dev/ferrygate/ferrygate`. Choose the `Performance` template from the "Description" dropdown, then replace its contents with the body. The headings and their order match the template. The `/label` quick action is the last line of the body.

**Proposed title:** `4.7.0: p99 latency 3.3 times higher than 4.6.2 when proxying 1 KiB responses`

I did not file anything, and this session had no network access. The gaps and decisions below are yours.

## Decisions for you

- **AI policy.** `CONTRIBUTING.md` has no AI policy, so the body does not disclose that a tool drafted it. Decide whether you want to add a line anyway. Before you file, make sure you can explain the measurements and the bisect yourself and answer follow-up questions without the tool.
- **What is left out on purpose.** The body does not name Oakridge Freight, the shipper contract ("p99 edge latency under 5 ms, measured monthly"), or the hostname `bench-03`, because the tracker is public. The production numbers stay, attributed to "our edge proxies" and "our monitoring dashboard". If even those are too much for a public tracker, delete the last sentence of Summary and the last sentence of Workaround. The benchmark alone still states the problem.
- **!1482.** It is merged, so I wrote a new issue instead of commenting there. You may also want to mention the new issue on !1482 or @-mention its author once it is filed. That is up to you.

## Gaps to close before filing

1. **Re-run the duplicate search.** The search is from 2026-09-23, more than a month ago. Search issues and merge requests in all states with `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`. Last time, the hits were !1482 (the bisected commit, cited in the body), #2291 (open, "4.7.0: memory growth with HTTP/2 upstreams", a different symptom), and #2140 and #1977 (closed, unrelated). If something new matches, comment there instead of filing.
2. **Check for a newer release.** The body says only 4.7.0 was measured. Look at the releases page and the changelog for a 4.7.x newer than 4.7.0, or any change to `worker.io_batch` on the default branch. If a newer patch release exists, repeat the measurement on it before filing: one 30-second warm-up, then ten runs of `wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k`. Then update the version line in Summary.
3. **Bisect script.** The body cites `bench/bisect-p99.sh` and describes what it does. If the script is ours and not in the Ferrygate repository, paste it into the Bisect section as a `bash` block. Otherwise a reader cannot re-run the bisect as written.
4. **Launch commands.** The notes give the core pinning (Ferrygate on 0-7, upstream on 12-15, `wrk` on 16-23) but not the exact `taskset` commands that start Ferrygate and `tools/bench-upstream`. If you have them, add them under How to measure. I did not invent them.
5. **Template and markup check.** I worked from the recorded headings of `.gitlab/issue_templates/Performance.md`. Open the create dialog and confirm the template still has the same headings, that no project or group default template adds anything, and that the attachment limit is still 10 MB.
6. **Security.** Nothing here suggests a vulnerability, and I did not read `SECURITY.md`. No action is needed unless you know otherwise.

## Left out of the body

- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks showed no difference above 1% between versions. They were run for an unrelated ticket and answer nothing a triager would ask here.
- The workaround runs on 4.7.0 had no warm-up recorded in the notes, so the body does not claim one.
- The 4.6.2 `perf report` output was not saved in the notes. The body states only that it has no `Coalescer` frame. If you have that output, it can go under Profiling data.
- The flame graph `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) are offered on request rather than attached. Strip any hostnames or paths from them before sharing.
