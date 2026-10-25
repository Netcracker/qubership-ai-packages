# Editing the packages in this directory

A package that hands wording to another skill names the rule, not one language's skill: "wording, tense, sentence
length, and dialect belong to the developer-style skill of the language the text is written in
(`english-developer-style` for English)", not "wording belongs to `english-developer-style`". The same package
installs beside `russian-developer-style` and `french-developer-style`, and a hard-coded English skill sends a
Russian or French text to the wrong one.

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
a change to a repository: the change is the skill's output, and the files it touches belong to the repository, not to
the case), and a `README.md` with the checks the output has to pass and the way to run the case. The cases stay out of
`agent-packages/<package>/`, because `apm install` copies the whole package directory into every consumer's
`apm_modules/`.

- **Run the skill as a consumer gets it.** Copy the skill at the revision under test to a directory outside the
  checkout, with `git archive <rev> <path to the skill> | tar -x -C <dir> --strip-components=<depth>`, and start the
  session outside the checkout too. A session that reads the skill inside the checkout also loads the `CLAUDE.md` and
  `AGENTS.md` files on the way, and a drafting agent should not see instructions for editing the skill.
- **A change to a skill re-runs the cases whose `## Skill parts` it touches.** A change to a skill is a change under
  `agent-packages/<package>/.apm/skills/<skill>/`. The frontmatter and the text above the first numbered section count
  for every case; a checklist item, a table row, or a worked example counts as the section whose rule it restates.
  Commit the results with the change, and say in the pull request which cases ran and why the others did not. A change
  to a case's checks re-runs its snippet over the committed results; a change to its `prompt.md` re-runs the case.
- **Before a version bump, run every case** on every model it has results for, and commit the results. A model with no
  results yet runs every case.
- **Every case declares its `## Skill parts`:** the `SKILL.md` sections and reference files whose rules its checks
  test, with a line of its own for each other skill the case runs with. Find each rule in the skill text, not from the
  section number the check cites. Update the declarations in the same commit that adds a check, renumbers the
  sections, or finds a check testing a part the list omits.
- **Write `scripts/skill-tree.sh <skill directory> [<rev>]` to `<model>/skill-tree` beside each result.** A result whose
  file matches `git rev-parse HEAD:<skill directory>` is current and needs no new run.
- **Grade every check by reading the result, not by the snippet's count,** and say in the commit message which checks
  each result fails, which cases improved or got worse, and what you ran.
- **Commit results and draw conclusions from the target models (Opus, Sonnet), at least two runs per cell.** Haiku is
  fine for iterating on wording against the checks a marker can catch; revert an edit that helps Haiku and hurts a
  target model.
- **Before publishing,** run `make check` and `make check-descriptions`, and run `final-review` in a fresh session
  over the change.
