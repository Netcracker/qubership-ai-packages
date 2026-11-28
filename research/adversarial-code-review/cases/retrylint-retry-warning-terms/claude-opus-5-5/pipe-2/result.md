# Review: Shorten the retry warning

Result: REQUEST_CHANGES (1 major, 3 minor, 1 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...7463fb4b6fd22662df5a220d656fb5f5d0ca9b37
Held until the code is settled: 1 finding (in the ledger)

The tests pass at the head (`python3 -m unittest`, 1 test). Diff coverage and mutation testing were not run because no tool for them is installed.

## Main problems

1. **The shortened warning makes up its own words (major).** The rewrite of `non_idempotent_retry` drops the words the README, the policy file and RFC 9110 use ("not idempotent", "retries", "the retried request") for new terms and notation. Rewriting `retrylint/messages.py:6-7` in those words fixes F1, F2, F3 and F5 at once. The verifier ran its proposed text, and for `post_retry.conf` it prints:
   `tests/golden/post_retry.conf:3: POST /orders has retries set to 3, but POST is not idempotent, so a retried request may apply its effect twice. Set retries to 0.`
   The endpoint and the count still come first, as the commit message wants. The two golden files would need updating to match.

## Findings

- **F1 major** `retrylint/messages.py:6-7`: The warning calls POST and PATCH "an unsafe method". retrylint actually warns on methods that are not idempotent (RFC 9110, section 9.2.2). PUT and DELETE are also unsafe, yet they get no warning, so the message gives the wrong reason for firing and contradicts the README.
- **F2 minor** `retrylint/messages.py:7`: "Drop the retry policy" uses the project's name for the whole policy file to mean the retries of a single endpoint.
- **F3 minor** `retrylint/messages.py:6`: The warning makes up the notation `=> retry x3`, which neither RFC 9110, the README nor retrylint's other output uses. `x3` also does not say whether 3 counts retries or attempts.
- **F5 nit, medium confidence** `retrylint/messages.py:7`: "a retry may apply its effect twice" says the effect belongs to the retry, but it is the retried request's effect that may be applied twice.

The held finding is F4 (minor, medium confidence). The commit message says the old warning wrapped over three lines; it actually wrapped over four. The new warning (136 and 141 characters in the golden files) still wraps over two lines in 80 columns. The commit message also doesn't mention that the RFC citation and the Idempotency-Key advice were removed. It is held because the commit gets reworded after the code settles.

The verifier dropped one finding: "the README never quotes the warning". That gap existed before this change, and once F1 is fixed the README's wording matches the warning again.

Files:
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/review.json`
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-7463fb4b/round-1-7463fb4b/ledger.md`
