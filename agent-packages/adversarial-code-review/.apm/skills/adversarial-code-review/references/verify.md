# Verifier's brief

Give this to a fresh subagent after every axis has written its findings.

> You verify the findings of a pull request review. Read `<skill dir>/references/finding-rules.md` first. The review
> input is `<work>/input.md`; the code at the reviewed head is in `<workspace>`; the change is `git diff
> <base>...<head>`. The findings are in `<work>/axes/*.json`. Out of scope: `<exclusions or "nothing">`. The earlier
> round's result, if any, is `<previous>`. `axes/previous.json` holds the threads of earlier rounds whose defect
> remains; verify them like any other finding.
>
> For every finding:
>
> 1. Read the code and text its evidence cites, at the reviewed head, and check each `fact`. Where a fact is wrong, or
>    the problem does not follow from the facts, drop the finding. Where it holds only under a condition you cannot
>    check, make it a `question` that names the condition.
> 2. Check that it is about the change and not out of scope, by `finding-rules.md`. Drop it otherwise.
> 3. Check the severity against the question in `finding-rules.md`, and correct it.
> 4. Check that `proposed_solution` resolves the problem without a side effect the finding does not mention.
>
> Then across findings:
>
> - Merge findings from different axes that ask for the same change; keep the higher severity and both axes' evidence.
> - Group the rest into classes: findings that likely share one root cause, so one fix addresses them together. Give
>   each class a title and a one-sentence root cause. A finding that shares a cause with no other has `class: null`.
> - Assign ids `F1`, `F2`, ... in severity order. Where `<previous>` has a finding this one continues (same defect at
>   the same place, or its `prior_thread`), keep that id, and number new findings after the highest id `<previous>`
>   used.
>
> Write `<work>/review.json` by `<schema>`: every field of `<work>/review-head.json` as it is, plus `findings` and
> `classes`. Reply with: findings kept per severity, findings dropped with a one-line reason each, and the classes.
