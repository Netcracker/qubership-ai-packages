# Hand-over note for the person filing

Nothing was filed or run. Every number is copied from the session notes. I recomputed the medians, ranges, the 3.3x ratio, and the 8.5% throughput drop from the tables, and they match.

## Title

`p99 latency 3.3x higher in 4.7.0 than in 4.6.2 for 1 KiB proxied responses with the default config`

File it in `git.ferrygate.dev/ferrygate/ferrygate` with the `Performance.md` template. The body keeps its headings in order. I added the "Possible cause" section after the last template field and before the `/label` line, which stays last.

## Fill in before filing

- **Launch commands.** The draft has a `<TBD: ...>` line under "How to measure". My notes give the core pinning and the `wrk` command, but not the command lines that start Ferrygate and `tools/bench-upstream` under `taskset`. The template requires the exact command, so paste them and delete the placeholder.
- **`bench/bisect-p99.sh`.** I could not tell whether it is in the project's tree or only on your machine. If it is local, paste its content into the Bisect section, because a reader cannot rerun the bisect without it.
- **Tarball checksums.** The report names the release tarballs only. Add `sha256sum` output if you want the builds pinned beyond the release number.

## Not established (the report says so where it matters)

- **Later 4.7.x patch releases and the development branch.** The report states that they were not tested. To close it, install the newest 4.7.x listed on the "Supported versions" page and run the same ten-run measurement. If it is fixed there, the report becomes a version-check question first.
- **Whether the project's compatibility promise covers latency.** I grounded the expectation in 4.6.2 behavior and in the release notes only. If the docs make a performance promise, quote it in the Summary. It would be a stronger grounding.
- **Lookups I could not make.** I did not open the template, `CONTRIBUTING.md`, `SECURITY.md`, or an existing issue to see how code blocks are entered. I assumed GitLab Markdown. Your notes say there is no AI policy, so I added no disclosure. This is not a vulnerability, so I used the public tracker.
- **Warm-up for the `io_batch = "off"` runs.** The notes say "five runs of the same command" and do not say whether a warm-up came first. The report says only "five runs".

## Tracker search to record

Queries (issues and merge requests, all states): `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`.

Hits: !1482 (the bisected commit, named in the report), #2291 (open, "4.7.0: memory growth with HTTP/2 upstreams", a different symptom), and #2140 and #1977 (closed, unrelated). I found no duplicate. A null result only covers those queries, so rerun them just before filing.

## Left out on purpose

- The customer's name, the shipper contract, and the bench host name. The report says only that we have a contractual p99 target below 5 ms. **Please confirm you are happy to state that target in a public tracker**, or cut that sentence.
- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks, which showed no difference beyond 1%. They do not bear on this report. Offer them if a maintainer asks what else was checked.
- The commit author's name and email appear in the pasted bisect output. They are already public in the project's history.

## For you to decide

- **Comment on !1482 as well?** It is merged, so a new issue is the right place for the report. A short comment linking the issue may still help the author. I did not draft one.
- **The profile files.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) exceed the 10 MB attachment limit. Decide whether to host the flame graph somewhere public. I would not publish `perf.data`, because it can contain more than the benchmark process.
- **Defending the report.** The project has no AI policy, so nothing is required. The maintainers' follow-up questions will go to you, so check that you can answer them from the measurements above.
- **The production numbers.** The dashboard figures (about 7 ms after the upgrade, about 2.4 ms after `io_batch = "off"`) come from the edge team and are attributed that way. Ask them for a screenshot or an export if you want to attach evidence.
