# Trial: one axis sharded over a large change

The trial behind sharding in `adversarial-code-review`, run in November 2026 on a pull request that added about 19000
lines of code, most of them to one package. The review itself is not published here; this page records the
measurements that the package README cites.

## What the unsharded review read

The review first ran at profile `high`, one subagent per axis. Asked afterwards which ranges of the large package they
had read, the correctness, comments, and simplicity subagents named between 0 and 2% of its added lines: each had
followed the description into a few files and stopped there.

## How the code was split

Before the second pass, several planners proposed a split of the package:

- the three axis subagents, asked how they would split the code: their plans were costly to obtain and rested on the
  little they had read;
- one fresh planner with the declarations map: six shards with the contracts between them;
- three planners on the cheapest model, each with another question. The one that grouped files by the declarations
  they name produced the best partition; the one that ranked by risk without reading the code invented a fact about
  a file. The seams the cheap planners named were worth taking as a union.

The final plan had six shards of 1500–3500 lines and a list of seams, which became the skill's two planners
(structure and risk) and its seam reviewer.

## Result

The correctness axis then ran as six shard subagents and one seam reviewer. They reported 20 findings; the verifier
kept 18 as defects and 2 as questions, 17 of them new to the review. 7 new findings were `major`. The sharded pass
used about 1.65 million tokens, and the verifier about 0.19 million.
