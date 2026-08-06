# adversarial-code-review

A user-invoked skill for reviewing GitHub pull requests and GitLab merge requests from an isolated Git workspace. It
covers source code, dependencies, configuration, contracts, migrations, infrastructure, delivery definitions, and
human-facing artifacts.

The skill uses the language of the review request for chat communication and the report. After a completed `APPROVE` or
`REQUEST_CHANGES` review, it asks one concise publication question only when the user has not already chosen immediate
publication or an unsubmitted draft. It does not ask follow-up questions or ask after `REVIEW_INCOMPLETE`.

GitHub and GitLab publications are in English by default. An explicit language request overrides this default. A
publication includes `Assessed by` only when the user clearly states that they personally reviewed the report and agree
with its findings. Publication authorization alone never adds this attribution.

Both publication modes support line-specific comments and a single-line model signature that includes any exposed
thinking or reasoning level.

GitHub handling stays in the main
[`SKILL.md`](.apm/skills/adversarial-code-review/SKILL.md). A conditional reference contains only the GitLab-specific
access setup, collection, and write or read mechanics that the skill needs for GitLab merge requests.

The report uses `APPROVE`, `REQUEST_CHANGES`, or `REVIEW_INCOMPLETE`. Each finding is `blocking` or `non-blocking` and
includes confidence, an exact chat location, and compact `Observation`, `Impact`, and `Resolution` fields. After
reporting or publishing, the skill removes only the disposable Git workspace it created.

Invoke `adversarial-code-review` with a GitHub pull request or GitLab merge request URL, or an unambiguous repository
and request number.
