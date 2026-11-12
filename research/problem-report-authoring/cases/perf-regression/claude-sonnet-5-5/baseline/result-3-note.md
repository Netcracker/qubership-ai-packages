# Hand-over note for the person filing

Nothing was filed, and nothing was re-run while drafting. Every number comes from the session notes. I rechecked the medians, the 3.3 times ratio, the 8.5% throughput gap, and the 1.2% gap for `io_batch = "off"` against the tables.

**Title (the template has no title field):**
`p99 latency 3.3x higher in 4.7.0 than in 4.6.2 for 1 KiB proxied responses with default settings`

**Target:** `git.ferrygate.dev/ferrygate/ferrygate`, template `Performance.md`. The body follows its headings in order and ends with the `/label` line. I added one section of my own, `## Possible cause`, after the last template field.

## Fill in before filing

- The report body has a `[TBD before filing: ...]` marker in step 1 of "How to measure". The notes do not record how `tools/bench-upstream` was started, and they give the `taskset` pinning only as core ranges. Add the real start-up command and flags, and replace the marker. If you have the `taskset` command lines, they can go in too.
- The warm-up is recorded only as "one 30-second warm-up run, discarded". If it used the same `wrk` options with `-d30s`, say so.
- `bench/bisect-p99.sh`: the notes do not say whether it is in the upstream repository or a local script. If it is local, paste it into the Bisect section or describe it in words.
- Checksums of the two release tarballs were not recorded. The release numbers resolve to a build, so this is optional.

## Lookups not made or worth re-running

- Later 4.7.x releases and the development branch were not tested. The report says so. To close it, run the same measurement on the newest 4.7.x tarball and on a build of the default branch.
- The tracker search comes from the notes, and I could not repeat it. Re-run these in issues and merge requests, all states: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Also open #2291 (memory growth with HTTP/2 upstreams) and confirm it is a different problem. I left it out of the body.
- I could not read the create dialog, its contact links, `SECURITY.md`, or an existing issue. I assumed GitLab Markdown, and the template is the one named in the notes. This is a latency regression with no sign of a vulnerability, so I treated it as public.
- The notes say `CONTRIBUTING.md` has no AI policy, so the body has no disclosure.
- The "Supported versions" page was read in the session. Check it still lists 4.6.x and 4.7.x.

## Decisions for you

- New issue or a comment on !1482? !1482 is merged and its description has no latency numbers. I wrote a new issue because the symptom, the numbers, and the ask belong to a release rather than to that change, and I linked !1482 from the body. A comment there is the alternative.
- Redaction: I left out the customer and shipper names and the bench machine's hostname. The body keeps the 5 ms service target and the production dashboard readings (about 7 ms, then about 2.4 ms), attributed to the edge team. Delete them if you would rather not share them. The goal sentence then needs another wording.
- The body uses neutral wording and not "I". The dashboard figures come from the edge team, not from the bench runs. If you can attach an export or screenshot of the dashboard, do so after checking it for internal names.
- The Possible cause section says plainly that the source was not read. Do not strengthen it unless you read `src/io/writer.rs` or run an experiment.
- Expected behavior: the body asks for p99 within the 4.6.2 range and below 5 ms on default settings, and leaves the fix (coalescer or default) to the project. Change that if you want a different position.

## Left out on purpose

- The gzip benchmark (`bench/gzip.sh`) and config-reload benchmark (`bench/reload.sh`) showed no difference beyond 1% between the versions. They were run for another ticket and answer no question here.
- The flame graph (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) are not attached because of the 10 MB limit. Check both for hostnames and paths before sharing them with anyone.
- Measurements at other response sizes or connection counts do not exist. If the maintainers ask, the 64 KiB body that !1482 benchmarked is the obvious second case.
