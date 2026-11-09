# review-delivery

Turns a finished code review into the form a reader needs, without reviewing anything itself. The input is a
`review.json` that follows [`schema/review.schema.json`](.apm/skills/review-delivery/schema/review.schema.json); the
reviewing skill (`adversarial-code-review`) writes it, and this skill renders it as:

- a chat report in the language of the request;
- a ledger file with every finding grouped by root-cause class, the input of a fixing session, rendered by a script
  rather than by the model;
- an email body for the user to send;
- a pending or submitted GitHub review with inline comments;
- GitLab Draft Notes or published notes.

Severity is `major`, `minor`, or `nit`, decided by what happens if the author does not fix the finding: the change does
not merge, the reviewer fixes it, or it stays. Requests about the branch rather than the code (squash, rebase, reword a
commit) are held back while any `major` or `minor` finding is open. There is no cap on the number of findings.

Writing to GitHub or GitLab needs the user's authorization, given once per review: publish now, or prepare a draft.
