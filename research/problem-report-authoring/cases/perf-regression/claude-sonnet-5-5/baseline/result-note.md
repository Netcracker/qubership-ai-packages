# Hand-over note for the person filing

Nothing was filed or sent. The issue body is in `draft.md`, in the headings of `.gitlab/issue_templates/Performance.md` in the template's order, ending with its `/label` line. I added one section of my own after the last template field (`Possible cause (unconfirmed)`).

Suggested title (names the symptom): `p99 latency 3.3x higher in 4.7.0 than 4.6.2 for 1 KiB proxied responses with default io_batch`

## Filing

Choose the "Performance" template from the "Description" dropdown on `git.ferrygate.dev/ferrygate/ferrygate` and paste `draft.md` over it. The headings already match. I did not check whether `glab issue create --description "$(cat draft.md)"` applies the template or the `/label` quick action; the web form is the safer route.

## Not established: add or run before filing

I had no network, so none of these lookups were made in this session.

1. **Routing and policy.** I read neither `CONTRIBUTING.md` nor `SECURITY.md` myself. Your notes say there is no AI policy, so the draft has no disclosure. This is a performance regression, not a suspected vulnerability.
2. **Duplicate search, rerun.** The queries in the notes were `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`, over issues and merge requests in all states. The hits were !1482 (the bisected change), #2291 (open, memory growth with HTTP/2 upstreams, a different symptom), and #2140 and #1977 (closed, unrelated). The report names only !1482. Rerun the queries just before filing, since the notes give no date for the search.
3. **Later 4.7.x releases.** Only 4.7.0 was tested. Check the releases page and the changelog for a later 4.7.x that touches `io_batch` or the coalescer. If one exists, rerun the benchmark on it. The report says this is not established.
4. **`bench/bisect-p99.sh`.** The notes do not say whether the script is in the repository at every bisected commit or is your own file. The report describes what it does but does not include it. If it is yours, paste it into the issue or link it.
5. **Commands not recorded in the notes.** The report lacks the command that started `tools/bench-upstream`, the exact `taskset` command lines, and the command used for the 30-second warm-up (I assumed the same `wrk` line with `-d30s`, but the report does not say so). Add them if you have them.
6. **Build identifiers.** The report names the release tarballs only. Add the SHA-256 of each tarball, or the `ferrygate --version` output, if you have them.
7. **Attachments.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) exceed the 10 MB limit, and the report offers them on request. Decide whether you will host them anywhere. Read them for hostnames, paths, and environment strings first. I did not see them.

## Decisions for you

- **The 5 ms figure.** The report states it as "our latency objective" and does not name the customer or the contract. The notes mention a contract with your largest shipper; I left the company, the shipper, and the contract out of the public issue. Confirm you are happy to state the 5 ms and the production numbers (about 7 ms after the upgrade, about 2.4 ms after `io_batch = "off"`) as coming from your edge dashboard.
- **Who "I" is.** The report is written in your voice. The bench measurements, the bisect, and the profile came from the session behind these notes. The production dashboard readings and the `io_batch = "off"` rollout are attributed to your edge team. Check that this matches who did what, since you will answer follow-up questions.
- **Offer of artifacts.** The report says you can provide the flame graph and `perf.data` on request. Remove that sentence if you do not want to.

## Left out on purpose

- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks, which showed no difference beyond 1%. They came from another ticket and say nothing about this one. Add a line if you think maintainers will ask whether other paths are affected.
- The internal hostname `bench-03`.
- Untried workarounds and guesses about who else is affected.
