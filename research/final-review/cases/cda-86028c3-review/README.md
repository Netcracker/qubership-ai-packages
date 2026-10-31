# Case: review a skill edit whose added rule already says where it stops

The noise control for [`cda-4f69810-review`](../cda-4f69810-review/). The input is commit `86028c3` of this repository,
one commit on top of `4f69810`: it makes `change-description-authoring` lead a pull request description with its
breaking changes. The added rule names the condition that ends it twice: a break leads "unless the next release from the
target branch is a major", and "A change with no break has neither the lead nor an empty heading". Two regression cases
come with it, and `pgjdbc-4392-no-break` is the input where the rule's item is noise.

## What it exercises

Whether the analogue of *Boundaries, partitions, and the negative control* for an instruction file stays quiet where
the instruction already carries its ending, and does not grow the report with a request for one.

## Skill parts

- `final-review`: `SKILL.md` §2a, the analogues of *Boundaries, partitions, and the negative control* and *What the
  writer says it verified*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked
- `apm-authoring`: loaded where §2a names it for a skill or an instruction file, not checked

## Checks

Graded by reading the report.

1. **No request for an ending the rule has.** No substantive finding says that the break-lead rule lacks the condition
   that ends it, or that it fires on a change with no break. A finding about another input the rule does not serve
   passes when it names one that the two stated conditions miss.
2. **No request for a noise control the change has.** No substantive finding says the change has no input where a lead
   is noise; `pgjdbc-4392-no-break` is that input. A finding that another branch of the rule's condition (a major
   release, an unknown release) has no case is a partition the change claims, and passes.
3. **The report did not grow.** At most 110% of the mean word count of the baseline reports of the same model. For
   Opus the baselines are `base-1`, `base-2`, and `base-3`, all on `origin/main`: 1964, 1914, and 2431 words, mean 2103,
   so at most 2313. The table of added instructions is the item this case is the noise input for, and
   `agent-packages/AGENTS.md` asks such a case to check that the output did not grow. `wc -w < result.md`
4. **The table of added instructions adds no noise.** Two parts, graded apart:
   - **4a. No finding twice.** No row of the table states a finding that another item of the report, or another row of
     the findings table, states as well. A findings-table row that only points to the table row passes. Graded by
     reading the report.
   - **4b. A table with no rows costs one line.** Where no instruction gets a row, the report writes no empty table, and
     the lines that replace it, `Added instructions:` and `Not findings:`, are at most 60 words together. Where rows
     remain, 4a governs them and 4b is n/a.

Check 3 was rebased on 2026-10-30. It used to compare with `base-1` alone (at most 2160), and `base-3`, run on the same
skills, is 124% of `base-1`: a limit the baseline itself fails measures run-to-run spread, not growth.

Check 4 replaced a word limit on the section *Boundaries, partitions, and the negative control* on 2026-10-30:
at most 110% of the mean of the same section in the baselines, 147, 147, and 206 words, so 183. That limit came from
baselines with no table, and `base-3` failed it. An empty table and its `Not findings:` line add about 50 words, which
left the table room only by pushing out the partition prose of the section: in V3j that prose was 69 to 157 words,
below every baseline, and every run still failed. What the table added past that cost was rows that repeat a finding
item 1 files, the excess *Iterations* below names, and the word limit could not tell them from a real
finding. Check 3 still guards the whole report against words moved from this section to another. The section's word
count stays in the tables below for comparison.

## Running it

As in [`cda-4f69810-review`](../cda-4f69810-review/README.md).

## Results

`base-<n>` ran the skills from `origin/main`, before the analogues for instruction files were added, as the baseline:
`base-1` on 2026-10-28, `base-2` and `base-3` on 2026-10-30, when `origin/main` also carried a newer `test-authoring`
(tree `403a0818`), which this case loads and does not check. `instr-<n>` ran final-review tree `796a9b8d` on branch
`vs/instruction-patch-rules` (variant V3m below, rewrapped) on 2026-10-30, with `apm-authoring` given to the reviewer
as well; the `1b1ebc3e` runs these labels held before are in git. Graded by reading `result.md`, 2026-10-30. Check 3 is
n/a for Haiku and Sonnet, which have no baseline; checks 4a and 4b apply to every model, and the baselines write no
table. Section words are the words under the heading that names *Boundaries, partitions*, up to the next heading of
the same or a higher level:

```sh
awk '/^#+ /{l=index($0," ")-1; if(f&&l<=n)exit
  if(!f&&tolower($0)~/boundaries, partitions/){f=1;n=l;next}} f' result.md | wc -w
```

