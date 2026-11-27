The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, one
commit. There is no separate task statement: take the claimed cases from the commit message (`git log <base>..HEAD`),
and say so in the report as the skill asks. The writer of the change reports: "The suite passes on HEAD, and
`test_page_rejects_zero_per_page` is gone with the check it tested." Its drift script is at
`<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run `git` and `gh` and read any file; do not build the project or run
its tests, and there is no network for a browser or curl. End with the report the skill describes, as your final
message.
