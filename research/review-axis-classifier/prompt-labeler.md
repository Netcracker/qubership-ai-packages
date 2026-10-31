You are building ground truth for an experiment: which review axes a pull request needed attention on, as submitted.

Research directory: DIR = <absolute path of research/review-axis-classifier>

Read `DIR/prompt-rubric.md` first: it defines 16 axes, the labels 0/1/2, and the review plan. Then, for each PR key assigned to you below:

1. Read `DIR/cache/views/<key>.md` (description, files, commits, reviews, review comments, conversation), `DIR/cache/views/<key>.initial.diff` (the version as submitted: the thing being labeled), and `DIR/cache/views/<key>.final.diff` (the version after review, for hindsight). Large diffs: read the parts that matter, not necessarily every line.
2. Use hindsight: what reviewers asked for, and what changed between the initial and final diff, is strong evidence that an axis needed attention. But reviewers miss things: also judge yourself what a careful focused reviewer would have raised on the initial version (for example, a JDK version bump whose docs still list the old version, a new property with no docs, a hot-path change with no benchmark).
3. Check repository context when it decides a label: a local clone of the PR's repository (read-only; never checkout, commit, or change anything in it) holds the base commit. Use `git -C <clone> show <base>:<path>`, `git -C <clone> grep -n <pattern> <base> -- <paths>`. Clones: CLONES. The base sha is in the view header (short form; `git -C <clone> rev-parse <short>` resolves it). For calcite the Jira issue CALCITE-NNNN may help: `curl -s https://issues.apache.org/jira/rest/api/2/issue/CALCITE-NNNN?fields=summary,description`.
4. Do not post anything to GitHub or Jira. Read only.

Write one JSON file per PR to `DIR/labels/LABELDIR/<key>.json` with exactly this shape:

{"key": "<key>",
 "summary": "<one sentence: what the PR does>",
 "axes": {"<axis id>": {"label": 0|1|2, "mandated": true|false, "finding": true|false, "evidence": "<one or two sentences: the review comment, later commit, or file:line that justifies the label; for 0 say why not touched>"}, ... all 16 axis ids ...},
 "plan": {"mode": "single"|"split", "groups": [["axis", ...], ...], "why": "<one sentence>"}}

`mandated` = the kind of change requires this check by the "mandated when" column. `finding` = the initial version has a concrete defect or omission on this axis (from hindsight or your own judgment). Label 2 iff mandated or finding (use judgment: a mandated check on a trivial one-liner may be 1). For `plan.groups` in single mode give one group with all axes labeled 2.

Be calibrated, not generous: most PRs should have most axes at 0. When done, reply with one line per PR: key and the axis ids labeled 2.
