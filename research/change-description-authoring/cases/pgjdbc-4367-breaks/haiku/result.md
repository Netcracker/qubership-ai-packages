## Breaking changes

Code that runs a multi-statement string with generated keys requested breaks in four ways. Each one worked on the 42.7.13 driver.

- With key column names, a statement after a `;` whose table lacks one of those columns fails with `column "id" does not exist` (SQLState `42703`). Before, it got no `RETURNING` and succeeded. The same statement run alone already fails this way. Pass only key columns that exist in that statement's table.
- With generated keys prepared, `executeUpdate()` fails with `A result was returned when none was expected.` (SQLState `0100E`) for a string such as `set search_path to public; insert into t(a) values(?)`. Before, it returned the count of the first statement and no keys. Call `execute()` instead. The same error already comes from a string whose last statement is an `UPDATE` or `DELETE` that does not end in `?`.
- With generated keys requested, an `INSERT` that is not the first statement, a last statement ending in `?`, or a statement after one that ends in a keyword such as `RETURNING` or `DELETE` returns its keys as a result set from `getMoreResults()`. Before, it returned an update count. `getUpdateCount()` is now `-1` for it. Read the keys from `getResultSet()`.
- An `INSERT` anywhere in a statement that starts with an unrecognized keyword now counts as an `INSERT`. With generated keys requested, `grant insert on t to bob` gets `RETURNING` appended and fails with a syntax error. The first statement of a string already behaves this way; this change extends it to later statements. Run such a statement without generated keys.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when run alone, so it returned an update count where the caller expected the keys. Three defects led there:

- `INSERT` counted only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or, after two or more statements, no command type. `update t set a=1; update t set a=?` is a common shape that hits this.
- The `;` branch reset the statement flags before the keyword in front of the `;` was examined, so that keyword set them on the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was too loose too: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement, and the server rejected it.

## What

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets when run alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords. A comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` is split into two statements and no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.

## Scope

- `INSERT` anywhere in a statement that starts with an unrecognized keyword keeps counting as an `INSERT`. This change does not narrow that rule, because `explain insert …` and `prepare p as insert …` rely on it.
- With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change. This change leaves that as it is.

## How to verify

In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, the genuine `BEGIN ATOMIC` bodies and three strings the old parser split correctly by accident pass on both parsers. Those three guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps, and it passes on both.

The caller-visible outcomes above were checked against PostgreSQL 17, with the 42.7.13 driver for the old behavior and this branch for the new. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL".
