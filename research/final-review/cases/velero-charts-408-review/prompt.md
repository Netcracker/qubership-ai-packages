The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, two
commits. The task statement is the pull request description, quoted here:

> [velero] Add Termination Grace Period Helm Value
>
> Adds in the ability to specify the termination grace period to the Helm chart. Primary use case is to allow Velero
> to finish a backup before terminating in case it takes more than the default, previously immutable, 30 seconds to
> perform a backup.

Its drift script is at `<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run local commands such as `git`, `helm template`, or `helm lint`;
there is no Kubernetes cluster, and you may not use gh, a browser, or curl. End with the report the skill describes,
as your final message.
