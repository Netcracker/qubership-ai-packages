You are the orchestrator of the `adversarial-code-review` skill, at one moment of a review: the input is collected,
the earlier review threads are rechecked, and the code map is written. Your only job now is to plan the subagents.
Do not review code, do not spawn subagents, do not edit anything outside `<out>`.

The skill is in `<skill>`: read `<skill>/SKILL.md` and `<skill>/references/sharding.md` and follow them for the steps
*Choose the axes*, *Plan the subagents* (and any step it says to do before ordering the axes), and the parts of
*Plan the shards* that decide what each planner's brief contains and which seams `PLAN.md` gets. Treat earlier steps as
done, with the files below as their output.

The request: "<request>"

Review state:
- `<work>` is `<workdir>`: `input.md` there is the collected input; `shards/map.md` is the code map (read its first
  table and skim the rest; do not read all of it).
- `<previous>` is `<previous-review>`.
- This round's `previous_findings` (the recheck of the earlier threads) are in `<prevfindings>`.
- Git: `<git>`; the earlier round's head is `<prevhead>`, this round's head is `<head>`, base `<base>`.

Write `<out>/plan-output.md` with:
1. The profile and why.
2. Every axis in your final order, with whether it applies, and how it runs: sharded, single, or `group-N`; the
   `reason` you would record for it in `axes`.
3. The number of axis subagents (shards counted as one per sharded axis), and what made it differ from the profile's
   row, if it does.
4. For each shard planner: the exact text you would add to its brief beyond the template, if any.
5. The seams you would add to `PLAN.md` beyond what the planners propose, each with its contract.
6. Anything you would add to `input.md` or to any reviewer's brief beyond the templates, verbatim.
7. The order in which you would recheck the earlier threads, if the skill says anything about it.
8. Any file the skill tells you to write at this point (such as a plan file), in full, as an appendix.

Reply with items 2 and 3 only, in under 30 lines.
