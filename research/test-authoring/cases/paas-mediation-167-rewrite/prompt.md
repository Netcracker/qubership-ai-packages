Read the skill at <skill>/SKILL.md in full, open its reference files under the `references/` directory next to it
where the skill says to, and follow it. Do not load any other copy of test-authoring.

The last commit of this repository changes only tests: it replaces the tests of how `CreateRoute`, `UpdateOrCreateRoute`,
and `DeleteRoute` in `service/internal/kubernetes/route.go` report the error the API server returned, in
`service/internal/kubernetes/route_test.go`, with tests that go through those methods and assert error semantics.
Rewrite the tests and helpers that commit added or changed according to the skill. Do not change the production code,
and do not commit. You may run the build; do not use gh, a browser, or curl. End with the message you would leave for
the author of the pull request: what you changed in the tests and why, and anything you propose and did not do.
