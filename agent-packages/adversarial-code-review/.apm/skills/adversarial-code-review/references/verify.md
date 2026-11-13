# Verifier's brief

Give this to a fresh subagent after every axis has written its findings.

> You verify the findings of a pull request review. Read `<skill dir>/references/finding-rules.md` first. The review
> input is `<work>/input.md`; the code at the reviewed head is in `<workspace>`; the change is
> `git diff <base>...<head>`. The findings are in `<work>/axes/*.json`. Out of scope: `<exclusions or "nothing">`. The
> earlier round's result, if any, is `<previous>`. `axes/previous.json` holds the threads of earlier rounds whose defect
> remains; verify them like any other finding.
>
> For every finding:
>
> 1. Read the code and text its evidence cites, at the reviewed head, and check each `fact`. Where a fact is wrong, or
>    the problem does not follow from the facts, drop the finding. Where it holds only under a condition you cannot
>    check, make it a `question` that names the condition.
> 2. Drop it where the request put it out of scope. Check its `origin`, `introduced_by`, and `disposition` by
>    *Origin* in `finding-rules.md`, and correct them. To run anything, add your own worktree first
>    (`git -C <workspace> worktree add <work>/verify-wt <sha>`) and run there, never in `<workspace>`.
> 3. Check the severity against the question in `finding-rules.md`, and correct it.
> 4. Check that `proposed_solution` resolves the problem without a side effect the finding does not mention.
>
> Then across findings:
>
> - Merge findings from different axes that ask for the same change; keep the higher severity and both axes' evidence.
> - Group the rest into classes: findings that likely share one root cause, so one fix addresses them together. Give
>   each class a title and a one-sentence root cause. A finding that shares a cause with no other has `class: null`.
>   Only `change` findings and `preexisting` findings with `disposition: extend_scope` join a class; the author fixes
>   neither of the others in this change.
> - Assign ids `F1`, `F2`, ... in severity order. Where `<previous>` has a finding this one continues (same defect at
>   the same place, or its `prior_thread`), keep that id, and number new findings after the highest id `<previous>`
>   used.
> - In each `previous_findings` entry whose thread a finding continues (its `prior_thread`), set `finding_id` to that
>   finding's id; delivery reads the thread's severity from it.
>
> Write `<work>/review.json` by `<schema>`: every field of `<work>/review-head.json` as it is, except those
> `finding_id` values, plus `findings` and `classes`. Reply with: findings kept per severity, findings dropped with a
> one-line reason each, and the classes.
