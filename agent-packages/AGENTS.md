# Editing the packages in this directory

Several packages here are the same skill written once per programming language or test framework. When you edit one
of them, make the matching edit in every sibling where it applies, in the same change, so the set does not drift.

Doc-comment packages, one per language (the section numbering is shared, so a rule that moves in one moves in all):

- `javadoc-authoring`
- `jsdoc-authoring`
- `godoc-authoring`
- `rustdoc-authoring`
- `pythondoc-authoring`

Test authoring, one reference file per role a library plays in a test (engine, assertions, doubles, property-based,
structural, mutation), grouped by ecosystem under `test-authoring/.apm/skills/test-authoring/references/`:

- `java/`: `junit5.md`, `junit5-assertions.md`, `junit4.md`, `junit4-assert.md`, `assertj.md`, `truth.md`,
  `hamcrest.md`, `mockito.md`, `jetcheck.md`, `archunit.md`
- `python/pytest.md`
- `go/`: `testing.md`, `testify.md`
- `rust/libtest.md`
- `javascript/`: `jest.md`, `vitest.md`, `node-test.md`
- `mutation-tools.md`, one table for every ecosystem

The rules for editing the skill's text, and the script that checks the mechanical ones, are in
`test-authoring/AGENTS.md` and `test-authoring/scripts/check-skill.sh`. A rule that holds in every language belongs in
the shared body (`test-authoring/.apm/skills/test-authoring/SKILL.md`), not in one reference file. A file carries one
role: an engine file says nothing about which assertion prints the operands, and an assertion file says nothing about
how a case is named. A file covers one major version and assumes the latest minor; two majors get two files only where
a test is written differently under each. Every failure message a file quotes is measured and recorded in
`research/test-authoring/framework_output.md`.
