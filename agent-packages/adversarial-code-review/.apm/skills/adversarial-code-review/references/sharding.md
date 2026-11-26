# Sharding an axis

An axis that runs sharded is held by one subagent per shard of the code, and one more subagent, the seam reviewer,
checks the contracts between the shards. *Plan the subagents* in `SKILL.md` decides which axes run sharded; this file
says how the shards are planned, what each subagent is told, how every axis reports what it read, and how unread code
gets a second reader.

## Plan the shards

1. Read the code map, `<work>/shards/map.md`, which *Plan the subagents* in `SKILL.md` writes for every change.
2. In the first wave, with the measurement subagent, spawn two planners on the cheapest model the harness offers, each
   with the planner's brief below: one with the structure question, one with the risk question.
3. When both reply, write `<work>/shards/PLAN.md` yourself, in the format below:
   - The structure plan is the partition; the risk plan gives the risk order and seams. Where only one planner
     replied, its plan is the partition; where neither did, split by directory and file size from `map.md`.
   - A file that holds two parts which serve different shards, such as a parser and the printer that must round-trip
     what it parses, is split by line range.
   - Keep each shard between 1500 and 3500 added lines of code, tests not counted. Merge a smaller shard into the
     shard it shares the most references with; split a larger one along its least-referenced boundary.
   - Assign every code file of the map, every test of its *Tests* list, and every code file of its *Deleted* list. A
     test goes to a shard that holds a code file whose declarations the test uses, the one first in the risk order
     where there are several, and a test that uses none to the shard of the nearest directory. A deleted file, and a
     code file that only removes lines, goes to the shard of the nearest directory. Code that does not run in the
     product, such as a command-line tool for developers or a benchmark, may form a shard of its own, last in the risk
     order. Only the request's exclusions leave code out.
   - Take the union of the seams both planners name, and drop one that names no declaration or line range, or does not
     cross two shards of the final partition. Add a seam for every file split by line range. Then, for every pair of
     final shards whose files use each other's declarations in `map.md`, and that no seam crosses yet, add a seam. It
     names up to five declarations: those used by the most files of the other shard. A seam crosses every pair of shards
     it touches. The references in `map.md` are a lower bound: they leave out a type named only in a signature or a
     field, the files a reference list counts as "and N more", and the calls a declaration lists as not attributed.
     Before deciding a pair has none, search the other shard's files in the diff for the names of the first shard's
     declarations. Where `map.md` has no declarations, add one seam for every pair of shards whose files share a parent
     directory, naming the files on each side. List the seams in the risk order of the first shard each touches.

## Plan format

```markdown
| Shard | Files and line ranges | Added lines (code, tests) | Risk |
| --- | --- | --- | --- |
| csv-export | src/export/csv.py, src/export/quote.py 1-180, tests/export/test_csv.py | 1480, 320 | high: writes user data |

Seams:
1. <the contract>: <what one shard produces> against <what another reads>, in <file:symbol> and <file:symbol>.
```

## Planner's brief

> You plan how to split the review of a large change between several reviewers, before the review starts. Each reviewer
> reads one shard of the code line by line, so code that has to be understood together stays in one shard. The code map
> is `<work>/shards/map.md`; the change is `git -C <workspace> diff <base>...<head>`; the description and discussion are
> in `<work>/input.md`. <question> Do not review the code and do not write findings.
>
> Write `<work>/shards/plan-<question name>.md`: the shards (each with its files and line ranges, its added lines of
> code and of tests, and the contract that ties its files together), the seams (contracts between two shards where a
> defect would be invisible to each shard alone), and the shards ordered by the number of undiscovered `major` defects
> you expect, with one sentence why. Every boundary and every seam names the declarations or line ranges it rests on,
> from `map.md` or the diff, that you checked; leave out one you cannot tie to either. Reply with the number of shards
> and seams.

The two questions:

- **structure:** "Group files by the declarations they share: from `map.md`, put files that use each other's
  declarations in one shard, and name the declarations that cross shards. `map.md` lists the uses sb resolved; a type
  named only in a signature or a field, and a call it did not attribute, are not there, so check the diff for them."
