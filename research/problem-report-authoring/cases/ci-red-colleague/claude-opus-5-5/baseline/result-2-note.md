# Hand-over note: Slack DM to Dana about the red `main`

The draft in `draft.md` is a Slack direct message to Dana Reyes. Slack renders the backticks and the `text` block as written. Nothing was sent.

## Check before sending

- **Is `main` still red?** Your notes were taken on 2026-10-30 at 14:10 UTC, and it is now 2026-10-31. Look at the latest `main` run in https://ci.internal.example/ledger-service/runs and at `git log origin/main` for a revert or a fix on top of `4f2a9c1`. If either landed, the message is stale. Drop it, or turn it into a question about #1311 and #1314.
- **Are #1311 and #1314 still blocked?** The merge queue may have moved on since your notes.
- **Has anyone else already raised this with Dana?** Search the team channel for `4f2a9c1` or `exportsEmptyBatch`. If someone has, reply in that thread with the local bisect result instead of sending a second message.

## What the message rests on

Every claim in the message comes from your notes. You ran both CI re-runs and the local runs, so the message says "I". I ran nothing in this session: I had no repository and no network. The cause line is marked as your unchecked guess. Every other sentence in the message stands without it.

## Left out on purpose

- The full 40-line trace. The CI run link carries it, and the frames that are left out are JUnit internals.
- An offer to revert the commit yourself. Your notes don't say whether you want to do that. If you do, add one line such as "I can revert it if you'd rather fix it on a branch."
