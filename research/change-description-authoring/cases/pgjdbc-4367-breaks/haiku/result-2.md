## Breaking changes

Compared with the 42.7.13 driver, a string of several statements run with generated keys requested (`RETURN_GENERATED_KEYS` or key column names) changes in these ways:

- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before this change it got no `RETURNING` clause and succeeded. Such a statement run alone already fails the same way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before, it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already fails this way.
- An `INSERT` that is not the first statement, a last statement that ends in `?`, or a statement after one that ends in a keyword such as `RETURNING` or `DELETE` now returns its keys as a result set from `getMoreResults()`, where it returned an update count. `getUpdateCount()` is `-1` for it.
- A statement after a `;` that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. Before this change, it ran without `RETURNING`.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when run alone, so it returned an update count where the caller expected the generated keys. Three defects lead there:

- `INSERT` was recognized only as the first statement of the string: the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or, after two or more statements, no command type. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before the keyword in front of the `;` was examined, so that keyword set them on the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was loose as well: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept in one statement, and the server rejected it.

## What

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets when run alone.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords; a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.
- Not changed: batch-rewrite eligibility is unchanged. Only the first statement can be rewritten.

## Scope

- This change keeps the rule that counts any `INSERT` in a statement that starts with an unrecognized keyword. That rule is why `grant insert` above gets `RETURNING`. `explain insert …` and `prepare p as insert …` rely on the same rule, so narrowing it would change them too.
- With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change.

## How to verify

- `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps.
- In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The other 9 pass on it: the 6 genuine bodies, and 3 strings the old parser splits correctly by accident, which guard the new checks.
- Each defect has a control case that passes on both the old and the new parser.
- Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL".
- The caller-visible outcomes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.
