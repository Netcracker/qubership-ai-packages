# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 3 minor, 1 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37
Held until the code is settled: 1 finding (in the ledger)

The new warning gives the wrong reason for flagging an endpoint. That alone blocks the merge. The golden tests pass at head (`python3 -m unittest`), but only because the golden files were rewritten to match the new text.

## Findings

- **F1 major** `retrylint/messages.py:6`: The warning says a method is retried "on an unsafe method", but retrylint flags non-idempotent methods (RFC 9110 §9.2.2), not unsafe ones (§9.2.1). PUT and DELETE are unsafe, yet they get no warning. A file with `PUT 5`, `DELETE 2` and `POST 3` warns only for POST, and the warning still calls it "unsafe". The text now contradicts the README, the comment at `retrylint/__main__.py:7-9`, and the `put_delete_retry` golden case. Both golden files now expect the wrong reason. Fix: say "on a non-idempotent method" and update the goldens.
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy." tells the user to remove the whole policy file, since the README and `policy.py` use "retry policy" for the file. The warning is about one endpoint's `retries`. The change also drops the Idempotency-Key alternative the old text offered.
- **F3 minor, medium confidence, question** `retrylint/messages.py:6-7`: Is one 80-column line the target? The new warnings are still 136 and 141 characters, so they still wrap in the 80-column terminal the commit message names (down from three lines to two).
- **F4 minor, medium confidence** `retrylint/messages.py:6`: "=> retry x3" replaces the policy's word "retries" with notation that can be read as three attempts in total. The old text, "retried up to 3 times", was unambiguous.

## Older than this change

- **F5 minor, pre-existing** `README.md:18`, outside the diff: The README describes the warning but never shows it as printed. Follow-up issue: not filed.

How the review ran:
- **Coverage:** profile medium. 12 axes ran: correctness, vocabulary and tests each on their own, plus two grouped reviewers. One fresh verifier merged the duplicate reports and kept 6 findings.
- **Merged reports:** five axes reported F1 independently.
- **Not run:** diff and mutation coverage were skipped because this Python project has no tool for them.
- **Skipped axes:** 7, each with its reason in `review.json`.
- **Verifier's result:** it copied the provisional `approve` result unchanged. I changed it to `request_changes` because F1 is a `major` finding this change made.
- **Held finding:** F6, a `code_settled` nit about the commit message, appears only in the ledger.
- **Cleanup:** I removed all review worktrees. The disposable clone is unchanged and nothing was published.

Files are in `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-7463fb4b/round-1-7463fb4b/`:
- review.json
- ledger.md
