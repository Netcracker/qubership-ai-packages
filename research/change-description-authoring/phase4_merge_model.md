# Phase 4: the merge model beyond squash

Addendum to `phase3_result.md` section 4, written on 2026-09-11 for the change that added rebase and merge, merge
commits, and the first-parent classifier to SKILL.md section 4. Each claim is marked *cited*, *derived*, or *asserted*
as in phase 3. Pages were read on 2026-09-11.

## Mechanics

1. *Cited.* GitHub's default squash message "uses the commit title and message if the pull request contains only 1
   commit, or the pull request title and list of commits if the pull request contains 2 or more commits"; the
   repository can instead "use just the pull request title, the pull request title and commit details, or the pull
   request title and description"
   (<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests>).
   The 2022-08-23 changelog introduced the last three as separate settings
   (<https://github.blog/changelog/2022-08-23-new-options-for-controlling-the-default-commit-message-when-merging-a-pull-request/>).
2. *Asserted.* Under "pull request title and commit details" a single-commit pull request gets that commit's message as
   the body, and several commits a bulleted list. The settings page does not spell out the single-commit case; the
   claim comes from the reviewer of the change and from observed behavior, not from a page checked here.
3. *Cited.* For a merge commit, "the default message includes the pull request number and title. For example, `Merge
   pull request #123 from patch-1`. You can also choose to use just the pull request title, or the pull request title
   and description"
   (<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-merging-for-pull-requests>).
   That the default message carries the title as the body is observed behavior, not stated on the page.
4. *Cited.* Rebase and merge on GitHub "always updates the committer information and creates new commit SHAs" and
   "drops commits that were empty to begin with"; the commits are "added onto the base branch individually without a
   merge commit" (<https://docs.github.com/en/pull-requests/reference/pull-request-merges>). The same page says an
   indirect merge marks a pull request merged when its commits reach the base branch by another route, which is the
   direct-push case the classifier cannot tell from a rebase.
5. *Cited.* GitLab's default squash template is `%{title}`, and a project can compose `%{title}`, `%{description}`,
   `%{first_commit}`, `%{all_commits}`, `%{issues}`, `%{reference}`, `%{co_authored_by}`
   (<https://docs.gitlab.com/user/project/merge_requests/commit_templates/>). The default appends no merge request
   number, so a GitLab squash has the same subject shape as a rebase.

## Rules and the classifier

- *Derived.* The classifier reads the target branch first-parent only (`git log --first-parent '<target>'`) so that
  neither the branch's own unmerged commits nor the commits behind a merge commit enter the count, and it tells a merge
  by parent count (`%P` with a space) rather than by the `Merge pull request` subject, because a merge commit under
  the "pull request title" setting ends in `(#n)` like a squash (mechanics 3). Tested on 2026-09-11 against
  Netcracker/qubership-ai-packages (`merge 0 squash 15 plain 25`) and pgjdbc/pgjdbc (`merge 0 squash 3 plain 37`);
  both repositories allow squash and rebase with merge commits off.
- *Derived.* A `plain` shape is ambiguous between rebase, direct push, and a GitLab default squash (mechanics 4, 5),
  and a mixed `squash` and `plain` count between "both allowed" and squash beside direct pushes; the skill routes both
  to a house rule or the detection-failed default rather than to a model row.
- *Derived.* Under rebase and merge and under a merge commit every branch commit survives (mechanics 3, 4), so every
  commit is written as a full message and fix-up commits are squashed before the merge; the platform appends no pull
  request number under rebase, so the issue number, where an issue exists, is the reference a commit carries.
- *Derived.* The description reaches `git log` only under a squash or merge commit with "title and description"
  (mechanics 1, 3); the description is shaped as a commit body in those cases alone.
