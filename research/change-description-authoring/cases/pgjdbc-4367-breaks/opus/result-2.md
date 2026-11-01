**Breaking changes.** Only multi-statement strings executed with generated keys requested (`RETURN_GENERATED_KEYS` or key column names) are affected. Each line compares this branch with the 42.7.13 driver.

- These statements now return a result set with their generated keys from `getMoreResults()`, and `getUpdateCount()` is `-1` for them. Before, they returned an update count:
  - an `INSERT` that is not the first statement;
  - a last statement that ends in `?`;
  - a statement after one that ends in a keyword such as `RETURNING` or `DELETE`.
- `executeUpdate()` on such a string, for example `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before, it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way. Call `execute()` instead, and read the keys from `getMoreResults()`.
- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before, it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- A later statement that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. The first statement of a string already failed this way.

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. The caller then got an update count where it expected the generated keys. Three defects caused this:

- `INSERT` was recognized only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type at all. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was too broad as well: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement, and the server rejected it.

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets when executed alone. Batch rewrite still applies only to the first statement. A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, after an optional `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

As a result, `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`). `getGeneratedKeys()` is unchanged: for a multi-statement string it returns no rows, both before and after this change.

Every defect has at least one control case in `ParserTest` that passes on both the old parser and this branch. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 9 of the 21 strings pass on the old parser: the 6 genuine bodies, and 3 strings that the old parser split correctly by accident and that guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes listed above were checked against PostgreSQL 17, once with the 42.7.13 driver and once with this branch.

**Scope.** An `INSERT` anywhere in a statement that starts with an unrecognized keyword still classifies that statement as an `INSERT`, which causes the `grant insert` break above. This change does not narrow that rule, because `explain insert …` and `prepare p as insert …` depend on it. With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. That happens both before and after this change, and this change does not fix it.
