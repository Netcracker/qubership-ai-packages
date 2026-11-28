# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 4 minor, 1 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37
Held until the code is settled: 2 findings (in the ledger)

## Main problems

1. **The shortened warning uses its own words and notation instead of those of the check, the README and RFC 9110** (major). The rewrite of `non_idempotent_retry` replaced three terms:
   - "not idempotent" became "unsafe".
   - "retried up to N times" became "=> retry xN".
   - The endpoint's retries became "the retry policy".

   This covers findings F1, F2 and F3.

## Findings

- **F1 major** `retrylint/messages.py:6`: The warning says the reason is "an unsafe method", but retrylint warns on methods that are not idempotent. RFC 9110 counts PUT and DELETE as unsafe too, and retrylint never warns about them.
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy" reads as deleting the whole policy file, which is what the README calls the retry policy. The warning actually clears when this one endpoint's retries are set to 0.
- **F3 minor** `retrylint/messages.py:6`: The warning writes the retry count as `=> retry x3`. Neither the policy file nor RFC 9110 uses that notation, and it doesn't say whether 3 counts retries or attempts.
- **F4 minor, medium confidence, question** `retrylint/messages.py` (old lines 8–9): Was it intended to drop the Idempotency-Key alternative? It leaves removing the retry as the only remedy for a POST that has to be retried.

The two held findings are about the commit message. They wait in the ledger until the code findings are fixed:
- **F5 minor:** the commit body describes only a reordering and a shortening. The change also dropped the RFC 9110 citation, the example and the Idempotency-Key alternative, and changed the stated reason.
- **F6 nit:** the body says the old warning wrapped over three lines at 80 columns. It took four, because the old golden lines were 303 and 309 characters.

## Notes

- **Tests:** The golden tests pass at the head. Running them with the old message makes both changed cases fail, so they do check the new text. No coverage or mutation tool is installed, so diff coverage was not measured.
- **Line length:** The new warnings are still 136 and 141 characters long, so they still wrap in an 80-column terminal. The commit doesn't promise a width, so this is not a finding.
- **Axes skipped:** comments, security, reliability, performance and formats; this change doesn't touch what they cover.
- **Cleanup:** I removed the worktrees the reviewers created, and the workspace has no changes. Nothing was published.

Files:
- review.json: `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/review.json`
- ledger.md (each finding's evidence, proposed text and retest): `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/ledger.md`
