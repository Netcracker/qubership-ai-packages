# Hand-over note: Ferrygate p99 regression report

Proposed title: `4.7.0: p99 latency rises from 2.1 ms to 6.9 ms versus 4.6.2 on a 1 KiB proxy benchmark with the default config`

Target: `git.ferrygate.dev/ferrygate/ferrygate`, new issue, "Description" dropdown set to `Performance`, then replace the pre-filled body with `result.md`. The headings match `.gitlab/issue_templates/Performance.md` in its order; my own sections (Related issues, Possible cause) come after the template's last heading, and the `/label` quick action stays the last line. Nothing was filed.

## Gaps to close before filing

1. **Newer 4.7.x and the default branch.** The report says only 4.7.0 was tested. Check the releases page and the changelog for 4.7.1 or later, and for any mention of `io_batch` or coalescing. If a newer 4.7.x exists, rerun the ten-run measurement on it with the default config and replace the "Not established" line under Environment with the result. If it is fixed there, do not file.
2. **Launch commands.** The notes record the pinning (cores 0–7, 12–15, 16–23) but not the exact `taskset ... ferrygate ...` and `taskset ... bench-upstream ...` command lines. Add them to "How to measure" as you actually ran them, so a triager can repeat the setup.
3. **`bench/bisect-p99.sh`.** If this script is yours and not in the Ferrygate repository, paste its contents under "Bisect"; the report describes what it does but a reader cannot run it otherwise.
4. **`perf` version.** Not recorded. Run `perf --version` on the bench machine and add it to Environment.
5. **Duplicate search again.** The search in the notes was run on 2026-09-22/23. Rerun the same queries (`latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`, issues and merge requests, all states) just before filing, and check the comments on !1482 for a latency discussion. An open report of the same regression should get this evidence as a comment instead.
6. **Markup check.** Open any existing issue in the project (for example #2291) to confirm the tables and fenced blocks render as expected.

## Decisions for you

- **Residual after `io_batch = "off"`.** With `off`, 4.7.0 is still slightly slower than 4.6.2 (p99 2.25–2.33 ms against 2.06–2.23 ms, throughput 1.2% lower, five runs only). The report mentions it under Workaround as uninvestigated. If it matters to you, a second bisect with a threshold near 2.2 ms and `io_batch = "off"` set would show whether a different commit is responsible; that would be a separate, linked issue.
- **AI disclosure.** `CONTRIBUTING.md` has no AI policy, so nothing is required. Decide whether you want to say the draft was written with a tool, and make sure you can answer follow-up questions on the measurements yourself.
- **Profile artifacts.** The report offers `flame-470.svg` (40.2 MB) and `perf.data` (1.3 GB) on request. Only hand them over if you are comfortable sharing them; `perf.data` includes kernel symbols and process details from the bench machine.

## What I left out, and why

- The company name, the shipper, and the contract wording: the public issue says only "our 5 ms p99 target". Remove even that if you prefer.
- The bench machine's host name (`bench-03`).
- The gzip and config-reload benchmarks run for another ticket: they showed no difference beyond 1% and do not bear on this path.
