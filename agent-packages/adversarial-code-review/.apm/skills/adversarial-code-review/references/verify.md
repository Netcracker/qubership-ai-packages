# Verifier's brief

Give this to a fresh subagent after every axis has written its findings.

> You verify the findings of a pull request review. Read `<skill dir>/references/finding-rules.md` and
> `<skill dir>/references/origin.md` first. The review
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
> 2. Drop it where the request put it out of scope.
> 3. Check the severity against the question in `finding-rules.md`, and correct it.
> 4. Check that `proposed_solution` resolves the problem without a side effect the finding does not mention. Whether
>    it removes the cause is checked after the families are updated, below.
> 5. Check the `location` range against *Location* in `finding-rules.md`, and correct it.
> 6. For a `defect`, check that `retest` fails at the reviewed head and would pass after any fix that resolves the
>    problem. For a `question`, check that it names the answer that settles the question. Rewrite it where it does not.
>    A finding from `axes/previous.json` keeps the `retest` it carries, unless the earlier one was wrong; then rewrite
>    it and say why in `evidence`.
> 7. Cut from `problem` and `proposed_solution` what `title`, `evidence`, or `suggestion` already says, and leave each
>    empty where nothing is left or where *Content* in `finding-rules.md` leaves it empty. Where `proposed_solution`
>    describes new text for the lines in `location`, move that text to `suggestion`, and check that it replaces the
>    whole range and nothing beyond it, and changes only what *Content* lets a `suggestion` change; where it changes
>    more, narrow it and `location` with it, and move a detail the author is to word into `proposed_solution`. Where
>    `evidence` cites a probe or a run whose code shows the defect, put that code in `reproducer`, cut to the lines that
>    show it, with the current and the expected result as comments, and drop from `problem` and `proposed_solution`
>    what it shows.
>
> Then across findings:
>
> - Drop a finding that raises again the defect or question of a `previous_findings` entry in
>   `<work>/review-head.json` whose `status` is `scope_deferred`: its follow-up issue tracks it. Drop one that raises
>   again an entry with `withdrawn` or `resolved_by_clarification` too, unless its evidence answers the entry's `reason`
>   or shows a consequence the thread did not consider. Keep such a finding as a continuation of the thread: set its
>   `prior_thread` to the entry's `thread_url`, and the entry's `status` to `fix_not_accepted`, with a `reason` that
>   says what the evidence adds.
> - Merge findings from different axes that ask for the same change; keep the higher severity, both axes' evidence, and
>   any `prior_thread`.
> - Set the `origin`, `introduced_by`, and `disposition` of every remaining finding by `origin.md`, so that each defect
>   is traced once; a finding from `axes/previous.json` keeps the ones it carries, unless it now meets the rule for
>   `split_out`, which is decided in the family step below. Rewrite the `proposed_solution` and `retest` of a claimed
>   case by `origin.md`. To run anything, add your own worktree first (`git -C <workspace> worktree add
>   <work>/verify-wt <sha>`) and run there, never in `<workspace>`.
> - Group the rest into classes: findings that likely share one root cause, so one fix addresses them together. Give
>   each class a title and a one-sentence root cause. A finding that shares a cause with no other has `class: null`.
>   Where one finding of a class carries the fix of the root cause, the `proposed_solution` of each other member whose
>   fix needs that cause names that finding and offers no fix of its own at the place the member was reported: an
>   author who defers the root cause would take that local fix, and it handles only the inputs the member names. It
>   says instead what becomes of the member if the root-cause fix is deferred: the member is deferred with it, or the
>   change takes out the decisions that depend on the cause.
>   Only `change` findings and `preexisting` findings with `disposition: extend_scope` join a class; the author fixes
>   neither of the others in this change.
> - Set each remaining finding's `family` from `families.json` (`[]` in a first round): the family whose property it
>   gets wrong at the family's sites, a new family where two findings of this round about what the code does share a
>   property and sites, or `null`. Add this round's members to each family, and mark it `recurring` by the rule in
>   *Track defect families* in `<skill dir>/SKILL.md`. Then check each `proposed_solution` against *Content* in
>   `finding-rules.md`, now that the families are known, and rewrite one that adds a case where that rule forbids it;
>   and decide `split_out` for each family by `origin.md`.
> - Assign ids `F1`, `F2`, ... in severity order. Where `<previous>` has a finding this one continues (same defect at
>   the same place, or its `prior_thread`), keep that id, and number new findings after the highest id `<previous>`
>   used.
> - In each `previous_findings` entry whose thread a finding continues (its `prior_thread`), set `finding_id` to that
>   finding's id; delivery reads the thread's severity from it.
>
> Write `<work>/review.json` by `<schema>`: every field of `<work>/review-head.json` as it is, except the
> `previous_findings` entries changed above, plus `findings`, `classes`, and `families`. Reply with: findings kept per
> severity, findings dropped with a one-line reason each, the classes, and the recurring families.
