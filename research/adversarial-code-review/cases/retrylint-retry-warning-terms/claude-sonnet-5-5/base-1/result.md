**Review of 7463fb4 "Shorten the retry warning" (base 8587e48): request_changes**

The commit shortens the non-idempotent-retry warning and updates two golden files. The golden test passes. I ran the review inline on this small diff (33 lines). I did not use the skill's subagent axes, verifier or `review.json`, so no independent verification pass ran and no `review.json` was written.

**Major**

1. **The warning now uses the wrong term, and the README contradicts it.** `retrylint/messages.py:6` says "on an unsafe method".
   - The linter flags methods that are not idempotent, not methods that are unsafe. `README.md` and the `IDEMPOTENT` set in `retrylint/__main__.py` both define the rule by idempotency (RFC 9110 §9.2.2).
   - PUT and DELETE are unsafe in the RFC sense but idempotent, and the linter deliberately accepts them. `tests/golden/put_delete_retry.conf` shows this.
   - A user who reads "unsafe method" and sees PUT or DELETE retries pass will conclude the tool is wrong or inconsistent.
   - Fix: say "non-idempotent method", for example `POST /orders => retry x3 on a non-idempotent method; ...`.

2. **The remedy is worse, and the reference is gone.** The old message offered two fixes: remove the retry, or send an `Idempotency-Key` header that the server deduplicates. The new text says only "Drop the retry policy."
   - The commit message only argues for shortening. It doesn't say the advice was removed on purpose.
   - Dropping retries is often not an option for POST or PATCH endpoints such as payments, and the Idempotency-Key route is the standard way to keep them.
   - The pointer to RFC 9110 §9.2.2, which justifies the warning, is also gone from the message.
   - Fix: keep a short form of the remedy, for example "...; drop the retry or add an Idempotency-Key". If the removal is deliberate, say so in the commit message.

**Minor**

3. **The `=>` and `x3` notation is unexplained.** "retry x3" is compact but ambiguous, because it doesn't say whether the request is sent 3 times or retried 3 times. The old text said "retried up to 3 times". The policy file's third column is the number of retries, so "retry x3" can read as 3 attempts in total. Consider "up to 3 retries".

4. **The test coverage is thin.** The golden files pin the exact text, so every wording change needs a golden update. No test checks the part that matters, which is that the message names the method, the endpoint and the retry count. That is fine for a wording-only change, but it is why item 1 got through.

I didn't find any problems in the logic. `lint` and `policy.parse` are untouched, and both golden outputs match the new format.
