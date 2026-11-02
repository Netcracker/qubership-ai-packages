**Breaking changes.** These affect code that requests generated keys (`RETURN_GENERATED_KEYS` or key column names) on a SQL string with more than one statement. The first three were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

- With key column names, a statement after a `;` now fails with `column "id" does not exist` (SQLState `42703`) when its table lacks one of those columns. On 42.7.13 it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- `executeUpdate()` on such a string now fails with `A result was returned when none was expected.` (SQLState `0100E`). One example is `set search_path to public; insert into t(a) values(?)`. On 42.7.13 it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- Some statements now return their keys as a result set from `getMoreResults()`, and `getUpdateCount()` is `-1` for them. On 42.7.13 they returned an update count. This applies to an `INSERT` that is not the first statement, to a last statement that ends in `?`, and to a statement after one that ends in a keyword such as `RETURNING` or `DELETE`.
- A later statement that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. Before this change, only the first statement of a string was treated this way.

`Parser.parseJdbcSql` classified a statement by what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected the generated keys. Three defects caused this:

- `INSERT` was recognized only in the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type. A common shape hits this: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was too loose as well: after any `CREATE`, any two consecutive keywords opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers. As a result, `create table begin(atomic int); insert into t(a) values(?)` stayed one statement, and the server rejected it with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Each statement is now classified by its own text, so it gets the same `RETURNING` clause as when it is executed alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten. `getGeneratedKeys()` is unchanged too. For a multi-statement string it returns no rows, before and after this change.

A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one, so `create table begin(atomic int); insert into t(a) values(?)` no longer fails. A body is detected only under these conditions:

- in a `CREATE` whose object keyword, after `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". Some cases pass on the old parser on purpose. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, the 6 genuine bodies pass on both, and so do 3 strings that the old parser split correctly by accident; those 3 guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps.

**Scope.** This change does not narrow which `INSERT` counts. `INSERT` anywhere in a statement that starts with an unrecognized keyword still classifies the statement as an `INSERT`, because `explain insert …` and `prepare p as insert …` rely on that rule. The `grant insert` break above comes from this rule. A separate failure is also not addressed: with `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, both before and after this change.
