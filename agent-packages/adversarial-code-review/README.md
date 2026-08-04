# adversarial-code-review

A user-invoked skill for reviewing GitHub pull requests and GitLab merge requests from an isolated Git workspace. It
covers source code, dependencies, configuration, contracts, migrations, infrastructure, delivery definitions, and
human-facing artifacts.

The skill reports in chat before any platform write. After explicit authorization, it can publish selected feedback
immediately or create an unsubmitted draft review. Both modes support line-specific comments and a single-line model
signature that includes any exposed thinking or reasoning level. It adds `Assessed by` with the selected GitHub or
GitLab account identity only after the user says that they reviewed the report.

GitHub handling stays in the main
[`SKILL.md`](.apm/skills/adversarial-code-review/SKILL.md). GitLab-specific collection and publication behavior live in
a conditional reference that the skill reads only for GitLab merge requests.

The report uses `APPROVE`, `REQUEST_CHANGES`, or `REVIEW_INCOMPLETE`. After the publication decision, the skill removes
only the disposable Git workspace it created.

Invoke `adversarial-code-review` with a GitHub pull request or GitLab merge request URL, or an unambiguous repository
and request number.
