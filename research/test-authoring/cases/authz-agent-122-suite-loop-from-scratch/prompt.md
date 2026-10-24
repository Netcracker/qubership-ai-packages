Read the skill at <skill>/SKILL.md in full, open its reference files under the `references/` directory next to it
where the skill says to, and follow it. Do not load any other copy of test-authoring.

The last commit of this repository changes how `make e2e-suite` and `make parity-suite` wait for the suite Job to
start, among other things, and adds no tests. Write the tests that change owes, according to the skill. Do not change
the production code, and do not commit. You may run tests: `bash`, `bats`, `make`, and Go are installed. There is no
Kubernetes cluster, and you may not create one: do not run kind, docker, or a kubectl or helm that reaches a cluster.
Do not use gh, a browser, or curl. End with the message you would leave for the author of the pull request: which
tests you added or changed and why, and anything you propose and did not do.