Haiku `instr-1` has no headings, so its count is the item 3 paragraph and the table block it writes after item 7 (59
and 208); Haiku `instr-2` puts the table under a heading of its own, and its count is the item 3 section and that one
(46 and 10).

| Model | Run | Check 1 | Check 2 | Check 3 | Check 4a | Check 4b | Words | Section words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | baseline `base-1` | pass | pass: "Negative control. `pgjdbc-4392-no-break` is present and passes" | pass | n/a | n/a | 1964 | 147 | 1.36 |
| Opus | baseline `base-2` | pass | pass | pass | n/a | n/a | 1914 | 147 | 1.36 |
| Opus | baseline `base-3` | pass | pass | fail | n/a | n/a | 2431 | 206 | 1.56 |
| Opus | `instr-1` | pass: the one row is a §4 rule 5 body where the leading breaks carry no `User-visible:` label | pass: "The control (`pgjdbc-4392`) covers 'no break'" | pass | pass: the findings row says "See the table row: the clause on the label" | n/a | 1832 | 192 | 1.15 |
| Opus | `instr-2` | pass: the one row is "the agent adds `feat!:` itself" on a branch whose next release is a minor | pass: "The no-break control varies a different input ... It is not the control for this condition" | pass | pass: the findings row says "See the item 3 row" | n/a | 1656 | 251 | 1.21 |
| Sonnet | `instr-1` | pass: the rows are a one-line break and a squash-copied commit body | pass: "The negative control (4392) varies the change, not the release" | n/a | pass: no row is restated; `:74` calls the second row "filed as a finding under item 2", where item 2 files only that the squash copy has no run | n/a | 2054 | 369 | 0.31 |
| Sonnet | `instr-2` | pass: the row is "a description with a single break line that already names the code" | pass: "`pgjdbc-4392-no-break` is the negative control for 'no break'" | n/a | fail: findings row 5 restates the row and its clause, "A single break line gets a paragraph restating the code that breaks" (`:93`) | n/a | 1778 | 254 | 0.33 |
| Haiku | `instr-1` | pass: the major-release row quotes "unless … is a major" as its ending and asks only for a run | pass: "The no-break control is present" | n/a | fail: F7 and F8 restate the three rows, "no case runs them" (`:54-55`), as item 3 does at `:22` | n/a | 1432 | 267 | 0.07 |
| Haiku | `instr-2` | pass | pass: "The major and no-version-file partitions have no evidence" | n/a | pass: no row | pass: "Added instructions: 11, no rows." and "Not findings: `:234`, `:241`, `:255`.", 10 words | 1336 | 56 | 0.27 |

No run asks for an ending the rule already carries or says 4392 is missing. Several runs file that 4392 has no run on
`origin/main`; that is a missing baseline for the control, not a missing control, and passes check 2.

Every Opus run of the change, on one scale. "Old check 4" is the section limit of 183 words that checks 4a and 4b
replaced; 4a and 4b were graded from V3j on.

| Tree | Variant | Runs | Words | Section words | Check 3 | Old check 4 | Check 4a | Check 4b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `39fdd294` (commit `dcc64e5`) | before V2 | instr-1, instr-2 | 2381, 2253 | 523, 472 | fail, pass | fail, fail | — | — |
| `ea45bd15` | V2b | instr-1, instr-2 | 2469, 2346 | 643, 580 | fail, fail | fail, fail | — | — |
| working copy | V3d | v3d-1, v3d-2 | 2048, 2453 | 383, 656 | pass, fail | fail, fail | — | — |
| working copy | V3e | v3e-1, v3e-2 | 2239, 2590 | 552, 495 | pass, fail | fail, fail | — | — |
| `1b1ebc3e` | V3f | v3f-1, v3f-2, instr-1, instr-2 | 2229, 1930, 1887, 2374 | 484, 387, 442, 412 | pass, pass, pass, fail | fail ×4 | — | — |
| working copy | V3g | v3g-1, v3g-2 | 2294, 2616 | 402, 562 | pass, fail | fail, fail | — | — |
| working copy | V3h | v3h-1, v3h-2 | 2560, 2132 | 387, 382 | fail, pass | fail, fail | — | — |
| working copy | V3i | v3i-1 to v3i-4 | 2302, 1713, 2227, 2221 | 451, 226, 320, 335 | pass ×4 | fail ×4 | — | — |
| `7093483a` | V3j | v3j-1 to v3j-4 | 2106, 1909, 1605, 1742 | 301, 223, 285, 229 | pass ×4 | fail ×4 | pass, fail, fail, fail | n/a ×4 |
| working copy | V3k | v3k-1 to v3k-4 | 1752, 2153, 2531, 2377 | 244, 249, 398, 292 | pass, pass, fail, fail | fail ×4 | — | — |
| `e904d9fa` | V3l | v3l-1 to v3l-4 | 1798, 2004, 2595, 2143 | 213, 290, 274, 229 | pass, pass, fail, pass | fail ×4 | pass ×4 | fail ×4 |
| `cada8e85` | V3m | v3m-1 to v3m-4 | 1831, 1824, 1722, 1894 | 182, 194, 84, 173 | pass ×4 | pass, fail, pass, pass | pass ×4 | n/a, n/a, pass, pass |
| `796a9b8d` | V3m with `apm-authoring` | instr-1, instr-2 | 1832, 1656 | 192, 251 | pass, pass | fail, fail | pass, pass | n/a, n/a |
| `8545c2eb` (working copy) | V3n | v3n-1, v3n-2 | 2086, 2058 | 206, 130 | pass, pass | fail, pass | pass, n/a | n/a, pass |

