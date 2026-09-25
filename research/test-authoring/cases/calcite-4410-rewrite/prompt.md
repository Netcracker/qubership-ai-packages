Read the skill at <skill>/SKILL.md in full, open its reference files under the `references/` directory next to it
where the skill says to, and follow it. Do not load any other copy of test-authoring.

The last commit of this repository fixes how the SQL validator expands a common column of `JOIN ... USING` and
`NATURAL JOIN` when names are matched case-insensitively, and adds tests for it to
`core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java`. Rewrite the tests that commit added according to
the skill. Do not change the production code, and do not commit. You may run the build; do not use gh, a browser, or
curl. End with the message you would leave for the author of the pull request: what you changed in the tests and why,
and anything you propose and did not do.
