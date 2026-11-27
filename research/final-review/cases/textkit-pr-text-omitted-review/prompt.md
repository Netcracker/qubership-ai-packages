The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the uncommitted change of this repository: the edits in
the working tree against `HEAD` and the untracked files. There is no separate task statement. The writer will commit
it with this message, which claims its cases:

> Add page_range() and a textkit-pages command
>
> page_range(number, per_page) returns the indexes of the first and the last item on a page, and the textkit-pages
> command prints page_count() for the two integers it is given.

Its drift script is at `<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run `git` and read any file; do not build the project or run its
tests. There is no network, so gh, a browser, and curl cannot reach GitHub. Where a skill asks you to run a gh
command, read the output saved for it under `<gh>` instead. End with the report the skill describes, as your final
message.
