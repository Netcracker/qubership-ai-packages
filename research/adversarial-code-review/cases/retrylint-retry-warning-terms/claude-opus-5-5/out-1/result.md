# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 4 minor, 1 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37
Held until the code is settled: 2 findings (in the ledger)

## Main problems

1. The shortened warning swaps the field's words for shorthand (major): to make the message shorter, the commit replaced the RFC term, the retry-count wording and the remedy with shorthand ("unsafe method", "=> retry xN", "the retry policy"). Each of those says something different from what the check actually decides. Findings F1, F2, F3.

## Findings

- **F1 major** `retrylint/messages.py:6`: The warning says POST and PATCH are retried "on an unsafe method", but the check flags methods that are not idempotent. PUT and DELETE are also unsafe under RFC 9110 §9.2.1, yet they are never reported. A run at the head on a policy with PUT, POST and DELETE retries confirmed this. The README, the function name and the old text all say "not idempotent". The proposed fix is "on a non-idempotent method", with both golden files updated to match.
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy" reads as removing the client's whole policy, because the README uses "retry policy" for the whole policy file. What clears the warning is setting this endpoint's retries to 0. The proposed text is "Set the endpoint's retries to 0."
- **F3 minor** `retrylint/messages.py:6`: `=> retry x3` replaces "is retried up to 3 times" with notation nobody can look up. It also no longer says whether 3 counts retries or attempts.
- **F5 minor, medium confidence, question** `retrylint/messages.py:6-7`: Is the shortened warning meant to fit on one 80-column line? Every warning still wraps: the two golden lines are 136 and 141 characters, and the message's fixed words alone are 91. No test limits the length.

The 2 held findings are about the commit message. They wait until the code findings above are settled, and they are listed in the ledger:
- **F4 minor:** the message doesn't say the change also drops the Idempotency-Key remedy and the RFC 9110 §9.2.2 reference.
- **F6 nit:** the message says the old warning wrapped over three 80-column lines; it wrapped over four.

## How the review ran

- **Profile:** medium.
- **Axes that ran:** 13. Comments, security, reliability, performance and formats were skipped because the change doesn't touch what they check.
- **Reruns:** the grouped reviewer didn't load the required style skills for change-description and docs-pages, so those two axes were rerun on their own.
- **Measurement:** coverage and mutation testing were skipped because this pure-Python repository has no tool for them.
- **Tests:** `python3 -m unittest` passes at the head.
- **Verification:** a separate verifier checked every finding and merged the duplicates from several axes. It dropped one finding, that the README doesn't quote the warning, because the base README didn't quote it either.
- **Head check:** the head was rechecked before this report and has not moved.
- **Cleanup:** the review's own worktrees were removed. Nothing in the clone was changed.

Files:
- /Users/vlsi/.cache/adversarial-code-review/local-retrylint-7463fb4b/round-1-7463fb4b/review.json
- /Users/vlsi/.cache/adversarial-code-review/local-retrylint-7463fb4b/round-1-7463fb4b/ledger.md
