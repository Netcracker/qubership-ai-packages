## Breaking changes

Code that executes a multi-statement string with generated keys requested (`RETURN_GENERATED_KEYS` or key column names) gets different results for the statements after the first `;`. Each statement now gets the `RETURNING` clause it gets when executed alone.

- With key column names, a statement after a `;` whose table lacks one of those columns fails with `column "id" does not exist` (SQLState `42703`). In 42.7.13 it got no `RETURNING` and succeeded. The same statement executed alone already fails this way. Request key column names only where every statement's table has those columns, or execute that statement on its own.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, fails with `A result was returned when none was expected.` (SQLState `0100E`). In 42.7.13 it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way. Call `execute()` and read each result with `getMoreResults()` instead.
- An `INSERT` that is not the first statement, a last statement that ends in `?`, or a statement after one that ends in a keyword such as `RETURNING` or `DELETE` returns its keys as a result set from `getMoreResults()`, and `getUpdateCount()` is `-1` for it. In 42.7.13 it returned an update count. Code that reads the count for such a statement reads the result set instead.
- A later statement that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, gets `RETURNING` appended and fails with a syntax error. Before this change only the first statement of a string failed this way. Execute such a statement without generated keys.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone, so it returned an update count where the caller expected the generated keys. Three defects lead there:

- `INSERT` was recognized only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or no command type after two or more statements. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set them on the next statement. In `select; update t set a=1` the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was loose as well: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept in one statement, and the server rejected it.

## What

Each statement is now classified by its own text. A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords; a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.
- Not changed: only the first statement of a string can be batch-rewritten.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Each defect has cases that fail on the parser before the fix and a control that passes on both. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser; the 6 genuine bodies pass, and so do 3 strings the old parser split correctly by accident, which guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes under "Breaking changes" and "User-visible changes" were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

## Scope

This change does not narrow which `INSERT` counts. `explain insert …` and `prepare p as insert …` rely on the same rule that makes `grant insert on t to bob` an `INSERT`.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change.
