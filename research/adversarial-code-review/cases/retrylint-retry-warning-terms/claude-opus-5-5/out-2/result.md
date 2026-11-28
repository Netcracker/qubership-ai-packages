# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 3 minor, 0 nit)
Revision: `8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37`
Held until the code is settled: 1 finding (in the ledger)

## Main problems

1. The shortened warning swaps RFC 9110's and the policy file's words for shorthand (major). Each phrase of the old warning was replaced by a shorter one without checking it against RFC 9110 or against how the project uses its terms. As a result, the reason, the retry count and the advice each say something the check does not do. Findings F1, F2, F3.

## Findings

- **F1 major** `retrylint/messages.py:6-7`: The warning gives "an unsafe method" as the reason, but retrylint flags methods that RFC 9110 does not define as idempotent. PUT and DELETE are also unsafe under RFC 9110, and they pass without a warning. The README, the `IDEMPOTENT` set and `put_delete_retry.conf` all state the rule as idempotency, and the updated golden files now lock in the wrong reason. Suggested text, as it prints for `post_retry.conf`: `POST /orders is retried up to 3 times, but RFC 9110 does not define POST as idempotent (section 9.2.2); a retry may apply its effect twice. Set this endpoint's retries to 0.`
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy" reads as "remove the whole policy file", because that is what the project calls "the retry policy". The actual fix is to set the reported endpoint's retries to 0.
- **F3 minor** `retrylint/messages.py:6`: `=> retry x3` is notation that neither RFC 9110 nor retrylint's other output uses. It also doesn't say whether 3 counts retries or total attempts.

The held finding, F4, is about the commit message. It only mentions shortening and reordering the warning, but the change also rewrites the reason and the advice, and drops both the RFC citation and the Idempotency-Key alternative. The message quotes neither the old nor the new text.

## How the review ran

- **Profile:** medium. The diff is small (2 code lines), so nothing was split into parts.
- **Axes that ran:** 14, as three single subagents and two groups.
- **Axes skipped:** comments, security, reliability and formats. Each was skipped because the change doesn't touch what it checks.
- **Measurements:** none. No coverage or mutation tool is installed, and I installed nothing.
- **Tests:** `python3 -m unittest` passes at the head.
- **Verifier, kept:** a fresh subagent checked every finding and merged the duplicates that several axes reported.
- **Verifier, dropped:**
  - That the 80-column target isn't met. The new line is still 136 characters, but the commit message doesn't promise one line.
  - That the README lacks a sample warning. The gap was there before this change.
  - That the Idempotency-Key alternative should come back. The policy file can't record it, so following that advice would never clear the warning.
- **Network access:** the vocabulary subagent fetched the public RFC 9110 text from rfc-editor.org. Nothing about you or this repository was sent, and the verifier was told not to use the network.
- **Workspace:** nothing in it was modified or committed. All worktrees created for the review have been removed.

Files are in `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-retrylint-7463fb4b/round-1-7463fb4b/`:
- `review.json`
- `ledger.md`
