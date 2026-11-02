`Parser.parseJdbcSql` now classifies each statement of a multi-statement string by its own text.

**Breaking changes.** These changes affect code that requests generated keys (`RETURN_GENERATED_KEYS` or key column names) and executes a SQL string that holds more than one statement. Each statement after the first can now get the `RETURNING` clause it gets when it runs alone, and it is then answered differently than with 42.7.13:

- With key column names, a statement after a `;` whose table lacks one of those columns fails with `column "id" does not exist` (SQLState `42703`). With 42.7.13 it got no `RETURNING` and succeeded. The same statement executed alone already failed this way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, fails with `A result was returned when none was expected.` (SQLState `0100E`). With 42.7.13 it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- Three kinds of statement now return their keys as a result set from `getMoreResults()`, and `getUpdateCount()` is `-1` for them, where they returned an update count before: an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement after one that ends in a keyword such as `RETURNING` or `DELETE`. `getGeneratedKeys()` does not change. For a multi-statement string it returns no rows, before and after this change.
- A later statement that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, gets `RETURNING` appended and fails with a syntax error. Before this change that happened only to the first statement of a string (see Scope).

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. Three defects caused this:

- `INSERT` was recognized only in the first statement, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- When `?` was the last character, the parser took it for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more earlier statements, it got no command type at all. This affects a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so the parser kept `create table begin(atomic int); insert into t(a) values(?)` as one statement. The server rejected it with `cannot insert multiple commands into a prepared statement` (SQLState `42601`). That string no longer fails.

Each statement is now classified by its own text, so it gets the same `RETURNING` clause it gets when executed alone. Batch-rewrite eligibility does not change: only the first statement can be rewritten. A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, after an optional `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not open a body;
- where `BEGIN` and `ATOMIC` are adjacent keywords. A comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

Some tests pass both with and without the change. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The 6 genuine bodies pass on both. So do 3 strings that the old parser split correctly by accident, and they guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The caller-visible outcomes above were checked on PostgreSQL 17 with the 42.7.13 driver and with this branch.

**Scope.** In a statement that starts with an unrecognized keyword, an `INSERT` anywhere in its text makes the parser classify it as an `INSERT`. This change keeps that rule because `explain insert …` and `prepare p as insert …` rely on it. The rule is what causes the `grant insert` break above. With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. That happens both before and after this change, and this change does not fix it.
