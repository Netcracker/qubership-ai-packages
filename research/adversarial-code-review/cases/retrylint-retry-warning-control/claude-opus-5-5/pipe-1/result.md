# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 3 minor, 0 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...4578588101d4a5af2876d0940d0bdad9252d621b
Held until the code is settled: 2 findings, F3 and F4, both about the commit message (in the ledger)

The tests pass at head (`python3 -m unittest`). I did not measure coverage or mutation coverage because no tool for either is installed for this Python project.

## Main problems

1. **The warning's consequence and remedy sentences (major).** The warning still carries a consequence clause and an Idempotency-Key remedy. The check can back neither: it does not count the effect, and it cannot see the header. Those two sentences are also most of what keeps the warning longer than two 80-column rows. Findings F1, F2, F7, F8.

## Findings

- **F1 major** `retrylint/messages.py:7-8`: The shorter warning still takes three or four rows in an 80-column terminal, so the change does not fix the wrapping that the commit message gives as its reason.
  - The golden warnings are 245 and 251 characters now, against 303 and 309 before, so they are still four rows.
  - The shortest warning the tool can print is 212 characters, which is three rows.
  - The commit message's "three lines" is also wrong about the old text, which took at least four rows for every input.
  - Suggested wording (the POST example), which fits in two rows: `…but POST is not idempotent (RFC 9110, section 9.2.2). Set retries to 0.`
- **F2 minor** `retrylint/messages.py:7`: "so a retry may apply its effect twice" has two problems:
  - "its" now points to the retry rather than the request.
  - "twice" undercounts: with 3 retries, the request can take effect up to 4 times.
- **F5 minor, pre-existing** `retrylint/messages.py:7`: The warning gives RFC 9110, section 9.2.2 as the source of "not idempotent" for every method it flags:
  - RFC 9110 does not define PATCH.
  - No RFC calls PROPFIND or unknown methods such as `FOO` non-idempotent.
  - The code's own comment at `retrylint/__main__.py:7-8` says this.
- **F6 minor, pre-existing** `retrylint/messages.py:6`: A policy line with 1 retry prints "is retried up to 1 times".
- **F7 minor, pre-existing** `retrylint/messages.py:8`: Following the "send an Idempotency-Key header" advice does not clear the warning. A policy line has no field for the header, so retrylint still prints the warning and exits with status 1.
- **F8 nit, medium confidence, pre-existing** `retrylint/messages.py:8`: "an Idempotency-Key header that the server deduplicates" says the server deduplicates the header, when it is the requests carrying the same key that get deduplicated.

Held until the code is settled (they are about the commit message):
- **F3 minor**: The commit message says the endpoint and retry count were in the middle of the warning and are now first. They already came right after `file:line: endpoint "`. The diff removes that wrapper and one clause, and the order stays the same.
- **F4 minor, medium confidence**: The commit message does not quote the new warning text. The old `endpoint "POST /orders"` form is gone, so a CI log filter that matched it will stop matching.

F5 to F8 were already in the old text, but they sit on lines this change rewrote, so they are offered as scope extensions. If you'd rather keep this change narrow, they can move to a separate follow-up issue.

Files:
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-45785881/round-1-45785881/review.json`
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-45785881/round-1-45785881/ledger.md`
