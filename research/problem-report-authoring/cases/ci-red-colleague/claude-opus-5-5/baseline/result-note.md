# Hand-over note: Slack DM to Dana about the red `main`

`draft.md` is the message body, ready to paste into a Slack DM to Dana. Nothing has been sent.

## Before you send

- **Check that `main` is still red.** Your notes were taken on 2026-10-30 at 14:10 UTC, and today is 2026-10-31. If someone has already reverted `4f2a9c1` or pushed a fix, the message is stale. Open the latest `main` run on https://ci.internal.example/ledger-service and check whether `OrderExportTest.exportsEmptyBatch()` still fails.
- **Check that #1311 and #1314 are still waiting in the merge queue.** The message says both are blocked.
- **Optional: link the re-runs.** The message names runs 88415 and 88419 by number only, because your notes give a URL for 88412 alone. If the pattern holds, the links are https://ci.internal.example/ledger-service/runs/88415 and https://ci.internal.example/ledger-service/runs/88419. Open them before you paste them in.

## What I did not do

- I ran nothing. There was no checkout and no network. Every observation in the message comes from your notes: the CI runs, the local Gradle runs, and the versions. The message presents them in your first person because you made them.
- I did not check the guess about `if (partitions.isEmpty()) return;` in `OrderExporter.export`. The message marks it as unchecked. To check it, read that method at `4f2a9c1` and line 57 of `OrderExportTest.java`, which counts the files the export writes.

## Checks

- The ask (fix forward or revert) is in the first line, together with the symptom and the commit.
- The trace is trimmed to the three lines from your notes, and the message says it is trimmed. The pasted text contains no secrets. The internal names stay because Dana works in the same codebase.
- The notes give no pronouns for Dana, so the message addresses them by name and never uses a third-person pronoun.