The `ea45bd15` results were overwritten by the `1b1ebc3e` runs under the same labels, and those by the `796a9b8d` runs;
their counts were taken before. The section counts of every run before `1b1ebc3e` were taken with the same rule as
check 4.

On `796a9b8d` both Opus runs pass checks 1 to 4a and stay within check 3, at 1832 and 1656 words against 1722 to 1894
for the four V3m runs without `apm-authoring`. Each writes one row, as v3m-1 and v3m-2 did, on an input the two stated
conditions miss, and the findings table points to it. The section is 192 and 251 words against 84 to 194 on V3m, so
the old check 4 would fail both; in `instr-2` the extra words are partition prose on the untested sides of the
condition, not a second row. Against the `1b1ebc3e` runs (1887 and 2374 words, sections 442 and 412) the section is
about half as long, and check 3 now passes in both runs.

Sonnet and Haiku had not run on V3m. Both keep checks 1 and 2 in every run, as on `1b1ebc3e`, and two of their four
runs fail check 4a. Sonnet `instr-2` restates its one row as findings row 5, input and clause both, instead of
pointing to it; Sonnet `instr-1` writes two rows and is the longest report of the six, 2054 words with a section of
369. Haiku `instr-1` writes three rows for inputs that have no run, one of them the major release the rule ends
itself, and F7 and F8 restate them; Haiku `instr-2` writes no row and keeps both lines to 10 words. Word counts moved
from 1742 and 2180 to 2054 and 1778 on Sonnet and from 1512 and 1672 to 1432 and 1336 on Haiku.

## Iterations on the wording

Variants of the §2a wording, run on this case, graded by reading against checks 1 and 2, and checks 3 and 4 as rebased
where Opus ran. Earlier cells that called a missing major-release case a missing control are re-graded as pass under the
reworded check 2.

- V1 is a table of added instructions with an example row.
- V1b adds "where the artifact already ends the instruction, quote it, not a finding".
- V1c makes the table part of the report (§4).
- V1d chooses the input inside the instruction's own condition.
- V1e labels a hypothetical input no reader meets as taste.
- V1f narrows taste to an input the artifact does not address at all.
- V2 replaces the paragraph with a three-step list: choose an input, fill the row from the text, label it (an ending
  quoted is not a finding, an input the artifact does not address is taste, else substantive).
- V2b adds to V2 "meets every condition the instruction states" and "a conflicting rule does not end it"; rewrapped,
  it is tree `ea45bd15`. On it the Opus reports were 2469 and 2346 words, with tables of seven rows for the one added
  rule: a row per sentence, four of them "not a finding" written out in full.
- V3 (2026-10-30) counts the instructions first: a rule that takes several sentences is one row, its definitions,
  exceptions and checklist line being its condition; a row the artifact already ends takes one short line; a row whose
  finding another item filed points there.
- V3b moves the instructions the artifact already ends out of the table into one line below it.
- V3c adds that line to the example in §2a: `Not findings: "…", ended by "…"`.
- V3d drops "one row per instruction" from §4, which contradicted V3b, and names the `Not findings:` line there.
- V3e limits each cell to one sentence.
- V3f limits each cell to a phrase of about fifteen words, as in the example row; rewrapped, it is tree `1b1ebc3e`.
- V3g, not kept, makes an added paragraph one row unless its sentences apply under different conditions, and files a
  row's finding once, in the findings table, with no restatement in the other items' prose.
