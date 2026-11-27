The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, one
commit. There is no separate task statement: take the claimed cases from the commit message (`git log <base>..HEAD`),
and say so in the report as the skill asks. The writer of the change reports: "The new test passes on HEAD and on
`<base>`; it pins the smallest partial page, which the fix in `<base>` already counts." Its drift script is at
`<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run `git` and read any file; do not build the project or run its
tests. There is no network, so gh, a browser, and curl cannot reach GitHub. Where a skill asks you to run a gh
command, read the output saved for it under `<gh>` instead. End with the report the skill describes, as your final
message.
