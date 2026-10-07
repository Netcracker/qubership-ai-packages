# Editing the blackbox-test-design package

These are instructions for changing the skill under `.apm/skills/blackbox-test-design/`, not for using it to design
questions.

## The skill serves every kind of reference

An edit drawn from one project has to hold for the others. Before an edit, check the new text against each kind of
reference by reading where no case covers one:

- a legacy service behind HTTP, queried on a shared stand, with a parity suite and a normalizing comparator;
- a vendor binary or library run locally with a call budget and no source;
- a third-party API with rate limits and documentation that is silent on edge cases;
- an executable spec checked against a large set of recorded goldens, with mutation and pairwise measures of its own;
- shadow or replayed production traffic diffed between the old and the new system.

## What an edit owes

- **A rule moves in all of its places in the same change.** A technique can sit in its section, in the checklist, in the
  worked example, in `references/idioms.md`, and in the package `README.md`. Run `bash
  agent-packages/test-authoring/scripts/check-skill.sh agent-packages/blackbox-test-design --index` to list every line
  that cites a section before editing it.
- **The split with `test-authoring` stays in both packages.** This skill decides which questions to ask;
  `test-authoring` governs the test that carries each one. The split is stated in four places: the paragraph near the
  top of each `SKILL.md`, the "Pairs with" section of this package's `README.md`, and the `blackbox-test-design` entry
  under "Pairs with" in `test-authoring/README.md`. An edit that moves the line edits all four.
- **A description edit re-runs the trigger eval.** The description is the only thing that loads this skill: the package
  has no instructions file. Run the harness in `research/blackbox-test-design/trigger/` on at least two models, keep the
  description under the limit `make check-descriptions` enforces, and commit the results with the change. A query that
  fails goes into the commit message with its rate.

The behavioral cases are under `research/blackbox-test-design/cases/`. They follow `agent-packages/AGENTS.md`, under
"Testing a skill against its cases", with one difference in layout: each case runs twice, with the skill and without it,
so a result goes to `results/<arm>-<model>/` rather than `<model>/`. Run a case with `cases/run-case.sh`, which copies
the skill from the working tree, and grade both arms with a separate agent given `cases/grade-prompt.md`. A change to
this skill re-runs the arm with the skill in every case and commits the results with it; a change to `test-authoring`
re-runs both arms. `skill-tree` and `skill-tree-test-authoring` in each result show which trees produced it. The
`probe-vendor-jar` case keeps the source of its jar under `src/`, and its `build.sh` compiles the jar into the session's
directory; the source is the answer key, and the repository holds no binary.
