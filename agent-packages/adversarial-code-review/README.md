# adversarial-code-review

A user-invoked skill for reviewing GitHub pull requests and GitLab merge requests from an isolated Git workspace. It
finds and verifies; it does not publish. Rendering and publishing the findings is
[`review-delivery`](../review-delivery/README.md)'s, which this package depends on. It also installs the authoring
skills its axes load: the doc-comment skills, `test-authoring`, `telemetry-authoring`, `docs-page-authoring`, and
`change-description-authoring`. A developer-style skill is not among them; install the one for the language the
repository writes in.

How a review runs:

1. Collect the request, its revision, its discussions, the repository's agent rules (`AGENTS.md`, `CLAUDE.md`), and
   what the change must agree with beyond its own tests, such as a specification, a golden suite, or the
   implementation it replaces, into a work directory.
2. Recheck every earlier review thread against the current code: the `major` findings first, then the findings that
   share a root cause, one cause at a time.
3. Run the review axes that apply to the change in subagents, as the profile below decides. The axes are files under
   [`references/axes/`](.apm/skills/adversarial-code-review/references/axes/): intent and scope, correctness,
   compatibility, security, reliability, telemetry, performance, architecture, simplicity, least surprise, formats,
   change reach, tests, comments, vocabulary, naive reader, documentation pages, and change description and branch. The
   request can add axes, narrow to some, and put surfaces out of scope. Where the build reports diff coverage and
   mutation testing (cribro, for example), one more subagent runs the changed modules' tests and the mutation tool
   alongside the first axes, and the tests and correctness axes start once it reports. This runs the request's code.

   Every profile orders the axes first: the two the reviewer judges most likely to find a `major` finding in this
   change, then a fixed order ranked by the findings of earlier reviews. The default profile, `medium`, runs the first
   three axes one per subagent, the next five in one subagent, and the rest in one more; `high` runs one subagent per
   axis; `low` runs two subagents, the first four axes and the rest. A subagent that holds several axes checks each
   less deeply. On two pull requests reviewed at all three profiles, the axis subagents of `medium` cost 39–45% less
   than one subagent per axis and found 3 of the 6 `major` findings; those of `low` cost 64–77% less and found 1 of 6.
   A rerun of single axes missed some of the same findings, so part of the loss is run-to-run variance. A change of
   more than 1000 lines, not counting generated and lock files, runs `medium` where the request asked for `low`.

   One subagent reads only so much code line by line. Where a change adds more than 4000 lines of code, not counting
   tests, documentation, data, configuration, and generated or lock files, `medium` and `high` shard the first two axes
   that read code a function at a time, such as correctness and tests: a script maps the changed files and the
   declarations they share, two planners on the cheapest model split the code into parts of 1500–3500 lines, one
   subagent per part holds the axis, and a seam reviewer checks the contracts between the parts, with differential tests
   where it can. Every axis reports the line ranges it read; at `medium` and `high`, the first two axes that read
   function bodies and left more than a quarter of their added code unread run once more over the unread ranges. On a
   pull request that added 19000 lines to one package, the single correctness subagent read about 2% of it; the same
   axis in six parts with a seam reviewer found seven `major` defects the review had missed, for about 1.8 million
   tokens with the verifier. The script outlines declarations with `sb` from
   [ast-bro](https://github.com/aeroxy/ast-bro) where it is on `PATH`; without it, the map has no declarations, and the
   planners split by directory and file size.

   Where the same request was reviewed before, the earlier round plans this one. The axes with the most `major` findings
   in it go first, and at `medium` and `high` an axis that found a `major` finding gets a subagent of its own, even
   where that adds subagents to the profile. The risk planner ranks first the shards that hold the files the fixes since
   the earlier round changed most, and the files of the defects still open. Where an earlier defect came from two code
   paths that have to agree and that fall in different shards, such as a check and the filter that must admit no more
   than it, the seam reviewer gets that contract as a seam. Every axis that applies still runs, and nothing the planning
   derives from the earlier findings reaches a reviewer's brief: the recheck in step 2 and the verifier handle those
   findings. Over 23 reviews with more than one round, an axis that found a `major` finding in one round found one in
   the next in 14 of 61 cases; an axis that had found none did so in 23 of 592.
4. A fresh subagent verifies every finding against the code, merges duplicates, and groups the rest into root-cause
   classes.
5. The result, `review.json`, goes to `review-delivery`: a chat report and a ledger by default, or an email, a GitHub
   review, or GitLab discussions on request.

Severity is `major`, `minor`, or `nit`, decided by what happens if the author does not fix the finding: the change does
not merge, the reviewer fixes it, or it stays. The result is `approve`, `request_changes` (at least one `major`), or
`review_incomplete`; only the findings the change makes count.

A defect the change did not make does not decide the result. One that another open request in the stack makes belongs
to that request, and a review of several dependent requests moves it there. One that already exists on the target
branch is either proposed for this change, where the change's purpose reaches it, or left to a follow-up issue that
`review-delivery` files with the user's agreement and links from the comment.

Invoke `adversarial-code-review` with a pull or merge request URL, or an unambiguous repository and request number.
