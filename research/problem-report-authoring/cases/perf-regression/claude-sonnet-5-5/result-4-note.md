# Hand-over note (not part of the issue)

Nothing was filed or sent. The body is `draft.md`, written into the headings of `.gitlab/issue_templates/Performance.md` in the template's order, with the `/label` line last.

**Proposed title** (the template has no title field; it names the symptom, not a fix):
`p99 latency 3.3x higher on 4.7.0 than on 4.6.2 with default config (1 KiB responses, 128 connections)`

## Decide before filing

1. **Can you explain and defend this report without me?** `CONTRIBUTING.md` has no AI policy, but I only know that file. I did not check for a policy elsewhere (the site, the create dialog, the template's checkboxes). The draft contains no disclosure statement. Add one if you find that the project asks for it.
2. **Is a new issue the right vehicle?** I wrote a new issue that links !1482. You may prefer a comment on !1482 (merged) or a note to its author. I found no open report of this symptom.
3. **The 5 ms contract.** The draft says only "a p99 target of 5 ms" and does not name Oakridge Freight, the shipper, or the contract, because the tracker is public. The draft also says the edge deployment's dashboard showed about 7 ms and later about 2.4 ms. Check that the edge team is fine with that being public. The dashboard figure before the upgrade is not in my notes, so the draft does not give one.
4. **Sharing the profile.** The draft offers `flame-470.svg` and `perf.data` on request. `perf.data` (1.3 GB) can contain process names, paths, and environment details. Review both before sending them.

## Gaps I could not close

- **Launch lines.** My notes do not record the commands that started Ferrygate and `tools/bench-upstream`. I did not invent them. The draft says they are not included. Paste the two lines (with the `taskset` arguments) under "How to measure" if you can find them in shell history.
- **Build identifiers.** The draft identifies the builds by release number and tarball name. If you have the tarball SHA-256 sums, or the commit the `v4.7.0` tag points to, add them to "Environment". I also do not know whether a newer 4.7.x exists; the draft says only that I tested 4.7.0 and not a later patch release or the development branch. One run on the newest 4.7.x would close it, using the same command and config.
- **Which build was profiled.** I assumed the `perf` capture ran on the 4.7.0 release tarball, like the benchmark runs. My notes say only "on 4.7.0". Confirm.
- **Re-run.** I could not run anything in this session, so the numbers are copied from the earlier session's notes. I recomputed the medians, ranges, the 3.3 times, and the 8.5% from the tables, and they match. Nobody re-ran the reproducer after the last edit. If you can, repeat one run per version before filing.
- **Reporter's wording for the workaround.** The "about 2.4 ms" after the rollout is the edge team's dashboard reading, not a run of mine, and the draft says so.
- **Checks I did not make.** Whether the project wants one problem per issue (the contribution guide may say), the project's AI policy outside `CONTRIBUTING.md`, and whether the template dropdown pre-fills a different default. None changes the draft, since it holds one problem.

## Left out of the issue, on purpose

- Tracker queries: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`, issues and merge requests, all states. Hits: !1482 (the bisected change), #2291 (open, different symptom), and #2140 and #1977 (closed, unrelated). The template has no slot for queries, so only the nearest hit and its difference are in the draft.
- The gzip (`bench/gzip.sh`) and config-reload (`bench/reload.sh`) benchmarks, which differed by under 1% on both versions. I have no output pasted for them, and they say nothing about the proxy path, so they would be an unsupported claim. Add them with their output if you want to show that other paths are unaffected.
- The bench host name and the bisect commit author's role: the author name and email appear only inside the verbatim `git bisect` output, which I kept as printed. Remove the `Author:` line if you would rather not repeat it.
- No fix is proposed. The only mechanism in the draft is the "Possible cause" section, marked unverified.
