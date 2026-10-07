# spec-proven

A team's executable spec matches 5000 goldens, has a 98% mutation score over its knobs, and complete pairwise coverage
over its own 14 dimensions, and their lead calls it proven. The answer should explain why those measures cannot find a
rule the spec lacks, without claiming the spec is right or wrong, and say what to add.

The prompt is in `prompt.md`; the files it names are under `files/`. Run it from the repository root with
`research/blackbox-test-design/cases/run-case.sh research/blackbox-test-design/cases/spec-proven
<with-skill|without-skill> <model>`, then grade both arms with `cases/grade-prompt.md`.

## Checks

- Says the spec is not proven and that the legacy stand should keep being asked
- Explains that the mutation score and the pairwise coverage are measured over the spec's own knobs and dimensions, so
  they cannot find rules the spec does not express
- Points out that goldens may not separate outcomes or may be hidden by the comparison (weakly pinned decisions,
  normalization)
- Proposes sources of questions independent of the spec (input format or grammar, platform idioms, raw input features)
- Proposes structural metamorphic relations, including reordering or adding irrelevant rules
- Proposes probing evaluation order or laziness through side channels or deliberate failures
- Proposes an independent second model (isolated from the spec) with differential testing
- Mentions that the legacy version or build should be recorded or that it may drift
- Gives a concrete, prioritized list of additions rather than only general advice
- Proposes turning surviving mutants or unpinned decisions into questions for the legacy stand
- States a stopping rule in terms of questions and answers (for example no new decisions in a round, or a bound from
  random agreement), not in terms of a score on the spec
