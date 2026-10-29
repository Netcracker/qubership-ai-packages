Read the skill at <skill>/SKILL.md in full, open its reference files under the `references/` directory next to it
where the skill says to, and follow it. Do not load any other copy of test-authoring.

The last commit of this repository moves the kind test harnesses from manifests applied with `kubectl apply` to a Helm
test-stand chart, and adds no tests for the move. Write the test plan this change owes, according to the skill: each
test or run, at which level, from which state, with which inputs, and what it shows. There is no kind cluster or
Docker daemon here, so do not try to run the harnesses. Do not change any file, and do not commit. Do not use gh, a
browser, or curl. End with the plan as the message you would leave for the author of the pull request.
