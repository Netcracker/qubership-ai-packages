# Case: plan round 2 of a review of Netcracker/qubership-authz-agent#205 from its round 1

A planning case for `adversarial-code-review`: given the state of a review at the moment it plans its subagents, which
axes it shards, which run single, which go into groups, and what it tells the shard planners and the seam reviewer. It
does not run a review. Use it to try another wording of *Plan the subagents* or *Plan from the earlier round* and see
the plan it produces, without paying for the review.

The change is [Netcracker/qubership-authz-agent#205][pr], about 22,500 added code lines. Round 1 reviewed it at
`c8315157` (tag `review/pr-205/round-1` in `vlsi/qubership-authz-agent`); the author then fixed its findings in waves,
and round 2 reviewed `1872c610` (tag `review/pr-205/round-2`) against base `e2c7029e` (tag `review/pr-205/base`).

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/205

## Files

- `input/input.md`: round 2's collected input. `<work>` stands for the round directory, which is not included;
  `<executable specification>` is the legacy service's executable specification and golden suite, which lives outside
  the repository.
- `input/map.md`: the code map of round 2 (`scripts/code-map.py`).
- `input/previous-review.json`: round 1's `review.json`, the `<previous>` of round 2: 92 findings, 27 `major`.
- `input/previous-PLAN.md`: round 1's shard plan of its sharded correctness pass.
- `input/previous_findings.json`: round 2's recheck of the round-1 threads.
- `outcome/round-2-review.json`: what round 2 found, 130 findings, 23 `major`. Grade a plan against it.
- `outcome/round-2-hot-files.txt`: the code files the branch's own commits between the rounds changed, with the
  number of commits, by the command in *Plan from the earlier round*. Grade check 4 against it.
- `prompt-plan.md`: the brief a planning run gets. Make a work directory with `input.md` and `shards/map.md` copied
  from `input/`, and replace `<workdir>` with it; replace `<previous-review>` with `input/previous-review.json`,
  `<prevfindings>` with `input/previous_findings.json`, `<git>` with a checkout of the repository that has the three
  tags fetched, and `<skill>`, `<prevhead>`, `<head>`, `<base>`, `<out>`, and `<request>` as their names say. Hide the
  variant's name from the run (a symlink with a neutral name works).

## How round 2 ran, and who found its `major` findings

The skill's own plan for round 2 (2.6.0, profile `medium`) sharded correctness and tests into 9 shards with a seam
reviewer, ran change description, compatibility, and comments single, and put security and performance in a group of
eight. The owner then asked for security and performance to run single, for two correctness reviewers that compared
the change with the executable specification's goldens, and for the seam reviewer to compare the access check with the
filter. Round 2 ran that amended plan.

| Subagent | `major` |
| --- | --- |
| correctness shards | 9 |
| seam reviewer (check against filter) | 2 |
| reviewers against the goldens | 1 new, 1 also found by a shard |
| performance, single | 3 |
| security, single | 0 |
| tests, sharded (all in the filter shard) | 2 |
| group-1 (change reach 3, reliability 1) | 4 |
| change description, compatibility, single | 1 each |

14 of the 17 `major` findings in code files sit in the 30 files the branch's own commits between the rounds changed
most (of 233 code files).

## Checks

A plan passes where:

1. Correctness and tests are sharded. Tests found only `minor` findings in round 1, where it ran single; sharded in
   round 2 it found 2 `major`.
2. Performance and security each run single or sharded, not in a group: round 1 found a `major` in each (F1, F2).
3. Change description and compatibility run single: each had `major` findings in round 1 and found one in round 2.
4. The risk planner's brief ranks the shards that hold the hot files first, and gives no reason for the list.
5. `PLAN.md` gets a seam between the access check and the filter, stated as a contract (the filter admits no more than
   the check), not as an earlier defect.
6. No brief, `input.md` addition, or `PLAN.md` line names a round-1 finding id, class, or family.
7. No axis runs shallower than in a plan made by the same wording with `input/previous-review.json` left out: sharded
   above single, single above grouped. Make that plan too and compare.

## Runs

| Skill | Plan | Checks |
| --- | --- | --- |
| 2.6.0 (no earlier-round planning) | correctness, tests sharded; security, performance in a group of eight | 1, 3, 6, 7 |
| 2.7.0 draft that reordered the axes by yield | correctness, performance sharded; tests grouped | 2, 3, 4, 5, 6 |
| 2.7.0 (the earlier round adds single subagents and takes nothing away) | correctness, security sharded; tests, compatibility, change description, comments, intent and scope, performance single; 10 subagents | 2, 3, 4, 5, 6 |

In the 2.7.0 run, step 1 of the order, which judges the two axes most likely to find a `major` from the description
and the diff, chose security over tests for the second shard, so tests ran single; check 7 was not run for it. The
skill now says that the order does not read `plan.md`, which that run had read before choosing. Round 2's security, single, read 14%
of the added code and found nothing, so whether a sharded security would have found more is unknown. Which shardable
axis gets the second shard is the open question this case leaves.