- V3h, built on V3f, names the instruction in its cell by its line and a few of its words, gives a `Not findings:` entry
  its line and the ending quoted, and writes no row for an input whose finding another item already files.
- V3i adds to V3h that a taste finding goes to the findings table alone, with no row, and cuts a `Not findings:` entry
  to the line and the first words of the ending.
- V3j limits a `Not findings:` entry to the line and at most five quoted words with no explanation, and asks the
  reviewer to read the other items' findings before writing a row.
- V3k, not kept, adds to V3j a kind of input the artifact never mentions (a kind of repository, a versioning scheme, a
  workflow) as the mark of taste.
- V3l, not kept, reorders the steps so the label comes before the row, takes the input from what the artifact names (an
  input brought from outside it is taste), sends an instruction that reads two ways or conflicts with another rule to
  item 1, has the findings table point to a row rather than restate it, and writes `Added instructions: <n>, no rows.`
  in place of an empty table.
- V3m sends an ambiguity to item 1 only where one of its readings serves the input, gives a row to an input that every
  reading fails, and keeps `Added instructions:` and `Not findings:` to numbers alone.
- V3n adds to V3m, in step 2, that only a condition ends an instruction: a clause on where the output stops, such as
  "end the sentence there", says what the agent writes once the instruction fires.

| Variant | Model | Runs | Check 1 | Check 2 | Check 3 | Old check 4 | Words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V1 | Haiku | v1-1, v1-2 | pass, pass | pass, pass | n/a | n/a | 1456, 1347 |
| V1b | Haiku | v1b-1, v1b-2, v1b-3 | pass, pass, pass | pass, pass, pass | n/a | n/a | 1898, 1836, 1033 |
| V1c | Haiku | v1c-1, v1c-2, v1c-3 | pass, pass, pass | pass, pass, pass | n/a | n/a | 1872, 1473, 1439 |
| V1c | Sonnet | v1c-1, v1c-2 | pass, fail | pass, pass | n/a | n/a | 2011, 2520 |
| V1d | Sonnet | v1d-1, v1d-2 | pass, pass | pass, pass | n/a | n/a | 2333, 2791 |
| V1e | Sonnet | v1e-1, v1e-2 | pass, pass | pass, pass | n/a | n/a | 2179, 2326 |
| V1f | Sonnet | v1f-1, v1f-2 | pass, pass | pass, pass | n/a | n/a | 1771, 1948 |
| V2 | Sonnet | v2-1, v2-2, v2-3 | pass, pass, pass | pass, pass, pass | n/a | n/a | 1753, 1683, 2727 |
| V2b | Sonnet | v2b-1, v2b-2 | pass, pass | pass, pass | n/a | n/a | 2130, 2157 |
| V3 | Haiku | v3-1, v3-2 | pass, pass | pass, pass | n/a | n/a | 2020, 1470 |
| V3 | Sonnet | v3-1, v3-2 | pass, pass | pass, pass | n/a | n/a | 2322, 2397 |
| V3b | Haiku | v3b-1, v3b-2 | pass, pass | pass, pass | n/a | n/a | 1676, 1725 |
| V3b | Sonnet | v3b-1, v3b-2 | pass, pass | pass, pass | n/a | n/a | 2063, 2119 |
| V3c | Sonnet | v3c-1, v3c-2 | pass, pass | pass, pass | n/a | n/a | 2421, 1762 |
| V3d | Sonnet | v3d-1, v3d-2 | pass, pass | pass, pass | n/a | n/a | 2497, 1702 |
| V3d | Opus | v3d-1, v3d-2 | pass, pass | pass, pass | pass, fail | fail, fail | 2048, 2453 |
| V3e | Sonnet | v3e-1, v3e-2 | pass, pass | pass, pass | n/a | n/a | 2256, 1761 |
| V3e | Opus | v3e-1, v3e-2 | pass, pass | pass, pass | pass, fail | fail, fail | 2239, 2590 |
| V3f | Opus | v3f-1, v3f-2 | pass, pass | pass, pass | pass, pass | fail, fail | 2229, 1930 |
| V3g | Opus | v3g-1, v3g-2 | pass, pass | pass, pass | pass, fail | fail, fail | 2294, 2616 |
| V3h | Opus | v3h-1, v3h-2 | pass, pass | pass, pass | fail, pass | fail, fail | 2560, 2132 |
| V3i | Opus | v3i-1 to v3i-4 | pass ×4 | pass ×4 | pass ×4 | fail ×4 | 2302, 1713, 2227, 2221 |
| V3j | Opus | v3j-1 to v3j-4 | pass ×4 | pass ×4 | pass ×4 | fail ×4 | 2106, 1909, 1605, 1742 |
| V3k | Opus | v3k-1 to v3k-4 | pass ×4 | pass ×4 | pass, pass, fail, fail | fail ×4 | 1752, 2153, 2531, 2377 |
| V3l | Opus | v3l-1 to v3l-4 | pass ×4 | pass ×4 | pass, pass, fail, pass | fail ×4 | 1798, 2004, 2595, 2143 |
| V3m | Opus | v3m-1 to v3m-4 | pass ×4 | pass ×4 | pass ×4 | pass, fail, pass, pass | 1831, 1824, 1722, 1894 |
| V3n | Opus | v3n-1, v3n-2 | pass, pass | pass, pass | pass, pass | fail, pass | 2086, 2058 |
| V3n | Sonnet | v3n-1, v3n-2 | pass, pass | pass, pass | n/a | n/a | 2082, 2078 |
| V3n | Haiku | v3n-1, v3n-2 | pass, pass | pass, pass | n/a | n/a | 1172, 1372 |