- **risk:** "Start from what the change can break: read the description and the discussion, find in `map.md` and the
  diff the code that decides security, data, or every request, and keep each such part whole in one shard."

## Coverage format

Every axis subagent, single, grouped, shard, or retry, writes what it read in this format, one section per axis it
holds; the seam reviewer writes one section per seam:

```markdown
## correctness

- src/export/csv.py: all
- src/export/quote.py: 1-90, 140-180
- src/export/cli.py: none
```

List every changed file the axis is responsible for. `all` means every added range of the file; ranges are line
numbers at the reviewed head.

## Shard brief

Give a subagent that holds one axis over one shard this brief:

> You are one reviewer of a pull request, responsible for the `<axis>` axis over the shard `<shard>` only. Read
> `<skill dir>/references/axes/<axis>.md` and `<skill dir>/references/finding-rules.md` first and follow them. The
> shard's files and line ranges are in `<work>/shards/PLAN.md`: read every function in them fully, and the tests that
> exercise them. Read a deleted file at `<base>` (`git -C <workspace> show <base>:<path>`), and its former callers at
> the head. Read outside the shard to understand a caller or a type, but report findings only about code in the shard;
> where `PLAN.md` lists seams, they belong to another reviewer. The review input is `<work>/input.md`; the code at the
> reviewed head is in `<workspace>`; the change is `git diff <base>...<head>`. Where `<work>/measure/` exists, its
> `README.md` says what was measured. Out of scope: `<exclusions or "nothing">`. To run anything, add your own worktree
> first (`git -C <workspace> worktree add <work>/axes/<name>-wt <sha>`) and run there, never in `<workspace>`. Where a
> `major` finding can be shown by a test, show it in your worktree and put the test in `reproducer`. Write your findings
> as a JSON array of finding records (the `finding` definition in `<schema>`, without `id` and `class`) to
> `<work>/axes/<name>.json`, and `[]` if there are none, and what you read to `<work>/axes/<name>-coverage.md`, in the
> coverage format of `<skill dir>/references/sharding.md`. Do not edit the workspace, run nothing that writes outside
> `<work>`, and post nothing. Reply with the number of findings per severity and the skills you loaded.

`<name>` is `<axis>--<shard>`.

## Seam reviewer's brief

One seam reviewer runs per review, for all the sharded axes, in the same wave as the shards:

> You are one reviewer of a pull request, responsible for the seams between the shards in `<work>/shards/PLAN.md`, for
> the axes `<sharded axes>`. Read `<skill dir>/references/finding-rules.md` and the file of each of those axes under
> `<skill dir>/references/axes/` first, and follow them. For each seam, read both sides fully enough to state the
> contract precisely, then look for inputs on which the two sides disagree. Prefer a differential test to reading: the
> same input through both sides, such as a serializer and the parser that reads its output, or one request sent whole
> and in parts. Report a finding at the side that should change, with `axis` set to the axis it belongs to. The review
> input is `<work>/input.md`; the code at the reviewed head is in `<workspace>`; the change is
> `git diff <base>...<head>`. Out of scope: `<exclusions or "nothing">`. To run anything, add your own worktree first
> (`git -C <workspace> worktree add <work>/axes/seams-wt <sha>`) and run there, never in `<workspace>`. Write your
> findings as a JSON array of finding records (the `finding` definition in `<schema>`, without `id` and `class`) to
> `<work>/axes/seams.json`, and `[]` if there are none, and what you read to `<work>/axes/seams-coverage.md`, in the
> coverage format above, one section per seam. Do not edit the workspace, run nothing that writes outside `<work>`, and
> post nothing. Reply with the number of findings per seam and severity, and the skills you loaded.

## Retry the unread ranges

*Check what the axes read* in `SKILL.md` decides which axis gets a second reader. Cut its unread ranges into
assignments of at most 3500 lines, keeping the ranges of one file together where they fit, and give each assignment
the shard brief with its ranges written in place of the `PLAN.md` shard, and `<name>` set to `<axis>--retry-<n>`, so
that no file of the first pass is overwritten. A retry has no minimum size, no plan, and no seam reviewer.
