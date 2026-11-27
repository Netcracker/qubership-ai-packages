## Review: `7463fb4` "Shorten the retry warning" (one commit on `8587e48`)

**Result: request_changes.** I found one major and two minor issues. I read the whole 3-file diff and the surrounding code myself. I did not run the skill's multi-axis subagent workflow, the verifier pass, or the measurement step, and I did not write `review.json`. This change is small, but none of its findings have had an independent verification pass. I did not run the tests.

### Major

**1. The new message says "unsafe method", which is the wrong property and contradicts the linter's own rules.**
- Location: `retrylint/messages.py:6`, plus the two golden files.
- The linter warns when a method is not idempotent. `__main__.py` defines `IDEMPOTENT`, and the README says "POST and PATCH are not idempotent".
- "Unsafe" is a different RFC 9110 term. PUT and DELETE are unsafe but idempotent. The repo's own `put_delete_retry.conf` expects no warning for them.
- A user who reads "retry x5 on an unsafe method" will reasonably conclude that PUT and DELETE retries are flagged too. They aren't, so the message misdescribes the rule.
- Failure case: the warning says `POST /orders => retry x3 on an unsafe method`. Someone who knows that PUT is unsafe will wonder why `PUT /orders/42 5` isn't flagged.
- Fix: say "non-idempotent method" (for example `retry x3 on a non-idempotent method`). It costs about 8 more characters.

### Minor

**2. The message no longer says what to do about it, and the advice is narrower.**
- The old text offered two remedies: remove the retry, or send an `Idempotency-Key` header that the server deduplicates. The new text offers only "Drop the retry policy".
- The linter's input has no way to express an idempotency key. A user who has deduplication in place now has only a message telling them to remove a retry they may need, with no way to suppress or acknowledge it.
- Keep the second remedy briefly, for example "Drop the retry or use an Idempotency-Key".

**2b. The RFC pointer was removed, and nothing replaces it.**
- The old message cited RFC 9110, section 9.2.2. The new one gives no source for why the method is flagged.
- The README still has the reference. This is acceptable if the shorter message is intended, but it is a loss for someone reading a CI log.

**3. The stated goal is only partly met, and the "retry x3" format is cryptic.**
- The commit says the old warning wrapped over three lines in an 80-column terminal.
- The new first line is still about 110 characters or more with a typical path, so it still wraps. The commit message overstates the result.
- "retry x3" and "=>" are terse and unlike the rest of the tool's text. The README has no matching documentation of the format. If anything parses the output, this is also a silent format change, but nothing in the repo does.

### Not an issue
- The golden files match the new f-string output exactly, including the file name, line number, method, path and count.
- The message function keeps its signature, and the summary line is unchanged.
