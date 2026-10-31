# Hand-over note: Ferrygate 4.7.0 p99 regression

## Filing

- Project: `git.ferrygate.dev/ferrygate/ferrygate`, template `Performance.md` from the "Description" dropdown. `draft.md` follows its headings in order and ends with the template's `/label` line.
- Title: `p99 latency 3.3 times higher in 4.7.0 than in 4.6.2 when proxying 1 KiB responses`
- From the web UI, pick the Performance template and replace its text with `draft.md`. From the CLI:

  ```bash
  GITLAB_HOST=git.ferrygate.dev glab issue create -R ferrygate/ferrygate \
    --title "p99 latency 3.3 times higher in 4.7.0 than in 4.6.2 when proxying 1 KiB responses" \
    --description "$(cat draft.md)"
  ```

  Afterward, check that the `performance` and `needs triage` labels were applied.

## Questions for you before filing

- `CONTRIBUTING.md` has no AI policy. Whether the project accepts a report drafted with an agent is not stated anywhere I could read. Decide whether to file as is or mention it. If maintainers ask follow-up questions, you'll need to be able to answer them yourself.
- !1482 is merged, so a new issue fits better than a comment there. Whether to also @-mention the commit author (Tomas Leino) is your call.

## Gaps and how to close them

- **Newer releases and main not tested.** The report says so under Environment. Check the project's releases for anything after 4.7.0 and re-run the ten-run measurement on the newest 4.7.x and on the default branch. If either is already fixed, update the report or don't file it.
- **`bench/bisect-p99.sh`.** The notes don't say whether this script is in the Ferrygate repository or is ours. If it's ours, attach it, or paste it into the Bisect section. As written, the report describes what it does, but a reader can't fetch it.
- **Exact launch commands.** The notes give the core sets (`taskset` 0-7, 12-15, 16-23) but not the full command lines for `ferrygate` and `tools/bench-upstream`, or the exact warm-up `wrk` command. I described the pinning in prose and didn't invent commands. If you have the real lines, add them under "How to measure".
- **Pre-upgrade production p99.** The notes give about 7 ms after the upgrade and about 2.4 ms after `io_batch = "off"`, but no pre-upgrade figure. If the dashboard has one, it's worth one clause in the Summary.
- **The remaining gap with `io_batch = "off"`** (p99 2.29 ms against 2.115 ms, throughput 1.2% lower) hasn't been investigated, and the report says so. To look for it, bisect between v4.6.2 and v4.7.0 with a p99 threshold around 2.2 ms. Set `io_batch = "off"` only on commits from 3f9c2e71 on, because older builds don't know the key. At a difference this small, three runs per step are likely too noisy; use ten.
- **Cause.** The "Possible cause" section is marked as a guess. To test it, read `Coalescer::flush_tick` in `src/io/writer.rs` at 3f9c2e71.
- **Profile artifacts.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) are over the 10 MB attachment limit. The report offers them on request, so have a place ready to share them.
- **Markup.** I didn't open an existing issue on the instance. The template is Markdown, and GitLab renders fenced blocks and tables, so this should render as written. Check the preview before submitting.

## Searches already run (issues and MRs, all states)

`latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Hits: !1482 (the bisected commit, cited in the report), #2291 (open, memory growth with HTTP/2 upstreams, cited as a different symptom), and #2140 and #1977 (closed, unrelated, left out). Rerun these just before filing in case something new has appeared.

## Left out on purpose

- The organization name, the shipper contract, and its 5 ms p99 target. These are private business details on a public tracker, and the production numbers already show the impact.
- The bench host's name (`bench-03`). It's an internal hostname and doesn't affect the result.
- The gzip and config-reload benchmarks (`bench/gzip.sh`, `bench/reload.sh`) showed no difference beyond 1%. They were run for another ticket and don't help explain this regression.
