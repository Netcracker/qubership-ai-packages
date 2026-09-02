# Fix GitHub repository settings

## `GH-001`: Default branch

Inspect open pull requests, branch references, workflow triggers, badges, release automation, Pages, and integrations.
Show the impact and exact rename, then use GitHub's branch-rename operation after confirmation. Read back
`defaultBranchRef`; repair confirmed file references in a separate batch. Do not delete the old branch or remote refs.

## `GH-002`: Repository topic

Fetch [`Netcracker/.github/config/topics.json`](https://github.com/Netcracker/.github/blob/main/config/topics.json) and
select the exact repository entry. Compare its `repositoryTopics` with GitHub. If the entry is missing or ambiguous,
prepare a central-registry request instead of inventing a topic. After confirmation, add only the selected topic and
read back the full list; preserve unrelated topics.

## `GH-003`: Repository description

Draft one factual public sentence from the README and show it before `gh repo edit --description`. Do not publish
internal names, customer names, unsupported claims, or placeholders. Read the description back.

## `GH-004`: Visibility or archived state

Do not change visibility or unarchive during compliance Apply. Explain the detected state and consequences. Require a
new request that names the repository and exact transition.

## `GH-005`: Block direct commits to `main`

Inspect active rulesets and branch protection. Passing requires a pull-request rule on the default branch, not only
status checks. Compare with
[`Protect-main-branch.json`](https://github.com/Netcracker/.github/blob/main/config/Protect-main-branch.json). If no
equivalent rule exists, show the ruleset diff and bypass actors, confirm admin access and any single-maintainer
exception, and update an equivalent ruleset instead of creating a duplicate. Remove response-only API fields from a
fetched example. Read back the active rule and enforcement state. Do not change merge methods.
