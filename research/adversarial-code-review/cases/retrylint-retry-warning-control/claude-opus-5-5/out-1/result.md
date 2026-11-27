# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 1 minor, 1 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...4578588101d4a5af2876d0940d0bdad9252d621b

The result counts only problems this change introduced. Older problems are listed separately below.

## Findings

- **F1 major** commit message, about `retrylint/messages.py:6`: the commit message makes two claims the diff doesn't support.
  - It says the change moves the endpoint and the retry count to the front. They were already right after `file:line:` before the change. The diff only removes the word `endpoint`, the quotes around the endpoint, and "such as creating a second resource".
  - It says the warning wrapped over three lines at 80 columns. For the README's `client.conf` example it was 286 characters, which is four lines, and it is now 228 characters, which still takes three. The two warnings in the test files take four lines both before and after.
  - Either the message should claim only what the change does, or the warning needs to be split to fit 80 columns, with a test that checks the width.
- **F3 minor** `retrylint/messages.py:7`: "so a retry may apply its effect twice" now makes the retry the subject, so "its effect" reads as the retry's own. "Twice" is also wrong: a request retried 3 times can take effect 4 times. The ledger has suggested wording.
- **F7 nit** `retrylint/messages.py:8`: the last string has an `f` prefix but no placeholders.

## Older than this change

These problems were already in the warning text before this commit. The commit only rewrote the lines they sit on.

- **F2 major, pre-existing** `retrylint/messages.py:8`: one fix the warning suggests can't clear it. It tells the user to send an Idempotency-Key header, but the policy file has no way to record that header. A fourth column makes the tool crash with `ValueError`, so the warning and exit status 1 stay. Follow-up issue: not filed.
- **F4 minor, pre-existing** `retrylint/messages.py:6`: with one retry the warning reads "is retried up to 1 times". No test file covers one retry, which is the smallest count that warns. Since this line is being rewritten anyway, it could be fixed in this change. Follow-up issue: not filed.
- **F5 minor, pre-existing, medium confidence** `retrylint/messages.py:7`: every warning cites RFC 9110, section 9.2.2. That section doesn't define PATCH, which comes from RFC 5789, as the comment in `retrylint/__main__.py` says. It also says nothing about methods the tool doesn't know, such as PROPFIND. The RFC texts weren't available offline, so this point rests on general knowledge. Follow-up issue: not filed.
- **F6 minor, pre-existing** `tests/test_golden.py:20`: when a warning doesn't match its expected file, the test failure hides the difference. `GoldenTest` keeps unittest's default `maxDiff`, which is shorter than a warning's diff. Setting `maxDiff = None` fixes it. Follow-up issue: not filed.

Notes:
- The tests pass at the head: `python3 -m unittest` runs one test, three cases.
- Diff coverage and mutation testing were skipped because no tool for them is installed for this Python repository.
- Five checks didn't apply to this change: comments, security, reliability, performance, and file formats. Only a message string and the expected test output changed.
- I didn't file follow-up issues for F2, F4, F5 or F6, because the request authorized no external writes.
- The workspace has no uncommitted changes, and every worktree the reviewers added has been removed.

Files:
- review.json: `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-4578588/round-1-45785881/review.json`
- ledger (full evidence and suggested fixes): `/Users/vlsi/.cache/adversarial-code-review/local-retrylint-4578588/round-1-45785881/ledger.md`
