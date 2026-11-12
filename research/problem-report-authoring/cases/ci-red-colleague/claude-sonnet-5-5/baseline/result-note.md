# Hand-over note: DM to Dana about the red `main`

The draft is in `draft.md`. It is a Slack DM, so it uses backticks and one triple-backtick block, with no headings. Nothing has been sent.

## Things to check before sending

- **The state is from 2026-10-30 14:10 UTC.** Check that `main` is still red and that nobody has already reverted or fixed it. If so, drop or change the ask.
- **PRs #1311 and #1314** were blocked at 14:10 UTC. Confirm they are still queued behind `main`.
- **The cause is a guess.** The draft marks it as unchecked. Nobody ran a revert of that one line, or a fix, to confirm it. To close it, remove the `isEmpty()` early return in `OrderExporter.export` locally and run `./gradlew :export:test --tests OrderExportTest`. Say so in the message if you do.
- **The trace is trimmed.** The draft keeps the failure line and the `OrderExportTest.java:57` frame. The notes say the other 40 lines are JUnit internals, so I left them out. The full trace is in run 88412.
- **The re-run links are missing.** The notes give only the numbers 88415 and 88419, not their URLs. The draft cites them by number. Add links if you have them.
- **The message sets no deadline.** The notes give none. If the queue needs an answer by a certain time, add it.
- **I added no offer to revert it yourself.** The notes don't say whether you can or want to. Add one if you do.

## Not done

I did not run or re-check anything. Every observation comes from your notes: the CI runs, the two re-runs, and the local pass and fail on `e01b77d` and `4f2a9c1`. The message presents the re-runs and the local runs as yours ("I re-ran", "Locally").

## Raised

None open. The notes name the recipient, the channel, and the ask.
