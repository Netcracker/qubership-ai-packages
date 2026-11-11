Only the test file changed, production code is untouched, and nothing is committed. Here's the message for the PR author.

---

**Message to the author of #1750:**

The fix had no tests, so I added the ones the change owes to the existing `springValueFieldTest` in `FrameworkTests.java`, alongside the other `@Value`/SpEL cases it already checks:

- **`NegativeCases`** — four new fields covering each syntactic form `NULL_COMPARISON_PATTERN` is meant to strip: `someBean != null ? ... `, `someBean == null ? ...`, `null != someBean ? ...`, and `null == someBean ? ...`. All four are distinct regex alternatives/operand orders your pattern handles (`[!=]=\s*\bnull\b|\bnull\b\s*[!=]=`), so each is a real way the fix could be half-applied (e.g. only one operand order, or only one operator). None of them should produce a diagnostic.
- **`PositiveCases`** — one control, `#{someBean != null ? null : 'default'}`, which combines a null comparison *and* a real null branch. This is the exact case your PR description calls out as needing to stay flagged, and it's the test that would catch a fix that over-corrects and stops detecting real null-producing expressions.

I verified this is a genuine regression test, not just a green run: with `SpringHandler.java` reverted to its pre-fix state (same test code, only the production file swapped back), the suite fails with `Saw unexpected error on line 13: @NonNull field 'nullComparedWithNotEquals' not initialized` — i.e. it fails on the bug's actual symptom, not a missing symbol. Restoring the fix makes it pass again. I also re-ran `:nullaway:test` (full suite, green) and `:nullaway:buildWithNullAway` (green).

What I didn't do, and would leave to you: I didn't add a case for mixed whitespace around the comparison operators (e.g. `!=null` or `!=  null`) — that's a property of the regex's `\s*`, not something your Javadoc specifies as a contract, so I treated it as implementation detail rather than a specification partition worth locking down. If you *do* want that guaranteed, it'd be a one-line addition to `NegativeCases`.
