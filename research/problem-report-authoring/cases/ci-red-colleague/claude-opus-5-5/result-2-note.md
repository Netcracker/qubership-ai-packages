# Hand-over note: Slack DM to Dana about the red `main`

The draft is in `draft.md`. Paste it into Slack as one message, so the question arrives with the evidence.

## Check before sending

- **The notes are from 2026-10-30 at 14:10 UTC, and the message is in the present tense.** Open the CI history for
  `ledger-service` `main` and confirm that the newest run on `main` is still red, and that nobody has already reverted
  `4f2a9c1` or pushed a fix. If anything changed, update the first sentence, or don't send.
- **Check that #1311 and #1314 are still waiting in the merge queue.** If either one merged or was dequeued, change or
  drop that sentence.
- **The guess about `OrderExporter.export` is unverified.** It's marked as unverified in the message. To check it,
  read the `4f2a9c1` diff of `OrderExporter.export` and `OrderExportTest.java:57`. Or, on `4f2a9c1`, comment out
  the early return and run `./gradlew :export:test --tests OrderExportTest`. If that confirms it, you can change "My
  guess, which I haven't checked" to say what you ran.

## Decisions left to you

- **Whether to offer to do the revert yourself.** The notes don't say you're willing to, so the draft asks Dana to
  choose and offers nothing. If you'd do it, add something like "I can revert it if that's easier for you."
- **Whether to set a deadline.** The draft gives none. If the blocked PRs are urgent, say by when you need an answer.

## What I left out, and why

- The local JDK, Gradle, and macOS versions. CI fails the same way, so the failure doesn't depend on your machine.
- The rest of the 40-line trace. It's JUnit internals, and the run link has the full trace.
- I found nothing to redact. The pasted lines contain no tokens or personal data, and the internal names stay because
  this is a DM within the team.
