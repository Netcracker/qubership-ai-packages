# Case: pgjdbc#4420, a test-only change whose tests guard several sites

The input is the description of [pgjdbc/pgjdbc#4420](https://github.com/pgjdbc/pgjdbc/pull/4420) as posted, 365
words for a change that only adds and removes tests, with the diff and the task to rewrite it. The new tests guard
seven production sites, and the diff does not say which test guards which: the posted text carries that pairing as a
table of mutants. It also carries a `git grep` that found no test, the mutation run itself, and a `./gradlew` command.
The case is the counterweight to the cases that cut test narration: the pairing of tests to sites stays, its framing
as a mutation run goes.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Verification, which test guards which site, a test removed or narrowed;
  What each paragraph must earn: the result not the route, length), §7
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The pairing of tests to sites stays** (`site_mapping_kept_4420`). At least three of `addBatch`,
   `QueryWithReturningColumnsKey`, `BaseQueryKey`, `executeCachedSql`, `CachedQueryCreateAction` each share a line
   or a sentence with a test or a case.
2. **The removed tests are named** (`removed_tests_named_4420`). `testBatchEscapeProcessing` and `escapeProcessing`.
3. **No route** (`no_route_4420`). No mutant, mutation run, "I checked", "I applied", or "I broke". The `git grep`
   that backs "no test turns escape processing off" may stay: it is the check of a claim about code outside the
   diff.
4. **No test command** (`no_test_command`).
5. **Short** (`prose_at_most_330_words`). At most 330 words outside fenced blocks, tables included.
6. **No tool footer** (`no_tool_footer`). The posted text ends in a "Generated with" line; the rewrite drops it.

## Running it

As in [the cases README](../README.md). `controls/as-posted.md` is the description as posted.
`controls/short-draft.md` is a rewrite that dropped the pairing. `controls/removed-tests-dropped.md` is
`controls/as-posted.md` with the lines that name the removed tests deleted. `controls/main-haiku.md` is a Haiku
draft, at effort medium, written under the skill at `main` 4ef3f8c.

`SKILL.md` quotes this case's `git grep` sentence and the `| Site | Guarded by |` shape, so the runs are open-book:
they show the skill's examples are followed, not that the rule carries to a pull request it does not quote.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. There are no
baselines for this case.

| Run | Pairing kept (1) | Removed tests named (2) | No route (3) | No command (4) | Words (5) | No footer (6) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes | passes: 273 | passes |
| Opus r2 | passes | passes | passes | passes | passes: 211 | passes |
| Haiku r1 | passes | passes | fails: "Each row below was checked by breaking that one site" | passes | passes: 319 | passes |
| Haiku r2 | passes | passes | passes | passes | passes: 330 | passes |
| `controls/as-posted.md` | passes | passes | fails: "I checked" | fails | passes: 319 | fails |
| `controls/removed-tests-dropped.md` | passes | fails: no `testBatchEscapeProcessing` | fails: "I checked" | fails | passes: 265 | fails |
| `controls/short-draft.md` | fails: only `addBatch` | passes | passes | passes | passes: 105 | passes |
| `controls/main-haiku.md` | passes | passes | fails: "I checked" | fails | fails: 393 | passes |

The script passes Haiku r1 on check 3: "checked by breaking" is not one of its markers. Haiku r2 sits exactly at the
330-word limit.
