# Hand-over note: Ferrygate 4.7.0 p99 regression

Nothing has been filed. `draft.md` is the issue body. It follows the headings of `.gitlab/issue_templates/Performance.md` in order and ends with the template's `/label` line.

## Filing

Title:

```text
p99 latency for 1 KiB responses rose from 2.1 ms in 4.6.2 to 6.9 ms in 4.7.0
```

Command, if you file from the CLI instead of the web form with the "Performance" template:

```bash
GITLAB_HOST=git.ferrygate.dev glab issue create -R ferrygate/ferrygate \
  --title "p99 latency for 1 KiB responses rose from 2.1 ms in 4.6.2 to 6.9 ms in 4.7.0" \
  --description "$(cat draft.md)"
```

## Decisions for you

- **Disclosure.** `CONTRIBUTING.md` has no AI policy, so the project asks for nothing. Decide whether you want to say the measurements and the draft came from an agent session. Either way, you have to be able to answer follow-up questions about the bench setup and the bisect yourself.
- **Comment on !1482 as well?** The MR is merged, so a new issue is the right vehicle. You might still mention the issue on !1482 or to its author so the person who knows the coalescer sees it. That's your call.
- **The residual gap with `io_batch = "off"`.** Median p99 is 2.29 ms with `off`, compared with 2.115 ms on 4.6.2, and throughput is 1.2% lower. The draft reports this only as a measurement in the Workaround section. It doesn't ask for a fix, because nothing shows it is a separate defect. If it matters to you, it could become a second, linked issue after more runs.

## Gaps to close before filing

Each item below is stated in the report as not established, or left out of it.

1. **Newer versions.** Only 4.7.0 was tested. Check the releases page for a later 4.7.x and the changelog for anything touching `worker.io_batch` or the coalescer. If there is one, rerun the ten-run measurement on it and update the Summary line "Tested on 4.7.0 only". `main` is untested too.
2. **`bench/bisect-p99.sh`.** The notes don't say whether this script is in the Ferrygate repository or is ours. If it's ours, paste it into the Bisect section, because a reader needs it to repeat the bisect.
3. **Start commands.** The template's "How to measure" asks for the exact command. The report gives the `wrk` command, the core pinning, and the warm-up length. It doesn't give the exact `taskset … ferrygate …` and `taskset … bench-upstream …` command lines or the warm-up `wrk` invocation, because the notes don't record them. Add them from the shell history on the bench machine.
4. **`perf` version.** It wasn't recorded. Run `perf --version` on the bench machine and add it to Environment if you want the profile to be repeatable.
5. **Template pre-fill and markup.** Neither was checked in the live create dialog. Open the dialog, select "Performance", and confirm that its headings still match. Look at one existing issue to confirm the code fences render.
6. **Duplicate search.** This was done in the session across issues and merge requests in all states. Queries: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Hits: !1482 (the bisected MR), #2291 (open, different symptom), #2140 and #1977 (closed, unrelated). Rerun the queries just before filing in case something new has appeared.
7. **Profiling artifacts.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) are offered on request because they're over the 10 MB attachment limit. Decide where you would host them if a maintainer asks. Read `perf.data` for anything you wouldn't share first, such as paths and command lines.

## Deliberately left out of the report

- Oakridge Freight's name, the shipper contract, and its 5 ms p99 clause. These are business details on a public tracker, and the observed production numbers already show the impact.
- The bench host name `bench-03`.
- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks. They were run for another ticket and showed no difference beyond 1%, so they answer no question this report raises.
