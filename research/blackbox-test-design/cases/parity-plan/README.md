# parity-plan

A team porting a tax engine has a green parity suite, a 94% mutation score, property tests, and complete pairwise
coverage, and gets one more round of at most 50 requests to a shared legacy stand before cutover. `STATUS.md` holds a
comparator that erases array order, nulls, number spelling, and error messages, decisions sourced from the port team's
own design doc, and two hand-written exception lists. The plan should find what the green measures cannot see and spend
the round on it.

The prompt is in `prompt.md`; the files it names are under `files/`. Run it from the repository root with
`research/blackbox-test-design/cases/run-case.sh research/blackbox-test-design/cases/parity-plan
<with-skill|without-skill> <model>`, then grade both arms with `cases/grade-prompt.md`.

## Checks

- Explains that the mutation score, the property-test generators and/or the pairwise coverage measure the port against
  itself, so they cannot reveal legacy rules the port lacks
- Works out from comparator.yaml at least two concrete differences the parity suite cannot see (line order, null versus
  absent, number scale or notation, error message text) and proposes a way to ask around them
- Treats the decisions sourced from the design doc (D3, D12, D15, D22) as unverified against legacy and gives them
  requests
- Treats a hand-written exception list (D7 rounding categories or D21 jurisdictions) as a possible footprint of a
  general rule and proposes requests that tell the rule from the list
- Includes structural relations over rule uploads: reordering rules or groups, adding an irrelevant rule, duplicating,
  or splitting a rule
- Asks what happens on an identity collision (two rules or groups with the same name, a reused name across
  jurisdictions)
- Uses the legacy platform (Java, Jackson, PostgreSQL) to propose concrete hypotheses (e.g. trim semantics, BigDecimal
  scale, Jackson coercion, column length limits)
- Proposes field state or spelling variants (absent / null / empty / blank, or number spellings) for at least one input
  field
- The round is at most 50 requests, tiered or ordered so that a budget cut drops the least informative requests first
- Brackets the round with control replays of already-answered requests to detect drift, and asks to record the legacy
  build or version
- Keeps the shared stand safe: rule uploads go to jurisdictions no recorded answer or other team depends on, or existing
  configuration is exported and restored
- Labels unverified expectations about legacy as hypotheses rather than stating them as fact
