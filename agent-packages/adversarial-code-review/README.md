# adversarial-code-review

A user-invoked skill for reviewing GitHub pull requests and GitLab merge requests from an isolated Git workspace. It
finds and verifies; it does not publish. Rendering and publishing the findings is
[`review-delivery`](../review-delivery/README.md)'s, which this package depends on. It also installs the authoring
skills its axes load: the doc-comment skills, `test-authoring`, `telemetry-authoring`, `docs-page-authoring`, and
`change-description-authoring`. A developer-style skill is not among them; install the one for the language the
repository writes in.

How a review runs:

1. Collect the request, its revision, its discussions, and the repository's agent rules (`AGENTS.md`, `CLAUDE.md`)
   into a work directory.
2. Recheck every earlier review thread against the current code.
3. Run one subagent per review axis that applies to the change. The axes are files under
   [`references/axes/`](.apm/skills/adversarial-code-review/references/axes/): intent and scope, correctness,
   compatibility, security, reliability, telemetry, performance, architecture, simplicity, least surprise, change
   reach, tests, comments, vocabulary, naive reader, documentation pages, and change description and branch. The
   request can add axes, narrow to some, and put surfaces out of scope. Where the build reports diff coverage and
   mutation testing (cribro, for example), one more subagent runs the changed modules' tests and the mutation tool
   alongside the first axes, and the tests and correctness axes start once it reports. This runs the request's code.
4. A fresh subagent verifies every finding against the code, merges duplicates, and groups the rest into root-cause
   classes.
5. The result, `review.json`, goes to `review-delivery`: a chat report and a ledger by default, or an email, a GitHub
   review, or GitLab discussions on request.

Severity is `major`, `minor`, or `nit`, decided by what happens if the author does not fix the finding: the change does
not merge, the reviewer fixes it, or it stays. The result is `approve`, `request_changes` (at least one `major`), or
`review_incomplete`.

Invoke `adversarial-code-review` with a pull or merge request URL, or an unambiguous repository and request number.
