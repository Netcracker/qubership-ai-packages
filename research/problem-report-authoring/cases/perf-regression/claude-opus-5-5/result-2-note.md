# Hand-over note: Ferrygate 4.7.0 p99 latency issue

Nothing has been filed. `draft.md` is the issue body for `git.ferrygate.dev/ferrygate/ferrygate`. It follows the `Performance` template's headings in its order and ends with the template's `/label` line.

## Title

```text
p99 latency 3.3 times higher on 4.7.0 than on 4.6.2 for 1 KiB responses (2.1 ms to 6.9 ms)
```

## Filing

Either pick "Performance" from the "Description" dropdown in the web UI and replace its contents with `draft.md`, or use the CLI:

```bash
glab issue create -R ferrygate/ferrygate \
  --title "p99 latency 3.3 times higher on 4.7.0 than on 4.6.2 for 1 KiB responses (2.1 ms to 6.9 ms)" \
  --description "$(cat out/draft.md)"
```

`glab` needs to point at the `git.ferrygate.dev` host (`GITLAB_HOST` or `glab auth login --hostname`). Check that the `/label` quick action was applied after filing. If it wasn't, add `--label performance --label "needs triage"` or set the labels by hand.

## Gaps to close before filing

1. **Newer builds.** The report says nothing newer than `v4.7.0` was tested. Check whether a release after 4.7.0 exists and whether its release notes mention `worker.io_batch`, the coalescer, or latency. If one exists, rerun the ten-run measurement on it and update Summary and Environment. Running the same bench on `main` would also help.
2. **Start commands.** The notes say the processes were pinned with `taskset` to cores 0-7, 12-15, and 16-23, but they don't record the exact command lines that started Ferrygate and `tools/bench-upstream`. The report describes the pinning in prose and doesn't invent the commands. If your shell history has them, paste them into "How to measure".
3. **Bisect script.** `bench/bisect-p99.sh` is referenced by path. If it's your own script and not in the Ferrygate tree, a reader can't fetch it. Paste its contents under "Bisect", or replace the path with a note that the script is local. The report describes what it does.
4. **perf version.** The `perf` version wasn't recorded. Add it (`perf --version`) if you have it.
5. **Artifacts.** The report offers `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) on request. Keep them until the issue is closed.

## Searches run (issues and merge requests, all states)

Queries: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Hits: !1482 (merged, the bisected change), #2291 (open, memory growth with HTTP/2 upstreams), and #2140 and #1977 (closed, unrelated). The report names #2291 and !1482. The template has no slot for the queries, so they're listed here. Rerun them just before filing in case a matching report appeared after 2026-09-23.

## Left out of the report on purpose

- The company name, the shipper contract ("p99 edge latency under 5 ms, measured monthly"), and the bench hostname are private, and the issue is public. The report says "our edge team" instead. If you want maintainers to see what's at stake, one sentence about a 5 ms p99 target would be enough. Don't name the customer.
- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks showed no difference beyond 1%. They don't help with this issue.
- The production numbers (about 7 ms before the workaround, about 2.4 ms after) come from the edge team's dashboard, and the notes contain no export of them. The report credits them to the edge team. Confirm the numbers with that team before filing.

## Open points for you

- **Remaining gap.** With `io_batch = "off"`, 4.7.0 still runs above 4.6.2's p99 range (2.25–2.33 ms against 2.06–2.23 ms) and about 1.2% below its throughput. The report mentions this and says it wasn't bisected. It could be a second regression elsewhere between the two tags. If you want it reported, bisect it with a threshold near 2.24 ms, setting `io_batch = "off"` on every commit that accepts the key. The release notes call the setting new in 4.7.0, so commits before `3f9c2e7` probably reject or ignore it; check how the parent `a51d07c` handles an unknown `[worker]` key before you start. If the bisect lands outside !1482, file it as a separate linked issue.
- **Talking to the author.** A comment on !1482 or a mention of its author could reach the right person sooner. That MR is merged, so a new issue is still the right place for the report. Whether to add the comment or mention is up to you.
- **AI policy.** `CONTRIBUTING.md` has no AI policy, so the report includes no disclosure. Whether the project welcomes a report drafted with an AI tool is unstated. You'll need to answer follow-up questions about the bench, the bisect, and the profile yourself.
- **Possible cause.** The last section is a guess based on the commit title and the profile. Nobody read `src/io/writer.rs` closely or tested the idea. Remove the section if you'd rather not defend it. The rest of the report doesn't depend on it.
