# Hand-over note: Ferrygate 4.7.0 p99 regression issue

Title: `4.7.0: p99 latency 3.3x higher than 4.6.2 for 1 KiB responses (bisected to !1482)`

Target: `git.ferrygate.dev/ferrygate/ferrygate`, new issue, template "Performance" from the Description dropdown. Paste `result.md` as the body; it follows the template's headings in order and keeps its `/label` line last. Nothing was filed, and no network lookup was made while drafting.

## Check before filing

1. **Newer releases.** The draft says no 4.7.x after 4.7.0 and no default-branch build was measured. Check the tags or releases page for 4.7.1 or later and the release notes for anything touching `io_batch` or write coalescing. If a newer 4.7.x exists, rerun the ten-run measurement on it (and ideally on the default branch) and replace the "Not established" line with the result. If it is fixed there, do not file.
2. **Duplicate search.** Queries run on 2026-09-23, issues and merge requests, all states: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Rerun them right before filing; anything newer than !1482 and #2291 changes the report, and an open issue for the same symptom should get this data as a comment instead.
3. **Comment on !1482 instead or in addition?** The bisected MR is merged, so a new issue is the normal route, but you may also want to mention the issue on !1482 so its author sees it. Your call.
4. **`bench/bisect-p99.sh`.** The draft cites it by path. If it is your script rather than one in the Ferrygate repo, attach it or paste it into the Bisect section, since a reader cannot rerun the bisect without it.
5. **Start commands.** The report gives core ranges and addresses but not the exact `taskset` command lines for Ferrygate and `tools/bench-upstream`. If you have them, add them under "How to measure"; do not reconstruct them from memory.
6. **Private details.** The draft leaves out the company name, the shipper contract, and the bench host name (`bench-03`). It keeps the 5 ms p99 target as a plain statement. Remove that clause if you do not want it public.
7. **Artifacts.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) exceed the instance's 10 MB attachment limit, so the draft offers them on request. Decide where you would host them if asked.
8. **Authorship.** `CONTRIBUTING.md` has no AI policy, so nothing is required. Whether to mention that a tool drafted the text is up to you. Be ready to answer follow-up questions about the measurements yourself.

## Left out on purpose

- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks showed no difference beyond 1% between the versions. They say nothing about this regression, so the report leaves them out. Add a line if a maintainer asks which other paths were checked.
- Closed issues #2140 and #1977 came up in the search and are unrelated.
