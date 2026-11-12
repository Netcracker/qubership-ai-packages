# Hand-over note: Ferrygate p99 regression issue

Nothing was filed. `draft.md` is the issue body for `git.ferrygate.dev/ferrygate/ferrygate`, using the `Performance.md` template headings in order, with the `/label` line last.

Suggested title: `p99 latency 3.3x higher on 4.7.0 than 4.6.2 with default config (1 KiB responses, 128 connections)`

## Before you file

1. **Template not fetched.** I worked from the headings and comments in my notes, not from the live template. Open the create dialog, pick "Performance" from the "Description" dropdown, and check that the headings and the `/label` line match. The report has no required field marked "not established" apart from the version gap below.
2. **Exact commands are missing.** The notes do not record how Ferrygate, `bench-upstream`, and the warm-up run were started, or the `taskset` invocations. The report describes the pinning in words and gives the measured `wrk` command only. Paste the real commands into "How to measure" or "Environment". I did not reconstruct them.
3. **Bisect script.** I don't know whether `bench/bisect-p99.sh` is in the Ferrygate repository or only on your machine. The report describes what it does and doesn't say where it lives. If it is local, add its contents.
4. **Newer release.** The report says a later 4.7.x and the development branch were not tested. If a later 4.7.x exists, install it and rerun the `wrk` command with the default config, then replace that sentence with the result.
5. **Production figures are not mine.** The roughly 7 ms and 2.4 ms dashboard values and the 2026-09-22 rollout come from your notes about the edge team. The report attributes them to the edge team's dashboard. Confirm them.
6. **Voice.** The draft uses "I" for the bench work and "we" for the production deployment. Adjust it if someone else should be named as the person who ran the benchmarks.
7. **Disclosure to the project.** The draft says there is a customer contract with a p99 under 5 ms and omits the customer's name. Confirm you are happy to state the 5 ms figure publicly. The draft also omits the bench host's name (`bench-03`).
8. **Attachments.** `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) exceed the 10 MB limit. The report offers them on request. If you would rather link them, upload them somewhere you control and add the link under "Profiling data". `perf.data` may contain paths and symbols you don't want public, so read it before sharing.

## Searches done

The notes record these searches, over issues and merge requests in all states: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Hits: !1482 (the bisected change), #2291 (different symptom), and #2140 and #1977 (closed, unrelated). The template has no field for queries, so the report names only the nearest hits. Keyword search can miss a differently worded duplicate, so run one more search for `throughput 4.7.0` and `slower` before filing.

## Left out of the report

- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks showed no difference above 1% between the versions. They answer no question the triager has, so I cut them. Add them if a maintainer asks how wide the regression is.
- No claim is made about syscall counts. I did not measure them, so I can't confirm or dispute the 4.7.0 release note.

## For you to decide

- Whether to also comment on !1482 (merged) linking the new issue. I did not draft one.
- The project has no AI policy in `CONTRIBUTING.md`, so I added no disclosure. I did not look for a policy elsewhere on the project's site or a checkbox in the form. You should be able to explain and answer follow-up questions about the measurements without me.
- This is not a suspected vulnerability, so a public issue is fine.

## Filing command

Not run. Only use it if you file from the CLI, after the edits above:

```bash
glab issue create --repo ferrygate/ferrygate --title "<title above>" --description "$(cat draft.md)"
```

The `/label` quick action on the last line is meant to apply on creation. Check the labels on the filed issue.
