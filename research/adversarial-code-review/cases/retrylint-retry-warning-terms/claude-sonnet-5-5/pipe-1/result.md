# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 4 minor, 0 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37
Out of scope: nothing

## Main problems

1. Rewritten warning text (major): the rewrite swapped in shorter wording without checking its terms, notation and advice against the check and the RFC. Findings F1, F2, F3.
2. Commit body misdescribes the change (minor): the body states a width goal the output doesn't meet and omits the advice the rewrite removed. Findings F4, F5.

## Findings

- **F1 major** `retrylint/messages.py:6-7`: The warning calls the method "unsafe", but the check flags non-idempotent methods. PUT and DELETE are unsafe in RFC 9110 terms yet are never flagged. A suggestion for lines 6-7 is in the ledger.
- **F2 minor** `retrylint/messages.py:6`: The new message invents notation (`=>` and `retry x3`) that RFC 9110 and similar linters don't use.
- **F3 minor** `retrylint/messages.py:7`: The warning drops the Idempotency-Key remedy and the RFC reference. "Drop the retry policy" doesn't say what to edit.
- **F4 minor** `tests/golden/post_retry.txt:1`: The commit body says the warning wrapped in an 80-column terminal. The new warning is 136 to 141 characters and still wraps (two lines each at 80 columns).
- **F5 minor** (no location, commit message): The commit body doesn't say that the Idempotency-Key remedy and the RFC reference were removed, or that "not idempotent" became "unsafe".

## Coverage notes

- **Skipped axes:** security, reliability, performance, architecture, simplicity, formats, comments and change-reach. The change is message text only.
- **Measurement:** skipped because neither `coverage` nor `mutmut` is installed.
- **Tests:** `python3 -m unittest` passes at the head.
- **Profile:** I ran the low profile, with two axis groups (tests, change description, correctness and naive reader; then intent and scope, vocabulary, telemetry, least surprise, compatibility and docs pages) and one verifier.
- **Gaps:** the review had no GitHub data, so there are no comments or reviews to reassess. Nothing was published.
- **Severity of F1:** the verifier raised F1 from minor to major. It's a wording defect in the one line the commit rewrites, so a reader may weigh it as a minor.

Files:
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/review.json`
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/ledger.md`

I changed no files in the repository and made no commit. The extra worktrees the subagents created live under the review directory in the cache.
