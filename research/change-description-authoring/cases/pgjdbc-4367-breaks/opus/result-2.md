**Breaking changes.** These changes affect code that requests generated keys, through `RETURN_GENERATED_KEYS` or key column names, for a string of several statements. The released driver (checked with 42.7.13) behaves differently for a statement after a `;`:
- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before this change it got no `RETURNING` and succeeded. The same statement executed alone already fails this way. Pass key column names only with statements whose tables have those columns.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before, it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way. Call `execute()` and read the results with `getMoreResults()` instead.
- Some statements now return their keys as a result set from `getMoreResults()` where they returned an update count, and `getUpdateCount()` is `-1` for them. This covers an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement after one that ends in a keyword such as `RETURNING` or `DELETE`. Read the keys with `getResultSet()`.
- `grant insert on t to bob` after a `;` now gets `RETURNING` appended and fails with a syntax error. It already failed this way as the first statement of a string.

`getGeneratedKeys()` is unchanged: for a multi-statement string it returns no rows before and after this change.

`Parser.parseJdbcSql` classified a statement by what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected the keys. Three defects caused this:

- `INSERT` was recognized only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type. A common shape hits this: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set them on the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was too broad: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` stayed one statement. The server rejected it with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets when executed alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten. A statement that starts with an unrecognized keyword and contains `INSERT` anywhere is still classified as an `INSERT`, because `explain insert …` and `prepare p as insert …` rely on that rule. The `grant` break above follows from it. A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

The `create table begin(atomic int); …` string is now split into two statements and no longer fails.

In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The other 9 pass on both parsers: 6 genuine bodies, and 3 strings that the old parser split correctly by accident and that guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

**Scope.** With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. This happens before and after this change, and the change does not address it.
