# Hand-over note: Ferrygate 4.7.0 p99 regression issue

Nothing has been filed. `draft.md` is the issue body for `git.ferrygate.dev/ferrygate/ferrygate`, written into the headings of `.gitlab/issue_templates/Performance.md` in the template's order. The last line is the template's own `/label` quick action.

## Filing

- Title: `4.7.0: p99 latency 3.3 times higher than 4.6.2 for small proxied responses`
- Web UI: New issue, choose "Performance" in the Description dropdown, then replace the pre-filled text with `draft.md`. If the dialog pre-fills a template that differs from the headings in `draft.md`, the template on the instance has changed since the notes were taken. Re-check the headings before filing.
- CLI alternative:

  ```bash
  GITLAB_HOST=git.ferrygate.dev glab issue create -R ferrygate/ferrygate \
    --title "4.7.0: p99 latency 3.3 times higher than 4.6.2 for small proxied responses" \
    --description "$(cat out/draft.md)"
  ```

## Gaps to close before filing

This session had no network and no checkout. Everything in the draft comes from the session notes of September 22 and 23, 2026.

1. **Newer builds.** The report says it was not tested on anything newer than 4.7.0. Check the releases page for a 4.7.x after 4.7.0, and its changelog for anything about write coalescing or `io_batch`. If a newer release or `main` exists, run the ten-run measurement on it. If the regression is gone there, this becomes a different report or none.
2. **Duplicates.** Re-run the tracker search with all states and include anything filed after September 23. The queries were `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`. If an open issue reports the same thing, comment there with the version, the bisect result, and the tables instead of filing.
3. **`bench/bisect-p99.sh`.** If this script is ours and not in the Ferrygate repository, the issue references a file the maintainers cannot see. Paste its contents into the Bisect section, or drop the path and keep the description.
4. **Start commands.** The notes do not record the exact command lines for `ferrygate`, `tools/bench-upstream`, or the `taskset` invocations. Add them to "How to measure" so a maintainer can repeat the setup exactly.
5. **`perf` version.** Not recorded. Run `perf --version` on the bench machine and add it to Environment.
6. **Profile artifacts.** The flame graph `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) are offered on request, not attached. Before sharing either, check them for internal paths or hostnames.

## Left out on purpose

- The customer contract (p99 under 5 ms, measured monthly), the customer, the company name, and the bench hostname. These are private and the issue tracker is public. The production observation stays, without names.
- The gzip and config-reload benchmarks run the same day (`bench/gzip.sh`, `bench/reload.sh`, no difference beyond 1%). They were run for another ticket and their run conditions were not recorded.
- The small gap that remains with `io_batch = "off"` (p99 2.25–2.33 ms against 2.06–2.23 ms on 4.6.2) is in the Workaround section only as an observation, based on five runs. To raise it as a separate ask, run ten runs first.

## Decisions for you

- `CONTRIBUTING.md` has no AI policy. Whether to say the measurements and the draft were prepared with an AI agent is your call. Before filing, make sure you can explain the numbers and the bisect and answer follow-up questions yourself.
- The bisected commit was authored by Tomas Leino through !1482 (merged). Mentioning them, or linking the issue from !1482, is up to you.
- The "Possible cause (untested)" section is a guess from the commit title and the profile. Nobody read `src/io/writer.rs` or tested it. Delete the section if you'd rather not include it; the report stands without it.
- This is a performance regression and not a security issue, so the public tracker is the right place.
