# adversarial-code-review

A user-invoked skill for reviewing GitHub pull requests and GitLab merge requests from an isolated Git workspace. It
covers source code, dependencies, configuration, contracts, migrations, infrastructure, delivery definitions, and
human-facing artifacts.

The skill uses the language of the review request for chat communication and the report. After a completed `APPROVE` or
`REQUEST_CHANGES` review, it asks one concise publication question only when the user has not already chosen immediate
publication or an unsubmitted draft. Completed chat and platform results include blocking and non-blocking finding
counts. The skill reports coverage only when `REVIEW_INCOMPLETE` requires an exact material-gap description. It does not
ask follow-up questions or ask after `REVIEW_INCOMPLETE`.

GitHub and GitLab publications are in English by default. An explicit language request overrides this default.

Both publication modes use line-specific comments by default. Each finding appears once. The general comment contains
the result, reviewed revision, model signature, optional human assessment, and complete findings that cannot be attached
to the current diff. When earlier reviews contain findings to recheck, the chat report and general comment include
one short line per previous finding: its comment link, fix status, and brief reason. First reviews omit this block.
The general comment ends with a request to rate finding comments with 👍 or 👎 to help assess and improve review
quality. It does not repeat new inline findings or include other review metadata.

GitHub handling stays in the main
[`SKILL.md`](.apm/skills/adversarial-code-review/SKILL.md). A conditional reference contains only the GitLab-specific
access setup, collection, and write or read mechanics that the skill needs for GitLab merge requests.

The report uses `APPROVE`, `REQUEST_CHANGES`, or `REVIEW_INCOMPLETE`. Each finding is `blocking` or `non-blocking` and
includes confidence, an exact chat location, and compact `Problem` and `Proposed solution` fields. The problem includes
the concrete impact. After reporting or publishing, the skill removes only the disposable Git workspace it created.

Invoke `adversarial-code-review` with a GitHub pull request or GitLab merge request URL, or an unambiguous repository
and request number.
