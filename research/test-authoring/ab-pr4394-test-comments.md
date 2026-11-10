# A/B trial: comments above tests, and where the reason for an expected value goes

Run on 2026-11-05 and 2026-11-10 against pgjdbc, on the tests owed by
[PR #4394](https://github.com/pgjdbc/pgjdbc/pull/4394). The pull request takes the SQL command type only from the first
word of a statement, stops typing EXPLAIN, and fixes three keyword matchers that missed a keyword at the end of the
input. A session under `test-authoring` 1.2.0 wrote its tests, and the maintainer's review then removed most of their
comments. The trial asks which skill text produced those comments and whether a patch moves them.

## The defects and the text behind them

The tests the session wrote had nine comments, and the review left three. The defects, each traced to the text that
licensed it:

1. A method comment restated the method name. §7, under the table, said the comment "may repeat the rule the message
   states", and nothing said that a test usually needs no comment.
2. Comments used the skill's working words: "The case is…", "are its controls". §7 defines *case*, *control*, and *act*
   for the writer, and nothing kept them out of the file.
3. A comment narrated history: "a matcher whose guard was already right". §7 defines a control as an input "whose
   expectation holds on the base commit", and the writer copied that fact into the comment.
4. "Pins the current behavior, not a JDBC requirement" sat in a comment. §7's message row had no slot for why an
   expected value is what it is, and `javadoc-authoring` §3 said the test comment "carries the reason".
5. Two tests had the same act and assertions and differed only in input. §7 principle 4 allowed separate tests on one
   helper and said nothing about a test that repeats a parameterized test of the same change.

## Setup

The eval base is the three code commits of the pull request with the tests removed. Each run got its own shallow clone,
with the before and after branches unreachable, and read the skills from a neutrally named copy. Builds and database
runs were forbidden, so every arm reasoned out its red run rather than running it. Each resulting diff went to one blind
Opus judge, which labeled every added comment and answered three questions:

- Where does the reason for each of two surprising values sit? `Statement.executeUpdate` returns -1 for an EXPLAIN with
  generated keys, where JDBC asks for an `SQLException`. An EXPLAIN of a statement with its own RETURNING still returns
  the plan as generated keys.
- Do two useful facts survive? One is why a `listen insert` test exists, the other where `\nRETURNING *` in the
  expected strings comes from.
- How many pairs of added tests could be rows of one parameterized test?

The labels were VOCAB (the working words), HISTORY, RESTATES, WHY_VALUE, CONSTRUCTION, WHY_TEST, and OTHER. As a
calibration, the judges also graded the session's original tests and the maintainer's version: the first got 3 VOCAB
comments and its reasons only in comments, the second its reasons in messages.

Arms: baseline (1.2.0); V1, which adds the message slot, a "most tests need no comment" block, a principle-4 sentence
on duplicates of a parameterized test, three §11 items, a §12 example, and the `javadoc-authoring` §3 sentence that
sends the reason for an expected value to the message; V2, which adds
to V1 the §7 table row for the comment, row-group headings named as restatement, the bullet on an expected value a
reader would correct, a message slot that asks for the specification or the release rather than the mechanism, and
the `javadoc-authoring` §4 paragraph. The change that adds this note is V2 with wording fixes from a review, listed
at the end; those fixes were not run.

## Results

| Opus, 3 runs per arm | baseline | V1 | V2 |
| --- | --- | --- | --- |
| Comments added | 0, 1, 2 | 0, 1, 0 | 1, 0, 0 (a CONSTRUCTION comment on a helper) |
| RESTATES | 0 | 0 | 0 |
| Reason for -1 in the message | 0 of 3 | 3 of 3, the mechanism | 3 of 3, each naming the JDBC deviation |
| Reason for the own-RETURNING value in the message | 0 of 3 | 1 of 3 | 1 of 3 |
| Origin of `\nRETURNING *` stated | 1 of 3 | 2 of 3 | 3 of 3 |
| Near-duplicate test pairs | 4, 4, 6 | 0, 3, 3 | 0, 0, 3 |

| Sonnet | baseline (5 runs) | V1 (3 runs) | V2 (4 runs) |
| --- | --- | --- | --- |
| Comments added | 0, 2, 8, 2, 3 | 4, 4, 7 | 0, 0, 0, 0 |
| RESTATES | 6 | 9 | 0 |
| Reason for -1 in the message | 0 of 5 | 0 of 3 | 3 of 4, the mechanism |
| Reason for the own-RETURNING value in the message | 0 of 5 | 0 of 3 | 0 of 4 |
| Origin of `\nRETURNING *` stated | 3 of 5 | 0 of 3 | 1 of 4 |
| Near-duplicate test pairs | 6, 4, 3, 11, 3 | 4, 4, 4 | 5, 4, 3, 4 |

V1 worked for Opus and not for Sonnet: Sonnet's comments under V1 were row-group headings inside a method source and
method Javadoc that restated the name, which V1 forbade only in prose under the table. V2 put the comment in the §7
table as a row of its own, and Sonnet then wrote no comment in any run. The V2 Opus message for -1 matches the
maintainer's: with generated keys requested, `Statement.executeUpdate` reports a result set as update count -1, where
JDBC asks for an `SQLException`. Sonnet's V2 messages give the mechanism, not the deviation.

## What this trial does not show

- The `listen insert` reason appears in no run of any arm, the baseline included.
- Defects 2 and 3 never appeared: VOCAB and HISTORY were 0 in every run. The original session's prompt asked it to
  "keep a contrast/control as the skill requires" and it ran its red runs; the eval prompt did neither. V2's rules
  against the working words and against history are therefore untested.
- V2 removed the helper comments that baseline Sonnet writes, which the judges labeled OTHER rather than noise, and the
  origin of `\nRETURNING *` appears in 1 of 4 Sonnet runs against 3 of 5.
- Sonnet's near-duplicate pairs did not move (baseline 6, 4, 3, 11, 3; V2 5, 4, 3, 4), and the reason for the
  own-RETURNING value reached the message in 1 of 3 Opus runs under both V1 and V2. The duplicate check and the bullet
  on an expected value a reader would correct are not shown to work on those two.
- No run checked that messages for unsurprising values stay as short as before.
- The cases under `cases/` whose skill parts include §7 ran on the final text, after the wording fixes below; each
  README names the tree, and the commit that adds the results grades them.

Wording fixes after the runs, not measured: the comment may say why a test that looks as if it cannot fail exists
(`javadoc-authoring` had allowed any reason the test exists); a part of the expected value that comes from the
test's own arguments may stay in the comment; the duplicate check covers a test that repeats a parameterized test of
the same change; the comment rules name the doc-comment skill of the language rather than `javadoc-authoring` alone;
and four reference files gained the reason clause of the message.

The prompts, the per-run diffs, the patch scripts, and the judge verdicts are kept outside this repository.
