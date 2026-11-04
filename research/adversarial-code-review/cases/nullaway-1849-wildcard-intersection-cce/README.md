# Case: review uber/NullAway#1849, a change that later crashed on a wildcard of a class with an intersection bound

A missed-defect case for `adversarial-code-review`. The input is [uber/NullAway#1849][pr] at `808427ba`, 21 commits on
top of `e12c544c`. A maintainer approved the pull request, and CodeRabbit, an AI reviewer, left three inline findings
about captured types; none of the review named the defect below. The change itself says it was written with the help of
Codex. A month later, [issue #2030][issue], still open and with no fix, reported a `ClassCastException` and bisected it
to this change. The gold answer therefore comes from a user's report, not from a reviewer or an agent.

The change makes `GenericsUtils.effectiveWildcardUpperBound`, through the new `resolveEffectiveUpperBound`, take the
upper bound of an existing capture from `capturedType.getUpperBound()`, the structural bound javac computed, where it
used to take the bound of the backing `? extends` wildcard. When a class declares `C<T extends E & I>` and the code
reads a field through `C<? extends W>`, with `W` a type variable, the capture's structural bound is the intersection of
`W`, `E`, and `I`. `CheckIdenticalNullabilityVisitor.visitClassType` replaces the right-hand side with that bound and
passes it to `TypeSubstitutionUtils.asSuper`, and `ClassDeclarationNullnessAnnotUtils.dfsWithFormals` casts every direct
supertype of the intersection to `DeclaredType`. One of them is the type variable `W`, and NullAway crashes with a
`ClassCastException` from `Type$TypeVar` to `DeclaredType`. Only wildcard handling (`JSpecifyExperimental=true` or
`HandleWildcardGenerics=true`) reaches this path.

The prompt names neither the pull request nor the issue. The pull request was merged in September 2026 and the issue
filed in October 2026, both after the June 2026 training cutoff of Claude Opus 5.5.

[pr]: https://github.com/uber/NullAway/pull/1849
[issue]: https://github.com/uber/NullAway/issues/2030

## What it exercises

Area *Correctness and data integrity*: the change widens the set of types one function returns (a structural capture
bound can be an intersection, and a component of it can be a type variable), and the reviewer has to follow the new
value into its consumers and find the one that assumes a class type. The pull request is large (21 commits, about 500
changed lines) and its tests cover dependent and captured bounds, but no intersection bound.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **A capture's structural bound can be an intersection with a type-variable component.** Pass: a finding that the
   bound from `capturedType.getUpperBound()` (`GenericsUtils.java` line 192), used now in place of the wildcard's
   `extends` bound, can be an intersection type when the formal has an intersection bound such as `T extends E & I`,
   and that a consumer does not handle it: `visitClassType` handles an intersection only on the left-hand side
   (`CheckIdenticalNullabilityVisitor.java` line 73) and passes the right-hand side to `TypeSubstitutionUtils.asSuper`,
   and `ClassDeclarationNullnessAnnotUtils.dfsWithFormals` casts each direct supertype to `DeclaredType`
   (`ClassDeclarationNullnessAnnotUtils.java` line 76), which fails on a type variable. A finding that names the
   intersection bound and a crash or `ClassCastException` on another consumer of the new bound also passes. Partial:
   the report says the new bound can be an intersection, or differs in shape from the old `extends` bound, and asks
   for a test, without naming a consumer that fails on it. Fail: neither.
   `grep -niE 'intersection|getUpperBound|ClassCast|DeclaredType|dfsWithFormals|asSuper' result.md`

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity* (boundary inputs, the
  implementation against what the tests assert)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation* (tests that would catch an
  incorrect implementation)

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `e12c544c576d88900343c41d76233025e5bb05f7` (the parent of the pull request's first commit), and `808427ba636e0b00dcebf8e7cc7dd9cc56870ef8` (the pull request's last commit). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/nullaway-1849-wildcard-intersection-cce <model> <label> <rev>
```
