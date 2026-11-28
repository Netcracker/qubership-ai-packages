The skill for this task is under <skills>: read `<skills>/adversarial-code-review/SKILL.md` in full and follow it. Do
not load any other copy of it.

Run a `medium` review of the change `<base>..HEAD` of this repository, a pull request to NullAway, an Error Prone checker
for Java nullness, with head `<head>` and base `<base>`. This directory is a disposable clone made for this review at
that head; use it as the isolated workspace and do not remove it. The GitHub integration is not available: take the
title, description, and stated intent from the commit messages (`git log <base>..HEAD`), and treat the discussion as
having no comments and no reviews. Do not record that as a coverage gap.

Do not change any file and do not commit. You may run local commands such as `git`; you may run the Gradle build only
with `--offline` and only if its dependencies are already cached, and you may not use gh, a browser, or curl.
Publication is not authorized and you may not ask about it. Render the review as the email the skill describes, and end
with the body of `email.md`, in English, as your final message.
