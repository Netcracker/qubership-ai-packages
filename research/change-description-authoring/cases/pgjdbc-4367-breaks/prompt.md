# Task

Write the pull request description for the change below, in Markdown, ready to paste into GitHub. The facts come from
the author's draft, which was checked against the code and against a running server; treat every fact in it as
verified, and add none that it does not carry. The draft is the author's, and you may restructure, cut, or reword it.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver.
- Target branch: `master`. Its `gradle.properties` says `pgjdbc.version=42.7.14`; the latest release tag is
  `REL42.7.14`. There is no milestone on the pull request.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template. The pull request has one commit.

## The author's draft

````markdown
## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested (`RETURN_GENERATED_KEYS` or key column names), a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone, so it returned an update count where the caller expected the generated keys. Three defects lead there:

- `INSERT` was recognized only as the first statement of the string: the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or, after two or more statements, no command type. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before the keyword in front of the `;` was examined, so that keyword set them on the next statement: in `select; update t set a=1` the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was loose as well: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept in one statement, and the server rejected it.

## What

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords; a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## What the caller sees

- **Breaks:** with key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`); before this change it got no `RETURNING` and succeeded. Such a statement executed alone already fails the same way.
- **Breaks:** `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`) where it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- With generated keys requested, an `INSERT` that is not the first statement, a last statement ending in `?`, or a statement after one that ends in a keyword such as `RETURNING` or `DELETE` returns its keys as a result set from `getMoreResults()` where it returned an update count, and `getUpdateCount()` is `-1` for it. `getGeneratedKeys()` is unchanged: for a multi-statement string it returns no rows before and after this change.
- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

## Scope

`INSERT` anywhere in a statement that starts with an unrecognized keyword classifies the statement as an `INSERT`, so with generated keys requested `grant insert on t to bob` gets `RETURNING` appended and fails with a syntax error. That was already the case for the first statement of a string; recognizing `INSERT` in every statement extends it to the later ones. This change does not narrow which `INSERT` counts, because `explain insert …` and `prepare p as insert …` rely on the same rule.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Each defect has cases that fail on the parser before the fix and a control that passes on both. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser; the 6 genuine bodies pass, and so do 3 strings the old parser split correctly by accident, which guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The caller-visible outcomes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

````
