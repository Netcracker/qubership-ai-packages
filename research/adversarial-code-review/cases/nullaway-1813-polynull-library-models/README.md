# Case: review uber/NullAway#1813 at `e28cc726`, a large feature whose defects sit where the new models meet old code

A coverage case for `adversarial-code-review` on a change too large to read in one pass. The input is
[uber/NullAway#1813][pr] at `e28cc726`, 28 commits and 2358 changed lines on top of `3b3a34b2`. The change adds PolyNull
library models, applies them to `Optional.orElseGet` and `Map.computeIfAbsent`, and lets custom `LibraryModels`
providers declare their own. The gold answer is the reviewer's five inline comments on that commit, the first review
round; the author replied in the thread or changed the code near each of the five. The review is from October 2026, and
reviews from 2025 on may have been agent-assisted.

One of the five defects is outside the lines the change adds: the dataflow rule for `computeIfAbsent` in
`AccessPathNullnessPropagation` is unchanged, and becomes unsafe only because the new model accepts a lambda that
returns `null`. The prompt names neither the pull request nor its title.

[pr]: https://github.com/uber/NullAway/pull/1813

## What it exercises

- *Correctness and data integrity*: an older rule whose safety depended on an error the change removes, and a new
  diagnostic that skips the flag every sibling diagnostic honors.
- *Compatibility and evolution*: what an existing custom `LibraryModels` provider meets after the upgrade, both in
  which mode its models apply and when two providers model the same method.
- *Verification and documentation*: a test that passes without checking the behavior its name claims.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **A `null`-returning `computeIfAbsent` function hides a later dereference.** Pass: a finding that, with the PolyNull
   model on `Map.computeIfAbsent` (`LibraryModelsHandler.java` lines 1241-1254), a mapping function that returns `null`
   is now accepted, while the dataflow rule in `AccessPathNullnessPropagation.java` (lines 1187-1210, unchanged by the
   change) still marks `map.get(key)` as non-null after the call whenever the function's declared return type carries
   no `@Nullable`; so `map.computeIfAbsent("k", k -> null); map.get("k").hashCode();` gets no error. Partial: the report
   says the dataflow rule for `computeIfAbsent` should take the resolved PolyNull nullness into account, but shows no
   case it gets wrong. Fail: neither. [Original comment][c1].
   `grep -niE 'computeIfAbsent|AccessPathNullnessPropagation|dataflow' result.md`
2. **The PolyNull inference failure ignores `WarnOnGenericInferenceFailure`.** Pass: a finding that
   `reportPolyNullInferenceFailure` in `GenericsChecks.java` (line 3693) reports `GENERIC_INFERENCE_FAILURE` without
   checking `config.warnOnGenericInferenceFailure()`, which `runInferenceForCall` checks (line 1463), so
   `-XepOpt:NullAway:WarnOnGenericInferenceFailure=false` still reports, for example, `o.orElseGet(() -> null)` assigned
   to a non-null field. Partial: the report notes two separate inference-failure reporting paths that may disagree, but
   does not name the flag. Fail: neither. [Original comment][c2].
   `grep -niE 'WarnOnGenericInferenceFailure|reportPolyNullInferenceFailure|inference fail' result.md`
3. **Custom PolyNull models depend on `isJSpecifyJDKModels`.** Pass: a finding that in `CombinedLibraryModels`
   (`LibraryModelsHandler.java` line 1527) the PolyNull models of every provider, custom providers included, are read
   and validated only when `config.isJSpecifyJDKModels()` is true; so a custom provider's PolyNull models are ignored
   in plain JSpecify mode, and an invalid one (a `Receiver` location, no nested location) fails only once someone turns
   the JDK-models flag on. Partial: the report says only that the built-in models are gated on the JDK-models flag, or
   only that validation is skipped, without connecting it to custom providers. Fail: neither. [Original comment][c3].
   `grep -niE 'isJSpecifyJDKModels|JSpecifyJDKModels|custom provider|provider' result.md`
4. **Two providers modeling one method stop the compilation.** Pass: a finding that `CombinedLibraryModels` throws
   `IllegalArgumentException("Multiple PolyNull library model providers for ...")` (`LibraryModelsHandler.java` lines
   1536-1544) when two providers declare PolyNull locations for one method, before `shouldSkipModel` is consulted (line
   1550), so `IgnoreLibraryModelsFor` cannot work around it; since `DefaultLibraryModels` already models
   `Optional.orElseGet` and `Map.computeIfAbsent`, a third-party provider that models either one breaks the build, while
   every other model kind merges entries from several providers. Partial: the report names the exception as a conflict
   that can occur, but not that the built-in models collide with a user's, or not that the ignore option cannot help.
   Fail: neither. [Original comment][c4].
   `grep -niE 'Multiple PolyNull|IgnoreLibraryModelsFor|shouldSkipModel|two providers|conflict' result.md`
5. **The explicit-type-argument test never uses the result.** Pass: a finding that
   `genericMethodAcceptsCompatibleExplicitTypeArguments` in `PolyNullLibraryModelsTests.java` (line 333) checks only
   that no error is reported and never dereferences or assigns the result of `PolyNullMethods.genericFirst`, so it does
   not check the resolved nullness, and it has no case with an explicit `@Nullable` type argument that must report.
   Partial: the report says the PolyNull tests check few results or lack a negative case, without naming this test or
   the explicit type arguments. Fail: neither. [Original comment][c5].
   `grep -niE 'genericMethodAcceptsCompatibleExplicitTypeArguments|explicit type argument|genericFirst' result.md`

[c1]: https://github.com/uber/NullAway/pull/1813#discussion_r4300813851
[c2]: https://github.com/uber/NullAway/pull/1813#discussion_r4300813856
[c3]: https://github.com/uber/NullAway/pull/1813#discussion_r4300813863
[c4]: https://github.com/uber/NullAway/pull/1813#discussion_r4300813866
[c5]: https://github.com/uber/NullAway/pull/1813#discussion_r4300813896

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, the paths that show the
  same symptom outside the changed helper (checks 1 and 2)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, bullets *Contracts* and
  *Inherited state* (checks 3 and 4)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch
  an incorrect implementation (check 5)
- `adversarial-code-review`: `SKILL.md` §Review areas, opening of *Intent and scope*, the change size that cannot be
  read in one pass

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `3b3a34b296c373f72aabcaa7380dd463631b42c3` (the parent of the pull request's first commit), and `e28cc72601f15d61b7e5cf364fc5a6ca7a30430d` (the commit the first review round was on). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/nullaway-1813-polynull-library-models <model> <label> <rev>
```
