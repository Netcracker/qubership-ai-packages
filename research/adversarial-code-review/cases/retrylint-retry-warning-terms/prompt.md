The skill for this task is under <skills>: read `<skills>/adversarial-code-review/SKILL.md` in full and follow it. Do
not load any other copy of it.

Review the pull request at head `<head>`, base `<base>`: the change `<base>..HEAD` of this repository, one commit. This
directory is a disposable clone made for this review at that head; use it as the isolated workspace and do not remove
it. The GitHub integration is not available: take the title, description, and stated intent from the commit message
(`git log <base>..HEAD`), and treat the discussion as having no comments and no reviews. Do not record that as a
coverage gap.

Do not change any file and do not commit. You may run local commands such as `git` and `python3`, and you may not use
gh, a browser, or curl. Publication is not authorized and you may not ask about it: end with the chat report the skill
describes, in English, as your final message.
