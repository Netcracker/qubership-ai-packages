"""The system prompt every generative classifier gets (Claude through `claude -p`, GPT through `codex exec`)."""
from common import AXES, path

RUBRIC = open(path("prompt-rubric.md")).read().split("## Review plan")[0]
SYSTEM = f"""You route pull request reviews. Given a pull request as submitted (title, description, files, possibly truncated diff), decide for each review axis how much attention a reviewer must pay, and how to organize the review.

{RUBRIC}
Label 2 when the kind of change mandates the check, or when the pull request likely has a defect or omission on that axis; 1 when touched but a glance suffices; 0 when not touched. Be calibrated: most axes of most pull requests are 0 or 1.

Review plan: "single" when one reviewer can cover the required axes (small or cohesive change); "split" when focused subagents should each take a group of axes.

Reply with JSON only, no prose, exactly:
{{"axes": {{"<axis id>": {{"label": 0|1|2, "p_required": <probability 0..1 that the axis deserves label 2>}}, ... all 16 ids: {", ".join(AXES)} }},
 "plan": {{"mode": "single"|"split", "groups": [["axis id", ...], ...]}},
 "why": "<at most two sentences naming the axes labeled 2 and why>"}}"""


def user_prompt(pr):
    import json
    return "Pull request:\n" + json.dumps(pr, indent=1)
