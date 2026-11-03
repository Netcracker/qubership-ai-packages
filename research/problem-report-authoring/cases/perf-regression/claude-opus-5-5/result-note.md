# Hand-over note: Ferrygate 4.7.0 p99 regression

Nothing has been filed. The issue body is in `draft.md`, next to this file.

## Title

```text
p99 latency of small proxied responses is 3.3 times higher in 4.7.0 than in 4.6.2
```

## How to file

Web UI: on `git.ferrygate.dev/ferrygate/ferrygate`, open a new issue, pick **Performance** from the "Description" dropdown, and replace the pre-filled text with `draft.md`. The headings match the template in order. The last line is the template's `/label` quick action. After filing, check that `~performance` and `~"needs triage"` were applied.

CLI alternative:

```bash
GITLAB_HOST=git.ferrygate.dev glab issue create -R ferrygate/ferrygate \
  --title "p99 latency of small proxied responses is 3.3 times higher in 4.7.0 than in 4.6.2" \
  --description "$(cat draft.md)"
```

## Gaps to close before filing

1. **Newer builds.** The notes say only that 4.7.x and 4.6.x are supported, so I don't know whether a release after 4.7.0 exists or whether the default branch still has this regression. The report says "I have not tested any build newer than 4.7.0." Check the releases page and the changelog for a 4.7.x after 4.7.0 and for any change to `worker.io_batch` or the coalescer. If there is a newer release, rerun the ten-run measurement on it and update the Summary and Environment sections. If it is already fixed, don't file.
2. **Commands that are not in the notes.** The report describes these steps, but nobody wrote down the exact commands: the `taskset` invocations, the command that starts `tools/bench-upstream`, and the warm-up command (presumably `wrk ... -d30s`, but that was never recorded). If you have them, paste them into "How to measure" so a maintainer can copy the setup. I did not make them up.
3. **`bench/bisect-p99.sh`.** The report describes what it does but doesn't include it. If it's your script and not in the Ferrygate repo, paste it into the Bisect section or link it.
4. **Profiles.** The flame graph (40.2 MB) and `perf.data` (1.3 GB) are over the 10 MB attachment limit, so the report offers them on request. A gzipped SVG might fit under 10 MB, but I haven't tried. You could also host it somewhere and link it.

## Decisions for you

- **AI policy.** `CONTRIBUTING.md` doesn't have one, so the project requires no disclosure. It's your call whether to mention that a tool drafted the report, and whether the project would welcome an agent-drafted report at all.
- **Production details.** I removed the company name, the shipper, the contract, and the host name `bench-03`. The report still says "We need to stay under 5 ms" and gives the dashboard figures (about 7 ms after the upgrade, about 2.4 ms with `io_batch = "off"`). If you don't want even that in public, delete the third Summary paragraph and the last Workaround paragraph. The rest of the report doesn't depend on them.
- **The leftover gap with `io_batch = "off"`.** Even with coalescing off, p99 is 2.29 ms against 2.115 ms on 4.6.2, and throughput is 1.2% lower. The ranges don't overlap. I reported this as a measurement in the Workaround section, not as a second expected result. If you want the project to fix it separately, it could become a second issue linked to this one. Without coalescing, though, the commit's other changes in `src/worker/loop.rs` may be the cause, and that was never measured on its own.
- **Contacting the author.** `3f9c2e7` came from !1482 by Tomas Leino, which was merged on 2026-07-16. You could mention them in the issue or link the issue from !1482, but that's up to you.

## Search record

These queries were run on issues and merge requests in all states: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`.

- !1482 (merged): the bisected commit. The report names it as the nearest hit, along with the difference: a 64 KiB benchmark and no latency numbers there, a 1 KiB benchmark here.
- #2291 (open, "4.7.0: memory growth with HTTP/2 upstreams"): a different symptom, not mentioned in the report.
- #2140 and #1977 (closed): unrelated.

Search again just before you file, because a matching issue may have been opened since September 23.

## Left out of the report

- The gzip and config-reload benchmarks (`bench/gzip.sh`, `bench/reload.sh`) showed no difference beyond 1%. They were run for another ticket and support nothing the report claims.
- The exact wording of the shipper contract.
