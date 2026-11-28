# Review of `7463fb4` ("Shorten the retry warning"): request changes

The change rewrites the retrylint warning text in `retrylint/messages.py` and updates the two golden files. The suite passes (`python3 -m unittest`, 1 test).

The review ran differently from the skill's full procedure. One reviewer subagent covered all the axes together, with no per-axis subagents, no measurement subagent and no separate verifier. I re-checked its findings against the code myself. No `review.json` was written, so there is no ledger. No earlier round, comments or reviews existed.

## Major findings

1. **The new wording names the wrong property** (`retrylint/messages.py:6`).
   - The message says "on an unsafe method". In RFC 9110, "unsafe" (§9.2.1) is a different property from "not idempotent" (§9.2.2).
   - PUT and DELETE are unsafe but idempotent. `IDEMPOTENT` in `retrylint/__main__.py` exempts them, and `tests/golden/put_delete_retry.conf` expects no warning for them.
   - The README and the code comment both say "idempotent". A reader will wrongly conclude that PUT is flagged, or that the rule is safe versus unsafe.
   - Suggested fix: say "non-idempotent method".

2. **The commit's 80-column claim is false** (commit message, `retrylint/messages.py:6-7`).
   - The goldens show lines of 141 columns for PATCH and 136 for POST, and the message alone is about 104. In an 80-column terminal each warning still wraps onto two lines.
   - The commit says the new text is "short enough to scan in a CI log", and the change doesn't deliver that.
   - Either shorten the text further or reword the claim to "shorter, with endpoint and retry count first".

3. **The message loses its remedy and its reason** (`retrylint/messages.py:6-7`).
   - The old text offered two fixes: remove the retry, or send an `Idempotency-Key` header that the server deduplicates. The new text offers only "Drop the retry policy".
   - The RFC 9110 §9.2.2 pointer is also gone. A grep finds `Idempotency-Key` nowhere in the repository now. The README never documented that option, so users lose the only mention of it.
   - The commit body doesn't say that content was removed, so a reader sees only a shortening.
   - Restore the second remedy (in the message or in the README), and state the removal in the commit body.

## Minor findings

- **Cryptic notation** (`retrylint/messages.py:6`): `=> retry x3` is unclear. The count is an upper bound ("up to 3 times" before), and `x3` reads as exact. The README calls the field "retries", so `retries: 3` or "retried up to 3 times" fits better.
- **Wrong target in the instruction** (`retrylint/messages.py:7`): "Drop the retry policy" names the whole policy file, but the warning concerns one endpoint line. Say "Remove the retries from this line" or "Set the retry count to 0".
- **Output compatibility** (`tests/golden/*.txt`): the message text is what a CI grep or parser sees. The quoted `endpoint "METHOD path"` form is gone, and neither the commit nor the README says which part of the output is stable.
- **Test gap** (`tests/test_golden.py`): the golden test compares whole lines, so it passes on any wording. Nothing checks that the method and endpoint stay in the message, or that the line fits the width the commit claims.

## Coverage

- No findings were dropped.
- The README and `retrylint/policy.py` were read in full.
- The subagent applied the commit-description and docs-page checks by hand and did not load those skills.