The one check-1 failure is V1c-2, which asks to limit the release-tool sentence to repositories with the tool although
the sentence opens "Where a release tool bumps".

What moved the reports: under V3 and V3b Sonnet kept a row per sentence and kept "not a finding" rows in the table,
writing "Listed below the table" in a row with no list below it; §4 still said "one row per instruction", and once V3d
removed that, every Opus run put those instructions in a `Not findings:` list, and so did the four Sonnet runs of V3d
and V3e, two of them keeping the rows as well. The rows that remain are findings on other inputs, which check 1 allows,
and under V3d and V3e their cells ran to two or three sentences each; V3f's fifteen-word phrase is the first limit Opus
kept. V3g did not shorten the control (section 402 and 562 words) and was reverted to V3f. Sonnet word counts move
between 1702 and 2497 within one variant, so they do not rank the variants.

V3h to V3j took the section from a mean of 431 words on V3f to 333 on V3i and 260 on V3j, and V3j keeps every Opus
report within check 3. In the V3j runs the section is about 70 to 160 words of partition prose, which the baselines
carry too, a `Not findings:` line of 17 to 25 words, and one to three rows of 77 to 170 words. The rows that remain
name inputs such as a 0.x or calendar-versioned project, or a service with no releases, which the artifact does not
address and which step 3 calls taste; Opus still writes them as rows. V3k named those kinds of input in the rule and
did not move the section (mean 296), so it was reverted to V3j. Check 4 still fails: one row of about 50 words on top
of the baselines' 147 to 206 words of prose is past the limit of 183.

Graded by checks 4a and 4b, V3j passes 4a in one run of four: in v3j-1 the findings table points to the two rows, and
in the other three the findings table or item 1 restates the row's finding, such as the trailer that "decides". V3l
wrote no row in any run: the ambiguities and the conflict went to item 1 and the 0.x input to the findings table as
taste. Its `Added instructions:` and `Not findings:` lines took 92 to 146 words, because Opus listed every instruction
and gave each `Not findings:` entry a sentence on why it ends, so 4b failed in all four; v3l-3 broke check 3 with
thirteen findings, not with the table. V3l also lost the target's row in one run of two. V3m keeps both lines to numbers
(10 words in the two runs with no row) and writes one row in v3m-1 and v3m-2, each on an input the two stated conditions
miss (a §4 rule 5 body that opens with breaks, a version file equal to a tagged `43.0.0`), each with a findings-table
row that points to it. The section is 84 to 194 words, so the old check 4 would pass three of four.

V3n, on final-review tree `8545c2eb`, targets the Sonnet runs of `cda-4f69810-review` and leaves the control where V3m
had it. Opus v3n-1 writes one row, on a release-please repository whose own `!` forces the major, and the findings
table says "The clause in the table row"; v3n-2 writes "Added instructions: 2, no rows." and a `Not findings:` line of
five line numbers. Both Opus reports pass check 3. Both Sonnet runs fail 4a: v3n-1 writes one row on a template with
fixed headings and findings row 4 repeats its clause, "Add 'only where the template has no section that fits' (see the
table)"; v3n-2 writes one row on a changed error code for an input that already failed, and findings row 7 restates it
with the clause. Sonnet `instr-2` on `796a9b8d` failed 4a the same way, and `instr-1` passed it. Both Haiku runs write
no row, and keep both lines to about ten words.
