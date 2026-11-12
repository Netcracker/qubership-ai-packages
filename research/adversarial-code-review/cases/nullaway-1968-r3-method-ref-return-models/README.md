# Case: review uber/NullAway#1968 at `2ad2feed`, a third round where calls and method references must agree

A coverage case for `adversarial-code-review` on a change too large to read in one pass. The input is
[uber/NullAway#1968][pr] at `2ad2feed`, 17 commits and 1512 changed lines on top of `5ba2b547`. The change applies
conditional library return models (`nullImpliesNullParameters`, the `Map.getOrDefault` rule) to method references such
as `String.class::cast` and `map::getOrDefault`, so that a reference gets the return nullness a direct call already
gets. The gold answer is the reviewer's four inline comments on that commit, the third review round; the author replied
in the thread or changed the code near each of the four. The review is from October 2026, and reviews from 2025 on may
have been agent-assisted.

Earlier rounds, by the same reviewer and others, are not given to the model, so the run starts with no previous
findings. A finding from an earlier round that is still unfixed at `2ad2feed` and that the model reports again is not
counted against the run. The prompt names neither the pull request nor its title.

[pr]: https://github.com/uber/NullAway/pull/1968

## What it exercises

- *Correctness and data integrity*: a rule the change copies from the call path to the method-reference path, where
  the copy combines it with the handler hint differently from the original.
- *Verification and documentation*: a coverage exclusion that claims a branch is unreachable, a mode the new tests do
  not cover, and test sources whose expected diagnostics are assembled at run time.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **`getOrDefault` merges the handler hint for references and replaces it for calls.** Pass: a finding that in
   `GenericsChecks.java` (lines 1907-1917) the method-reference path combines `getMapGetOrDefaultReturnNullnessHint`
   with the hint from `handler.onMethodReferenceReturnNullnessHint` through `NullnessHint.merge`, which ranks
   `FORCE_NONNULL` above `HINT_NULLABLE` (`Handler.java`), while the call path in `AccessPathNullnessPropagation.java`
   (lines 1154-1162) assigns the `getOrDefault` hint and ignores the handlers; so with a custom `LibraryModels` that
   lists `Map.getOrDefault` in `nullImpliesNullParameters`, `map::getOrDefault` on a `Map<K, @Nullable V>` is accepted
   while `map.getOrDefault(k, d)` is reported. Partial: the report says the two paths compute the `getOrDefault`
   result separately and may drift, without naming the merge order or a case where they disagree. Fail: neither.
   [Original comment][c1].
   `grep -niE 'getOrDefault|merge|FORCE_NONNULL|HINT_NULLABLE' result.md`
2. **The raw-`Map` branch is reachable but excluded from coverage.** Pass: a finding that in `GenericsUtils.java`
   `getMapValueType` (lines 54-56) marks `mapType.getTypeArguments().size() != 2` with
   `// diff-coverage: ignore -- Raw Map.`, although a receiver whose class extends a raw `HashMap` reaches it, because
   `asSuper` then returns a raw `Map`; the marker should go and a test should cover that receiver for both the call and
   the reference. Partial: the report says the branch has no test, or questions the exclusion markers in general,
   without showing that it is reachable. Fail: neither. [Original comment][c2].
   `grep -niE 'raw|diff-coverage|getMapValueType' result.md`
3. **No legacy-mode test for an unbound `Class::cast`.** Pass: a finding that the legacy-mode tests in
   `Java8Tests.java` (`classCastMethodReferenceUsesDeclarationParameterNullness`, line 54, and the two after it) use
   only the bound `String.class::cast`, so the receiver offset that
   `LibraryModelsHandler.onMethodReferenceReturnNullnessHint` adds for an unbound reference
   (`parameterOffset = isUnbound ? 1 : 0`) has no test outside JSpecify mode. Partial: the
   report says the unbound or offset path lacks a test, but only for JSpecify mode or without naming the mode. Fail:
   neither. [Original comment][c3].
   `grep -niE 'Class::cast|unbound|parameterOffset|legacy|Java8Tests' result.md`
4. **Expected diagnostics are spliced in with `.replace`.** Pass: a finding that
   `checkGetOrDefaultWildcardValues` in `MapNullableValuesTests.java` (lines 23-67) builds both test sources from one
   text block with `// CALL_DIAGNOSTIC` and `// REFERENCE_DIAGNOSTIC` placeholders that two `.replace` calls (lines 58
   and 61) turn into `// BUG: Diagnostic contains:` markers or empty lines, so neither source shows which lines must
   report; the two settings of `HandleWildcardGenerics` should each have a complete source. Partial: the report calls
   the parameterized helper hard to read without saying that the expected diagnostics are hidden. Fail: neither.
   [Original comment][c4].
   `grep -niE 'replace|_DIAGNOSTIC|checkGetOrDefaultWildcardValues|MapNullableValuesTests' result.md`

[c1]: https://github.com/uber/NullAway/pull/1968#discussion_r4339396100
[c2]: https://github.com/uber/NullAway/pull/1968#discussion_r4339396133
[c3]: https://github.com/uber/NullAway/pull/1968#discussion_r4339396140
[c4]: https://github.com/uber/NullAway/pull/1968#discussion_r4339396152

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, the other paths that show
  the same symptom (check 1)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Architecture and maintainability*, duplicated policy
  (check 1)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that cover
  behavior and would catch an incorrect implementation (checks 2, 3, and 4)
- `adversarial-code-review`: `SKILL.md` §Reassess previous findings, a later round with no previous findings given

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `5ba2b547cecb789fbd8371e37205edfdbba9fa03` (the parent of the pull request's first commit), and `2ad2feed93c5e583a46690ed3ca775cd94ee6056` (the commit the third review round was on). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/nullaway-1968-r3-method-ref-return-models <model> <label> <rev>
```
