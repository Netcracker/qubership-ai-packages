The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository. The task
statement is the pull request description, quoted here:

> set a timeout to get the return from requesting SSL upgrade.
>
> There are reported instances of cloud services changing the host underneath the connection and hanging when asking
> for SSL upgrade. This sets the timeout temporarily to avoid this

Its drift script is at `<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run `git` and read any file; do not build the project or run its
tests, and you may not use gh, a browser, or curl. End with the report the skill describes, as your final message.
