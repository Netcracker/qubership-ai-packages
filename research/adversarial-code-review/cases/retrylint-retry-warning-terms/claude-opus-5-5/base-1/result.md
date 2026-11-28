# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 1 minor, 2 nit)
Revision: `8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37`
Held until the code is settled: 1 finding (F4, in the ledger)

The main blocker is F1: the new message gives the wrong reason for the warning. Five reviewers found it independently, and running the head confirmed it.

## Findings

- **F1 major** `retrylint/messages.py:6`: The warning gives "on an unsafe method" as the reason, but the check flags methods that are not idempotent.
  - "Safe" (RFC 9110 §9.2.1) and "idempotent" (§9.2.2) are different properties. PUT and DELETE are unsafe, yet retrylint never warns on them.
  - Run on a policy with retried PUT, DELETE, POST and PURGE, the head warns only on POST and PURGE, both "on an unsafe method".
  - The new wording contradicts the README, the `IDEMPOTENT` set in `__main__.py` and the function name `non_idempotent_retry`.
  - The two updated golden files lock the wrong wording in.
  - Fix: say "non-idempotent method" and update `tests/golden/post_retry.txt` and `tests/golden/patch_retry.txt`.
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy." tells the user to remove every retry in the policy file. The warning is about one endpoint, and the README uses "retry policy" for the whole file.
  - Fix: something like "Set its retries to 0." for this endpoint.
  - The Idempotency-Key advice the change removed could never silence the check, because `policy.py` reads no headers, so it does not need to come back.
- **F3 nit** `retrylint/messages.py:6`: "=> retry x3" uses symbols where words belong, and doesn't say whether 3 counts retries or total attempts. The old "retried up to 3 times" matched the file's retries column.
- **F4 nit, held** (commit message): The commit body says the old warning wrapped over three lines at 80 columns and treats that as the problem.
  - The old text actually took four lines.
  - The new warning is still 119 characters with the README's `client.conf`, so it still wraps onto two lines.

## Review notes

- **Measurement skipped:** no diff-coverage or mutation tool applies to this pure Python repository. The golden suite (`python3 -m unittest`) passes at the head.
- **Axes:**
  - These ran at profile `medium`: correctness, telemetry, tests, change description, change reach, architecture, documentation pages, intent and scope, least surprise, compatibility, simplicity.
  - These were skipped because nothing they cover changed: security, reliability, performance, formats, comments, vocabulary, naive reader.
- **Dropped by the verifier (3):**
  - The question whether removing the Idempotency-Key advice and the RFC citation was intended: shortening the message, the stated goal, covers that, and the removed advice had no effect on the check.
  - The commit message not quoting the new text: the subject already says the warning changed.
  - The README never quoting the warning: F1's fix removes the mismatch.
- **Delivery schema:** `review-delivery` wasn't next to this skill's directory, so I used the copy installed at `~/.claude/skills/review-delivery`. `review.json` validates against its schema.
- **Cleanup:** I removed all the worktrees this review created. The review clone is unchanged at `7463fb4b`, with no edits and no commits.

Files are in `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-1/round-1-7463fb4b/`:
- review.json
- ledger.md
