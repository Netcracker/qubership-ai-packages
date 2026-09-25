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

## Testing a skill against its cases

A skill can have regression cases under `research/<package>/cases/<case>/`: the input in `prompt.md` (frozen notes, or
the task for a repository pinned at a tag), the output of each model under `<model>/` (`result.md`, or `result.diff` for
a change to a repository), and a `README.md` with the checks the output has to pass and the way to run the case. The
cases stay out of `agent-packages/<package>/`, because `apm install` copies the whole package directory into every
consumer's `apm_modules/`.

- **Run the skill as a consumer gets it.** Copy the skill at the revision under test to a directory outside the
  checkout, with `git archive <rev> <path to the skill> | tar -x -C <dir> --strip-components=<depth>`, and start the
  session outside the checkout too. A session that reads the skill inside the checkout also loads the `CLAUDE.md` and
  `AGENTS.md` files on the way, and a drafting agent should not see instructions for editing the skill.
- **A change to a skill is a change to a file under `agent-packages/<package>/.apm/skills/<skill>/`**, the `SKILL.md` or
  a reference file. It re-runs every case of that skill, and the results go into the same commit as the change, so that
  every commit holds results generated from its own skill and the diff of the result shows what the change did to each
  case. A change to the package README, `apm.yml`, or an `AGENTS.md` is not a change to the skill. A change to a case's
  checks re-runs that case's snippet over the committed results, not the models; a change to a case's `prompt.md`
  re-runs that case.
- **Each result records the skill it came from.** Write `scripts/skill-tree.sh <skill directory> <rev>` (or, before
  the skill is committed, `scripts/skill-tree.sh <skill directory>`) to `<model>/skill-tree` beside the result. Before
  re-running a case, compare that file with `git rev-parse HEAD:<skill directory>`: where they match, the result is
  current, and a rebase, an amend, or a regrouping of commits that leaves the skill unchanged needs no new run. A
  reviewer checks the same way, without reading the history.
- **The commit message says which checks each result fails,** not only how long it is. Grade every check of the case
  README by reading the result; the snippet counts only the checks a marker can catch, and a result that passes the
  snippet can still fail a check it does not count. An edit that improves one case and makes another worse says so.
- **One run per cell is noisy.** The same model on the same skill has produced reports whose length differed by
  nearly a factor of two. Before calling a change a fix or a regression, run the cell the conclusion rests on at
  least twice.
- **A run costs money.** One Opus run of a case costs about a dollar at list API prices, most of it in writing the
  skill into the prompt cache. A full pass over several cases and three models costs several dollars; say what you
  ran in the commit message.
- **Before publishing,** run `make check` and `make check-descriptions`, and run `final-review` in a fresh session
  over the change.
