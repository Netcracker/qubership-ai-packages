# Hand-over note: Ferrygate 4.7.0 p99 regression issue

The issue body is in `draft.md`. Nothing has been filed. This note is not part of the issue.

## Title

Suggested title, following the `4.7.0: ...` style of #2291:

`4.7.0: p99 latency up from 2.1 ms to 6.9 ms for 1 KiB responses with default config`

## Filing

Use the `Performance` template from the "Description" dropdown on `git.ferrygate.dev/ferrygate/ferrygate`. The headings in `draft.md` follow that template in its order, and the `/label` quick action is the last line. To file from the command line instead:

```bash
glab issue create -R ferrygate/ferrygate \
  --title "4.7.0: p99 latency up from 2.1 ms to 6.9 ms for 1 KiB responses with default config" \
  --description "$(cat draft.md)"
```

Run it only after the checks below.

## Gaps to close before filing

Each item is a lookup or a check this session could not make, because it had no network and no checkout.

1. **Newer releases.** Only 4.7.0 was measured. Check the releases page and the changelog for any 4.7.x after 4.7.0 that mentions `io_batch`, coalescing, or latency. If one exists, rerun the ten-run measurement on it and replace the "Not established" line under Environment with the result. If the regression is gone there, don't file. Point the edge team at that release instead.
2. **Tracker search, repeated.** The search ran on September 22 and 23 over issues and merge requests in all states, with these queries: `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`. Rerun them for anything filed since. If an open issue reports the same regression, post the measurements there as a comment instead of filing a new issue.
3. **Exact commands.** The notes record the core pinning but not the exact command lines for starting `tools/bench-upstream` and Ferrygate under `taskset`, or the exact warm-up command. Add those lines to step 1 and step 2 of "How to measure" so a maintainer can paste them. The issue does not invent them.
4. **`bench/bisect-p99.sh`.** If this script is ours and not in the Ferrygate repository, paste it under "Bisect" or link it. The issue references it and nobody upstream can fetch it otherwise.
5. **Workaround runs.** The notes don't say whether the five `io_batch = "off"` runs had a warm-up. If they did, add "after the same warm-up" to the Workaround section. If they didn't, say so.
6. **`perf` version.** It wasn't recorded. Add the output of `perf --version` to the Profiling data section.
7. **Compatibility statement.** The expectation rests on 4.6.2 being a supported release with the old behavior. I couldn't read whether the project says anything about performance in its compatibility or versioning policy. If it does, cite it in the Summary's grounding sentence.
8. **Template pre-fill.** Open the create dialog with the `Performance` template once and confirm that its headings match `draft.md`.

## Decisions that are yours

- **AI policy.** `CONTRIBUTING.md` has no AI policy, so nothing has to be disclosed. Whether the project welcomes a report drafted with a tool isn't stated. You decide that. You should also be able to answer maintainers' follow-up questions about the measurements yourself.
- **What to disclose about Oakridge Freight.** The issue doesn't name the company, the shipper, or the contract. It says only "the 5 ms p99 target we have to meet". Delete that clause if even that is too much. The bench hostname (`bench-03`) is left out.
- **The residual with `io_batch = "off"`.** With `off`, p99 is still about 8% above 4.6.2, and that's from five runs. The issue reports this under Workaround and does not ask for it separately. If you want it pursued, it needs its own ten-run measurement and possibly a separate linked issue.
- **The artifacts.** `perf.data` (1.3 GB) and `flame-470.svg` (40.2 MB) were not attached. Before sharing either on request, check them for host paths, command lines, and anything else internal. Send them only to a maintainer who asks, not as a public link.

## Left out on purpose

- The gzip and config-reload benchmarks (`bench/gzip.sh`, `bench/reload.sh`). They were run for an unrelated ticket and showed no difference beyond 1%. They don't answer anything a maintainer asks about this regression.
- Any claim about the code in `src/io/writer.rs`. Nobody read it closely, so the cause section stays marked as a guess.
