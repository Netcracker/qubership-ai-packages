# Hand-over note (not part of the issue)

Target: `git.ferrygate.dev/ferrygate/ferrygate`, template `Performance.md`. The first line of `draft.md` is the title; the rest is the body, starting at `## Summary`. I filed nothing and had no network access.

## Decide before filing

- **Is this a defect or an intended tradeoff?** The report says it does not know, and asks for the default to be reconsidered or the cost documented. If you would rather ask first, a question or discussion thread may fit better.
- **Comment on !1482 instead?** It introduced the change and has no latency numbers. A new issue seems right, because the regression is visible to users, but that is your call.
- **Can you explain and defend the report without me?** `CONTRIBUTING.md` has no AI policy, so I wrote no disclosure. Add one if you want.
- **Project activity:** I did not check for maintainer replies or for a 4.7.x release after 4.7.0.

## Not established (close these first)

1. **Newer releases.** The "Supported versions" page lists 4.7.x and 4.6.x. I did not check whether a release after 4.7.0 exists or whether `main` still shows the regression. The report says this was not established. If one exists, re-run the ten-run measurement on it and update the Summary.
2. **Duplicate search.** I did not re-run it, so this is from the notes. Queries used: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`, issues and merge requests, all states. Hits: !1482 (named in the report); #2291 (open, memory growth with HTTP/2 upstreams, different symptom); #2140 and #1977 (closed, unrelated). The report names only !1482. Try also `tail latency`, `write batching`, and `epoll`, since a duplicate may be worded differently.
3. **Exact commands for the pinning.** The notes only say Ferrygate, the upstream, and `wrk` were pinned with `taskset` to cores 0-7, 12-15, and 16-23. Paste the real command lines under "Environment", including how `tools/bench-upstream` was started. A reader cannot rerun the setup without them.
4. **`bench/bisect-p99.sh`.** The notes describe it (warm-up, three `wrk` runs, exit 1 if median p99 exceeds 4 ms) but not its source. Check whether it is tracked in the repository. If not, paste it into the Bisect section.
5. **Tracker markup.** I assumed GitLab-flavored Markdown with fenced blocks. Open one filed issue to confirm.
6. **Attachments.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) are over the instance's 10 MB limit. The report offers them on request. If you want to link them, host them somewhere first and check `perf.data` for hostnames or other private data before sharing.

## Choices I made in the draft

- I left out the customer name, the contract wording, and the 5 ms figure. The report is about the benchmark. The production numbers (about 7 ms, about 2.4 ms) appear once, in the Workaround section, attributed to the operating team's dashboard. I have no pre-upgrade production p99, so the report gives none. If you can supply one with the dashboard's name and window, it would strengthen that paragraph.
- I left out the gzip and config-reload benchmarks (no difference beyond 1%). They answer no question a triager asks.
- I put the unverified cause in its own last section, ahead of the `/label` line, because the template has no analysis field.
- The "Expected" paragraph asks for the default to give about the `off` result, because `off` does not return to the 4.6.2 numbers (the Workaround section shows this). That makes the expectation reachable on this benchmark. I did not propose a fix.
- No names were changed or removed. The commit author's name and address are in the pasted bisect output because they are in the public commit.
