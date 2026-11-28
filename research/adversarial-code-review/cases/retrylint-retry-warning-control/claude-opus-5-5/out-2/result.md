# Review: "Shorten the retry warning" (`8587e48..4578588`)

**Result: request changes.** The commit is meant to stop the warning wrapping in an 80-column terminal, but the new warning still wraps onto four lines, the same as before.

Reviewed at profile medium: 13 review areas, with an independent pass that re-checked every finding. The tests pass at the head (`python3 -m unittest`), and the changed lines are covered. Five findings survived: 1 major, 4 minor.

## Major

**F1: The shorter warning still wraps onto four lines at 80 columns** (`retrylint/messages.py:6-8`)
- **Line counts:** checked with `fold -w 80` on both expected-output files the tests compare against:

  | File | Characters before → after | Lines at 80 columns |
  | --- | --- | --- |
  | `post_retry.txt` | 303 → 245 | 4 → 4 |
  | `patch_retry.txt` | 309 → 251 | 4 → 4 |

- **Wrong count in the commit message:** it says the old warning wrapped over *three* lines; it actually took four.
- **Fix:** either shorten the message until it fits in fewer lines, or reword the commit message to claim only what the diff does. One version that fits in 3 lines (195 characters) combines F3's wording and drops the remedy F4 says cannot work:
  ```
  tests/golden/post_retry.conf:3: POST /orders is retried up to 3 times, but POST is not idempotent (RFC 9110, section 9.2.2), so a retried request may take effect more than once. Remove the retry.
  ```
- **Retest:** both expected-output files, plus a longer path such as `POST /v1/customers/orders 3`, should come out under 4 lines. Otherwise the commit message should drop the line-count claim.

## Minor

- **F2: "Put them first" mostly doesn't match the diff** (commit message). The endpoint and the retry count already came right after `file:line:`. The count still follows "is retried up to". What the diff actually does goes unmentioned:
  - it drops the word "endpoint" and the quotes around the endpoint;
  - it removes "such as creating a second resource".
- **F3: "so a retry may apply its effect twice" is confusing** (`messages.py:7-8`). "Its" now points to the retry rather than the request. "Twice" is also wrong when there are 2 or more retries: with 3 retries the request can take effect up to 4 times. Suggested replacement:
  ```python
          f"{endpoint.method} is not idempotent (RFC 9110, section 9.2.2), so a retried request may take effect more "
          f"than once. Remove the retry, or send an Idempotency-Key header that the server deduplicates."
  ```
- **F4: Following the Idempotency-Key advice never clears the warning** (`messages.py:8`). This was already wrong before this commit, but the commit rewrites this line. A policy file holds only the method, path and retry count, so there is nowhere to record the header. A user who adds it still gets the warning and exit status 1. Simplest fix here: drop that half of the advice. Letting a policy declare the header would need a format change, which belongs in a follow-up.
- **F5: No test checks the 80-column goal.** The tests compare the exact output, and the expected files were regenerated along with the new text. This depends on F1: add a length test once the message meets its target, or skip it if the commit message drops the claim.

F1 and F5 share one cause: the commit sets a line budget for the warning that the new text doesn't meet and no test enforces. Fixing F1 settles F5.

## Coverage notes
- **Merged and downgraded findings:** four reviewers independently flagged the four-line wrapping, and those became F1. Two flagged the "a retry" wording, which became F3. The verifier lowered F2 and F5 from major to minor.
- **Skipped areas:** comments, security, reliability, performance and file formats, because nothing in the change touches them.
- **Mutation testing:** not run, because no tool is installed.
- **Missing helper skills:** some reviewers ran without the writing guides their checklists name, because this session doesn't offer them. These were the guides for commit messages, tests and documentation pages, plus an English-style guide.
- **Not installed:** the skill that formats review reports, so I wrote this report directly from `review.json`.

No files in the repository were changed, and the extra worktrees made for the review have been removed. The record is in `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-4578588/round-1-45785881/`, with the findings in `review.json`.
