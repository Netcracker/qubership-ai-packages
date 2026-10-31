# Case: a build check against a committed list

The input restates the `verifyReleaseDependencies` check of Apache JMeter from `../../ab-verify-release-deps.md` as
notes, with one module added and the size over its limit. Every row of the subsection on the caller's channel applies.
Up to 1.1.0 the skill showed this very check as its second example, so the baseline runs copy it; 1.2.0 drops the
example, and the case checks that the rows still reach the message without it.

## Skill parts

- `SKILL.md`: §2 (What a message on the caller's channel carries)
- `english-developer-style`: §5 (sizes in two forms), §7 (Error and log messages)

## Checks

1. **Why the check exists** (`why_the_check`): it catches modules that enter the release unnoticed, or growth.
1. **The module** (`names_the_module`): `org.example:foo`.
1. **The diagnose command, filled in** (`diagnose_command_filled_in`): `dependencyInsight` with `--dependency
   org.example:foo`.
1. **The limit with its file** (`limit_with_its_file`): `total-size-limit` and `expected_release_artifacts.txt`.
1. **The accept command, runnable as printed** (`accept_command`).
1. **The path when the change is not intended** (`not_intended_path`).
1. **What to report** (`what_to_report`): what goes into the pull request description.
1. **Nothing invented** (`nothing_invented`): no path, key, command, or flag the notes do not establish.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `f3764558`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

Every run passes checks 1 to 7. Check 8 fails in one: Sonnet r2 says the accept command `sets
total-size-limit=88080384`, a value the notes do not establish, and offers a third way out, `Make room instead`, that
names no change the reader could make.

The baseline runs copy the removed example's sentences (Sonnet r1 almost word for word: `The check catches dependencies
that enter the release unnoticed, often transitively`); the new runs write their own. Three of the four new runs say
when accepting the change is wrong (`Do not run -PupdateExpectedJars only to make the build pass`), which no baseline
run did; Sonnet r2 says when to choose the other way out instead. Both new Sonnet runs list the largest jars, as every
baseline run did; both Opus runs give instead the overage, which equals the size of `foo-1.2.jar`. Length: new 199 to
234 words, baseline 140 to 213.
