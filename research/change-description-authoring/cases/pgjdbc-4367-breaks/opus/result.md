**Breaking changes.** These apply to a string of several statements executed with generated keys requested (`RETURN_GENERATED_KEYS` or key column names). Each statement after a `;` is now classified the same way as when it runs alone:

- An `INSERT` that is not the first statement now returns its keys as a result set from `getMoreResults()` instead of an update count, and `getUpdateCount()` is `-1` for it. The same applies to a last statement ending in `?` and to a statement after one that ends in a keyword such as `RETURNING` or `DELETE`.
- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before, it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before, it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- A statement after a `;` that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. The first statement of a string already failed this way.

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected the generated keys. Three defects caused this:

- `INSERT` was recognized only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type at all. This affects a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before checking the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement. It failed with `cannot insert multiple commands into a prepared statement` (SQLState `42601`), and now it succeeds.

Each statement is now classified by its own text. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten. `getGeneratedKeys()` is unchanged too, and for a multi-statement string it returns no rows, both before and after this change. A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, after an optional `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment between them is allowed but a comma, a parenthesis, a quoted identifier, or a literal is not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

**Scope.** This change does not narrow which `INSERT` counts, which is why `grant insert` breaks in the list above. `explain insert …` and `prepare p as insert …` depend on the same rule: an `INSERT` anywhere in a statement that starts with an unrecognized keyword classifies it as an `INSERT`. The change also leaves one failure in place. With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, both before and after this change.

Each defect has a control case that passes on the old parser too. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The other 9 pass on both parsers: the 6 genuine bodies, and 3 strings the old parser split correctly by accident, which guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes above were checked against PostgreSQL 17, both with the 42.7.13 driver and with this branch.
