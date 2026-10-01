Read the skill at <skill>/SKILL.md in full, open its reference files under the `references/` directory next to it
where the skill says to, and follow it. Do not load any other copy of test-authoring.

The last commit of this repository changes which errors frictionless reports when a table's header does not match
its schema, and adds no tests. Write the tests that change owes, according to the skill. Do not change the production
code, and do not commit. You may run the tests: `uv` is installed, and a Python 3.11 environment can be made under
`.python/`, which git ignores. Do not use gh, a browser, or curl. End with the message you would leave for the author
of the pull request: which tests you added or changed and why, and anything you propose and did not do.
