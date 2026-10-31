# Hand-over note: Ferrygate 4.7.0 p99 regression report

Nothing has been filed. `draft.md` is the issue body for `git.ferrygate.dev/ferrygate/ferrygate`, written into the headings of `.gitlab/issue_templates/Performance.md` in their order, with the template's `/label` line at the end. I wrote it offline from the session notes, so the lookups and checks below are still open.

## Title

```text
4.7.0: p99 latency for 1 KiB responses is about 3 times that of 4.6.2 with the default worker.io_batch
```

## Filing

In the web UI, pick "Performance" from the "Description" dropdown, then replace the pre-filled text with `draft.md`. Or, from a shell:

```bash
GITLAB_HOST=git.ferrygate.dev glab issue create -R ferrygate/ferrygate \
  --title '4.7.0: p99 latency for 1 KiB responses is about 3 times that of 4.6.2 with the default worker.io_batch' \
  --description "$(cat out/draft.md)"
```

The `/label` quick action in the body applies `~performance` and `~"needs triage"` either way.

## To fill in or check before filing

- **Start commands.** The report gives the core pinning in prose but not the commands that started Ferrygate and `bench-upstream`; the notes do not record them, and I did not invent them. Add them, with their `taskset` prefixes, under How to measure.
- **`bench/bisect-p99.sh`.** If this script is not in the Ferrygate tree, the reader cannot rerun the bisect. Paste it into the Bisect section, or attach it.
- **Newer releases.** I could not check whether a 4.7.x release after 4.7.0 exists, or whether its changelog touches `worker.io_batch` or the coalescer. Check the releases page and `CHANGELOG.md`. If a newer 4.7.x exists, rerun the ten runs on it before filing, and update the "Not tested on any later 4.7.x release" line in Environment.
- **Duplicate search.** The notes record this search from the session. Rerun it just before filing, on issues and merge requests in all states: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. The session found !1482 (merged, the bisected change), #2291 (open, different symptom), and #2140 and #1977 (closed, unrelated). If an open issue about this regression has appeared since then, add your numbers to it as a comment instead.
- **Markup.** I could not open an existing issue on the instance. The template is Markdown, so the fenced blocks and tables should render, but look at the preview.
- **perf version.** The report gives no version for `perf`. It is optional data, but you can add it (`perf --version`).

## Open items the report states but does not resolve

- **The remainder with `io_batch = "off"`.** Five runs give a median p99 of 2.29 ms, still above every 4.6.2 run. That is five runs against ten for the two versions. Rerunning ten runs with `off` would make the comparison even. Bisecting that remainder may also be worth it; this is not a plain rerun, because the setting first appears in `3f9c2e71` and earlier commits may reject the key. If the remainder turns out to come from a different commit, it may deserve a linked issue of its own.
- **The cause section is a guess.** It is marked as unverified in the report. Delete it if you would rather not defend it in the thread.

## Removed from the report, on purpose

- The company name, the shipper contract and its "p99 edge latency under 5 ms" clause, and the bench hostname `bench-03`. The tracker is public, and none of these helps the maintainers. The production numbers stay, credited to "our edge team's dashboard".
- The gzip and config-reload benchmarks (`bench/gzip.sh`, `bench/reload.sh`). They were run for another ticket and support no claim here.
- The search queries. The report names the nearest hit, and the queries are listed above.

## Profiling artifacts

The report offers `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) on request, since both are over the 10 MB attachment limit. Before you share `perf.data`, check what it contains: perf recordings include the hostname, the kernel build, and the command lines of the processes recorded.

## Decisions for you

- `CONTRIBUTING.md` has no AI policy. Decide whether to say that the report was drafted with a tool. The project does not ask for it.
- Make sure you can explain and defend the numbers and the bisect in the thread yourself.
- After filing, you could link the issue from !1482 so its author sees it. That is optional, because a comment on a merged MR is easy to miss.
